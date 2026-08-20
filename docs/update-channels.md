# rio update channels

`rio update` updates an AppImage install from Azure Blob Storage (public-read),
keyed by the running binary's version string:

| Version pattern | Channel | Manifest URL |
|---|---|---|
| `X.Y.Z` | `release` | `https://riocliartifacts.blob.core.windows.net/release/latest.json` |
| `X.Y.Z+devel.<sha>` | `devel` | `https://riocliartifacts.blob.core.windows.net/devel/latest.json` |
| `X.Y.Z+dev.<branch>.<sha>` | none | not auto-updatable (development build) |

The channel marker lives in the version's local segment (after `+`) so the
stamped version stays PEP 440-valid for `uv build`; channel detection reads
the build-metadata segment.

pip installs are unaffected — they continue to upgrade from PyPI via the existing `check_for_updates` / `pip_install_cli` path.

## Overriding the base URL

Set `RIO_APPIMAGE_BASE_URL` to redirect all manifest and download requests to a
different host (useful for staging or local testing):

```sh
RIO_APPIMAGE_BASE_URL=https://staging.example.com rio update
```

The env var replaces the entire base; channel and filename are appended as usual
(`<base>/<channel>/latest.json`, `<base>/<channel>/<file>`).

## CI prerequisites (GitHub secrets)

Two secrets must be set in the repository before the blob-upload workflows
will function. **Do not put secret values in source files or commit history.**

| Secret | Description |
|---|---|
| `AZURE_STORAGE_ACCOUNT` | Name of the Azure Storage account that hosts the public-read containers (`riocliartifacts`). Used by CI to construct the azcopy destination URL. |
| `AZURE_SAS_TOKEN` | Write-scoped, container-scoped, time-bound Shared Access Signature. Passed to azcopy for uploads. Anonymous public reads do not use this token. **Expires 2027-06-14 — rotate before that date.** |

These secrets are consumed by:

- `.github/workflows/upload-appimage.yml` — devel pushes (`CHANNEL=devel`) and PR builds (`CHANNEL=dev`).
- `.github/workflows/release.yml` — tagged releases (`CHANNEL=release`), via the `.releaserc.json` prepare step.

## Build and publish scripts

The AppImage pipeline is split across several scripts so that building stays free of
CI-only side effects:

| Script | Role |
|---|---|
| `scripts/build-rio-appimage.sh` | Builds the AppImage from the current tree. No network uploads, no edits to tracked files — safe to run by hand. |
| `scripts/stamp-channel-version.sh` | **CI only.** Rewrites `__version__` in `riocli/bootstrap.py` with the channel marker. Requires `CHANNEL`; a no-op for `release` (where `bump-version.sh` already set the version). Run before the build so the marker lands in the wheel. |
| `scripts/publish-rio-appimage.sh` | **CI only.** Installs azcopy and uploads the built AppImage — plus `latest.json` on the `devel`/`release` channels — to the matching container. A no-op when the Azure secrets are absent (e.g. fork PRs). |
| `scripts/branch-slug.sh` | Prints the sanitized branch identifier. Single source of truth shared by the version stamp, the `dev/<slug>/` upload path, and the PR-comment URL. |

## Azure Blob infra (provisioned)

The storage account is live in **OKD4 Prod**:

| Property | Value |
|---|---|
| Storage account | `riocliartifacts` |
| Resource group | `rio-cli` |
| Region | `japaneast` |
| Base URL | `https://riocliartifacts.blob.core.windows.net` |

### Containers

| Container | Access | Lifecycle policy |
|---|---|---|
| `release` | Anonymous blob read (public) | Permanent — blobs are never auto-deleted |
| `devel` | Anonymous blob read (public) | 30-day auto-delete |
| `dev` | Anonymous blob read (public) | 15-day auto-delete |

### SAS rotation reminder

The write SAS stored in `AZURE_SAS_TOKEN` expires **2027-06-14**. Before that
date, issue a new SAS with equivalent permissions (write, container-scoped) and
update the GitHub secret. Uploads will fail silently after expiry because
azcopy will receive a 403; rotate proactively.
