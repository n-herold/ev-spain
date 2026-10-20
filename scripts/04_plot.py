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


def run_sql_file(name):
    """Liest eine SQL-Datei aus sql/ und gibt das Ergebnis als Tabelle zurück."""
    text = (project_dir / "sql" / name).read_text(encoding="utf-8").strip().rstrip(";")
    return con.execute(text).df()


# 2) Beide Abfragen ausführen und über year und month zusammenführen
growth = run_sql_file("03_growth.sql")
anom = run_sql_file("04_anomalies.sql")

df = growth.merge(
    anom[["year", "month", "share_pct", "base_pct", "diff_pp", "z_score"]],
    on=["year", "month"],
)

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

# Auffällige Monate (Schwelle hier ändern)
Z_SCHWELLE = 2
df["auffaellig"] = df["z_score"].abs() >= Z_SCHWELLE

stichtag = pd.Timestamp("2026-02-28")  # Hormus-Schließung

fig_dir = project_dir / "figures"
fig_dir.mkdir(exist_ok=True)

# 4) Abbildung 1: links einzeln, rechts kumuliert
fig, axes = plt.subplots(3, 2, sharex=True, figsize=(14, 10))

axes[0, 0].plot(df["date"], df["bev"], marker="o")
axes[0, 0].set_ylabel("BEV pro Monat")
axes[0, 0].set_title("Einzelwerte pro Monat")

axes[1, 0].plot(df["date"], df["bev_share_pct"], marker="o", color="green")
axes[1, 0].set_ylabel("Anteil BEV (%)")

axes[2, 0].plot(df["date"], df["growth_yoy_pct"], marker="o", color="orange")
axes[2, 0].axhline(0, color="grey", linewidth=0.8)
axes[2, 0].set_ylabel("Wachstum zum Vorjahresmonat (%)")

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

# 6) Abbildung 3: Anomalien (oben Anteil gegen Basis, unten z-Score)
fig3, (ax1, ax2) = plt.subplots(
    2, 1, sharex=True, figsize=(11, 8), gridspec_kw={"height_ratios": [2, 1]}
)

ax1.plot(df["date"], df["share_pct"], marker="o", label="Anteil BEV (%)")
ax1.plot(df["date"], df["base_pct"], linestyle="--", color="grey", label="Basis (Nachbarmonate)")
ax1.set_ylabel("Anteil BEV an Neuzulassungen (%)")
ax1.legend()

hot = df[df["auffaellig"]]
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

colors = ["red" if flag else "steelblue" for flag in df["auffaellig"]]
ax2.bar(df["date"], df["z_score"], width=20, color=colors)
ax2.axhline(0, color="black", linewidth=0.8)
ax2.axhline(Z_SCHWELLE, color="red", linestyle="--", linewidth=0.8)
ax2.axhline(-Z_SCHWELLE, color="red", linestyle="--", linewidth=0.8)
ax2.set_ylabel("z-Score")

for ax in (ax1, ax2):
    ax.grid(alpha=0.3)

ax1.set_title(f"BEV-Anteil und Abweichung vom lokalen Normalwert (|z| ab {Z_SCHWELLE} markiert)")
plt.tight_layout()
plt.savefig(fig_dir / "bev_anomalies.png", dpi=150)

plt.show()