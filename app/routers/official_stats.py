from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models

router = APIRouter(prefix="/official-stats", tags=["official-stats"])


@router.get("/area-rent")
def official_area_rent(
    area_code: str = Query(..., min_length=3),
    property_type: str = Query(..., min_length=3),  # e.g. "Two Bedrooms" / "All categories"
    db: Session = Depends(get_db),
):
    row = (
        db.query(models.OfficialRentStat)
        .filter(models.OfficialRentStat.area_code == area_code)
        .filter(models.OfficialRentStat.property_type == property_type)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="No official stats found for the given area_code/property_type")

    return {
        "source": row.source,
        "period": {"start": row.period_start, "end": row.period_end},
        "geography_level": row.geography_level,
        "area_code": row.area_code,
        "area_name": row.area_name,
        "property_type": row.property_type,
        "count_rents": row.count_rents,
        "mean": row.mean,
        "lower_quartile": row.lower_quartile,
        "median": row.median,
        "upper_quartile": row.upper_quartile,
    }


@router.get("/search")
def official_search(
    q: str = Query(..., min_length=2),
    property_type: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(models.OfficialRentStat).filter(models.OfficialRentStat.area_name.ilike(f"%{q}%"))
    if property_type:
        query = query.filter(models.OfficialRentStat.property_type == property_type)

    rows = query.limit(limit).all()

    return [
        {
            "geography_level": r.geography_level,
            "area_code": r.area_code,
            "la_code": r.la_code,
            "area_name": r.area_name,
            "property_type": r.property_type,
            "median": r.median,
            "mean": r.mean,
            "count_rents": r.count_rents,
        }
        for r in rows
    ]