window.FANLOOP_RESULTS = {
  "schema": "fanloop.results/v0",
  "case": "ducted-fan-1kn",
  "status": "not_run",
  "generated_by": "week-1 scaffold",
  "disclaimer": "Placeholder. No solver has been run. Nulls are unset, not zero. Do not quote thrust, efficiency, or noise from this file.",
  "quantities": [
    {
      "id": "thrust_N",
      "label": "Thrust",
      "value": null,
      "unit": "N",
      "state": "unset"
    },
    {
      "id": "pressure_rise_Pa",
      "label": "Pressure rise",
      "value": null,
      "unit": "Pa",
      "state": "unset"
    },
    {
      "id": "mass_flow_kg_s",
      "label": "Mass flow",
      "value": null,
      "unit": "kg/s",
      "state": "unset"
    },
    {
      "id": "shaft_power_W",
      "label": "Shaft power",
      "value": null,
      "unit": "W",
      "state": "unset"
    }
  ],
  "gates": [
    {
      "id": "export_control",
      "label": "Export control",
      "state": "watch",
      "note": "Cold-fan intent only. No ITAR geometry in this repo."
    },
    {
      "id": "geometry_smoke",
      "label": "Geometry smoke",
      "state": "local",
      "note": "STL export is a visual solid, not a CFD surface."
    },
    {
      "id": "mesh",
      "label": "Volume mesh",
      "state": "not_started",
      "note": "No fan mesh yet. The OpenFOAM skeleton uses blockMesh on a rectangular duct."
    },
    {
      "id": "solver",
      "label": "Solver",
      "state": "not_run",
      "note": "simpleFoam has not been executed."
    },
    {
      "id": "validation",
      "label": "Validation",
      "state": "blocked",
      "note": "No bench test and no published comparison."
    }
  ]
};
