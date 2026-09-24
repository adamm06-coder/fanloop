# ducted-fan-1kn

Cold, single-stage electric ducted fan. Impeller plus stator. Research
placeholder for a ~1 kN class unit aimed at UAS, experimental, and R&D work.

The intent file is `intent.yaml`. The product target is 1000 N. That number
is a target, not a result. `thrust_status` is `target-only-not-a-result` and
the loader will not accept a measured thrust in this schema.

[`GATES.md`](GATES.md) is the gate list (A, B_lite, B, C1, C2, C3, D, E, F).
[`docs/ANALYSIS_GATES.md`](../../docs/ANALYSIS_GATES.md) only points here.
Gate E materials are the stub [`materials.yaml`](materials.yaml): handbook
names only, no copied allowables. Demo discussion uses Gate A and Gate
B_lite, and B_lite stays labeled DEMO. Hardware talk uses Gate A, Gate B
with a mesh study, Gates C1–C3, and Gate E. None of those passes are in
this week. The OpenFOAM duct is not the impeller, and thrust stays unset.

## What the numbers are

| Input | Value | Meaning |
| --- | --- | --- |
| Diameter | 0.30 m | Round starting size, not a closed design. |
| Hub ratio | 0.40 | Hub radius / tip radius. |
| Blades / stators | 8 / 9 | Different counts so the parametric model is not a repeating copy. Not an optimized count. |
| Duct length | 0.25 m | Envelope only. |
| RPM | 12000 | Desired cold operating point. The Week-1 solver does not read it. |

A hand sketch, using static actuator-disk momentum theory and sea-level
density 1.2 kg/m³, shows why this is not a finished size. Disk area is
π·(0.15 m)² ≈ 0.071 m². Ideal induced velocity for 1000 N is about 77 m/s,
and ideal power is about 77 kW. Tip speed at 12000 rpm is about 190 m/s.
Those figures are arithmetic, not a FanLoop output, and they are not in the
dashboard. A real machine at this thrust would likely move diameter, RPM, or
both. The incompressible duct skeleton cannot represent that tip speed.

## Export control

`export_control.intent` is EAR99-like cold-fan research geometry. `itar`,
`hot_section`, and `part33` are false. The loader rejects a case that flips
any of those on. Do not add blade coordinates from a restricted design, a
hot section, or a Part 33 certification model.

## What Week 1 runs

Geometry export builds a visual STL from this file. The OpenFOAM case that
can be submitted later is `solvers/openfoam`, a rectangular cold duct. It
does not use this RPM and it does not produce thrust.
