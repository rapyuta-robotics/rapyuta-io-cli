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

# Making AppRun
sed -i -e 's|/opt/python3.13/bin/python3.13|/usr/bin/rio|g' squashfs-root/AppRun

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
