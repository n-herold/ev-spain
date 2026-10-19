from pathlib import Path

import duckdb
import pandas as pd

# Name der SQL-Datei im Ordner sql/, die ausgeführt werden soll
SQL_FILE = "03_growth.sql"

project_dir = Path(__file__).resolve().parent.parent
parquet_glob = (project_dir / "data" / "processed" / "*.parquet").as_posix()

con = duckdb.connect()

# Alle Parquet-Dateien als eine Tabelle namens "registrations" bereitstellen
con.execute(
    f"CREATE VIEW registrations AS SELECT * FROM read_parquet('{parquet_glob}')"
)

sql_text = (project_dir / "sql" / SQL_FILE).read_text(encoding="utf-8")

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 50)

# Abfragen sind durch Semikolon getrennt; jede wird einzeln ausgeführt
for statement in sql_text.split(";"):
    if not statement.strip():
        continue
    print("-" * 60)
    print(statement.strip())
    print()
    print(con.execute(statement).df().to_string(index=False))
    
    