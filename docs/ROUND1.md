# Round 1 freeze

Date: 2026-09-24

Working name: **FanLoop**. Also called ThrustForge CEM / AeroCEM Lite in
discussion. The repo and the Python package are `fanloop`.

## Product

Capital-light computational-engineering workflow for a Dayton / Beavercreek
founder. The company does not build jet engines. The first product is a
reproducible case library, an OSC job runner, and a results dashboard.

Frozen first vertical: a cold, about 1 kN, electric ducted fan. Single-stage
impeller and stator.

Year-1 path: UAS, experimental, R&D, and AFWERX SBIR-shaped work. Not FAA
Part 33. Cases stay EAR99-like cold fans.

## MVP loop

1. Intent YAML.
2. Parametric geometry. CadQuery or Build123d is the spine. Week 1 also
   ships a pure-Python STL so a checkout runs without the CadQuery wheel.
3. Mesh. Not implemented for the fan in Week 1. The OpenFOAM skeleton meshes
   a rectangular duct with `blockMesh`.
4. OSC Slurm. OpenFOAM first (`module load openfoam/2606` on Cardinal,
   Pitzer, and Ascend). SU2 only if that module is actually installed.
5. Results dashboard. Week 1 page reads a placeholder JSON whose performance
   values are null.

Geometry notes that stay in force:

- PicoGK is optional later. The maintained API is C#.
- Fusion is inspect-only. It is not the spine that produces an OSC case.

## Stamps

| Role | Stamp |
| --- | --- |
| Researcher | Conditional pass |
| Structures | Conditional pass |
| Systems engineering | Conditional pass |
| Inventor | Pass |
| Strategist | Validate first |

Conditional pass means the vertical may proceed only while the rows in
`cases/ducted-fan-1kn/GATES.md` stay honest. `docs/ANALYSIS_GATES.md` points
at that card. Validate first means a number is not a result until a gate
says so.

## Out of year 1

- Ansys wrappers
- A Sapphire-style clone
- Hot combustor CFD
- FAA Part 33
- ITAR designs
- Secrets, project codes, or credentials in git

## What this scaffold delivers

Week 1 is a local smoke path and a rendered, not submitted, OSC script.
It does not claim a thrust, a mesh of the fan, or a completed OSC job.
