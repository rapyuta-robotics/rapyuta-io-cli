#! /bin/bash

# CI only: upload the AppImage built by build-rio-appimage.sh to its channel's
# Azure Blob container. Downloads are anonymous (public-read); uploads
# authenticate with a write-scoped SAS token.
#
# Required env: CHANNEL, AZURE_STORAGE_ACCOUNT, AZURE_SAS_TOKEN.
#
#   dev builds           -> dev/<branch-slug>/<file>, no manifest (dev is not
#                           an update channel)
#   devel/release builds -> <channel>/<file> + latest.json manifest

set -uxe

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANNEL="${CHANNEL:?CHANNEL must be set (release|devel|dev)}"

if [[ -z "${AZURE_STORAGE_ACCOUNT:-}" || -z "${AZURE_SAS_TOKEN:-}" ]]; then
  echo "AZURE_STORAGE_ACCOUNT / AZURE_SAS_TOKEN not set — skipping blob upload"
  exit 0
fi

cd "$REPO_ROOT/scripts"

APPIMAGE_FILE=$(find . -maxdepth 1 -name 'rio*.AppImage' | head -n1 | sed 's|^\./||')
[[ -n "$APPIMAGE_FILE" ]] || { echo "ERROR: no rio*.AppImage found in scripts/"; exit 1; }

# Installing azcopy
wget -q https://aka.ms/downloadazcopy-v10-linux -O azcopy.tar.gz
tar -xzf azcopy.tar.gz --strip-components=1 --wildcards '*/azcopy'
chmod +x azcopy
export PATH="$PWD:$PATH"

BASE="https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"

# silence trace: the SAS token is part of the destination URL
set +x
if [[ "$CHANNEL" == "dev" ]]; then
  SLUG=$("$REPO_ROOT/scripts/branch-slug.sh")
  azcopy copy "${APPIMAGE_FILE}" \
    "${BASE}/dev/${SLUG}/${APPIMAGE_FILE}?${AZURE_SAS_TOKEN}" --overwrite=true
else
  SHA256=$(sha256sum "${APPIMAGE_FILE}" | cut -d' ' -f1)
  # The stamped __version__ the AppImage reports at runtime. Distinct from the
  # VERSION that build-rio-appimage.sh exports for appimagetool's file naming.
  MANIFEST_VERSION=$(grep -m1 '^__version__' "$REPO_ROOT/riocli/bootstrap.py" \
    | sed -E 's/.*"([^"]+)".*/\1/')
  cat > latest.json <<JSON
{"version": "${MANIFEST_VERSION}", "file": "${APPIMAGE_FILE}", "sha256": "${SHA256}"}
JSON
  azcopy copy "${APPIMAGE_FILE}" \
    "${BASE}/${CHANNEL}/${APPIMAGE_FILE}?${AZURE_SAS_TOKEN}" --overwrite=true
  azcopy copy "latest.json" \
    "${BASE}/${CHANNEL}/latest.json?${AZURE_SAS_TOKEN}" --overwrite=true
fi
set -x
