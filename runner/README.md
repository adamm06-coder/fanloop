# Runner

Local commands only. This package does not SSH, does not call `sbatch`, and
does not store an OSC project code.

```bash
python -m runner list
python -m runner package ducted-fan-1kn
OSC_PROJECT=your_code python -m runner render-sbatch \
  --job runner/jobs/ducted-fan-1kn.yaml \
  -o /tmp/fanloop-1kn.sbatch
```

`package` writes `dist/<case>.tar.gz` with the intent, the case README, and a
copy of `solvers/openfoam`. The manifest says `contains_credentials: false`.

`render-sbatch` reads `OSC_PROJECT` from the environment. If it is unset, or
if it is one of the sample codes from OSC's own documentation (`pas1234`,
`pas4321`), the command exits 2 and writes nothing. Rendered scripts go
outside the repo or under `dist/` (gitignored). `*.sbatch` is gitignored
because the file contains the project code.

The job YAML allows `openfoam/2606` and a serial `simpleFoam` only. Parallel
launch is refused so the template cannot invent an MPI line. OSC's OpenFOAM
page still shows `openfoam/5.0` examples; the rendered script tells you to
run `module show openfoam/2606` on the cluster.

See `docs/OSC_SETUP.md` before submitting anything.
