# Solvers

| Path | Status |
| --- | --- |
| `openfoam/` | Cold rectangular-duct `simpleFoam` skeleton. Not a fan. |
| SU2 | Not vendored. Use it only if `module spider su2` shows a module on OSC. |

Week 1 ships one OpenFOAM case so a later OSC job has a real directory to
`cd` into. It does not ship a rotating-frame (MRF or AMI) setup, a sliding
interface, or a force report.

Ansys wrappers are out of scope for year 1.
