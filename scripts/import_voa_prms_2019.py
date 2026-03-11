import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]  # project root
sys.path.insert(0, str(ROOT))
import pandas as pd
from sqlalchemy.orm import Session

from app.db import SessionLocal, init_db
from app import models



XLS_PATH = "Publication_AllTables_200619.xls"  


TABLE_SHEETS = [
    "Table2.1",
    "Table2.2",
    "Table2.3",
    "Table2.4",
    "Table2.5",
    "Table2.6",
    "Table2.7",
]

def to_int(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if v == "" or v == ".":
            return None
    try:
        return int(float(v))
    except Exception:
        return None

def to_str(v):
    if v is None:
        return None
    if isinstance(v, float) and pd.isna(v):
        return None
    s = str(v).strip()
    return None if s == "" or s.lower() == "nan" else s

def detect_level(area_code: str | None, la_code: str | None, area_name: str) -> str:
    if area_name.upper() == "ENGLAND":
        return "ENGLAND"
    if la_code:
        return "LA"
    if area_code and area_code.startswith("E12"):
        return "REGION"
    return "UNKNOWN"

def import_one_sheet(db: Session, sheet_name: str):
    df = pd.read_excel(XLS_PATH, sheet_name=sheet_name, engine="xlrd", header=None)

    # property type label is in row 5, col 4 (based on the file layout)
    prop_type = to_str(df.iloc[5, 4]) or "UNKNOWN"

    # header row at index 6, actual data starts at 7
    start = 7
    inserted = 0

    for i in range(start, len(df)):
        la_code = to_str(df.iloc[i, 1])
        area_code = to_str(df.iloc[i, 2])
        area_name = to_str(df.iloc[i, 3])

        # stop when area_name becomes empty for a while
        if not area_name:
            continue

        count_rents = to_int(df.iloc[i, 4])
        mean = to_int(df.iloc[i, 5])
        lq = to_int(df.iloc[i, 6])
        med = to_int(df.iloc[i, 7])
        uq = to_int(df.iloc[i, 8])

        geo = detect_level(area_code, la_code, area_name)

        row = models.OfficialRentStat(
            property_type=prop_type,
            la_code=la_code,
            area_code=area_code,
            area_name=area_name,
            geography_level=geo,
            count_rents=count_rents,
            mean=mean,
            lower_quartile=lq,
            median=med,
            upper_quartile=uq,
        )
        db.add(row)
        inserted += 1

    db.commit()
    print(f"{sheet_name} ({prop_type}): inserted {inserted} rows")

def main():
    init_db()
    db = SessionLocal()

    # optional: clear old imports (avoid duplicates)
    db.query(models.OfficialRentStat).delete()
    db.commit()

    for s in TABLE_SHEETS:
        import_one_sheet(db, s)

    db.close()
    print("Done.")

if __name__ == "__main__":
    main()