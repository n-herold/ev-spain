from pathlib import Path

import duckdb
import pandas as pd

# Name of the SQL file in q1/sql/ to run
SQL_FILE = "04_anomalies.sql"

project_dir = Path(__file__).resolve().parent.parent.parent
parquet_glob = (project_dir / "q1" / "data" / "processed" / "*.parquet").as_posix()

con = duckdb.connect()

# Expose all Parquet files as one table called "registrations"
con.execute(
    f"CREATE VIEW registrations AS SELECT * FROM read_parquet('{parquet_glob}')"
)

sql_text = (project_dir / "q1" / "sql" / SQL_FILE).read_text(encoding="utf-8")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

# Queries are separated by semicolons and run one by one
for statement in sql_text.split(";"):
    if not statement.strip():
        continue
    print("-" * 60)
    print(statement.strip())
    print()
    print(con.execute(statement).df().to_string(index=False))
    
    