from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    postcode_prefix = Column(String, nullable=True, index=True)
    city = Column(String, nullable=True, index=True)
    avg_income_monthly = Column(Integer, nullable=True)  # optional, for affordability analytics

    listings = relationship("Listing", back_populates="area", cascade="all, delete-orphan")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)

    area_id = Column(Integer, ForeignKey("areas.id"), nullable=False, index=True)

    title = Column(String, nullable=False, index=True)
    rent_pcm = Column(Integer, nullable=False, index=True)  # rent per calendar month
    bedrooms = Column(Integer, nullable=False, index=True)
    property_type = Column(String, nullable=False, index=True)  # flat/house/studio...
    furnished = Column(Boolean, nullable=False, default=False)
    available_from = Column(Date, nullable=True)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    area = relationship("Area", back_populates="listings")

class OfficialRentStat(Base):
    __tablename__ = "official_rent_stats"

    id = Column(Integer, primary_key=True, index=True)

    source = Column(String, nullable=False, default="VOA PRMS Apr2018-Mar2019")
    period_start = Column(String, nullable=False, default="2018-04")
    period_end = Column(String, nullable=False, default="2019-03")

    property_type = Column(String, nullable=False, index=True)  # Room/Studio/Two Bedrooms...
    la_code = Column(String, nullable=True, index=True)         # e.g. 1355 (some rows empty)
    area_code = Column(String, nullable=True, index=True)       # e.g. E06000047 / E12000001
    area_name = Column(String, nullable=False, index=True)      # e.g. County Durham UA
    geography_level = Column(String, nullable=False, default="UNKNOWN")  # ENGLAND/REGION/LA

    count_rents = Column(Integer, nullable=True)
    mean = Column(Integer, nullable=True)
    lower_quartile = Column(Integer, nullable=True)
    median = Column(Integer, nullable=True)
    upper_quartile = Column(Integer, nullable=True)