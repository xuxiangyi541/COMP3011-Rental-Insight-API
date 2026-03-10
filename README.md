# Rental Insights API

A FastAPI + SQLAlchemy + SQLite REST API for managing rental listings and providing rental market insights (analytics), with optional integration of **official UK rental statistics** (VOA PRMS 2018–2019).

## Highlights

- **Listings CRUD**: create, list, retrieve, update (PATCH), delete rental listings
- **Areas CRUD**: manage areas (e.g., City Centre / postcode prefix / income)
- **Analytics (computed from your Listings table)**
  - `GET /analytics/area-rent` — mean/median/p25/p75 with optional filters
  - `GET /analytics/affordability` — affordability ratio (median rent / monthly income) with optional filters
- **Official Statistics (VOA PRMS Apr 2018–Mar 2019)**
  - Import `.xls` tables into `official_rent_stats`
  - Query via `/official-stats/search` and `/official-stats/area-rent`
- **Interactive API docs** via Swagger UI (`/docs`) and OpenAPI schema (`/openapi.json`)

## Tech Stack

- **FastAPI**
- **SQLAlchemy ORM**
- **SQLite** (default local database file: `rental.db`)
- **pandas + xlrd** (to import `.xls` official statistics)
- (Optional) **pytest** for testing

## Project Structure

```
rental-insights-api/
  app/
    main.py
    db.py
    models.py
    schemas.py
    crud.py
    routers/
      listings.py
      areas.py
      analytics.py
      official_stats.py
  docs/
    api-docs.pdf
  scripts/
    import_voa_prms_2019.py
    check_official_stats.py
    check_db.py
  tests/
  requirements.txt
  README.md
  README_CN.md
```

## Quick Start (Windows CMD)

> Make sure you are in the project root folder.

### 1) Create and activate virtual environment

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

### 2) Install dependencies

```bat
pip install -r requirements.txt
```

### 3) Run the server

```bat
uvicorn app.main:app --reload
```

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- Health check: `http://127.0.0.1:8000/health`

## API Documentation (Coursework Deliverable)

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`
- PDF: `docs/api-docs.pdf`

## Core Endpoints

### Listings

- `POST /listings`
- `GET /listings`
- `GET /listings/{listing_id}`
- `PATCH /listings/{listing_id}`
- `DELETE /listings/{listing_id}`

Example (create a listing):

```json
{
  "area_id": 1,
  "title": "2-bed flat near station",
  "rent_pcm": 1200,
  "bedrooms": 2,
  "property_type": "flat",
  "furnished": true,
  "available_from": "2026-03-01"
}
```

### Areas

- `POST /areas`
- `GET /areas`
- `GET /areas/{area_id}`
- `PATCH /areas/{area_id}`
- `DELETE /areas/{area_id}`

Example (create an area):

```json
{
  "name": "City Centre",
  "postcode_prefix": "LS1",
  "city": "Leeds",
  "avg_income_monthly": 2500
}
```

### Analytics (from Listings)

#### Area rent statistics

`GET /analytics/area-rent?area_id=1`

Optional filters:

- `bedrooms` (e.g., `&bedrooms=2`)
- `furnished` (e.g., `&furnished=true`)

Example response:

```json
{
  "area_id": 1,
  "area_name": "City Centre",
  "filters": {"bedrooms": null, "furnished": null},
  "count": 2,
  "mean_rent_pcm": 1125.5,
  "median_rent_pcm": 1126,
  "p25_rent_pcm": 1088,
  "p75_rent_pcm": 1163
}
```

#### Affordability

`GET /analytics/affordability?area_id=1`

Optional filters:

- `bedrooms`
- `furnished`

Example response:

```json
{
  "area_id": 1,
  "area_name": "City Centre",
  "filters": {"bedrooms": null, "furnished": null},
  "median_rent_pcm": 1126,
  "avg_income_monthly": 2500,
  "affordability_ratio": 0.45,
  "label": "unaffordable"
}
```

### Official Statistics (VOA PRMS 2018–2019)

These endpoints query the imported **VOA Private Rental Market Summary Statistics (Apr 2018–Mar 2019)** tables.

#### Import official stats (one-time)

1) Place the `.xls` file in the project root (e.g., `Publication_AllTables_200619.xls`).
2) Run:

```bat
python scripts\import_voa_prms_2019.py
```

(Optional) Verify import:

```bat
python scripts\check_official_stats.py
```

#### Search areas by name

`GET /official-stats/search?q=England&property_type=Room&limit=5`

Example response item:

```json
{
  "geography_level": "ENGLAND",
  "area_code": "E92000001",
  "la_code": null,
  "area_name": "ENGLAND",
  "property_type": "Room",
  "median": 390,
  "mean": 411,
  "count_rents": 26320
}
```

#### Get rent distribution for an official area

`GET /official-stats/area-rent?area_code=E92000001&property_type=Room`

Example response:

```json
{
  "source": "VOA PRMS Apr2018-Mar2019",
  "period": {"start": "2018-04", "end": "2019-03"},
  "geography_level": "ENGLAND",
  "area_code": "E92000001",
  "area_name": "ENGLAND",
  "property_type": "Room",
  "count_rents": 26320,
  "mean": 411,
  "lower_quartile": 349,
  "median": 390,
  "upper_quartile": 450
}
```

## Testing (optional)

If you added tests:

```bat
pytest
```

## Notes

- Database file `rental.db` is created automatically on first run.
- This project is designed for coursework submission: version control history, API docs (PDF), a short technical report, and slides.
- I used GenAI minimally to draft some initial API scaffolding and example payloads. All outputs were reviewed and validated by running the API locally, testing via Swagger, and running pytest
