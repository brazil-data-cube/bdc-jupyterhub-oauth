#!/usr/bin/env bash
#
# This file is part of Brazil Data Cube JupyterHub OAuth 2.0.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube JupyterHub OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

pydocstyle bdc_jupyterhub_oauth examples tests setup.py && \
isort bdc_jupyterhub_oauth examples tests setup.py --check-only --diff && \
check-manifest --ignore ".travis.yml,.drone.yml,.readthedocs.yml,development_config.py" && \
sphinx-build -qnW --color -b doctest docs/sphinx/ docs/sphinx/_build/doctest && \
pytest
