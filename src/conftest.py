"""
Shared pytest fixtures for the contract test suite.

Every endpoint in docs/API_CONTRACT.md must be covered by a test marked
`@pytest.mark.contract`. The suite is the gate that prevents silent
API drift during the ongoing dependency upgrade.
"""
from __future__ import annotations

import itertools

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from account.models import User

# Monotonic counter so each fixture call gets a unique phone.
_phone_seq = itertools.count(1)


def _next_phone() -> str:
    # Russian-format 11-digit number.
    return f"+79{next(_phone_seq):09d}"


@pytest.fixture
def api_client() -> APIClient:
    """Plain unauthenticated DRF client."""
    return APIClient()


@pytest.fixture
def user(db) -> User:
    """Create a user the same way prod does — via User.objects.make().

    This also materialises Profile + ProfileLocation, which several views
    dereference as `request.user.profile` / `request.user.profilelocation`.
    A plain .create() would trip RelatedObjectDoesNotExist.
    """
    return User.objects.make(phone=_next_phone())


@pytest.fixture
def other_user(db) -> User:
    return User.objects.make(phone=_next_phone())


@pytest.fixture
def auth_client(db, user) -> APIClient:
    """DRF client pre-authenticated with a Token header (same as Android)."""
    token, _ = Token.objects.get_or_create(user=user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client


@pytest.fixture
def api_url():
    """Build a v1.0.0-prefixed URL for the tests to hit."""
    def _build(path: str) -> str:
        return f"/api/v1.0.0/{path.lstrip('/')}"
    return _build
