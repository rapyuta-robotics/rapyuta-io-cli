# Contribution Guidelines
## Setup your development environment

The project uses [pipenv](https://pipenv.pypa.io/en/latest/) for
development. It needs to be installed to setup the development environment.

``` bash
pip install pipenv
```

Once Pipenv is installed, a Python virtual environment can be quickly
bootstrapped by running the following commands in the root of the repository.

``` bash
pipenv install --dev
```

This will create a virtual environment in the pipenv's preconfigured location
(if one doesn't already exist). It will also install all the dependencies and
`riocli` package in the location.

To run the CLI (or any command) under the context of Pipenv's virtual
environment, prepend the commands with `pipenv run`
 
```bash
pipenv run rio
```

To run the RIO CLI from the source directly, you can use `riocli` module
directly.

``` bash
pipenv run python -m riocli
```

New dependencies can be installed directly using `pipenv`. This modifies the
`Pipfile` and `Pipfile.lock`.

``` bash
pipenv install {dependency}
```

But using the `pipenv` directly doesn't sync the dependencies in the
`setup.py` file. Please make sure you update the `setup.py` file with
the new dependencies in the `install_requires` section.