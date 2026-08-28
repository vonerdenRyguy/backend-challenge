from fastapi import FastAPI

from app.database import Base, engine
from app.routers import items

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend Challenge")

app.include_router(items.router)


@app.get("/health")
def health():
    return {"status": "ok"}
