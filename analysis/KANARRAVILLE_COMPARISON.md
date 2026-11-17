# Kanarraville Subset vs. Countywide Parcel Layer

**Subset:** `demo.gdb/Kanarraville_Parcels` — 508 polygons (rebuilt)
**County layer:** `iron_county_parcels.gdb/Parcels_Iron_LIR` — 68,965 polygons
**Same snapshot:** `CURRENT_ASOF` = 2024-07-18

---

## The rebuilt subset now matches the attribute population exactly

| | Count |
|---|---|
| Rows with `PARCEL_CITY = 'Kanarraville'` in the county layer | **508** |
| Rows in `Kanarraville_Parcels` | **508** |
| City-attributed rows missing from the subset | **0** |
| Subset rows not attributed to Kanarraville | **0** |

A row-for-row comparison on `(PARCEL_ID, geometry)` found **zero differences**
between the subset and the 508 city-attributed rows in the county layer. The
boundary relationship also matches exactly: 474 parcels fully inside the
municipal boundary and 34 partially intersecting it, in both sets.

This is the correct "all Kanarraville parcels" definition. It replaces the
earlier 475-row centroid-based selection, which omitted 33 boundary-straddling
parcels.

### What the 33 added parcels changed

| Metric | First subset (475) | Rebuilt subset (508) |
|---|---|---|
| Rows | 475 | 508 |
| Boundary relationship | 474 within, 1 partial | 474 within, 34 partial |
| Rows in duplicate-ID groups | 342 (72.0%) | 362 (71.3%) |
| Rows sharing identical geometry | 338 (71.2%) | 354 (69.7%) |
| Blank `PARCEL_ID` | 5 | 9 |
| Rows with no assessor attributes | 8 | 12 |
| Building data present | 85.1% | 83.7% |
| Address present | 80.6% | 79.3% |
| Acreage within 10% of geometry | 91.6% | 90.5% |
| Acreage within 25% | 96.8% | 95.8% |
| Acreage >25% off | 3.2% | 4.2% |
| Property classes | 9 | 9 |
| `TAX_DISTRICT` values | 1 (`03`) | 2 (`03`, `10`) |
| Subdivision names | 26 | 27 |

The added boundary parcels are slightly less attributed: 21 of 34 have building
data, 4 of 34 have blank IDs, and 4 of 34 have no assessor attributes. That
accounts for the small drop in completeness and the new blank-ID rows.

---

## Head-to-head metrics

| Metric | Countywide | Kanarraville (508) |
|---|---|---|
| Rows | 68,965 | 508 |
| Invalid / null / zero-area geometry | 0 | 0 |
| Slivers < 1 m² | 67 | 0 |
| Multipart features | 113 | 0 |
| Cross-parcel overlaps (different IDs) | 168 | **0** |
| Identical-geometry overlap findings | 31,818 | 378 |
| Rows with duplicated `PARCEL_ID` | 28,038 (40.7%) | 362 (**71.3%**) |
| Rows with duplicated geometry | 19,968 (29.0%) | 354 (**69.7%**) |
| Blank `PARCEL_ID` | 1,517 (2.2%) | 9 (1.8%) |
| Sentinel `9999999` IDs | 532 | 0 |
| Rows with no assessor attributes | 3,259 (4.7%) | 12 (2.4%) |
| Building data present | 48.0% | **83.7%** |
| Address present | 49.8% | **79.3%** |
| Median `PARCEL_ACRES` | 0.78 | 0.46 |
| Acreage within 10% of equal-area geometry | 79.5% | **90.5%** |
| Acreage within 25% | 83.6% | **95.8%** |
| Acreage >25% off (≥0.05 acre) | 16.4% | **4.2%** |
| Property classes | 14 | 9 (89.2% Residential) |

---

## Why the duplicate rate is higher here — and why it is not an error

The 362 duplicated-ID rows are not failed deduplication. They are a
one-parcel-to-many-buildings data model.

Example: `A-0646-0001-0000` at **280 S MAIN ST** has 7 rows sharing the same
parcel ID, serial number, geometry, acreage, total market value, land value, and
`HOUSE_CNT = 7`. What differs is the per-building detail:

| `BLDG_SQFT` | `BUILT_YR` |
|---|---|
| 1,322 | 1970 |
| 576 | 1996 |
| 64 | 1970 |
| 320 | 1970 |
| 96 | 1970 |
| 1,120 | 2013 |
| 1,283 | 1996 |

Across the 129 duplicate-ID groups, `BLDG_SQFT` varies in 126 groups,
`CONST_MATERIAL` in 126, `EFFBUILT_YR` in 120, and `BUILT_YR` in 78. Parcel-level
fields (`TOTAL_MKT_VALUE`, `LAND_MKT_VALUE`, `HOUSE_CNT`) stay constant.

**Demo consequence:** deleting or merging "duplicate" rows would destroy real
units. This is the best "the model proposes, the gate rejects" case in the
dataset.

---

## New edge cases introduced by the boundary parcels

The 33 added parcels are useful demo material because they expose the limits of
row-level validation:

1. **Four new blank-ID parcels.** The subset now has 9 blank IDs, all with every
   attribute null. Four of them are boundary-straddling parcels.
2. **One different tax district.** `E-0337-0002-00R1` is the only parcel in tax
   district `10`; it is a Greenbelt parcel, partially inside the boundary, with
   **10.11 stated acres versus 0.885 mapped acres** (11.4× overstatement). This is
   a genuine single-feature outlier, not a multipart artifact.
3. **Multipart parcels at the edge.** Four duplicate-ID groups contain more than
   one geometry:

   | Parcel ID | Rows | Unique geoms | Stated acres | Unique geometry acres |
   |---|---|---|---|---|
   | `A-0640-0002-0000` | 2 | 2 | 1.800 | 1.533 |
   | `A-0647-0647-000N` | 6 | 2 | 0.475 | 0.966 |
   | `A-0714-0000-0000` | 3 | 3 | 4.700 | 4.560 |
   | `A-0714-0001-0000` | 3 | 3 | 15.547 | 13.521 |

   The `A-0714` pairs are multipart parcels: evaluated row by row, one part
   looks **90.5×** too small, but the dissolved parcel is 4.56 acres versus 4.70
   stated. The `A-0647` group is different: it contains two nearly identical
   geometries (0.483476 and 0.482880 acres), each repeated three times, so the
   unique-geometry sum double-counts and looks like a 2× error. That group needs
   near-duplicate detection, not a simple dissolve.
4. **A new subdivision block.** `KANARRA TOWN SURVEY BLK 26` appears with 4
   parcels; all subdivision names remain clean and consistently formatted.

### Row-level vs. parcel-level acreage

| Level | n | Within 10% | Within 25% | >25% off |
|---|---|---|---|---|
| Row level | 496 rows | 90.5% | 95.8% | 4.2% |
| Parcel level (dissolve unique geometries by `PARCEL_ID`) | 263 parcels | 89.0% | 95.4% | 4.6% |

The headline 90.5× row-level outlier disappears when the multipart parcel is
dissolved. The genuine worst parcel-level case is `E-0337-0002-00R1` at 11.4×.
This is a key design lesson: **validate at the parcel level, not the row level,
and handle near-duplicate geometries separately.**

---

## What is genuinely cleaner in Kanarraville

- Geometry is pristine: no invalid features, no slivers, no multipart polygons.
- Topology is clean: **zero** overlaps between different parcels. All 378 overlap
  findings are the same footprint counted twice.
- Acreage is much more trustworthy than countywide: 90.5% within 10% at row level
  and 89.0% at parcel level, versus 79.5% countywide.
- Attributes are much more complete: 83.7% building data and 79.3% addresses,
  versus roughly half countywide.
- Identifiers are cleaner: no `9999999` placeholders, only 9 blanks and 3 legacy
  7-digit IDs, and 12 rows with no assessor attributes.
- Subdivisions are uniform: 27 values, all `KANARRA TOWN SURVEY BLK nn`,
  `KANARRA FIELDS SUBDIVISION`, or similarly clean names.

## What is the same as the countywide setup

- **Web Mercator storage.** Native CRS is EPSG:3857; area is 1.593× the
  equal-area value (+59.3%). `Shape_Area` remains unusable for acreage.
- **`EFFBUILT_YR` is still an age, not a year.** Range 1–97, median 19.
- **Dead fields remain:** `BLDG_SQFT_INFO` 100% null, `TAXEXEMPT_TYPE` = `Unknown`,
  `FLOORS_INFO` a single value.
- **No domains, subtypes, or attribute rules.**
- **Snapshot is still 2024-07-18.**

---

## What this means for the demo

1. **Use the 508-row subset.** It is exactly the attribute population and is
   still small enough to demo quickly.
2. **Gate at the parcel level.** Dissolve unique geometries by `PARCEL_ID` before
   comparing stated acreage; otherwise multipart parcels produce false 90×
   errors. Add a near-duplicate geometry check for cases like `A-0647`.
3. **Keep the multi-unit group as the money shot.** Prompt the LLM to find
   duplicate parcels; it will propose deleting or merging the 7 rows at
   280 S MAIN ST. The gate rejects the fix because the rows represent distinct
   buildings/units.
4. **Add a second rejection beat.** Have the LLM propose "fixing"
   `A-0714-0000-0000` by changing its acreage to match the 0.052-acre part. The
   gate rejects because the parcel's three parts dissolve to 4.56 acres versus
   4.70 stated — the row is not the unit of analysis.
5. **Keep the Web Mercator area check.** It still produces a clean rejection
   (area +59.3%), even though Kanarraville's native acreage values are otherwise
   good.
6. **Boundary cases are realistic.** Nine blank IDs, one tax-district outlier,
   and 34 partial parcels give the talk honest edge cases without fabricating
   them.

---

## Reproduce

```powershell
$py = "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
& $py analysis\profile_attributes.py "demo\GDBs\demo.gdb\Kanarraville_Parcels"
& $py analysis\geometry_pass.py       "demo\GDBs\demo.gdb\Kanarraville_Parcels"
& $py analysis\deep_dive.py           "demo\GDBs\demo.gdb\Kanarraville_Parcels"
& $py analysis\topology_check.py      "demo\GDBs\demo.gdb\Kanarraville_Parcels"
& $py analysis\compare_kanarraville.py
& $py analysis\kanarraville508_details.py
```
