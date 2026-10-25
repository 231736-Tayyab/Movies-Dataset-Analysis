"""Train the deterministic SVD model and save its Surprise artifact."""

from .model import train_and_save_model


if __name__ == "__main__":
    train_and_save_model()
    print("Saved the MovieLens SVD model to models/movielens_svd")
