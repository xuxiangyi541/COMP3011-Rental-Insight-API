import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sqlalchemy import text
from app.db import SessionLocal, init_db

def main():
    init_db()
    db = SessionLocal()
    try:
        count = db.execute(text("SELECT COUNT(*) FROM official_rent_stats")).scalar()
        print("official_rent_stats row count =", count)

        rows = db.execute(text("""
            SELECT area_name, area_code, property_type, median, mean, count_rents
            FROM official_rent_stats
            WHERE area_code IS NOT NULL
            LIMIT 5
        """)).fetchall()

        print("sample rows:")
        for r in rows:
            print(r)
    finally:
        db.close()

if __name__ == "__main__":
    main()