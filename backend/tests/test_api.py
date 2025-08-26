def test_create_tweet_and_like_flow(client):
    HEADERS = {"X-API-Key": "test_api_key"}

    # Создаем твит
    response = client.post(
        "/api/tweets",
        json={"tweet_data": "Hello", "tweet_media_ids": []},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "tweet_id" in data
    tweet_id = data["tweet_id"]

    # Лайкаем твит
    response = client.post(f"/api/tweets/{tweet_id}/likes", headers=HEADERS)
    assert response.status_code == 200, response.text
    assert response.json().get("result") is True

    # Проверяем список твитов (фид)
    response = client.get("/api/tweets", headers=HEADERS)
    assert response.status_code == 200
    tweets = response.json()
    assert "tweets" in tweets
    assert any(tweet["id"] == tweet_id for tweet in tweets["tweets"])
