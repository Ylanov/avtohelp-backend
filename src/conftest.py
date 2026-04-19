"""
Shared pytest fixtures for the contract test suite.

Every endpoint in docs/API_CONTRACT.md must be covered by a test marked
`@pytest.mark.contract`. The suite is the gate that prevents silent
API drift during the ongoing dependency upgrade.
"""
from __future__ import annotations

import factory
import pytest
from phonenumber_field.phonenumber import PhoneNumber
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from account.models import User
from catalog.models import City
from userprofile.models import Profile


# ---------------------------------------------------------------------- factories
class CityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = City

    name = factory.Sequence(lambda n: f"City {n}")


class UserFactory(factory.django.DjangoModelFactory):
    """Creates a User + its associated Profile in one go."""

    class Meta:
        model = User

    phone = factory.Sequence(lambda n: PhoneNumber.from_string(f"+7900000{n:04d}"))
    username = factory.Sequence(lambda n: f"user{n}")
    is_active = True

    @factory.post_generation
    def profile(self, create, extracted, **kwargs):
        if create and not Profile.objects.filter(user=self).exists():
            Profile.objects.create(
                user=self,
                first_name=f"First{self.pk}",
                last_name=f"Last{self.pk}",
            )


# ---------------------------------------------------------------------- fixtures
@pytest.fixture
def api_client() -> APIClient:
    """Plain unauthenticated DRF client."""
    return APIClient()


@pytest.fixture
def user(db) -> User:
    return UserFactory()


@pytest.fixture
def other_user(db) -> User:
    return UserFactory()


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
