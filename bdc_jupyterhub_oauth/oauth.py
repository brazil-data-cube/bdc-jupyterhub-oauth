#
# This file is part of Brazil Data Cube JupyterHub OAuth 2.0.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube JupyterHub OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#
"""Brazil Data Cube JupyterHub OAuth Module"""

import base64
import os
import re
from urllib.parse import urlencode

from oauthenticator.oauth2 import OAuthenticator
from tornado.auth import OAuth2Mixin
from tornado.httpclient import HTTPRequest
from traitlets import default, Unicode, List

from .utils import filter_roles_by_application_name


def user_name_pattern(name):
    """Converts the user's email into a valid Unix username

    Args:
        name (str): User Email
    Returns:
        str: formatted email
    Example:
        user_name_pattern('myemail@brazildatacube.org') -> myemail_brazildatacube_org
    """
    return re.sub("[ ,.@]", "_", name)


class BrazilDataCubeOAuthMixin(OAuth2Mixin):
    _OAUTH_USERDATA_URL = "https://brazildatacube.dpi.inpe.br/auth/v1/users/me"
    _OAUTH_AUTHORIZE_URL = "https://brazildatacube.dpi.inpe.br/auth/v1/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://brazildatacube.dpi.inpe.br/auth/v1/oauth/token"


class BrazilDataCubeOAuthenticator(OAuthenticator, BrazilDataCubeOAuthMixin):
    refresh_pre_spawn = True
    enable_auth_state = True
    login_service = "Brazil Data Cube OAuth"

    oauth_application_name = Unicode(
        config=True, help="Name of the application that is registered in the Brazil Data Cube OAuth"
    )

    @default("oauth_application_name")
    def _default_oauth_application_name(self):
        return os.environ.get("OAUTH_APPLICATION_NAME", "jupyter")

    allowed_roles = List(
        Unicode(),
        config=True,
        help="Automatically allow members of selected roles",
    )

    @default("allowed_roles")
    def _allowed_roles_default(self):
        return []  # all roles are valid!

    admin_roles = List(
        Unicode(),
        config=True,
        help="Groups whose members should have Jupyterhub admin privileges",
    )

    @default("admin_roles")
    def _admin_roles_default(self):
        return [""]  # No one is admin

    @default('scope')
    def _scope_default(self):
        return ['openid', 'email']

    @default("authorize_url")
    def _authorize_url_default(self):
        return os.environ.get("OAUTH2_AUTHORIZE_URL", self._OAUTH_AUTHORIZE_URL)

    @default("userdata_url")
    def _userdata_url_default(self):
        return os.environ.get("OAUTH_USERDATA_URL", self._OAUTH_USERDATA_URL)

    @default("token_url")
    def _access_token_url_default(self):
        return os.environ.get("OAUTH_ACCESS_TOKEN_URL", self._OAUTH_ACCESS_TOKEN_URL)

    def _check_user_roles(self, user_profile, valid_roles):
        if valid_roles:
            user_roles = user_profile.get("roles", [])
            application_roles = filter_roles_by_application_name(self.oauth_application_name, user_roles)

            user_roles = list(
                map(lambda x: x.split(":")[1], application_roles)
            )

            return bool(set(user_roles) & set(valid_roles))
        return True

    def _is_user_admin(self, user_profile):
        return self._check_user_roles(user_profile, self.admin_roles)

    def _is_user_roles_valid(self, user_profile):
        return self._check_user_roles(user_profile, self.allowed_roles)

    def _get_headers(self):
        headers = {"Accept": "application/json", "User-Agent": "JupyterHub"}

        b64key = base64.b64encode(
            bytes("{}:{}".format(self.client_id, self.client_secret), "utf8")
        )
        headers.update({"Authorization": "Basic {}".format(b64key.decode("utf8"))})
        return headers

    def _get_token(self, headers, params):
        req = HTTPRequest(
            self.token_url,
            method="POST",
            headers=headers,
            body=urlencode(params),
        )
        return self.fetch(req, "fetching access token")

    def _get_user_data(self, token_response):
        access_token = token_response["access_token"]
        token_type = token_response["token_type"]

        # Determine who the logged in user is
        headers = {
            "Accept": "application/json",
            "User-Agent": "JupyterHub",
            "Authorization": "{} {}".format(token_type, access_token),
        }

        req = HTTPRequest(self.userdata_url, headers=headers)
        return self.fetch(req, "fetching user data")

    @staticmethod
    def _create_auth_state(token_response, user_data_response):
        access_token = token_response["access_token"]
        refresh_token = token_response.get("refresh_token", None)
        scope = token_response.get("scope", "")
        if isinstance(scope, str):
            scope = scope.split(" ")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "oauth_user": user_data_response,
            "scope": scope,
        }

    async def authenticate(self, handler, data=None):
        code = handler.get_argument("code")

        params = dict(
            redirect_uri=self.get_callback_url(handler),
            code=code,
            grant_type="authorization_code",
        )

        headers = self._get_headers()

        token_resp_json = await self._get_token(headers, params)
        user_data_resp_json = await self._get_user_data(token_resp_json)

        if user_data_resp_json and self._is_user_roles_valid(user_data_resp_json):
            user_info = {
                "name": user_data_resp_json['email'],
                "auth_state": self._create_auth_state(token_resp_json, user_data_resp_json),
                "admin": self._is_user_admin(user_data_resp_json),
            }
        else:
            self.log.info(
                "The user does not have the necessary permissions to access the service. Please, check the user roles"
            )

            user_info = None
        return user_info

    def normalize_username(self, username):
        return user_name_pattern(username)


__all__ = (
    "BrazilDataCubeOAuthenticator"
)
