import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app import models

client = TestClient(app)


# Перед тестами чистим БД и создаём пользователя с api_key
@pytest.fixture(autouse=True, scope="module")
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user = models.User(name="TestUser", api_key="test_api_key")
    db.add(user)
    db.commit()
    db.refresh(user)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


HEADERS = {"X-API-Key": "test_api_key"}


def test_create_tweet_and_like_flow():
    # Создать твит
    r = client.post(
        "/api/tweets",
        json={"tweet_data": "Hello", "tweet_media_ids": []},
        headers=HEADERS,
    )
    assert r.status_code == 200, r.text
    tweet = r.json()
    assert tweet["tweet_data"] == "Hello"

    tweet_id = tweet["id"]

    # Лайкнуть твит
    r = client.post(f"/api/tweets/{tweet_id}/likes", headers=HEADERS)
    assert r.status_code == 200, r.text
    like = r.json()
    assert like["tweet_id"] == tweet_id

    # Проверить список твитов
    r = client.get("/api/tweets", headers=HEADERS)
    assert r.status_code == 200
    tweets = r.json()
    assert len(tweets) == 1
    assert tweets[0]["id"] == tweet_id

    # Проверить список лайков
    r = client.get(f"/api/tweets/{tweet_id}/likes", headers=HEADERS)
    assert r.status_code == 200
    likes = r.json()
    assert len(likes) == 1
