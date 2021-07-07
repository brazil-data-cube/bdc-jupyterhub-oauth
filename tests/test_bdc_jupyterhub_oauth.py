#
# This file is part of Brazil Data Cube JupyterHub OAuth 2.0.
# Copyright (C) 2021 INPE.
#
# Brazil Data Cube JupyterHub OAuth 2.0 is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
#

"""Unit-test for Brazil Data Cube JupyterHub OAuth Client"""

from oauthenticator.tests.conftest import client, io_loop
from oauthenticator.tests.mocks import setup_oauth_mock
from pytest import fixture, mark

from bdc_jupyterhub_oauth import BrazilDataCubeOAuthenticator


def user_model(role):
    """Return a user model"""

    return {
        "email": "user@email.com",
        "id": 99,
        "name": "User Name",
        "profile": {
            "institution": "User Institute",
            "occupation": "User occupation"
        },
        "roles": [
            f"jupyter:{role}"
        ]
    }


@fixture
def bdc_client(client):
    setup_oauth_mock(
        client,
        host="brazildatacube.dpi.inpe.br",
        access_token_path="/auth/v1/oauth/token",
        user_path="/auth/v1/users/me"
    )

    return client


@mark.asyncio
async def test_user_authenticated_informations(bdc_client):
    authenticator = BrazilDataCubeOAuthenticator()
    handler = bdc_client.handler_for_user(user_model("user"))

    user_info = await authenticator.authenticate(handler)

    assert sorted(user_info) == ["admin", "auth_state", "name"]


@mark.asyncio
async def test_user_authenticated_auth_state_values(bdc_client):
    authenticator = BrazilDataCubeOAuthenticator()
    handler = bdc_client.handler_for_user(user_model("user"))

    user_info = await authenticator.authenticate(handler)
    user_auth_state = user_info["auth_state"]

    assert sorted(user_auth_state.keys()) == ["access_token", "oauth_user", "refresh_token", "scope"]


@mark.asyncio
async def test_when_user_role_is_admin_jupyterhub_should_grant_admin_privileges_to_user(bdc_client):
    authenticator = BrazilDataCubeOAuthenticator(admin_roles=["admin"])
    handler = bdc_client.handler_for_user(user_model("admin"))

    user_info = await authenticator.authenticate(handler)

    assert user_info["admin"]


@mark.asyncio
async def test_when_user_role_is_admin_of_another_application_jupyterhub_should_not_grant_admin_privileges(bdc_client):
    authenticator = BrazilDataCubeOAuthenticator(admin_roles=["admin"], oauth_application_name="jupyterhub")
    handler = bdc_client.handler_for_user(user_model("admin"))

    user_info = await authenticator.authenticate(handler)

    assert not user_info["admin"]


@mark.asyncio
async def test_when_user_role_not_is_admin_jupyterhub_should_not_grant_admin_privileges(bdc_client):
    authenticator = BrazilDataCubeOAuthenticator(admin_roles=["admin"])
    handler = bdc_client.handler_for_user(user_model("user"))

    user_info = await authenticator.authenticate(handler)

    assert not user_info["admin"]


@mark.asyncio
async def test_when_user_role_is_not_allowed_jupyterhub_should_deny_the_user_access(bdc_client):
    authenticator = BrazilDataCubeOAuthenticator(allowed_roles=["user", "admin"])
    handler = bdc_client.handler_for_user(user_model("anotherole"))

    user_info = await authenticator.authenticate(handler)

    assert user_info is None
