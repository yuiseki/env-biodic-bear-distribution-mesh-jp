import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from convert import BEARS, cell_bounds, mesh_problems

ROOT = Path(__file__).resolve().parent.parent
PQ = ROOT / "data" / "parquet" / "bear_mesh_long.parquet"


def test_mesh_problems():
    assert mesh_problems("30365027") == []
    assert mesh_problems("493235") == []
    assert mesh_problems("3036502") == ["length 7"]
    assert "5 km digits" in mesh_problems("30365033")
    assert "2nd-order digits" in mesh_problems("493285")
    assert mesh_problems("49323a") == ["not digits"]


def test_cell_bounds_known_cells():
    w, s, e, n = cell_bounds("30365027")  # polygon seen in Bear.shp: 136.0625 20.416667 .. 136.125 20.458334
    assert (round(w, 4), round(s, 5), round(e, 4), round(n, 5)) == (136.0625, 20.41667, 136.125, 20.45833)
    w, s, e, n = cell_bounds("46304577")
    assert (round(w, 4), round(s, 5)) == (130.6875, 31.04167)
    w, s, e, n = cell_bounds("493235")  # 2nd-order mesh
    assert round(e - w, 5) == 0.125 and round(n - s, 5) == round(5 / 60, 5)


@pytest.mark.skipif(not PQ.exists(), reason="run scripts/02_build.py first")
def test_parquet_only_bears_and_counts():
    t = pq.read_table(PQ)
    assert set(t.column("species").to_pylist()) <= {*BEARS, "ツキノワグマ・ヒグマ", "クマ類（ヒグマ・ツキノワグマ）"}
    assert t.num_rows == json.loads((ROOT / "docs" / "summary.json").read_text())["rows"]
    assert b"geo" in t.schema.metadata
    assert all(isinstance(x, str) and x.isdigit() for x in t.column("mesh_code").to_pylist())
