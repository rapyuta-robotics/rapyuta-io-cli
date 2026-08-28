#! /bin/bash

# Print a portable identifier for the branch being built.
#
# Single source of truth: used by stamp-channel-version.sh for the version
# stamp, by publish-rio-appimage.sh for the dev blob path, and by
# upload-appimage.yml for the PR-comment URL. Keeping one implementation
# means the commented link cannot drift from the actual upload path.

set -ue

RAW_BRANCH="${GITHUB_HEAD_REF:-${GITHUB_REF_NAME:-local}}"
SLUG=$(echo "$RAW_BRANCH" | tr -c '0-9A-Za-z' '-' | sed -E 's/-+/-/g; s/^-|-$//g')
echo "$SLUG"
