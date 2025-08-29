from __future__ import annotations

from fastapi import FastAPI

from .database import engine
from .models import Base
from .routes import tweets, medias, users

# ensure tables exist for tests/local run (Alembic recommended for production)
Base.metadata.create_all(bind=engine)  # type: ignore[attr-defined]

app = FastAPI(title="Microblog")

app.include_router(tweets.router)
app.include_router(medias.router)
app.include_router(users.router)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Microblog Service API"}
