from pathlib import Path
import pandas as pd

project_dir = Path(__file__).resolve().parent.parent.parent
csv_path = project_dir / "q3" / "data" / "ree_generation_gwh.csv"

raw = pd.read_csv(csv_path, encoding="latin-1", skiprows=4, nrows=17,
                  decimal=",", na_values=["-"])
print(raw.iloc[:, :4])
print(raw.dtypes.head())

long = raw.melt(id_vars="Fecha", var_name="month", value_name="gwh")
long = long.rename(columns={"Fecha": "technology"})
print(long.head())
print(len(long))
month_map = {"ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
             "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12}
long["year"] = 2000 + long["month"].str[4:].astype(int)
long["month"] = long["month"].str[:3].map(month_map)

total = long[long["technology"] == "Generación total"].copy()
long = long[long["technology"] != "Generación total"].copy()
long["gwh"] = long["gwh"].fillna(0)

print(long.head())
print(long["month"].unique())
print(len(long))
check = long.groupby(["year", "month"])["gwh"].sum().reset_index()
total = total.rename(columns={"gwh": "total_gwh"})
check = check.merge(total[["year", "month", "total_gwh"]], on=["year", "month"])
check["diff"] = check["gwh"] - check["total_gwh"]
print(check["diff"].abs().max())
out_path = project_dir / "q3" / "data" / "generation_gwh_long.csv"
long[["year", "month", "technology", "gwh"]].to_csv(out_path, index=False)
print("saved", out_path)