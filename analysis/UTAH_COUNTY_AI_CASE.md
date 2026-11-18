# Utah County geospatial AI assessment workflow — case notes (2026-11-18)

A Utah county building AI for parcel-reassessment triage **in-house** — the
closest precedent to the talk's thesis, and the strongest local validation.

## What it is

- Utah County's **GIS Division** built the workflow itself (no vendor product).
- An AI model scans high-resolution aerial imagery and **detects building
  footprints**; ArcGIS Pro compares the detected outlines against the
  **Assessor's building sketches** (the source of taxable square footage) and
  computes match scores.
- Scores are classified **green** (strong match) / **yellow** (possible
  discrepancy) / **red** (likely warrants field inspection).
- Results publish to ArcGIS Online and surface in a staff web app built with
  the **ArcGIS Maps SDK for JavaScript** (parcel record + imagery + sketch +
  AI footprint on one map).

## People

- Built by GIS Programmer **Nathan Thomas** (6 years at the county).
- Awarded the **2026 Utah Excellence in GIS Award** by UGIC (announced
  2026-05-06, Kanab).
- GIS manager: **Darin Sleight** ("innovative but also highly practical").
- Quoted in Esri case study: IS Director **Patrick Wawro** — *"The assessor
  doesn't have to worry so much about going out and finding and discovering
  where the issues are… staff can actually focus on deciding what to do and how
  to assess."*

## Numbers (money slide)

| Metric | Value |
|---|---|
| Properties processed (approaching reassessment) | 56,993 |
| Strong matches — ruled out of further review | 48,846 (86%) |
| Flagged for additional review | 7,494 |
| High-priority field-inspection candidates | 653 |
| Outsourcing cost eliminated | ~$160K/year |

Context: Utah's state-mandated 5-year reassessment cycle forces counties to
review every property; manual inspection of 284K+ parcels is impossible.

## Why it's "built from scratch"

The footprint model is **computer vision** (object detection on imagery) —
not an LLM, not a purchased product. Thomas also built a storm-drain detection
model on the same pattern (high-res aerial imagery → object detection; used for
mosquito-abatement / West Nile risk mapping; countywide imagery in ~25 hours).
So it's an internal AI capability, not a one-off.

## Why it matters for the talk

1. **Same architecture thesis**: AI produces *triage* (green/yellow/red);
   humans make the *determination* (valuation, inspection). "The model drafts
   the review queue; the appraiser decides."
2. **Hometown credibility**: a Utah county, a UGIC 2026 award, $160K/year.
3. **Sharpens the LLM framing**: this is a narrow, purpose-trained CV model for
   a high-confidence decision path. Our talk's LLM uses sit at the *edges* of
   QC (spec reading, code drafting, memos) — the parts CV can't do. The two are
   complements, not competitors: "AI-in-QC is a placement question, not one
   technology."
4. **EO 2026-08 tie-in**: human-in-the-loop on determinations affecting
   individuals (taxation qualifies) is exactly what their web app implements.

## Sources

- Esri case study: https://www.esri.com/en-us/lg/industry/government/stories/utah-county-modernizes-property-assessment-with-gis-and-ai
- UGIC 2026 award: https://ugic.org/news/utah-excellence-in-gis-award-2026/
