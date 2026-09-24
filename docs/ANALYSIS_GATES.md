# Analysis gates

Round 1 stamps (2026-09-24): Researcher, Structures, and Systems Engineering
are a conditional pass. Inventor is a pass. Strategist is validate first.

Conditional pass means this vertical can be built only while the rows below
stay true. Validate first means a plotted number is not a result until the
validation row says so. The Week-1 dashboard starts with nulls on purpose.

| Gate | Week-1 state | What a later pass would require |
| --- | --- | --- |
| Scope freeze | Closed for Round 1 | A written change to `docs/ROUND1.md` if the vertical moves. |
| Export control | Watch | Case stays cold. `itar`, `hot_section`, and `part33` stay false. No restricted geometry in git. No request for OSC export-controlled hosting. |
| Geometry smoke | Local only | STL opens and the bounding cylinder matches the intent diameter. Still not a manufacturing model. |
| Fan surface | Not started | One closed CFD surface of the impeller and stator. The pure-Python STL does not qualify: blades intersect the hub and the shells are separate. |
| Volume mesh | Not started | A mesh of that surface, with a cell count and a wall-spacing note you are willing to defend. The rectangular `blockMesh` duct does not qualify. |
| Solver smoke | Not run | `simpleFoam` completes on the duct at OSC, log saved, and the dashboard still shows thrust as unset. |
| Fan physics | Blocked | A declared rotating model (MRF or AMI, or a later method) on the fan mesh. Inlet velocity of the duct skeleton is not this gate. |
| Validation | Blocked | Comparison to a published fan or to a bench test, with the discrepancy stated. Momentum-theory sketches in the case README are not validation. |
| Claim | Blocked | Thrust, efficiency, or noise may be quoted only after validation. Part 33 language stays unavailable. |

The intent loader enforces the export-control flags. It does not know whether
a mesh is good. A green Slurm job does not close the claim gate.

Structures and systems notes that are still open, and are why those stamps
are conditional:

- No stress model, no blade retention, no whirl or containment story.
- No mass, no motor, no electrical power budget tied to a real machine.
- The 1000 N figure is a market target. The 0.30 m / 12000 rpm set is a
  placeholder that the case README shows is a heavy disk loading.

Inventor pass covers the workflow shape (case library, runner, dashboard),
not a qualified fan design.
