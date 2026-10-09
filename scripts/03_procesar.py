"""Convierte la caché cruda (data/raw) en tablas parquet (data/processed), sin red.

Procesa Matches de cada temporada de config/params.yaml y todos los partidos que tengan algo
en la caché. Es incremental: lo ya convertido se salta (usa --forzar para rehacerlo).

Cómo correrlo (PowerShell, desde la raíz del repo y con el entorno activado):
    python scripts/03_procesar.py
    python scripts/03_procesar.py --forzar
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter

from tqdm import tqdm

from ojo.config import DIR_RAW, params
from ojo.datos import almacen


def ids_en_cache() -> list[int]:
    """Partidos con al menos una API por partido en la caché (nombres {match_id}.json.gz)."""
    ids = set()
    for api in ("events", "frames_360", "lineups", "team_match_stats"):
        for archivo in DIR_RAW.glob(f"{api}/*/*.json.gz"):
            nombre = archivo.name.removesuffix(".json.gz")
            if nombre.isdigit():
                ids.add(int(nombre))
    return sorted(ids)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--forzar", action="store_true", help="rehace también lo ya convertido")
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    p = params()
    for s in p["liga"]["season_ids"]:
        try:
            almacen.procesar_temporada(p["liga"]["competition_id"], s)
        except FileNotFoundError as error:
            print(f"⚠ {error}")
    ids = ids_en_cache()
    escritas: Counter[str] = Counter()
    for match_id in tqdm(ids, desc="Procesando", unit="partido"):
        escritas.update(almacen.procesar_partido(match_id, forzar=args.forzar))
    print(f"Partidos en caché: {len(ids):,}. Tablas escritas: {dict(escritas) or 'ninguna (todo estaba al día)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
