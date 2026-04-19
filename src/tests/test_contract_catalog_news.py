"""Contract tests for catalog, car dictionaries, news and general_info (§4, §8)."""
import pytest

pytestmark = pytest.mark.contract


def test_catalog_cities_route(auth_client, api_url):
    resp = auth_client.get(api_url("catalog/cities"))
    assert resp.status_code == 200


def test_car_marks_accepts_mark_name_filter(auth_client, api_url):
    resp = auth_client.get(api_url("car/marks?mark_name=Toyota"))
    assert resp.status_code == 200


def test_car_colors_include_hex_color_field(auth_client, api_url):
    resp = auth_client.get(api_url("car/colors"))
    assert resp.status_code == 200
    body = resp.json()
    if isinstance(body, list) and body:
        assert "hex_color" in body[0]


def test_car_cars_route(auth_client, api_url):
    resp = auth_client.get(api_url("car/cars"))
    assert resp.status_code == 200


def test_general_info_shape(auth_client, api_url):
    """This endpoint was missing and added in Phase F."""
    resp = auth_client.get(api_url("api/general_info"))
    assert resp.status_code == 200
    body = resp.json()
    assert "cities" in body
    assert "car_colors" in body
    assert "car_makes" in body
    if body["car_makes"]:
        make = body["car_makes"][0]
        assert {"id", "name", "car_models"} <= set(make.keys())


def test_news_list_uses_cursor_pagination(auth_client, api_url):
    resp = auth_client.get(api_url("base/news"))
    assert resp.status_code == 200
    body = resp.json()
    for k in ("results", "next", "previous"):
        assert k in body


def test_recommendations_list_route(auth_client, api_url):
    resp = auth_client.get(api_url("base/recommendations"))
    assert resp.status_code == 200


def test_health_endpoint(api_client):
    """Healthcheck for Docker / k8s."""
    resp = api_client.get("/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
