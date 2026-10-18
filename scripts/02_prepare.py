import zipfile
from pathlib import Path

import pandas as pd

project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"
out_dir = project_dir / "data" / "processed"
out_dir.mkdir(parents=True, exist_ok=True)

# Feste Spaltenpositionen der DGT-Datei: Name -> (Start, Ende)
COLUMNS = {
    "reg_date": (0, 8),          # FEC_MATRICULA, Format TTMMJJJJ
    "brand": (17, 47),           # MARCA_ITV
    "model": (47, 69),           # MODELO_ITV
    "vehicle_type": (91, 93),    # COD_TIPO (40 = Pkw)
    "province": (152, 154),      # COD_PROVINCIA_VEH
    "procedure": (156, 157),     # CLAVE_TRAMITE (1 = normale Zulassung)
    "new_used": (178, 179),      # IND_NUEVO_USADO (N = neu)
    "municipality_ine": (192, 197),  # COD_MUNICIPIO_INE_VEH
    "ev_category": (453, 457),   # CATEGORIA_VEHICULO_ELECTRICO
}


def prepare_month(zip_path: Path) -> pd.DataFrame:
    """Liest eine Monats-ZIP, filtert neue Pkw und gibt die Zeilen zurück."""
    with zipfile.ZipFile(zip_path) as z:
        txt_name = z.namelist()[0]
        with z.open(txt_name) as f:
            df = pd.read_fwf(
                f,
                colspecs=list(COLUMNS.values()),
                names=list(COLUMNS.keys()),
                skiprows=1,              # Kopfzeile überspringen
                dtype=str,
                encoding="latin-1",
                keep_default_na=False,   # leere Felder bleiben leer
            )

    # Nur neue Pkw mit normaler Zulassung
    df = df[
        (df["vehicle_type"] == "40")
        & (df["procedure"] == "1")
        & (df["new_used"] == "N")
    ].copy()

    # Datum umwandeln (TTMMJJJJ) und Jahr/Monat ableiten
    df["reg_date"] = pd.to_datetime(df["reg_date"], format="%d%m%Y", errors="coerce")
    df["year"] = df["reg_date"].dt.year
    df["month"] = df["reg_date"].dt.month

    # Leere Elektrokategorie = Verbrenner bzw. sonstige
    df["ev_category"] = df["ev_category"].replace("", "OTHER")

    return df.drop(columns=["vehicle_type", "procedure", "new_used"])


for zip_path in sorted(raw_dir.glob("export_mensual_mat_*.zip")):
    period = zip_path.stem.split("_")[-1]        # z. B. 202301
    target = out_dir / f"registrations_{period}.parquet"

    if target.exists():
        print(f"{period}: schon vorhanden, übersprungen")
        continue

    df = prepare_month(zip_path)

    # Nur Zeilen, deren Datum im Zielmonat liegt (Altfälle wie 1958 fallen raus)
    expected_year, expected_month = int(period[:4]), int(period[4:])
    df = df[(df["year"] == expected_year) & (df["month"] == expected_month)]

    df.to_parquet(target, index=False)
    print(f"{period}: {len(df):,} neue Pkw gespeichert")

print("Fertig.")