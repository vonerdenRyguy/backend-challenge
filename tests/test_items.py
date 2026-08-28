def test_create_and_get_item(client):
    resp = client.post("/items/", json={"name": "widget", "description": "a thing"})
    assert resp.status_code == 201
    item = resp.json()
    assert item["name"] == "widget"

    resp = client.get(f"/items/{item['id']}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "widget"


def test_get_missing_item(client):
    resp = client.get("/items/999")
    assert resp.status_code == 404


def test_update_item(client):
    resp = client.post("/items/", json={"name": "widget"})
    item_id = resp.json()["id"]

    resp = client.patch(f"/items/{item_id}", json={"description": "updated"})
    assert resp.status_code == 200
    assert resp.json()["description"] == "updated"


def test_delete_item(client):
    resp = client.post("/items/", json={"name": "widget"})
    item_id = resp.json()["id"]

    resp = client.delete(f"/items/{item_id}")
    assert resp.status_code == 204

    resp = client.get(f"/items/{item_id}")
    assert resp.status_code == 404
