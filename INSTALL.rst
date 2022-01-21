..
    This file is part of Brazil Data Cube JupyterHub OAuth 2.0.
    Copyright (C) 2022 INPE.

    Brazil Data Cube JupyterHub OAuth 2.0 is free software; you can redistribute it and/or modify it
    under the terms of the MIT License; see LICENSE file for more details.

Installation
============


Development Installation
------------------------


Clone the software repository::

    git clone https://github.com/brazil-data-cube/bdc-jupyterhub-oauth.git


Go to the source code folder:


.. code-block:: shell

    cd bdc-jupyterhub-oauth


Install in development mode::

    pip3 install -e .[all]


Generate the documentation:


.. code-block:: shell

    python setup.py build_sphinx


The above command will generate the documentation in HTML and it will place it under::

    docs/sphinx/_build/html/
