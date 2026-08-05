#! /bin/bash
# Local variant of build-rio-appimage.sh: pulls appimagetool and the Python
# AppImage from GitHub releases instead of the internal MinIO bucket (no
# credentials needed), and keeps every downloaded, extracted and generated
# file inside ./local-build/. CI still uses build-rio-appimage.sh.

set -ueo pipefail

APPIMAGETOOL_URL=https://github.com/AppImage/appimagetool/releases/download/1.9.1/appimagetool-x86_64.AppImage
PYTHON_APPIMAGE=python3.13.14-cp313-cp313-manylinux_2_28_x86_64.AppImage
PYTHON_APPIMAGE_URL=https://github.com/niess/python-appimage/releases/download/python3.13/$PYTHON_APPIMAGE

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BUILD=$ROOT/local-build
mkdir -p "$BUILD"

# Make the AppImage runtimes unpack to a temp dir instead of mounting, so
# neither appimagetool nor the built AppImage needs the fusermount helper —
# no FUSE, no sudo, no apt on the developer's machine.
export APPIMAGE_EXTRACT_AND_RUN=1

# Keep the host's ~/.local out of sys.path. The stock python-appimage AppRun
# used during the install steps does not isolate Python, so pip would treat
# packages in the user site as already satisfied and omit them from the
# bundle — and scripts/AppRun runs Python with -I, so they are gone at
# runtime (ModuleNotFoundError for e.g. pydantic).
export PYTHONNOUSERSITE=1

STEP=0
TOTAL=8
step() {
    STEP=$((STEP + 1))
    echo
    echo "==> [$STEP/$TOTAL] $1"
}
done_() { echo "    done: $1"; }

step "Downloading appimagetool and Python AppImage"
wget -nc -P "$BUILD" "$APPIMAGETOOL_URL"
wget -nc -P "$BUILD" "$PYTHON_APPIMAGE_URL"
chmod +x "$BUILD"/*.AppImage
done_ "local-build/appimagetool-x86_64.AppImage, local-build/$PYTHON_APPIMAGE"

step "Building the rio CLI wheel"
(cd "$ROOT" && uv build --out-dir local-build/dist)
WHEEL=$(ls -1t "$BUILD"/dist/rapyuta_io_cli-*.whl | head -1)
done_ "local-build/dist/$(basename "$WHEEL")"

step "Extracting the Python AppImage"
cd "$BUILD"
rm -rf squashfs-root
./"$PYTHON_APPIMAGE" --appimage-extract >/dev/null
done_ "local-build/squashfs-root"

step "Installing the rio CLI into the AppImage"
./squashfs-root/AppRun -m pip install --quiet --upgrade pip
./squashfs-root/AppRun -m pip install --quiet "$WHEEL"
done_ "rio installed"

# Force-reinstall cryptography with a manylinux_2_28 wheel so the AppImage
# works on systems with GLIBC >= 2.28 (Ubuntu 20.04+). Without this, hosts
# with newer GLIBC pull manylinux_2_34 wheels whose _rust.abi3.so requires
# GLIBC_2.33 symbols unavailable on older distros.
step "Pinning cryptography to a manylinux_2_28 wheel"
WHEEL_DIR=$BUILD/wheels
rm -rf "$WHEEL_DIR" && mkdir -p "$WHEEL_DIR"
./squashfs-root/AppRun -m pip download --quiet \
    --only-binary=:all: \
    --platform manylinux_2_28_x86_64 \
    --python-version 3.13 \
    --implementation cp \
    --abi cp313 --abi abi3 --abi none \
    --no-deps \
    --dest "$WHEEL_DIR" \
    cryptography
./squashfs-root/AppRun -m pip install --quiet \
    --force-reinstall --no-deps \
    --no-index --find-links "$WHEEL_DIR" \
    cryptography
done_ "$(ls -1 "$WHEEL_DIR" | tail -1)"

step "Setting up AppRun and rio.desktop"
# Custom AppRun uses Python's -I (isolated mode) to prevent host Python
# environment leakage.
cp "$ROOT/scripts/AppRun" squashfs-root/AppRun
chmod +x squashfs-root/AppRun

DESKTOP=$(echo "$PYTHON_APPIMAGE" | sed -E 's/^(python[0-9.]+)-.*/\1.desktop/')
mv "squashfs-root/usr/share/applications/$DESKTOP" squashfs-root/usr/share/applications/rio.desktop
sed -i -e 's|^Name=.*|Name=rio|g' squashfs-root/usr/share/applications/rio.desktop
sed -i -e 's|^Exec=.*|Exec=rio|g' squashfs-root/usr/share/applications/rio.desktop
sed -i -e 's|^Comment=.*|Comment=A rapyuta.io CLI|g' squashfs-root/usr/share/applications/rio.desktop
rm "squashfs-root/$DESKTOP"
cp squashfs-root/usr/share/applications/rio.desktop squashfs-root/
done_ "AppRun, rio.desktop"

if [[ $# -eq 0 ]] || [[ -z "$1" ]]; then
    export VERSION=$(git -C "$ROOT" rev-parse --short HEAD)
else
    export VERSION=$1
fi

step "Building the AppImage (version $VERSION)"
rm -f rio*.AppImage
./appimagetool-x86_64.AppImage -n squashfs-root/
OUT=$(ls -1t rio*.AppImage | head -1)
done_ "local-build/$OUT"

step "Smoke-testing the AppImage"
./"$OUT" --help >/dev/null
done_ "rio --help ran clean"

echo
echo "AppImage built: local-build/$OUT"
