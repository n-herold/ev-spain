import zipfile
from pathlib import Path

import pandas as pd

project_dir = Path(__file__).resolve().parent.parent.parent
raw_dir = project_dir / "q1" / "data" / "raw"
out_dir = project_dir / "q1" / "data" / "processed"
out_dir.mkdir(parents=True, exist_ok=True)

# Fixed column positions of the DGT file: name -> (start, end)
COLUMNS = {
    "reg_date": (0, 8),          # FEC_MATRICULA, format DDMMYYYY
    "brand": (17, 47),           # MARCA_ITV
    "model": (47, 69),           # MODELO_ITV
    "vehicle_type": (91, 93),    # COD_TIPO (40 = passenger car)
    "province": (152, 154),      # COD_PROVINCIA_VEH
    "procedure": (156, 157),     # CLAVE_TRAMITE (1 = normal registration)
    "new_used": (178, 179),      # IND_NUEVO_USADO (N = new)
    "municipality_ine": (192, 197),  # COD_MUNICIPIO_INE_VEH
    "ev_category": (453, 457),   # CATEGORIA_VEHICULO_ELECTRICO
}


def prepare_month(zip_path: Path) -> pd.DataFrame:
    """Read one monthly ZIP, keep new passenger cars and return the rows."""
    with zipfile.ZipFile(zip_path) as z:
        txt_name = z.namelist()[0]
        with z.open(txt_name) as f:
            df = pd.read_fwf(
                f,
                colspecs=list(COLUMNS.values()),
                names=list(COLUMNS.keys()),
                skiprows=1,              # skip header line
                dtype=str,
                encoding="latin-1",
                keep_default_na=False,   # empty fields stay empty
            )

    # Only new passenger cars with a normal registration
    df = df[
        (df["vehicle_type"] == "40")
        & (df["procedure"] == "1")
        & (df["new_used"] == "N")
    ].copy()

    # Convert date (DDMMYYYY) and derive year/month
    df["reg_date"] = pd.to_datetime(df["reg_date"], format="%d%m%Y", errors="coerce")
    df["year"] = df["reg_date"].dt.year
    df["month"] = df["reg_date"].dt.month

    # Empty electric category = combustion engine or other
    df["ev_category"] = df["ev_category"].replace("", "OTHER")

    return df.drop(columns=["vehicle_type", "procedure", "new_used"])


for zip_path in sorted(raw_dir.glob("export_mensual_mat_*.zip")):
    period = zip_path.stem.split("_")[-1]        # e.g. 202301
    target = out_dir / f"registrations_{period}.parquet"

    if target.exists():
        print(f"{period}: already exists, skipped")
        continue

    df = prepare_month(zip_path)

    # Only rows whose date is in the target month (legacy cases like 1958 drop out)
    expected_year, expected_month = int(period[:4]), int(period[4:])
    df = df[(df["year"] == expected_year) & (df["month"] == expected_month)]

    df.to_parquet(target, index=False)
    print(f"{period}: {len(df):,} new passenger cars saved")

print("Done.")