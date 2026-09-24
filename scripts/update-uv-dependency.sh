#!/usr/bin/env bash
set -euo pipefail

./scripts/bump-version.sh "${1#[vV]}"
uv lock --upgrade-package rapyuta-io-sdk-v2
