#!/usr/bin/env python3
"""Build the wave-2 training-set video package from the Excel source.

- one target video per Excel row (column K)
- groups downloads by model (Excel column G) + internal/external (column E)
- zips into parts below GitHub's 2GB per-asset limit
"""
import csv
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "source")
OUT = os.path.join(ROOT, "out")
XLSX = os.path.join(SRC, "AMU：训练集-圣诞盲盒真实数据第二波.xlsx")
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PART_LIMIT = 1_700_000_000  # stay under GitHub's 2GB per release asset


def read_xlsx(path):
    z = zipfile.ZipFile(path)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(NS + "si"):
            ss.append("".join(t.text or "" for t in si.iter(NS + "t")))
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.find(NS + "sheetData").findall(NS + "row"):
        cells = {}
        for c in row.findall(NS + "c"):
            ref = c.get("r")
            col = re.match(r"[A-Z]+", ref).group(0)
            t = c.get("t")
            v = c.find(NS + "v")
            isv = c.find(NS + "is")
            if t == "s" and v is not None:
                val = ss[int(v.text)]
            elif t == "inlineStr" and isv is not None:
                val = "".join(x.text or "" for x in isv.iter(NS + "t"))
            elif v is not None:
                val = v.text
            else:
                val = ""
            cells[col] = val
        rows.append((int(row.get("r")), cells))
    return rows


def excel_time(v):
    if not v:
        return ""
    try:
        base = dt.datetime(1899, 12, 30)
        return (base + dt.timedelta(days=float(v))).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return v


def safe_model(m):
    return m or "unknown"


def main(dry_run=False):
    rows = read_xlsx(XLSX)
    header = rows[0][1]
    data = rows[1:]
    records = []
    for rn, c in data:
        req = {}
        try:
            req = json.loads(c.get("J") or "{}")
        except Exception:
            pass
        internal = c.get("E", "") == "1"
        model = safe_model(c.get("G", ""))
        scope = "internal" if internal else "external"
        tpl = c.get("A", "")
        url = c.get("K", "").strip()
        rel = f"videos/{model}/{scope}/r{rn:03d}_{tpl}.mp4" if url else ""
        records.append({
            "excel_row": rn,
            "session_id": tpl,
            "template_id": c.get("B", ""),
            "template_record_id": c.get("C", ""),
            "uid": c.get("D", ""),
            "is_internal": c.get("E", ""),
            "create_time": excel_time(c.get("F", "")),
            "model": model,
            "pay_ok": c.get("H", ""),
            "billing_status": c.get("I", ""),
            "pick_a": req.get("pick_a", ""),
            "pick_b": req.get("pick_b", ""),
            "pick_c": req.get("pick_c", ""),
            "pick_model": req.get("pick_model", ""),
            "person_1": req.get("person_1", ""),
            "video_url": url,
            "file": rel,
            "status": "pending" if url else "missing_video_url",
            "part": "",
        })

    os.makedirs(OUT, exist_ok=True)
    readme_src = os.path.join(ROOT, "README.md")
    if os.path.exists(readme_src):
        shutil.copyfile(readme_src, os.path.join(OUT, "README.md"))
    work = os.path.join(OUT, "work")
    if not dry_run:
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work, exist_ok=True)

    def download(rec):
        path = os.path.join(work, rec["file"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        part = path + ".part"
        if os.path.exists(part):
            os.remove(part)
        r = subprocess.run([
            "curl", "-fSL", "--retry", "3", "--retry-delay", "2",
            "--connect-timeout", "20", "--max-time", "300",
            "-o", part, rec["video_url"],
        ], capture_output=True, text=True)
        if r.returncode != 0:
            if os.path.exists(part):
                os.remove(part)
            return rec["excel_row"], "download_failed", (r.stderr or "")[:200]
        size = os.path.getsize(part)
        if size < 100_000:
            os.remove(part)
            return rec["excel_row"], "too_small", f"{size} bytes"
        os.replace(part, path)
        return rec["excel_row"], "ok", f"{size} bytes"

    if not dry_run:
        todo = [r for r in records if r["video_url"]]
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = {pool.submit(download, r): r for r in todo}
            done = 0
            for fut in as_completed(futures):
                row, status, msg = fut.result()
                for rec in records:
                    if rec["excel_row"] == row:
                        rec["status"] = status
                        break
                done += 1
                print(f"[{done}/{len(todo)}] row {row}: {status} {msg}", flush=True)

    total_bytes = 0
    for rec in records:
        if rec["status"] == "ok" and not dry_run:
            total_bytes += os.path.getsize(os.path.join(work, rec["file"]))

    # split into parts by cumulative size
    parts, current, current_size = [], [], 0
    for rec in records:
        if rec["status"] != "ok":
            continue
        size = os.path.getsize(os.path.join(work, rec["file"]))
        if current and current_size + size > PART_LIMIT:
            parts.append(current)
            current, current_size = [], 0
        current.append(rec)
        current_size += size
    if current:
        parts.append(current)
    for i, part in enumerate(parts, 1):
        for rec in part:
            rec["part"] = f"wave2_part{i:02d}.zip"

    # manifest
    fields = ["excel_row", "session_id", "template_id", "template_record_id", "uid",
              "is_internal", "create_time", "model", "pay_ok", "billing_status",
              "pick_a", "pick_b", "pick_c", "pick_model", "person_1",
              "video_url", "file", "status", "part"]
    manifest_path = os.path.join(OUT, "manifest.csv")
    with open(manifest_path, "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=fields)
        w.writeheader()
        for rec in records:
            w.writerow({k: rec.get(k, "") for k in fields})

    missing_path = os.path.join(OUT, "missing.csv")
    with open(missing_path, "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(["excel_row", "session_id", "model", "is_internal", "pay_ok", "billing_status", "status", "video_url"])
        for rec in records:
            if rec["status"] != "ok":
                w.writerow([rec["excel_row"], rec["session_id"], rec["model"], rec["is_internal"],
                            rec["pay_ok"], rec["billing_status"], rec["status"], rec["video_url"]])

    ok = sum(1 for r in records if r["status"] == "ok")
    summary = {
        "excel_rows": len(records),
        "videos_ok": ok,
        "missing": len(records) - ok,
        "total_bytes": total_bytes,
        "parts": [{"name": f"wave2_part{i:02d}.zip", "files": len(p),
                   "bytes": sum(os.path.getsize(os.path.join(work, r['file'])) for r in p)}
                  for i, p in enumerate(parts, 1)],
        "by_model": {},
        "by_status": {},
    }
    for rec in records:
        summary["by_status"][rec["status"]] = summary["by_status"].get(rec["status"], 0) + 1
    for rec in records:
        key = rec["model"] + "/" + ("internal" if rec["is_internal"] == "1" else "external")
        ent = summary["by_model"].setdefault(key, [0, 0, 0])
        ent[0] += 1
        if rec["status"] == "ok":
            ent[1] += 1
            ent[2] += os.path.getsize(os.path.join(work, rec["file"])) if not dry_run else 0
        else:
            ent[1] += 0
    print(json.dumps(summary, ensure_ascii=False, indent=1))

    if dry_run:
        return

    # zip parts
    common = ["manifest.csv", "missing.csv", "README.md", "build_summary.txt"]
    with open(os.path.join(OUT, "build_summary.txt"), "w", encoding="utf-8") as fp:
        fp.write(json.dumps(summary, ensure_ascii=False, indent=1) + "\n")
    for i, part in enumerate(parts, 1):
        name = f"wave2_part{i:02d}.zip"
        zp = os.path.join(OUT, name)
        with zipfile.ZipFile(zp, "w", zipfile.ZIP_STORED) as z:
            for rec in part:
                z.write(os.path.join(work, rec["file"]), arcname=rec["file"])
            for f in common:
                srcp = os.path.join(OUT, f)
                if os.path.exists(srcp):
                    z.write(srcp, arcname=f)
            z.write(XLSX, arcname="source/" + os.path.basename(XLSX))
        print(f"{name}: {os.path.getsize(zp)/1e9:.2f} GB", flush=True)

    shas = []
    for i, _ in enumerate(parts, 1):
        name = f"wave2_part{i:02d}.zip"
        h = hashlib.sha256()
        with open(os.path.join(OUT, name), "rb") as fp:
            for chunk in iter(lambda: fp.read(1 << 20), b""):
                h.update(chunk)
        shas.append(f"{h.hexdigest()}  {name}")
    with open(os.path.join(OUT, "wave2_sha256.txt"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(shas) + "\n")
    print("\n".join(shas))


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)
