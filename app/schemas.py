from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field
from typing import Optional


class ListingBase(BaseModel):
    area_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=200)
    rent_pcm: int = Field(..., gt=0)
    bedrooms: int = Field(..., gt=0, le=20)
    property_type: str = Field(..., min_length=1, max_length=50)
    furnished: bool = False
    available_from: Optional[date] = None


class ListingCreate(ListingBase):
    pass


class ListingUpdate(BaseModel):
    # PATCH
    area_id: Optional[int] = Field(None, gt=0)
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    rent_pcm: Optional[int] = Field(None, gt=0)
    bedrooms: Optional[int] = Field(None, gt=0, le=20)
    property_type: Optional[str] = Field(None, min_length=1, max_length=50)
    furnished: Optional[bool] = None
    available_from: Optional[date] = None


class ListingOut(ListingBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True  # pydantic v2 / ORM compatible


class AreaBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    postcode_prefix: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=60)
    avg_income_monthly: Optional[int] = Field(None, gt=0)

class AreaCreate(AreaBase):
    pass

class AreaUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    postcode_prefix: Optional[str] = Field(None, max_length=10)
    city: Optional[str] = Field(None, max_length=60)
    avg_income_monthly: Optional[int] = Field(None, gt=0)

class AreaOut(AreaBase):
    id: int
    class Config:
        from_attributes = True