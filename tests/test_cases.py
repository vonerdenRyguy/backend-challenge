def get_one(client, status):
    resp = client.get("/cases", params={"status": status})
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) > 0
    return cases[0]


def test_list_cases_seeded_and_ordered_by_study_date(client):
    resp = client.get("/cases")
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) >= 8
    dates = [c["studyDate"] for c in cases]
    assert dates == sorted(dates)


def test_list_cases_filter_by_status(client):
    resp = client.get("/cases", params={"status": "PENDING"})
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) > 0
    assert all(c["status"] == "PENDING" for c in cases)


def test_list_cases_filter_by_claimed_by(client):
    in_progress = get_one(client, "IN_PROGRESS")
    username = in_progress["claimedBy"]

    resp = client.get("/cases", params={"claimedBy": username})
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) > 0
    assert all(c["claimedBy"] == username for c in cases)


def test_list_cases_filter_by_status_and_claimed_by(client):
    in_progress = get_one(client, "IN_PROGRESS")
    username = in_progress["claimedBy"]

    resp = client.get("/cases", params={"status": "IN_PROGRESS", "claimedBy": username})
    assert resp.status_code == 200
    cases = resp.json()
    assert len(cases) > 0
    assert all(c["status"] == "IN_PROGRESS" and c["claimedBy"] == username for c in cases)


def test_list_cases_filter_by_unknown_claimed_by_returns_empty(client):
    resp = client.get("/cases", params={"claimedBy": "nobody-with-this-username"})
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_case_success(client):
    pending = get_one(client, "PENDING")
    resp = client.get(f"/cases/{pending['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pending["id"]


def test_get_case_not_found(client):
    resp = client.get("/cases/999999")
    assert resp.status_code == 404


def test_claim_pending_case_succeeds(client):
    pending = get_one(client, "PENDING")

    resp = client.post(f"/cases/{pending['id']}/claim", json={"claimedBy": "jsmith"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "IN_PROGRESS"
    assert body["claimedBy"] == "jsmith"
    assert body["claimedAt"] is not None


def test_claim_already_in_progress_case_fails(client):
    in_progress = get_one(client, "IN_PROGRESS")

    resp = client.post(f"/cases/{in_progress['id']}/claim", json={"claimedBy": "jsmith"})
    assert resp.status_code == 409


def test_claim_completed_case_fails(client):
    completed = get_one(client, "COMPLETED")

    resp = client.post(f"/cases/{completed['id']}/claim", json={"claimedBy": "jsmith"})
    assert resp.status_code == 409


def test_claim_missing_username_fails(client):
    pending = get_one(client, "PENDING")

    resp = client.post(f"/cases/{pending['id']}/claim", json={})
    assert resp.status_code == 400


def test_claim_unknown_username_fails(client):
    pending = get_one(client, "PENDING")

    resp = client.post(f"/cases/{pending['id']}/claim", json={"claimedBy": "no-such-user"})
    assert resp.status_code == 400


def test_claim_missing_case_fails(client):
    resp = client.post("/cases/999999/claim", json={"claimedBy": "jsmith"})
    assert resp.status_code == 404


def test_submit_report_on_in_progress_succeeds(client):
    pending = get_one(client, "PENDING")
    client.post(f"/cases/{pending['id']}/claim", json={"claimedBy": "jsmith"})

    resp = client.post(
        f"/cases/{pending['id']}/report",
        json={"author": "jsmith", "report": "Findings are consistent with..."},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "COMPLETED"
    assert body["report"] == "Findings are consistent with..."


def test_submit_report_on_pending_case_fails(client):
    pending = get_one(client, "PENDING")

    resp = client.post(
        f"/cases/{pending['id']}/report",
        json={"author": "jsmith", "report": "Some findings"},
    )
    assert resp.status_code == 409


def test_submit_report_on_completed_case_fails(client):
    completed = get_one(client, "COMPLETED")
    username = completed["claimedBy"]

    resp = client.post(
        f"/cases/{completed['id']}/report",
        json={"author": username, "report": "Some findings"},
    )
    assert resp.status_code == 409


def test_submit_report_with_empty_body_fails(client):
    pending = get_one(client, "PENDING")
    client.post(f"/cases/{pending['id']}/claim", json={"claimedBy": "jsmith"})

    resp = client.post(
        f"/cases/{pending['id']}/report", json={"author": "jsmith", "report": ""}
    )
    assert resp.status_code == 400


def test_submit_report_by_wrong_employee_fails(client):
    pending = get_one(client, "PENDING")
    client.post(f"/cases/{pending['id']}/claim", json={"claimedBy": "jsmith"})

    resp = client.post(
        f"/cases/{pending['id']}/report",
        json={"author": "agupta", "report": "Someone else's findings"},
    )
    assert resp.status_code == 403
