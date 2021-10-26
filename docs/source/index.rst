Welcome to Rapyuta.io CLI documentation!
========================================

Rapyuta CLI exposes features of Rapyuta.io platform on the command-line.

The application is written in Python 3 and it is distributed through PyPI for
Python 3 environments.

Installation
--------------

It is recommended you install the latest Python SDK using pip

.. code:: bash    
    
    pip install rapyuta-io

Rio CLI is available on PyPI index and can be installed directly by running the
following command.

.. code:: bash

    pip install rapyuta-io-cli

On Unix-like systems it places the ``rio`` executable in the user's PATH. On
Windows it places the ``rio.exe`` in the centralized ``Scripts`` directory which
should be in the user's PATH.

To install the CLI from source, you can use the ``setup.py`` script directly.
Clone the repository and from the root of the directory, run the following
command.

.. code:: bash

        python setup.py install

Getting Started
---------------

To begin using the CLI, it must be authenticated with the Platform.

.. code:: bash

        rio auth login

The Email and Password can either be given through flags (for scripting
purposes) or interactively through the Prompts.

NOTE: Entering password as a Flag is not recommended because it leaves the
Traces.

Commands
--------

Rapyuta CLI has commands for all rapyuta.io resources. You can read more about the sub-commands on there pages:

.. toctree::
   :maxdepth: 1

   Authentication <auth>
   Build <build>
   Completion <completion>
   Deployment <deployment>
   Device <device>
   Network <network>
   Package <package>
   Project <project>
   Rosbag  <rosbag>
   Secret <secret>
   Static Routes <static_route>



Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
