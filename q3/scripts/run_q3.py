from pathlib import Path
import duckdb
import pandas as pd

SQL_FILE = "02_groups.sql"

project_dir = Path(__file__).resolve().parent.parent.parent
csv_path = project_dir / "q3" / "data" / "generation_gwh_long.csv"

con = duckdb.connect()
con.register("generation", pd.read_csv(csv_path))

sql_text = (project_dir / "q3" / "sql" / SQL_FILE).read_text(encoding="utf-8")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)
for statement in sql_text.split(";"):
    if not statement.strip():
        continue
    print("-" * 60); print(statement.strip()); print()
    print(con.execute(statement).df().to_string(index=False))
    
    