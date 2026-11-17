# Trust but Verify: LLM-Assisted GIS Data QC

Working repository for a 30-minute talk for local-government GIS professionals,
and for the ArcGIS Pro demo that accompanies it. The core idea: an open-weight
LLM may *propose* parcel QC findings and fixes as structured JSON, but a
deterministic gate — spatial predicates, topology rules, schema constraints, and
a human reviewer — decides what is accepted. The model never writes to the
geodatabase.

## Repository layout

| Path | Contents |
|---|---|
| `presentation-topics.md` | Candidate talk topics, selected topic, source list, verification caveats |
| `analysis/` | ArcPy QC scripts and raw output; `QC_ASSESSMENT.md` summarizes the Iron County findings |
| `demo/` | ArcGIS Pro project scaffold and its geodatabases |
| `demo/GDBs/iron_county_parcels.gdb` | Iron County parcel extract used by the demo |
| `DATA_LICENSE.md` | Data source, CC BY 4.0 terms, attribution, and disclaimer |
| `LICENSE` | MIT license for the source code |

## Data

The demo uses **Utah Iron County Parcels LIR** from the Utah Geospatial Resource
Center (UGRC), formerly AGRC: 68,965 polygon features with county assessor and
tax-roll attributes. The extract's own `CURRENT_ASOF` value is 2024-07-18.

The data are licensed **CC BY 4.0**. Attribution:

> Data: Utah Iron County Parcels LIR, Utah Geospatial Resource Center (UGRC) /
> SGID, CC BY 4.0. Source data: Iron County, Utah. Accessed 2026-11-17.

See [`DATA_LICENSE.md`](DATA_LICENSE.md) for the full terms, the required
disclaimer, and change notes. The MIT license on this repository covers the code
only, not the data.

## QC analysis

`analysis/QC_ASSESSMENT.md` documents what the extract looks like: valid
geometry and complete county coverage, but a one-to-many parcel identity problem,
widespread duplicate footprints, and a 16.4% stated-acreage-versus-geometry
mismatch. The scripts reproduce those results.

They require ArcGIS Pro's Python environment and take the feature-class path as
their only argument:

```powershell
$py = "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
& $py analysis\inventory_gdb.py       "demo\GDBs\iron_county_parcels.gdb"
& $py analysis\profile_attributes.py "demo\GDBs\iron_county_parcels.gdb\Parcels_Iron_LIR"
& $py analysis\geometry_pass.py       "demo\GDBs\iron_county_parcels.gdb\Parcels_Iron_LIR"
& $py analysis\deep_dive.py           "demo\GDBs\iron_county_parcels.gdb\Parcels_Iron_LIR"
& $py analysis\topology_check.py      "demo\GDBs\iron_county_parcels.gdb\Parcels_Iron_LIR"
& $py analysis\final_checks.py        "demo\GDBs\iron_county_parcels.gdb\Parcels_Iron_LIR"
```

## Demo

The ArcGIS Pro project is `demo/Pro Projects/demo.aprx`. The parcel feature class
is `demo/GDBs/iron_county_parcels.gdb/Parcels_Iron_LIR`.

## License

- **Code:** MIT — see [`LICENSE`](LICENSE).
- **Data:** CC BY 4.0 — see [`DATA_LICENSE.md`](DATA_LICENSE.md).
