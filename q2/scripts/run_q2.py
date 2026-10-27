from pathlib import Path

import duckdb
import pandas as pd

# Name of the SQL file in q2/sql/ that should be run
SQL_FILE = "01_quarterly.sql"

# This file lives in q2/scripts/, so the project root is three levels up
project_dir = Path(__file__).resolve().parent.parent.parent
csv_path = project_dir / "q2" / "data" / "eafo_charging_points.csv"

con = duckdb.connect()

# EAFO charging points (AC and DC per quarter) as a table called "charging_points"
# Read with pandas and register it in DuckDB, so DuckDB does not have to guess the CSV format
con.register("charging_points", pd.read_csv(csv_path))

sql_text = (project_dir / "q2" / "sql" / SQL_FILE).read_text(encoding="utf-8")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

# Queries are separated by semicolons and each one is run on its own
for statement in sql_text.split(";"):
    if not statement.strip():
        continue
    print("-" * 60)
    print(statement.strip())
    print()
    print(con.execute(statement).df().to_string(index=False))
    