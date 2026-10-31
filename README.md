# env-biodic-bear-distribution-mesh-jp

Scripts that fetch the bear (ツキノワグマ, ヒグマ) mesh distribution data of the Ministry of the Environment's Biodiversity Center
(自然環境保全基礎調査 動物分布調査 第2, 4, 5, 6回 and 要注意鳥獣(クマ等)生息分布調査), build one table from them, verify it through
three routes (GDAL, geopandas, DuckDB), and publish it.

The data and its card are on Hugging Face: <https://huggingface.co/datasets/yuiseki/env-biodic-bear-distribution-mesh-jp>
(published at revision `7f635cbfb92be5093fa707dbe6afec0e37d240f4`; `docs/revision.json`). Source:
<https://www.biodic.go.jp/shapedata/download.html>.

These are records of where bears were reported, found or caught, aggregated to meshes: not evidence of absence. Read the card.

- `src/fetch.py`: fetch (one request at a time), `scripts/02_build.py`, `03_verify.py`, `04_figure.py`, `05_card.py`: table, cross-check, figure, card.
- `src/publish.py`, `scripts/06_verify_hub.py`: the publication and the read-back from the Hub.

The code is offered as is; the data is under the terms of the Biodiversity Center (PDL1.0), see the card.
