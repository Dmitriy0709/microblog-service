from __future__ import annotations

import os

from fastapi.testclient import TestClient

# Тестовая БД (sqlite3)
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from app.database import SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Base, User  # noqa: E402

client = TestClient(app)

# Инициализируем чистую схему
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# Создадим пользователей
with SessionLocal() as db:
    me = User(name="Alice", api_key="key-alice")
    bob = User(name="Bob", api_key="key-bob")
    db.add_all([me, bob])
    db.commit()

HEADERS = {"api-key": "key-alice"}

def test_create_tweet_and_like_flow():
    # Создать твит
    r = client.post("/api/tweets", headers=HEADERS, json={"tweet_data": "Hello", "tweet_media_ids": []})
    assert r.status_code == 200, r.text
    tid = r.json()["tweet_id"]

    # Лайк от автора
    r = client.post(f"/api/tweets/{tid}/likes", headers=HEADERS)
    assert r.status_code == 200

    # Лента (никого не фоловлю — пусто)
    r = client.get("/api/tweets", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["tweets"] == []
