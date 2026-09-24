# Gates — ducted-fan-1kn

This card is the gate list for the cold ~1 kN electric ducted fan.
[`docs/ANALYSIS_GATES.md`](../../docs/ANALYSIS_GATES.md) points here. The
dashboard uses these ids: A, B_lite, B, C1, C2, C3, D, E, F.

Round 1 stamps are in [`docs/ROUND1.md`](../../docs/ROUND1.md). Conditional
means the vertical may continue only while the colors below stay honest.
The Inventor pass covers the workflow shape. It does not turn any row green.

Colors are red, yellow, green, and unset. Green means the evidence in the
last column is in the repo. No row is green. Red is unused: work that has
not started is unset. Yellow is a partial the checkout can actually show.

## What the rows are for

| Use | Rows | Limit |
| --- | --- | --- |
| Demo | A and B_lite | B_lite stays labeled DEMO. Force integrals from a propeller or actuation-disk model stay under that label. |
| Hardware talk | A, B with a mesh study, C1, C2, C3, and E | Those rows are green together. D does not fill in for any of them. |

Gate F is how a later green row becomes something another person can
regenerate. The scripted local smoke path does not turn a plot into
hardware evidence.

Thrust, shaft power, efficiency, factor of safety, and tip gap stay unset
on the dashboard until the row allowed to produce them is green. The 1000 N
figure in `intent.yaml` is a target (`thrust_status:
target-only-not-a-result`). The momentum-theory sketch in the case README is
arithmetic on that target. It is not a B_lite force integral.

## Rows

| Gate | Asks | Week-1 color | What would have to be true |
| --- | --- | --- | --- |
| A Geometry | Parametric solid (CadQuery or Build123d) and an STL smoke check against the intent envelope. | Yellow | A CadQuery or Build123d solid of the impeller and stator, plus an STL whose bounding cylinder matches the intent diameter. Today the pure-Python STL does that diameter check locally. The plates intersect the hub and the shells are separate, so there is no closed CFD surface and no manufacturing model. |
| B_lite Aero, demo | OpenFOAM propeller or actuation disk, with force integrals, labeled DEMO. | Unset | A declared propeller or actuation-disk case, a saved log, and force integrals written down as DEMO. `solvers/openfoam` is a rectangular cold duct. It is not the impeller, and it has not been executed. A later `simpleFoam` run of that duct still leaves thrust unset. A B_lite plot does not pass Gate B and is not hardware talk. |
| B Aero | Blade-resolved flow and a mesh study. | Unset | One closed CFD surface of the impeller and stator. A volume mesh of that surface, with a cell count and a wall-spacing note. A declared rotating model (MRF or AMI) on that mesh. A mesh study. A comparison to a published fan or a bench test, with the discrepancy stated. The rectangular `blockMesh` duct does not qualify as this mesh or this physics. Thrust, efficiency, and noise stay unquoted until that comparison exists. Part 33 language stays unavailable. |
| C1 Structure, centrifugal | Blades and hub under centrifugal load. | Unset | A stress model with stated loads and restraints, and a factor of safety that comes from that model. No stress model is in the repo. Dashboard factor of safety stays null. |
| C2 Structure, torque | Torque path through the blades, hub, and shaft. | Unset | The same kind of model as C1, for torque. No blade-retention or torque-path model is in the repo. |
| C3 Structure, casing and mount | Duct, mounts, and the path into the vehicle. | Unset | A casing and mount model. None is in the repo. |
| D Thermo | Metal temperatures and hot-structure allowables. | Unset, N/A | The case is cold: `operating_point.thermal` is `cold` and `export_control.hot_section` is false. N/A means the row is not open. It is not a pass and it does not waive C or E. |
| E Materials | Allowables for a chosen alloy or composite, with a basis. | Unset | [`materials.yaml`](materials.yaml) names handbooks to open later. No alloy, temper, product form, or A/B/S basis is selected, and no handbook number is copied into git. |
| F Reproducibility | Someone else can regenerate the artifact from this repo. | Unset | Case, mesh, solver version, and the command that produced the number. The Week-1 smoke path is scripted, and there is no analysis number to regenerate. A green Slurm job does not close this row and does not authorize a thrust quote. |

## Week-1 reading

Gate A is the only yellow row.

The case scope stays the Round 1 freeze in
[`docs/ROUND1.md`](../../docs/ROUND1.md). Export control stays on the intent
file: `itar`, `hot_section`, and `part33` are false, and the loader rejects
a flip. Those checks are not additional gates.

Still open, which is why the structures stamp stays conditional: no whirl or
containment story, and no mass, motor, or electrical power budget tied to a
real machine. The 0.30 m / 12000 rpm set is the placeholder the case README
shows is a heavy disk loading.

Tip clearance in the intent file is a geometry input. It is not a measured
gap and not a Gate C result.
