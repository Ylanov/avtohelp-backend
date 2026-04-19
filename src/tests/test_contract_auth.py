"""Contract tests for the authorization endpoints.

Frozen against docs/API_CONTRACT.md §1 — any response shape drift here
means the Android app will break.
"""
import pytest

pytestmark = pytest.mark.contract


def test_verify_does_not_leak_sms_code(db, api_client, api_url):
    """POST /authorization/verify must never return the code."""
    resp = api_client.post(
        api_url("authorization/verify"),
        {"phone": "+79000000001", "mode": 0},
        format="json",
    )
    # Empty body is the contract — never {"code": "..."}.
    assert resp.status_code in (200, 201), resp.content
    body = resp.json()
    assert "code" not in body, "SMS code must not be echoed in the response"


def test_verify_requires_phone(db, api_client, api_url):
    resp = api_client.post(api_url("authorization/verify"), {}, format="json")
    assert resp.status_code == 400


def test_auth_requires_phone_and_code(db, api_client, api_url):
    resp = api_client.post(api_url("authorization/auth"), {}, format="json")
    assert resp.status_code == 400


def test_auth_with_test_sms_code_returns_token_and_profile(
    db, api_client, api_url, settings
):
    """When TEST_SMS_CODE=true the dev-fixed code "12345" must work."""
    settings.TEST_SMS_CODE = True
    settings.USE_SMS = False
    phone = "+79000000002"

    # Step 1: request code (creates the SMSCode row with code=12345)
    api_client.post(
        api_url("authorization/verify"),
        {"phone": phone, "mode": 0},
        format="json",
    )

    # Step 2: exchange code for token
    resp = api_client.post(
        api_url("authorization/auth"),
        {"phone": phone, "code": "12345"},
        format="json",
    )
    assert resp.status_code in (200, 201), resp.content
    body = resp.json()
    assert "token" in body
    assert "profile" in body
    profile = body["profile"]
    assert {"id", "first_name", "last_name", "created"} <= set(profile.keys())


def test_logout_requires_auth(db, api_client, api_url):
    resp = api_client.post(api_url("authorization/logout"))
    assert resp.status_code == 401
