# Cold internal-flow skeleton

Steady incompressible flow in a straight rectangular duct, solved with
`simpleFoam` if OpenFOAM is on the machine. Dimensions are 0.08 m × 0.08 m ×
0.22 m, on the same length scale as `cases/ducted-fan-1kn` and not the fan
passage.

| File | Role |
| --- | --- |
| `system/blockMeshDict` | The only mesh. Hexahedral duct. |
| `system/controlDict` | 50 iterations or the residual control in `fvSolution`, whichever stops first. |
| `0/U` | 5 m/s in +z. A placeholder, not the RPM in the intent file. |
| `0/p` | Kinematic pressure, p/ρ, in m²/s². Not pascals. |
| `constant/transportProperties` | Newtonian air, ν = 1.5×10⁻⁵ m²/s. |
| `constant/physicalProperties` | Same ν, for OpenFOAM.com builds that read this name. |
| `constant/turbulenceProperties` | k–ω SST. |
| `system/decomposeParDict` | Unused by the Week-1 serial script. |

`Allrun` calls `blockMesh` then `simpleFoam` and exits if those commands are
not on `PATH`. It does not source a guessed OpenFOAM `bashrc`.

```bash
module load openfoam/2606   # on OSC; confirm with module show
module show openfoam/2606
./Allrun
```

OSC's software page still documents older `openfoam/5.0` batch examples and
draws `blockMeshDict` under `constant/polyMesh`. This case uses the current
layout: `blockMeshDict` lives in `system/`. If `simpleFoam` rejects a scheme
or a boundary condition, fix that on the cluster and record the OpenFOAM
banner. A failed or converged duct run is still not a thrust number.

The inlet turbulence values (k ≈ 0.094 m²/s², ω ≈ 100 1/s) match a 5 m/s
inlet, 5% intensity, and a mixing length of about 0.07 × 0.08 m. They are
not measurements.

This skeleton has not been executed in the Week-1 scaffold. Do not describe
it as a run that already happened.
