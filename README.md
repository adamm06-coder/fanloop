# FanLoop

FanLoop is a capital-light computational-engineering workflow for a founder
in Dayton / Beavercreek. It is a case library, a job runner for the Ohio
Supercomputer Center, and a results dashboard. It is not a jet-engine
company, and this repository does not design one.

The frozen first vertical (Round 1, 2026-09-24) is a **cold, about 1 kN,
electric ducted fan**: one impeller and one stator. The year-1 path is UAS,
experimental, R&D, and AFWERX SBIR-shaped work. It is not FAA Part 33. Cases
stay EAR99-like cold fans. The freeze, the stamps, and the refusal list are
in [`docs/ROUND1.md`](docs/ROUND1.md).

```
intent YAML → parametric geometry → mesh → OSC Slurm → results dashboard
```

Week 1 implements the ends of that line and is explicit about the middle.
Geometry export and the dashboard run locally. The mesh of the fan does not
exist yet. The OpenFOAM directory is a cold rectangular duct, not the
impeller. The runner writes a Slurm script and does not submit it.

## Four weeks

| Week | Outcome | You are done when |
| --- | --- | --- |
| 1 | Local smoke | The commands below produce an STL, a tarball, a refused-or-rendered sbatch, and a dashboard of nulls. |
| 2 | One OSC case | A real project code, `module load openfoam/2606`, and `simpleFoam` on the cold duct. Thrust in the dashboard stays null. |
| 3 | Sweep and dashboard | A declared parameter sweep writes a results JSON the page reads. Thrust stays null until Gate B on the case card allows a quoted result. |
| 4 | Vertical polish | The impeller-plus-stator geometry and the chosen mesher are written down against [`cases/ducted-fan-1kn/GATES.md`](cases/ducted-fan-1kn/GATES.md). Still no Part 33 claim and no quoted thrust. |

## Layout

| Path | What it is |
| --- | --- |
| `cases/ducted-fan-1kn/` | The only case. Intent YAML, the structures gate card, a Gate E materials stub, and a README that says the 1000 N figure is a target. |
| `geom/` | STL export. Pure Python by default. CadQuery optional. |
| `mesh/` | ASCII-STL inspection. Not a volume mesher. |
| `solvers/openfoam/` | `blockMesh` + `simpleFoam` skeleton for a cold duct. |
| `runner/` | `list`, `package`, `render-sbatch`. |
| `viz/` | Static page over placeholder JSON. |
| `docs/` | Round 1 freeze, OSC setup, analysis gates. |

## Local smoke

Requires Python 3.11 or newer. From a fresh clone:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

python -m geom.ducted_fan cases/ducted-fan-1kn/intent.yaml \
  -o /tmp/fanloop-ducted-fan.stl --backend pure
python -m mesh.inspect_stl /tmp/fanloop-ducted-fan.stl
python -m runner list
python -m runner package ducted-fan-1kn
python -m unittest discover -s tests -v
```

`package` writes `dist/ducted-fan-1kn.tar.gz`. That directory is gitignored.
The STL is a visual solid (duct, hub, blades, stators). It is not a
watertight CFD surface. Details are in [`geom/README.md`](geom/README.md).

Rendering a batch script needs your OSC project code in the environment.
Without it, the command exits 2 and writes nothing:

```bash
python -m runner render-sbatch \
  --job runner/jobs/ducted-fan-1kn.yaml \
  -o /tmp/fanloop-1kn.sbatch
```

With a real code from `OSCfinger` (never one of OSC's sample codes, and
never committed):

```bash
export OSC_PROJECT=the_code_from_OSCfinger
python -m runner render-sbatch \
  --job runner/jobs/ducted-fan-1kn.yaml \
  -o /tmp/fanloop-1kn.sbatch
```

The dashboard, served so it can fetch the JSON:

```bash
cd viz && python -m http.server 8765
```

Open `http://127.0.0.1:8765/`. Opening `viz/index.html` as a file also works;
it falls back to the same object in `viz/data/results.placeholder.js`.
Every performance value is null.

## OSC path

Week 1 stops at the rendered script. Week 2 is the first submit.
[`docs/OSC_SETUP.md`](docs/OSC_SETUP.md) has the account, the clusters, and
the module command.

Public OSC pages, as checked for this scaffold:

- Industry startup package listed at $500: <https://www.osc.edu/industry>
- OnDemand: <https://ondemand.osc.edu>
- `module load openfoam/2606` on Cardinal, Pitzer, and Ascend
  (changelog 2026-07-28)

The OpenFOAM software page still shows `openfoam/5.0` batch examples. Do not
copy them. Run `module show openfoam/2606` on the cluster. SU2 is used only
if `module spider su2` finds it. This repo does not ship a SU2 deck.

There is no Ansys path in year 1.

## Geometry stack

CadQuery (or Build123d, same Python family) is the parametric spine. Install
it with `pip install -e ".[cadquery]"` when you want that backend. The wheel
is large; the pure-Python exporter exists so Week 1 does not depend on it.
PicoGK can wait, and its maintained API is C#. Fusion is for looking at a
model, not for producing the case that goes to OSC.

## What this repo will not do in year 1

Ansys wrappers. A clone of a commercial fan-design product. Hot combustor
CFD. Part 33 certification work. ITAR geometry. Secrets or OSC project codes
in git. A thrust number that did not pass the gates in
[`cases/ducted-fan-1kn/GATES.md`](cases/ducted-fan-1kn/GATES.md).

NASA-released tools such as OpenVSP are a possible later geometry check.
They are not the Week-1 spine. FanLoop is not a NASA project, not an OSC
product, and not an AFRL or AFWERX program. Dayton / Beavercreek is where
the work is based. OSC in Columbus is the machine.

## License

Apache-2.0. See [LICENSE](LICENSE).
