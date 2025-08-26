from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


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

    # Проверка, что повторный лайк возвращает того же пользователя
    r3 = client.post(f"/api/tweets/{tweet_id}/likes")
    assert r3.status_code == 200
    like2 = r3.json()
    assert like2["user_id"] == like["user_id"]


def test_list_users():
    r = client.get("/api/users")
    assert r.status_code == 200
    users = r.json()
    assert isinstance(users, list)
