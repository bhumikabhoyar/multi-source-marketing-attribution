import pandas as pd
import sqlalchemy
import urllib.parse
from pathlib import Path

DB_USER     = "root"
DB_PASSWORD = "Bhumika@2026"    # ← apna password
DB_HOST     = "localhost"
DB_PORT     = 3306
DB_NAME     = "marketing_db"

DATA_DIR = Path(r"C:\Users\Dell\OneDrive\Desktop\Multi-Source Marketing Attribution Model\data")

password = urllib.parse.quote_plus(DB_PASSWORD)
engine = sqlalchemy.create_engine(
    f"mysql+pymysql://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Foreign key checks band karo taaki tables drop ho sakein
with engine.connect() as conn:
    conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 0;"))

# Reverse order mein drop karo pehle
DROP_ORDER = ["ab_assignments", "conversions", "touchpoints", "customers"]
with engine.connect() as conn:
    for table in DROP_ORDER:
        conn.execute(sqlalchemy.text(f"DROP TABLE IF EXISTS {table};"))
        print(f"Dropped {table}")
    conn.execute(sqlalchemy.text("SET FOREIGN_KEY_CHECKS = 1;"))
    conn.commit()

# Ab fresh load karo
LOAD_ORDER = ["customers", "touchpoints", "conversions", "ab_assignments"]
for table in LOAD_ORDER:
    df = pd.read_csv(DATA_DIR / f"{table}.csv")
    df.to_sql(table, engine, if_exists="replace", index=False, chunksize=1000, method="multi")
    print(f"Loaded  {table:<20} {len(df):>6,} rows")

print("\nDone! Ab 02_indexes.sql Workbench mein run karo.")