#
# This file is part of Brazil Data Cube JupyterHub OAuth 2.0.
# Copyright (C) 2022 INPE.
#
# Brazil Data Cube JupyterHub OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube JupyterHub OAuth Client."""

from .oauth import BrazilDataCubeOAuthenticator
from .version import __version__

__all__ = (
    "__version__",
    "BrazilDataCubeOAuthenticator",
)
