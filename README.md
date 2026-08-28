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

## Manual test UI

A small dashboard is served at **http://127.0.0.1:8000/ui** once the server is running (same `uvicorn` command above — no extra setup or separate process needed). It's a single static HTML page that calls the same API endpoints as any other client; it's not part of the graded API surface, just a convenience for clicking through the workflow instead of using curl or Postman.

From there you can:
- View all cases in a table, filterable by status and claimed-by.
- Claim a `PENDING` case by picking an employee and clicking **Claim**.
- Submit a report on an `IN_PROGRESS` case (author + report text).
- Add, rename, or delete employees. Deleting one who has claimed cases pops a confirmation before proceeding (see the deletion assumption below).
- See real API errors surface as a toast (e.g. trying to submit a report as the wrong employee).

## API

- `GET /cases` — list all cases, ordered by `studyDate` ascending. Optional `status` and `claimedBy` (username) query params, combinable with AND.
- `GET /cases/:id` — single case, 404 if missing.
- `GET /employees`, `POST /employees`, `PUT /employees/:id`, `DELETE /employees/:id` (`?force=true` to override the warning when the employee has claimed cases — see assumptions below).
- `POST /cases/:id/claim` — body `{"claimedBy": "username"}`. `PENDING` → `IN_PROGRESS`.
- `POST /cases/:id/report` — body `{"author": "username", "report": "..."}`. `IN_PROGRESS` → `COMPLETED`.

Error status codes used throughout: `400` for missing/invalid input (empty username, unknown username, empty report), `404` for missing resource, `409` for invalid state transitions and username conflicts, `403` when an employee other than the one who claimed the case tries to submit its report.

## Documenting Assumptions

Q: For GET /cases?claimedBy=..., what if the username doesn't match any employee?
Assumption: Returns an empty array rather than a 404/400, consistent with a filter that simply matches nothing.

Q: Should usernames have length limits, character restrictions, or a specific format?
Assumption: No, any non-empty string is accepted, since the spec's only stated constraint is uniqueness.

Q: Should a completed case's report ever be editable?
Assumption: No, once COMPLETED, the case is immutable through the given endpoints. The spec only describes a one-way PENDING → IN_PROGRESS → COMPLETED flow.

Q: Why SQLite + SQLAlchemy instead of a plain in-memory Python list/dict?
Assumption: SQLite was chosen because it gives real persistence between restarts, real query filtering (WHERE status = ...)

Q: Why are routes split into cases.py and employees.py instead of one routes.py?
Assumption: Each file maps to one resource. Splitting means you can open the file for "everything about cases" without scrolling past unrelated employee-management code

Q: How does the API know the caller actually is the employee they claim to be?
Assumption: Out of scope for this exercise

Q: How do new cases actually enter the queue?
Assumption: Cases are only ever seeded, not created through the API, so I assume  in a real system they'd arrive from an imaging system via some ingestion pipeline that's outside this challenge's scope, but I didn't build one since it wasn't asked for.
