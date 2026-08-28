def test_list_employees_seeded(client):
    resp = client.get("/employees")
    assert resp.status_code == 200
    employees = resp.json()
    assert len(employees) >= 3


def test_create_employee(client):
    resp = client.post("/employees", json={"username": "newperson"})
    assert resp.status_code == 201
    assert resp.json()["username"] == "newperson"


def test_create_employee_missing_username_fails(client):
    resp = client.post("/employees", json={"username": ""})
    assert resp.status_code == 400


def test_create_employee_duplicate_username_fails(client):
    client.post("/employees", json={"username": "dupe"})
    resp = client.post("/employees", json={"username": "dupe"})
    assert resp.status_code == 409


def test_update_employee(client):
    created = client.post("/employees", json={"username": "before"}).json()

    resp = client.put(f"/employees/{created['id']}", json={"username": "after"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "after"


def test_update_employee_not_found(client):
    resp = client.put("/employees/999999", json={"username": "whoever"})
    assert resp.status_code == 404


def test_update_employee_duplicate_username_fails(client):
    client.post("/employees", json={"username": "taken"})
    created = client.post("/employees", json={"username": "changeling"}).json()

    resp = client.put(f"/employees/{created['id']}", json={"username": "taken"})
    assert resp.status_code == 409


def test_delete_employee_without_cases_succeeds(client):
    created = client.post("/employees", json={"username": "throwaway"}).json()

    resp = client.delete(f"/employees/{created['id']}")
    assert resp.status_code == 204

    resp = client.get("/employees")
    assert all(e["username"] != "throwaway" for e in resp.json())


def test_delete_employee_not_found(client):
    resp = client.delete("/employees/999999")
    assert resp.status_code == 404


def test_delete_employee_with_claimed_cases_warns_without_force(client):
    cases = client.get("/cases", params={"claimedBy": "jsmith"}).json()
    assert len(cases) > 0
    employee_id = [e for e in client.get("/employees").json() if e["username"] == "jsmith"][0]["id"]

    resp = client.delete(f"/employees/{employee_id}")
    assert resp.status_code == 409

    resp = client.get("/employees")
    assert any(e["username"] == "jsmith" for e in resp.json())


def test_delete_employee_with_claimed_cases_force_clears_claim(client):
    cases_before = client.get("/cases", params={"claimedBy": "jsmith"}).json()
    assert len(cases_before) > 0
    employee_id = [e for e in client.get("/employees").json() if e["username"] == "jsmith"][0]["id"]

    resp = client.delete(f"/employees/{employee_id}", params={"force": "true"})
    assert resp.status_code == 204

    for case in cases_before:
        updated = client.get(f"/cases/{case['id']}").json()
        assert updated["claimedBy"] is None
