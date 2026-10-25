import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

export interface Movie {
  movie_id: number;
  title: string;
  year: number | null;
  genres: string;
  average_rating: number | null;
  rating_count: number;
}

export interface Catalog {
  movies: Movie[];
  users: number[];
  genres: string[];
  year_range: [number, number];
}

export interface Prediction {
  user_id: number;
  movie: Movie;
  predicted_rating: number;
  likely_to_like: boolean;
  like_threshold: number;
}

export interface Recommendation extends Movie {
  predicted_rating: number;
}

interface RecommendationResponse {
  user_id: number;
  recommendations: Recommendation[];
}

@Injectable({ providedIn: 'root' })
export class RecommenderApi {
  private readonly http = inject(HttpClient);

  getCatalog(): Observable<Catalog> {
    return this.http.get<Catalog>('/api/catalog');
  }

  predict(userId: number, movieId: number): Observable<Prediction> {
    return this.http.post<Prediction>('/api/predict', {
      user_id: userId,
      movie_id: movieId,
    });
  }

  recommend(request: {
    user_id: number;
    limit: number;
    min_ratings: number;
    genres: string[];
    year_min: number;
    year_max: number;
  }): Observable<RecommendationResponse> {
    return this.http.post<RecommendationResponse>('/api/recommendations', request);
  }
}
