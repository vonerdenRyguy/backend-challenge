# Backend Challenge Scaffold

FastAPI + SQLAlchemy (sync) + SQLite starter, ready to adapt to whatever the actual prompt asks for.

## Structure

```
app/
  main.py         # FastAPI app, mounts routers, creates tables on startup
  config.py       # settings (reads .env)
  database.py     # engine, session, Base, get_db dependency
  models.py       # SQLAlchemy models (placeholder: Item)
  schemas.py      # Pydantic request/response models
  crud.py         # DB access functions
  routers/
    items.py      # example CRUD endpoints
tests/
  conftest.py     # test DB + TestClient fixtures
  test_items.py   # example tests
```

## Setup

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Run

```
uvicorn app.main:app --reload
```

Docs at http://127.0.0.1:8000/docs

## Test

```
pytest
```

## Adapting to the real prompt

- Rename `Item` -> whatever the domain entity is (models.py, schemas.py, crud.py, routers/items.py, main.py include).
- Add more models/relationships in `models.py` as needed; `Base.metadata.create_all` in `main.py` picks them up automatically.
- Add new routers under `app/routers/` and `include_router` them in `main.py`.
- If the challenge wants auth, add a `security.py` / `auth.py` with OAuth2PasswordBearer + JWT.
- If it wants Postgres instead of SQLite, just change `DATABASE_URL` in `.env` (e.g. `postgresql://user:pass@localhost/db`) and `pip install psycopg2-binary`.
