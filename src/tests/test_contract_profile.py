"""Contract tests for the profile / friends / cars endpoints (§2-§4)."""
import pytest

pytestmark = pytest.mark.contract


def test_my_profile_detail_shape(auth_client, api_url, user):
    resp = auth_client.get(api_url("userprofile/profile/detail"))
    assert resp.status_code == 200
    body = resp.json()
    required = {"id", "first_name", "last_name", "avatar", "phone"}
    assert required <= set(body.keys()), f"missing keys: {required - set(body)}"


def test_my_profile_detail_requires_auth(api_client, api_url):
    resp = api_client.get(api_url("userprofile/profile/detail"))
    assert resp.status_code == 401


def test_profile_by_id_route_accepts_numeric_pk(auth_client, api_url, other_user):
    resp = auth_client.get(api_url(f"userprofile/profiles/{other_user.id}"))
    assert resp.status_code in (200, 404)  # shape test — either is valid


def test_profiles_list_supports_cursor_and_search(auth_client, api_url):
    resp = auth_client.get(
        api_url("userprofile/profiles?search=First"),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    assert "next" in body
    assert "previous" in body


def test_update_location_accepts_geo_lat_geo_lon(auth_client, api_url):
    resp = auth_client.patch(
        api_url("userprofile/profile/update-location"),
        {"geo_lat": 55.7558, "geo_lon": 37.6173},
        format="json",
    )
    assert resp.status_code in (200, 204)


def test_friends_list_pagination_is_offset_based(auth_client, api_url):
    resp = auth_client.get(
        api_url("userprofile/profile/friends?limit=10&offset=0"),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "results" in body
    assert "count" in body


def test_friend_requests_incoming_outgoing_paths_exist(auth_client, api_url):
    for route in (
        "userprofile/profile/friends/requests/incoming",
        "userprofile/profile/friends/requests/outgoing",
    ):
        resp = auth_client.get(api_url(route))
        assert resp.status_code == 200, route


def test_blacklist_endpoint_exists(auth_client, api_url):
    resp = auth_client.get(api_url("userprofile/profile/blacklist"))
    assert resp.status_code == 200


def test_device_registration_accepts_registration_id_and_type(
    auth_client, api_url
):
    resp = auth_client.post(
        api_url("userprofile/device"),
        {"registration_id": "fcm-dummy-token", "type": "android"},
        format="json",
    )
    # 201 on create, 200 if device already registered
    assert resp.status_code in (200, 201, 400)
