# Geometry

`ducted_fan.py` reads a case `intent.yaml` and writes an ASCII STL.

```bash
python -m geom.ducted_fan cases/ducted-fan-1kn/intent.yaml \
  -o /tmp/fanloop-ducted-fan.stl --backend pure
```

## What the STL is

A faceted duct, a hub with a short nose, and thin staggered plates for the
rotor and stator. Blade count, diameter, and hub ratio come from the YAML.
The plates intersect the hub. The bodies are separate shells.

That is enough to open in a mesh viewer and see a ducted-fan-shaped solid.
It is not a manufacturing model, not a watertight CFD surface, and not a
volume mesh. `mesh/` only inspects the STL.

## Backends

| Backend | When |
| --- | --- |
| `pure` | Always available. This is the Week-1 path. |
| `cadquery` | Optional. Not imported unless you ask for it or `auto` finds it. |
| `auto` | CadQuery if `import cadquery` works, otherwise pure. |

CadQuery is the intended parametric spine, with Build123d as a later
alternative in the same Python family. The Week-1 checkout does not require
it, because the OpenCascade wheel is large and easy to fail in a fresh
environment.

```bash
pip install -e ".[cadquery]"
python -m geom.ducted_fan cases/ducted-fan-1kn/intent.yaml \
  -o /tmp/fanloop-ducted-fan.stl --backend cadquery
```

The CadQuery exporter is best-effort and is not part of the Week-1 smoke
test. If it fails, use `--backend pure` and treat that STL as the artifact.

PicoGK is out of scope here. The maintained PicoGK API is C#. Fusion is for
inspection only and is not on the path that produces an OSC case.
