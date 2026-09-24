"""Week-1 smoke tests. No CadQuery, no OpenFOAM binary, no network."""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
import tarfile
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import yaml
from pydantic import ValidationError

from geom.ducted_fan import export_stl
from geom.materials import MaterialsCard, load_materials
from geom.mesh_stub import build_mesh
from geom.models import load_intent
from mesh.inspect_stl import inspect_path
from runner.cli import cmd_list, cmd_package, find_repo_root
from runner.sbatch import MissingProject, load_job, write_sbatch

REPO = Path(__file__).resolve().parents[1]
CASE = REPO / "cases" / "ducted-fan-1kn"
INTENT = CASE / "intent.yaml"
MATERIALS = CASE / "materials.yaml"
JOB = REPO / "runner" / "jobs" / "ducted-fan-1kn.yaml"
STRUCTURE_GATE_IDS = ("A", "B_lite", "B", "C1", "C2", "C3", "D", "E", "F")


class SmokeTests(unittest.TestCase):
    def test_repo_root_and_intent_round_trip(self):
        self.assertEqual(find_repo_root(REPO), REPO)
        intent = load_intent(INTENT)
        self.assertEqual(intent.name, "ducted-fan-1kn")
        self.assertEqual(intent.target_thrust_N, 1000)
        self.assertEqual(intent.thrust_status, "target-only-not-a-result")
        self.assertEqual(intent.operating_point.thermal, "cold")
        self.assertFalse(intent.export_control.itar)

    def test_year1_scope_refuses_restricted_flags(self):
        raw = yaml.safe_load(INTENT.read_text(encoding="utf-8"))
        raw["export_control"]["hot_section"] = True
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "intent.yaml"
            path.write_text(yaml.safe_dump(raw), encoding="utf-8")
            with self.assertRaises(ValidationError) as caught:
                load_intent(path)
        self.assertIn("hot-section", str(caught.exception))

    def test_pure_stl_tracks_diameter_and_blade_count(self):
        intent = load_intent(INTENT)
        tris, stats = build_mesh(intent)
        self.assertEqual(stats.backend, "pure")
        self.assertEqual(stats.triangles, len(tris))
        expected_radius = intent.geometry.diameter_m / 2.0 + intent.geometry.wall_thickness_m
        self.assertTrue(math.isclose(stats.max_radius_m, expected_radius, rel_tol=0, abs_tol=1e-9))
        length = intent.geometry.duct_length_m
        for tri in tris:
            for x, y, z in tri:
                self.assertGreaterEqual(z, -1e-9)
                self.assertLessEqual(z, length + 1e-9)
                self.assertLessEqual(math.hypot(x, y), expected_radius + 1e-9)

        more_blades = intent.geometry.model_copy(
            update={"blade_count": intent.geometry.blade_count + 1}
        )
        _, more_stats = build_mesh(intent.model_copy(update={"geometry": more_blades}))
        self.assertEqual(more_stats.triangles - stats.triangles, 12)

        with tempfile.TemporaryDirectory() as tmp:
            stl = Path(tmp) / "fan.stl"
            written = export_stl(intent, stl, backend="pure")
            self.assertEqual(written.triangles, stats.triangles)
            report = inspect_path(stl)
        self.assertEqual(report["triangles"], stats.triangles)
        self.assertTrue(math.isclose(report["max_radius_m"], expected_radius, abs_tol=1e-6))

    def test_list_and_package(self):
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = cmd_list(REPO)
        self.assertEqual(code, 0)
        listed = buffer.getvalue()
        self.assertIn("ducted-fan-1kn", listed)
        self.assertIn("not a result", listed)

        with tempfile.TemporaryDirectory() as tmp:
            archive_path = Path(tmp) / "case.tar.gz"
            self.assertEqual(cmd_package(REPO, "ducted-fan-1kn", archive_path), 0)
            with tarfile.open(archive_path, "r:gz") as archive:
                names = set(archive.getnames())
                payload = json.loads(
                    archive.extractfile("ducted-fan-1kn/manifest.json").read()
                )
            blob = archive_path.read_bytes().lower()
        self.assertIn("ducted-fan-1kn/intent.yaml", names)
        self.assertIn("ducted-fan-1kn/openfoam/system/blockMeshDict", names)
        self.assertIn("ducted-fan-1kn/openfoam/0/U", names)
        self.assertFalse(payload["contains_credentials"])
        self.assertFalse(payload["osc_submitted"])
        self.assertIn("ducted-fan-1kn/manifest.json", payload["files"])
        self.assertNotIn(b"password", blob)
        self.assertNotIn(b"osc_project", blob)

    def test_sbatch_fails_closed_and_renders_outside_the_repo(self):
        job = load_job(JOB)
        self.assertEqual(job.solver, "simpleFoam")
        self.assertEqual(job.modules, ["openfoam/2606"])
        self.assertFalse(job.parallel)

        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.sbatch"
            with self.assertRaises(MissingProject) as caught:
                write_sbatch(JOB, missing, REPO, env={})
            self.assertIn("OSC_PROJECT", str(caught.exception))
            self.assertFalse(missing.exists())

            for sample in ("pas1234", "PAS4321", "changeme"):
                with self.assertRaises(MissingProject):
                    write_sbatch(JOB, Path(tmp) / "sample.sbatch", REPO, env={"OSC_PROJECT": sample})

            dest = Path(tmp) / "fanloop-1kn.sbatch"
            text = write_sbatch(JOB, dest, REPO, env={"OSC_PROJECT": "prj9999"})

        with self.assertRaises(ValueError) as refused:
            write_sbatch(
                JOB,
                REPO / "runner" / "nope.sbatch",
                REPO,
                env={"OSC_PROJECT": "prj9999"},
            )
        self.assertIn("Refusing", str(refused.exception))
        self.assertFalse((REPO / "runner" / "nope.sbatch").exists())

        self.assertIn("#SBATCH --account=prj9999", text)
        self.assertIn("#SBATCH --job-name=fanloop-1kn", text)
        self.assertIn("module load openfoam/2606", text)
        self.assertIn("simpleFoam", text)
        self.assertIn("NOT submitted", text)
        self.assertNotIn("mpiexec", text)
        lowered = text.lower()
        self.assertNotIn("password", lowered)
        self.assertNotIn("token", lowered)
        self.assertNotIn("pas1234", lowered)

    def test_openfoam_skeleton_matches_its_patches(self):
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
            self.assertTrue(text.strip(), rel)
            if rel not in {"README.md", "Allrun"}:
                self.assertIn("FoamFile", text)
        block = (root / "system" / "blockMeshDict").read_text(encoding="utf-8")
        for patch in ("inlet", "outlet", "walls"):
            self.assertIn(patch, block)
            for field in ("U", "p", "k", "omega", "nut"):
                self.assertIn(patch, (root / "0" / field).read_text(encoding="utf-8"))
        self.assertIn("simpleFoam", (root / "system" / "controlDict").read_text(encoding="utf-8"))
        self.assertTrue((root / "Allrun").read_text(encoding="utf-8").startswith("#!/bin/sh"))

    def test_materials_card_loads_as_placeholder(self):
        card = load_materials(MATERIALS)
        self.assertEqual(card.case, "ducted-fan-1kn")
        self.assertEqual(card.gate, "E")
        self.assertEqual(card.status, "research-placeholder")
        self.assertEqual(card.claim, "none")
        self.assertEqual(card.thermal, "cold")
        self.assertTrue(all(item.allowable_status == "unset" for item in card.candidates))
        self.assertTrue(all(item.alloy == "unset" for item in card.candidates))
        self.assertTrue(all(ref.copied_allowable is False for ref in card.references))
        self.assertTrue(all(ref.locator == "unset" for ref in card.references))

        raw = yaml.safe_load(MATERIALS.read_text(encoding="utf-8"))
        raw["candidates"][0]["ftu_MPa"] = 276
        with self.assertRaises(ValidationError):
            MaterialsCard.model_validate(raw)

        readme = (CASE / "README.md").read_text(encoding="utf-8")
        self.assertIn("[`GATES.md`](GATES.md)", readme)
        self.assertIn("[`materials.yaml`](materials.yaml)", readme)
        gates = (CASE / "GATES.md").read_text(encoding="utf-8")
        for token in ("B_lite", "C1", "C2", "C3", "DEMO", "mesh study"):
            self.assertIn(token, gates)

    def test_placeholder_dashboard_has_null_results_only(self):
        data = json.loads((REPO / "viz" / "data" / "results.placeholder.json").read_text())
        js = (REPO / "viz" / "data" / "results.placeholder.js").read_text()
        prefix = "window.FANLOOP_RESULTS = "
        self.assertTrue(js.startswith(prefix))
        parsed_js = json.loads(js[len(prefix) :].strip().rstrip(";"))
        self.assertEqual(parsed_js, data)
        self.assertEqual(data["status"], "not_run")
        self.assertTrue(all(row["value"] is None for row in data["quantities"]))
        quantity_ids = {row["id"] for row in data["quantities"]}
        for qid in ("thrust_N", "shaft_power_W", "efficiency", "factor_of_safety", "tip_gap_m"):
            self.assertIn(qid, quantity_ids)
        self.assertNotIn("structures_gates", data)
        by_gate = {gate["id"]: gate for gate in data["gates"]}
        self.assertEqual(tuple(by_gate), STRUCTURE_GATE_IDS)
        retired = {"export_control", "geometry_smoke", "mesh", "solver", "validation", "fan_surface"}
        self.assertTrue(retired.isdisjoint(by_gate))
        self.assertEqual(by_gate["A"]["ryg"], "yellow")
        for gate_id in STRUCTURE_GATE_IDS:
            if gate_id == "A":
                continue
            self.assertEqual(by_gate[gate_id]["ryg"], "unset", gate_id)
        self.assertNotIn("green", {gate["ryg"] for gate in data["gates"]})
        self.assertIn("DEMO", by_gate["B_lite"]["note"])
        self.assertIn("N/A", by_gate["D"]["note"])
        analysis = (REPO / "docs" / "ANALYSIS_GATES.md").read_text(encoding="utf-8")
        self.assertIn("cases/ducted-fan-1kn/GATES.md", analysis)
        self.assertNotIn("Scope freeze", analysis)
        self.assertNotIn("Fan surface", analysis)
        card = (CASE / "GATES.md").read_text(encoding="utf-8")
        self.assertIn("rectangular cold duct", card)
        self.assertIn("not the impeller", card)
        html = (REPO / "viz" / "index.html").read_text(encoding="utf-8")
        self.assertIn("data/results.placeholder.json", html)
        self.assertIn("data/results.placeholder.js", html)
        self.assertIn('id="gates"', html)
        self.assertNotIn("structures-gates", html)
        self.assertIn("ryg-", html)

    def test_cli_list_and_refuses_missing_project(self):
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
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertIn("ducted-fan-1kn", listed.stdout)
        out = "/tmp/fanloop-should-not-write.sbatch"
        rendered = subprocess.run(
            [
                sys.executable,
                "-m",
                "runner",
                "render-sbatch",
                "--job",
                str(JOB),
                "-o",
                out,
            ],
            cwd=REPO,
            env=env,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(rendered.returncode, 2, rendered.stdout + rendered.stderr)
        self.assertIn("OSC_PROJECT", rendered.stderr)
        self.assertFalse(Path(out).exists())


if __name__ == "__main__":
    unittest.main()
