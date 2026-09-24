# Structures gate card — ducted-fan-1kn

Structures reading of the cold ~1 kN electric ducted fan. This card sits
beside [`docs/ANALYSIS_GATES.md`](../../docs/ANALYSIS_GATES.md) and uses the
Week-1 states already written there. It does not close any row in that
table.

Systems engineering on this card is conditional. Conditional means the
vertical may continue only while the rows below stay honest. It is not a
Gate B pass, not a Gate C pass, and not permission to quote thrust, power,
efficiency, factor of safety, or tip gap.

The dashboard colors are red, yellow, green, and unset. Green would mean the
evidence in the last column exists in the repo. No row is green. Red is
unused: "not started" is unset, not a failed run. Yellow is a partial that
the repo can actually show.

## What the rows are for

| Use | Rows | Limit |
| --- | --- | --- |
| Demo | A and B_lite | B_lite stays labeled DEMO. Force integrals from a propeller or actuation-disk model stay in that label. |
| Hardware talk | A, B with a mesh study, C1, C2, C3, and E | All of those rows have to be green together. D does not fill in for any of them. |

Gate F is how a later green row becomes something another person can
regenerate. A scripted local smoke path is part of F and does not by itself
turn a plot into hardware evidence.

## Rows

| Gate | Asks | Week-1 color | What would have to be true |
| --- | --- | --- | --- |
| A Geometry | Parametric solid (CadQuery or Build123d) and an STL smoke check against the intent envelope. | Yellow | A CadQuery or Build123d solid of the impeller and stator, plus an STL whose bounding cylinder matches the intent diameter. Today the pure-Python STL does that diameter check locally. The plates intersect the hub and the shells are separate, which is the "fan surface: not started" row in `ANALYSIS_GATES.md`. Yellow is that smoke check. It is not a manufacturing model. |
| B_lite Aero, demo | OpenFOAM propeller or actuation disk, with force integrals, labeled DEMO. | Unset | A declared propeller or actuation-disk case, a saved log, and force integrals written down as DEMO. `solvers/openfoam` is a rectangular cold duct and has not been executed. That skeleton is the solver-smoke row in `ANALYSIS_GATES.md`, and it is not this gate. A later B_lite plot still does not pass Gate B and is not hardware talk. |
| B Aero | Blade-resolved flow and a mesh study. | Unset | One closed CFD surface, a volume mesh with a cell count and a wall-spacing note, a declared rotating model (MRF or AMI), and a mesh study. Those are the fan-surface, volume-mesh, fan-physics, and validation rows in `ANALYSIS_GATES.md`. They are not started or blocked. |
| C1 Structure, centrifugal | Blades and hub under centrifugal load. | Unset | A stress model with stated loads and restraints, and a factor of safety that comes from that model. No stress model is in the repo. Dashboard factor of safety stays null. |
| C2 Structure, torque | Torque path through the blades, hub, and shaft. | Unset | The same kind of model as C1, for torque. No blade-retention or torque-path model is in the repo. |
| C3 Structure, casing and mount | Duct, mounts, and the path into the vehicle. | Unset | A casing and mount model. None is in the repo. |
| D Thermo | Metal temperatures and hot-structure allowables. | Unset, N/A | The case is cold: `operating_point.thermal` is `cold` and `export_control.hot_section` is false. N/A means the row is not open. It is not a pass and it does not waive C or E. |
| E Materials | Allowables for a chosen alloy or composite, with a basis. | Unset | [`materials.yaml`](materials.yaml) names handbooks to open later. No alloy, temper, product form, or A/B/S basis is selected, and no handbook number is copied into git. |
| F Reproducibility | Someone else can regenerate the artifact from this repo. | Unset | Case, mesh, solver version, and the command that produced the number. The Week-1 smoke path is scripted, and there is no analysis number to regenerate. A green Slurm job would not close this row by itself; `ANALYSIS_GATES.md` already says that about the claim gate. |

## Week-1 reading

Gate A is the only yellow row. The Round 1 scope freeze in
[`docs/ROUND1.md`](../../docs/ROUND1.md) stays as written there. That freeze
is not painted green on this card.

The 1000 N figure in `intent.yaml` is a target (`thrust_status:
target-only-not-a-result`). The momentum-theory sketch in the case README is
arithmetic on that target. It is not a B_lite force integral and it is not
on the dashboard.

Thrust, shaft power, efficiency, factor of safety, and tip gap stay unset
until a gate that is allowed to produce them has passed. Tip clearance in
the intent file is a geometry input, not a measured gap and not a Gate C
result.
