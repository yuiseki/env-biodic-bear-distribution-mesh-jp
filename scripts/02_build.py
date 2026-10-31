#!/usr/bin/env python3
"""raw/<date>/zips/*.zip -> data/parquet/bear_mesh_long.parquet (GeoParquet, JGD2011 EPSG:6668) and docs/summary.json."""

import json
import sys
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from convert import ATTR_COLUMNS, CLASS, SURVEYS, cell_polygon, long_rows

RAW = sorted((ROOT / "raw").iterdir())[-1]
OUT = ROOT / "data" / "parquet" / "bear_mesh_long.parquet"
OUT_CELLS = ROOT / "data" / "parquet" / "bear_mesh_cells_from_code.parquet"


def main() -> None:
    frames = []
    for s in SURVEYS:
        zp = RAW / "zips" / s.zip_name
        if s.survey_id != "yo4":
            frames.append(pd.DataFrame(long_rows(s, zp)))
            continue
        g = pyogrio.read_dataframe(f"/vsizip/{zp}/{s.member_suffix}", encoding=None)  # encoding from Bear.cpg (Shift_JIS)
        names = list(g.columns)
        d = pd.DataFrame({
            "survey_id": s.survey_id, "survey_label": s.survey_label, "species": CLASS, "species_in_source": False,
            "mesh_code": g["5kmMesh"].astype(str), "source_file": f"{s.zip_name}:{s.member_suffix}", "source_row": range(1, len(g) + 1),
        })  # fmt: skip
        for c in ATTR_COLUMNS:
            d[c] = g[c].astype(str) if c in names else None
        d["geometry"] = g.geometry.values
        frames.append(d)
        yo4_crs = g.crs
    cols = ["survey_id", "survey_label", "species", "species_in_source", "mesh_code", "source_file", "source_row", *ATTR_COLUMNS, "geometry"]
    frames = [f.reindex(columns=cols) for f in frames]
    for f in frames:
        if "geometry" in f and f["geometry"].isna().all():
            f["geometry"] = None
    df = pd.concat(frames, ignore_index=True)
    for c in ATTR_COLUMNS:
        df[c] = df[c].astype("string")
    geo = gpd.GeoDataFrame(df, geometry="geometry", crs=yo4_crs)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    geo.to_parquet(OUT, index=False, compression="zstd", write_covering_bbox=True)
    # a separate file: cells COMPUTED from mesh_code (not the distributed shapes), one row per row of the long table, joined by (survey_id, source_row)
    cells = gpd.GeoDataFrame(
        {
            "survey_id": geo.survey_id, "source_row": geo.source_row, "mesh_code": geo.mesh_code,
            "mesh_digits": geo.mesh_code.str.len().astype("int64"),
            "cell_kind": geo.mesh_code.str.len().map({6: "2nd-order regional mesh (6 digits)", 8: "5 km mesh (8 digits)"}),
            "geometry_computed_from_mesh_code": [cell_polygon(c) for c in geo.mesh_code],
        },
        geometry="geometry_computed_from_mesh_code", crs=yo4_crs,
    )  # fmt: skip
    cells.to_parquet(OUT_CELLS, index=False, compression="zstd", write_covering_bbox=True)
    summ = {
        "raw": RAW.relative_to(ROOT).as_posix(), "rows": len(geo), "crs": str(yo4_crs), "crs_epsg": yo4_crs.to_epsg(), "cells_rows": len(cells),
        "rows_by_survey_species": {f"{k[0]}|{k[1]}": int(v) for k, v in geo.groupby(["survey_id", "species"]).size().items()},
    }  # fmt: skip
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "summary.json").write_text(json.dumps(summ, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps(summ, ensure_ascii=False, indent=1), OUT.stat().st_size)


if __name__ == "__main__":
    main()
