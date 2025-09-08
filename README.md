# ParlAI: NBA Parlay Probability Analyzer

ParlAI is an end-to-end web app that estimates the probability of NBA parlay legs (e.g., Over 25.5 PTS) and the overall parlay probability in real time. It ingests game logs from Basketball-Reference, cleans and merges them per player, trains per-player/per-prop quantile regression models with AutoGluon, and serves probabilities via a FastAPI backend consumed by a React/Vite frontend.

## Highlights
- 9 supported props: PTS, REB, AST, STL, BLK, TOV, FG3, FG, FT
- Per-leg and overall parlay probabilities (independence assumption for legs)
- FastAPI + Pydantic backend, React + Vite frontend, AutoGluon Tabular models
- Data pipeline for roster discovery, game-log scraping (2022–2025), cleaning, and merging

## Repository Structure

```
src/
  api/            # FastAPI app + Pydantic schemas
  data/           # Scrapers, cleaning, and dataset utilities
  model/          # ParlayEvaluator, quantile->prob conversion, registry
  main.py         # Uvicorn startup
  train.py        # Offline training over teams/players/props
frontend/         # React/Vite frontend (router, pages, styling)
model/            # Persisted AutoGluon models by player/prop (generated)
AutogluonModels/  # Additional AGT artifacts (generated)
pyproject.toml    # Python deps and packaging
```

## End-to-End Architecture
1) Data layer (`src/data`)
- `download.py`
  - `download_rosters(teams)`: Scrapes roster lists into `src/data/csv/rosters/`.
  - `get_player_ids_from_rosters(teams)`: Builds name→id map (Basketball-Reference style IDs).
  - `get_player_data(player, year, player_ids)`: Scrapes per-year regular season and playoff logs to CSVs.
- `cleanup.py`
  - `clean_df`: Filters DNP/Inactive rows, normalizes NaNs, keeps relevant columns, sorts by date.
  - `combine_and_clean_player(pid)`: Consolidates yearly CSVs to `<pid>-regular.csv` and `<pid>-playoffs.csv`.
  - `merge_player_csvs(pid)`: Merges regular/playoffs, adds `is_playoff`, writes `<pid>-combined.csv`.
  - `update_rebound_column_in_combined_csvs()`: Creates `reb = orb + drb`, drops `orb/drb`.
  - `gradient_weighting_by_season()`: Adds season-based `weight` (more recent seasons weighted higher).
- `player_dataset.py`
  - Loads `<pid>-combined.csv` and exposes:
    - `get_stats()` full dataset
    - `get_career_averages()` (since 2022)
    - `get_recent_averages(num_games=5)`
    - `get_playoffs_avg(n)` to build an inference feature row

2) Modeling layer (`src/model`)
- `parlay_evaluator.py`
  - Trains AutoGluon `TabularPredictor` with `problem_type='quantile'` across 9 quantiles.
  - Adds Gaussian feature noise for regularization; sample weights via `is_playoff`.
  - Persists models per player/prop to `model/<player_id>/<prop>/`.
  - During inference: loads model, predicts quantiles for a recent-playoff average row, inflates spread slightly, converts to hit probabilities.
- `quantile_converter.py`
  - Interpolates a CDF from predicted quantiles and returns P(X ≤ threshold); derives Over/Under.
- `model_registry.py`
  - Filesystem registry helper for model paths (load/save existence checks).
- `train.py`
  - Batch trains per player/prop for configured teams (`IND`, `OKC`) using `PlayerDataset`.

3) API layer (`src/api`)
- `model.py`: Pydantic types
  - `ParlayLeg` (player, prop, line, over/under)
  - `PostParlayRequest/Response`, `ParlayLegProbability`, `PropStat` enum
- `server.py`: FastAPI app
  - `POST /api/parlay/` → per-leg probabilities + overall probability (product of legs)
  - `GET /api/players/` → list of `{ name, id }` for UI autocomplete
  - `GET /api/player_stats/{player_id}` → `career` and `recent` averages
- `main.py`: boots Uvicorn; configures CORS for Vite dev origin

4) Frontend (`frontend`)
- React + Vite + React Router
- `HomePage.jsx`: Build 2–6 legs, player autocomplete, prop dropdown, line validation (.5 steps), pull player stats, submit to backend.
- `ResultPage.jsx`: Visualizes per-leg probabilities and overall probability with color-mapped bars and player images.
- `vite.config.js`: Proxies `/api` to backend at `http://localhost:8000`.

## Setup

### Prerequisites
- Python 3.10.x (AutoGluon pinning)
- Node 18+

### Backend install
```sh
python3.10 -m venv venv
source venv/bin/activate
pip install .
```

### Frontend install
```sh
cd frontend
npm install
```

## Data Ingestion & Preparation
By default, this project focuses on 2022–2025 seasons and teams `IND`, `OKC` (configurable).

1) Ensure rosters exist (or scrape them):
```sh
python -c "from data.download import download_rosters; download_rosters(['IND','OKC'])"
```

2) Download per-player, per-season logs and build combined CSVs:
```sh
python src/data/pipeline.py
```
This will:
- Download game logs to `src/data/csv/players/`.
- Create `<pid>-regular.csv`, `<pid>-playoffs.csv`, and `<pid>-combined.csv`.
- Merge rebounds into `reb` and add season weights.

## Model Training
Train per-player, per-prop quantile models and persist them to `model/<pid>/<prop>/`:
```sh
python src/train.py
```

Training details:
- AutoGluon Tabular with `problem_type='quantile'` and quantiles `[0.01, 0.05, 0.10, 0.30, 0.50, 0.70, 0.90, 0.95, 0.99]`
- `presets='medium_quality'`, `time_limit=300`, `num_bag_folds=5`, `num_stack_levels=1`
- Sample weights: `is_playoff`
- Simple data augmentation: Gaussian noise on numeric features

## Running the App

### Start backend
```sh
python src/main.py
```
This starts Uvicorn (FastAPI) at `http://localhost:8000` with CORS for the Vite dev server.

### Start frontend
```sh
cd frontend
npm run dev
```
This starts Vite at `http://localhost:5173` with a proxy to the backend for `/api`.

## API Reference (Dev)

Base URL: `http://localhost:8000/api`

### POST /parlay/
Request body:
```json
{
  "parlayLegs": [
    { "player": "Tyrese Haliburton", "prop": "pts", "value": 24.5, "overUnder": "over" },
    { "player": "Chet Holmgren", "prop": "reb", "value": 9.5, "overUnder": "under" }
  ]
}
```
Response:
```json
{
  "parlayLegProbabilities": [
    { "player": "Tyrese Haliburton", "prop": "pts", "value": 24.5, "overUnder": "over", "probability": 0.61 },
    { "player": "Chet Holmgren", "prop": "reb", "value": 9.5, "overUnder": "under", "probability": 0.43 }
  ],
  "overallProbability": 0.262
}
```

### GET /players/
Response:
```json
{
  "players": [ { "name": "Tyrese Haliburton", "id": "halibty01" }, ... ]
}
```

### GET /player_stats/{player_id}
Response:
```json
{
  "career": { "pts": 20.4, "reb": 4.0, "ast": 9.5, "stl": 1.4, "blk": 0.5, "tov": 2.7, "fg3": 2.9, "fg": 7.0, "ft": 3.0 },
  "recent": { "pts": 24.8, "reb": 5.1, "ast": 10.7, "stl": 1.2, "blk": 0.6, "tov": 3.1, "fg3": 3.4, "fg": 7.9, "ft": 3.5 }
}
```

## Frontend Usage
1) Navigate to `http://localhost:5173`.
2) Build 2–6 legs by selecting player, prop, line (validated to .5 increments ≥ 0.5), and Over/Under.
3) Review career and last‑5 averages next to selected players.
4) Submit to see per‑leg probabilities and overall parlay probability with color‑coded bars. Click “New Parlay” to iterate.

## Modeling Notes
- Quantile regression predicts the distribution of a stat conditioned on recent playoff context.
- Interpolation converts predicted quantiles into a smooth CDF; Over/Under = 1 − CDF(line) / CDF(line).
- Independence assumption multiplies leg probabilities for overall parlay odds; consider correlation modeling as a future enhancement.

## Configuration & Extensibility
- Teams and seasons: adjust in `src/data/pipeline.py` (`TEAMS`, `SEASONS`).
- Add more players/teams: update rosters, re-run pipeline, then `src/train.py`.
- Extend props: update `api/model.py` `PropStat` enum and retrain.
- Images: place player images in `frontend/public/images/{player_id}.png` (fallback provided).

## Troubleshooting
- Missing combined CSV: ensure pipeline ran; file expected at `src/data/csv/players/<pid>-combined.csv`.
- Model not found: train models (`python src/train.py`) to create `model/<pid>/<prop>/`.
- CORS/proxy issues: backend runs on 8000, frontend on 5173; Vite proxy defined in `frontend/vite.config.js`.

## License
Educational project for coursework; models and scraped data are for non‑commercial use.
