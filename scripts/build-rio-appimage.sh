#! /bin/bash

set -uxe

# Installing minio client
wget https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc

# Setting up mc config
./mc alias set local $MINIO_URL $MINIO_ACCESS_KEY $MINIO_SECRET

# Copying Python AppImage and appImage tool databases
./mc cp -r local/appimages/appimagetool-x86_64.AppImage scripts/
./mc cp -r local/appimages/python3.13.7-cp313-cp313-manylinux_2_28_x86_64.AppImage scripts/
chmod +x scripts/*.AppImage

# Install azcopy for Azure Blob uploads (used later in the upload stage).
# Export PATH now (cwd = repo root) so azcopy stays on PATH after cd scripts.
wget -q https://aka.ms/downloadazcopy-v10-linux -O azcopy.tar.gz
tar -xzf azcopy.tar.gz --strip-components=1 --wildcards '*/azcopy'
chmod +x azcopy
export PATH="$PWD:$PATH"

# Stamp a channel suffix into __version__ for non-release builds so the
# installed AppImage knows which Azure Blob container to update from.
# CHANNEL is set by the calling workflow (release|devel|dev). Release
# builds are versioned upstream by bump-version.sh and are left as-is.
# cwd = repo root here, so riocli/bootstrap.py has no leading ../
CHANNEL="${CHANNEL:-dev}"
RAW_BRANCH="${GITHUB_HEAD_REF:-${GITHUB_REF_NAME:-local}}"
# Sanitize the branch to a portable identifier (no slashes/special chars) used
# in BOTH the version stamp and the dev blob path. upload-appimage.yml applies
# the same transform to the PR-comment URL so the link matches the upload.
SAFE_BRANCH=$(echo "$RAW_BRANCH" | tr -c '0-9A-Za-z' '-' | sed -E 's/-+/-/g; s/^-|-$//g')
if [[ "$CHANNEL" != "release" ]]; then
  BASE_VERSION=$(grep -m1 '^__version__' riocli/bootstrap.py | sed -E 's/.*"([^"]+)".*/\1/')
  SHORT_SHA=$(git rev-parse --short "${GITHUB_SHA:-HEAD}")
  # The channel marker goes in the PEP 440 local-version segment (after +)
  # so `uv build` accepts it; a semver-style -prerelease (e.g. -dev.x) is
  # NOT PEP 440-valid and fails the wheel build. semver still parses these
  # (the segment is build metadata), and channel_for_version reads .build.
  if [[ "$CHANNEL" == "devel" ]]; then
    STAMP="${BASE_VERSION}+devel.${SHORT_SHA}"
  else
    # dev / PR build: include the sanitized branch identifier
    STAMP="${BASE_VERSION}+dev.${SAFE_BRANCH}.${SHORT_SHA}"
  fi
  sed -i -E "0,/^__version__.*/s/^__version__.*/__version__ = \"${STAMP}\"/" riocli/bootstrap.py
fi

# Creating rio-cli wheel
uv build
cp dist/rapyuta_io_cli-*.whl scripts/

# Enabling FUSE
sudo apt-get update
sudo apt-get install fuse libfuse2

# Extracting Python AppImage
cd scripts
./python3.13.7-cp313-cp313-manylinux_2_28_x86_64.AppImage --appimage-extract

# Bundling RIO CLI in AppImage
./squashfs-root/AppRun -m pip install --upgrade pip
./squashfs-root/AppRun -m pip install rapyuta_io_cli-*.whl

# Force-reinstall cryptography with a manylinux_2_28 wheel so the
# AppImage works on systems with GLIBC >= 2.28 (Ubuntu 20.04+).
# Without this, CI hosts with newer GLIBC pull manylinux_2_34 wheels
# whose _rust.abi3.so requires GLIBC_2.33 symbols unavailable on
# older distros.
WHEEL_DIR=/tmp/rio-wheels
rm -rf "$WHEEL_DIR" && mkdir -p "$WHEEL_DIR"
./squashfs-root/AppRun -m pip download \
    --only-binary=:all: \
    --platform manylinux_2_28_x86_64 \
    --python-version 3.13 \
    --implementation cp \
    --abi cp313 --abi abi3 --abi none \
    --no-deps \
    --dest "$WHEEL_DIR" \
    cryptography
./squashfs-root/AppRun -m pip install \
    --force-reinstall --no-deps \
    --no-index --find-links "$WHEEL_DIR" \
    cryptography

# Replacing AppRun with a custom script that uses Python's -I (isolated
# mode) to completely prevent host Python environment leakage.
cp AppRun squashfs-root/AppRun
chmod +x squashfs-root/AppRun

# Making rio.desktop
mv squashfs-root/usr/share/applications/python3.13.7.desktop squashfs-root/usr/share/applications/rio.desktop
sed -i -e 's|^Name=.*|Name=rio|g' squashfs-root/usr/share/applications/rio.desktop
sed -i -e 's|^Exec=.*|Exec=rio|g' squashfs-root/usr/share/applications/rio.desktop
sed -i -e 's|^Comment=.*|Comment=A rapyuta.io CLI|g' squashfs-root/usr/share/applications/rio.desktop
rm squashfs-root/python3.13.7.desktop
cp squashfs-root/usr/share/applications/rio.desktop squashfs-root/

# Setting Version
if [[ $# -eq 0 ]] || [[ -z "$1" ]] ; then
  export VERSION=$(git rev-parse --short $GITHUB_SHA)
else
  export VERSION=$1
fi

# Building AppImage
./appimagetool-x86_64.AppImage -n squashfs-root/

APPIMAGE_FILE=$(find . -maxdepth 1 -name 'rio*.AppImage' | head -n1 | sed 's|^\./||')
[[ -n "$APPIMAGE_FILE" ]] || { echo "ERROR: no rio*.AppImage found in scripts/"; exit 1; }

# Upload the built AppImage to the channel's Azure Blob container.
# Download stays anonymous (public-read); upload authenticates with a
# write-scoped SAS token. Required env: CHANNEL, AZURE_STORAGE_ACCOUNT,
# AZURE_SAS_TOKEN.
# dev builds  -> dev/<safe-branch>/<file>, no manifest (not an update channel)
# devel/release builds -> <channel>/<file> + latest.json manifest
if [[ -n "${AZURE_STORAGE_ACCOUNT:-}" && -n "${AZURE_SAS_TOKEN:-}" ]]; then
  # silence trace: SAS token is in the URL
  set +x
  if [[ "$CHANNEL" == "dev" ]]; then
    DEST="https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/dev/${SAFE_BRANCH}/${APPIMAGE_FILE}?${AZURE_SAS_TOKEN}"
    azcopy copy "${APPIMAGE_FILE}" "${DEST}" --overwrite=true
  else
    SHA256=$(sha256sum "${APPIMAGE_FILE}" | cut -d' ' -f1)
    VERSION=$(grep -m1 '^__version__' ../riocli/bootstrap.py | sed -E 's/.*"([^"]+)".*/\1/')
    cat > latest.json <<EOF
{"version": "${VERSION}", "file": "${APPIMAGE_FILE}", "sha256": "${SHA256}"}
EOF
    BASE="https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/${CHANNEL}"
    azcopy copy "${APPIMAGE_FILE}" "${BASE}/${APPIMAGE_FILE}?${AZURE_SAS_TOKEN}" --overwrite=true
    azcopy copy "latest.json" "${BASE}/latest.json?${AZURE_SAS_TOKEN}" --overwrite=true
  fi
  set -x
else
  echo "AZURE_STORAGE_ACCOUNT / AZURE_SAS_TOKEN not set — skipping blob upload"
fi
