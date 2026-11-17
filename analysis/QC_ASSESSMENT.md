# Iron County Parcel Data — QC Assessment

**Dataset:** `iron_county_parcels.gdb / Parcels_Iron_LIR`
**Rows:** 68,965 polygons · 29 fields · no domains, subtypes, or attribute rules
**Native CRS:** WGS 1984 Web Mercator Auxiliary Sphere (EPSG:3857)
**Snapshot:** `CURRENT_ASOF` = 2024-07-18 (single value for every row)
**Source:** Iron County, Utah — assessor/recorder URLs in the attributes

---

## Verdict

This is a **typical-to-good public parcel extract**: geometrically sound and
textually standardized, but **not a one-row-per-parcel dataset**. The dominant
problem is parcel identity and record-level duplication, not bad geometry. For
a QC demonstration it is excellent material; for production analysis it needs
an identity/dedup layer first.

My read: **B- overall**, with geometry much stronger than the identifier and
acreage dimensions.

---

## Scorecard

| Dimension | Finding | My read |
|---|---|---|
| Geometry validity | 0 null, 0 invalid (CheckGeometry), 0 zero-area; 67 slivers <1 m² | Strong |
| Coverage / topology | Unique footprint area 8,534.7 km² vs county ~8,552 km²; only ~658 genuine overlap findings after removing identical-geometry pairs | Strong |
| Coordinate system / measurement | Native CRS is Web Mercator; `SHAPE_Area` is **60.1% inflated** vs equal-area | Poor for analysis |
| Parcel identity | 49,597 distinct IDs for 68,965 rows; 40.7% of rows share an ID; 3.0% have no usable ID | Weak |
| Attribute completeness | 50.2% no address, 52.0% no building data (partly legitimate vacancy); 4.7% no assessor attributes | Moderate |
| Cross-field consistency | 16.4% of parcels have stated acreage >25% off mapped area; 188 `PRIMARY_RES=Y` without building data | Moderate |
| Schema / metadata | No domains or rules; 3 dead fields; `EFFBUILT_YR` is an age, not a year; snapshot 2.3 years old | Weak |
| Text normalization | Uniform uppercase; zero case/whitespace variants in city, subdivision, construction material | Strong |

---

## What is clean

- **Geometry is valid.** `CheckGeometry` found 0 problems across 68,965 polygons.
  No null, empty, or zero-area geometries. 113 multipart features, longest
  2,863 vertices — all normal.
- **Coverage is essentially complete.** After collapsing identical geometries,
  the polygons total 8,534.7 km², very close to Iron County's ~8,552 km² land area.
- **Real topology errors are rare.** Of 32,476 "Must Not Overlap" findings,
  31,818 (98.0%) are the *same geometry counted twice*. Only 168 are overlaps
  between genuinely different parcels; 21 are same-parcel overlaps; 469 involve
  unattributed polygons.
- **Text is standardized.** `PARCEL_CITY` contains exactly the six incorporated
  cities (Cedar City, Enoch, Parowan, Brian Head, Paragonah, Kanarraville) plus
  blank for unincorporated areas. No case, whitespace, or punctuation variants
  in city, subdivision, or construction-material values.
- **Assessor coding is coherent where present.** `PROP_CLASS` has 14 sensible
  categories; `CONST_MATERIAL` has a structured 39-value taxonomy;
  `PRIMARY_RES` is a clean Y/N; no negative or zero market values.

## What is not clean

1. **Parcel identity is one-to-many.** 10,186 `PARCEL_ID` values appear on more
   than one row (28,038 rows, 40.7%). The largest groups:
   - `9999999` — 532 rows, no attributes (placeholder ID).
   - `E-1229-0000-0000` — 523 rows, 522 distinct geometries, all attributed as
     the same 74.863-acre residential parcel.
   - `C-0060-0001-0000` — 137 rows, same attributes, 137 geometries.
   This is partly legitimate (multipart parcels and condo units), but it means
   naive joins on `PARCEL_ID` multiply records and spatial sums double-count.

2. **29% of rows share an exact footprint with another row.** 19,968 rows across
   7,871 duplicated geometries; the largest footprint is repeated 69 times.
   - 281 groups / 1,796 rows: different parcel IDs sharing a footprint — mostly
     `Commercial - Apartment & Condo`, which is expected for condos.
   - 7,590 groups / 18,172 rows: same parcel ID, repeated geometry with differing
     attribute rows — multiple assessment records on one footprint.

3. **Stated acreage disagrees with mapped area for 16.4% of parcels.**
   Comparing `PARCEL_ACRES` to equal-area (EPSG:5070) geometry for parcels
   ≥0.05 acre (n=61,397): 79.5% within 10%, 83.6% within 25%, 16.4% worse than
   25%. Overstatements dominate: 1,082 parcels state >100× their mapped area,
   1,707 state 10–100×, 4,252 state 2–10×. Some are parent/child or multipart
   artifacts; some are real. This is the richest deterministic-gate material in
   the dataset.

4. **`SHAPE_Area` is unusable as-is.** The layer is stored in Web Mercator, so
   its area field is 1.601× the equal-area value at this latitude (+60.1%).
   `PARCEL_ACRES` itself is mostly geodesic-correct (median ratio 1.000), but
   anyone computing area from the native geometry will overstate by ~60%.

5. **3.0% of features cannot be identified or attributed.**
   - 1,517 blank `PARCEL_ID`, every attribute null (2.2%); 1,477 of their
     geometries are unique to these rows.
   - 532 rows with literal ID `9999999`, no attributes.
   - 16 all-zero IDs; 1,133 other bare 7-digit numeric IDs (legacy format).
   - 3,259 rows (4.7%) have no assessor attributes at all.

6. **Dead or misleading schema.**
   - `BLDG_SQFT_INFO`: 100% null.
   - `TAXEXEMPT_TYPE`: single value `Unknown` on all 65,706 non-null rows.
   - `FLOORS_INFO`: single value on all rows.
   - `EFFBUILT_YR` ("Effective Year Built"): values 1–124, median 15; 100% below
     1980. It is an **effective age in years**, not a year.
   - No domains, subtypes, or attribute rules — nothing stops a bad code from
     being written.
   - `CURRENT_ASOF` is a constant 2024-07-18; the extract is 2.3 years old.

7. **Minor attribute noise.**
   - 63 rows with `BLDG_SQFT = 1`; 93 rows ≤10 sq ft (sentinel-like).
   - 188 rows `PRIMARY_RES = Y` with no building record.
   - 28 rows have `TOTAL_MKT_VALUE` but no `LAND_MKT_VALUE`.
   - 28 `TAX_DISTRICT` values use a 4-character `07-2` style instead of the
     2-character norm.
   - 10,388 duplicate normalized addresses (many are apartment/mobile-home
     parks and condos, so not automatically errors).

---

## Interpretation caveats

- **Duplicate IDs are not automatically errors.** In parcel extracts, multipart
  parcels and condo units are often multiple features per legal parcel. The
  problem is that the data model is not documented: there is no field telling a
  consumer whether a row is a parcel, a part, or a unit.
- **Vacancy explains much of the missing building data.** `Residential` parcels
  with no building record (20,291) are plausibly vacant lots; `Greenbelt` and
  `Agricultural` similarly. Missing address (50%) is consistent with a rural
  county where many parcels have no situs address.
- **Acreage may be a different concept than polygon area.** Deeded/assessed
  acreage can include areas outside the mapped polygon or exclude rights-of-way.
  The 16.4% disagreement is still worth flagging, but it needs a business-rule
  decision before it becomes an "error."
- **The snapshot is fixed.** Nothing in this file is newer than 2024-07-18.

---

## Why this dataset is good for the talk

The defects are real, varied, and each maps to a deterministic check:

| Defect in this data | Deterministic gate |
|---|---|
| 40.7% of rows in duplicate-ID groups | Uniqueness / cardinality rule per ID |
| 1,517 unattributed + 532 placeholder IDs | Mandatory-attribute and ID-format rules |
| 19,968 rows sharing exact footprints | Exact-geometry duplicate detection |
| 32,476 topology overlaps (98% same footprint) | `Must Not Overlap` after dedup |
| 16.4% acreage mismatch | Area in equal-area CRS vs stated acreage |
| Web Mercator `SHAPE_Area` +60.1% | CRS/measurement validation |
| `EFFBUILT_YR` 1–124 | Domain/range rule |
| `9999999`, blank IDs, all-zero IDs | Sentinel-value detection |
| 2024-07-18 snapshot | Freshness check |

The "money shot" writes itself: an LLM proposes a batch of fixes, the
deterministic gate rejects a plausible one (e.g., "set 9999999 to the owner's
parcel" or "snap acreage to `SHAPE_Area`"), and the audit trail shows the model
never touched the data.

For a live demo, subset to Cedar City (~21,275 rows) or a few thousand parcels;
68,965 polygons is more than a 7-minute demo needs.

---

## Reproduction

Scripts and raw output are in this folder:

- `inventory_gdb.py` — schema, domains, row counts
- `profile_attributes.py` — completeness, distributions, value checks
- `geometry_pass.py` — validity, duplicate geometry, CRS/area comparison
- `deep_dive.py` — duplicate-ID semantics, acreage mismatches, cross-tabs
- `topology_check.py` — `Must Not Overlap` classification
- `final_checks.py` — unattributed rows, duplicate-vs-acreage link, outliers

Run with ArcGIS Pro's Python (`arcgispro-py3`) and pass the feature-class path
as the only argument.
