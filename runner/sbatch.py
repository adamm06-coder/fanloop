"""Render an OSC Slurm script from a job YAML file.

The renderer does not submit, does not SSH, and does not invent a project code.
The account is read from an environment variable at render time. The rendered
file contains that code, so it must stay out of git.
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

SBATCH_SCHEMA = "fanloop.sbatch/v0"
CLUSTERS = ("cardinal", "pitzer", "ascend")

# OSC's own job-script page uses these as illustrations. Never treat them as real.
_EXAMPLE_ACCOUNTS = {
    "pas1234",
    "pas4321",
    "pas0000",
    "project",
    "account",
    "none",
    "null",
    "test",
    "changeme",
    "todo",
    "example",
    "yourproject",
    "youroscproject",
    "oscproject",
}
_SECRET_MARKERS = (
    "password:",
    "secret:",
    "token:",
    "api_key:",
    "begin openssh",
    "begin rsa",
    "private key",
)
_JOB_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,14}$")
_TIME = re.compile(r"^(\d+-)?\d{1,3}:\d{2}:\d{2}$")
_ACCOUNT = re.compile(r"^[A-Za-z][A-Za-z0-9]{2,15}$")


class JobSpec(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: str = Field(alias="schema")
    job_name: str
    account_env: str = "OSC_PROJECT"
    cluster: Literal["cardinal", "pitzer", "ascend"]
    nodes: int = Field(ge=1, le=4)
    ntasks_per_node: int = Field(ge=1, le=48)
    time: str
    modules: list[str] = Field(min_length=1)
    case_relpath: str
    solver: Literal["simpleFoam"]
    parallel: bool = False
    notes: str = ""

    @model_validator(mode="after")
    def check_week1(self) -> JobSpec:
        if self.schema_version != SBATCH_SCHEMA:
            raise ValueError(f"unsupported job schema {self.schema_version!r}")
        if not _JOB_NAME.match(self.job_name):
            raise ValueError(
                "job_name must be 1-15 characters, start with a letter, and contain "
                "only letters, digits, '_' or '-'. OSC documents a 15-character job-name limit."
            )
        if not _TIME.match(self.time):
            raise ValueError("time must look like HH:MM:SS or D-HH:MM:SS")
        if self.account_env != "OSC_PROJECT":
            raise ValueError("account_env must be OSC_PROJECT; do not put a project code in YAML")
        if self.parallel:
            raise ValueError(
                "Week-1 render is serial only. Parallel MPI launchers on OSC depend on "
                "the module stack; do not guess one."
            )
        if any(item != "openfoam/2606" for item in self.modules):
            raise ValueError("Week-1 jobs load openfoam/2606 only. Confirm other modules on the cluster.")
        if ".." in Path(self.case_relpath).parts:
            raise ValueError("case_relpath must stay inside the repo")
        return self


class MissingProject(Exception):
    """OSC_PROJECT was unset or looked like a placeholder."""


def load_job(path: Path) -> JobSpec:
    text = Path(path).read_text(encoding="utf-8")
    lowered = text.lower()
    for marker in _SECRET_MARKERS:
        if marker in lowered:
            raise ValueError(f"{path} contains {marker!r}. Job YAML must not hold secrets.")
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must be a YAML mapping")
    return JobSpec.model_validate(raw)


def read_project_code(env: dict[str, str] | None = None) -> str:
    source = os.environ if env is None else env
    raw = source.get("OSC_PROJECT", "").strip()
    if not raw:
        raise MissingProject(
            "OSC_PROJECT is unset. On an OSC login node, run OSCfinger and read "
            "'SLURM Accounts'. Export that code in your shell. Do not commit it."
        )
    if not _ACCOUNT.match(raw) or raw.lower() in _EXAMPLE_ACCOUNTS:
        raise MissingProject(
            "OSC_PROJECT is missing or looks like a placeholder/example "
            f"({raw!r}). Refusing to render. Use the code from OSCfinger, not a sample."
        )
    return raw


def render_sbatch(job: JobSpec, account: str) -> str:
    login = {
        "cardinal": "Submit from a Cardinal login node (cardinal.osc.edu) or the Cardinal shell in OnDemand.",
        "pitzer": "Submit from a Pitzer login node (pitzer.osc.edu) or the Pitzer shell in OnDemand.",
        "ascend": "Submit from the Ascend shell in OnDemand (https://ondemand.osc.edu). Confirm the SSH host before using one.",
    }[job.cluster]
    module_lines = "\n".join(f"module load {name}" for name in job.modules)
    rendered_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    notes = job.notes.strip() or "Cold internal-flow smoke case. Not a fan performance run."
    return f"""#!/bin/bash
# FanLoop rendered sbatch. Rendered at {rendered_at}.
# This file was NOT submitted. FanLoop does not log in to OSC and does not call sbatch.
# {login}
# {notes}
# The --account value came from the OSC_PROJECT environment variable at render time.
# Do not commit this file. It is covered by *.sbatch in .gitignore.
#SBATCH --job-name={job.job_name}
#SBATCH --account={account}
#SBATCH --nodes={job.nodes}
#SBATCH --ntasks-per-node={job.ntasks_per_node}
#SBATCH --time={job.time}
#SBATCH --output={job.job_name}.%j.out

set -euo pipefail

{module_lines}

# OSC's OpenFOAM software page still shows older batch examples (openfoam/5.0).
# Confirm this module before trusting the job:
#   module show openfoam/2606
if ! command -v blockMesh >/dev/null 2>&1 || ! command -v {job.solver} >/dev/null 2>&1; then
  echo "blockMesh or {job.solver} is not on PATH after module load." >&2
  echo "Run: module show openfoam/2606" >&2
  exit 1
fi

CASE="${{SLURM_SUBMIT_DIR}}/{job.case_relpath}"
cd "${{CASE}}"
test -f system/blockMeshDict
test -f system/controlDict

# Serial smoke. An MPI launcher is intentionally absent until the module stack is known.
blockMesh
{job.solver}

echo "FanLoop: {job.solver} finished."
echo "This was the cold rectangular-duct skeleton, not the impeller."
echo "Do not report thrust from this log."
"""


def assert_output_outside_source(repo: Path, output: Path) -> None:
    """Keep project codes out of the working tree except gitignored dist/."""
    resolved = output.resolve()
    root = repo.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return
    dist = (root / "dist").resolve()
    try:
        resolved.relative_to(dist)
    except ValueError:
        raise ValueError(
            f"Refusing to write {output} inside the repo. The script contains your "
            "OSC project code. Write it under dist/ or outside the checkout."
        )


def write_sbatch(job_path: Path, output: Path, repo: Path, env: dict[str, str] | None = None) -> str:
    job = load_job(job_path)
    account = read_project_code(env)
    assert_output_outside_source(repo, output)
    case_dir = repo / job.case_relpath
    if not (case_dir / "system" / "controlDict").is_file():
        raise ValueError(f"OpenFOAM skeleton not found at {job.case_relpath}")
    text = render_sbatch(job, account)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(text, encoding="utf-8")
    return text
