#! /bin/bash

# CI only: stamp a channel marker into riocli/bootstrap.py's __version__ so
# the installed AppImage knows which Azure Blob container to update from.
#
# Requires CHANNEL (release|devel|dev). Release builds are versioned upstream
# by bump-version.sh and are left untouched.
#
# This rewrites a tracked file, which is why it lives here rather than inside
# build-rio-appimage.sh — that script stays safe to run by hand.

set -uxe

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANNEL="${CHANNEL:?CHANNEL must be set (release|devel|dev)}"

if [[ "$CHANNEL" == "release" ]]; then
  echo "release channel: version already set by bump-version.sh, nothing to stamp"
  exit 0
fi

BASE_VERSION=$(grep -m1 '^__version__' "$REPO_ROOT/riocli/bootstrap.py" \
  | sed -E 's/.*"([^"]+)".*/\1/')
SHORT_SHA=$(git -C "$REPO_ROOT" rev-parse --short "${GITHUB_SHA:-HEAD}")

# The channel marker goes in the PEP 440 local-version segment (after +) so
# `uv build` accepts it; a semver-style -prerelease (e.g. -dev.x) is NOT
# PEP 440-valid and fails the wheel build. semver still parses these (the
# segment is build metadata), and channel_for_version reads .build.
if [[ "$CHANNEL" == "devel" ]]; then
  STAMP="${BASE_VERSION}+devel.${SHORT_SHA}"
else
  # dev / PR build: include the sanitized branch identifier
  STAMP="${BASE_VERSION}+dev.$("$REPO_ROOT/scripts/branch-slug.sh").${SHORT_SHA}"
fi

sed -i -E "0,/^__version__.*/s/^__version__.*/__version__ = \"${STAMP}\"/" \
  "$REPO_ROOT/riocli/bootstrap.py"
