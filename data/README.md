---
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
---

# env-biodic-bear-distribution-mesh-jp-2021-03

The bear (ツキノワグマ, ヒグマ) distribution mesh files that the Biodiversity Center of the Ministry of the Environment of Japan
(環境省 生物多様性センター) publishes for five surveys, put into one long table of 28,194 rows, with the values left as they are in the files.
Only the bear rows are kept; the ZIPs hold other species too (listed below), and those are not republished.

Credit. 出典：環境省生物多様性センター『自然環境保全基礎調査』『要注意鳥獣(クマ等)生息分布調査』を加工して作成
(<https://www.biodic.go.jp/shapedata/download.html>, データダウンロード日 2026-10-31).
Processed. Rows were picked out of the original files and put in one Parquet table by yuiseki: nothing was corrected, re-projected, filled in or merged.
This is not a publication of the Ministry, and nothing here is to be shown as if the Ministry had made it.

## What this is, and what it is not

- It is a mesh tally of records of bears being there (sightings, signs, captures, answers to questionnaires and interviews, depending on the survey).
  A mesh without a row, or a yo4 mesh with all flags 0, is not evidence that bears are absent: it only means no information was collected or kept.
- The surveys used different methods, periods, sources and mesh sizes, so the counts of one survey are not directly comparable with another.
  The Ministry says so itself (quotes below). Do not read a change of counts between surveys as a change of the bears.
- Reports of the Ministry state that the 5 km mesh includes "一時的な目撃等" and that information from the deep mountains may be thin (quotes below).

## Sources

All from <https://www.biodic.go.jp/shapedata/download.html> (page saved in the raw copy, read 2026-10-31; fetch started 2026-10-31T10:22:45+00:00).
Fetched with plain `curl`, one file at a time, 2 seconds apart, User-Agent `Mozilla/5.0 (research; yuiseki)` (`src/fetch.py`). No request was refused. Only www.biodic.go.jp, www.arcgis.com and www.digital.go.jp were asked.

| id | survey | period (as the Biodiversity Center page gives it) | mesh | bear rows in this table | ZIP |
|---|---|---|---|---|---|
| `do02` | 自然環境保全基礎調査 第2回 動物分布調査 (哺乳類) | 昭和53年度 | 6-digit code, see "Mesh codes" | ツキノワグマ: 1,298 rows / 1,298 meshes; ヒグマ: 742 rows / 742 meshes | `do02.zip` 2,993,179 B, Last-Modified Thu, 21 May 2026 01:25:51 GMT |
| `do04` | 第4回 動物分布調査 (哺乳類) | 平成元～3年度 | 6-digit code | ツキノワグマ: 1,338 rows / 912 meshes; ヒグマ: 428 rows / 340 meshes | `do04.zip` 2,088,351 B, Last-Modified Mon, 27 Jul 2026 05:17:53 GMT |
| `do05` | 第5回 動物分布調査 (哺乳類) = 生物多様性調査 種の多様性調査 第1期 | 平成9, 10年度 | 6-digit code | ツキノワグマ: 464 rows / 252 meshes; ヒグマ: 121 rows / 85 meshes | `do05.zip` 2,364,009 B, Last-Modified Thu, 21 May 2026 01:27:03 GMT |
| `do06` | 第6回 動物分布調査 (哺乳類) = 種の多様性調査 第2期 | 平成12～16年度 | 8-digit 5 km mesh code | ツキノワグマ・ヒグマ: 6,735 rows / 6,735 meshes | `do06.zip` 182,327 B, Last-Modified Thu, 21 May 2026 01:27:22 GMT |
| `yo4` | 要注意鳥獣(クマ等)生息分布調査 平成28～30年度 (平成30年度中大型哺乳類分布調査) ヒグマ、ツキノワグマ | 情報は平成22年度以降 | 8-digit 5 km mesh code + polygon | クマ類（ヒグマ・ツキノワグマ）: 17,068 rows / 17,068 meshes | `yo4.zip` 698,539 B, Last-Modified Sun, 10 May 2026 23:31:04 GMT |

Not taken: do03 (birds only), yo1 (アライグマ), yo5 (カモシカ), and the non-mammal CSVs inside do02, do04 and do05.

### What was inside each ZIP

- `do02.zip`: `動物分布調査第2回_哺乳類.csv`, `動物分布調査第2回_昆虫類.csv`, `動物分布調査第2回_鳥類.csv`. Species in the mammal CSV (rows): {"ニホンザル": 1766, "シカ": 1736, "ツキノワグマ": 1298, "ヒグマ": 742, "イノシシ": 1617, "キツネ": 3348, "タヌキ": 3396, "アナグマ": 2396}.
- `do04.zip`: `do04/` with the CSVs 両生類・は虫類, 哺乳類, 昆虫類（トンボ・チョウ・セミ・ガ・甲虫）, 淡水魚類, 貝類. The mammal CSV has 43,995 rows and 112 species names, among them both bears.
- `do05.zip`: CSVs 両生類・爬虫類, 哺乳類, 昆虫類（トンボ・チョウ・セミ・ガ・甲虫）, 淡水魚魚類 (sic), 貝類. The mammal CSV has 24,819 rows and 108 species names.
- `do06.zip`: `動物分布調査第6回_哺乳類.csv` only. Species (rows): {"アナグマ": 5062, "イノシシ": 6693, "カモシカ": 5010, "キツネ": 11668, "ツキノワグマ・ヒグマ": 6735, "ニホンザル": 3471, "ニホンジカ": 7344, "タヌキ": 11476, "マングース": 87}. The two bears are one label there.
- `yo4.zip`: `Bear.shp/.dbf/.shx/.prj/.qpj/.cpg` and `クマ類分布図shpファイルの説明.txt`. One layer, 17,068 polygons, no species field.
  The ZIP holds only bears (クマ類); カモシカ is in yo5, a different file.
- Full file lists with sha256 are in `raw/2026-10-31/MANIFEST.json` (the raw files themselves are not republished, because they contain other species).

## Files

- `parquet/bear_mesh_long.parquet`: GeoParquet 1.1.0, 28,194 rows. CRS of the geometry: EPSG:6668 (JGD2011).
- `raw/2026-10-31/MANIFEST.json`: url, bytes, sha256, fetch time (UTC), HTTP Last-Modified of every file fetched, including the ZIPs, the pages and PDFs that are not republished.
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
| `調査票番号`, `調査者コード`, `年月` | do04 and do05 columns |
| `確認調査` | do06 column |
| `Descriptio`, `H22_29`, `単年度`, `第6回で確`, `第6回のみ`, `両調査で確` | yo4 (Bear.dbf) fields. The DBF cuts field names at 10 bytes, so `Descriptio`, `第6回で確` and `両調査で確` are cut names; the full names are not given by the source (確認できていない) |
| `geometry` | yo4: the 5 km mesh polygon as in Bear.shp. CSV rows: null (the CSV files carry no geometry) |

All attribute columns are strings, as in the source; a column that the survey does not have is null.

### Mesh codes

- `do06` and `yo4`: 8 digits. In every row the 7th and 8th digits are 2 or 7 (no row breaks this in do06, no row breaks this in yo4),
  and for all 17,068 yo4 polygons the polygon equals the cell computed from the code: the 5 km mesh (経度差3分45秒、緯度差2分30秒, polygon 0.0625 x 0.04167 degrees)
  is named by the code of the 3rd-order mesh at its centre. The Biodiversity Center's own page (col_mesh.html) gives the 5倍地域メッシュ size and says it is 約5×5Km.
- `do02`, `do04`, `do05`: 6 digits, with the 5th and 6th digits in 0..7 in every row: this matches the code of the 2nd-order regional mesh (経度差7分30秒、緯度差5分, 約10km on the Biodiversity Center page), not a 5 km mesh.
  Two do02 rows were checked by hand against the place name (493235 高知県宿毛市, 493236 高知県中村市) and fall in the right 2nd-order cells.
  The Biodiversity Center's mammal page says the 第2回 results are shown in 5倍地域メッシュ; the delivered CSV has 6-digit codes. Why the codes are coarser than that page says: 確認できていない (the ZIPs contain no description).
  So `do02/do04/do05` rows are not on the same grid as `do06/yo4`.
- `年月` (do04, do05): 4 digits (`0208` to `9201` in do04; `1009` to `9812` in do05). The format is not documented in the ZIP; it looks like YYMM but the century is not given, so the values are kept as strings. 確認できていない.
- `調査者コード` (do04, do05) is a 7-digit code of the surveyor in the original files (222 distinct codes in do04, 218 in do05); no names. It is kept as published by the Biodiversity Center.

## Attributes of the yo4 file (Bear.shp)

The ZIP's own note (`クマ類分布図shpファイルの説明.txt`, Shift_JIS), in full: 「file1：属性データとして「H22‐29」、「第6回」、「重複」、「単年度」」. It does not say more.
The values are 1 and 0 as strings. Counts by GDAL: {"H22_29": {"0": 7713, "1": 9355}, "単年度": {"0": 16245, "1": 823}, "第6回で確": {"0": 10334, "1": 6734}, "第6回のみ": {"0": 16996, "1": 72}, "両調査で確": {"0": 10406, "1": 6662}}.
Combinations (H22_29, 第6回で確, 第6回のみ, 両調査で確, 単年度): {"0,0,0,0,0": 7641, "0,1,1,0,0": 72, "1,0,0,0,0": 1873, "1,0,0,0,1": 820, "1,1,0,1,0": 6659, "1,1,0,1,1": 3}.

What the columns mean is read from the report's figure 3-1-3 legend (quoted in `evidence/report_h30_quotes.txt`) and from the counts. This is a reading, not a definition given by the Ministry for the field names:

| field | reading | evidence |
|---|---|---|
| `H22_29` = 1 | information obtained in this survey (本調査) | the report: 「平成22 (2010) 年度以降の情報を対象とし」; 9,355 meshes (the report text says 9,358 meshes, 3 more; why: 確認できていない) |
| `第6回で確` = 1 | confirmed in the 6th survey | 6,734 meshes; the report says 6,735 for the 6th survey (do06 has 6,735, one mesh, `64430527`, is not in Bear.shp) |
| `両調査で確` = 1 | confirmed in both | legend 「第6回調査(2003年度)と本調査で...」; 6,662 meshes |
| `第6回のみ` = 1 | confirmed in the 6th survey only | legend 「第6回調査(2003年度)のみで...」; 72 meshes. Added in March 2021 (see Correction). `第6回で確` = `第6回のみ` + `両調査で確` holds: 6734 = 72 + 6662 |
| `単年度` = 1 | possibly temporary: information in one year only | the report: 「単年度のみの情報が得られた(調査対象の2010-2017年の間で、目撃・痕跡・捕獲等の情報が1年度のみ得られた)メッシュ」; 823 meshes |
| `Descriptio` | not described by the source: a 7-digit string; it equals the first 7 digits of `5kmMesh` in only 4,261 of the 17,068 rows. 確認できていない | |

Bear.shp holds all 17,068 meshes of the national frame, so the rows with every flag 0 (7,641) are meshes without information, not meshes with bears.
Meshes with at least one bear flag: 9,427 (= H22_29 = 1 or 第6回のみ = 1). The shapefile does not separate the two species.
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
- Same report (p.22): 第2回調査 distinguished 「繁殖地域」 and 「出没区地域」 (sic) by wintering and cubs; the 第6回 and this survey did not keep that distinction. do02 `備考` has two values (見た 1,921, 聞いた 119); the source does not define them (確認できていない).
- do06 `確認調査` has two values: {"第2回と第6回で確認": 4808, "第6回のみ確認": 1927}. They compare the 6th with the 2nd survey; the source does not define the column further (確認できていない).
- Counts: the mesh sizes are not the same (2nd-order mesh for do02/do04/do05, 5 km for do06/yo4), do04/do05 rows are records (a mesh repeats: do04 1,338 Asiatic black bear rows fall in 912 meshes), and do06/yo4 do not separate the species.

## Counts (from `docs/verification.json`)

| survey | species | rows | distinct meshes |
|---|---|---|---|
| do02 | ツキノワグマ | 1,298 | 1,298 |
| do02 | ヒグマ | 742 | 742 |
| do04 | ツキノワグマ | 1,338 | 912 |
| do04 | ヒグマ | 428 | 340 |
| do05 | ツキノワグマ | 464 | 252 |
| do05 | ヒグマ | 121 | 85 |
| do06 | ツキノワグマ・ヒグマ | 6,735 | 6,735 |
| yo4 | クマ類（ヒグマ・ツキノワグマ） | 17,068 | 17,068 |

Total 28,194 rows. Read back three ways with the same result: GDAL (`ogrinfo` through `/vsizip/`), geopandas/pyarrow and DuckDB (28,194 / 28,194 / 28,194 rows);
mesh codes, species labels and every attribute column equal the GDAL reading row by row; mismatches: 0.
No mesh code is malformed, do06 and yo4 have no repeated code, and yo4 has 0 invalid geometries.
do06 vs yo4: 6,734 meshes of do06 are `第6回で確` in yo4; only in do06: ['64430527']; only in yo4: [].

Example (DuckDB):

```sql
select survey_id, species, count(*) rows, count(distinct mesh_code) meshes
from read_parquet('parquet/bear_mesh_long.parquet') group by all order by 1, 2;
```

## Correction of March 2021

The notice 訂正等のお知らせ (環境省生物多様性センター, 2021年3月; sha256 `d1b04ddde5a9aeffd78b8d95cfb5920de0ec1d3a4e8070d6a1cdb0e5df333d0b`, Last-Modified Wed, 31 Mar 2021 09:11:11 GMT; the PDF is not republished) says:

- The public data of the 平成30年度中大型哺乳類分布調査業務 report (クマ類・カモシカ, March 2019) had a part in error. The correction concerns カモシカ: meshes 55383022, 58404072 and 60405072 were wrongly recorded as no information although information was obtained in this survey. This does not touch the bear rows here.
- Added for bears: 「クマ類のGISデータに「第6回（自然環境保全）調査のみで生息情報が得られたメッシュ」を追加しました。」 This is the `第6回のみ` field (72 meshes in the delivered Bear.shp).
- The report page says 「一部訂正しました（2021年４月）」 while the download page and the notice say March 2021; the corrected report PDF has ModDate 2021-04-07 (`raw/2026-10-31/pages/h30_chuogata_list.pdf` is the 正誤表, not republished).
- Within yo4.zip the note text file is dated 2021-03-26 and Bear.* 2019-09-12 (ZIP member timestamps).

## Dates of the files

HTTP Last-Modified of the ZIPs: yo4 Sun, 10 May 2026 23:31:04 GMT, do02 Thu, 21 May 2026 01:25:51 GMT, do04 Mon, 27 Jul 2026 05:17:53 GMT, do05 Thu, 21 May 2026 01:27:03 GMT, do06 Thu, 21 May 2026 01:27:22 GMT.
ZIP member timestamps: the do02, do05 and do06 CSVs 2026-05-21; the do04 mammal CSV 2026-07-16; Bear.* 2019-09-12. So the do02 to do06 CSV files were (re)made in 2026; what changed in them, if anything, is not stated (確認できていない).
The repository name carries 2021-03 (the date of the yo4 correction) by the maintainer's first plan; by these timestamps 2026-07 may be the right month.

## License

Source terms (fetched 2026-10-31, copies in `evidence/`):

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
- The CSV rows have no geometry. The figure `docs/bear_mesh_by_survey.png` draws cells computed from the code (JIS X 0410) for the picture only.
- do04 and do05 rows are records, not unique meshes. `年月` values are unexplained (do05 has values such as `1009` although the survey years are 1997-98).
- The report says 9,358 meshes (this survey) and 6,735 (6th); Bear.shp has 9,355 and 6,734; one 6th-survey mesh of do06 is not in Bear.shp. The cause is 確認できていない.
- The page for the youchui survey dates the correction April 2021, the notice and the download page March 2021.
- The 5 ZIPs and the unzipped files are kept locally under `raw/` (not republished because of the other species); their sha256 are in MANIFEST.json.
- The text of the report was read by OCR (the PDF text layer is garbled); only p.22 was checked by eye.
