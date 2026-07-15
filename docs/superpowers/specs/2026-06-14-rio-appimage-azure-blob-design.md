# `rio update` — host AppImages on Azure Blob (kill GitHub rate-limit)

- **Date:** 2026-06-14
- **Status:** Design — pending review
- **Owner:** amitsingh21
- **Slack:** https://rapyuta-robotics.slack.com/archives/CBAP39MGD/p1781061285374049

## Problem

`rio update` fails for AppImage installs:

```
🎉 A newer version (10.5.0) is available.
Do you want to update? [y/N]: y
❌ Failed to update: Failed to retrieve the download URL for the latest AppImage
```

Root cause (confirmed in thread by Tom, U01672FEFPD):

> "This must be rate limiting from Github on the office IP. The upgrade uses Github API to fetch the artifact. We have seen this happening before."

`update_appimage()` (`riocli/utils/__init__.py:213`) calls `https://api.github.com/repos/rapyuta-robotics/rapyuta-io-cli/releases/latest`, then downloads the matched asset's `browser_download_url`. The **`api.github.com` call** is unauthenticated and shares the office-IP rate-limit budget; when exhausted, the assets lookup returns nothing and the download URL resolution fails.

## Goals

1. AppImage `rio update` downloads from **our Azure Blob storage**, not `api.github.com` — no shared GitHub rate limit.
2. Channel-aware updates: a `release`-channel binary updates from the release channel; a `devel`-channel binary from devel.
3. Per-branch PR AppImages hosted on our storage too (replace the GitHub-Actions-artifact PR-comment link).

## Non-goals

- **Do not** touch the pip/PyPI path. `is_pip_installation()` → `pip_install_cli()` stays exactly as-is; pip users keep using PyPI. Blob storage is queried *only* in the AppImage branch.
- **Do not** migrate the MinIO build-input cache (appimagetool + python base AppImage). Separate concern, not user-facing, not rate-limiting anyone. Stays as-is.
- **Do not** remove PyPI publishing (`pypi.yml`) or GitHub Release creation. Both kept (GitHub Release is the transition fallback — see Backwards Compatibility).

## Current state (reference)

| Trigger | Workflow | Output (today) |
|---|---|---|
| push `devel` | `upload-appimage.yml` | AppImage → GitHub Actions artifact (15d) |
| push `main` | `upload-appimage.yml` + `release.yml` | GH artifact + semantic-release |
| `release.yml` (semantic-release, main) | builds versioned AppImage | GitHub Release asset + changelog commit |
| PR | `upload-appimage.yml` | GH Actions artifact + bot PR comment link |
| GitHub release published | `pypi.yml` | PyPI publish |

- Version check `check_for_updates()` (`utils/__init__.py:173`) → PyPI JSON. (Not rate-limited; PyPI is fine.)
- Update dispatch `bootstrap.py:141`: pip → `pip_install_cli`; AppImage → `update_appimage`.
- Azure precedent already in repo: `riocli/chart/util.py:12` `https://chartsbranch.blob.core.windows.net/charts-per-branch`, fetched with anonymous `requests.get()` (public-read). This design copies that access pattern.

## Architecture

### Storage account

New dedicated Azure Storage account in the **OKD4 Prod subscription** (e.g. `riocliartifacts`). **Public-read containers, authenticated write** — anonymous GET for `rio update` (no creds shipped in the CLI), CI authenticates to upload.

| Container | Contents | Written by | Lifecycle | `rio update` channel? |
|---|---|---|---|---|
| `release` | `rio-<ver>-x86_64.AppImage`, `latest.json` | `release.yml` | permanent | **yes (release)** |
| `devel` | `rio-<ver>-x86_64.AppImage`, `latest.json` | `upload-appimage.yml` (push devel) | 30d auto-expire | **yes (devel)** |
| `dev` | `<branch>/rio-<sha>-x86_64.AppImage` | `upload-appimage.yml` (PR) | 15d auto-expire | no — download host only |

Separate containers (not path prefixes) so each can carry its own retention/lifecycle policy.

### Channel identity — version suffix

The build stamps `__version__` so an installed binary is self-describing; no extra bundled file.

| Channel | `__version__` example | Container |
|---|---|---|
| release | `10.6.0` | `release` |
| devel | `10.6.0-devel+<sha>` | `devel` |
| dev/PR | `10.6.0-dev.<branch>+<sha>` | `dev` (not updatable) |

`rio update` parses its own `__version__`:
- pre-release token contains `devel` → devel channel.
- pre-release token contains `dev.` → dev build → **not auto-updatable**; print a notice ("development build — rebuild from your branch or install a release").
- otherwise → release channel.

### `latest.json` manifest (release + devel only)

```json
{
  "version": "10.6.0-devel+abc1234",
  "file": "rio-10.6.0-devel+abc1234-x86_64.AppImage",
  "sha256": "<hex>"
}
```

CI regenerates and overwrites it on every build of that channel. The `dev` container has no manifest (per-branch, not a moving "latest").

## Producer changes (CI)

### `scripts/build-rio-appimage.sh`

After the AppImage is built, add an upload stage driven by a `CHANNEL` env set by the calling workflow:

1. Compute `sha256sum` of the built `rio-*.AppImage`.
2. For `release`/`devel`: write `latest.json` (version, file, sha256).
3. `azcopy copy` the AppImage (and, for release/devel, `latest.json`) into the channel container.
   - `release`/`devel`: container root.
   - `dev`: `dev/<branch>/`.
4. Auth via a write-scoped **SAS token** (recommended) or account key, from a new GH secret.

New GH secrets:
- `AZURE_STORAGE_ACCOUNT` — account name.
- `AZURE_SAS_TOKEN` — write-scoped SAS (container-scoped, short rotation) **or** `AZURE_STORAGE_KEY` account key.

The build script already receives the version as `$1` (from `.releaserc.json` exec). For devel/dev (no semantic-release version), the script derives a version+suffix from `git` (`<base>-devel+<sha>` / `<base>-dev.<branch>+<sha>`).

### `upload-appimage.yml`

- **PR**: build → upload to `dev/<branch>/`. PR bot comment links to the blob URL instead of the GitHub-Actions-artifact run page. (Keep `upload-artifact` if desired as a secondary, or drop it.)
- **push `devel`**: build → upload to `devel` + regenerate `devel/latest.json`.
- **Remove `main`** from this workflow's triggers — `release.yml` owns main.
- Pass `CHANNEL` + Azure secrets as env.

### `release.yml` / `.releaserc.json`

- semantic-release flow unchanged through changelog/version bump/GitHub Release/PyPI.
- `build-rio-appimage.sh` (already a `prepareCmd` exec) gains the upload stage; called with `CHANNEL=release` → uploads versioned AppImage to `release` + regenerates `release/latest.json`.
- **Keep** the `@semantic-release/github` asset attach (GitHub Release still carries the AppImage — transition fallback) and PyPI publish.

## Consumer changes (CLI)

### `update_appimage()` (`riocli/utils/__init__.py:213`)

Replace the `api.github.com` lookup with blob fetch:

1. Derive channel from `__version__`. If dev build → print notice, return (no auto-update).
2. `GET https://<account>.blob.core.windows.net/<container>/latest.json` (anonymous).
3. Download `https://<account>.blob.core.windows.net/<container>/<file>`.
4. Verify `sha256` against the manifest; abort on mismatch.
5. Swap the executable — **keep existing logic** (temp dir → chmod 755 → `os.remove(sys.executable)` → `move`, with the root-user warning on `OSError`).

Account name: a module constant (mirrors `chart/util.py`'s `BRANCH_REPO_BASE`), overridable by env (e.g. `RIO_APPIMAGE_BASE_URL`) for testing/staging.

### `check_for_updates()` (`riocli/utils/__init__.py:173`)

Make installation-aware so the AppImage branch doesn't depend on PyPI for non-release channels:
- pip install → PyPI JSON (unchanged).
- AppImage → read `latest.json` for the binary's channel; compare `version` via `semver`.

`bootstrap.py update` keeps its shape; the check + download just route by installation type and channel.

### Fallback (optional, recommended for transition)

If the blob `latest.json`/download is unreachable, fall back to the existing GitHub Release path so updates still work during rollout / blob outages.

## Security / access model

- **Download:** anonymous public-read containers. AppImages are already publicly downloadable on GitHub Releases, so no confidentiality change. No credentials shipped in the CLI.
- **Upload:** CI only, via SAS token / account key in GH secrets. Prefer a container-scoped, write-only, time-bound SAS with a rotation reminder.
- **Integrity:** sha256 in `latest.json`, verified client-side before swapping the executable.

## Lifecycle / retention

- `release`: permanent.
- `devel`: blob lifecycle rule, delete after 30d.
- `dev`: blob lifecycle rule, delete after 15d (matches today's GH-artifact retention).

## Backwards compatibility / migration

- AppImages **already in the field** (e.g. 10.5.0) run the old `update_appimage` that hits GitHub. They keep working **only while the GitHub Release path exists** — hence GitHub Release is kept. First `rio update` from an old binary still goes through GitHub, lands them on a blob-aware version; every update after that uses Azure.
- The first blob-aware release must also be published as a normal GitHub Release so existing users can reach it.
- No flag day; the two paths coexist. GitHub Release asset attach can be dropped only after the field has largely rolled past the last GitHub-only version (future cleanup).

## Testing

- **Unit (`tests/unit/`, no network):**
  - channel-from-version parsing: `10.6.0` → release; `10.6.0-devel+x` → devel; `10.6.0-dev.feat+x` → dev/non-updatable.
  - manifest URL construction per channel (mirror `test_chart_branch_util.py`).
  - sha256 verify: pass on match, abort on mismatch.
  - env override of the base URL.
- **Manual / staging:** point the base-URL env at a staging container; run `rio update` from a built devel AppImage end to end.
- **CI dry-run:** verify `build-rio-appimage.sh` upload stage against a throwaway container (SAS) before wiring secrets into the real workflows.

## Open questions / follow-ups

1. Final storage-account name + container names (`release`/`devel`/`dev` vs `release`/`devel`/`branches` — `devel`/`dev` are one letter apart; confirm acceptable).
2. azcopy auth: write-scoped SAS (preferred) vs account key — infra preference + rotation policy.
3. Exact retention days for `devel`/`dev` (proposed 30/15).
4. Who provisions the account + public-access policy in OKD4 Prod (infra ticket).
