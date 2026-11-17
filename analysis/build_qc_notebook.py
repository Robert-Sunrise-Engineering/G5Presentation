import json, os

cells = []


def md(src):
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": src.strip("\n").splitlines(keepends=True),
    })


def code(src):
    cells.append({
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": src.strip("\n").splitlines(keepends=True),
    })


md(r"""
# Trust but Verify — LLM-Assisted Parcel QC

**Demo dataset:** Kanarraville, Iron County, Utah — 508 parcels (`demo.gdb/Kanarraville_Parcels`)

**Flow:** deterministic checks → local LLM proposes cleanup actions → deterministic gate accepts/rejects → human review → audit log + reversible patch.

**Runtime:** ArcGIS Pro 3.7 Python (`arcpy`, `pandas`) + local Ollama (`gemma4:12b`). Nothing leaves the machine.
""")

code(r"""
import os, json, time, tempfile, shutil, hashlib
from datetime import datetime
import urllib.request, urllib.error

import arcpy
import pandas as pd

# ---------------------------------------------------------------- config
ROOT      = r"C:\Users\user\projects\G5Presentation"
GDB       = os.path.join(ROOT, "demo", "GDBs", "demo.gdb")
PARCELS   = os.path.join(GDB, "Kanarraville_Parcels")
BOUNDARY  = os.path.join(GDB, "Kanarraville_Boundary")

OLLAMA    = "http://localhost:11434"
MODEL     = "gemma4:12b"
NUM_CTX   = 8192

EQUAL_AREA = 5070          # NAD83 / Conus Albers, metres
ACRE       = 4046.8564224
TOL        = 0.05          # 5% acreage tolerance -> "no change justified"
AUDIT_DIR  = os.path.join(ROOT, "analysis")

print("arcpy", arcpy.GetInstallInfo()["Version"])
print("parcels:", PARCELS)
print("model  :", MODEL)
""")

md(r"""
## Step 1 — Load the layer and measure it honestly

Two things this cell gets right that a naive script does not:

1. **The layer's native CRS is Web Mercator.** `SHAPE@AREA` there overstates area by ~59% in Utah. We reproject to NAD83 / Conus Albers (EPSG:5070) before comparing acreage.
2. **Many parcels have several rows.** We measure at **parcel level**: dissolve identical footprints (`WKB`) by `PARCEL_ID` before comparing to assessed acreage.
""")

code(r"""
FIELDS = ["OID@", "PARCEL_ID", "PARCEL_ADD", "PARCEL_ACRES", "HOUSE_CNT",
          "BLDG_SQFT", "BUILT_YR", "CONST_MATERIAL", "PROP_CLASS",
          "TAX_DISTRICT", "TOTAL_MKT_VALUE", "CURRENT_ASOF", "SHAPE@"]

rows = []
with arcpy.da.SearchCursor(PARCELS, FIELDS) as cur:
    for r in cur:
        g = r[-1]
        rows.append({
            "oid": r[0],
            "parcel_id": (r[1] or "").strip(),
            "address": r[2],
            "stated_acres": r[3],
            "house_cnt": r[4],
            "bldg_sqft": r[5],
            "built_yr": r[6],
            "const_material": r[7],
            "prop_class": r[8],
            "tax_district": r[9],
            "total_value": r[10],
            "asof": r[11],
            "area_3857": g.area if g else None,          # Web Mercator m^2
            "wkb": hashlib.sha1(bytes(g.WKB)).hexdigest() if g else None,
            "geometry": g,
        })

df = pd.DataFrame(rows)

with arcpy.da.SearchCursor(BOUNDARY, ["SHAPE@"]) as cur:
    boundary = next(cur)[0]

def boundary_class(g):
    if g is None:
        return "null"
    if g.within(boundary):
        return "within"
    if not g.disjoint(boundary):
        return "partial"
    return "outside"

df["boundary"] = df["geometry"].map(boundary_class)

# equal-area measurement (disposable scratch GDB)
scratch_dir = tempfile.mkdtemp(prefix="qc_")
scratch_gdb = os.path.join(scratch_dir, "qc_scratch.gdb")
arcpy.management.CreateFileGDB(scratch_dir, "qc_scratch.gdb")
proj_fc = os.path.join(scratch_gdb, "parcels_5070")
arcpy.management.Project(PARCELS, proj_fc, arcpy.SpatialReference(EQUAL_AREA))

area_by_oid = {}
with arcpy.da.SearchCursor(proj_fc, ["OID@", "SHAPE@AREA"]) as cur:
    for oid, a in cur:
        area_by_oid[oid] = a

df["area_5070"] = df["oid"].map(area_by_oid)
df["geom_acres"] = df["area_5070"] / ACRE
df["merc_acres"] = df["area_3857"] / ACRE

print(f"rows loaded: {len(df)}")
print(df["boundary"].value_counts().to_string())

infl = (df["merc_acres"] / df["geom_acres"] - 1) * 100
print(f"\nWeb Mercator area inflation vs EPSG:5070: "
      f"median {infl.median():.1f}%, max {infl.max():.1f}%")
print("Rows >25% off if you trust the native Shape_Area:",
      int((abs(df['merc_acres'] / df['geom_acres'] - 1) > 0.25).sum()))
""")

md(r"""
## Step 2 — Deterministic checks build the evidence base

No LLM yet. These are measurements, each with a reason a reviewer can check:
duplicate parcel IDs, assessed-vs-measured acreage, boundary clipping, blank IDs, snapshot age.
""")

code(r"""
def varies(series):
    vals = {str(v).strip() for v in series.tolist() if v is not None and str(v).strip() != ""}
    return len(vals) > 1

def to_float(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

pid_df = df[df["parcel_id"] != ""]
evidence = {}
rows_by_pid = {}

for pid, grp in pid_df.groupby("parcel_id"):
    uniq = grp.drop_duplicates(subset="wkb")
    dissolved = float(uniq["geom_acres"].sum())
    stated_vals = [v for v in grp["stated_acres"].tolist() if v is not None]
    stated = float(stated_vals[0]) if stated_vals else None
    hc = [str(v) for v in grp["house_cnt"].dropna().tolist()]

    evidence[pid] = {
        "parcel_id": pid,
        "address": next((a for a in grp["address"].tolist() if a), None),
        "n_rows": int(len(grp)),
        "n_geoms": int(grp["wkb"].nunique()),
        "stated_acres": stated,
        "dissolved_acres": round(dissolved, 4),
        "ratio": round(stated / dissolved, 3) if stated and dissolved else None,
        "house_cnt": hc[0] if hc else None,
        "bldg_sqft_varies": varies(grp["bldg_sqft"]),
        "built_yr_varies": varies(grp["built_yr"]),
        "const_material_varies": varies(grp["const_material"]),
        "boundary": sorted(set(grp["boundary"])),
        "prop_class": next((p for p in grp["prop_class"].tolist() if p), None),
        "tax_district": next((t for t in grp["tax_district"].tolist() if t), None),
    }
    rows_by_pid[pid] = grp["oid"].tolist()

dup_ids    = [p for p, e in evidence.items() if e["n_rows"] > 1]
multi_unit = [p for p in dup_ids if (to_float(evidence[p]["house_cnt"]) or 0) > 1]
area_off   = [p for p, e in evidence.items()
              if e["stated_acres"] and e["dissolved_acres"]
              and e["stated_acres"] >= 0.05
              and abs(e["ratio"] - 1) > 0.25]
blank_rows = df[df["parcel_id"] == ""]
asof = sorted({str(v) for v in df["asof"].dropna().tolist()})

print(f"rows={len(df)} | unique parcel IDs={len(evidence)} | blank-ID rows={len(blank_rows)}")
print(f"parcels with duplicate IDs={len(dup_ids)} | of which HOUSE_CNT>1={len(multi_unit)}")
print(f"parcels with acreage >25% off dissolved geometry={len(area_off)}")
print(f"CURRENT_ASOF={asof} | snapshot age="
      f"{(pd.Timestamp.today().normalize() - pd.Timestamp(asof[0])).days} days")

print("\nExample: one parcel, many buildings (NOT duplicates to delete)")
print(pd.DataFrame([evidence["A-0646-0001-0000"]]).T.to_string(header=False))
print("\nIts rows differ only in per-building detail:")
print(df[df.parcel_id == "A-0646-0001-0000"][
      ["oid", "address", "house_cnt", "bldg_sqft", "built_yr", "geom_acres"]].to_string(index=False))
""")

md(r"""
## Step 3 — Ask the local model for proposals

We send **only the measured evidence** — no hints about what the right answer is — and require schema-valid JSON.
Everything runs against Ollama on this machine.
""")

code(r"""
CASE_IDS = ["A-0646-0001-0000",   # 7 rows, one parcel, 7 real units
            "A-0714-0000-0000",   # 3 rows, 3 geometries, assessed 4.70 vs mapped 4.56
            "A-0714-0001-0000",   # 3 rows, 3 geometries, assessed 15.547 vs mapped 13.521
            "A-0640-0002-0000",   # 2 rows, 2 geometries
            "A-0647-0647-000N",   # 6 rows, 2 geometries
            "E-0337-0002-00R1",   # genuine outlier: 10.11 assessed vs 0.885 mapped, clipped
            "A-0729-0002-0002"]   # single row, 0.988 assessed vs 0.491 mapped

cases = []
for pid in CASE_IDS:
    if pid not in evidence:
        continue
    c = dict(evidence[pid])
    c["objectids"] = rows_by_pid[pid]
    cases.append(c)

SCHEMA = {
    "type": "object",
    "properties": {
        "proposals": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "parcel_id": {"type": "string"},
                    "action": {"type": "string",
                               "enum": ["delete_rows", "merge_rows", "update_field",
                                        "flag_review", "no_action"]},
                    "affected_objectids": {"type": "array", "items": {"type": "integer"}},
                    "field": {"type": "string"},
                    "new_value": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["parcel_id", "action", "affected_objectids",
                             "field", "new_value", "rationale"],
            },
        }
    },
    "required": ["proposals"],
}

prompt = (
    "You are a GIS data QC assistant reviewing a municipal parcel layer.\n"
    "Below are deterministic measurements for parcels that failed checks.\n"
    "For every parcel with more than one row, decide explicitly whether the rows are duplicate\n"
    "records of one real-world parcel or distinct records (for example separate units or\n"
    "buildings). Propose merge_rows or delete_rows only when they are duplicates; otherwise\n"
    "flag_review. For acreage discrepancies, either propose update_field with a numeric value\n"
    "or flag_review.\n"
    "Allowed actions: delete_rows, merge_rows, update_field, flag_review, no_action.\n"
    "Use the object IDs exactly as listed. Never invent object IDs.\n"
    "For update_field set field='PARCEL_ACRES' and a numeric new_value.\n"
    "For other actions use empty strings for field and new_value.\n"
    "Return JSON only.\n\nCases:\n" + json.dumps(cases, indent=1)
)

body = {
    "model": MODEL, "stream": False, "think": False,
    "options": {"num_ctx": NUM_CTX, "temperature": 0},
    "format": SCHEMA,
    "prompt": prompt,
}
req = urllib.request.Request(
    OLLAMA + "/api/generate",
    data=json.dumps(body).encode("utf-8"),
    headers={"Content-Type": "application/json"},
)

t0 = time.time()
try:
    with urllib.request.urlopen(req, timeout=600) as resp:
        out = json.loads(resp.read())
except urllib.error.HTTPError as e:
    raise RuntimeError(f"Ollama returned HTTP {e.code}: {e.read()[:300]!r}") from e
except urllib.error.URLError as e:
    raise RuntimeError(
        f"Cannot reach Ollama at {OLLAMA}. Is `ollama serve` running and is `{MODEL}` pulled?"
    ) from e
elapsed = time.time() - t0

proposals = json.loads(out["response"])["proposals"]

eval_s = out.get("eval_duration", 1) / 1e9
print(f"model={MODEL}  elapsed={elapsed:0.1f}s  "
      f"load={out.get('load_duration', 0)/1e9:0.1f}s  "
      f"eval={out.get('eval_count', 0)} tokens @{out.get('eval_count', 0)/max(eval_s, 0.001):0.1f} tok/s")
print(f"proposals returned: {len(proposals)}\n")
for p in proposals:
    print(f"- {p['parcel_id']}: {p['action']} oids={p.get('affected_objectids')}"
          f" field={p.get('field')} value={p.get('new_value')}")
    print(f"    {p['rationale']}")
""")

md(r"""
## Step 4 — The deterministic gate

The model's output is a **proposal**, not an edit. The gate is plain code with named rules; it either accepts a non-destructive action, downgrades a risky edit to a review flag, or rejects it outright.

| Rule | Check | Outcome |
|---|---|---|
| G0 | parcel known, action allowed, every OID belongs to that parcel | reject |
| G1 | destructive action on a parcel with `HOUSE_CNT > 1` or varying per-building fields | **reject** |
| G2 | edit field on the protected list (`PARCEL_ID`, geometry, values) | reject |
| G3 | proposed acreage must match dissolved geometry within 1% | reject |
| G4 | proposed acreage change must exceed the 5% tolerance | **reject** |
| G5 | parcel partly outside the boundary → mapped footprint is clipped | **downgrade to review** |
| G6 | composite parcel (multiple distinct geometries) → area is a sum | downgrade |
| G7 | `flag_review` / `no_action` | accept |

Nothing here calls a model, reads natural language, or trusts the rationale text.
""")

code(r"""
KNOWN_ACTIONS = {"delete_rows", "merge_rows", "update_field", "flag_review", "no_action"}
EDITABLE      = {"PARCEL_ACRES"}
PROTECTED     = {"PARCEL_ID", "SERIAL_NUM", "geometry"}

def gate(p, ev, rows_for_pid):
    pid    = p.get("parcel_id", "")
    action = p.get("action")
    oids   = p.get("affected_objectids") or []

    if ev is None:
        return dict(verdict="REJECT", rule="G0", reason=f"unknown parcel {pid!r}")
    if action not in KNOWN_ACTIONS:
        return dict(verdict="REJECT", rule="G0", reason=f"action {action!r} not allowed")
    bad = [o for o in oids if o not in rows_for_pid]
    if bad:
        return dict(verdict="REJECT", rule="G0",
                    reason=f"object IDs {bad} do not belong to parcel {pid}")

    # G1 - destructive actions on a one-parcel-many-units data model
    if action in ("delete_rows", "merge_rows"):
        units = (to_float(ev["house_cnt"]) or 0) > 1
        fields_vary = ev["bldg_sqft_varies"] or ev["built_yr_varies"] or ev["const_material_varies"]
        if units or fields_vary:
            return dict(verdict="REJECT", rule="G1",
                        reason=("HOUSE_CNT=%s and per-building fields vary -> rows are real units, "
                                "not duplicates" % ev["house_cnt"]))
        return dict(verdict="DOWNGRADE", rule="G1",
                    reason="destructive action never auto-applied; queued as review")

    if action == "update_field":
        field = p.get("field")
        if field in PROTECTED:
            return dict(verdict="REJECT", rule="G2", reason=f"{field} is protected")
        if field not in EDITABLE:
            return dict(verdict="REJECT", rule="G2", reason=f"{field!r} not editable by gate")
        if field == "PARCEL_ACRES":
            val = to_float(str(p.get("new_value", "")).strip())
            if val is None:
                return dict(verdict="REJECT", rule="G3", reason="proposed acreage not numeric")
            if abs(val - ev["dissolved_acres"]) / ev["dissolved_acres"] > 0.01:
                return dict(verdict="REJECT", rule="G3",
                            reason=f"proposed {val} not traceable to measured "
                                   f"{ev['dissolved_acres']}")
            if not ev["stated_acres"]:
                return dict(verdict="REJECT", rule="G4", reason="no assessed acreage to compare")
            delta = abs(ev["stated_acres"] - ev["dissolved_acres"]) / ev["stated_acres"]
            if delta < TOL:
                return dict(verdict="REJECT", rule="G4",
                            reason=(f"assessed {ev['stated_acres']} vs measured "
                                    f"{ev['dissolved_acres']} is {delta*100:.1f}% "
                                    f"(within {TOL*100:.0f}% tolerance) -> no change justified"))
            if "partial" in ev["boundary"]:
                return dict(verdict="DOWNGRADE", rule="G5",
                            reason="parcel straddles the boundary; mapped footprint is clipped, "
                                   "so a replacement acreage cannot be derived")
            if ev["n_geoms"] > 1:
                return dict(verdict="DOWNGRADE", rule="G6",
                            reason="composite parcel; measured acres are a dissolve sum")
            return dict(verdict="ACCEPT", rule="G7",
                        reason=(f"measured {ev['dissolved_acres']} is "
                                f"{delta*100:.0f}% from assessed; within boundary; single geometry"))

    return dict(verdict="ACCEPT", rule="G7", reason="non-destructive review action")

results = [gate(p, evidence.get(p.get("parcel_id")), rows_by_pid.get(p.get("parcel_id"), []))
           for p in proposals]
""")

md(r"""
### Policy self-test

The gate's behaviour must not depend on what the model happens to say today. These fixed proposals exercise every rule and are checked on every run. If a rule changes, this table fails loudly.
""")

code(r"""
SELFTEST = [
    # parcel, proposal, expected rule
    ("A-0646-0001-0000", dict(action="merge_rows", rationale="rows look duplicated"), "G1"),
    ("A-0646-0001-0000", dict(action="update_field", field="PARCEL_ID",
                             new_value="X", rationale="rename"), "G2"),
    ("A-0714-0000-0000", dict(action="update_field", field="PARCEL_ACRES",
                             new_value="4.023", rationale="use the largest part"), "G3"),
    ("A-0714-0000-0000", dict(action="update_field", field="PARCEL_ACRES",
                             new_value="4.5597", rationale="use the dissolved area"), "G4"),
    ("E-0337-0002-00R1", dict(action="update_field", field="PARCEL_ACRES",
                              new_value="0.8852", rationale="use the measured area"), "G5"),
    ("A-0647-0647-000N", dict(action="update_field", field="PARCEL_ACRES",
                              new_value="0.9664", rationale="use the dissolved area"), "G6"),
    ("A-0729-0002-0002", dict(action="update_field", field="PARCEL_ACRES",
                              new_value="0.4912", rationale="use the measured area"), "G7"),
]

st_rows = []
for pid, prop, expected in SELFTEST:
    p = {"parcel_id": pid, "affected_objectids": rows_by_pid.get(pid, []), **prop}
    r = gate(p, evidence.get(pid), rows_by_pid.get(pid, []))
    st_rows.append({"parcel_id": pid, "action": prop["action"], "expected": expected,
                    "got": r["rule"], "verdict": r["verdict"], "reason": r["reason"]})

selftest = pd.DataFrame(st_rows)
print(selftest.to_string(index=False))
print("\npolicy self-test:", "PASS" if bool((selftest.expected == selftest.got).all()) else "FAIL")
""")

md(r"""
## Step 5 — Human review table

This is what goes in front of the data steward: the model's proposal, its rationale, and the gate's verdict with the rule that decided it.
""")

code(r"""
review_rows = []
for i, (p, g) in enumerate(zip(proposals, results), 1):
    review_rows.append({
        "#": i,
        "parcel_id": p.get("parcel_id"),
        "action": p.get("action"),
        "oids": ",".join(map(str, p.get("affected_objectids") or [])),
        "field": p.get("field") or "",
        "new value": p.get("new_value") or "",
        "model rationale": (p.get("rationale") or "")[:105],
        "verdict": g["verdict"],
        "rule": g["rule"],
        "gate reason": g["reason"],
    })

review = pd.DataFrame(review_rows)

for _, r in review.iterrows():
    print(f"[{r['verdict']:<9}] {r['parcel_id']}  {r['action']}  ({r['rule']})")
    print(f"    model: {r['model rationale']}")
    print(f"    gate : {r['gate reason']}\n")

print(review.groupby(["verdict", "rule"]).size().to_string())
""")

md(r"""
## Step 6 — Audit trail and a reversible patch

Every run writes two files: an **audit CSV** (what the model said, what the gate decided, why) and a **patch JSON** containing only gate-accepted edits, each with its original value and `status: pending_human_approval`.

The demo then applies the accepted *review flags* to a **scratch copy** of the layer, shows the result, and undoes it — proving the change is reversible without touching the production feature class.
""")

code(r"""
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
audit_path = os.path.join(AUDIT_DIR, f"qc_audit_{stamp}.csv")
patch_path = os.path.join(AUDIT_DIR, f"qc_patch_{stamp}.json")

review.to_csv(audit_path, index=False)

patch = {
    "created": datetime.now().isoformat(timespec="seconds"),
    "model": MODEL,
    "parcels_fc": PARCELS,
    "edits": [],
    "flags": [],
}
for p, g in zip(proposals, results):
    pid = p.get("parcel_id")
    ev  = evidence.get(pid, {})
    if g["verdict"] == "ACCEPT" and p.get("action") == "update_field":
        patch["edits"].append({
            "parcel_id": pid,
            "oid": p.get("affected_objectids"),
            "field": p.get("field"),
            "new_value": p.get("new_value"),
            "original_value": ev.get("stated_acres"),
            "status": "pending_human_approval",
        })
    elif g["verdict"] in ("ACCEPT", "DOWNGRADE"):
        patch["flags"].append({
            "parcel_id": pid,
            "oids": p.get("affected_objectids"),
            "verdict": g["verdict"],
            "rule": g["rule"],
            "reason": g["reason"],
        })

with open(patch_path, "w", encoding="utf-8") as f:
    json.dump(patch, f, indent=2)

print("audit ->", audit_path)
print("patch ->", patch_path)
print(f"\naccepted edits awaiting human approval: {len(patch['edits'])}")
print(f"review flags: {len(patch['flags'])}")
print("destructive actions auto-applied: 0")
""")

code(r"""
# --- apply / undo on a scratch copy, so production data is never touched ---
edit_fc = os.path.join(scratch_gdb, "parcels_edit")
if arcpy.Exists(edit_fc):
    arcpy.management.Delete(edit_fc)
arcpy.management.CopyFeatures(PARCELS, edit_fc)
arcpy.management.AddField(edit_fc, "QC_STATUS", "TEXT", field_length=32)

flag_oids = sorted({o for f in patch["flags"] for o in (f["oids"] or [])})
mark = "REVIEW_" + stamp

def set_status(fc, oids, value):
    changed = 0
    with arcpy.da.UpdateCursor(fc, ["OID@", "QC_STATUS"]) as cur:
        for oid, _ in cur:
            if oid in oids:
                cur.updateRow([oid, value])
                changed += 1
    return changed

def status_counts(fc):
    vals = [s if s is not None else "(unset)"
            for (s,) in arcpy.da.SearchCursor(fc, ["QC_STATUS"])]
    return pd.Series(vals).value_counts().to_dict()

n = set_status(edit_fc, set(flag_oids), mark)
print(f"applied: {n} rows flagged in scratch copy {os.path.basename(edit_fc)}")
print("QC_STATUS after apply:", status_counts(edit_fc))

# undo: only rows this run marked
undo = set_status(edit_fc, set(flag_oids), None)
print(f"undone: {undo} rows restored")
print("QC_STATUS after undo :", status_counts(edit_fc))
""")

md(r"""
## Step 7 — What this demonstrates

**The model is useful, not authoritative.**

- It reads structured evidence well and returns schema-valid JSON consistently.
- It makes *plausible* suggestions: merging the 280 S MAIN ST rows, rewriting an assessed acreage from mapped geometry.
- It also produces confident nonsense — e.g. calling an ID a duplicate because its *text* contains a repeated segment.

**The gate is the product.**

- It rejects destructive edits on a one-parcel-many-buildings model (G1).
- It rejects acreage changes that are inside tolerance (G4) or derived from clipped geometry (G5).
- It accepts non-destructive review flags, and queues any genuine edit for a human with the original value attached.

**Everything is auditable and reversible:** audit CSV + patch JSON with originals, applied only on explicit approval.

### Talking points

1. Validate at **parcel level** (dissolve unique geometry by `PARCEL_ID`), never row level.
2. **Reproject before measuring.** Web Mercator inflates area ~59% here.
3. Separate **near-duplicate geometry** (`A-0647-0647-000N`) from **duplicate attributes**.
4. The gate should encode **policy**, not cleverness: tolerances, protected fields, clipped footprints.
5. Keep the model local; the data never leaves the machine.
""")

code(r"""
# cleanup scratch workspace
try:
    arcpy.management.Delete(scratch_gdb)
except Exception:
    pass
try:
    shutil.rmtree(scratch_dir, ignore_errors=True)
except Exception:
    pass
print("scratch cleaned")
""")

nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "ArcGIS Pro",
            "language": "python",
            "name": "conda-env-arcgispro-py3",
        },
        "language_info": {"name": "python", "version": "3.13"},
    },
    "nbformat": 4,
    "nbformat_minor": 5,
}

out_path = r"C:\Users\user\projects\G5Presentation\demo\Pro Projects\Notebooks\qc_demo.ipynb"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
print("wrote", out_path, "cells:", len(cells))
