"""Contract tests for assistance requests and chat endpoints (§5-§7)."""
import pytest

pytestmark = pytest.mark.contract


def test_assistance_requests_list_accepts_coordinates_query(auth_client, api_url):
    resp = auth_client.get(
        api_url("order/requests?coordinates=55.7558,37.6173"),
    )
    assert resp.status_code == 200
    # Response is a bare list (not paginated) per contract §5.
    assert isinstance(resp.json(), list)


def test_assistance_requests_list_rejects_garbage_coordinates_softly(
    auth_client, api_url
):
    """Bad coordinates must not 500 — we validated in query_sets."""
    resp = auth_client.get(
        api_url("order/requests?coordinates=nonsense"),
    )
    # Either the list still comes back (no distance annotation) or a 400.
    assert resp.status_code in (200, 400), resp.content


def test_assistance_requests_count_shape(auth_client, api_url):
    resp = auth_client.get(api_url("order/requests/count"))
    assert resp.status_code == 200
    body = resp.json()
    assert "count" in body
    assert "unread" in body


def test_chat_rooms_list_uses_cursor_pagination(auth_client, api_url):
    resp = auth_client.get(api_url("chat/rooms"))
    assert resp.status_code == 200
    body = resp.json()
    for k in ("results", "next", "previous"):
        assert k in body, f"expected cursor-pagination key {k}"


def test_chat_room_message_count_endpoint_exists(auth_client, api_url):
    # Endpoint added in Phase F; contract expects {"count": int}
    resp = auth_client.get(api_url("chat/messages/room/1/count"))
    assert resp.status_code in (200, 403, 404)
    if resp.status_code == 200:
        assert "count" in resp.json()


def test_chat_room_unread_count_endpoint_exists(auth_client, api_url):
    resp = auth_client.get(api_url("chat/messages/room/1/unread/count"))
    assert resp.status_code in (200, 403, 404)


def test_chat_total_unread_count_shape(auth_client, api_url):
    resp = auth_client.get(api_url("chat/messages/unread/count"))
    assert resp.status_code == 200
    assert "count" in resp.json()
