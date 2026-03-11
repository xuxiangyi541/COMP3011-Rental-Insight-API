from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import crud, schemas

router = APIRouter(prefix="/listings", tags=["listings"])


@router.post("", response_model=schemas.ListingOut, status_code=status.HTTP_201_CREATED)
def create_listing(payload: schemas.ListingCreate, db: Session = Depends(get_db)):
    return crud.create_listing(db, payload)


@router.get("", response_model=list[schemas.ListingOut])
def get_listings(
    area_id: int | None = Query(default=None, gt=0),
    max_rent: int | None = Query(default=None, gt=0),
    bedrooms: int | None = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.list_listings(db, area_id=area_id, max_rent=max_rent, bedrooms=bedrooms, skip=skip, limit=limit)


@router.get("/{listing_id}", response_model=schemas.ListingOut)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return listing


@router.patch("/{listing_id}", response_model=schemas.ListingOut)
def patch_listing(listing_id: int, payload: schemas.ListingUpdate, db: Session = Depends(get_db)):
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return crud.update_listing(db, listing, payload)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_listing(listing_id: int, db: Session = Depends(get_db)):
    listing = crud.get_listing(db, listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    crud.delete_listing(db, listing)
    return None