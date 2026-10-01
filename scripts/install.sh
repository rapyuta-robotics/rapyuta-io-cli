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
BASE_URL="https://github.com/rapyuta-robotics/rapyuta-io-cli/releases"

### Print the rapyuta.io banner ascii art
echo -n 'ICAgICAgICAgICAgICAgICAgICAgICAgICAgICBfICAgICAgICAgIF8gICAgIC
AgDQogXyBfXyBfXyBfIF8gX18gIF8gICBfIF8gICBffCB8XyBfXyBfICAoXykgX19fIC
ANCnwgJ19fLyBfYCB8ICdfIFx8IHwgfCB8IHwgfCB8IF9fLyBfYCB8IHwgfC8gXyBcIA
0KfCB8IHwgKF98IHwgfF8pIHwgfF98IHwgfF98IHwgfHwgKF98IHxffCB8IChfKSB8DQ
p8X3wgIFxfXyxffCAuX18vIFxfXywgfFxfXyxffFxfX1xfXyxfKF8pX3xcX19fLyANCi
AgICAgICAgICB8X3wgICAgfF9fXy8gICAgICAgICAgICAgICAgICAgICAgICAgIA==' | base64 -d
echo -ne '\n\n'

### Resolve the release tag.
### The unauthenticated GitHub API is rate limited to 60 requests/hour per IP,
### which silently breaks this script behind shared/corporate NATs. The
### /releases/latest redirect is not rate limited, so follow that instead.
if [ "$#" -eq 0 ]; then
  TAG=$(curl -fsSLI -o /dev/null -w '%{url_effective}' "$BASE_URL/latest" | sed 's|.*/tag/||')
else
  TAG="$1"
fi

if [ -z "$TAG" ]; then
  echo -e "\033[1;31mError: could not resolve the latest release tag from $BASE_URL/latest\033[0m"
  exit 1
fi

### Assets are named rio-<version>-x86_64.AppImage, where <version> is the tag
### without its leading "v".
ASSET_URL="$BASE_URL/download/$TAG/rio-${TAG#v}-x86_64.AppImage"

echo -e "\033[1;34m⏳ Downloading release $TAG...\033[0m"

### Set the temporary download location in /tmp
TEMP_PATH=$(mktemp)

### Set a trap to clean up the temporary file on exit, interrupt, or termination
trap 'rm -f "$TEMP_PATH"' EXIT INT TERM

### Download the asset with a progress bar
curl -fSL -o "$TEMP_PATH" --progress-bar "$ASSET_URL"

### Install the asset to /usr/local/bin
sudo install -C -m 755 "$TEMP_PATH" /usr/local/bin/rio

echo -e "\033[1;32m✅ Installation complete! You can now run 'rio auth login' to get started.\033[0m"