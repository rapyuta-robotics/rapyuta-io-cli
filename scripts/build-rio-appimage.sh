#! /bin/bash

set -uxe

# Keep the host's ~/.local out of sys.path. The stock python-appimage AppRun
# used below does not isolate Python, so pip would treat packages in the user
# site as already satisfied and omit them from the bundle, while the final
# AppRun runs Python with -I and cannot see them at runtime.
export PYTHONNOUSERSITE=1

# Downloading Python AppImage and appImage tool databases
BLOB_BASE="https://${AZURE_STORAGE_ACCOUNT}.blob.core.windows.net"
BLOB_PATH="mirror/appimages"

wget --output-document="scripts/appimagetool-x86_64.AppImage" "$BLOB_BASE/$BLOB_PATH/appimagetool-x86_64.AppImage"
wget --output-document="scripts/python3.13.7-cp313-cp313-manylinux_2_28_x86_64.AppImage" "$BLOB_BASE/$BLOB_PATH/python3.13.7-cp313-cp313-manylinux_2_28_x86_64.AppImage"

# Pinned checksums of the mirrored artifacts; update when bumping either one.
sha256sum --check - <<'SUM'
b90f4a8b18967545fda78a445b27680a1642f1ef9488ced28b65398f2be7add2  scripts/appimagetool-x86_64.AppImage
b5c8e6624b17673e86b999666f8d2ddd16c8a78e0127ae572f2a1c702801d45e  scripts/python3.13.7-cp313-cp313-manylinux_2_28_x86_64.AppImage
SUM

chmod +x scripts/*.AppImage

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
