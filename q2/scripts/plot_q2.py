from pathlib import Path

import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# This file lives in q2/scripts/, so the project root is three levels up
project_dir = Path(__file__).resolve().parent.parent.parent
csv_path = project_dir / "q2" / "data" / "eafo_charging_points.csv"

# Charging points as a table called "charging_points" (same setup as run_q2.py)
con = duckdb.connect()
con.register("charging_points", pd.read_csv(csv_path))

# Run the quarterly query from the SQL file
sql = (project_dir / "q2" / "sql" / "01_quarterly.sql").read_text(encoding="utf-8").strip().rstrip(";")
df = con.execute(sql).df()

# Quarter labels for the x axis, for example 2024Q4
df["label"] = df["year"].astype(str) + "Q" + df["quarter"].astype(str)
x = range(len(df))

fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(11, 8), gridspec_kw={"height_ratios": [2, 1]})

# Top: number of public charging points per quarter, AC and DC stacked
ax1.bar(x, df["ac"], label="AC")
ax1.bar(x, df["dc"], bottom=df["ac"], label="DC")
ax1.set_ylabel("Public charging points")
ax1.legend()

# Bottom: change versus the previous quarter in percent
ax2.plot(x, df["ac_qoq_pct"], marker="o", label="AC")
ax2.plot(x, df["dc_qoq_pct"], marker="o", label="DC")
ax2.plot(x, df["total_qoq_pct"], marker="o", color="black", label="Total")
ax2.axhline(0, color="grey", linewidth=0.8)
ax2.set_ylabel("Change vs previous quarter (%)")
ax2.legend()

ax2.set_xticks(list(x))
ax2.set_xticklabels(df["label"], rotation=45, ha="right")

for ax in (ax1, ax2):
    ax.grid(alpha=0.3)

ax1.set_title("Public EV charging points in Spain, 2023 Q1 to 2026 Q3 (source: EAFO)")
plt.tight_layout()

# Save and show
fig_dir = project_dir / "q2" / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)
plt.savefig(fig_dir / "charging_points_quarterly.png", dpi=150)
plt.show()