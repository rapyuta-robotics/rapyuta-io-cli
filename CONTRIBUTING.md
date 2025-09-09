## 🚀 Contribution Guidelines
## 🛠️ Setup your development environment

The project uses [uv](https://docs.astral.sh/uv/) for development. 
It needs to be installed to set up the development environment.

✨ **Let's get started!**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh  # 🐍 Install uv
```

Once `uv` is installed, a Python virtual environment can be quickly
bootstrapped by running the following commands in the root of the repository:

```bash
uv venv                                 # 📦 Create virtual environment
source .venv/bin/activate               # 🔗 Activate environment
```

This will create a virtual environment in `.venv` directory and activate it. 🎉

Next, install all dependencies using the following command:
```bash
uv sync                                 # 📥 Install dependencies
```

To run the CLI (or any command) under the context of the virtual
environment, prepend the commands with `uv run`:
```bash
uv run rio --help                       # 🚦 Run CLI
```

New dependencies can be installed directly using `uv`. This modifies the
`pyproject.toml` and `uv.lock`:
```bash
uv add <package-name>                    # ➕ Add new dependency
```

### 🧹 Linting and formatting
After setting up the environment and syncing dependencies, install pre-commit hooks:
```bash
uv tool install pre-commit
pre-commit install                      # 🪄 Enable pre-commit hooks
```
This will ensure code style and formatting checks are run automatically before each commit. 📝

You can now commit your changes and start contributing! 🚀