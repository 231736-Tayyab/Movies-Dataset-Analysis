import { HttpErrorResponse } from '@angular/common/http';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { RecommenderApi } from './recommender-api.service';
import type {
  Catalog,
  Movie,
  Prediction,
  Recommendation,
} from './recommender-api.service';

const DEMO_CATALOG: Catalog = {
  users: [1],
  genres: ['Action', 'Adventure', 'Comedy', 'Drama', 'Sci-Fi'],
  year_range: [1980, 1998],
  movies: [
    { movie_id: 1, title: 'Toy Story', year: 1995, genres: 'Animation Adventure Comedy', average_rating: 3.88, rating_count: 452 },
    { movie_id: 50, title: 'Star Wars', year: 1977, genres: 'Action Adventure Romance Sci-Fi War', average_rating: 4.36, rating_count: 583 },
    { movie_id: 100, title: 'Fargo', year: 1996, genres: 'Crime Drama Thriller', average_rating: 4.16, rating_count: 508 },
    { movie_id: 174, title: 'Raiders of the Lost Ark', year: 1981, genres: 'Action Adventure', average_rating: 4.21, rating_count: 420 },
  ],
};

@Component({
  selector: 'app-root',
  imports: [ReactiveFormsModule],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App implements OnInit {
  private readonly api = inject(RecommenderApi);
  readonly isStaticDemo =
    typeof window !== 'undefined' && window.location.hostname.endsWith('github.io');
  readonly catalog = signal<Catalog | null>(null);
  readonly prediction = signal<Prediction | null>(null);
  readonly recommendations = signal<Recommendation[]>([]);
  readonly loadingCatalog = signal(false);
  readonly busyAction = signal<'predict' | 'recommend' | null>(null);
  readonly errorMessage = signal('');

  readonly predictionForm = new FormGroup({
    userId: new FormControl(1, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1)],
    }),
    movieId: new FormControl(1, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1)],
    }),
  });

  readonly recommendationForm = new FormGroup({
    userId: new FormControl(1, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1)],
    }),
    limit: new FormControl(10, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1), Validators.max(30)],
    }),
    minRatings: new FormControl(30, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(0)],
    }),
    genre: new FormControl('', { nonNullable: true }),
    yearMin: new FormControl(1922, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1922), Validators.max(1998)],
    }),
    yearMax: new FormControl(1998, {
      nonNullable: true,
      validators: [Validators.required, Validators.min(1922), Validators.max(1998)],
    }),
  });

  ngOnInit(): void {
    if (this.isStaticDemo) {
      this.catalog.set(DEMO_CATALOG);
      return;
    }

    this.loadingCatalog.set(true);
    this.api.getCatalog().subscribe({
      next: (catalog) => {
        this.catalog.set(catalog);
        this.predictionForm.controls.userId.setValue(catalog.users[0] ?? 1);
        this.recommendationForm.controls.userId.setValue(catalog.users[0] ?? 1);
        this.predictionForm.controls.movieId.setValue(catalog.movies[0]?.movie_id ?? 1);
        this.recommendationForm.controls.yearMin.setValue(catalog.year_range[0]);
        this.recommendationForm.controls.yearMax.setValue(catalog.year_range[1]);
        this.loadingCatalog.set(false);
      },
      error: (error: HttpErrorResponse) => {
        this.loadingCatalog.set(false);
        this.errorMessage.set(this.errorText(error));
      },
    });
  }

  predict(): void {
    if (this.predictionForm.invalid) {
      this.predictionForm.markAllAsTouched();
      return;
    }
    this.errorMessage.set('');
    this.prediction.set(null);
    this.recommendations.set([]);
    const { userId, movieId } = this.predictionForm.getRawValue();
    if (this.isStaticDemo) {
      const movie = this.findMovie(movieId);
      if (movie) {
        this.prediction.set({
          user_id: userId,
          movie,
          predicted_rating: 4.2,
          likely_to_like: true,
          like_threshold: 4,
        });
      }
      return;
    }

    this.busyAction.set('predict');
    this.api.predict(userId, movieId).subscribe({
      next: (result) => {
        this.prediction.set(result);
        this.busyAction.set(null);
      },
      error: (error: HttpErrorResponse) => {
        this.errorMessage.set(this.errorText(error));
        this.busyAction.set(null);
      },
    });
  }

  recommend(): void {
    if (this.recommendationForm.invalid) {
      this.recommendationForm.markAllAsTouched();
      return;
    }
    const values = this.recommendationForm.getRawValue();
    if (values.yearMin > values.yearMax) {
      this.errorMessage.set('The earliest year must not be later than the latest year.');
      return;
    }
    this.errorMessage.set('');
    this.prediction.set(null);
    this.recommendations.set([]);
    if (this.isStaticDemo) {
      this.recommendations.set(
        this.demoRecommendations(values.genre, values.limit),
      );
      return;
    }

    this.busyAction.set('recommend');
    this.api
      .recommend({
        user_id: values.userId,
        limit: values.limit,
        min_ratings: values.minRatings,
        genres: values.genre ? [values.genre] : [],
        year_min: values.yearMin,
        year_max: values.yearMax,
      })
      .subscribe({
        next: (result) => {
          this.recommendations.set(result.recommendations);
          this.busyAction.set(null);
        },
        error: (error: HttpErrorResponse) => {
          this.errorMessage.set(this.errorText(error));
          this.busyAction.set(null);
        },
      });
  }

  private findMovie(movieId: number): Movie | undefined {
    return this.catalog()?.movies.find((movie) => movie.movie_id === movieId);
  }

  private demoRecommendations(genre: string, limit: number): Recommendation[] {
    return (this.catalog()?.movies ?? [])
      .filter((movie) => !genre || movie.genres.split(' ').includes(genre))
      .slice(0, limit)
      .map((movie, index) => ({ ...movie, predicted_rating: 4.6 - index * 0.2 }));
  }

  private errorText(error: HttpErrorResponse): string {
    if (typeof error.error?.error === 'string') {
      return error.error.error;
    }
    if (error.status === 0) {
      return 'Cannot reach the local Flask API. Start it on 127.0.0.1:5000 and retry.';
    }
    return `The request failed (${error.status}). Please try again.`;
  }
}
