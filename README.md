# Sirona Case Queue API

FastAPI + SQLAlchemy + SQLite API for the radiologist case queue challenge.

## Structure

```
app/
  main.py         # FastAPI app, mounts routers, seeds DB on startup
  config.py       # settings (reads .env)
  database.py     # engine, session, Base, get_db dependency
  models.py       # SQLAlchemy models: Employee, Case (+ Modality/CaseStatus enums)
  schemas.py      # Pydantic request/response models
  crud.py         # business logic: filtering, claim, report, employee CRUD
  seed.py         # seeds 3 employees + 8 cases on first startup
  routers/
    cases.py      # GET /cases, GET /cases/:id, POST /cases/:id/claim, POST /cases/:id/report
    employees.py  # GET/POST/PUT/DELETE /employees
  static/
    index.html    # optional manual-test dashboard, served at /ui (not part of the graded API)
tests/
  conftest.py     # isolated per-test SQLite DB + seeded TestClient fixture
  test_cases.py   # claim/report/list/get scenarios
  test_employees.py
```

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

(`.env` is optional — `DATABASE_URL` defaults to a local SQLite file if you don't create one. Copy `.env.example` to `.env` only if you want to override it.)

## Run

```
uvicorn app.main:app --reload
```

That single command starts the server and seeds the database on first run (skipped on later runs since the tables are no longer empty). No manual DB setup needed.

- API root: http://127.0.0.1:8000
- Interactive Swagger docs: http://127.0.0.1:8000/docs
- Simple manual-test dashboard: http://127.0.0.1:8000/ui

On first startup the DB is seeded with 3 employees (`jsmith`, `agupta`, `mchen`) and 8 cases (4 `PENDING`, 2 `IN_PROGRESS`, 2 `COMPLETED`).

## Test

```
pytest
```

29 tests covering all required scenarios (claim/report transitions and their error cases, plus employee CRUD and list filtering).

## API

- `GET /cases` — list all cases, ordered by `studyDate` ascending. Optional `status` and `claimedBy` (username) query params, combinable with AND.
- `GET /cases/:id` — single case, 404 if missing.
- `GET /employees`, `POST /employees`, `PUT /employees/:id`, `DELETE /employees/:id` (`?force=true` to override the warning when the employee has claimed cases — see assumptions below).
- `POST /cases/:id/claim` — body `{"claimedBy": "username"}`. `PENDING` → `IN_PROGRESS`.
- `POST /cases/:id/report` — body `{"author": "username", "report": "..."}`. `IN_PROGRESS` → `COMPLETED`.

Error status codes used throughout: `400` for missing/invalid input (empty username, unknown username, empty report), `404` for missing resource, `409` for invalid state transitions and username conflicts, `403` when an employee other than the one who claimed the case tries to submit its report.

## Documenting Assumptions

Q: The spec says a case's `claimedBy` "references the employees table" but "the API accepts and exposes username, not the internal id." How should this be modeled?
Assumption: Internally, `Case.claimed_by_id` is a foreign key to `Employee.id`. On every response, it's resolved to the current `username` of that employee. The `claim` and `report` request bodies take a username and look up the matching employee server-side.

Q: What does `DELETE /employees/:id` do if that employee has claimed cases (in progress or completed)?
Assumption: Deleting is a two-step confirm: calling `DELETE /employees/:id` when the employee has any associated cases returns `409` with a warning listing the affected case IDs, and does *not* delete. Calling it again with `?force=true` proceeds with the deletion and clears `claimedBy` (sets it to `null`) on those cases, since the employee record — and therefore the username — no longer exists to resolve to.

Q: `GET /cases?claimedBy=...` — what if the username doesn't match any employee?
Assumption: Returns an empty array rather than a 404/400, consistent with a filter that simply matches nothing.

Q: What HTTP status codes should the various error conditions use, since the spec only says "an appropriate error"?
Assumption: `404` for a case/employee that doesn't exist, `400` for missing/invalid input (empty or unknown username, empty report body, empty employee username), `409` for a case in the wrong status for the requested transition or a username conflict on create/update, and `403` specifically for "you're not the employee who claimed this case."

Q: What data types should `Case.id` / `Employee.id` use, given the spec allows "string or int"?
Assumption: Auto-incrementing integers, since nothing in the spec requires client-supplied or globally-unique string IDs.

Q: Should `GET /cases` support pagination?
Assumption: No — the spec doesn't ask for it and 8 seed records don't need it. All matching cases are returned in one array.

Q: Is `claimedBy` username matching case-sensitive?
Assumption: Yes, exact string match, since usernames are treated as opaque identifiers rather than display text.
