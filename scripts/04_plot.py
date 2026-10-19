from pathlib import Path

import duckdb
import pandas as pd
import matplotlib.pyplot as plt

# 1) Projektordner und Verbindung (wie in run_sql.py)
project_dir = Path(__file__).resolve().parent.parent
parquet_glob = (project_dir / "data" / "processed" / "*.parquet").as_posix()

con = duckdb.connect()
con.execute(
    f"CREATE VIEW registrations AS SELECT * FROM read_parquet('{parquet_glob}')"
)

# 2) Growth-Abfrage ausführen
sql = (project_dir / "sql" / "03_growth.sql").read_text(encoding="utf-8").strip().rstrip(";")
df = con.execute(sql).df()

# 3) Datum und Kumulierungen berechnen
df["date"] = pd.to_datetime(dict(year=df["year"], month=df["month"], day=1))

# Kumuliert seit Jan 2023
df["bev_cum"] = df["bev"].cumsum()
df["total_cum"] = df["total"].cumsum()
df["share_cum_pct"] = df["bev_cum"] * 100 / df["total_cum"]

# Kumuliert seit Jahresbeginn (YTD)
df["bev_ytd"] = df.groupby("year")["bev"].cumsum()
df["total_ytd"] = df.groupby("year")["total"].cumsum()
df["share_ytd_pct"] = df["bev_ytd"] * 100 / df["total_ytd"]

# YTD-Wachstum: Jahr-bis-heute gegen denselben Zeitraum im Vorjahr
df["growth_ytd_pct"] = (df["bev_ytd"] / df["bev_ytd"].shift(12) - 1) * 100

stichtag = pd.Timestamp("2026-02-28")  # Hormus-Schließung

# 4) Abbildung 1: links einzeln, rechts kumuliert
fig, axes = plt.subplots(3, 2, sharex=True, figsize=(14, 10))

# Linke Spalte: Einzelwerte pro Monat
axes[0, 0].plot(df["date"], df["bev"], marker="o")
axes[0, 0].set_ylabel("BEV pro Monat")
axes[0, 0].set_title("Einzelwerte pro Monat")

axes[1, 0].plot(df["date"], df["bev_share_pct"], marker="o", color="green")
axes[1, 0].set_ylabel("Anteil BEV (%)")

axes[2, 0].plot(df["date"], df["growth_yoy_pct"], marker="o", color="orange")
axes[2, 0].axhline(0, color="grey", linewidth=0.8)
axes[2, 0].set_ylabel("Wachstum zum Vorjahresmonat (%)")

# Rechte Spalte: kumuliert
axes[0, 1].plot(df["date"], df["bev_cum"], color="purple")
axes[0, 1].set_ylabel("BEV kumuliert (seit Jan 2023)")
axes[0, 1].set_title("Kumuliert")

axes[1, 1].plot(df["date"], df["share_cum_pct"], color="green", label="seit Jan 2023")
axes[1, 1].plot(df["date"], df["share_ytd_pct"], color="darkgreen", linestyle=":", label="seit Jahresbeginn")
axes[1, 1].set_ylabel("Anteil BEV (%)")
axes[1, 1].legend()

axes[2, 1].plot(df["date"], df["growth_ytd_pct"], color="orange")
axes[2, 1].axhline(0, color="grey", linewidth=0.8)
axes[2, 1].set_ylabel("Wachstum YTD zum Vorjahr (%)")

for ax in axes.flat:
    ax.axvline(stichtag, color="red", linestyle="--")
    ax.grid(alpha=0.3)

fig.suptitle("BEV-Neuzulassungen in Spanien, Jan 2023 bis Sep 2026")
plt.tight_layout()

fig_dir = project_dir / "figures"
fig_dir.mkdir(exist_ok=True)
plt.savefig(fig_dir / "bev_monthly.png", dpi=150)

# 5) Abbildung 2: kumuliert pro Jahr, absolut und als Anteil
fig2, (axa, axb) = plt.subplots(1, 2, figsize=(14, 5))
for year, grp in df.groupby("year"):
    axa.plot(grp["month"], grp["bev_ytd"], marker="o", label=str(year))
    axb.plot(grp["month"], grp["share_ytd_pct"], marker="o", label=str(year))

axa.set_title("BEV seit Jahresbeginn")
axa.set_ylabel("BEV kumuliert")
axb.set_title("Anteil BEV seit Jahresbeginn")
axb.set_ylabel("Anteil (%)")

for ax in (axa, axb):
    ax.set_xticks(range(1, 13))
    ax.set_xlabel("Monat")
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig(fig_dir / "bev_cumulative_by_year.png", dpi=150)

plt.show()