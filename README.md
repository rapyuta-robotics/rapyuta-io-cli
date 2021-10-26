# Rapyuta CLI

Rapyuta CLI exposes features of Rapyuta.io platform on the command-line.

The application is written in Python 3 and it is distributed through PyPI for
Python 3 environments.

For Reference on directory structure please refer Please have a look at the
corresponding article:
http://gehrcke.de/2014/02/distributing-a-python-command-line-application/

## Install

Rio CLI is available on PyPI index and can be installed directly by running the
following command.

``` bash
pip install rapyuta-io-cli
```


On Unix-like systems it places the `rio` executable in the user's PATH. On
Windows it places the `rio.exe` in the centralized `Scripts` directory
which should be in the user's PATH.

To install the CLI from source, you can use the `setup.py` script directly.
Clone the repository and from the root of the directory, run the following
command.

``` bash
python setup.py install
```

## Getting Started

To begin using the CLI, it must be authenticated with the Platform.

``` bash
rio auth login
```

The Email and Password can either be given through flags (for scripting
purposes) or interactively through the Prompts.

NOTE: Entering password as a Flag is not recommended because it leaves the
Traces.

## Development

Rio CLI project uses [Pipenv](https://pipenv.pypa.io/en/latest/) for
development. It needs to be installed to setup the development environment.

``` bash
pip install pipenv
```

Once Pipenv is installed, a Python virtual environment can be quickly
bootstrapped by running the following commands in the root of the repository.

``` bash
pipenv install --dev
```

This will create a virtual environment in the Pipenv's preconfigured location
(if one doesn't already exists). It will also install all the dependencies and
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
`setup.py` file. For this, the project uses a utility called `pipenv-setup`
which allows us to sync the dependencies.

``` bash
pipenv run pipenv-setup sync
```
