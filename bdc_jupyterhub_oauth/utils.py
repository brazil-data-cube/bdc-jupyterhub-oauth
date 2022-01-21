#
# This file is part of Brazil Data Cube JupyterHub OAuth 2.0.
# Copyright (C) 2022 INPE.
#
# Brazil Data Cube JupyterHub OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Brazil Data Cube JupyterHub OAuth Utilities."""

import re


def filter_roles_by_application_name(application_name, roles):
    """Filter the roles that should be scanned based on the application name returned by OAuth.

    Args:
        application_name (str): application name
        roles (list): List of user roles (returned by Brazil Data Cube OAuth Service)
    Returns:
        list: List of application roles
    """
    return list(
        filter(
            lambda x: application_name == x.split(":")[0],
            [] if roles is None else roles,
        )
    )


def convert_user_name_pattern(name):
    """Convert the user's email into a valid Unix username.

    Args:
        name (str): User Email

    Returns:
        str: formatted email

    Example:
        user_name_pattern('myemail@brazildatacube.org') -> myemail_brazildatacube_org
    """
    return re.sub("[ ,.@]", "_", name)
