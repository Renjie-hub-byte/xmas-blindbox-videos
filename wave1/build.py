#!/usr/bin/env python3
"""Build the complete wave-1 package from the full annotation page.

Input : source/盲盒真实数据第一波送标.html  (178 cases embedded in ALL_DATA)
Output: wave1_partNN.zip  (targets grouped by model + gift group, shared candidates)
"""
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_HTML = os.path.join(ROOT, "source", "盲盒真实数据第一波送标.html")
XLSX = os.path.join(ROOT, os.pardir, "wave2", "source", "AMU：训练集-圣诞盲盒真实数据第二波.xlsx")
OUT = os.path.join(ROOT, "out")
NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
PART_LIMIT = 1_700_000_000


def read_html_cases(path):
    h = open(path, encoding="utf-8").read()
    i = h.find("const ALL_DATA = ")
    if i < 0:
        raise SystemExit("ALL_DATA not found")
    i = h.find("[", i)
    data, _ = json.JSONDecoder(strict=False).raw_decode(h[i:])
    return data


def excel_rows(path):
    """case_id -> excel row number (only needs column A)."""
    if not os.path.exists(path):
        return {}
    z = zipfile.ZipFile(path)
    ss = []
    if "xl/sharedStrings.xml" in z.namelist():
        import xml.etree.ElementTree as ET
        root = ET.fromstring(z.read("xl/sharedStrings.xml"))
        for si in root.findall(NS + "si"):
            ss.append("".join(t.text or "" for t in si.iter(NS + "t")))
    import xml.etree.ElementTree as ET
    sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    mapping = {}
    for row in sheet.find(NS + "sheetData").findall(NS + "row"):
        rn = int(row.get("r"))
        for c in row.findall(NS + "c"):
            if c.get("r") == f"A{rn}" and c.get("t") == "s":
                v = c.find(NS + "v")
                if v is not None and v.text:
                    mapping[ss[int(v.text)]] = rn
    return mapping


def ext_of(url):
    return ".mov" if url.split("?")[0].lower().endswith(".mov") else ".mp4"


def main(dry_run=False):
    cases = read_html_cases(SRC_HTML)
    xl = excel_rows(XLSX)

    records = []
    cands = {}  # url -> record
    for c in cases:
        req = c.get("online_request") or {}
        idx = c["idx"]
        gid = req.get("gift_id", "")
        model = (req.get("model") or "unknown").replace("/", "_")
        bgroup = gid.split("-")[0] if "-" in gid else "other"
        turl = (c.get("target_video_path") or "").strip()
        tfile = f"videos/wave1/{model}/{bgroup}/{idx:03d}_{gid}_target{ext_of(turl) or '.mp4'}" if turl else ""
        cand_files = []
        for v in c.get("source_video_candidates") or []:
            u = v.get("original_url") or v.get("preview_url")
            if not u:
                continue
            name = f"videos/wave1/candidates/{v['group']}_{v['id']}_{v['version']}_{v['gender']}{ext_of(u)}"
            cand_files.append(name)
            if u not in cands:
                cands[u] = {"kind": "candidate", "file": name, "url": u,
                            "fallback": v.get("preview_url", ""), "status": "pending"}
        records.append({
            "idx": idx,
            "case_id": c.get("case_id", ""),
            "gift_id": gid,
            "gift_name": req.get("gift_name", ""),
            "model": model,
            "pick_a": req.get("pick_a", ""),
            "pick_b": req.get("pick_b", ""),
            "pick_c": req.get("pick_c", ""),
            "excel_row": xl.get(c.get("case_id", ""), ""),
            "target_file": tfile,
            "target_url": turl,
            "cand_A_v1": next((f for f in cand_files if "/A_" in f and "_v1_" in f), ""),
            "cand_A_v2": next((f for f in cand_files if "/A_" in f and "_v2_" in f), ""),
            "cand_B_v1": next((f for f in cand_files if "/B_" in f and "_v1_" in f), ""),
            "cand_B_v2": next((f for f in cand_files if "/B_" in f and "_v2_" in f), ""),
            "target_status": "pending" if turl else "missing_target_url",
            "part": "",
        })

    os.makedirs(OUT, exist_ok=True)
    work = os.path.join(OUT, "work")
    if not dry_run:
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work, exist_ok=True)

    jobs = [{"file": r["target_file"], "url": r["target_url"], "status": "pending"} for r in records if r["target_url"]]
    jobs += list(cands.values())

    def download(rec):
        path = os.path.join(work, rec["file"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        part = path + ".part"
        r = subprocess.run([
            "curl", "-fSL", "--retry", "3", "--retry-delay", "2",
            "--connect-timeout", "20", "--max-time", "300",
            "-o", part, rec["url"],
        ], capture_output=True, text=True)
        if r.returncode != 0 and rec.get("fallback") and rec["fallback"] != rec["url"]:
            r = subprocess.run([
                "curl", "-fSL", "--retry", "3", "--retry-delay", "2",
                "--connect-timeout", "20", "--max-time", "300",
                "-o", part, rec["fallback"],
            ], capture_output=True, text=True)
        if r.returncode != 0:
            if os.path.exists(part):
                os.remove(part)
            return rec["file"], "download_failed", (r.stderr or "").strip()[-160:]
        size = os.path.getsize(part)
        if size < 100_000:
            os.remove(part)
            return rec["file"], "too_small", f"{size} bytes"
        os.replace(part, path)
        return rec["file"], "ok", f"{size}"

    if not dry_run:
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = {pool.submit(download, j): j for j in jobs}
            done = 0
            for fut in as_completed(futures):
                f, status, msg = fut.result()
                done += 1
                print(f"[{done}/{len(jobs)}] {status:15s} {f} {msg}", flush=True)

    by_file = {}
    for r in records:
        if r["target_file"] and os.path.exists(os.path.join(work, r["target_file"])):
            r["target_status"] = "ok"
        by_file[r["target_file"]] = r
    for u, rec in cands.items():
        rec["status"] = "ok" if os.path.exists(os.path.join(work, rec["file"])) else rec.get("status", "pending")

    # collect everything actually present
    present = []
    for r in records:
        if r["target_status"] == "ok":
            present.append({"file": r["target_file"], "bytes": os.path.getsize(os.path.join(work, r["target_file"])), "ref": r})
    for rec in cands.values():
        if rec["status"] == "ok":
            present.append({"file": rec["file"], "bytes": os.path.getsize(os.path.join(work, rec["file"])), "ref": None})

    parts, current, size_acc = [], [], 0
    for item in sorted(present, key=lambda x: (x["file"].startswith("videos/wave1/candidates"), x["file"])):
        if current and size_acc + item["bytes"] > PART_LIMIT:
            parts.append(current)
            current, size_acc = [], 0
        current.append(item)
        size_acc += item["bytes"]
    if current:
        parts.append(current)

    part_of = {}
    for i, part in enumerate(parts, 1):
        for item in part:
            part_of[item["file"]] = f"wave1_part{i:02d}.zip"
    for r in records:
        r["part"] = part_of.get(r["target_file"], "")
        if r["target_file"] and not r["part"]:
            r["target_status"] = "download_failed"

    fields = ["idx", "case_id", "gift_id", "gift_name", "model", "pick_a", "pick_b", "pick_c",
              "excel_row", "target_file", "target_url", "cand_A_v1", "cand_A_v2",
              "cand_B_v1", "cand_B_v2", "target_status", "part"]
    with open(os.path.join(OUT, "manifest.csv"), "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.DictWriter(fp, fieldnames=fields)
        w.writeheader()
        for r in records:
            w.writerow(r)

    with open(os.path.join(OUT, "candidates.csv"), "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(["file", "group", "id", "version", "gender", "status", "source_url", "part"])
        for rec in sorted(cands.values(), key=lambda x: x["file"]):
            m = re.search(r"/([AB])_(\w+?)_(v\d)_(\w+)\.\w+$", rec["file"])
            meta = m.groups() if m else ("", "", "", "")
            w.writerow([rec["file"], *meta, rec["status"], rec["url"], part_of.get(rec["file"], "")])

    with open(os.path.join(OUT, "missing.csv"), "w", newline="", encoding="utf-8-sig") as fp:
        w = csv.writer(fp)
        w.writerow(["idx", "case_id", "gift_id", "model", "target_status", "target_url"])
        for r in records:
            if r["target_status"] != "ok":
                w.writerow([r["idx"], r["case_id"], r["gift_id"], r["model"], r["target_status"], r["target_url"]])

    summary = {
        "cases": len(records),
        "targets_ok": sum(1 for r in records if r["target_status"] == "ok"),
        "targets_failed": sum(1 for r in records if r["target_status"] != "ok"),
        "candidates_ok": sum(1 for r in cands.values() if r["status"] == "ok"),
        "candidates_failed": sum(1 for r in cands.values() if r["status"] != "ok"),
        "total_bytes": sum(x["bytes"] for x in present),
        "overlap_with_excel": sum(1 for r in records if r["excel_row"]),
        "parts": [{"name": f"wave1_part{i:02d}.zip",
                   "files": len(p), "bytes": sum(x["bytes"] for x in p)} for i, p in enumerate(parts, 1)],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    if dry_run:
        return

    with open(os.path.join(OUT, "build_summary.txt"), "w", encoding="utf-8") as fp:
        fp.write(json.dumps(summary, ensure_ascii=False, indent=1) + "\n")
    shutil.copyfile(SRC_HTML, os.path.join(OUT, "source_page.html"))
    readme = os.path.join(ROOT, "README.md")
    if os.path.exists(readme):
        shutil.copyfile(readme, os.path.join(OUT, "README.md"))

    common = ["README.md", "manifest.csv", "candidates.csv", "missing.csv", "build_summary.txt", "source_page.html"]
    for i, part in enumerate(parts, 1):
        name = f"wave1_part{i:02d}.zip"
        with zipfile.ZipFile(os.path.join(OUT, name), "w", zipfile.ZIP_STORED) as z:
            for item in part:
                z.write(os.path.join(work, item["file"]), arcname=item["file"])
            for f in common:
                p = os.path.join(OUT, f)
                if os.path.exists(p):
                    z.write(p, arcname=f)
        print(f"{name}: {os.path.getsize(os.path.join(OUT, name))/1e9:.2f} GB", flush=True)

    lines = []
    for i, _ in enumerate(parts, 1):
        name = f"wave1_part{i:02d}.zip"
        h = hashlib.sha256()
        with open(os.path.join(OUT, name), "rb") as fp:
            for chunk in iter(lambda: fp.read(1 << 20), b""):
                h.update(chunk)
        lines.append(f"{h.hexdigest()}  {name}")
    with open(os.path.join(OUT, "wave1_sha256.txt"), "w", encoding="utf-8") as fp:
        fp.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(dry_run="--dry-run" in sys.argv)