#!/usr/bin/env bash
set -euo pipefail

VERSION="$1"

# Bump Version
sed "0,/__version__.*/s/__version__.*/__version__ = \"$VERSION\"/" -i riocli/bootstrap.py
sed "0,/;; Version:.*/s/;; Version:.*/;; Version: $VERSION/" -i lisp/tramp-rio.el
sed "0,/;; Version:.*/s/;; Version:.*/;; Version: $VERSION/" -i lisp/rio.el
