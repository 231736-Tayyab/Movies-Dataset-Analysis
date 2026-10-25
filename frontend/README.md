# MovieLens Angular frontend

This Angular 21 standalone client calls the local Flask REST API through the development proxy. Angular 21 supports the repository's installed Node.js 24.13 runtime; Angular 22 requires Node.js 24.15 or newer.

From this directory:

```powershell
npm ci
npm start
```

Keep the Flask server running in another terminal (`python -m api.app` from the repository root), then open <http://localhost:4200>. The dev proxy forwards `/api` to `http://127.0.0.1:5000`.

```powershell
npm run build
```

The production bundle is a static frontend in `dist/movie-recommender-frontend/browser`. GitHub Pages runs a sample-only demo because it cannot host the Python API or execute the trained model.
