"""Pure-Python ducted-fan-ish triangle mesh.

The solid is a visual stand-in: a faceted duct, hub, nose, and flat staggered
blades/stators. Blades intersect the hub. Shells are separate. This is not a
watertight CFD surface and not a volume mesh.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from geom.models import CaseIntent

Vec3 = tuple[float, float, float]
Tri = tuple[Vec3, Vec3, Vec3]

# Facet count around the duct. Enough to read as round in a mesh viewer.
N_THETA = 48


@dataclass(frozen=True)
class MeshStats:
    triangles: int
    backend: str
    blade_count: int
    stator_count: int
    diameter_m: float
    max_radius_m: float


def build_mesh(intent: CaseIntent) -> tuple[list[Tri], MeshStats]:
    g = intent.geometry
    radius = g.diameter_m / 2.0
    hub_r = g.hub_ratio * radius
    tip_r = radius - g.tip_clearance_m
    length = g.duct_length_m

    tris: list[Tri] = []
    _add_tube(tris, radius + g.wall_thickness_m, radius, 0.0, length, N_THETA)

    hub_z0 = 0.22 * length
    hub_z1 = 0.58 * length
    _add_closed_cylinder(tris, hub_r, hub_z0, hub_z1, N_THETA)
    _add_cone(tris, hub_r, hub_z0, hub_z0 - 0.12 * length, N_THETA)

    _add_row(
        tris,
        count=g.blade_count,
        r0=hub_r * 0.98,
        r1=tip_r,
        chord=g.blade_chord_m,
        thickness=g.blade_thickness_m,
        z_center=0.40 * length,
        stagger_deg=g.rotor_stagger_deg,
        angle_offset_deg=0.0,
    )
    _add_row(
        tris,
        count=g.stator_count,
        r0=hub_r * 0.98,
        r1=tip_r,
        chord=g.blade_chord_m * 0.9,
        thickness=g.blade_thickness_m,
        z_center=0.68 * length,
        stagger_deg=-g.stator_stagger_deg,
        angle_offset_deg=(180.0 / g.stator_count) if g.stator_count else 0.0,
    )

    _reject_degenerate(tris)
    max_r = max(math.hypot(p[0], p[1]) for tri in tris for p in tri)
    stats = MeshStats(
        triangles=len(tris),
        backend="pure",
        blade_count=g.blade_count,
        stator_count=g.stator_count,
        diameter_m=g.diameter_m,
        max_radius_m=max_r,
    )
    return tris, stats


def write_ascii_stl(path: Path, tris: list[Tri], name: str = "fanloop") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"solid {name}"]
    for tri in tris:
        nx, ny, nz = _unit_normal(*tri)
        lines.append(f"  facet normal {nx:.6e} {ny:.6e} {nz:.6e}")
        lines.append("    outer loop")
        for x, y, z in tri:
            lines.append(f"      vertex {x:.6e} {y:.6e} {z:.6e}")
        lines.append("    endloop")
        lines.append("  endfacet")
    lines.append(f"endsolid {name}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _add_row(
    tris: list[Tri],
    *,
    count: int,
    r0: float,
    r1: float,
    chord: float,
    thickness: float,
    z_center: float,
    stagger_deg: float,
    angle_offset_deg: float,
) -> None:
    if count <= 0:
        return
    for i in range(count):
        angle = math.radians(angle_offset_deg + i * 360.0 / count)
        corners = _blade_corners(r0, r1, chord, thickness, z_center, stagger_deg, angle)
        _add_box(tris, corners)


def _blade_corners(
    r0: float,
    r1: float,
    chord: float,
    thickness: float,
    z_center: float,
    stagger_deg: float,
    angle: float,
) -> list[Vec3]:
    """Eight corners of a thin radial plate, staggered about the radial axis."""
    stagger = math.radians(stagger_deg)
    cos_s, sin_s = math.cos(stagger), math.sin(stagger)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    corners: list[Vec3] = []
    for radius in (r0, r1):
        for chord_pos in (-chord / 2.0, chord / 2.0):
            for thick in (-thickness / 2.0, thickness / 2.0):
                tangential = thick * cos_s - chord_pos * sin_s
                axial = thick * sin_s + chord_pos * cos_s + z_center
                x = radius * cos_a - tangential * sin_a
                y = radius * sin_a + tangential * cos_a
                corners.append((x, y, axial))
    return corners


def _add_box(tris: list[Tri], corners: list[Vec3]) -> None:
    # Corner order matches _blade_corners: r, then chord, then thickness.
    faces = (
        (0, 2, 3, 1),
        (4, 5, 7, 6),
        (0, 1, 5, 4),
        (2, 6, 7, 3),
        (0, 4, 6, 2),
        (1, 3, 7, 5),
    )
    center = (
        sum(p[0] for p in corners) / 8.0,
        sum(p[1] for p in corners) / 8.0,
        sum(p[2] for p in corners) / 8.0,
    )
    for a, b, c, d in faces:
        pa, pb, pc, pd = corners[a], corners[b], corners[c], corners[d]
        normal = _cross(_sub(pb, pa), _sub(pc, pa))
        outward = _dot(normal, _sub(pa, center))
        if outward < 0:
            _add_quad(tris, pa, pd, pc, pb)
        else:
            _add_quad(tris, pa, pb, pc, pd)


def _add_tube(
    tris: list[Tri], r_outer: float, r_inner: float, z0: float, z1: float, n: int
) -> None:
    outer0 = _ring(r_outer, z0, n)
    outer1 = _ring(r_outer, z1, n)
    inner0 = _ring(r_inner, z0, n)
    inner1 = _ring(r_inner, z1, n)
    for i in range(n):
        j = (i + 1) % n
        _add_quad(tris, outer0[i], outer0[j], outer1[j], outer1[i])
        _add_quad(tris, inner0[j], inner0[i], inner1[i], inner1[j])
        _add_quad(tris, outer0[j], outer0[i], inner0[i], inner0[j])
        _add_quad(tris, outer1[i], outer1[j], inner1[j], inner1[i])


def _add_closed_cylinder(tris: list[Tri], radius: float, z0: float, z1: float, n: int) -> None:
    bot = _ring(radius, z0, n)
    top = _ring(radius, z1, n)
    center_bot = (0.0, 0.0, z0)
    center_top = (0.0, 0.0, z1)
    for i in range(n):
        j = (i + 1) % n
        _add_quad(tris, bot[i], bot[j], top[j], top[i])
        _add_tri(tris, center_bot, bot[j], bot[i])
        _add_tri(tris, center_top, top[i], top[j])


def _add_cone(tris: list[Tri], radius: float, z_base: float, z_apex: float, n: int) -> None:
    base = _ring(radius, z_base, n)
    apex = (0.0, 0.0, z_apex)
    center = (0.0, 0.0, z_base)
    for i in range(n):
        j = (i + 1) % n
        # Apex is upstream of the base (smaller z), so this winding points out.
        _add_tri(tris, apex, base[i], base[j])
        _add_tri(tris, center, base[j], base[i])


def _ring(radius: float, z: float, n: int) -> list[Vec3]:
    return [
        (radius * math.cos(2.0 * math.pi * i / n), radius * math.sin(2.0 * math.pi * i / n), z)
        for i in range(n)
    ]


def _add_quad(tris: list[Tri], a: Vec3, b: Vec3, c: Vec3, d: Vec3) -> None:
    _add_tri(tris, a, b, c)
    _add_tri(tris, a, c, d)


def _add_tri(tris: list[Tri], a: Vec3, b: Vec3, c: Vec3) -> None:
    tris.append((a, b, c))


def _reject_degenerate(tris: list[Tri]) -> None:
    for tri in tris:
        edge_a = _sub(tri[1], tri[0])
        edge_b = _sub(tri[2], tri[0])
        area2 = _dot(_cross(edge_a, edge_b), _cross(edge_a, edge_b))
        if area2 < 1e-24:
            raise RuntimeError("mesh stub produced a degenerate triangle")


def _sub(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _unit_normal(a: Vec3, b: Vec3, c: Vec3) -> Vec3:
    n = _cross(_sub(b, a), _sub(c, a))
    mag = math.sqrt(_dot(n, n))
    if mag < 1e-18:
        return (0.0, 0.0, 0.0)
    return (n[0] / mag, n[1] / mag, n[2] / mag)
