from tests.fastapi.models import WindowAPI


def test_create_window(api_client):
    payload = {"x": 10, "y": 20}
    resp = api_client.post("/v1/windows/", json=payload)
    resp_json = resp.json()
    assert resp_json["x"] == 10
    assert resp_json["y"] == 20


def test_create_house(api_client):
    payload = {"x": 10, "y": 20}
    resp = api_client.post("/v1/houses/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1


def test_create_house_with_window_link(api_client):
    payload = {"x": 10, "y": 20}
    resp = api_client.post("/v1/windows/", json=payload)

    window_id = resp.json()["_id"]

    payload = {"id": window_id}
    resp = api_client.post("/v1/houses_with_window_link/", json=payload)
    resp_json = resp.json()
    assert resp_json["windows"][0]["collection"] == "WindowAPI"


def test_create_house_2(api_client):
    window = WindowAPI(x=10, y=10)
    window.insert()
    payload = {"name": "TEST", "windows": [str(window.id)]}
    resp = api_client.post("/v1/houses_2/", json=payload)
    resp_json = resp.json()
    assert len(resp_json["windows"]) == 1


def test_revision_id(api_client):
    payload = {"x": 10, "y": 20}
    resp = api_client.post("/v1/windows_2/", json=payload)
    resp_json = resp.json()
    assert "revision_id" not in resp_json
    assert resp_json == {"x": 10, "y": 20, "_id": resp_json["_id"]}
