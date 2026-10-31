#!/usr/bin/env python3
"""Push the card, licence, provenance, Parquet, MANIFEST, evidence, scripts and docs.

uv run python src/publish.py             # dry run: list the files and their sizes (the default; nothing is sent)
uv run python src/publish.py --push      # one commit; prints the sha and writes docs/revision.json (NOT to be run without the person's approval)

The raw ZIPs, the unzipped files and the fetched PDFs/pages stay local: the ZIPs hold other species, and the notice PDF is not republished.
Only raw/<date>/MANIFEST.json (url, bytes, sha256, Last-Modified) goes up.
"""

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPO = "yuiseki/env-biodic-bear-distribution-mesh-jp-2021-03"
ALLOWED_SPECIES = {"ツキノワグマ", "ヒグマ", "ツキノワグマ・ヒグマ", "クマ類（ヒグマ・ツキノワグマ）"}


def collect() -> dict[str, Path]:
    """path in the repo -> local file. The card is the repo's README.md."""
    card = (DATA / "README.md").read_text(encoding="utf-8")
    if "license: other" not in card or "license_name:" not in card:
        raise SystemExit("the card does not declare license: other with a license_name")
    summ = json.loads((ROOT / "docs" / "summary.json").read_text())
    ver = json.loads((ROOT / "docs" / "verification.json").read_text())
    if ver["mismatches"]:
        raise SystemExit(f"verification has mismatches: {ver['mismatches']}")
    if "出典：環境省生物多様性センター" not in card or "加工して作成" not in card:
        raise SystemExit("the card lacks the credit or the processing notice")
    files: dict[str, Path] = {"README.md": DATA / "README.md", "LICENSE": DATA / "LICENSE", "provenance.yaml": DATA / "provenance.yaml"}  # fmt: skip
    pqs = sorted((DATA / "parquet").glob("*.parquet"))
    n = summ["rows"]
    if len(pqs) != 1 or f"{n:,} rows" not in card:
        raise SystemExit("the card does not state the row count, or there is not exactly one Parquet")
    species = set(pq.read_table(pqs[0], columns=["species"]).column("species").to_pylist())
    if not species <= ALLOWED_SPECIES:
        raise SystemExit(f"species other than the bears in the Parquet: {species - ALLOWED_SPECIES}")
    files[f"parquet/{pqs[0].name}"] = pqs[0]
    man = ROOT / summ["raw"] / "MANIFEST.json"
    if not man.is_file():
        raise SystemExit("missing MANIFEST.json")
    files[man.relative_to(ROOT).as_posix()] = man
    for sub in ("evidence", "docs"):
        for p in sorted((ROOT / sub).glob("*")):
            if p.is_file() and p.name != "revision.json":
                files[f"{sub}/{p.name}"] = p
    for sub in ("scripts", "src"):
        for p in sorted((ROOT / sub).glob("*.py")):
            files[f"{sub}/{p.name}"] = p
    bad = [k for k in files if k.startswith("raw/") and not k.endswith("MANIFEST.json")]
    if bad or any(k.endswith((".zip", ".shp", ".dbf")) for k in files):
        raise SystemExit(f"raw files must not be published: {bad}")
    return files


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true", help="upload; needs the person's approval")
    a = ap.parse_args()
    files = collect()
    total = sum(p.stat().st_size for p in files.values())
    print(f"{a.repo}\n  {len(files)} files, {total:,} bytes")
    for k, v in files.items():
        print(f"  {v.stat().st_size:>12,}  {k}")
    if not a.push:
        print("\ndry run. pass --push to upload")
        return 0
    from huggingface_hub import CommitOperationAdd, HfApi

    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True, private=False)
    ops = [CommitOperationAdd(path_in_repo=k, path_or_fileobj=str(v)) for k, v in files.items()]
    c = api.create_commit(a.repo, ops, repo_type="dataset", commit_message="Add bear 5 km mesh distribution of the Biodiversity Center (do02, do04, do05, do06, yo4)")
    rev = {"repo": a.repo, "revision": c.oid, "pushed": datetime.now(UTC).isoformat(timespec="seconds"),
           "sha256": {k: sha256(v) for k, v in files.items()}}  # fmt: skip
    (ROOT / "docs" / "revision.json").write_text(json.dumps(rev, indent=1) + "\n")
    print(f"pushed {a.repo} revision {c.oid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
