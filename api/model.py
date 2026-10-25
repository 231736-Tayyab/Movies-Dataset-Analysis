"""Train, persist, and load the MovieLens SVD recommendation model."""

from pathlib import Path

import pandas as pd
from surprise import Dataset, Reader, SVD, dump


BASE_DIR = Path(__file__).resolve().parents[1]
RATINGS_PATH = BASE_DIR / "u.data"
ARTIFACT_PATH = BASE_DIR / "models" / "movielens_svd"
SVD_PARAMS = {
    "n_factors": 100,
    "n_epochs": 20,
    "lr_all": 0.005,
    "reg_all": 0.02,
    "random_state": 42,
}


def load_ratings() -> pd.DataFrame:
    return pd.read_csv(
        RATINGS_PATH,
        sep="\t",
        names=["user_id", "movie_id", "rating", "timestamp"],
    ).drop_duplicates()


def train_and_save_model() -> None:
    ratings = load_ratings()
    dataset = Dataset.load_from_df(
        ratings[["user_id", "movie_id", "rating"]],
        Reader(rating_scale=(1, 5)),
    )
    trainset = dataset.build_full_trainset()
    model = SVD(**SVD_PARAMS)
    model.fit(trainset)
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    dump.dump(str(ARTIFACT_PATH), algo=model)


def load_model():
    if not ARTIFACT_PATH.is_file():
        raise FileNotFoundError(
            f"Model artifact not found at {ARTIFACT_PATH}. "
            "Run `py -3.12 -m api.train_model` first."
        )
    _, model = dump.load(str(ARTIFACT_PATH))
    return model, model.trainset
