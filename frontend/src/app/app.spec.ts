import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { App } from './app';
import { RecommenderApi } from './recommender-api.service';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        {
          provide: RecommenderApi,
          useValue: {
            getCatalog: () =>
              of({
                users: [1],
                genres: ['Action'],
                year_range: [1922, 1998],
                movies: [
                  {
                    movie_id: 1,
                    title: 'Toy Story',
                    year: 1995,
                    genres: 'Animation Adventure Comedy',
                    average_rating: 3.88,
                    rating_count: 452,
                  },
                ],
              }),
            predict: () => of({}),
            recommend: () => of({ recommendations: [] }),
          },
        },
      ],
    }).compileComponents();
  });

  it('renders the recommendation and prediction forms', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    fixture.detectChanges();

    const rendered = fixture.nativeElement as HTMLElement;
    expect(rendered.querySelector('h1')?.textContent).toContain('worth');
    expect(rendered.textContent).toContain('Recommendations');
    expect(rendered.textContent).toContain('Predict a rating');
  });

  it('does not submit a prediction when the form is invalid', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const component = fixture.componentInstance;
    component.predictionForm.controls.userId.setValue(0);

    component.predict();

    expect(component.prediction()).toBeNull();
  });
});
