"""Export a ducted-fan-ish STL from a FanLoop intent YAML file.

The default path is pure Python and has no CAD dependency. CadQuery is optional
and is not what Week-1 tests run.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic import ValidationError

from geom.mesh_stub import MeshStats, build_mesh, write_ascii_stl
from geom.models import CaseIntent, load_intent


def export_stl(intent: CaseIntent, path: Path, backend: str = "auto") -> MeshStats:
    chosen = resolve_backend(backend)
    if chosen == "cadquery":
        export_cadquery(intent, path)
        return MeshStats(
            triangles=-1,
            backend="cadquery",
            blade_count=intent.geometry.blade_count,
            stator_count=intent.geometry.stator_count,
            diameter_m=intent.geometry.diameter_m,
            max_radius_m=(intent.geometry.diameter_m / 2.0) + intent.geometry.wall_thickness_m,
        )
    tris, stats = build_mesh(intent)
    write_ascii_stl(path, tris, name=intent.name)
    return stats


def resolve_backend(choice: str) -> str:
    if choice == "pure":
        return "pure"
    if choice == "cadquery":
        return "cadquery"
    if choice != "auto":
        raise ValueError(f"unknown backend {choice!r}")
    try:
        import cadquery  # noqa: F401
    except ImportError:
        return "pure"
    return "cadquery"


def export_cadquery(intent: CaseIntent, path: Path) -> None:
    """Best-effort CadQuery solid. Week-1 smoke tests do not execute this."""
    try:
        import cadquery as cq
    except ImportError as exc:
        raise SystemExit(
            "CadQuery is not installed. Use --backend pure, or install the optional extra:\n"
            '  pip install -e ".[cadquery]"\n'
            "CadQuery pulls a large OpenCascade wheel. The pure-Python STL is the "
            "supported Week-1 path when that install is too heavy."
        ) from exc

    solid = _cadquery_solid(cq, intent)
    path.parent.mkdir(parents=True, exist_ok=True)
    cq.exporters.export(solid, str(path))


def _cadquery_solid(cq, intent: CaseIntent):
    g = intent.geometry
    radius = g.diameter_m / 2.0
    length = g.duct_length_m
    hub_r = g.hub_ratio * radius
    tip_r = radius - g.tip_clearance_m
    span = tip_r - hub_r

    duct = cq.Workplane("XY").circle(radius + g.wall_thickness_m).circle(radius).extrude(length)
    hub_z0 = 0.22 * length
    hub = (
        cq.Workplane("XY")
        .circle(hub_r)
        .extrude(0.36 * length)
        .translate((0, 0, hub_z0))
    )
    solid = duct.union(hub)

    def add_row(count: int, z_center: float, stagger_deg: float, chord: float) -> None:
        nonlocal solid
        if count <= 0:
            return
        for i in range(count):
            mid_r = (hub_r + tip_r) / 2.0
            blade = (
                cq.Workplane("XZ")
                .center(mid_r, 0)
                .rect(span, chord)
                .extrude(g.blade_thickness_m / 2.0, both=True)
            )
            blade = blade.rotate((mid_r, 0, 0), (mid_r + 1.0, 0, 0), stagger_deg)
            blade = blade.translate((0, 0, z_center))
            blade = blade.rotate((0, 0, 0), (0, 0, 1), i * 360.0 / count)
            solid = solid.union(blade)

    add_row(g.blade_count, 0.40 * length, g.rotor_stagger_deg, g.blade_chord_m)
    add_row(g.stator_count, 0.68 * length, -g.stator_stagger_deg, g.blade_chord_m * 0.9)
    return solid


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Export a ducted-fan-ish STL from FanLoop intent YAML. "
            "The mesh is a visual solid, not a CFD surface."
        )
    )
    parser.add_argument("intent", type=Path, help="path to intent.yaml")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output STL path")
    parser.add_argument(
        "--backend",
        choices=("auto", "pure", "cadquery"),
        default="auto",
        help="auto uses CadQuery only when it is already installed (default: pure otherwise)",
    )
    args = parser.parse_args(argv)
    try:
        intent = load_intent(args.intent)
        stats = export_stl(intent, args.output, backend=args.backend)
    except ValidationError as exc:
        print(exc, file=sys.stderr)
        return 1
    except (OSError, ValueError, RuntimeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(
        f"wrote {args.output} backend={stats.backend} "
        f"triangles={stats.triangles} diameter_m={stats.diameter_m} "
        f"blades={stats.blade_count} stators={stats.stator_count}"
    )
    if stats.backend == "pure":
        print("pure-Python STL: visual stand-in, not a watertight CFD surface.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
