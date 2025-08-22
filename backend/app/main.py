from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from .database import engine
from .models import Base
from .routes import medias, tweets, users

# Инициализация БД (для простоты — create_all; для продакшена — Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microblog Service", version="1.0.0")

@app.exception_handler(Exception)
async def all_exceptions_handler(request: Request, exc: Exception):
    error = {
        "result": False,
        "error_type": exc.__class__.__name__,
        "error_message": str(exc),
    }
    if isinstance(exc, IntegrityError):
        error["error_type"] = "IntegrityError"
        error["error_message"] = "Integrity violation (possibly duplicate like/follow)"
    return JSONResponse(status_code=400, content=error)

app.include_router(medias.router)
app.include_router(tweets.router)
app.include_router(users.router)

@app.get("/health")
async def health():
    return {"status": "ok"}
