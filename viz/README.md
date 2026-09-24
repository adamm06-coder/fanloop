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

Week 3 is when a real run is allowed to write a results file. Thrust stays
null until `docs/ANALYSIS_GATES.md` says a validation gate has passed. Do not
hand-edit a number into the placeholder to make the page look finished.
