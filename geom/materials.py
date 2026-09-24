"""Gate E materials card.

Year-1 cards are research placeholders. They may name a handbook. They may
not carry a copied allowable.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, model_validator

MATERIALS_SCHEMA = "fanloop.materials/v0"


class MaterialReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    kind: Literal["handbook-index", "standard-index"]
    title: str = Field(min_length=1)
    locator: Literal["unset"]
    copied_allowable: Literal[False]
    note: str = ""


class MaterialCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    role: Literal["blade", "hub", "casing", "mount"]
    family: Literal["unset"]
    alloy: Literal["unset"]
    temper: Literal["unset"]
    product_form: Literal["unset"]
    basis: Literal["unset"]
    allowable_status: Literal["unset"]
    reference_ids: list[str] = Field(min_length=1)


class MaterialsCard(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: str = Field(alias="schema")
    case: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    gate: Literal["E"]
    status: Literal["research-placeholder"]
    thermal: Literal["cold"]
    claim: Literal["none"]
    note: str
    references: list[MaterialReference] = Field(min_length=1)
    candidates: list[MaterialCandidate] = Field(min_length=1)

    @model_validator(mode="after")
    def placeholder_only(self) -> MaterialsCard:
        if self.schema_version != MATERIALS_SCHEMA:
            raise ValueError(f"unsupported materials schema {self.schema_version!r}")
        known = {ref.id for ref in self.references}
        if len(known) != len(self.references):
            raise ValueError("material reference ids must be unique")
        seen_roles: set[str] = set()
        for candidate in self.candidates:
            if candidate.role in seen_roles:
                raise ValueError(f"duplicate material role {candidate.role}")
            seen_roles.add(candidate.role)
            missing = [ref_id for ref_id in candidate.reference_ids if ref_id not in known]
            if missing:
                raise ValueError(f"{candidate.id} references unknown ids {missing}")
        return self


def load_materials(path: Path) -> MaterialsCard:
    raw = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must be a YAML mapping")
    return MaterialsCard.model_validate(raw)
