import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, Base, engine
from app import models

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Удаляем пользователя с таким же api_key, если есть
    existing_user = db.query(models.User).filter(models.User.api_key == "test_api_key").first()
    if existing_user:
        db.delete(existing_user)
        db.commit()

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
    assert "tweet_id" in tweet
    tweet_id = tweet["tweet_id"]

    # Лайкнуть твит
    r = client.post(f"/api/tweets/{tweet_id}/likes", headers=HEADERS)
    assert r.status_code == 200, r.text
    res = r.json()
    assert res.get("result") is True

    # Проверить список твитов (фид)
    r = client.get("/api/tweets", headers=HEADERS)
    assert r.status_code == 200
    tweets = r.json()
    assert "tweets" in tweets
    assert any(t["id"] == tweet_id for t in tweets["tweets"])
