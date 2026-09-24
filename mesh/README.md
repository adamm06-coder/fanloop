# Mesh

Week 1 does not mesh the fan.

`inspect_stl.py` reads an ASCII STL and prints triangle count, bounding box,
and max radius. That is a file check, not a mesh-quality check. There is no
y+, no cell count in the fan passage, and no claim the surface is closed.

```bash
python -m mesh.inspect_stl /tmp/fanloop-ducted-fan.stl
```

The only volume mesh in the repo is `solvers/openfoam/system/blockMeshDict`:
a rectangular duct used as a cold-flow smoke case. It does not use the STL.

A later week picks one mesher after the geometry is a single CFD surface.
Candidates are snappyHexMesh, cfMesh, or Gmsh. None of those are wired up yet.
Do not convert the pure-Python STL and call the result a fan mesh: the blades
intersect the hub and the shells are separate.
