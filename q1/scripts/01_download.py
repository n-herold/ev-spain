import time
from pathlib import Path

import requests

# Target folder: <project>/q1/data/raw (created if missing)
project_dir = Path(__file__).resolve().parent.parent.parent
raw_dir = project_dir / "q1" / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

# Period: January 2023 to September 2026
START = (2023, 1)
END = (2026, 9)

for year in range(START[0], END[0] + 1):
    for month in range(1, 13):
        # Skip months outside the period
        if (year, month) < START or (year, month) > END:
            continue

        filename = f"export_mensual_mat_{year}{month:02d}.zip"
        target = raw_dir / filename

        # Already downloaded? Then skip
        if target.exists():
            print(f"{filename}: already exists, skipped")
            continue

        url = (
            f"https://www.dgt.es/microdatos/salida/{year}/{month}"
            f"/vehiculos/matriculaciones/{filename}"
        )

        response = requests.get(url, timeout=120)

        # Only save on success (200)
        if response.status_code != 200:
            print(f"{filename}: ERROR, status code {response.status_code}")
            continue

        with open(target, "wb") as f:
            f.write(response.content)

        print(f"{filename}: saved ({len(response.content) / 1_000_000:.1f} MB)")

        # Short pause to avoid overloading the server
        time.sleep(2)

print("Done.")