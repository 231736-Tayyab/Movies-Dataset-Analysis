"""Flask REST API for the MovieLens SVD recommender."""

from functools import lru_cache
from pathlib import Path

import pandas as pd
from flask import Flask, jsonify, request

from api.model import BASE_DIR, load_model, load_ratings


MOVIES_PATH = BASE_DIR / "movielens_100k.csv"
LIKE_THRESHOLD = 4
DEFAULT_LIMIT = 10
MAX_LIMIT = 30


@lru_cache(maxsize=1)
def get_model():
    return load_model()


@lru_cache(maxsize=1)
def get_catalog() -> tuple[pd.DataFrame, pd.DataFrame]:
    ratings = load_ratings()
    movies = pd.read_csv(MOVIES_PATH)
    movies["title"] = movies["title"].fillna("").astype(str)
    movies["genres"] = movies["genres"].fillna("").astype(str)
    stats = ratings.groupby("movie_id")["rating"].agg(
        n_ratings="count", avg_rating="mean"
    )
    movies = movies[["movie_id", "title", "year", "genres"]].merge(
        stats, on="movie_id", how="left"
    )
    movies["n_ratings"] = movies["n_ratings"].fillna(0).astype(int)
    movies["avg_rating"] = movies["avg_rating"].round(2)
    return ratings, movies


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/api/health")
    def health():
        get_model()
        return jsonify({"status": "ok", "model": "SVD", "rating_scale": [1, 5]})

    @app.get("/api/catalog")
    def catalog():
        ratings, movies = get_catalog()
        users = sorted(int(value) for value in ratings["user_id"].unique())
        return jsonify(
            {
                "movies": [
                    movie_payload(movie)
                    for _, movie in movies.sort_values(
                        "n_ratings", ascending=False
                    ).head(1000).iterrows()
                ],
                "users": users,
                "genres": sorted(
                    {
                        genre
                        for genres in movies["genres"]
                        for genre in genres.split()
                    }
                ),
                "year_range": [
                    int(movies["year"].min()),
                    int(movies["year"].max()),
                ],
            }
        )

    @app.post("/api/predict")
    def predict():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400
        user_id, error = parse_positive_integer(payload, "user_id")
        if error:
            return jsonify({"error": error}), 400
        movie_id, error = parse_positive_integer(payload, "movie_id")
        if error:
            return jsonify({"error": error}), 400
        ratings, movies = get_catalog()
        known_users = set(ratings["user_id"])
        known_movies = set(movies["movie_id"])
        if user_id not in known_users:
            return jsonify({"error": f"Unknown user_id: {user_id}."}), 404
        if movie_id not in known_movies:
            return jsonify({"error": f"Unknown movie_id: {movie_id}."}), 404
        model, _ = get_model()
        estimate = float(model.predict(user_id, movie_id).est)
        movie = movies.loc[movies["movie_id"] == movie_id].iloc[0]
        return jsonify(
            {
                "user_id": user_id,
                "movie": movie_payload(movie),
                "predicted_rating": round(estimate, 4),
                "likely_to_like": estimate >= LIKE_THRESHOLD,
                "like_threshold": LIKE_THRESHOLD,
            }
        )

    @app.post("/api/recommendations")
    def recommendations():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object."}), 400
        user_id, error = parse_positive_integer(payload, "user_id")
        if error:
            return jsonify({"error": error}), 400
        limit, error = parse_positive_integer(
            payload, "limit", default=DEFAULT_LIMIT
        )
        if error:
            return jsonify({"error": error}), 400
        if limit > MAX_LIMIT:
            return jsonify({"error": f"limit must not exceed {MAX_LIMIT}."}), 400
        min_ratings, error = parse_nonnegative_integer(
            payload, "min_ratings", default=30
        )
        if error:
            return jsonify({"error": error}), 400
        genres = payload.get("genres", [])
        if not isinstance(genres, list) or not all(
            isinstance(genre, str) for genre in genres
        ):
            return jsonify({"error": "genres must be a list of strings."}), 400
        year_min, year_max, error = parse_year_range(payload)
        if error:
            return jsonify({"error": error}), 400

        ratings, movies = get_catalog()
        if user_id not in set(ratings["user_id"]):
            return jsonify({"error": f"Unknown user_id: {user_id}."}), 404
        known_genres = {
            genre for values in movies["genres"] for genre in values.split()
        }
        unknown_genres = sorted(set(genres) - known_genres)
        if unknown_genres:
            return jsonify(
                {"error": f"Unknown genre(s): {', '.join(unknown_genres)}."}
            ), 400

        seen = set(ratings.loc[ratings["user_id"] == user_id, "movie_id"])
        pool = movies[
            (movies["n_ratings"] >= min_ratings)
            & (~movies["movie_id"].isin(seen))
            & (
                movies["year"].between(year_min, year_max)
                | movies["year"].isna()
            )
        ].copy()
        if genres:
            pool = pool[
                pool["genres"].apply(
                    lambda values: any(genre in values.split() for genre in genres)
                )
            ]
        model, _ = get_model()
        pool["predicted_rating"] = [
            round(float(model.predict(user_id, int(movie_id)).est), 4)
            for movie_id in pool["movie_id"]
        ]
        result = [
            {
                **movie_payload(row),
                "predicted_rating": row["predicted_rating"],
            }
            for _, row in pool.sort_values(
                "predicted_rating", ascending=False
            ).head(limit).iterrows()
        ]
        return jsonify({"user_id": user_id, "recommendations": result})

    return app


def parse_positive_integer(
    payload: dict, key: str, default: int | None = None
) -> tuple[int | None, str | None]:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        return None, f"{key} must be a positive integer."
    return value, None


def parse_nonnegative_integer(
    payload: dict, key: str, default: int
) -> tuple[int | None, str | None]:
    value = payload.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None, f"{key} must be a non-negative integer."
    return value, None


def parse_year_range(payload: dict) -> tuple[int | None, int | None, str | None]:
    year_min = payload.get("year_min", 1922)
    year_max = payload.get("year_max", 1998)
    if any(isinstance(year, bool) or not isinstance(year, int) for year in (year_min, year_max)):
        return None, None, "year_min and year_max must be integers."
    if year_min > year_max:
        return None, None, "year_min must not exceed year_max."
    return year_min, year_max, None


def movie_payload(movie: pd.Series) -> dict:
    return {
        "movie_id": int(movie["movie_id"]),
        "title": str(movie["title"]),
        "year": int(movie["year"]) if pd.notna(movie["year"]) else None,
        "genres": str(movie["genres"]),
        "average_rating": (
            float(movie["avg_rating"]) if pd.notna(movie["avg_rating"]) else None
        ),
        "rating_count": int(movie["n_ratings"]),
    }


app = create_app()


if __name__ == "__main__":
    if not Path(BASE_DIR / "models" / "movielens_svd").is_file():
        raise SystemExit(
            "Model artifact missing. Run `py -3.12 -m api.train_model` first."
        )
    app.run(host="127.0.0.1", port=5000, debug=False)
