# import  libs and modules
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from app.database import Base, SessionLocal, engine
from app.routers import cases, employees
from app.seed import seed_if_empty

STATIC_DIR = Path(__file__).parent / "static"


Base.metadata.create_all(bind=engine)


#  start FastAPI and populate the database with initial data if empty
@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()
    yield

# initialize FastAPI app with title and lifespan context
app = FastAPI(title="Sirona Case Queue API", lifespan=lifespan)

app.include_router(cases.router)
app.include_router(employees.router)


@app.get("/health")
def health():
    return {"status": "ok"}


# handles basic UI to test
@app.get("/ui", include_in_schema=False)
def ui():
    return FileResponse(STATIC_DIR / "index.html")
