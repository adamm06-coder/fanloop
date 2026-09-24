"""Week-1 smoke tests. No CadQuery, no OpenFOAM binary, no network."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tarfile
from pathlib import Path

import yaml
from pydantic import ValidationError

from geom.ducted_fan import export_stl
from geom.mesh_stub import build_mesh
from geom.models import load_intent
from mesh.inspect_stl import inspect_path
from runner.cli import cmd_list, cmd_package, find_repo_root
from runner.sbatch import MissingProject, load_job, write_sbatch

REPO = Path(__file__).resolve().parents[1]
INTENT = REPO / "cases" / "ducted-fan-1kn" / "intent.yaml"
JOB = REPO / "runner" / "jobs" / "ducted-fan-1kn.yaml"


def test_repo_root_and_intent_round_trip():
    assert find_repo_root(REPO) == REPO
    intent = load_intent(INTENT)
    assert intent.name == "ducted-fan-1kn"
    assert intent.target_thrust_N == 1000
    assert intent.thrust_status == "target-only-not-a-result"
    assert intent.operating_point.thermal == "cold"
    assert intent.export_control.itar is False


def test_year1_scope_refuses_restricted_flags(tmp_path: Path):
    raw = yaml.safe_load(INTENT.read_text(encoding="utf-8"))
    raw["export_control"]["hot_section"] = True
    path = tmp_path / "intent.yaml"
    path.write_text(yaml.safe_dump(raw), encoding="utf-8")
    try:
        load_intent(path)
    except ValidationError as exc:
        assert "hot-section" in str(exc)
    else:
        raise AssertionError("hot-section case was accepted")


def test_pure_stl_tracks_diameter_and_blade_count(tmp_path: Path):
    intent = load_intent(INTENT)
    tris, stats = build_mesh(intent)
    assert stats.backend == "pure"
    assert stats.triangles == len(tris)
    expected_radius = intent.geometry.diameter_m / 2.0 + intent.geometry.wall_thickness_m
    assert math.isclose(stats.max_radius_m, expected_radius, rel_tol=0, abs_tol=1e-9)
    length = intent.geometry.duct_length_m
    for tri in tris:
        for x, y, z in tri:
            assert 0.0 - 1e-9 <= z <= length + 1e-9
            assert math.hypot(x, y) <= expected_radius + 1e-9

    more_blades = intent.geometry.model_copy(update={"blade_count": intent.geometry.blade_count + 1})
    _, more_stats = build_mesh(intent.model_copy(update={"geometry": more_blades}))
    assert more_stats.triangles - stats.triangles == 12

    stl = tmp_path / "fan.stl"
    written = export_stl(intent, stl, backend="pure")
    assert written.triangles == stats.triangles
    report = inspect_path(stl)
    assert report["triangles"] == stats.triangles
    assert math.isclose(report["max_radius_m"], expected_radius, abs_tol=1e-6)


def test_list_and_package(tmp_path: Path, capsys):
    assert cmd_list(REPO) == 0
    listed = capsys.readouterr().out
    assert "ducted-fan-1kn" in listed
    assert "not a result" in listed

    archive_path = tmp_path / "case.tar.gz"
    assert cmd_package(REPO, "ducted-fan-1kn", archive_path) == 0
    with tarfile.open(archive_path, "r:gz") as archive:
        names = set(archive.getnames())
    assert "ducted-fan-1kn/intent.yaml" in names
    assert "ducted-fan-1kn/openfoam/system/blockMeshDict" in names
    assert "ducted-fan-1kn/openfoam/0/U" in names
    manifest = archive_path  # re-open for the manifest body
    with tarfile.open(manifest, "r:gz") as archive:
        payload = json.loads(archive.extractfile("ducted-fan-1kn/manifest.json").read())
    assert payload["contains_credentials"] is False
    assert payload["osc_submitted"] is False
    assert "ducted-fan-1kn/manifest.json" in payload["files"]
    blob = archive_path.read_bytes()
    assert b"password" not in blob.lower()
    assert b"OSC_PROJECT" not in blob


def test_sbatch_fails_closed_and_renders_outside_the_repo(tmp_path: Path):
    job = load_job(JOB)
    assert job.solver == "simpleFoam"
    assert job.modules == ["openfoam/2606"]
    assert job.parallel is False

    try:
        write_sbatch(JOB, tmp_path / "missing.sbatch", REPO, env={})
    except MissingProject as exc:
        assert "OSC_PROJECT" in str(exc)
    else:
        raise AssertionError("missing project code was accepted")
    assert not (tmp_path / "missing.sbatch").exists()

    for sample in ("pas1234", "PAS4321", "changeme"):
        try:
            write_sbatch(JOB, tmp_path / "sample.sbatch", REPO, env={"OSC_PROJECT": sample})
        except MissingProject:
            pass
        else:
            raise AssertionError(f"sample account {sample} was accepted")

    try:
        write_sbatch(JOB, REPO / "runner" / "nope.sbatch", REPO, env={"OSC_PROJECT": "prj9999"})
    except ValueError as exc:
        assert "Refusing" in str(exc)
    else:
        raise AssertionError("in-repo sbatch write was accepted")

    dest = tmp_path / "fanloop-1kn.sbatch"
    text = write_sbatch(JOB, dest, REPO, env={"OSC_PROJECT": "prj9999"})
    assert "#SBATCH --account=prj9999" in text
    assert "#SBATCH --job-name=fanloop-1kn" in text
    assert "module load openfoam/2606" in text
    assert "simpleFoam" in text
    assert "NOT submitted" in text
    assert "mpiexec" not in text
    lowered = text.lower()
    assert "password" not in lowered
    assert "token" not in lowered
    assert "pas1234" not in lowered


def test_openfoam_skeleton_matches_its_patches():
    root = REPO / "solvers" / "openfoam"
    required = [
        "README.md",
        "Allrun",
        "system/controlDict",
        "system/fvSchemes",
        "system/fvSolution",
        "system/blockMeshDict",
        "system/decomposeParDict",
        "constant/transportProperties",
        "constant/physicalProperties",
        "constant/turbulenceProperties",
        "0/U",
        "0/p",
        "0/k",
        "0/omega",
        "0/nut",
    ]
    for rel in required:
        text = (root / rel).read_text(encoding="utf-8")
        assert text.strip()
        if rel not in {"README.md", "Allrun"}:
            assert "FoamFile" in text
    block = (root / "system" / "blockMeshDict").read_text(encoding="utf-8")
    for patch in ("inlet", "outlet", "walls"):
        assert patch in block
        for field in ("U", "p", "k", "omega", "nut"):
            assert patch in (root / "0" / field).read_text(encoding="utf-8")
    assert "simpleFoam" in (root / "system" / "controlDict").read_text(encoding="utf-8")
    assert (root / "Allrun").read_text(encoding="utf-8").startswith("#!/bin/sh")


def test_placeholder_dashboard_has_null_results_only():
    data = json.loads((REPO / "viz" / "data" / "results.placeholder.json").read_text())
    js = (REPO / "viz" / "data" / "results.placeholder.js").read_text()
    prefix = "window.FANLOOP_RESULTS = "
    assert js.startswith(prefix)
    parsed_js = json.loads(js[len(prefix) :].strip().rstrip(";"))
    assert parsed_js == data
    assert data["status"] == "not_run"
    assert all(row["value"] is None for row in data["quantities"])
    html = (REPO / "viz" / "index.html").read_text(encoding="utf-8")
    assert "data/results.placeholder.json" in html
    assert "data/results.placeholder.js" in html


def test_cli_list_and_refuses_submit_language():
    env = os.environ.copy()
    env.pop("OSC_PROJECT", None)
    listed = subprocess.run(
        [sys.executable, "-m", "runner", "list"],
        cwd=REPO,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert listed.returncode == 0
    assert "ducted-fan-1kn" in listed.stdout
    rendered = subprocess.run(
        [
            sys.executable,
            "-m",
            "runner",
            "render-sbatch",
            "--job",
            str(JOB),
            "-o",
            "/tmp/fanloop-should-not-write.sbatch",
        ],
        cwd=REPO,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert rendered.returncode == 2
    assert "OSC_PROJECT" in rendered.stderr
    assert not Path("/tmp/fanloop-should-not-write.sbatch").exists()
