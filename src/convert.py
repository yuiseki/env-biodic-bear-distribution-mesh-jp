"""Read the bear rows out of the Biodiversity Center ZIPs, as they are, into one long table.

Nothing is corrected: values stay the original strings (mesh codes with their digits), field names stay as in the files.
The CSV files carry no geometry, so their rows have a null geometry. yo4 (Bear.shp) carries the 5 km mesh polygons (JGD2011).
"""

from __future__ import annotations

import csv
import io
import zipfile
from dataclasses import dataclass
from pathlib import Path

BEARS = ("ツキノワグマ", "ヒグマ")
COMBINED = "ツキノワグマ・ヒグマ"  # do06's own species label
CLASS = "クマ類（ヒグマ・ツキノワグマ）"  # yo4 has no species field; the Geoportal metadata calls the layer this

# attributes of the source files, in the order they appear in the long table
ATTR_COLUMNS = [
    "地名", "分類群", "種コード", "備考",  # do02
    "調査票番号", "調査者コード", "年月",  # do04, do05 (分類群 and 種コード are shared with do02)
    "確認調査",  # do06
    "Descriptio", "H22_29", "単年度", "第6回で確", "第6回のみ", "両調査で確",  # yo4 (DBF names are cut at 10 bytes)
]  # fmt: skip


@dataclass(frozen=True)
class Survey:
    survey_id: str
    survey_label: str
    zip_name: str
    member_suffix: str
    mesh_field: str
    species_field: str | None


SURVEYS = [
    Survey("do02", "第2回自然環境保全基礎調査 動物分布調査 (昭和53年度)", "do02.zip", "動物分布調査第2回_哺乳類.csv", "メッシュコード", "種名"),
    Survey("do04", "第4回自然環境保全基礎調査 動物分布調査 (平成元～3年度)", "do04.zip", "動物分布調査第4回_哺乳類.csv", "メッシュコード", "種名"),
    Survey("do05", "第5回自然環境保全基礎調査 動物分布調査 (平成9, 10年度; 種の多様性調査 第1期)", "do05.zip", "動物分布調査第5回_哺乳類.csv", "メッシュコード", "種名"),
    Survey("do06", "第6回自然環境保全基礎調査 動物分布調査 (平成12～16年度; 種の多様性調査 第2期)", "do06.zip", "動物分布調査第6回_哺乳類.csv", "５ｋｍメッシュコード", "種名"),
    Survey("yo4", "要注意鳥獣(クマ等)生息分布調査 平成28～30年度 (平成30年度中大型哺乳類分布調査 クマ類)", "yo4.zip", "Bear.shp", "5kmMesh", None),
]  # fmt: skip


def zip_members(z: zipfile.ZipFile) -> dict[str, zipfile.ZipInfo]:
    """member name as a person would read it (cp932 names that the ZIP did not flag as UTF-8 are decoded) -> ZipInfo."""
    out = {}
    for zi in z.infolist():
        name = zi.filename
        if not zi.flag_bits & 0x800:
            try:
                name = name.encode("cp437").decode("cp932")
            except UnicodeError:
                pass
        out[name] = zi
    return out


def read_csv_rows(zip_path: Path, member_suffix: str) -> tuple[str, list[dict[str, str]]]:
    with zipfile.ZipFile(zip_path) as z:
        members = zip_members(z)
        hits = [n for n in members if n.endswith(member_suffix)]
        if len(hits) != 1:
            raise SystemExit(f"{zip_path.name}: expected one member ending with {member_suffix}, got {hits}")
        raw = z.read(members[hits[0]])
    text = raw.decode("cp932")  # strict: a wrong guess fails loudly
    rows = list(csv.DictReader(io.StringIO(text, newline="")))
    return hits[0], rows


def long_rows(survey: Survey, zip_path: Path) -> list[dict]:
    """The bear rows of one CSV survey, in file order. source_row is the 1-based data row number in the CSV."""
    member, rows = read_csv_rows(zip_path, survey.member_suffix)
    out = []
    for i, r in enumerate(rows, start=1):
        sp = r[survey.species_field]
        if sp not in BEARS and sp != COMBINED:
            continue
        rec = {
            "survey_id": survey.survey_id, "survey_label": survey.survey_label, "species": sp, "species_in_source": True,
            "mesh_code": r[survey.mesh_field], "source_file": f"{survey.zip_name}:{member}", "source_row": i,
        }  # fmt: skip
        for c in ATTR_COLUMNS:
            rec[c] = r.get(c)
        out.append(rec)
    return out


def mesh_problems(code: str) -> list[str]:
    """Structure checks of a Japanese regional mesh code. 6 digits = 2nd-order mesh; 8 digits = the 5 km mesh as it is coded in do06/yo4
    (3rd-order code of the cell at the centre of the 2x2 block: the last two digits are each 2 or 7)."""
    bad = []
    if not code.isascii() or not code.isdigit():
        return ["not digits"]
    if len(code) not in (6, 8):
        return [f"length {len(code)}"]
    if not 30 <= int(code[:2]) <= 68:
        bad.append("latitude part")
    if not 22 <= int(code[2:4]) <= 54:
        bad.append("longitude part")
    if code[4] not in "01234567" or code[5] not in "01234567":
        bad.append("2nd-order digits")
    if len(code) == 8 and (code[6] not in "27" or code[7] not in "27"):
        bad.append("5 km digits")
    return bad


def cell_bounds(code: str) -> tuple[float, float, float, float]:
    """(west, south, east, north) of a mesh code, from the JIS X 0410 rule. Used only for the figure; never written to the data."""
    lat = int(code[:2]) / 1.5 + int(code[4]) * 5 / 60
    lon = 100 + int(code[2:4]) + int(code[5]) * 7.5 / 60
    if len(code) == 6:
        return lon, lat, lon + 7.5 / 60, lat + 5 / 60
    lat += (0 if code[6] == "2" else 5) * 30 / 3600
    lon += (0 if code[7] == "2" else 5) * 45 / 3600
    return lon, lat, lon + 3.75 / 60, lat + 2.5 / 60
