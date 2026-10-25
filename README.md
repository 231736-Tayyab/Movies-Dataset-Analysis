# MovieLens 100K Recommendation Research App

This project compares collaborative-filtering baselines from the research work, selects a deterministic SVD model, and adds a full-stack interface for local inference. It includes both the original Streamlit app and a Flask + Angular application.

## Research and model

The notebook, [movieData.ipynb](./movieData.ipynb), compares Surprise SVD and user-based cosine KNN on MovieLens 100K using an 80/20 split and the like threshold `rating >= 4`. Its recorded comparison reports SVD ROC-AUC 77.44% and KNN ROC-AUC 72.69%; KNN has a slightly higher F1 score (53.18% vs. 51.97%). The new-model feature is SVD-based item-factor similarity, exposed in the Streamlit UI alongside recommendations for a new user.

This is a partial, educational comparison rather than a reproduction of every experiment in the 2025 paper: the paper also evaluates SVD++, co-clustering, neural and graph models, and ranking metrics such as NDCG@10, while the notebook reports thresholded classification metrics for SVD and KNN. The paper reports that neural and graph approaches can improve results on larger datasets and that traditional models remain practical baselines for smaller datasets.

The new API artifact is a fitted Surprise SVD model trained on all available MovieLens ratings. It uses `n_factors=100`, `n_epochs=20`, `lr_all=0.005`, `reg_all=0.02`, and `random_state=42`. Rating regression is the model's prediction task; a score of 4 or higher is displayed as likely to be liked. See [model_metadata.json](./model_metadata.json) for the input schema and provenance.

The associated Scientific Reports paper is [Collaborative filtering models: an experimental and detailed comparative study](https://doi.org/10.1038/s41598-025-15096-4). The supplied review paper, *From Bias to Fairness: Mitigating Popularity Bias in LLM-Based Recommendation Systems via Supervised Fine-Tuning and Direct Preference Optimization*, studies Qwen2.5 fine-tuning on MovieLens. It is background only here: this project does not implement or claim those LLM, SFT, DPO, or fairness results.

## Dataset

MovieLens 100K contains 100,000 ratings from 943 users across 1,682 movies. `u.data` provides tab-separated `user_id`, `movie_id`, `rating`, and `timestamp` fields; `movielens_100k.csv` provides movie titles, years, and genres. The project retains the original MovieLens IDs and 1-to-5 rating scale.

## Full-stack architecture

```text
Angular browser (localhost:4200)
     | /api via development proxy
     v
Flask API (127.0.0.1:5000)
     | catalog and ratings + fitted Surprise SVD
     v
rating prediction / personalized recommendations

GitHub Actions -> Python API tests + Angular production build
               -> GitHub Pages (static Angular interface only)
```

GitHub Pages cannot run this Python API. On Pages the Angular interface explicitly switches to a sample-only demo; actual predictions are available when the local Flask API and Angular development server are both running.

## Windows setup and run

Use Python 3.12 and Node.js 24 or a compatible runtime. The checked-in frontend uses Angular 21 because the installed Node.js 24.13 runtime is below Angular 22's minimum Node.js 24.15 requirement. From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r Requirements.txt
```

Train and save the deterministic model artifact once (re-run after changing the model or ratings):

```powershell
python -m api.train_model
```

Start the Flask API in Terminal 1 and leave it running:

```powershell
python -m api.app
```

In Terminal 2:

```powershell
cd frontend
npm ci
npm start
```

Open <http://localhost:4200>. The Angular development proxy forwards `/api` requests to Flask. The From the repository root, the API accepts the example in [sample_payload.json](./sample_payload.json):

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/predict -Method Post -ContentType "application/json" -InFile .\sample_payload.json
```

API endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Service and model information |
| `GET` | `/api/catalog` | Movie, user, genre, and year-range options |
| `POST` | `/api/predict` | Predict a rating for `{"user_id": 1, "movie_id": 1}` |
| `POST` | `/api/recommendations` | Recommend unseen movies with optional genre, year, and popularity filters |

The app validates identifiers, query ranges, genre values, and result limits; errors are returned as JSON. The development server binds to loopback only.

## Tests and builds

From the repository root:

```powershell
python -m pytest
```

From `frontend`:

```powershell
npm ci
npm run build
```

GitHub Actions runs the Python API tests and Angular production build on pushes and pull requests. On pushes to `main`, it also deploys the static Angular build to GitHub Pages. Enable Pages for the repository and select **GitHub Actions** as the build and deployment source. The Pages deployment does not package or expose the Python model/API.

## Original Streamlit application

The existing richer exploration app remains available from the repository root:

```powershell
streamlit run App.py
```

It provides existing-user and new-user recommendations, rating prediction, item-factor similarity, genre/year filters, and held-out evaluation charts.
