from pathlib import Path
import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

project_dir = Path(__file__).resolve().parent.parent.parent
csv_path = project_dir / "q3" / "data" / "generation_gwh_long.csv"
sql_path = project_dir / "q3" / "sql" / "02_groups.sql"
fig_dir = project_dir / "q3" / "figures"
fig_dir.mkdir(parents=True, exist_ok=True)

# run the grouping query on the cleaned CSV
con = duckdb.connect()
con.register("generation", pd.read_csv(csv_path))
df = con.execute(sql_path.read_text(encoding="utf-8")).df()
df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))

colors = {"Renewable": "#2E8B57", "Nuclear": "#7B4FA3", "Fossil": "#C0652B"}

fig, ax = plt.subplots(figsize=(12, 6))
for grp, sub in df.groupby("grp"):
    ax.plot(sub["date"], sub["share_pct"], marker="o", markersize=5,
            linewidth=2.2, color=colors[grp])
    last = sub.iloc[-1]
    ax.annotate(f"{grp} {last['share_pct']:.1f}%", (last["date"], last["share_pct"]),
                xytext=(8, 0), textcoords="offset points", va="center",
                color=colors[grp], fontweight="bold")

ax.set_title("Spain's electricity mix: monthly share by source group",
             loc="left", fontsize=14, fontweight="bold", pad=24)
ax.text(0, 1.02, "Share of monthly generation in %, Jan 2023 to Sep 2026. Source: REE (www.ree.es)",
        transform=ax.transAxes, fontsize=9, color="grey")

ax.spines[["top", "right"]].set_visible(False)
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
ax.set_xlim(df["date"].min() - pd.Timedelta(days=15), df["date"].max() + pd.Timedelta(days=130))
ax.set_ylim(0, 70)
ax.set_ylabel("Share of generation (%)")
ax.grid(axis="y", alpha=0.3)

fig.tight_layout()
fig.savefig(fig_dir / "generation_groups_monthly.png", dpi=150)
plt.show()