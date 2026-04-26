#!/usr/bin/env python3
"""
Flash a prepped character pack via USB (pio run -t uploadfs).
Faster than the BLE drop target when you're iterating on a character.

Usage:
  python3 tools/flash_character.py characters/bufo
  python3 tools/flash_character.py characters/bufo --env m5stickc-plus

Defaults to the StickS3 env (m5sticks3) since that's what's actually
plugged in for most development. Pass --env to target the classic board.
"""
import argparse, json, shutil, subprocess, sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATA    = PROJECT / "data" / "characters"
CAP     = 1_800_000


def flash(src: Path, env: str) -> None:
    if not (src / "manifest.json").exists():
        sys.exit(f"no manifest.json in {src} — run tools/prep_character.py first")
    name = json.loads((src / "manifest.json").read_text())["name"]

    total = sum(f.stat().st_size for f in src.iterdir() if f.is_file())
    if total > CAP:
        sys.exit(f"{total:,} bytes — over the {CAP:,} LittleFS cap")

    # uploadfs flashes everything under data/. To allow multiple GIF
    # characters to coexist on LittleFS (firmware now cycles through them
    # via the settings menu), only replace the named character's folder
    # and leave any siblings intact. Existing chars on the device stay
    # because uploadfs syncs the cumulative data/ directory.
    DATA.mkdir(parents=True, exist_ok=True)
    dst = DATA / name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)

    siblings = sorted(p.name for p in DATA.iterdir() if p.is_dir() and p.name != name)
    print(f"staged {name}: {total:,} bytes -> {dst}")
    if siblings:
        print(f"keeping siblings: {', '.join(siblings)}")

    subprocess.run(["pio", "run", "-e", env, "-t", "uploadfs"], cwd=PROJECT, check=True)
    print(f"\nflashed via env {env}. on the stick: hold A -> settings -> ascii pet -> press B to cycle")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src", help="character folder, e.g. characters/bufo")
    p.add_argument("--env", default="m5sticks3",
                   help="PlatformIO env to flash (default: m5sticks3; use m5stickc-plus for classic)")
    args = p.parse_args()
    flash(Path(args.src).resolve(), args.env)
