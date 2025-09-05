default:
  @just --list

[doc("Run tests across multiple Python versions using uv and rio")]
test:
    #!/bin/bash
    set -euo pipefail

    PYTHON_VERSIONS=("3.8" "3.9" "3.10" "3.11" "3.12" "3.13")

    uv sync
    source .venv/bin/activate

    for version in "${PYTHON_VERSIONS[@]}"; do
        echo "Checking for Python $version"
        uv sync -p "$version"
        rio --help
    done

[doc("Run ruff linter checks on riocli")]
check:
    @ruff check riocli

[doc("Format code in riocli (pass extra flags if needed)")]
format +FLAGS:
    @ruff format riocli {{FLAGS}}

[doc("Check formatting without making changes (runs: ruff format --check)")]
format-check:
    just format --check
