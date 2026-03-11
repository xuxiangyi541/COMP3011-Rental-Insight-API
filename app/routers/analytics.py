from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models, crud

router = APIRouter(prefix="/analytics", tags=["analytics"])


def _percentile(sorted_vals: list[int], p: float) -> int:
    """
    Percentile with linear interpolation.
    sorted_vals must be sorted ascending.
    p in [0, 1]
    Returns an integer rent (GBP) rounded to nearest pound.
    """
    n = len(sorted_vals)
    if n == 0:
        raise ValueError("empty")
    if n == 1:
        return sorted_vals[0]

    pos = (n - 1) * p
    lo = int(pos)
    hi = min(lo + 1, n - 1)
    if lo == hi:
        return sorted_vals[lo]

    frac = pos - lo
    return int(round(sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac))


def _median(sorted_vals: list[int]) -> int:
    return _percentile(sorted_vals, 0.5)


def _build_rent_query(
    db: Session,
    area_id: int,
    bedrooms: int | None,
    furnished: bool | None,
):
    q = db.query(models.Listing.rent_pcm).filter(models.Listing.area_id == area_id)
    if bedrooms is not None:
        q = q.filter(models.Listing.bedrooms == bedrooms)
    if furnished is not None:
        q = q.filter(models.Listing.furnished == furnished)
    return q


@router.get("/area-rent")
def area_rent_stats(
    area_id: int = Query(..., gt=0),
    bedrooms: int | None = Query(default=None, gt=0),
    furnished: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    # 1) validate area exists
    area = crud.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    # 2) fetch rents with optional filters
    rents = _build_rent_query(db, area_id, bedrooms, furnished).all()
    rents_list = [r[0] for r in rents]

    if len(rents_list) == 0:
        raise HTTPException(status_code=404, detail="No listings found for this area (with current filters)")

    # 3) compute stats
    rents_list.sort()
    count = len(rents_list)
    mean_val = float(sum(rents_list)) / count
    median_val = _median(rents_list)
    p25 = _percentile(rents_list, 0.25)
    p75 = _percentile(rents_list, 0.75)

    return {
        "area_id": area_id,
        "area_name": area.name,
        "filters": {"bedrooms": bedrooms, "furnished": furnished},
        "count": count,
        "mean_rent_pcm": round(mean_val, 2),
        "median_rent_pcm": median_val,
        "p25_rent_pcm": p25,
        "p75_rent_pcm": p75,
    }


@router.get("/affordability")
def affordability(
    area_id: int = Query(..., gt=0),
    bedrooms: int | None = Query(default=None, gt=0),
    furnished: bool | None = Query(default=None),
    db: Session = Depends(get_db),
):
    # 1) validate area exists
    area = crud.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")

    # 2) validate income exists
    if not area.avg_income_monthly:
        raise HTTPException(status_code=400, detail="avg_income_monthly is not set for this area")

    # 3) median rent (with optional filters)
    rents = _build_rent_query(db, area_id, bedrooms, furnished).all()
    rents_list = [r[0] for r in rents]

    if len(rents_list) == 0:
        raise HTTPException(status_code=404, detail="No listings found for this area (with current filters)")

    rents_list.sort()
    median_rent = _median(rents_list)

    # 4) affordability ratio + label
    ratio = median_rent / float(area.avg_income_monthly)

    # simple label rule (explain in report)
    if ratio < 0.30:
        label = "affordable"
    elif ratio <= 0.45:
        label = "moderate"
    else:
        label = "unaffordable"

    return {
        "area_id": area_id,
        "area_name": area.name,
        "filters": {"bedrooms": bedrooms, "furnished": furnished},
        "median_rent_pcm": median_rent,
        "avg_income_monthly": area.avg_income_monthly,
        "affordability_ratio": round(ratio, 3),
        "label": label,
    }