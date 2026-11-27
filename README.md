# rapyuta.io CLI

The rapyuta.io CLI exposes features of the rapyuta.io cloud platform on the command-line.

The application is written in Python 3, and it is distributed through PyPI for Python 3 environments.

For Reference on directory structure please refer Please have a look at the
corresponding article:
http://gehrcke.de/2014/02/distributing-a-python-command-line-application/

## Installation

### [Recommended] Installing the `AppImage`

You can install the latest `AppImage` using the following command.

```bash
curl -fSsL https://cli.rapyuta.io/install.sh | bash
```

> Note: The `AppImage` is a self-contained executable that can be run on any Linux distribution.
However, it is not supported for non-Linux systems.

### Installing with `uv`

[uv](https://docs.astral.sh/uv/) installs `rio` into its own isolated
environment, with a Python it downloads itself. Unlike the `AppImage`, it does
not need FUSE.

```bash
sudo apt-get install libmagic1                    # Ubuntu/Debian; see below
curl -LsSf https://astral.sh/uv/install.sh | sh   # skip if uv is installed
uv tool install --python 3.13 rapyuta-io-cli
```

- `rio` needs the `libmagic` system library at start-up. Without it, every
  command fails with `ImportError: failed to find libmagic`. Desktop Ubuntu
  usually has it already; minimal and server images do not. On Fedora/RHEL
  install `file-libs`, on macOS `brew install libmagic`.
- `--python 3.13` keeps `rio` on a Python version that CI tests (3.10 to 3.13).
  Without it, uv picks the newest Python it can find.
- uv puts `rio` in `~/.local/bin` (`uv tool dir --bin`). If an `AppImage` is
  still installed at `/usr/local/bin/rio`, check which one runs with
  `type -a rio`.

To upgrade or remove it later:

```bash
uv tool upgrade rapyuta-io-cli
uv tool uninstall rapyuta-io-cli
```

### Installing via `pip`

```bash
pip install rapyuta-io-cli
```

On Unix-like systems it places the `rio` executable in the user's PATH. On
Windows it places the `rio.exe` in the centralized `Scripts` directory
which should be in the user's PATH.

### Installing from source

To install the CLI from source, you can use the `setup.py` script directly.
Clone the repository and from the root of the directory, run the following
command.

```bash
git clone git@github.com:rapyuta-robotics/rapyuta-io-cli.git
cd rapyuta-io-cli
python setup.py install
```

## Getting Started

To begin using the CLI, it must be authenticated with rapyuta.io.

```bash
rio auth login
```

The `email` and `password` can either be given through flags (for scripting purposes) or interactively through the prompt.

> Note: Entering the password as a flag is not recommended because it leaves the traces.

Once set up, run `rio --help` to see the available commands.

## References
* [Development Guide](CONTRIBUTING.md)