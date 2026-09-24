window.FANLOOP_RESULTS = {
  "schema": "fanloop.results/v0",
  "case": "ducted-fan-1kn",
  "status": "not_run",
  "generated_by": "week-1 scaffold",
  "disclaimer": "Placeholder. No solver has been run. Nulls are unset, not zero. Do not quote thrust, power, efficiency, factor of safety, or tip gap from this file.",
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
    },
    {
      "id": "efficiency",
      "label": "Efficiency (η)",
      "value": null,
      "unit": "",
      "state": "unset"
    },
    {
      "id": "factor_of_safety",
      "label": "Factor of safety",
      "value": null,
      "unit": "",
      "state": "unset"
    },
    {
      "id": "tip_gap_m",
      "label": "Tip gap",
      "value": null,
      "unit": "m",
      "state": "unset"
    }
  ],
  "gates": [
    {
      "id": "A",
      "label": "A Geometry",
      "ryg": "yellow",
      "note": "Partial. Local STL smoke matches the intent diameter. CadQuery/Build123d was not run. Shells are separate, so this is not a CFD surface."
    },
    {
      "id": "B_lite",
      "label": "B_lite Aero demo",
      "ryg": "unset",
      "note": "DEMO only, and not run. The OpenFOAM case is a rectangular duct, not the impeller. A duct run would leave thrust unset and would not pass Gate B."
    },
    {
      "id": "B",
      "label": "B Aero",
      "ryg": "unset",
      "note": "Blade-resolved aero and a mesh study are not started."
    },
    {
      "id": "C1",
      "label": "C1 Centrifugal",
      "ryg": "unset",
      "note": "No centrifugal stress model. Factor of safety stays null."
    },
    {
      "id": "C2",
      "label": "C2 Torque",
      "ryg": "unset",
      "note": "No torque-path model."
    },
    {
      "id": "C3",
      "label": "C3 Casing and mount",
      "ryg": "unset",
      "note": "No casing or mount model."
    },
    {
      "id": "D",
      "label": "D Thermo",
      "ryg": "unset",
      "note": "N/A. The case is cold. N/A is not a pass."
    },
    {
      "id": "E",
      "label": "E Materials",
      "ryg": "unset",
      "note": "materials.yaml names handbooks only. No alloy and no copied allowable."
    },
    {
      "id": "F",
      "label": "F Reproducibility",
      "ryg": "unset",
      "note": "The local smoke path is scripted. No analysis result exists to regenerate."
    }
  ]
};
