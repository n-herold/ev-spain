from pathlib import Path

import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# 1) Project folder and connection (as in run_sql.py)
project_dir = Path(__file__).resolve().parent.parent.parent
parquet_glob = (project_dir / "q1" / "data" / "processed" / "*.parquet").as_posix()

con = duckdb.connect()
con.execute(
    f"CREATE VIEW registrations AS SELECT * FROM read_parquet('{parquet_glob}')"
)


def run_sql_file(name):
    """Read a SQL file from q1/sql/ and return the result as a table."""
    text = (project_dir / "q1" / "sql" / name).read_text(encoding="utf-8").strip().rstrip(";")
    return con.execute(text).df()


# 2) Run both queries and merge them on year and month
growth = run_sql_file("03_growth.sql")
anom = run_sql_file("04_anomalies.sql")

df = growth.merge(
    anom[["year", "month", "share_pct", "base_pct", "diff_pp", "z_score"]],
    on=["year", "month"],
)

# 3) Compute date and cumulative values
df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))

# Cumulative since Jan 2023
df["bev_cum"] = df["bev"].cumsum()
df["total_cum"] = df["total"].cumsum()
df["share_cum_pct"] = df["bev_cum"] * 100 / df["total_cum"]

# Cumulative since start of year (YTD)
df["bev_ytd"] = df.groupby("year")["bev"].cumsum()
df["total_ytd"] = df.groupby("year")["total"].cumsum()
df["share_ytd_pct"] = df["bev_ytd"] * 100 / df["total_ytd"]

# YTD growth: year to date vs the same period last year
df["growth_ytd_pct"] = (df["bev_ytd"] / df["bev_ytd"].shift(12) - 1) * 100

# Flagged months (change threshold here)
Z_THRESHOLD = 2
df["flagged"] = df["z_score"].abs() >= Z_THRESHOLD

event_date = pd.Timestamp("2026-02-28")  # Hormuz closure (date unverified)

fig_dir = project_dir / "q1" / "figures"
fig_dir.mkdir(exist_ok=True)

# 4) Figure 1: single values on the left, cumulative on the right
fig, axes = plt.subplots(3, 2, sharex=True, figsize=(14, 10))

axes[0, 0].plot(df["date"], df["bev"], marker="o")
axes[0, 0].set_ylabel("BEV per month")
axes[0, 0].set_title("Single values per month")

axes[1, 0].plot(df["date"], df["bev_share_pct"], marker="o", color="green")
axes[1, 0].set_ylabel("BEV share (%)")

axes[2, 0].plot(df["date"], df["growth_yoy_pct"], marker="o", color="orange")
axes[2, 0].axhline(0, color="grey", linewidth=0.8)
axes[2, 0].set_ylabel("Growth vs same month last year (%)")

axes[0, 1].plot(df["date"], df["bev_cum"], color="purple")
axes[0, 1].set_ylabel("BEV cumulative (since Jan 2023)")
axes[0, 1].set_title("Cumulative")

axes[1, 1].plot(df["date"], df["share_cum_pct"], color="green", label="since Jan 2023")
axes[1, 1].plot(df["date"], df["share_ytd_pct"], color="darkgreen", linestyle=":", label="since start of year")
axes[1, 1].set_ylabel("BEV share (%)")
axes[1, 1].legend()

axes[2, 1].plot(df["date"], df["growth_ytd_pct"], color="orange")
axes[2, 1].axhline(0, color="grey", linewidth=0.8)
axes[2, 1].set_ylabel("YTD growth vs last year (%)")

for ax in axes.flat:
    ax.axvline(event_date, color="red", linestyle="--")
    ax.grid(alpha=0.3)

fig.suptitle("BEV new registrations in Spain, Jan 2023 to Sep 2026")
plt.tight_layout()
plt.savefig(fig_dir / "bev_monthly.png", dpi=150)

# 5) Figure 2: cumulative per year, absolute and as share
fig2, (axa, axb) = plt.subplots(1, 2, figsize=(14, 5))
for year, grp in df.groupby("year"):
    axa.plot(grp["month"], grp["bev_ytd"], marker="o", label=str(year))
    axb.plot(grp["month"], grp["share_ytd_pct"], marker="o", label=str(year))

axa.set_title("BEV since start of year")
axa.set_ylabel("BEV cumulative")
axb.set_title("BEV share since start of year")
axb.set_ylabel("Share (%)")

for ax in (axa, axb):
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("Month")
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(fig_dir / "bev_cumulative_by_year.png", dpi=150)

# 6) Figure 3: anomalies (top: share vs baseline, bottom: z-score)
fig3, (ax1, ax2) = plt.subplots(
    2, 1, sharex=True, figsize=(11, 8), gridspec_kw={"height_ratios": [2, 1]}
)

ax1.plot(df["date"], df["share_pct"], marker="o", label="BEV share (%)")
ax1.plot(df["date"], df["base_pct"], linestyle="--", color="grey", label="Baseline (neighbouring months)")
ax1.set_ylabel("BEV share of new registrations (%)")
ax1.legend()

hot = df[df["flagged"]]
ax1.scatter(hot["date"], hot["share_pct"], color="red", zorder=3)
for _, row in hot.iterrows():
    ax1.annotate(
        row["date"].strftime("%b %Y"),
        (row["date"], row["share_pct"]),
        textcoords="offset points",
        xytext=(0, 8),
        ha="center",
        fontsize=8,
    )

colors = ["red" if flag else "steelblue" for flag in df["flagged"]]
ax2.bar(df["date"], df["z_score"], width=20, color=colors)
ax2.axhline(0, color="black", linewidth=0.8)
ax2.axhline(Z_THRESHOLD, color="red", linestyle="--", linewidth=0.8)
ax2.axhline(-Z_THRESHOLD, color="red", linestyle="--", linewidth=0.8)
ax2.set_ylabel("z-score")

for ax in (ax1, ax2):
    ax.grid(alpha=0.3)

ax1.set_title(f"BEV share and deviation from local baseline (flagged at |z| >= {Z_THRESHOLD})")
plt.tight_layout()
plt.savefig(fig_dir / "bev_anomalies.png", dpi=150)

plt.show()