#!/usr/bin/env python3
"""Write data/README.md (the card), data/LICENSE and data/provenance.yaml from docs/verification.json and raw/<date>/MANIFEST.json.
Every number in the card comes from those files."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
V = json.loads((ROOT / "docs" / "verification.json").read_text())
S = json.loads((ROOT / "docs" / "summary.json").read_text())
RAW = ROOT / S["raw"]
M = json.loads((RAW / "MANIFEST.json").read_text())
by = {Path(f["path"]).name: f for f in M["files"]}
sv = V["surveys"]
n = S["rows"]
DAY = RAW.name


def row(sid: str, label: str, period: str, mesh: str, zipn: str) -> str:
    i = sv[sid]
    ps = i["per_species"]
    cells = "; ".join(f"{k}: {v['rows']:,} rows / {v['distinct_meshes']:,} meshes" for k, v in ps.items())
    z = by[zipn]
    return f"| `{sid}` | {label} | {period} | {mesh} | {cells} | `{zipn}` {z['bytes']:,} B, Last-Modified {z['last_modified']} |"


y = sv["yo4"]
fc = y["flag_combinations (H22_29, 第6回で確, 第6回のみ, 両調査で確, 単年度)"]
fr = y["attribute_frequencies_gdal"]
cx = V["cross_checks"]
only_this = fc["1,0,0,0,0"] + fc["1,0,0,0,1"]
card = f"""---
license: other
license_name: biodic-terms-of-service-pdl-1.0
license_link: https://www.biodic.go.jp/copyright/terms_of_service.html
language:
- ja
tags:
- japan
- bear
- ursus-thibetanus
- ursus-arctos
- distribution
- mesh
- biodiversity
- ministry-of-the-environment
- geoparquet
size_categories:
- 10K<n<100K
pretty_name: Bear (Asiatic black bear, brown bear) 5 km mesh distribution of Japan, Biodiversity Center, 5 surveys
configs:
- config_name: default
  data_files: parquet/bear_mesh_long.parquet
- config_name: cells_from_code
  data_files: parquet/bear_mesh_cells_from_code.parquet
---

# env-biodic-bear-distribution-mesh-jp

The bear (ツキノワグマ, ヒグマ) distribution mesh files that the Biodiversity Center of the Ministry of the Environment of Japan
(環境省 生物多様性センター) publishes for five surveys, put into one long table of {n:,} rows, with the values left as they are in the files.
Only the bear rows are kept; the ZIPs hold other species too (listed below), and those are not republished.

Credit. 出典：環境省生物多様性センター『自然環境保全基礎調査』『要注意鳥獣(クマ等)生息分布調査』を加工して作成
(<https://www.biodic.go.jp/shapedata/download.html>, データダウンロード日 {M['fetched_at_utc'][:10]}).
Processed. Rows were picked out of the original files and put in a Parquet table by yuiseki (the surveyor-code column was left out, see Columns): nothing was corrected, re-projected, filled in or merged. A second file holds cells that yuiseki computed from the mesh codes; they are not shapes distributed by the Ministry.
This is not a publication of the Ministry, and nothing here is to be shown as if the Ministry had made it.

## What this is, and what it is not

- It is a mesh tally of records of bears being there (sightings, signs, captures, answers to questionnaires and interviews, depending on the survey).
  A mesh without a row, or a yo4 mesh with all flags 0, is not evidence that bears are absent: it only means no information was collected or kept.
- The surveys used different methods, periods, sources and mesh sizes, so the counts of one survey are not directly comparable with another.
  The Ministry says so itself (quotes below). Do not read a change of counts between surveys as a change of the bears.
- Reports of the Ministry state that the 5 km mesh includes "一時的な目撃等" and that information from the deep mountains may be thin (quotes below).

## Sources

All from <https://www.biodic.go.jp/shapedata/download.html> (page saved in the raw copy, read {DAY}; fetch started {M['fetched_at_utc']}).
Fetched with plain `curl`, one file at a time, 2 seconds apart, User-Agent `{M['user_agent']}` (`src/fetch.py`). No request was refused. Only www.biodic.go.jp, www.arcgis.com and www.digital.go.jp were asked.

| id | survey | period (as the Biodiversity Center page gives it) | mesh | bear rows in this table | ZIP |
|---|---|---|---|---|---|
{row('do02', '自然環境保全基礎調査 第2回 動物分布調査 (哺乳類)', '昭和53年度', '6-digit code, see "Mesh codes"', 'do02.zip')}
{row('do04', '第4回 動物分布調査 (哺乳類)', '平成元～3年度', '6-digit code', 'do04.zip')}
{row('do05', '第5回 動物分布調査 (哺乳類) = 生物多様性調査 種の多様性調査 第1期', '平成9, 10年度', '6-digit code', 'do05.zip')}
{row('do06', '第6回 動物分布調査 (哺乳類) = 種の多様性調査 第2期', '平成12～16年度', '8-digit 5 km mesh code', 'do06.zip')}
{row('yo4', '要注意鳥獣(クマ等)生息分布調査 平成28～30年度 (平成30年度中大型哺乳類分布調査) ヒグマ、ツキノワグマ', '情報は平成22年度以降', '8-digit 5 km mesh code + polygon', 'yo4.zip')}

Not taken: do03 (birds only), yo1 (アライグマ), yo5 (カモシカ), and the non-mammal CSVs inside do02, do04 and do05.

### What was inside each ZIP

- `do02.zip`: `動物分布調査第2回_哺乳類.csv`, `動物分布調査第2回_昆虫類.csv`, `動物分布調査第2回_鳥類.csv`. Species in the mammal CSV (rows): {json.dumps(sv['do02']['species_in_csv_all'], ensure_ascii=False)}.
- `do04.zip`: `do04/` with the CSVs 両生類・は虫類, 哺乳類, 昆虫類（トンボ・チョウ・セミ・ガ・甲虫）, 淡水魚類, 貝類. The mammal CSV has {sv['do04']['gdal_features_in_layer']:,} rows and {len(sv['do04']['species_in_csv_all'])} species names, among them both bears.
- `do05.zip`: CSVs 両生類・爬虫類, 哺乳類, 昆虫類（トンボ・チョウ・セミ・ガ・甲虫）, 淡水魚魚類 (sic), 貝類. The mammal CSV has {sv['do05']['gdal_features_in_layer']:,} rows and {len(sv['do05']['species_in_csv_all'])} species names.
- `do06.zip`: `動物分布調査第6回_哺乳類.csv` only. Species (rows): {json.dumps(sv['do06']['species_in_csv_all'], ensure_ascii=False)}. The two bears are one label there.
- `yo4.zip`: `Bear.shp/.dbf/.shx/.prj/.qpj/.cpg` and `クマ類分布図shpファイルの説明.txt`. One layer, {y['gdal_features_in_layer']:,} polygons, no species field.
  The ZIP holds only bears (クマ類); カモシカ is in yo5, a different file.
- Full file lists with sha256 are in `raw/{DAY}/MANIFEST.json` (the raw files themselves are not republished, because they contain other species).

## Files

- `parquet/bear_mesh_long.parquet`: GeoParquet {V['geoparquet']['version']}, {n:,} rows. The `geometry` column is the polygon from the distributed file and exists for yo4 only (null elsewhere); CRS EPSG:6668 (JGD2011).
- `parquet/bear_mesh_cells_from_code.parquet`: GeoParquet, {n:,} rows, one per row of the long table (join on `survey_id` + `source_row`). Its polygon column `geometry_computed_from_mesh_code` is computed by yuiseki from `mesh_code`; it is not a shape distributed by the Ministry (see "Cells computed from the mesh code").
- `raw/{DAY}/MANIFEST.json`: url, bytes, sha256, fetch time (UTC), HTTP Last-Modified of every file fetched, including the ZIPs, the pages and PDFs that are not republished.
- `evidence/`: the terms of use, the Geoportal metadata and the PDL1.0 text as fetched, with plain-text extracts, and the quotes from the report.
- `docs/`: `bear_mesh_by_survey.png`, `verification.json`, `summary.json`.
- `scripts/`, `src/`: the code that fetched, built and verified this (`uv run python scripts/02_build.py` etc.).

## Columns

| column | meaning |
|---|---|
| `survey_id` | do02, do04, do05, do06, yo4 |
| `survey_label` | survey name and period as written above |
| `species` | the value of 種名 in the CSV (ツキノワグマ or ヒグマ; do06: `ツキノワグマ・ヒグマ`). yo4 has no species field: the label `クマ類（ヒグマ・ツキノワグマ）` is the name the Geoportal metadata gives that layer |
| `species_in_source` | false for yo4 (species label not in the file) |
| `mesh_code` | the mesh code as a string, as in the file (CSV: メッシュコード, ５ｋｍメッシュコード; yo4: 5kmMesh) |
| `source_file` | `<zip>:<member>` |
| `source_row` | 1-based data row (CSV) or feature number (yo4) in the original file |
| `地名`, `分類群`, `種コード`, `備考` | do02 columns, as in the CSV (`分類群` and `種コード` also in do04, do05) |
| `調査票番号`, `年月` | do04 and do05 columns. The CSV also has `調査者コード`; it is not published here (see below) |
| `確認調査` | do06 column |
| `Descriptio`, `H22_29`, `単年度`, `第6回で確`, `第6回のみ`, `両調査で確` | yo4 (Bear.dbf) fields. The DBF cuts field names at 10 bytes, so `Descriptio`, `第6回で確` and `両調査で確` are cut names; the full names are not given by the source (確認できていない) |
| `geometry` | yo4: the 5 km mesh polygon as in Bear.shp. CSV rows: null (the CSV files carry no geometry). Computed cells for all rows are in the other file |

All attribute columns are strings, as in the source; a column that the survey does not have is null.

### Cells computed from the mesh code

`parquet/bear_mesh_cells_from_code.parquet` columns: `survey_id`, `source_row`, `mesh_code` (the key: the same three values as in the long table, same order), `mesh_digits`, `cell_kind`, and the polygon `geometry_computed_from_mesh_code`.
These polygons were not distributed by the Ministry. They are computed from the code by yuiseki (`src/convert.py`: `cell_bounds`), so that every row has a cell. Rule, from the Biodiversity Center page <https://www.biodic.go.jp/kiso/col_mesh.html> (基準地域メッシュ, 標準地域メッシュ・システム, 昭48.7.12 行政管理庁告示第143号):
「第１次地域区画は、経度差１度、緯度差40分で区画された範囲を指す。第２次地域区画は第１次地域区画を縦横８等分したもので、第３次地域区画は第２次地域区画を縦横10等分したものである。」
「５倍地域メッシュ 経度差３分45秒、緯度差２分30秒」「第２次地域区画（２次メッシュ） 経度差７分30秒、緯度差５分」.
Code reading used: digits 1-2 latitude (value / 1.5 degrees), 3-4 longitude (100 + value), 5 and 6 the 2nd-order row and column. 6-digit codes (do02, do04, do05) become the 2nd-order cell (0.125 x 0.0833 degrees).
8-digit codes (do06, yo4) become the 5 km cell (0.0625 x 0.0417 degrees), taking the 7th and 8th digits (2 or 7) as the position of the 3rd-order cell at the centre of a 2x2 block (2 = south or west half, 7 = north or east half).
This 7th and 8th digit reading is not stated by the Ministry: it was found from the data and holds for all {y['polygon_bounds_equal_to_cell_computed_from_code']:,} yo4 polygons, and is assumed (not testable without polygons) for do06, which uses the same code shape.
Likewise the 6-digit reading as a 2nd-order mesh is an inference (see Mesh codes below).

Check against the distributed shapes (yo4): {V['cells_from_code']['yo4_computed_cell_equals_distributed_polygon (bounds within 2e-6 deg, area within 1e-7)'][0]:,} of {V['cells_from_code']['yo4_computed_cell_equals_distributed_polygon (bounds within 2e-6 deg, area within 1e-7)'][1]:,} computed cells equal the distributed polygons (bounds within 2e-6 degrees, area within 1e-7; the shapefile rounds coordinates to 6 decimals).
CRS: declared EPSG:6668 (JGD2011), the CRS of Bear.shp. The mesh grid is defined by latitude and longitude values; the geodetic datum that the older surveys (do02 to do05) used is not stated in the files (確認できていない), so for them 6668 is a labelling choice to match yo4, not a claim, and no datum conversion was done.
The cells are rectangles on the grid and say nothing about where in the cell a bear was recorded.

### Mesh codes

- `do06` and `yo4`: 8 digits. In every row the 7th and 8th digits are 2 or 7 ({sv['do06']['mesh_code_structure_problems'] or 'no row breaks this'} in do06, {sv['yo4']['mesh_code_structure_problems'] or 'no row breaks this'} in yo4),
  and for all {y['polygon_bounds_equal_to_cell_computed_from_code']:,} yo4 polygons the polygon equals the cell computed from the code: the 5 km mesh (経度差3分45秒、緯度差2分30秒, polygon {y['cell_sizes_deg_lon_lat'][0][0]} x {y['cell_sizes_deg_lon_lat'][0][1]} degrees)
  is named by the code of the 3rd-order mesh at its centre. The Biodiversity Center's own page (col_mesh.html) gives the 5倍地域メッシュ size and says it is 約5×5Km.
- `do02`, `do04`, `do05`: 6 digits, with the 5th and 6th digits in 0..7 in every row: this matches the code of the 2nd-order regional mesh (経度差7分30秒、緯度差5分, 約10km on the Biodiversity Center page), not a 5 km mesh.
  Two do02 rows were checked by hand against the place name (493235 高知県宿毛市, 493236 高知県中村市) and fall in the right 2nd-order cells.
  The Biodiversity Center's mammal page says the 第2回 results are shown in 5倍地域メッシュ; the delivered CSV has 6-digit codes. Why the codes are coarser than that page says: 確認できていない (the ZIPs contain no description).
  So `do02/do04/do05` rows are not on the same grid as `do06/yo4`.
- `年月` (do04, do05): 4 digits (`{sv['do04']['年月_min_max'][0]}` to `{sv['do04']['年月_min_max'][1]}` in do04; `{sv['do05']['年月_min_max'][0]}` to `{sv['do05']['年月_min_max'][1]}` in do05). The format is not documented in the ZIP; it looks like YYMM but the century is not given, so the values are kept as strings. 確認できていない.
- `調査者コード` (do04, do05; 7-digit code of the surveyor) was left out of the published Parquet. It is in the Ministry's publication and holds no name, but it was removed to avoid any chance of tying it to a person. The values remain in the local raw files (not republished). The other columns are unchanged.

## Attributes of the yo4 file (Bear.shp)

The ZIP's own note (`クマ類分布図shpファイルの説明.txt`, Shift_JIS), in full: 「file1：属性データとして「H22‐29」、「第6回」、「重複」、「単年度」」. It does not say more.
The values are 1 and 0 as strings. Counts by GDAL: {json.dumps(fr, ensure_ascii=False)}.
Combinations (H22_29, 第6回で確, 第6回のみ, 両調査で確, 単年度): {json.dumps(fc, ensure_ascii=False)}.

What the columns mean is read from the report's figure 3-1-3 legend (quoted in `evidence/report_h30_quotes.txt`) and from the counts. This is a reading, not a definition given by the Ministry for the field names:

| field | reading | evidence |
|---|---|---|
| `H22_29` = 1 | information obtained in this survey (本調査) | the report: 「平成22 (2010) 年度以降の情報を対象とし」; {fr['H22_29']['1']:,} meshes (the report text says 9,358 meshes, 3 more; why: 確認できていない) |
| `第6回で確` = 1 | confirmed in the 6th survey | {fr['第6回で確']['1']:,} meshes; the report says 6,735 for the 6th survey (do06 has {cx['do06_meshes']:,}, one mesh, `{cx['only_do06'][0]}`, is not in Bear.shp) |
| `両調査で確` = 1 | confirmed in both | legend 「第6回調査(2003年度)と本調査で...」; {fr['両調査で確']['1']:,} meshes |
| `第6回のみ` = 1 | confirmed in the 6th survey only | legend 「第6回調査(2003年度)のみで...」; {fr['第6回のみ']['1']:,} meshes. Added in March 2021 (see Correction). `第6回で確` = `第6回のみ` + `両調査で確` holds: {y['第6回で確 == 第6回のみ + 両調査で確'][0]} = {y['第6回で確 == 第6回のみ + 両調査で確'][1]} + {y['第6回で確 == 第6回のみ + 両調査で確'][2]} |
| `単年度` = 1 | possibly temporary: information in one year only | the report: 「単年度のみの情報が得られた(調査対象の2010-2017年の間で、目撃・痕跡・捕獲等の情報が1年度のみ得られた)メッシュ」; {fr['単年度']['1']:,} meshes |
| `Descriptio` | not described by the source: a 7-digit string; it equals the first 7 digits of `5kmMesh` in only 4,261 of the 17,068 rows. 確認できていない | |

Bear.shp holds all {y['rows']:,} meshes of the national frame, so the rows with every flag 0 ({fc['0,0,0,0,0']:,}) are meshes without information, not meshes with bears.
Meshes with at least one bear flag: {fr['H22_29']['1'] + fr['第6回のみ']['1']:,} (= H22_29 = 1 or 第6回のみ = 1). The shapefile does not separate the two species.
The Geoportal metadata of the same layer (2019 クマ類全国分布メッシュ) describes other fields (a 7-digit 5kmMesh and one 0/1 field `2015-2018`); the delivered Bear.shp does not match that description (8-digit codes, five flags). Which is current: 確認できていない.

## Survey methods and notes of the Ministry

From the Biodiversity Center page <https://www.biodic.go.jp/kiso/do_kiso4_mam_f.html> (哺乳類の分布調査):

- 第2回 (昭和53年度): 「各都道府県の鳥獣保護員、林務関係職員等(2,235名)による狩猟者など(44,853名)に対する聞きとり調査。」 Results: 「調査結果は、都道府県ごとに５万分の１地形図を16等分した区画( ５倍地域メッシュ 、約５㎞×５㎞メッシュ)によって示され」.
- 第4回 (平成元～3年度): 「調査は平成元年度から２年度に、哺乳類において鳥獣保護員の参加や(社)大日本猟友会の協力を求める等、調査体制の再検討及び体制整備を図った。次に平成３年度に専門家を中心とした調査員からの情報収集を実施、その後中間集計のうえ補足調査を実施した(調査員2,521名、調査対象種2,456種(対象種コードの数))。」
- 第5回 (平成9, 10年度): the page describes 種の多様性調査 (都道府県委託調査: 「47都道府県に調査を委託して文献、標本及び現地調査により分布情報を収集した。」) and (専門家調査): 「環境省から専門家に直接依頼して分布情報を収集し、第４回までの情報を補完した。」 Which of the two the do05 rows come from: 確認できていない.
- 第6回 (平成12～16年度): 「第２回調査との比較を行うため、中大型哺乳類８種の調査を実施した。各都道府県の鳥獣保護員、林務関係職員等による狩猟者などに対する聞き取り調査を実施した。」 Result: 「「ツキノワグマやサルについては、西中国などにおいて、分布域が孤立している地域がある」ことが確認された。」
- 要注意鳥獣(クマ等)生息分布調査 平成28～30年度 (<https://www.biodic.go.jp/youchui/youchui_top.html>): 「平成22年度以降の情報を対象とし、野生鳥獣情報システム（WIS）、国・都道府県による調査結果、研究機関・専門家による調査結果、市区町村へのアンケート等によって各種の生息に関する情報を収集し、５kmメッシュ単位で分布図を作成した。」

Not comparable (Ministry's words):

- The same page, on the 中大型哺乳類分布調査 (for タヌキ, キツネ, アナグマ, not the bears): 「今回の調査は様々な情報源から生息情報を収集するなど、第6回調査と調査手法が異なる部分があることから、過去の調査との単純比較には注意が必要である。」 This is the nearest statement on the Biodiversity Center page; it is about another set of species.
- The bear report (平成30年度中大型哺乳類分布調査 調査報告書, p.22): 「各種の分布状況の評価のための経時的な比較対象として、第6回調査結果を用いた。ただし、本調査とは調査手法、情報収集体制が異なるため、以下に留意点等を示した。」 and
  「第6回調査で収集された情報は、クマ類20,327件、カモシカ56,372件となり、都道府県においての情報集約・整理を経ているため、本調査の情報件数とは単純に比較は出来ない」.
- Same report (p.24, read by OCR): 「5kmメッシュで確認された地点は、恒常的な分布に限らず、一時的な目撃等に基づく情報も含まれていることに留意する必要がある。」 and 「奥山での情報が薄い可能性などがある」.
- Same report (p.22): 第2回調査 distinguished 「繁殖地域」 and 「出没区地域」 (sic) by wintering and cubs; the 第6回 and this survey did not keep that distinction. do02 `備考` has two values (見た {sv['do02']['frequency_of_備考']['見た']:,}, 聞いた {sv['do02']['frequency_of_備考']['聞いた']:,}); the source does not define them (確認できていない).
- do06 `確認調査` has two values: {json.dumps(sv['do06']['frequency_of_確認調査'], ensure_ascii=False)}. They compare the 6th with the 2nd survey; the source does not define the column further (確認できていない).
- Counts: the mesh sizes are not the same (2nd-order mesh for do02/do04/do05, 5 km for do06/yo4), do04/do05 rows are records (a mesh repeats: do04 {sv['do04']['per_species']['ツキノワグマ']['rows']:,} Asiatic black bear rows fall in {sv['do04']['per_species']['ツキノワグマ']['distinct_meshes']:,} meshes), and do06/yo4 do not separate the species.

## Counts (from `docs/verification.json`)

| survey | species | rows | distinct meshes |
|---|---|---|---|
""" + "\n".join(
    f"| {sid} | {sp} | {v['rows']:,} | {v['distinct_meshes']:,} |" for sid, i in sv.items() for sp, v in i["per_species"].items()
) + f"""

Total {n:,} rows. Read back three ways with the same result: GDAL (`ogrinfo` through `/vsizip/`), geopandas/pyarrow and DuckDB ({V['parquet_rows']:,} / {V['arrow_rows']:,} / {V['duckdb_rows']:,} rows);
mesh codes, species labels and every attribute column equal the GDAL reading row by row; mismatches: {len(V['mismatches'])}.
No mesh code is malformed, do06 and yo4 have no repeated code, and yo4 has {y['invalid_geometries']} invalid geometries.
do06 vs yo4: {cx['in_both']:,} meshes of do06 are `第6回で確` in yo4; only in do06: {cx['only_do06']}; only in yo4: {cx['only_yo4']}.

Example (DuckDB):

```sql
select survey_id, species, count(*) rows, count(distinct mesh_code) meshes
from read_parquet('parquet/bear_mesh_long.parquet') group by all order by 1, 2;

-- cells computed from the code, joined to the rows
select l.survey_id, l.species, l.mesh_code, c.geometry_computed_from_mesh_code
from read_parquet('parquet/bear_mesh_long.parquet') l
join read_parquet('parquet/bear_mesh_cells_from_code.parquet') c using (survey_id, source_row) limit 5;
```

## Correction of March 2021

The notice 訂正等のお知らせ (環境省生物多様性センター, 2021年3月; sha256 `{by['news_yo_210331.pdf']['sha256']}`, Last-Modified {by['news_yo_210331.pdf']['last_modified']}; the PDF is not republished) says:

- The public data of the 平成30年度中大型哺乳類分布調査業務 report (クマ類・カモシカ, March 2019) had a part in error. The correction concerns カモシカ: meshes 55383022, 58404072 and 60405072 were wrongly recorded as no information although information was obtained in this survey. This does not touch the bear rows here.
- Added for bears: 「クマ類のGISデータに「第6回（自然環境保全）調査のみで生息情報が得られたメッシュ」を追加しました。」 This is the `第6回のみ` field ({fr['第6回のみ']['1']} meshes in the delivered Bear.shp).
- The report page says 「一部訂正しました（2021年４月）」 while the download page and the notice say March 2021; the corrected report PDF has ModDate 2021-04-07 (`raw/{DAY}/pages/h30_chuogata_list.pdf` is the 正誤表, not republished).
- Within yo4.zip the note text file is dated 2021-03-26 and Bear.* 2019-09-12 (ZIP member timestamps).

## Dates of the files

HTTP Last-Modified of the ZIPs: {", ".join(f"{k.replace('.zip','')} {by[k]['last_modified']}" for k in ('yo4.zip','do02.zip','do04.zip','do05.zip','do06.zip'))}.
ZIP member timestamps: the do02, do05 and do06 CSVs 2026-05-21; the do04 mammal CSV 2026-07-16; Bear.* 2019-09-12. So the do02 to do06 CSV files were (re)made in 2026; what changed in them, if anything, is not stated (確認できていない).
The repository name carries no date because the surveys span 1978 to 2018 and the files carry different dates.

## License

Source terms (fetched {DAY}, copies in `evidence/`):

- 生物多様性センター ウェブサイト利用規約 (<https://www.biodic.go.jp/copyright/terms_of_service.html>, 令和７年３月11日 改正): 「…別紙で定める生物多様性センターが所管しているコンテンツの著作権は、特記されていない限り生物多様性センターに帰属し、権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）に準拠した利用条件の下で、利用することができます。」
  Credit: 「本コンテンツを利用する際は出典を記載してください。」 Processing: 「本コンテンツを編集・加工等して利用する場合は、上記出典とは別に、編集・加工等を行ったこと及びその主体を記載してください。なお、編集・加工した情報を、あたかも国(又は府省等)が作成した未加工のままであるかのような態様で公表・利用してはいけません。」
  Law: 「当ウェブサイトのコンテンツには、国土地理院の地図を使用しているものがあります。国土地理院の地図（基本測量の測量成果）は、測量法によって、複製頒布や一定の態様の二次利用について、国土地理院の長の承認が必要とされています。」 These files are mesh tables and polygons and use no GSI map as far as the files show; the Biodiversity Center's note about GSI maps is quoted for completeness.
- PDL1.0 (デジタル庁, <https://www.digital.go.jp/resources/open_data/public_data_license_v1.0>): 「本利用ルールは、クリエイティブ・コモンズ・ライセンスの表示4.0 国際ライセンスに規定される著作権利用許諾条件（以下「CC BY」といいます。）と互換性があります。」
- Environment Ministry Geoportal metadata of 「2019 クマ類全国分布メッシュ」 (<https://www.arcgis.com/sharing/rest/content/items/c9496d832e564920a49a4127d903977c/info/metadata/metadata.xml?format=default&output=html>):
  出典: 「環境省． 2019 ．平成 30 年度（ 2018 年度）中大型哺乳類分布調査 調査報告書」; License: 「-」; Terms of Use: 「ご利用にあたっては、生物多様性センターウェブサイト利用規約を必ず遵守するようにしてください。」「上記規約は、クリエイティブ・コモンズ・ライセンスの表示4.0国際と互換性があり、利用規約が適用されるコンテンツは CC BY に従うことでも利用することができます。」

Maintainer's note: by the terms above the data follow PDL1.0, which is stated to be compatible with CC BY 4.0. This card uses `license: other` and does not claim a Creative Commons license of its own.
The terms apply to the Biodiversity Center's content; the Parquet is a processed copy, and the credit and the processing notice at the top of this card must be kept.
The report titles of each survey (the 報告書 pages linked from <https://www.biodic.go.jp/kiso/do_kiso4_mam_f.html> and the youchui page) are in `data/provenance.yaml`.

## Known issues

- yo4 has no species field and do06 merges the two bears: only do02, do04 and do05 separate ツキノワグマ and ヒグマ. There is no Akita (or any prefecture) column; a prefecture needs a join with other data, which this dataset does not do.
- do02, do04 and do05 use 6-digit (2nd-order) codes; do06 and yo4 use 8-digit 5 km codes. They are different grids.
- The CSV rows have no distributed geometry (null in `bear_mesh_long.parquet`). `bear_mesh_cells_from_code.parquet` has cells computed from the code, not shapes of the Ministry; the 8-digit rule (7th and 8th digits 2 or 7) and the 6-digit 2nd-order reading are inferences (see above). The figure `docs/bear_mesh_by_survey.png` draws these computed cells.
- The surveyor code (`調査者コード`) of do04 and do05 is not published here, to avoid tying it to a person; it is in the Ministry's publication, holds no name, and remains in the local raw files.
- do04 and do05 rows are records, not unique meshes. `年月` values are unexplained (do05 has values such as `1009` although the survey years are 1997-98).
- The report says 9,358 meshes (this survey) and 6,735 (6th); Bear.shp has {fr['H22_29']['1']:,} and {cx['yo4_第6回で確_meshes']:,}; one 6th-survey mesh of do06 is not in Bear.shp. The cause is 確認できていない.
- The page for the youchui survey dates the correction April 2021, the notice and the download page March 2021.
- The 5 ZIPs and the unzipped files are kept locally under `raw/` (not republished because of the other species); their sha256 are in MANIFEST.json.
- The text of the report was read by OCR (the PDF text layer is garbled); only p.22 was checked by eye.
"""
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "README.md").write_text(card, encoding="utf-8")

(ROOT / "data" / "LICENSE").write_text(
    """The source data are content of the Biodiversity Center of the Ministry of the Environment of Japan (環境省 生物多様性センター).
Terms: https://www.biodic.go.jp/copyright/terms_of_service.html (最終改正 令和7年3月11日):
  権利表記の記載がない限り「公共データ利用規約（第1.0版）」（PDL1.0）に準拠した利用条件の下で、利用することができます。
PDL1.0: https://www.digital.go.jp/resources/open_data/public_data_license_v1.0
  本利用ルールは、クリエイティブ・コモンズ・ライセンスの表示4.0 国際ライセンスに規定される著作権利用許諾条件（CC BY）と互換性があります。

When you use this dataset:
 1. State the source: 出典：環境省生物多様性センター『自然環境保全基礎調査』『要注意鳥獣(クマ等)生息分布調査』を加工して作成 (https://www.biodic.go.jp/shapedata/download.html)
 2. State that it was edited or processed and by whom: processed into Parquet tables by yuiseki (rows selected, columns added, the surveyor-code column left out, values and distributed geometry unchanged; cells computed from the mesh codes are in a separate file and are not distributed shapes).
 3. Do not present the processed data as if the State (or the Ministry) had published it unprocessed.
 4. Some content may be restricted by other laws (the terms mention GSI maps under the Survey Act); these files use no GSI map as far as they show.

The original text of the terms, the Geoportal metadata and PDL1.0 as fetched is in evidence/. This file is a notice by the maintainer, not a license grant.
""",
    encoding="utf-8",
)

prov = ["source: 環境省生物多様性センター 自然環境保全基礎調査 動物分布調査(do02, do04, do05, do06), 要注意鳥獣(クマ等)生息分布調査(yo4)",
        "url: https://www.biodic.go.jp/shapedata/download.html",
        "terms: https://www.biodic.go.jp/copyright/terms_of_service.html",
        "license: 生物多様性センター ウェブサイト利用規約 (公共データ利用規約 第1.0版 PDL1.0 に準拠, CC BY 4.0 互換とされる)",
        f"fetched_at_utc: \"{M['fetched_at_utc']}\"",
        f"raw: raw/{DAY}/ (MANIFEST.json has url, bytes, sha256, Last-Modified; ZIPs not republished)",
        "credit: 出典：環境省生物多様性センター『自然環境保全基礎調査』『要注意鳥獣(クマ等)生息分布調査』を加工して作成",
        "surveys:"]
reports = {
    "do02": "動物分布調査報告書[哺乳類] 昭和55年 全国版 (https://www.biodic.go.jp/reports/2-5/ac000.html), 昭和56年 全国版その２",
    "do04": "動植物分布調査報告書 哺乳類 平成5年 (https://www.biodic.go.jp/reports/4-02/index.html)",
    "do05": "動物分布調査報告書 哺乳類 平成14年 (https://www.biodic.go.jp/reports2/5th/ap_mam/index.html)",
    "do06": "哺乳類分布調査報告書 平成16年 (https://www.biodic.go.jp/reports2/6th/6_mammal/index.html)",
    "yo4": "平成30年度（2018年度）中大型哺乳類分布調査 調査報告書 クマ類（ヒグマ・ツキノワグマ）・カモシカ (環境省 2019, 一部訂正 2021) https://www.biodic.go.jp/youchui/reports/h30_chuogata_houkoku_teisei.pdf",
}
for sid in ("do02", "do04", "do05", "do06", "yo4"):
    z = by[f"{sid}.zip"]
    prov += [f"  - id: {sid}", f"    report: \"{reports[sid]}\"", f"    zip_sha256: {z['sha256']}", f"    zip_last_modified: \"{z['last_modified']}\"",
             f"    rows_in_table: {sum(v['rows'] for v in sv[sid]['per_species'].values())}"]
n_ = by["news_yo_210331.pdf"]
prov += [f"correction_notice: {{url: {n_['url']}, sha256: {n_['sha256']}, last_modified: \"{n_['last_modified']}\", republished: false}}",
         f"rows: {n}", "crs: EPSG:6668 (JGD2011), as in Bear.prj; no reprojection; CSV rows have null geometry",
         "processing: selected the bear rows, added survey_id/survey_label/species/species_in_source/mesh_code/source_file/source_row, kept all source attributes unchanged as strings except that the surveyor-code column (調査者コード of do04/do05) is not published; no correction, repair, reprojection, filling or merging. A second file, bear_mesh_cells_from_code.parquet, has cells computed by yuiseki from mesh_code (geometry_computed_from_mesh_code), not distributed shapes",
        f"cells_from_code_check: yo4 computed cell equals distributed polygon in {V['cells_from_code']['yo4_computed_cell_equals_distributed_polygon (bounds within 2e-6 deg, area within 1e-7)'][0]} of {V['cells_from_code']['yo4_computed_cell_equals_distributed_polygon (bounds within 2e-6 deg, area within 1e-7)'][1]}"]
(ROOT / "data" / "provenance.yaml").write_text("\n".join(prov) + "\n", encoding="utf-8")
print(len(card))
