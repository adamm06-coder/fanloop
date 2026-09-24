# Results page

`index.html` is a static Week-1 dashboard. It shows the placeholder in
`data/results.placeholder.json`. Every performance number in that file is
`null`. Null means unset, not zero.

Opening the file directly still works: the page falls back to
`data/results.placeholder.js`, which carries the same object. A test checks
that the two files match. When you serve the directory, the page fetches the
JSON instead:

```bash
cd viz
python -m http.server 8765
```

Then open `http://127.0.0.1:8765/`.

The page also renders the structures gate card (A, B_lite, B, C1, C2, C3, D,
E, F) from `structures_gates` in that same file. Each row is red, yellow,
green, or unset. Week 1 marks geometry yellow because the local STL smoke
exists and is only a visual solid. The other rows stay unset. Green is
unused. The words for those rows live in `cases/ducted-fan-1kn/GATES.md`.

Week 3 is when a real run is allowed to write a results file. Thrust, shaft
power, efficiency, factor of safety, and tip gap stay null until a gate that
is allowed to produce them has passed. Do not hand-edit a number into the
placeholder to make the page look finished.
