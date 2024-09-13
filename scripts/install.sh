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

### Set the repository base URL (hardcoded)
BASE_URL="https://api.github.com/repos/rapyuta-robotics/rapyuta-io-cli/releases"

### Get the tag or assume the latest release if no tag is provided
if [ "$#" -eq 0 ]; then
  # Download the latest release if no tag is specified
  echo -e "\033[1;34m⏳ Downloading the latest release...\033[0m"
  API_URL="$BASE_URL/latest"
else
  # Download the specified release tag
  echo -e "\033[1;34m⏳ Downloading release $1...\033[0m"
  TAG="$1"
  API_URL="$BASE_URL/tags/$TAG"
fi

### Fetch release information from GitHub API
RELEASE_DATA=$(curl -s "$API_URL")

### Extract the asset URL from the release data
ASSET_URL=$(echo "$RELEASE_DATA" | grep '"browser_download_url":' | grep '.AppImage' | sed -E 's/.*"browser_download_url":\s*"(https:[^"]*)".*/\1/')

### Check if the asset URL was found
if [ "$ASSET_URL" = "null" ] || [ -z "$ASSET_URL" ]; then
  # Error: No assets found in release
  echo -e "\033[1;31mError: No assets found in release \"$TAG\" for the repository rapyuta-robotics/rapyuta-io-cli\033[0m"
  exit 1
fi

### Set the temporary download location in /tmp
TEMP_PATH=$(mktemp)

### Set a trap to clean up the temporary file on exit, interrupt, or termination
trap 'rm -f "$TEMP_PATH"' EXIT INT TERM

### Download the asset with a progress bar
curl -fSL -o "$TEMP_PATH" --progress-bar "$ASSET_URL"

### Install the asset to /usr/local/bin
sudo install -C -m 755 "$TEMP_PATH" /usr/local/bin/rio

echo -e "\033[1;32m✅ Installation complete! You can now run 'rio auth login' to get started.\033[0m"