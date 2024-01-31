# -*- coding: utf-8 -*-

"""setup.py: setuptools control."""

import re

from setuptools import find_packages, setup

version = re.search(
    '^__version__\s*=\s*"(.*)"', open("riocli/bootstrap.py").read(), re.M
).group(1)

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name="rapyuta-io-cli",
    packages=find_packages(),
    package_data={
        'riocli': [
            'apply/manifests/*.yaml',
            'jsonschema/schemas/*.yaml'
        ]
    },
    include_package_data=True,
    entry_points={"console_scripts": ["rio = riocli.bootstrap:cli"]},
    version=version,
    description="Rapyuta.io CLI Python command line application.",
    long_description=long_descr,
    long_description_content_type='text/markdown',
    author="Rapyuta Robotics",
    author_email="opensource@rapyuta-robotics.com",
    url="http://docs.rapyuta.io",
    install_requires=[
        "pretty-traceback>=2022.1018",
        "argparse>=1.4.0",
        "click-completion>=0.5.2",
        "click-help-colors>=0.9.1",
        "click-repl>=0.2.0",
        "click-spinner>=0.1.10",
        "click-plugins>=1.1.1",
        "click>=8.0.1",
        "dictdiffer>=0.9.0",
        "graphlib-backport>=1.0.3",
        "jinja2>=3.0.1",
        "munch>=2.4.0",
        "python-dateutil>=2.8.2",
        "pytz",
        "pyyaml>=5.4.1",
        "rapyuta-io>=1.14.0",
        "requests>=2.20.0",
        "setuptools",
        "six>=1.13.0",
        "tabulate>=0.8.0",
        "urllib3>=1.23",
        "pyrfc3339>=1.1",
        "directory-tree>=0.0.3.1",
        "yaspin==2.5.0",
        "jsonschema==4.0.0",
        "waiting>=1.4.1",
        "semver>=3.0.0",
        "email-validator==2.0.0.post2",
    ],
    setup_requires=["flake8"],
)
