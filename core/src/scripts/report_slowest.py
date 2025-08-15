#!/usr/bin/env python3
import os, json, glob
from datetime import datetime

LOG_DIR = os.getenv("LOG_DIR", "./logs")
OUT_DIR = os.getenv("REPORT_OUT", "./logs")
os.makedirs(OUT_DIR, exist_ok=True)

def latest_jsonl():
    paths = sorted(glob.glob(os.path.join(LOG_DIR, "*.jsonl")))
    return paths[-1] if paths else None

def parse_jsonl(path):
    with open(path, "r") as f:
        for line in f:
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

def main():
    src = latest_jsonl()
    if not src:
        print("No JSONL logs found"); return 1

    rows = []
    for rec in parse_jsonl(src):
        # förväntat loggformat: {"ts": "...", "path": "...", "method": "GET", "lat_ms": 12.3, "rid": "...", "status": 200, ...}
        lat = rec.get("lat_ms")
        if lat is None: 
            continue
        rows.append((lat, rec.get("method"), rec.get("path"), rec.get("status"), rec.get("rid"), rec.get("ts")))

    rows.sort(reverse=True, key=lambda r: r[0])
    top = rows[:10]

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    md_path = os.path.join(OUT_DIR, f"slowest_{ts}.md")
    with open(md_path, "w") as f:
        f.write("# Top 10 långsammaste requests\n\n")
        f.write("| lat_ms | method | status | path | rid | ts |\n|---:|:---:|---:|---|---|---|\n")
        for lat, m, p, s, rid, t in top:
            f.write(f"| {lat:.1f} | {m} | {s} | `{p}` | `{rid}` | {t} |\n")

    print(md_path)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
