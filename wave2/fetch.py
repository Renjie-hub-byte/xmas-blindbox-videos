#!/usr/bin/env python3
"""Download the wave-2 release parts without needing gh, then unzip.

Usage:
  python3 fetch.py            # download all wave2_part*.zip into ./wave2
  python3 fetch.py --list     # only list release assets
"""
import json
import os
import subprocess
import sys
import urllib.request

REPO = "Renjie-hub-byte/xmas-blindbox-videos"
TAG = "v2"
OUT = "wave2"


def main():
    url = f"https://api.github.com/repos/{REPO}/releases/tags/{TAG}"
    with urllib.request.urlopen(url, timeout=60) as resp:
        release = json.load(resp)
    parts = [a for a in release["assets"] if a["name"].startswith("wave2_part")
             and a["name"].endswith(".zip")]
    if not parts:
        raise SystemExit("no wave2_part*.zip assets found")
    for a in parts:
        print(a["id"], a["name"], a["size"])
    if "--list" in sys.argv:
        return
    os.makedirs(OUT, exist_ok=True)
    for a in parts:
        path = os.path.join(OUT, a["name"])
        if os.path.exists(path) and os.path.getsize(path) == a["size"]:
            print("skip (already complete)", path)
            continue
        tmp = path + ".part"
        subprocess.run([
            "curl", "-fSL", "--retry", "3", "--retry-delay", "3",
            "-H", "Accept: application/octet-stream",
            "-o", tmp, a["url"],
        ], check=True)
        if os.path.getsize(tmp) != a["size"]:
            raise SystemExit(f"size mismatch: {tmp}")
        os.replace(tmp, path)
        print("downloaded", path)
    print(f"\nDone. Unzip with:\n  cd {OUT} && for z in wave2_part*.zip; do unzip -o \"$z\"; done")


if __name__ == "__main__":
    main()
