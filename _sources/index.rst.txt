Welcome to rapyuta.io CLI documentation!
========================================

The rapyuta.io CLI (aka riocli) exposes features of Rapyuta.io platform on the command-line.

The application is written in Python 3 and it is distributed through PyPI for
Python 3 environments.

Installation
--------------

Installing the ``AppImage``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can install the latest ``AppImage`` on your Linux systems using the following command.

.. code:: bash

    curl -fSsL https://cli.rapyuta.io/install.sh | bash

Installing via ``pip``
~~~~~~~~~~~~~~~~~~~~~~

Alternatively, you can install the CLI using ``pip``.

.. code:: bash

    pip install rapyuta-io-cli


On Unix-like systems it places the ``rio`` executable in the user's PATH. On
Windows it places the ``rio.exe`` in the centralized ``Scripts`` directory which
should be in the user's PATH.

Installing from source
~~~~~~~~~~~~~~~~~~~~~~~

To install the CLI from source, you can use the ``setup.py`` script directly.
Clone the repository and from the root of the directory, run the following
command.

.. code:: bash

        git clone git@github.com:rapyuta-robotics/rapyuta-io-cli.git
        cd rapyuta-io-cli
        python setup.py install


Getting Started
---------------

To begin using the CLI, it must be authenticated with rapyuta.io.

.. code:: bash

        rio auth login

The ``email`` and ``password`` can either be given through flags (for scripting
purposes) or interactively through the Prompts.

.. note::

    Entering ``password`` as a flag is not recommended because it leaves the traces.

Commands
--------

Rapyuta CLI has commands for all rapyuta.io resources. You can read more about the sub-commands on there pages:

.. toctree::
   :maxdepth: 1

   Apply <apply>
   Authentication <auth>
   Chart <chart>
   Completion <completion>
   ConfigTree <config_tree>
   Deployment <deployment>
   Device <device>
   Disk <disk>
   Hardware-in-Loop <hwil>
   Network <network>
   Organization <organization>
   Package <package>
   Parameter <parameter>
   Project <project>
   Rosbag  <rosbag>
   Secret <secret>
   Static Route <static_route>
   User Group <usergroup>
   VPN <vpn>



Indices and tables
==================
* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
