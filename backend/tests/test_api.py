import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Заголовки с API-ключом для Alice (добавляется при инициализации БД)
HEADERS = {"X-API-Key": "key-alice"}


def test_create_tweet_and_like_flow():
    # Создать твит
    r = client.post(
        "/api/tweets",
        headers=HEADERS,
        json={"tweet_data": "Hello", "tweet_media_ids": []},
    )
    assert r.status_code == 200, r.text
    tid = r.json()["tweet_id"]

    # Лайк от автора
    r = client.post(f"/api/tweets/{tid}/likes", headers=HEADERS)
    assert r.status_code == 200

    # Лента (никого не фоловлю — пусто)
    r = client.get("/api/tweets", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["tweets"] == []

    # Теперь подпишусь на себя (искусственно)
    client.post(f"/api/users/{1}/follow", headers=HEADERS)

    # Лента снова
    r = client.get("/api/tweets", headers=HEADERS)
    assert r.status_code == 200
    data = r.json()
    assert len(data["tweets"]) == 1
    tweet = data["tweets"][0]
    assert tweet["content"] == "Hello"
    assert tweet["likes"][0]["user_id"] == 1
