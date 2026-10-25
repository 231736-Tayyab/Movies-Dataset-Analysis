import pytest

from api import app as api_module
from api.model import load_model, load_ratings


class FakeModel:
    def predict(self, _user_id, _movie_id):
        return type("Prediction", (), {"est": 4.25})()


@pytest.fixture
def client(monkeypatch):
    api_module.get_catalog.cache_clear()
    monkeypatch.setattr(api_module, "get_model", lambda: (FakeModel(), None))
    with api_module.create_app().test_client() as test_client:
        yield test_client
    api_module.get_catalog.cache_clear()


def test_health_returns_model_and_rating_scale(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "model": "SVD",
        "rating_scale": [1, 5],
    }


def test_catalog_returns_user_movie_and_filter_metadata(client):
    response = client.get("/api/catalog")
    body = response.get_json()

    assert response.status_code == 200
    assert 1 in body["users"]
    assert body["movies"]
    assert {"movie_id", "title", "genres", "rating_count"} <= set(
        body["movies"][0]
    )
    assert "Action" in body["genres"]


def test_prediction_returns_rating_and_liked_verdict(client):
    response = client.post(
        "/api/predict", json={"user_id": 1, "movie_id": 1}
    )
    body = response.get_json()

    assert response.status_code == 200
    assert body["predicted_rating"] == 4.25
    assert body["likely_to_like"] is True
    assert body["movie"]["title"]


def test_saved_artifact_runs_through_prediction_endpoint(client, monkeypatch):
    monkeypatch.setattr(api_module, "get_model", load_model)

    response = client.post(
        "/api/predict", json={"user_id": 1, "movie_id": 1}
    )

    assert response.status_code == 200
    assert response.get_json()["predicted_rating"] == pytest.approx(4.283, abs=0.01)


@pytest.mark.parametrize(
    "payload",
    [
        [],
        {"user_id": True, "movie_id": 1},
        {"user_id": 0, "movie_id": 1},
        {"user_id": 1, "movie_id": "1"},
        {"user_id": 999999, "movie_id": 1},
        {"user_id": 1, "movie_id": 999999},
    ],
)
def test_prediction_rejects_invalid_or_unknown_ids(client, payload):
    response = client.post("/api/predict", json=payload)

    assert response.status_code in (400, 404)
    assert "error" in response.get_json()


def test_recommendations_exclude_seen_movies_and_obey_filters(client):
    seen_movie_ids = set(
        load_ratings().loc[lambda ratings: ratings["user_id"] == 1, "movie_id"]
    )
    response = client.post(
        "/api/recommendations",
        json={
            "user_id": 1,
            "limit": 5,
            "min_ratings": 1,
            "genres": ["Action"],
            "year_min": 1980,
            "year_max": 1998,
        },
    )
    body = response.get_json()

    assert response.status_code == 200
    assert len(body["recommendations"]) <= 5
    assert all("Action" in movie["genres"].split() for movie in body["recommendations"])
    assert all(
        movie["movie_id"] not in seen_movie_ids
        for movie in body["recommendations"]
    )
    assert all(
        movie["year"] is None or 1980 <= movie["year"] <= 1998
        for movie in body["recommendations"]
    )


@pytest.mark.parametrize(
    "payload",
    [
        {"user_id": 1, "limit": 31},
        {"user_id": 1, "limit": True},
        {"user_id": 1, "genres": "Action"},
        {"user_id": 1, "genres": ["not-a-genre"]},
        {"user_id": 1, "year_min": 2000, "year_max": 1990},
        {"user_id": 999999},
    ],
)
def test_recommendations_reject_invalid_request(client, payload):
    response = client.post("/api/recommendations", json=payload)

    assert response.status_code in (400, 404)
    assert "error" in response.get_json()
