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

## CI prerequisites (GitHub OIDC + managed identities)

Uploads authenticate with Entra ID through GitHub OIDC; there is no storage key
or SAS in GitHub. Each workflow runs `azure/login` with a user-assigned managed
identity, and azcopy reuses that session (`AZCOPY_AUTO_LOGIN_TYPE=AZCLI`).

| Name | Kind | Description |
|---|---|---|
| `AZURE_STORAGE_ACCOUNT` | secret | Name of the storage account (`riocliartifacts`). Used to build the azcopy destination URL. |
| `AZURE_TENANT_ID` | variable | Entra tenant of the managed identities. |
| `AZURE_CLIENT_ID_PR` | variable | Client ID of `id-riocli-gha-pr`. Federated subject `repo:rapyuta-robotics/rapyuta-io-cli:pull_request`. Role: Storage Blob Data Contributor on the `dev` container only. |
| `AZURE_CLIENT_ID_PUBLISH` | variable | Client ID of `id-riocli-gha-publish`. Federated subjects `ref:refs/heads/devel` and `ref:refs/heads/main`. Role: Storage Blob Data Contributor on the `devel` and `release` containers only. |

Azure accepts each identity only for its federated subject, so a PR build
cannot write `devel`/`release`. Fork PRs receive no OIDC token and skip the
upload. The identities live in resource group `rio-cli` (OKD4 Prod).

These settings are consumed by:

- `.github/workflows/upload-appimage.yml` — devel pushes (`CHANNEL=devel`) and PR builds (`CHANNEL=dev`).
- `.github/workflows/publish-release.yaml` — tagged releases (`CHANNEL=release`), after release branches are merged to `main`. It also uploads the AppImage as a GitHub release asset.

## Build and publish scripts

The AppImage pipeline is split across several scripts so that building stays free of
CI-only side effects:

| Script | Role |
|---|---|
| `scripts/build-rio-appimage.sh` | Builds the AppImage from the current tree. No network uploads, no edits to tracked files — safe to run by hand. |
| `scripts/stamp-channel-version.sh` | **CI only.** Rewrites `__version__` in `riocli/bootstrap.py` with the channel marker. Requires `CHANNEL`; a no-op for `release` (where `bump-version.sh` already set the version). Run before the build so the marker lands in the wheel. |
| `scripts/publish-rio-appimage.sh` | **CI only.** Installs azcopy and uploads the built AppImage — plus `latest.json` on the `devel`/`release` channels — to the matching container. A no-op when no Azure login happened (e.g. fork PRs). |
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
