#!/usr/bin/env python3
"""docs/bear_mesh_by_survey.png: the bear meshes of each survey side by side (Japan, transparent background, no basemap).

do02/do04/do05 panels: ツキノワグマ rows only (2nd-order mesh cells, ~10 km). do06 and yo4 panels: the source does not separate the two species
(ツキノワグマ・ヒグマ / クマ類); yo4 shows the meshes with H22_29 = 1 or 第6回のみ = 1. Cell outlines of the CSV surveys are computed from the mesh
code (JIS X 0410) for this picture only; the CSV data carry no geometry and the Parquet has none for them.
"""

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from convert import cell_bounds

plt.rcParams["font.family"] = ["Noto Sans CJK JP", "DejaVu Sans"]
g = gpd.read_parquet(ROOT / "data" / "parquet" / "bear_mesh_long.parquet")
panels = [
    ("do02", "第2回 (昭和53年度)\nツキノワグマ  2次メッシュ", g[(g.survey_id == "do02") & (g.species == "ツキノワグマ")].mesh_code.unique()),
    ("do04", "第4回 (平成元〜3年度)\nツキノワグマ  2次メッシュ", g[(g.survey_id == "do04") & (g.species == "ツキノワグマ")].mesh_code.unique()),
    ("do05", "第5回 (平成9,10年度)\nツキノワグマ  2次メッシュ", g[(g.survey_id == "do05") & (g.species == "ツキノワグマ")].mesh_code.unique()),
    ("do06", "第6回 (平成12〜16年度)\nツキノワグマ・ヒグマ (種の区別なし)  5kmメッシュ", g[g.survey_id == "do06"].mesh_code.unique()),
    ("yo4", "要注意鳥獣(クマ等) 平成28〜30年度\nクマ類 (種の区別なし)  5kmメッシュ  H22_29=1 または 第6回のみ=1",
     g[(g.survey_id == "yo4") & ((g.H22_29 == "1") | (g["第6回のみ"] == "1"))].mesh_code.unique()),
]
fig, axes = plt.subplots(2, 3, figsize=(15, 9.5), sharex=True, sharey=True)
for ax, (sid, title, codes) in zip(axes.flat, panels):
    polys = []
    for c in codes:
        w, s, e, n = cell_bounds(c)
        polys.append([(w, s), (e, s), (e, n), (w, n)])
    ax.add_collection(PolyCollection(polys, facecolors="#1b4d3e", edgecolors="none", linewidths=0))
    ax.set_xlim(122.5, 154.2)
    ax.set_ylim(30.5, 45.8)
    ax.set_aspect(1 / 0.82)
    ax.set_title(f"{title}\n{len(codes):,} meshes", fontsize=10)
    ax.patch.set_alpha(0)
    ax.tick_params(labelsize=7)
fig.delaxes(axes.flat[5])
fig.text(0.70, 0.27, "出典：環境省生物多様性センター『自然環境保全基礎調査』\n『要注意鳥獣(クマ等)生息分布調査』を加工して作成\n(yuiseki が mesh コードから描画。環境省の公表物ではありません)\n\n"
         "いた記録のメッシュ集計であり、空白は「いない」の証拠ではありません。\n調査回で手法が異なり、単純比較はできません。", fontsize=10, va="center", ha="left")
fig.patch.set_alpha(0)
(ROOT / "docs").mkdir(exist_ok=True)
fig.savefig(ROOT / "docs" / "bear_mesh_by_survey.png", dpi=110, transparent=True, bbox_inches="tight")
print("ok")
