"""Intent models for a FanLoop case.

Year-1 scope is enforced here: cold flow, no ITAR flag, no hot section, no Part 33.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

INTENT_SCHEMA = "fanloop.intent/v0"


class ExportControl(BaseModel):
    model_config = ConfigDict(extra="forbid")

    intent: str = Field(min_length=1)
    itar: bool
    hot_section: bool
    part33: bool


class GeometrySpec(BaseModel):
    """Parametric ducted-fan envelope. Numbers are inputs, not a sized design."""

    model_config = ConfigDict(extra="forbid")

    diameter_m: float = Field(gt=0, le=2.0)
    hub_ratio: float = Field(gt=0.05, lt=0.85)
    blade_count: int = Field(ge=2, le=24)
    stator_count: int = Field(ge=0, le=24)
    duct_length_m: float = Field(gt=0, le=2.0)
    wall_thickness_m: float = Field(gt=0, le=0.05, default=0.004)
    tip_clearance_m: float = Field(ge=0, lt=0.05, default=0.002)
    blade_chord_m: float = Field(gt=0, le=0.5, default=0.04)
    blade_thickness_m: float = Field(gt=0, le=0.02, default=0.003)
    rotor_stagger_deg: float = Field(ge=-70, le=70, default=25)
    stator_stagger_deg: float = Field(ge=-70, le=70, default=12)

    @model_validator(mode="after")
    def span_fits_duct(self) -> GeometrySpec:
        radius = self.diameter_m / 2.0
        span = radius * (1.0 - self.hub_ratio) - self.tip_clearance_m
        if span <= 0:
            raise ValueError("blade span is not positive; reduce hub ratio or tip clearance")
        if self.blade_chord_m >= self.duct_length_m:
            raise ValueError("blade chord must be shorter than the duct")
        return self


class OperatingPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rpm: float = Field(gt=0, le=100_000)
    fluid: Literal["air"]
    thermal: Literal["cold"]
    note: str = ""


class SolverIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary: Literal["openfoam"]
    module: str = "openfoam/2606"
    alternate: Literal["su2", "none"] = "su2"
    week1_case: str
    physics_week1: str


class CaseIntent(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: str = Field(alias="schema")
    name: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str
    status: Literal["research-placeholder"]
    export_control: ExportControl
    mission: str
    target_thrust_N: float = Field(gt=0, le=100_000)
    thrust_status: Literal["target-only-not-a-result"]
    geometry: GeometrySpec
    operating_point: OperatingPoint
    solver: SolverIntent
    notes: str = ""

    @model_validator(mode="after")
    def year1_scope(self) -> CaseIntent:
        if self.schema_version != INTENT_SCHEMA:
            raise ValueError(f"unsupported intent schema {self.schema_version!r}")
        flags = self.export_control
        if flags.itar or flags.hot_section or flags.part33:
            raise ValueError(
                "Year-1 FanLoop refuses ITAR designs, hot-section cases, and Part 33 scope."
            )
        if self.operating_point.thermal != "cold":
            raise ValueError("Year-1 cases are cold flow only.")
        return self


def load_intent(path: Path) -> CaseIntent:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must be a YAML mapping")
    return CaseIntent.model_validate(raw)
