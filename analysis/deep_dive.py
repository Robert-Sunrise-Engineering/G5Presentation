"""Deep dive: duplicate semantics, acreage consistency, attribute cross-checks."""
import sys, os, tempfile, hashlib, time
import arcpy
import numpy as np
import pandas as pd

fc = sys.argv[1]
d = arcpy.Describe(fc)
fields = [f.name for f in d.fields if f.type not in ("Geometry", "OID", "Blob")]
read = ["OID@", "SHAPE@"] + fields

rows = []
with arcpy.da.SearchCursor(fc, read) as cur:
    for r in cur:
        oid, g = r[0], r[1]
        attrs = list(r[2:])
        wh = hashlib.sha1(g.WKB).hexdigest() if g is not None else None
        rows.append([oid, g.area if g else None, wh, g.partCount if g else None] + attrs)
cols = ["oid", "area_3857", "wkb_sha1", "parts"] + fields
df = pd.DataFrame(rows, columns=cols)
df["PARCEL_ID"] = df["PARCEL_ID"].fillna("").astype(str).str.strip()
attr_fields = [f for f in fields if f not in ("SHAPE_Length", "SHAPE_Area")]

# ---- exact duplicate records (all attributes + geometry identical) ----
attr_cols = attr_fields + ["wkb_sha1"]
exact_dup = df.duplicated(subset=attr_cols, keep="first")
print(f"\nExact duplicate records (all attributes + geometry): {exact_dup.sum():,}")
print(f"  ...rows involved in exact-duplicate sets         : {df.duplicated(subset=attr_cols, keep=False).sum():,}")

# ---- classify duplicate PARCEL_ID groups ----
print("\n--- Duplicate PARCEL_ID group semantics ---")
g = df[df["PARCEL_ID"] != ""].groupby("PARCEL_ID")
agg = g.agg(n=("oid", "size"), n_geom=("wkb_sha1", "nunique"))
attrs_key = pd.util.hash_pandas_object(df[attr_fields], index=False)
df["_attrkey"] = attrs_key
agg["n_attr"] = df[df["PARCEL_ID"] != ""].groupby("PARCEL_ID")["_attrkey"].nunique()
m = agg[agg["n"] > 1]
print(f"duplicate-ID groups: {len(m):,}")
print(f"  exact duplicates (same geom, same attrs) : {((m.n_geom==1)&(m.n_attr==1)).sum():,} groups, "
      f"{m[(m.n_geom==1)&(m.n_attr==1)]['n'].sum():,} rows")
print(f"  same attrs, different geometry (multipart): {((m.n_geom>1)&(m.n_attr==1)).sum():,} groups, "
      f"{m[(m.n_geom>1)&(m.n_attr==1)]['n'].sum():,} rows")
print(f"  different attributes                      : {(m.n_attr>1).sum():,} groups, "
      f"{m[m.n_attr>1]['n'].sum():,} rows")

print("\nTop 10 largest PARCEL_ID groups:")
top = m.sort_values("n", ascending=False).head(10).index
for pid in top:
    sub = df[df["PARCEL_ID"] == pid]
    print(f"\n  ID={pid!r}  rows={len(sub)}  distinct_geom={sub.wkb_sha1.nunique()}  "
          f"distinct_attrs={sub._attrkey.nunique()}")
    for c in ("PROP_CLASS", "TAX_DISTRICT", "PARCEL_ADD", "SUBDIV_NAME", "PARCEL_ACRES"):
        vals = sub[c].dropna().astype(str).unique()
        print(f"    {c:14s}: {vals[:4].tolist()}{' ...' if len(vals) > 4 else ''}")

# ---- exact-geometry duplicates by class ----
print("\n--- Rows sharing identical geometry, by property class ---")
dupgeo = df[df["wkb_sha1"].duplicated(keep=False) & df["wkb_sha1"].notna()]
print(dupgeo["PROP_CLASS"].fillna("<null>").value_counts().head(12).to_string())

print("\n--- Duplicate-geometry group semantics ---")
gg = df[df["wkb_sha1"].notna()].groupby("wkb_sha1").agg(
    n=("oid", "size"), n_pid=("PARCEL_ID", "nunique"),
    n_attr=("_attrkey", "nunique"), n_acres=("PARCEL_ACRES", "nunique"),
)
gm = gg[gg["n"] > 1]
print(f"duplicate-geometry groups          : {len(gm):,}  rows={int(gm['n'].sum()):,}")
print(f"  ...single PARCEL_ID in group     : {(gm['n_pid']==1).sum():,}  rows={int(gm[gm['n_pid']==1]['n'].sum()):,}")
print(f"  ...multiple PARCEL_IDs in group  : {(gm['n_pid']>1).sum():,}  rows={int(gm[gm['n_pid']>1]['n'].sum()):,}")
print(f"  ...non-geometry attrs identical  : {(gm['n_attr']==1).sum():,}  rows={int(gm[gm['n_attr']==1]['n'].sum()):,}")
print(f"  ...stated acres differ           : {(gm['n_acres']>1).sum():,}")
multi_pid_hashes = set(gm[gm["n_pid"] > 1].index)
print("\nRows in multi-PID duplicate-geometry groups, by class:")
print(df[df["wkb_sha1"].isin(multi_pid_hashes)]["PROP_CLASS"].fillna("<null>")
      .value_counts().head(10).to_string())
print("\nExamples of multi-PID shared geometry:")
for h in gm[gm["n_pid"] > 1].sort_values("n", ascending=False).head(2).index:
    sub = df[df["wkb_sha1"] == h]
    print(f"\n  geometry {h[:10]}  rows={len(sub)}  PIDs={sub.PARCEL_ID.nunique()}")
    print(sub[["PARCEL_ID", "PROP_CLASS", "PARCEL_ADD", "PARCEL_ACRES"]].head(6).to_string(index=False))

print("\n--- Placeholder / suspicious IDs ---")
p = df["PARCEL_ID"]
checks = {
    "blank": p == "",
    "all 9s": p.str.fullmatch(r"9+"),
    "all 0s": p.str.fullmatch(r"0+"),
    "7-digit numeric (any)": p.str.fullmatch(r"\d{7}"),
    "7-digit, not all 0/9": p.str.fullmatch(r"\d{7}") & ~p.str.fullmatch(r"[09]+"),
}
for label, mask in checks.items():
    print(f"{label:28s}: {int(mask.sum()):,}")

# ---- blank parcel IDs ----
print("\n--- Rows with blank PARCEL_ID ---")
blank = df[df["PARCEL_ID"] == ""]
print(f"count={len(blank):,}")
print(blank["PROP_CLASS"].fillna("<null>").value_counts().to_string())
print(f"distinct geometry={blank.wkb_sha1.nunique():,}  exact-dup rows={blank.duplicated(subset=attr_cols).sum():,}")
print("sample:")
print(blank[["PARCEL_ID", "SERIAL_NUM", "PROP_CLASS", "PARCEL_ADD", "PARCEL_ACRES"]].head(5).to_string(index=False))

# ---- acreage vs equal-area geometry ----
print("\n--- Acreage consistency (equal-area geometry) ---")
tmp = tempfile.mkdtemp(prefix="iron_qc2_")
scratch = os.path.join(tmp, "s.gdb")
arcpy.management.CreateFileGDB(tmp, "s.gdb")
proj = os.path.join(scratch, "p5070")
arcpy.management.Project(fc, proj, arcpy.SpatialReference(5070))
ao = []
with arcpy.da.SearchCursor(proj, ["OID@", "SHAPE@AREA"]) as cur:
    for oid, a in cur:
        ao.append((oid, a))
albers = pd.DataFrame(ao, columns=["oid", "area_5070"])
df = df.merge(albers, on="oid", how="left")
df["ratio"] = df["PARCEL_ACRES"] * 4046.8564224 / df["area_5070"]
sub = df.dropna(subset=["ratio"])
print(f"n={len(sub):,}")
print("ratio percentiles:", {p: round(float(sub.ratio.quantile(p)), 3)
                            for p in (.01, .05, .25, .5, .75, .95, .99)})
big = sub[sub["PARCEL_ACRES"] >= 0.05]
print(f"\nacres >= 0.05 (n={len(big):,}): within 10% of geometry = "
      f"{((big.ratio-1).abs() <= .10).mean()*100:.1f}%, within 25% = "
      f"{((big.ratio-1).abs() <= .25).mean()*100:.1f}%")
severe = big[(big.ratio > 1.25) | (big.ratio < 0.8)]
print(f"severe mismatch (>25% off, n={len(severe):,}) by class:")
print(severe["PROP_CLASS"].fillna("<null>").value_counts().head(10).to_string())
buckets = {
    "stated >100x geometry": (severe.ratio > 100).sum(),
    "stated 10-100x geometry": ((severe.ratio > 10) & (severe.ratio <= 100)).sum(),
    "stated 2-10x geometry": ((severe.ratio > 2) & (severe.ratio <= 10)).sum(),
    "stated 1.25-2x geometry": ((severe.ratio > 1.25) & (severe.ratio <= 2)).sum(),
    "stated 0.5-0.8x geometry": ((severe.ratio >= 0.5) & (severe.ratio < 0.8)).sum(),
    "stated <0.5x geometry": (severe.ratio < 0.5).sum(),
}
print("mismatch buckets:", {k: int(v) for k, v in buckets.items()})
tiny_geom = big[(big["area_5070"] / 4046.8564224 < 0.01) & (big["PARCEL_ACRES"] >= 0.05)]
print(f"stated >=0.05 ac but geometry <0.01 ac : {len(tiny_geom):,}")
print("\nTop 15 overstatements (stated acres >> geometry):")
o = severe.sort_values("ratio", ascending=False).head(15)
print(o[["PARCEL_ID", "PARCEL_ACRES", "area_5070", "ratio", "parts", "PROP_CLASS", "PARCEL_ADD"]]
      .assign(area_5070=lambda x: (x.area_5070 / 4046.8564224).round(3))
      .rename(columns={"area_5070": "geom_acres", "ratio": "stated/geom"})
      .to_string(index=False))
print("\nTop 15 understatements (stated acres << geometry):")
u = severe.sort_values("ratio").head(15)
print(u[["PARCEL_ID", "PARCEL_ACRES", "area_5070", "ratio", "parts", "PROP_CLASS", "PARCEL_ADD"]]
      .assign(area_5070=lambda x: (x.area_5070 / 4046.8564224).round(3))
      .rename(columns={"area_5070": "geom_acres", "ratio": "stated/geom"})
      .to_string(index=False))

# ---- cross-field checks ----
print("\n--- Cross-field checks ---")
bldg_fields = ["HOUSE_CNT", "BLDG_SQFT", "FLOORS_CNT", "BUILT_YR", "CONST_MATERIAL"]
has_bldg = df[bldg_fields].notna().any(axis=1)
print("PROP_CLASS x has building data:")
print(pd.crosstab(df["PROP_CLASS"].fillna("<null>"), has_bldg).to_string())
print("\nPRIMARY_RES x has building data:")
print(pd.crosstab(df["PRIMARY_RES"].fillna("<null>"), has_bldg).to_string())

# ---- string normalization variants ----
print("\n--- String variants (case/whitespace/punctuation) ---")
for c in ("SUBDIV_NAME", "CONST_MATERIAL", "PARCEL_CITY"):
    s = df[c].dropna().astype(str)
    raw = s.str.strip()
    norm = (raw.str.upper()
              .str.replace(r"[^A-Z0-9 ]", " ", regex=True)
              .str.replace(r"\s+", " ", regex=True)
              .str.strip())
    print(f"{c:16s} raw distinct={raw.nunique():,}  normalized distinct={norm.nunique():,}  "
          f"collapsed={raw.nunique()-norm.nunique():,}")
    if norm.nunique() < raw.nunique():
        # show a few groups where multiple raw forms collapse
        tmpv = pd.DataFrame({"raw": raw, "norm": norm})
        vg = tmpv.groupby("norm")["raw"].nunique()
        worst = vg[vg > 1].sort_values(ascending=False).head(3)
        for n, k in worst.items():
            forms = tmpv[tmpv["norm"] == n]["raw"].unique()[:4]
            print(f"    {k} forms -> {forms}")

# ---- parcel id patterns ----
print("\n--- PARCEL_ID format families ---")
p = df["PARCEL_ID"]
fam = p.str.replace(r"[A-Z]", "A", regex=True).str.replace(r"[0-9]", "9", regex=True)
print(fam.value_counts().head(12).to_string())
print("\nShort ID samples:")
print(p[p.str.len().between(1, 9)].head(10).tolist())
