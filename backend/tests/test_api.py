from fastapi.testclient import TestClient
from microblog.main import app

client = TestClient(app)


import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)

# фиктивные ключи, должны совпадать с тем, что мы создаём в БД (например, в CI миграциях)
HEADERS = {"X-API-Key": "key-alice"}


@pytest.fixture(autouse=True)
def setup_db():
    """Очищаем БД перед каждым тестом"""
    db = SessionLocal()
    db.query(models.Like).delete()
    db.query(models.Follow).delete()
    db.query(models.Media).delete()
    db.query(models.Tweet).delete()
    db.query(models.User).delete()

    # создаём пользователей
    alice = models.User(name="Alice", api_key="key-alice")
    bob = models.User(name="Bob", api_key="key-bob")
    carol = models.User(name="Carol", api_key="key-carol")
    db.add_all([alice, bob, carol])
    db.commit()
    yield
    db.close()



def test_create_tweet_and_like_flow():
    # Создать твит
    r = client.post(
        "/api/tweets",

        json={"tweet_data": "Hello", "tweet_media_ids": []},
    )
    assert r.status_code == 200, r.text
    tweet = r.json()
    assert tweet["content"] == "Hello"
    assert "id" in tweet

    tweet_id = tweet["id"]

    # Поставить лайк
    r2 = client.post(f"/api/tweets/{tweet_id}/likes")
    assert r2.status_code == 200, r2.text
    like = r2.json()
    assert "user_id" in like
    assert "name" in like

    # Проверка, что лайк появился
    r3 = client.post(f"/api/tweets/{tweet_id}/likes")
    assert r3.status_code == 200
    like2 = r3.json()
    assert like2["user_id"] == like["user_id"]


def test_list_users():
    r = client.get("/api/users")
    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)

        headers=HEADERS,
        json={"tweet_data": "Hello", "tweet_media_ids": []},
    )
    assert r.status_code == 200, r.text
    tid = r.json()["tweet_id"]

    # Лайк от автора
    r = client.post(f"/api/tweets/{tid}/likes", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["name"] == "Alice"

    # Лента (никого не фоловлю — пусто)
    r = client.get("/api/tweets", headers=HEADERS)
    assert r.status_code == 200
    assert r.json()["tweets"] == []

    # Подписаться на Alice от Bob
    db = SessionLocal()
    alice = db.query(models.User).filter_by(name="Alice").first()
    bob = db.query(models.User).filter_by(name="Bob").first()
    follow = models.Follow(follower_id=bob.id, followee_id=alice.id)
    db.add(follow)
    db.commit()
    db.close()

    # Теперь Bob видит твит Alice
    r = client.get("/api/tweets", headers={"X-API-Key": "key-bob"})
    assert r.status_code == 200
    tweets = r.json()["tweets"]
    assert len(tweets) == 1
    assert tweets[0]["content"] == "Hello"
    assert tweets[0]["likes"][0]["name"] == "Alice"


def test_me_endpoint():
    r = client.get("/api/users/me", headers=HEADERS)
    assert r.status_code == 200
    me = r.json()
    assert me["name"] == "Alice"
    assert me["api_key"] == "key-alice"
