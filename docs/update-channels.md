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
- `.github/workflows/release.yml` — tagged releases (`CHANNEL=release`).

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
