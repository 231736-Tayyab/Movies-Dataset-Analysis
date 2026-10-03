"""
Movie Recommender (SVD) - MovieLens 100K
Streamlit app built from movieData.ipynb, using the better model (SVD).
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score, precision_score,
                             recall_score, roc_auc_score, roc_curve)
from sklearn.model_selection import train_test_split
from surprise import SVD, Dataset, Reader

BASE_DIR = Path(__file__).parent
RATINGS_PATH = BASE_DIR / "u.data"
MOVIES_PATH = BASE_DIR / "movielens_100k.csv"

# Hyper-parameters from the notebook
SVD_PARAMS = dict(n_factors=100, n_epochs=20, lr_all=0.005, reg_all=0.02, random_state=42)
LIKE_THRESHOLD = 4
NEW_USER_ID = 999999

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")


# ------------------------------------------------------------------ data
@st.cache_data
def load_data():
    ratings = pd.read_csv(RATINGS_PATH, sep="\t",
                          names=["user_id", "movie_id", "rating", "timestamp"]).drop_duplicates()
    movies = pd.read_csv(MOVIES_PATH)
    movies["title"] = movies["title"].astype(str).str.title()
    movies["genres"] = movies["genres"].fillna("")
    stats = ratings.groupby("movie_id")["rating"].agg(n_ratings="count", avg_rating="mean").reset_index()
    movies = movies[["movie_id", "title", "year", "genres"]].merge(stats, on="movie_id", how="left")
    movies["n_ratings"] = movies["n_ratings"].fillna(0).astype(int)
    movies["avg_rating"] = movies["avg_rating"].round(2)
    return ratings, movies


def fit_svd(df: pd.DataFrame):
    ds = Dataset.load_from_df(df[["user_id", "movie_id", "rating"]], Reader(rating_scale=(1, 5)))
    trainset = ds.build_full_trainset()
    model = SVD(**SVD_PARAMS)
    model.fit(trainset)
    return model, trainset


@st.cache_resource(show_spinner="Training SVD model...")
def get_model(_ratings):
    return fit_svd(_ratings)


@st.cache_resource(show_spinner="Building your profile...")
def get_new_user_model(_ratings, picks: tuple):
    extra = pd.DataFrame([(NEW_USER_ID, m, r, 0) for m, r in picks],
                         columns=["user_id", "movie_id", "rating", "timestamp"])
    return fit_svd(pd.concat([_ratings, extra], ignore_index=True))


@st.cache_data(show_spinner="Evaluating on a held-out 20% test set...")
def evaluate(_ratings):
    train_df, test_df = train_test_split(_ratings[["user_id", "movie_id", "rating"]],
                                         test_size=0.20, random_state=42)
    model, _ = fit_svd(train_df)
    preds = np.array([p.est for p in model.test(list(test_df.itertuples(index=False, name=None)))])
    y_true = (test_df["rating"].values >= LIKE_THRESHOLD).astype(int)
    y_pred = (preds >= LIKE_THRESHOLD).astype(int)
    fpr, tpr, _ = roc_curve(y_true, preds)
    return {
        "RMSE": float(np.sqrt(np.mean((preds - test_df["rating"].values) ** 2))),
        "MAE": float(np.mean(np.abs(preds - test_df["rating"].values))),
        "Accuracy": accuracy_score(y_true, y_pred),
        "Precision": precision_score(y_true, y_pred, zero_division=0),
        "Recall": recall_score(y_true, y_pred, zero_division=0),
        "F1 Score": f1_score(y_true, y_pred, zero_division=0),
        "ROC-AUC": roc_auc_score(y_true, preds),
        "cm": confusion_matrix(y_true, y_pred), "fpr": fpr, "tpr": tpr,
        "n_train": len(train_df), "n_test": len(test_df),
    }


# ------------------------------------------------------------------ helpers
def recommend(model, uid, seen, movies, top_n, min_ratings, genres, year_range):
    pool = movies[(movies["n_ratings"] >= min_ratings) & (~movies["movie_id"].isin(seen))]
    if genres:
        pool = pool[pool["genres"].apply(lambda g: any(x in g.split() for x in genres))]
    pool = pool[pool["year"].between(*year_range) | pool["year"].isna()]
    pool = pool.copy()
    pool["predicted_rating"] = [round(model.predict(uid, m).est, 2) for m in pool["movie_id"]]
    pool = pool.sort_values("predicted_rating", ascending=False).head(top_n)
    pool.index = np.arange(1, len(pool) + 1)
    return pool[["title", "year", "genres", "predicted_rating", "avg_rating", "n_ratings"]]


def similar_movies(model, trainset, movie_id, movies, top_n, min_ratings):
    if not trainset.knows_item(movie_id):
        return None
    inner = trainset.to_inner_iid(movie_id)
    q = model.qi
    qn = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-9)
    sims = qn @ qn[inner]
    raw = np.array([trainset.to_raw_iid(i) for i in range(trainset.n_items)])
    df = pd.DataFrame({"movie_id": raw, "similarity": sims.round(3)})
    df = df[df["movie_id"] != movie_id].merge(movies, on="movie_id")
    df = df[df["n_ratings"] >= min_ratings].sort_values("similarity", ascending=False).head(top_n)
    df.index = np.arange(1, len(df) + 1)
    return df[["title", "year", "genres", "similarity", "avg_rating"]]


# ------------------------------------------------------------------ load
if not (RATINGS_PATH.exists() and MOVIES_PATH.exists()):
    st.error("Put `u.data` and `movielens_100k.csv` in the same folder as `app.py`.")
    st.stop()

ratings, movies = load_data()
model, trainset = get_model(ratings)
title_of = movies.set_index("movie_id")["title"].to_dict()
all_genres = sorted({g for gs in movies["genres"] for g in gs.split()})
year_min, year_max = int(movies["year"].min()), int(movies["year"].max())

st.title("🎬 Movie Recommender")
st.caption("Powered by SVD matrix factorization · MovieLens 100K")

with st.sidebar:
    st.header("Filters")
    top_n = st.slider("Number of results", 5, 30, 10)
    min_ratings = st.slider("Min. ratings a movie must have", 1, 200, 30,
                            help="Higher = more popular, safer picks. Lower = more obscure finds.")
    genres = st.multiselect("Genres (any of)", all_genres)
    year_range = st.slider("Release year", year_min, year_max, (year_min, year_max))

tab_user, tab_new, tab_pred, tab_sim, tab_model = st.tabs(
    ["🍿 For an existing user", "🆕 For me (new user)", "🔮 Predict a rating",
     "🎞️ Similar movies", "📈 About the model"])

# ---- existing user
with tab_user:
    uid = st.selectbox("User ID", sorted(ratings["user_id"].unique()))
    seen = set(ratings.loc[ratings["user_id"] == uid, "movie_id"])
    st.subheader(f"Top {top_n} picks for user {uid}")
    recs = recommend(model, int(uid), seen, movies, top_n, min_ratings, genres, year_range)
    if recs.empty:
        st.warning("No movies match these filters. Try loosening them.")
    else:
        st.dataframe(recs.rename(columns={"predicted_rating": "predicted ★", "avg_rating": "avg ★",
                                          "n_ratings": "# ratings"}), width="stretch")
    with st.expander("Movies this user rated highest"):
        hist = ratings[ratings["user_id"] == uid].merge(movies, on="movie_id")
        st.dataframe(hist.sort_values("rating", ascending=False).head(15)[["title", "year", "genres", "rating"]],
                     hide_index=True, width="stretch")

# ---- new user
with tab_new:
    st.write("Rate a few movies you know (the more, the better) and get personalised picks.")
    popular = movies.sort_values("n_ratings", ascending=False).head(300)
    chosen = st.multiselect("Pick movies you've seen", popular["movie_id"].tolist(),
                            format_func=lambda m: f"{title_of[m]} ({int(movies.loc[movies.movie_id == m, 'year'].iloc[0])})"
                            if pd.notna(movies.loc[movies.movie_id == m, 'year'].iloc[0]) else title_of[m])
    my_ratings = {}
    cols = st.columns(3)
    for i, m in enumerate(chosen):
        my_ratings[m] = cols[i % 3].slider(title_of[m], 1, 5, 4, key=f"nr_{m}")
    if len(my_ratings) < 3:
        st.info("Choose at least 3 movies to get recommendations.")
    elif st.button("Get my recommendations", type="primary"):
        m_new, _ = get_new_user_model(ratings, tuple(sorted(my_ratings.items())))
        out = recommend(m_new, NEW_USER_ID, set(my_ratings), movies, top_n, min_ratings, genres, year_range)
        if out.empty:
            st.warning("No movies match these filters. Try loosening them.")
        else:
            st.dataframe(out.rename(columns={"predicted_rating": "predicted ★", "avg_rating": "avg ★",
                                             "n_ratings": "# ratings"}), width="stretch")

# ---- single prediction
with tab_pred:
    c1, c2 = st.columns(2)
    p_user = c1.selectbox("User", sorted(ratings["user_id"].unique()), key="pu")
    p_movie = c2.selectbox("Movie", movies["movie_id"].tolist(), key="pm",
                           format_func=lambda m: f"{title_of[m]}")
    est = model.predict(int(p_user), int(p_movie)).est
    actual = ratings[(ratings.user_id == p_user) & (ratings.movie_id == p_movie)]["rating"]
    a, b, c = st.columns(3)
    a.metric("Predicted rating", f"{est:.2f} ★")
    b.metric("Verdict", "👍 Likely to like" if est >= LIKE_THRESHOLD else "👎 Probably not")
    c.metric("Actual rating", f"{int(actual.iloc[0])} ★" if len(actual) else "Not rated yet")

# ---- similar movies
with tab_sim:
    s_movie = st.selectbox("Pick a movie", movies.sort_values("n_ratings", ascending=False)["movie_id"].tolist(),
                           format_func=lambda m: title_of[m], key="sm")
    sim = similar_movies(model, trainset, int(s_movie), movies, top_n, min_ratings)
    if sim is None or sim.empty:
        st.warning("No similar movies found with the current filters.")
    else:
        st.caption("Similarity = cosine between SVD item factors (movies liked by the same kinds of users).")
        st.dataframe(sim.rename(columns={"avg_rating": "avg ★"}), width="stretch")

# ---- model info
with tab_model:
    st.write(
        "SVD was chosen over KNN because it scored better on accuracy, precision and ROC-AUC in the "
        "notebook, and has a lower rating-prediction error. Metrics below use an 80/20 split with "
        f"'liked' = rating ≥ {LIKE_THRESHOLD}. The app itself is trained on all ratings."
    )
    ev = evaluate(ratings)
    cols = st.columns(7)
    for col, k in zip(cols, ["RMSE", "MAE", "Accuracy", "Precision", "Recall", "F1 Score", "ROC-AUC"]):
        v = ev[k]
        col.metric(k, f"{v:.4f}" if k in ("RMSE", "MAE") else f"{v * 100:.2f}%")
    l, r = st.columns(2)
    with l:
        fig, ax = plt.subplots(figsize=(4.5, 3.8))
        sns.heatmap(ev["cm"], annot=True, fmt="d", cmap="Blues", ax=ax,
                    xticklabels=["Not liked", "Liked"], yticklabels=["Not liked", "Liked"])
        ax.set_title("Confusion matrix"); ax.set_xlabel("Predicted"); ax.set_ylabel("Actual")
        st.pyplot(fig); plt.close(fig)
    with r:
        fig, ax = plt.subplots(figsize=(4.5, 3.8))
        ax.plot(ev["fpr"], ev["tpr"], label=f"SVD (AUC = {ev['ROC-AUC']:.2f})")
        ax.plot([0, 1], [0, 1], "--", color="gray", label="Random")
        ax.set_xlabel("False Positive Rate"); ax.set_ylabel("True Positive Rate"); ax.legend()
        ax.set_title("ROC curve")
        st.pyplot(fig); plt.close(fig)
    st.caption(f"Hyper-parameters: {SVD_PARAMS}")