import time
from pathlib import Path

import requests

# Zielordner: <Projektordner>/data/raw (wird angelegt, falls er fehlt)
project_dir = Path(__file__).resolve().parent.parent
raw_dir = project_dir / "data" / "raw"
raw_dir.mkdir(parents=True, exist_ok=True)

# Zeitraum: Januar 2023 bis September 2026
START = (2023, 1)
END = (2026, 9)

for year in range(START[0], END[0] + 1):
    for month in range(1, 13):
        # Monate außerhalb des Zeitraums überspringen
        if (year, month) < START or (year, month) > END:
            continue

        filename = f"export_mensual_mat_{year}{month:02d}.zip"
        target = raw_dir / filename

        # Schon vorhanden? Dann nicht noch einmal laden
        if target.exists():
            print(f"{filename}: schon vorhanden, übersprungen")
            continue

        url = (
            f"https://www.dgt.es/microdatos/salida/{year}/{month}"
            f"/vehiculos/matriculaciones/{filename}"
        )

        response = requests.get(url, timeout=120)

        # Nur bei Erfolg (200) speichern
        if response.status_code != 200:
            print(f"{filename}: FEHLER, Statuscode {response.status_code}")
            continue

        with open(target, "wb") as f:
            f.write(response.content)

        print(f"{filename}: gespeichert ({len(response.content) / 1_000_000:.1f} MB)")

        # Kurze Pause, um den Server nicht zu belasten
        time.sleep(2)

print("Fertig.")