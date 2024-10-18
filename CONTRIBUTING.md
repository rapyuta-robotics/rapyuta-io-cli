# Contribution Guidelines
## Setup your development environment

The project uses [uv](https://docs.astral.sh/uv/) for development. 
It needs to be installed to set up the development environment.

``` bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once `uv` is installed, a Python virtual environment can be quickly
bootstrapped by running the following commands in the root of the repository.

``` bash
uv venv
source .venv/bin/activate
```

This will create a virtual environment in `.venv` directory and activate it.

Next, install all dependencies using the following command
```bash
uv sync
```

To run the CLI (or any command) under the context of the virtual
environment, prepend the commands with `uv run`
 
```bash
uv run rio --help
```

New dependencies can be installed directly using `uv`. This modifies the
`pyproject.toml` and `uv.lock`.

``` bash
uv add <package-name>
```

### Linting and formatting
You can check and fix the code style by running the following commands.
```bash
uvx ruff check --fix
uvx ruff format
```