# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup, find_packages


version = re.search(
    '^__version__\s*=\s*"(.*)"', open("riocli/bootstrap.py").read(), re.M
).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")


setup(
    name="rapyuta-io-cli",
    packages=find_packages(),
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
        "argparse==1.4.0",
        "certifi==2019.9.11",
        "chardet==3.0.4",
        "click==8.0.1",
        "click-completion==0.5.2",
        "click-help-colors==0.9.1",
        "click-repl==0.2.0",
        "click-plugins==1.1.1",
        "click-spinner==0.1.10",
        "concurrencytest==0.1.2",
        "enum34==1.1.6",
        "extras==1.0.0",
        "fixtures==3.0.0",
        "funcsigs==1.0.2",
        "idna==2.6",
        "jinja2==3.0.1; python_version >= '3.6'",
        "linecache2==1.0.0",
        "markupsafe==2.0.1; python_version >= '3.6'",
        "mock==2.0.0",
        "nose==1.3.1",
        "pbr==5.4.4",
        "prompt-toolkit==3.0.20; python_full_version >= '3.6.2'",
        "pyfakefs==3.7",
        "python-dateutil==2.8.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "python-mimeparse==1.6.0",
        "python-subunit==1.4.0",
        "pytz==2021.1",
        "pyyaml==5.4.1",
        "rapyuta-io==0.32.0",
        "requests==2.18.4",
        "shellingham==1.4.0; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "six==1.13.0; python_version >= '2.6' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "testtools==2.4.0",
        "traceback2==1.4.0",
        "unittest2==1.1.0",
        "urllib3==1.22",
        "wcwidth==0.2.5",
    ],
    setup_requires=["flake8"],
)
