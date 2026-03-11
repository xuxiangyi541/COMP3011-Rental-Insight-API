from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import crud, schemas

router = APIRouter(prefix="/areas", tags=["areas"])

@router.post("", response_model=schemas.AreaOut, status_code=status.HTTP_201_CREATED)
def create_area(payload: schemas.AreaCreate, db: Session = Depends(get_db)):
    return crud.create_area(db, payload)

@router.get("", response_model=list[schemas.AreaOut])
def get_areas(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    return crud.list_areas(db, skip=skip, limit=limit)

@router.get("/{area_id}", response_model=schemas.AreaOut)
def get_area(area_id: int, db: Session = Depends(get_db)):
    area = crud.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return area

@router.patch("/{area_id}", response_model=schemas.AreaOut)
def patch_area(area_id: int, payload: schemas.AreaUpdate, db: Session = Depends(get_db)):
    area = crud.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    return crud.update_area(db, area, payload)

@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_area(area_id: int, db: Session = Depends(get_db)):
    area = crud.get_area(db, area_id)
    if not area:
        raise HTTPException(status_code=404, detail="Area not found")
    crud.delete_area(db, area)
    return None