# OSC setup

FanLoop renders a Slurm script. You submit it. The repo never logs in, never
stores a project code, and never calls `sbatch`.

Checked against OSC's public pages on 2026-09-24. Re-check them before
spending money or submitting a job. Module names and prices move.

## Account

Industry clients: OSC lists a startup package at $500 that includes the
annual maintenance fee for the initial project, $250 of credit, basic
support, and home-directory storage. Open-source software already on the
system has no extra license fee. Commercial licenses are your responsibility.
Export-controlled hosting is a separate service. Year-1 FanLoop does not
request it. Stay on the ordinary project with cold, EAR99-like cases.

- Industry packages: <https://www.osc.edu/industry>
- Start an industry account: <https://www.osc.edu/supercomputing/accounts/bcc_account>
- Client portal: <https://my.osc.edu>
- OnDemand: <https://ondemand.osc.edu>

You need a user and a project before any job will queue. On a login node,
`OSCfinger` prints `SLURM Accounts`. That value is `OSC_PROJECT`. Keep it in
your shell, not in a file in this repo.

OSC's job-script page shows account codes `pas1234` and `pas4321` as
examples. The renderer rejects those strings so a copied example cannot
become a job. Job names are limited to 15 characters on that same page;
`fanloop-1kn` fits.

## Where to log in

OnDemand is the straightforward path: <https://ondemand.osc.edu>, then
Clusters, then a shell.

SSH hosts published in the new-user guide:

- `cardinal.osc.edu`
- `pitzer.osc.edu`

Use the Ascend shell inside OnDemand unless you have confirmed the Ascend
SSH hostname yourself. The Week-1 job YAML targets Cardinal. Change
`cluster` in `runner/jobs/ducted-fan-1kn.yaml` if you submit elsewhere.
The rendered script does not pass `--cluster`; you submit from that
cluster's login node.

## OpenFOAM

OSC's changelog for 2026-07-28 says OpenFOAM 2606 is available on Cardinal,
Pitzer, and Ascend, loaded with:

```bash
module load openfoam/2606
module show openfoam/2606
```

The software list, still updated in September 2026, shows 2312, 2412
(Cardinal only), and 2606. The batch examples on that page still load
`openfoam/5.0` and, in one script, mention the retired Ruby cluster. Do not
copy those examples. Version numbers 2312 / 2412 / 2606 match the
OpenFOAM.com release calendar. The page's vendor line says OpenFOAM
Foundation. Trust `module show` on the cluster over either sentence.

- Changelog: <https://www.osc.edu/resources/technical_support/hpc_changelog/2026/openfoam_2606_available_on_cardinal_pitzer_ascend>
- Software page: <https://www.osc.edu/resources/available_software/software_list/openfoam>
- Job scripts: <https://www.osc.edu/supercomputing/batch-processing-at-osc/job-scripts>

SU2 is not assumed. Run `module spider su2`. If nothing is there, the
alternate solver in the intent file stays a note.

## Week-2 submit, after the local smoke

From a checkout on OSC (home or project space, not a laptop path):

```bash
module load openfoam/2606
module show openfoam/2606
export OSC_PROJECT=the_code_from_OSCfinger
python -m runner render-sbatch \
  --job runner/jobs/ducted-fan-1kn.yaml \
  -o "$TMPDIR/fanloop-1kn.sbatch"
# read the script, then:
sbatch "$TMPDIR/fanloop-1kn.sbatch"
```

The script runs `blockMesh` and `simpleFoam` in `solvers/openfoam`. That is
a cold rectangular duct. Copy the Slurm log back if you want a record. Do
not write a thrust into `viz/data`. A duct residual is not fan performance.

`Allrun` in the case directory does the same two commands without Slurm, for
an interactive session. It exits if `blockMesh` is not on `PATH`.

## What not to put on OSC for this project in year 1

- ITAR geometry or a request for export-controlled hosting
- Ansys or other commercial CFD, unless you already hold the license and
  have a reason that is outside this repo's year-1 scope
- A job that claims Part 33 credit
