"""Local FanLoop commands: list cases, package a case, render an sbatch file.

Nothing here contacts OSC.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import tarfile
from pathlib import Path

from pydantic import ValidationError

from geom.models import load_intent
from runner.sbatch import MissingProject, write_sbatch


def find_repo_root(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").is_file() and (candidate / "cases").is_dir():
            return candidate
    raise FileNotFoundError(
        "Could not find the fanloop checkout (pyproject.toml and cases/). "
        "Run these commands from the repo."
    )


def iter_cases(repo: Path) -> list[Path]:
    root = repo / "cases"
    if not root.is_dir():
        return []
    return sorted(path for path in root.iterdir() if (path / "intent.yaml").is_file())


def cmd_list(repo: Path) -> int:
    cases = iter_cases(repo)
    if not cases:
        print("No cases found under cases/*/intent.yaml")
        return 1
    for case_dir in cases:
        intent = load_intent(case_dir / "intent.yaml")
        geo = intent.geometry
        print(
            f"{intent.name}  thrust_target_N={intent.target_thrust_N:g} "
            f"(not a result)  D={geo.diameter_m:g} m  blades={geo.blade_count}  "
            f"stators={geo.stator_count}  thermal={intent.operating_point.thermal}"
        )
    return 0


def cmd_package(repo: Path, case_name: str, output: Path | None) -> int:
    case_dir = repo / "cases" / case_name
    intent_path = case_dir / "intent.yaml"
    if not intent_path.is_file():
        print(f"No intent.yaml in cases/{case_name}", file=sys.stderr)
        return 1
    intent = load_intent(intent_path)
    if intent.name != case_name:
        print(
            f"intent name {intent.name!r} does not match directory {case_name!r}",
            file=sys.stderr,
        )
        return 1
    skeleton = repo / "solvers" / "openfoam"
    if not (skeleton / "system" / "controlDict").is_file():
        print("solvers/openfoam skeleton is missing", file=sys.stderr)
        return 1

    dest = output or (repo / "dist" / f"{case_name}.tar.gz")
    dest.parent.mkdir(parents=True, exist_ok=True)

    files: list[str] = []
    with tarfile.open(dest, "w:gz") as archive:
        _add(archive, intent_path, f"{case_name}/intent.yaml", files)
        readme = case_dir / "README.md"
        if readme.is_file():
            _add(archive, readme, f"{case_name}/README.md", files)
        for path in sorted(skeleton.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts:
                rel = path.relative_to(skeleton).as_posix()
                _add(archive, path, f"{case_name}/openfoam/{rel}", files)
        files.append(f"{case_name}/manifest.json")
        manifest = {
            "schema": "fanloop.package/v0",
            "case": case_name,
            "contains_credentials": False,
            "osc_submitted": False,
            "files": list(files),
            "note": (
                "Local bundle of the intent YAML and the cold-duct OpenFOAM skeleton. "
                "Not a CFD result. This archive contains no OSC project code."
            ),
        }
        payload = json.dumps(manifest, indent=2).encode("utf-8")
        info = tarfile.TarInfo(name=f"{case_name}/manifest.json")
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))

    print(f"wrote {dest} ({len(files)} files, credentials=none, submitted=false)")
    return 0


def _add(archive: tarfile.TarFile, path: Path, arcname: str, files: list[str]) -> None:
    archive.add(path, arcname=arcname, recursive=False)
    files.append(arcname)


def cmd_render_sbatch(repo: Path, job: Path, output: Path) -> int:
    try:
        write_sbatch(job, output, repo)
    except MissingProject as exc:
        print(exc, file=sys.stderr)
        return 2
    print(f"wrote {output}")
    print("Not submitted. Review the script, then run sbatch yourself on OSC.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fanloop",
        description="Local FanLoop case tools. Does not log in to OSC and does not submit jobs.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="list local cases under cases/")

    package = sub.add_parser("package", help="tar a case plus the OpenFOAM skeleton")
    package.add_argument("case", help="case directory name under cases/")
    package.add_argument("-o", "--output", type=Path, help="tarball path (default: dist/<case>.tar.gz)")

    render = sub.add_parser(
        "render-sbatch",
        help="render a Slurm script from job YAML; requires OSC_PROJECT in the environment",
    )
    render.add_argument("--job", type=Path, required=True, help="job YAML template")
    render.add_argument("-o", "--output", type=Path, required=True, help="output .sbatch path")

    args = parser.parse_args(argv)
    try:
        repo = find_repo_root()
        if args.cmd == "list":
            return cmd_list(repo)
        if args.cmd == "package":
            return cmd_package(repo, args.case, args.output)
        if args.cmd == "render-sbatch":
            return cmd_render_sbatch(repo, args.job, args.output)
    except ValidationError as exc:
        print(exc, file=sys.stderr)
        return 1
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"unknown command {args.cmd}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
