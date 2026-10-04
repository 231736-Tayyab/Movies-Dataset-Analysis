
## Project Overview

This project compares two collaborative filtering algorithms on the **MovieLens 100K** dataset:

1. **Singular Value Decomposition (SVD)**
2. **K-Nearest Neighbors (KNNBasic)**

The goal is to evaluate how well both models can predict whether a movie rating should be considered **positive or negative**, and then compare their performance using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

A Streamlit application was also developed to provide a simple interface for using the selected/best-performing model.

---

## Dataset

### MovieLens 100K

The project uses the **MovieLens 100K** dataset.

Dataset characteristics:

- **100,000 ratings**
- **943 users**
- **1,682 movies**
- Rating scale: **1 to 5**
- Main fields:
  - `user_id`
  - `movie_id`
  - `rating`
  - `timestamp`

The dataset is a widely used benchmark for recommender-system research.

Dataset source:

https://grouplens.org/datasets/movielens/

---

## Research Background

The model selection is based on recent research using MovieLens datasets for collaborative filtering.

The 2025 research paper **"Collaborative filtering models: an experimental and detailed comparative study"** evaluates several collaborative filtering approaches, including SVD and KNN-based methods, using MovieLens datasets including MovieLens 100K.

Paper:

https://doi.org/10.1038/s41598-025-15096-4

This project uses the research as academic motivation for selecting established collaborative filtering algorithms, while adapting the evaluation to the classification metrics required for this project.

---

## Project Workflow

```text
MovieLens 100K
       |
       v
Data Loading
       |
       v
Data Inspection
       |
       v
Data Preprocessing
       |
       v
Feature / Target Preparation
       |
       v
Rating >= 4  ---> Positive (1)
Rating <  4  ---> Negative (0)
       |
       v
80% Training / 20% Testing
       |
       +-------------------+
       |                   |
       v                   v
      SVD                KNNBasic
       |                   |
       +---------+---------+
                 |
                 v
          Model Evaluation
                 |
       +---------+---------+
       |         |         |
       v         v         v
   Accuracy  Precision  Recall
       |
       v
      F1
       |
       v
    ROC-AUC
