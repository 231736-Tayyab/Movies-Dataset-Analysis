# Beyond Popularity: Discovering Underserved Film Audiences and Catalogue Opportunities Using MovieLens 100K

## 1. Research Overview

### Central Research Question

Can we identify films and genre–audience segments that are overlooked by popularity-based discovery, yet show evidence of strong audience preference, and can we recommend these films without substantially reducing recommendation relevance?

### Proposed Contribution

Develop a data-driven decision-support system for streaming catalogue curators that combines audience preferences, movie popularity, genre representation, and recommendation quality to identify promising discovery opportunities.

The goal is to move beyond simply selecting the best-performing recommendation model. The research should investigate whether audience preferences and observed catalogue representation can reveal films or genre–audience segments that conventional popularity-based discovery may overlook.

## 2. Proposed Research Workflow

### 2.1 Analyze Audience Demand

Use historical ratings to estimate preference for movies and genres across user segments. Use only demographic attributes that are actually available in MovieLens 100K.

Possible analyses include:
- Genre preference across available demographic groups.
- User-segment rating patterns.
- Differences between general movie popularity and preference within a particular audience segment.

Interpret these results as patterns in the MovieLens sample, not as definitive claims about all film audiences.

### 2.2 Measure Catalogue Representation

Estimate how frequently movies and genres appear in the rating data. Compare observed representation with estimated audience preference to identify possible demand–catalogue gaps.

Important limitation: rating frequency is only a proxy based on observed ratings. MovieLens 100K does not provide streaming impressions, actual platform exposure, watch time, box-office revenue, or verified catalogue visibility. Do not claim that a film is truly under-promoted or commercially underserved based on rating counts alone.

### 2.3 Identify Discovery Opportunities

Find lower-frequency-rated movies with promising predicted ratings for particular audience segments.

Account for uncertainty so that a movie with only a few ratings is not automatically classified as a hidden gem. Investigate how sparse ratings affect estimated preference and consider minimum-evidence rules, uncertainty estimates, or other defensible methods.

The aim is to identify potential discovery opportunities for further evaluation—not to assert that these films will be commercially successful.

### 2.4 Test the Industry-Relevant Outcome

Compare the proposed approach against appropriate baselines, including:
- Popularity-based recommendations.
- The existing best-performing recommendation model in the current project.
- Any additional baseline justified by the literature and available implementation.

Evaluate:
- Recommendation relevance.
- Catalogue coverage.
- Long-tail recommendation share.
- Genre diversity.
- Performance across audience segments.
- The contribution of each component through an ablation study.

Use a held-out test set for final evaluation. Keep user segments and evaluation protocols consistent across baselines. Fit thresholds, selection rules, and model components using training and validation data only; do not use test results to select the method.

## 3. Why This Is More Than a Recommendation App

The existing application answers:

> Which movies should this user receive based on the best-performing recommendation model?

The proposed research asks a broader question:

> Which potentially valuable films and audience segments may be missed by conventional discovery, and can a recommendation strategy help address this gap?

The intended practical output is a decision-support system for streaming catalogue curators and audience researchers. It should help explore potential discovery opportunities using the evidence available in MovieLens 100K.

## 4. Evaluation Plan

| Evaluation dimension | Research question |
|---|---|
| Rating error or ranking quality | Does the method preserve recommendation relevance? |
| Catalogue coverage | Does it surface a broader range of movies? |
| Long-tail share | Does it recommend more less-frequently rated titles? |
| Genre diversity | Does it avoid repeatedly recommending the same kinds of films? |
| Segment-level performance | Do the results differ across audience groups? |
| Ablation study | Which components actually produce the improvement? |

Select suitable metrics for each dimension and define them before running final experiments. Report relevance and discovery outcomes separately so that increasing the number of less-frequently rated recommendations is not mistakenly treated as an improvement by itself.

## 5. Potential Research Novelty

Popularity bias and long-tail recommendation are established research topics. Therefore, do not claim that identifying lesser-known or less-frequently rated films is itself novel.

The potential contribution is a specific, validated combination of:

1. **Audience demand–catalogue gap measurement:** use available ratings, genres, and demographic information to estimate possible gaps between audience preference and observed representation.
2. **Uncertainty-aware discovery:** avoid confusing low rating counts with strong audience preference.
3. **Segment-specific opportunity analysis:** identify which audience groups may have different preferences and which films may be promising for those groups.
4. **Controlled evaluation:** test whether the proposed discovery strategy improves coverage and diversity while preserving recommendation relevance.

This is a candidate research gap, not a confirmed first-ever contribution. Conduct a focused literature review to determine whether closely related frameworks already exist. Compare the proposed method with the nearest prior work and narrow or revise the contribution if necessary.

## 6. Dataset Scope and Limitations

MovieLens 100K is the primary dataset for this project.

Before implementation:
- Verify the exact dataset files and schema against the official GroupLens documentation.
- Confirm which demographic attributes and genre labels are available.
- Audit missing values, rating distributions, movie rating counts, and user activity.
- Document the data split and prevent information leakage.
- Distinguish observations supported by the data from hypotheses and industry interpretations.

Do not claim that MovieLens 100K directly measures:
- Actual streaming exposure or impressions.
- Watch time or completion rates.
- Box-office revenue, profit, or production budgets.
- Marketing expenditure.
- Whether a platform promoted or suppressed a film.
- Current audience demand across the film industry.

Rating counts may be used as an observed-frequency or popularity proxy, but the limitation must be stated clearly. Findings should be framed as evidence from the MovieLens 100K sample, not as direct proof of present-day streaming-market behaviour.

## 7. Research Integrity and Implementation Principles

- Inspect the existing notebook, Streamlit app, code, results, and model files before modifying the project.
- Treat the actual files and verified outputs as the source of truth; do not assume which model is best.
- Review relevant peer-reviewed papers and primary sources before making novelty claims.
- Cite sources accurately and do not fabricate papers, results, or citations.
- Establish baselines and evaluation protocols before testing the proposed method.
- Report negative or inconclusive results honestly.
- Preserve working code where practical and keep the implementation reproducible.
- Do not add external datasets without approval.
- Separate verified facts, literature-supported findings, hypotheses, and recommendations.

## 8. Expected Research Deliverables

1. Dataset audit and exploratory analysis.
2. Literature review and closest-work comparison matrix.
3. Research gap, objectives, research questions, and hypotheses.
4. Precise operational definitions for audience segments and catalogue opportunities.
5. A defensible methodology and leakage-free experimental protocol.
6. Baseline and proposed-method implementations.
7. Reproducible evaluation tables and visualizations.
8. A Streamlit decision-support application.
9. Results, discussion, limitations, and future-work sections.
10. Technical documentation and a thesis-ready report.

## 9. First Tasks for ChatGPT

Before writing new code:

1. Inspect all available project files and summarize what has already been implemented.
2. Audit the exact MovieLens 100K dataset files and identify the available fields.
3. Review literature on popularity bias, long-tail recommendation, catalogue coverage, genre diversity, demographic audience segmentation, and demand–catalogue gaps.
4. Identify the closest prior studies and create a literature matrix.
5. Assess whether the proposed contribution is sufficiently distinct; do not claim novelty before checking.
6. Define measurable research questions and hypotheses.
7. Propose operational definitions, baselines, metrics, data splits, statistical comparisons, and ablation experiments.
8. Recommend an implementation roadmap that reuses the existing code where practical.

If the proposed research gap is not sufficiently novel or the dataset cannot support a claim, explain why and recommend a more defensible alternative before implementation.

## Official Dataset Reference

GroupLens Research — MovieLens 100K:
https://grouplens.org/datasets/movielens/100k/
