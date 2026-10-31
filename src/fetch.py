#!/usr/bin/env python3
"""Fetch the source files one at a time, 2 seconds apart, with plain curl. Stops at the first 403/429/other refusal.

uv run python src/fetch.py [YYYY-MM-DD]     # raw/<date>/ ; writes raw/<date>/MANIFEST.json
The listing page raw/<date>/pages/download.html is fetched by hand before this (it is also recorded here if present).
"""

import hashlib
import json
import subprocess
import sys
import time
import zipfile
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "Mozilla/5.0 (research; yuiseki)"
B = "https://www.biodic.go.jp"
ITEMS = [  # (kind, url, relative path)
    ("page", f"{B}/shapedata/download.html", "pages/download.html"),
    ("zip", f"{B}/shapedata/yo4.zip", "zips/yo4.zip"),
    ("zip", f"{B}/shapedata/do/do02.zip", "zips/do02.zip"),
    ("zip", f"{B}/shapedata/do/do04.zip", "zips/do04.zip"),
    ("zip", f"{B}/shapedata/do/do05.zip", "zips/do05.zip"),
    ("zip", f"{B}/shapedata/do/do06.zip", "zips/do06.zip"),
    ("notice", f"{B}/shapedata/files/news_yo_210331.pdf", "pages/news_yo_210331.pdf"),
    ("page", f"{B}/kiso/history_f.html", "pages/history_f.html"),
    ("terms", f"{B}/copyright/terms_of_service.html", "pages/terms_of_service.html"),
    ("terms", "https://www.arcgis.com/sharing/rest/content/items/c9496d832e564920a49a4127d903977c/info/metadata/metadata.xml?format=default&output=html", "pages/geoportal_2019_bear_mesh_metadata.html"),
    ("terms", "https://www.digital.go.jp/resources/open_data/public_data_license_v1.0", "pages/pdl_1.0.html"),
]


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def headers_of(p: Path) -> dict[str, str]:
    out = {}
    for line in p.read_text(errors="replace").splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip().lower()] = v.strip()
    return out


def main() -> int:
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%Y-%m-%d")
    raw = ROOT / "raw" / day
    (raw / "zips").mkdir(parents=True, exist_ok=True)
    (raw / "pages").mkdir(parents=True, exist_ok=True)
    files = []
    for kind, url, rel in ITEMS:
        dest = raw / rel
        hdr = dest.with_suffix(dest.suffix + ".headers")
        if not dest.exists():
            t0 = datetime.now(UTC).isoformat(timespec="seconds")
            r = subprocess.run(["curl", "-sS", "-A", UA, "-D", str(hdr), "-o", str(dest), "-w", "%{http_code}", url], capture_output=True, text=True)
            code = r.stdout.strip()
            if code != "200":
                dest.unlink(missing_ok=True)
                print(f"STOP: {url} -> HTTP {code} {r.stderr.strip()}", file=sys.stderr)
                return 1
            time.sleep(2)
        else:
            t0 = None
        h = headers_of(hdr) if hdr.exists() else {}
        files.append({"path": dest.relative_to(ROOT).as_posix(), "url": url, "kind": kind, "bytes": dest.stat().st_size, "sha256": sha256(dest),
                      "fetched_at_utc": t0 or datetime.fromtimestamp(dest.stat().st_mtime, UTC).isoformat(timespec="seconds"),
                      "last_modified": h.get("last-modified"), "etag": h.get("etag"), "content_type": h.get("content-type")})
    # unzip next to the zips, unchanged (names as stored; cp932 names are decoded for the directory only)
    for f in list(files):
        if f["kind"] != "zip":
            continue
        zp = ROOT / f["path"]
        out = raw / "unzipped" / zp.stem
        with zipfile.ZipFile(zp) as z:
            for zi in z.infolist():
                if zi.is_dir():
                    continue
                name = zi.filename
                if not (zi.flag_bits & 0x800):
                    try:
                        name = zi.filename.encode("cp437").decode("cp932")
                    except UnicodeError:
                        pass
                target = out / name
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_bytes(z.read(zi))
                files.append({"path": target.relative_to(ROOT).as_posix(), "from_zip": zp.name, "zip_member_as_stored": zi.filename,
                              "kind": "extracted", "bytes": target.stat().st_size, "sha256": sha256(target)})
    man = {"fetched_at_utc": datetime.now(UTC).isoformat(timespec="seconds"), "user_agent": UA, "files": files}
    (raw / "MANIFEST.json").write_text(json.dumps(man, indent=1, ensure_ascii=False) + "\n")
    print(f"{len(files)} entries in {raw / 'MANIFEST.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
