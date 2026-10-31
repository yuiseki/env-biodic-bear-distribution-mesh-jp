#!/usr/bin/env python3
"""Verify the Parquet against the ZIPs read by a different route.

Route A: GDAL (ogrinfo, through /vsizip/), parsed as text. Route B: geopandas/pyarrow on the Parquet. Route C: DuckDB on the Parquet.
Also: mesh code structure, duplicates, geometry vs the code, and the relations the sources state about themselves.
Writes docs/verification.json; exits 1 on any mismatch.
"""

import collections
import json
import re
import subprocess
import sys
from pathlib import Path

import duckdb
import geopandas as gpd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from convert import BEARS, COMBINED, SURVEYS, cell_bounds, mesh_problems

RAW = sorted((ROOT / "raw").iterdir())[-1]
PQ = ROOT / "data" / "parquet" / "bear_mesh_long.parquet"
FIELD = re.compile(rb"^  (.+?) \((\w+)\) = (.*)$")


def ogr_features(zip_name: str, member: str, enc: str) -> tuple[list[dict[str, str]], list[str]]:
    """All features of one layer through GDAL; returns (rows as dict, the ogrinfo summary lines)."""
    path = f"/vsizip/{RAW / 'zips' / zip_name}/{member}"
    summ = subprocess.run(["ogrinfo", "-ro", "-so", "-al", path], capture_output=True, check=True).stdout.decode("utf-8", "replace").splitlines()
    out = subprocess.run(["ogrinfo", "-ro", "-q", "-al", "-geom=NO", path], capture_output=True, check=True).stdout
    rows, cur = [], None
    for line in out.split(b"\n"):
        if line.startswith(b"OGRFeature("):
            cur = {}
            rows.append(cur)
        else:
            m = FIELD.match(line)
            if m and cur is not None:
                cur[m.group(1).decode(enc)] = m.group(3).decode(enc)
    return rows, summ


def member_of(zip_name: str, suffix: str) -> str:
    """the member name as ogr must be given it (the bytes the ZIP stores; unzip -Z1 prints them as they are)."""
    raw = subprocess.run(["unzip", "-Z1", str(RAW / "zips" / zip_name)], capture_output=True, check=True).stdout.split(b"\n")
    hits = []
    for b in raw:
        for enc in ("utf-8", "cp932"):
            try:
                t = b.decode(enc)
            except UnicodeError:
                continue
            if t.endswith(suffix):
                hits.append(t)
            break
    if len(hits) != 1:
        raise SystemExit(f"{zip_name}: {suffix} -> {hits}")
    return hits[0]


def main() -> int:
    mism: list[str] = []
    gdf = gpd.read_parquet(PQ)
    tbl = pq.read_table(PQ)
    con = duckdb.connect()
    duck = {(a, b): n for a, b, n in con.execute(f"select survey_id, species, count(*) from read_parquet('{PQ}') group by 1,2").fetchall()}
    pqc = {k: int(v) for k, v in gdf.groupby(["survey_id", "species"]).size().items()}
    out: dict = {"parquet_rows": len(gdf), "arrow_rows": tbl.num_rows, "duckdb_rows": con.execute(f"select count(*) from read_parquet('{PQ}')").fetchone()[0],
                 "surveys": {}}  # fmt: skip
    for k, v in (("arrow_rows", len(gdf)), ("duckdb_rows", len(gdf))):
        if out[k] != v:
            mism.append(f"{k}: {out[k]} != {v}")
    if duck != pqc:
        mism.append(f"geopandas vs duckdb group counts differ: {pqc} {duck}")
    geo_meta = json.loads(tbl.schema.metadata[b"geo"])
    out["geoparquet"] = {"version": geo_meta["version"], "primary_column": geo_meta["primary_column"], "crs_id": geo_meta["columns"]["geometry"]["crs"]["id"],
                         "geometry_types": geo_meta["columns"]["geometry"]["geometry_types"]}  # fmt: skip
    mesh_sets: dict[str, set[str]] = {}
    # cells computed from the code: one row per row of the long table, same key, same order; compared with the distributed polygons for yo4
    CPQ = ROOT / "data" / "parquet" / "bear_mesh_cells_from_code.parquet"
    cg = gpd.read_parquet(CPQ)
    cmeta = json.loads(pq.read_table(CPQ).schema.metadata[b"geo"])
    cinfo: dict = {"rows": len(cg), "duckdb_rows": con.execute(f"select count(*) from read_parquet('{CPQ}')").fetchone()[0],
                   "primary_column": cmeta["primary_column"], "crs_id": cmeta["columns"][cmeta["primary_column"]]["crs"]["id"]}  # fmt: skip
    cinfo["key_equals_long_table"] = bool((cg[["survey_id", "source_row", "mesh_code"]].reset_index(drop=True) == gdf[["survey_id", "source_row", "mesh_code"]].reset_index(drop=True)).all().all())
    cinfo["key_unique"] = bool(not cg.duplicated(["survey_id", "source_row"]).any())
    cinfo["null_geometries"] = int(cg.geometry.isna().sum())
    cinfo["invalid_geometries"] = int((~cg.geometry.is_valid).sum())
    cinfo["cell_sizes_deg_by_digits"] = {str(k): sorted({(round(g.bounds[2] - g.bounds[0], 5), round(g.bounds[3] - g.bounds[1], 5)) for g in grp.geometry}) for k, grp in cg.groupby("mesh_digits")}
    if cinfo["rows"] != len(gdf) or cinfo["duckdb_rows"] != len(gdf) or not cinfo["key_equals_long_table"] or not cinfo["key_unique"] or cinfo["null_geometries"] or cinfo["invalid_geometries"]:
        mism.append(f"cells file does not match the long table: {cinfo}")
    ydist = gdf[gdf.survey_id == "yo4"].reset_index(drop=True)
    ycell = cg[cg.survey_id == "yo4"].reset_index(drop=True)
    same = sum(1 for a, b in zip(ydist.geometry, ycell.geometry) if max(abs(x - y) for x, y in zip(a.bounds, b.bounds)) < 2e-6 and abs(a.area - b.area) < 1e-7)
    cinfo["yo4_computed_cell_equals_distributed_polygon (bounds within 2e-6 deg, area within 1e-7)"] = [same, len(ydist)]
    if same != len(ydist):
        mism.append(f"yo4: only {same} of {len(ydist)} computed cells equal the distributed polygons")
    out["cells_from_code"] = cinfo
    for s in SURVEYS:
        member = member_of(s.zip_name, s.member_suffix)
        rows, summ = ogr_features(s.zip_name, member, "utf-8" if s.survey_id == "yo4" else "cp932")  # GDAL recodes the DBF itself; CSV bytes pass through
        info: dict = {"member": member, "gdal_features_in_layer": len(rows)}
        sub = gdf[gdf.survey_id == s.survey_id]
        if s.survey_id == "yo4":
            bear = rows
            ogr_geom = [ln for ln in summ if ln.startswith("Geometry:")][0]
            ogr_count = [ln for ln in summ if ln.startswith("Feature Count:")][0]
            ext = [ln for ln in summ if ln.startswith("Extent:")][0]
            info.update({"gdal_geometry": ogr_geom, "gdal_feature_count_line": ogr_count, "gdal_extent": ext,
                         "gdal_crs_id": [ln.strip() for ln in summ if 'ID["EPSG"' in ln][-1]})  # fmt: skip
            freq = {f: dict(collections.Counter(r[f] for r in bear)) for f in ("H22_29", "単年度", "第6回で確", "第6回のみ", "両調査で確")}
            info["attribute_frequencies_gdal"] = freq
            for f, c in freq.items():
                mine = dict(collections.Counter(sub[f]))
                if mine != c:
                    mism.append(f"yo4 {f}: gdal {c} vs parquet {mine}")
            if [r["5kmMesh"] for r in bear] != list(sub.mesh_code):
                mism.append("yo4 mesh codes differ in order or value")
            if [r["Descriptio"] for r in bear] != list(sub["Descriptio"]):
                mism.append("yo4 Descriptio differs")
            tot = gdf[gdf.survey_id == "yo4"].geometry
            b = tot.total_bounds
            info["parquet_bounds"] = [round(float(x), 6) for x in b]
            info["geometry_types"] = dict(collections.Counter(tot.geom_type))
            info["invalid_geometries"] = int((~tot.is_valid).sum())
            ok = 0
            for code, geom in zip(sub.mesh_code, sub.geometry):
                w, so, e, n = cell_bounds(code)
                gb = geom.bounds
                if max(abs(gb[0] - w), abs(gb[1] - so), abs(gb[2] - e), abs(gb[3] - n)) < 2e-6:
                    ok += 1
            info["polygon_bounds_equal_to_cell_computed_from_code"] = ok
            if ok != len(sub):
                mism.append(f"yo4: {len(sub) - ok} polygons differ from the cell computed from the code")
            ws = {(round(g.bounds[2] - g.bounds[0], 5), round(g.bounds[3] - g.bounds[1], 5)) for g in tot}
            info["cell_sizes_deg_lon_lat"] = sorted(ws)
            flags = collections.Counter((r["H22_29"], r["第6回で確"], r["第6回のみ"], r["両調査で確"], r["単年度"]) for r in bear)
            info["flag_combinations (H22_29, 第6回で確, 第6回のみ, 両調査で確, 単年度)"] = {",".join(k): v for k, v in sorted(flags.items())}
            n6 = sum(1 for r in bear if r["第6回で確"] == "1")
            nboth = sum(1 for r in bear if r["両調査で確"] == "1")
            nonly = sum(1 for r in bear if r["第6回のみ"] == "1")
            info["第6回で確 == 第6回のみ + 両調査で確"] = (n6, nonly, nboth, n6 == nonly + nboth)
            if n6 != nonly + nboth:
                mism.append("yo4: 第6回で確 != 第6回のみ + 両調査で確")
            mesh_sets["yo4_any"] = {r["5kmMesh"] for r in bear if r["H22_29"] == "1" or r["第6回のみ"] == "1"}
            mesh_sets["yo4_h22_29"] = {r["5kmMesh"] for r in bear if r["H22_29"] == "1"}
            mesh_sets["yo4_6"] = {r["5kmMesh"] for r in bear if r["第6回で確"] == "1"}
        else:
            sp_f, mcol = s.species_field, s.mesh_field
            if sp_f is None:
                raise SystemExit("species field required")
            bear = [r for r in rows if r[sp_f] in (*BEARS, COMBINED)]
            species_counts = dict(collections.Counter(r[sp_f] for r in bear))
            all_species = dict(collections.Counter(r[sp_f] for r in rows))
            info["species_in_csv_all"] = all_species
            info["gdal_bear_rows"] = species_counts
            mine = dict(collections.Counter(sub.species))
            if mine != species_counts:
                mism.append(f"{s.survey_id}: gdal {species_counts} vs parquet {mine}")
            if [r[mcol] for r in bear] != list(sub.mesh_code):
                mism.append(f"{s.survey_id}: mesh codes differ in order or value")
            for c in ("地名", "分類群", "種コード", "備考", "調査票番号", "年月", "確認調査"):
                if c in bear[0]:
                    if [r[c] for r in bear] != [x if isinstance(x, str) else None for x in sub[c]]:
                        mism.append(f"{s.survey_id}: column {c} differs")
            for c in ("備考", "確認調査", "分類群"):
                if c in bear[0]:
                    info[f"frequency_of_{c}"] = dict(collections.Counter(r[c] for r in bear))
            if "年月" in bear[0]:
                ym = [r["年月"] for r in bear]
                info["年月_min_max"] = [min(ym), max(ym)]
                info["年月_lengths"] = dict(collections.Counter(len(x) for x in ym))
            if s.survey_id in ("do04", "do05"):
                info["distinct_survey_sheets(調査票番号)"] = len({r["調査票番号"] for r in bear})
                info["distinct_surveyor_codes(調査者コード)"] = len({r["調査者コード"] for r in bear})
            if s.survey_id == "do06":
                mesh_sets["do06"] = {r[mcol] for r in bear}
                mesh_sets["do06_only6"] = {r[mcol] for r in bear if r["確認調査"] == "第6回のみ確認"}
        codes = list(sub.mesh_code)
        info["rows"] = len(codes)
        info["distinct_mesh_codes"] = len(set(codes))
        info["mesh_code_lengths"] = dict(collections.Counter(len(c) for c in codes))
        probs = collections.Counter(p for c in codes for p in mesh_problems(c))
        info["mesh_code_structure_problems"] = dict(probs)
        if probs:
            mism.append(f"{s.survey_id}: mesh code problems {dict(probs)}")
        if s.survey_id in ("do06", "yo4") and len(set(codes)) != len(codes):
            mism.append(f"{s.survey_id}: duplicated mesh codes")
        if s.survey_id == "do02" and len(set(codes)) != len(codes):
            info["do02_duplicates_within_species"] = True
        per_species = {}
        for sp, g in sub.groupby("species"):
            per_species[sp] = {"rows": len(g), "distinct_meshes": int(g.mesh_code.nunique())}
        info["per_species"] = per_species
        if s.survey_id != "yo4":
            dups = {sp: v["rows"] - v["distinct_meshes"] for sp, v in per_species.items()}
            info["duplicate_rows_within_species(mesh repeated)"] = dups
        c_lat = [int(c[:2]) for c in codes]
        c_lon = [int(c[2:4]) for c in codes]
        info["mesh_prefix_range(lat,lon)"] = [[min(c_lat), max(c_lat)], [min(c_lon), max(c_lon)]]
        out["surveys"][s.survey_id] = info
    # relations between sources
    do6, y6 = mesh_sets["do06"], mesh_sets["yo4_6"]
    rel = {"do06_meshes": len(do6), "yo4_第6回で確_meshes": len(y6), "in_both": len(do6 & y6), "only_do06": sorted(do6 - y6), "only_yo4": sorted(y6 - do6),
           "do06_第6回のみ確認_rows": len(mesh_sets["do06_only6"]), "yo4_第6回のみ_meshes": len({m for m in mesh_sets["yo4_any"] if m not in mesh_sets["yo4_h22_29"]}),
           "yo4_H22_29_meshes": len(mesh_sets["yo4_h22_29"])}  # fmt: skip
    out["cross_checks"] = rel
    out["mismatches"] = mism
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "verification.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(json.dumps({"mismatches": mism, "rows": out["parquet_rows"], "cross_checks": rel}, ensure_ascii=False, indent=1))
    return 1 if mism else 0


if __name__ == "__main__":
    sys.exit(main())
