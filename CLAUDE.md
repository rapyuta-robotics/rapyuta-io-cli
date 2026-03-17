# AI Agent Instructions

This file provides guidance to AI coding assistants (Claude Code, GitHub Copilot, etc.) when working with code in this repository.

## What This Is

`rapyuta-io-cli` is the `rio` CLI tool for managing the [rapyuta.io](https://rapyuta.io) cloud robotics platform. The entry point is `riocli/bootstrap.py` (`safe_cli` for production, `cli` for development with full tracebacks).

## Commands

**Setup:**
```bash
uv sync          # Install dependencies
uv run rio       # Run CLI locally
```

**Lint & Format:**
```bash
uv run ruff check .           # Lint
uv run ruff format --check .  # Check formatting
uv run ruff format .          # Auto-format
```

**Tests (integration tests hitting a real platform):**
```bash
uv run pytest tests/main/test_02_auth.py -v               # Single test file
uv run pytest tests/main/test_02_auth.py::TestClass -v    # Single class
uv run pytest tests/main/test_02_auth.py::TestClass::test_method -v  # Single test
just run auth          # Run auth tests via justfile
just run all           # Run all tests sequentially (required order)
just run auth true     # With coverage (outputs to htmlcov/)
```

Tests require `tests/.test.config.json` (auth tokens, platform URLs) and `tests/.password` (credentials). See `tests/README.md` and `tests/.password.example` for setup.

## Architecture

### Module Structure

Each resource type (`auth`, `project`, `device`, `deployment`, etc.) is a Python package under `riocli/` following this pattern:

```
riocli/<resource>/
├── __init__.py    # Click group definition + add_command() calls
├── create.py      # Create subcommand
├── delete.py      # Delete subcommand
├── list.py        # List subcommand
├── inspect.py     # Inspect/show subcommand
└── util.py        # Helpers for this resource
```

The bootstrap registers all resource groups into the top-level `cli` Click group.

### Key Patterns

**Click group with aliasing** — all groups use `AliasedGroup` (from `riocli/utils/`) enabling prefix-matching and explicit aliases (e.g., `o2` → `oauth2`, `sr` → `static-route`).

**Configuration singleton** — `riocli/config/config.py` holds auth state, project context, and client construction. Commands access it via `ctx.obj` (passed through Click context).

**Two SDK clients:**
- `new_client()` → `rapyuta_io` SDK v1 (legacy resources)
- `new_v2_client()` → `rapyuta-io-sdk-v2` (newer resources like file upload, permissions)

**`apply` subsystem** — `riocli/apply/` implements a manifest-based declarative workflow. It supports `apply`, `delete`, `explain`, `graph`, and `template` subcommands operating on YAML manifests. This is the primary way to manage resources as code.

**`compose` module** — wraps Docker Compose semantics for rapyuta.io deployments; reads `docker-compose.yml` and translates to platform resources.

### Shared Utilities

- `riocli/utils/` — display helpers (tables, spinners, errors), Click utilities, REST helpers
- `riocli/constants/` — `Colors`, `Symbols`, exit codes shared across modules
- `riocli/model/` — shared data models
- `riocli/exceptions/` — custom exception hierarchy

### Test Infrastructure

Tests use `pytest` with Click's `CliRunner` (not subprocess). Fixtures in `tests/conftest.py` provide pre-authenticated users (`super_user`, `test_user_11`, `test_user_12`) against the `CliTest` organization on a staging platform. Tests must run in the order defined in `justfile` due to resource dependencies between test files.
