"""Count triangles and report the bounding box of an ASCII STL.

This does not build a volume mesh. It only checks that an exported STL is
non-empty and reports its extent.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

Vec3 = tuple[float, float, float]
Tri = tuple[Vec3, Vec3, Vec3]


def parse_ascii_stl(text: str) -> list[Tri]:
    tris: list[Tri] = []
    current: list[Vec3] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 4 and parts[0] == "vertex":
            current.append((float(parts[1]), float(parts[2]), float(parts[3])))
            if len(current) == 3:
                tris.append((current[0], current[1], current[2]))
                current = []
    if current:
        raise ValueError("STL ended inside a facet")
    if not tris:
        raise ValueError("no triangles found; expected an ASCII STL")
    return tris


def summarize(tris: list[Tri]) -> dict:
    points = [p for tri in tris for p in tri]
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    zs = [p[2] for p in points]
    max_r = max(math.hypot(p[0], p[1]) for p in points)
    return {
        "triangles": len(tris),
        "bbox_min_m": [min(xs), min(ys), min(zs)],
        "bbox_max_m": [max(xs), max(ys), max(zs)],
        "max_radius_m": max_r,
        "note": "Triangle inspection only. This is not a volume mesh and not a CFD check.",
    }


def inspect_path(path: Path) -> dict:
    tris = parse_ascii_stl(path.read_text(encoding="utf-8"))
    report = summarize(tris)
    report["stl"] = str(path)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect an ASCII STL. Does not mesh it.")
    parser.add_argument("stl", type=Path)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="optional JSON report path (stdout always gets the summary)",
    )
    args = parser.parse_args(argv)
    try:
        report = inspect_path(args.stl)
    except (OSError, ValueError) as exc:
        print(exc, file=sys.stderr)
        return 1
    text = json.dumps(report, indent=2)
    print(text)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
