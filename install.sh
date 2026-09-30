#!/usr/bin/env bash

# Copyright 2024 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -o errexit
set -o pipefail

### Function to print usage instructions and exit
usage() {
  echo -e "\033[1;31mUsage: $0 [<release tag>]\033[0m"
  echo -e "\033[1;31mIf no release tag is specified, the latest release will be used.\033[0m"
  echo -e "\033[1;31mExample: $0 v1.0.0\033[0m"
  exit 1
}

### Check if more than one argument is provided
if [ "$#" -gt 1 ]; then
  # Print usage and exit if more than one argument is provided
  usage
fi

### Check that jq is available for parsing the release manifest
if ! command -v jq >/dev/null 2>&1; then
  echo -e "\033[1;31mError: jq is required to install rio. Please install jq and try again.\033[0m"
  echo -e "\033[1;31mUbuntu/Debian: sudo apt-get install jq\033[0m"
  exit 1
fi

### Set the AppImage release channel described in docs/update-channels.md
BASE_URL="${RIO_APPIMAGE_BASE_URL:-https://riocliartifacts.blob.core.windows.net}"
BASE_URL="${BASE_URL%/}"
CHANNEL="release"
MANIFEST_URL="$BASE_URL/$CHANNEL/latest.json"

### Print the rapyuta.io banner ascii art
echo -n 'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICBfICAgICAgICAgIF8gICAgIC
AgDQogXyBfXyBfXyBfIF8gX18gIF8gICBfIF8gICBffCB8XyBfXyBfICAoXykgX19fIC
ANCnwgJ19fLyBfYCB8ICdfIFx8IHwgfCB8IHwgfCB8IF9fLyBfYCB8IHwgfC8gXyBcIA
0KfCB8IHwgKF98IHwgfF8pIHwgfF98IHwgfF98IHwgfHwgKF98IHxffCB8IChfKSB8DQ
p8X3wgIFxfXyxffCAuX18vIFxfXywgfFxfXyxffFxfX1xfXyxfKF8pX3xcX19fLyANCi
AgICAgICAgICB8X3wgICAgfF9fXy8gICAgICAgICAgICAgICAgICAgICAgICAgIA==' | base64 -d
echo -ne '\n\n'

### Get the tag or assume the latest release if no tag is provided
if [ "$#" -eq 0 ]; then
  # Download the latest release if no tag is specified
  echo -e "\033[1;34m⏳ Downloading the latest release...\033[0m"
else
  # Download the specified release tag
  echo -e "\033[1;34m⏳ Downloading release $1...\033[0m"
  TAG="$1"
fi

### Fetch release information from the public release-channel manifest
RELEASE_DATA=$(curl -fsSL "$MANIFEST_URL")

### Parse and validate the required release details from the manifest
if ! MANIFEST_VALUES=$(printf '%s' "$RELEASE_DATA" | jq -er '
  if type != "object"
    or (.version | type) != "string"
    or (.version | length) == 0
    or (.file | type) != "string"
    or (.file | length) == 0
    or (.sha256 | type) != "string"
    or (.sha256 | test("^[0-9A-Fa-f]{64}$") | not)
  then error("missing or invalid version, file, or sha256")
  else [.version, .file, .sha256] | @tsv
  end
'); then
  echo -e "\033[1;31mError: Invalid release manifest at $MANIFEST_URL\033[0m"
  exit 1
fi
IFS=$'\t' read -r VERSION ASSET_FILE EXPECTED_SHA256 <<< "$MANIFEST_VALUES"

### The channel manifest only describes the latest release
if [ -n "${TAG:-}" ] && [ "${TAG#v}" != "$VERSION" ]; then
  echo -e "\033[1;31mError: Release \"$TAG\" is not the latest release ($VERSION).\033[0m"
  exit 1
fi

ASSET_URL="$BASE_URL/$CHANNEL/$ASSET_FILE"

### Set the temporary download location in /tmp
TEMP_PATH=$(mktemp)

### Set a trap to clean up the temporary file on exit, interrupt, or termination
trap 'rm -f "$TEMP_PATH"' EXIT INT TERM

### Download the asset with a progress bar
curl -fSL -o "$TEMP_PATH" --progress-bar "$ASSET_URL"

### Verify the downloaded AppImage against the release manifest
if ! printf '%s  %s\n' "$EXPECTED_SHA256" "$TEMP_PATH" | sha256sum --check --status; then
  echo -e "\033[1;31mError: Checksum verification failed for release $VERSION.\033[0m"
  exit 1
fi

### Install the asset to /usr/local/bin
sudo install -C -m 755 "$TEMP_PATH" /usr/local/bin/rio

echo -e "\033[1;32m✅ Installation complete! You can now run 'rio auth login' to get started.\033[0m"
