# Rental Insights API 

## Base URL
- Local: `http://127.0.0.1:8000`

## Interactive Docs
- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

## Common Conventions
- Content-Type: `application/json`
- Date format: `YYYY-MM-DD`
- Query booleans: `true` / `false`
- Typical errors:
  - `400 Bad Request` – invalid business condition (e.g., missing income)
  - `404 Not Found` – resource does not exist / no data
  - `422 Unprocessable Entity` – validation error (FastAPI/Pydantic)

---

## Health & Root

### GET `/health`
**Description:** Health check  
**Response 200**
```json
{ "status": "ok" }
```

### GET `/`
**Description:** Root endpoint  
**Response 200**
```json
{ "message": "Rental Insights API is running" }
```

---

# 1) Listings API

## Listing Object (Response)
```json
{
  "id": 1,
  "area_id": 1,
  "title": "2-bed flat near station",
  "rent_pcm": 1200,
  "bedrooms": 2,
  "property_type": "flat",
  "furnished": true,
  "available_from": "2026-03-01",
  "created_at": "2026-02-27T12:34:56.123456"
}
```

### POST `/listings`
**Description:** Create a listing  
**Request Body**
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
**Response 201:** Listing object (see above)

**Possible errors**
- 422 if validation fails (e.g., `rent_pcm <= 0`, missing required fields)

---

### GET `/listings`
**Description:** List listings (supports filters + pagination)

**Query Params**
- `area_id` (int, optional, >0)
- `max_rent` (int, optional, >0) — returns listings with `rent_pcm <= max_rent`
- `bedrooms` (int, optional, >0)
- `skip` (int, optional, default 0)
- `limit` (int, optional, default 50, max 200)

**Example**
`GET /listings?area_id=1&max_rent=1500&bedrooms=2&skip=0&limit=50`

**Response 200**
```json
[
  {
    "id": 1,
    "area_id": 1,
    "title": "2-bed flat near station",
    "rent_pcm": 1200,
    "bedrooms": 2,
    "property_type": "flat",
    "furnished": true,
    "available_from": "2026-03-01",
    "created_at": "2026-02-27T12:34:56.123456"
  }
]
```

---

### GET `/listings/{listing_id}`
**Description:** Retrieve a listing by id  
**Path Params**
- `listing_id` (int)

**Response 200:** Listing object  
**Response 404**
```json
{ "detail": "Listing not found" }
```

---

### PATCH `/listings/{listing_id}`
**Description:** Partially update a listing (PATCH)

**Path Params**
- `listing_id` (int)

**Request Body (any subset of fields)**
```json
{
  "rent_pcm": 1150,
  "furnished": false
}
```

**Response 200:** Updated listing object  
**Response 404**
```json
{ "detail": "Listing not found" }
```

---

### DELETE `/listings/{listing_id}`
**Description:** Delete a listing  
**Response 204:** No content  
**Response 404**
```json
{ "detail": "Listing not found" }
```

---

# 2) Areas API

## Area Object (Response)
```json
{
  "id": 1,
  "name": "City Centre",
  "postcode_prefix": "LS1",
  "city": "Leeds",
  "avg_income_monthly": 2500
}
```

### POST `/areas`
**Description:** Create an area  
**Request Body**
```json
{
  "name": "City Centre",
  "postcode_prefix": "LS1",
  "city": "Leeds",
  "avg_income_monthly": 2500
}
```
**Response 201:** Area object

---

### GET `/areas`
**Description:** List areas (pagination)
**Query Params**
- `skip` (int, default 0)
- `limit` (int, default 50, max 200)

**Response 200**
```json
[
  {
    "id": 1,
    "name": "City Centre",
    "postcode_prefix": "LS1",
    "city": "Leeds",
    "avg_income_monthly": 2500
  }
]
```

---

### GET `/areas/{area_id}`
**Description:** Retrieve an area by id  
**Response 200:** Area object  
**Response 404**
```json
{ "detail": "Area not found" }
```

---

### PATCH `/areas/{area_id}`
**Description:** Partially update an area  
**Request Body example**
```json
{ "avg_income_monthly": 2600 }
```
**Response 200:** Updated area object  
**Response 404**
```json
{ "detail": "Area not found" }
```

---

### DELETE `/areas/{area_id}`
**Description:** Delete an area  
**Response 204:** No content  
**Response 404**
```json
{ "detail": "Area not found" }
```

---

# 3) Analytics API (computed from Listings)

> These endpoints compute statistics from the `listings` table for a given `area_id`, optionally filtered by `bedrooms` and/or `furnished`.

### GET `/analytics/area-rent`
**Description:** Rent distribution statistics for an area

**Query Params**
- `area_id` (int, required, >0)
- `bedrooms` (int, optional, >0)
- `furnished` (bool, optional)

**Example**
`GET /analytics/area-rent?area_id=1&bedrooms=2&furnished=true`

**Response 200**
```json
{
  "area_id": 1,
  "area_name": "City Centre",
  "filters": { "bedrooms": 2, "furnished": true },
  "count": 2,
  "mean_rent_pcm": 1125.5,
  "median_rent_pcm": 1126,
  "p25_rent_pcm": 1088,
  "p75_rent_pcm": 1163
}
```

**Possible errors**
- 404 if area not found
- 404 if no listings found for this area (with current filters)

---

### GET `/analytics/affordability`
**Description:** Affordability ratio for an area (median rent / avg monthly income)

**Query Params**
- `area_id` (int, required, >0)
- `bedrooms` (int, optional, >0)
- `furnished` (bool, optional)

**Example**
`GET /analytics/affordability?area_id=1`

**Response 200**
```json
{
  "area_id": 1,
  "area_name": "City Centre",
  "filters": { "bedrooms": null, "furnished": null },
  "median_rent_pcm": 1126,
  "avg_income_monthly": 2500,
  "affordability_ratio": 0.45,
  "label": "moderate"
}
```

**Notes**
- Requires `areas.avg_income_monthly` to be set.

**Possible errors**
- 404 if area not found
- 404 if no listings found for this area (with current filters)
- 400 if `avg_income_monthly` is missing for the area
```json
{ "detail": "avg_income_monthly is not set for this area" }
```

---

# 4) Official Statistics API (VOA PRMS Apr 2018 – Mar 2019)

> These endpoints query the imported official dataset stored in `official_rent_stats`.

## Import (one-time)
Place `Publication_AllTables_200619.xls` in the project root, then run:
```bat
python scripts\import_voa_prms_2019.py
```
Verify import:
```bat
python scripts\check_official_stats.py
```

---

### GET `/official-stats/search`
**Description:** Search official geographies by name (and optional property type)

**Query Params**
- `q` (string, required, min 2) — matched against `area_name`
- `property_type` (string, optional) — e.g. `Room`, `Studio`, `One Bedroom`, `Two Bedrooms`, `All categories`
- `limit` (int, optional, default 20, max 200)

**Example**
`GET /official-stats/search?q=England&property_type=Room&limit=5`

**Response 200**
```json
[
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
]
```

---

### GET `/official-stats/area-rent`
**Description:** Retrieve official rent distribution for a geography (by `area_code` + `property_type`)

**Query Params**
- `area_code` (string, required) — e.g. `E92000001`
- `property_type` (string, required) — e.g. `Room`

**Example**
`GET /official-stats/area-rent?area_code=E92000001&property_type=Room`

**Response 200**
```json
{
  "source": "VOA PRMS Apr2018-Mar2019",
  "period": { "start": "2018-04", "end": "2019-03" },
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

**Response 404**
```json
{ "detail": "No official stats found for the given area_code/property_type" }
```

---
