"""Compare the Kanarraville subset with the same area in the countywide parcel layer."""
import os, sys, tempfile, hashlib
import arcpy
import numpy as np
import pandas as pd

full_fc = r"C:\Users\user\projects\G5Presentation\demo\GDBs\iron_county_parcels.gdb\Parcels_Iron_LIR"
sub_fc = r"C:\Users\user\projects\G5Presentation\demo\GDBs\demo.gdb\Kanarraville_Parcels"
bnd_fc = r"C:\Users\user\projects\G5Presentation\demo\GDBs\demo.gdb\Kanarraville_Boundary"

d = arcpy.Describe(full_fc)
fields = [f.name for f in d.fields if f.type not in ("Geometry", "OID", "Blob")]
attr_fields = [f for f in fields if f not in ("SHAPE_Length", "SHAPE_Area", "Shape_Length", "Shape_Area")]

def read_fc(fc):
    rows = []
    with arcpy.da.SearchCursor(fc, ["OID@", "SHAPE@"] + fields) as cur:
        for r in cur:
            oid, g = r[0], r[1]
            attrs = list(r[2:])
            rows.append([oid, g.area if g else None,
                         hashlib.sha1(g.WKB).hexdigest() if g else None,
                         g.partCount if g else None] + attrs)
    return pd.DataFrame(rows, columns=["oid", "area_3857", "wkb_sha1", "parts"] + fields)

print("reading subset...")
sub = read_fc(sub_fc)
print("reading full layer...")
full = read_fc(full_fc)
full["PARCEL_ID"] = full["PARCEL_ID"].fillna("").astype(str).str.strip()
sub["PARCEL_ID"] = sub["PARCEL_ID"].fillna("").astype(str).str.strip()
full["PARCEL_CITY"] = full["PARCEL_CITY"].fillna("").astype(str).str.strip()
city = full[full["PARCEL_CITY"] == "Kanarraville"].copy()

print(f"\nfull layer                  : {len(full):,}")
print(f"full, PARCEL_CITY=Kanarraville: {len(city):,}")
print(f"Kanarraville_Parcels subset : {len(sub):,}")

# OID relationship
sub_oids = set(sub.oid)
city_oids = set(city.oid)
print(f"subset OIDs also in city set : {len(sub_oids & city_oids):,} / {len(sub_oids):,}")
if len(sub_oids & city_oids) >= 0.9 * len(sub_oids):
    missing = city[~city.oid.isin(sub_oids)]
    extra = sub[~sub.oid.isin(city_oids)]
    print(f"city-set rows missing from subset: {len(missing):,}")
    print(f"subset rows not in city set      : {len(extra):,}")
else:
    # match on (PARCEL_ID, geometry hash) multiset
    key = ["PARCEL_ID", "wkb_sha1"]
    city_counts = city.groupby(key, dropna=False).size().rename("city_n")
    sub_counts = sub.groupby(key, dropna=False).size().rename("sub_n")
    m = pd.concat([city_counts, sub_counts], axis=1).fillna(0).astype(int)
    print(f"(PARCEL_ID, geometry) groups where counts differ: {((m.city_n - m.sub_n) != 0).sum():,}")
    print(f"  rows in city set not represented in subset: {int((m.city_n - m.sub_n).clip(lower=0).sum()):,}")
    print(f"  rows in subset not in city set            : {int((m.sub_n - m.city_n).clip(lower=0).sum()):,}")
    missing = None

# Boundary test for the city-attributed rows and the subset
print("\n--- Boundary relationship ---")
with arcpy.da.SearchCursor(bnd_fc, ["SHAPE@"]) as cur:
    boundary = next(cur)[0]

def boundary_counts(fc, where=None):
    out = {"within": 0, "intersects (partial)": 0, "outside": 0}
    with arcpy.da.SearchCursor(fc, ["OID@", "SHAPE@"], where) as cur:
        for oid, g in cur:
            if g is None:
                continue
            if g.within(boundary):
                k = "within"
            elif not g.disjoint(boundary):
                k = "intersects (partial)"
            else:
                k = "outside"
            out[k] += 1
    return out

print("all PARCEL_CITY=Kanarraville rows:", boundary_counts(full_fc, "PARCEL_CITY = 'Kanarraville'"))
print("Kanarraville_Parcels subset     :", boundary_counts(sub_fc))

# Albers areas for acreage comparison
tmp = tempfile.mkdtemp(prefix="kan_cmp_")
arcpy.management.CreateFileGDB(tmp, "s.gdb")
proj_full = os.path.join(tmp, "s.gdb", "full5070")
arcpy.management.Project(full_fc, proj_full, arcpy.SpatialReference(5070))
alb = []
with arcpy.da.SearchCursor(proj_full, ["OID@", "SHAPE@AREA"]) as cur:
    for oid, a in cur:
        alb.append((oid, a))
alb = pd.DataFrame(alb, columns=["oid", "area_5070"])
full = full.merge(alb, on="oid", how="left")
city = city.merge(alb, on="oid", how="left")

proj_sub = os.path.join(tmp, "s.gdb", "sub5070")
arcpy.management.Project(sub_fc, proj_sub, arcpy.SpatialReference(5070))
alb_sub = []
with arcpy.da.SearchCursor(proj_sub, ["OID@", "SHAPE@AREA"]) as cur:
    for oid, a in cur:
        alb_sub.append((oid, a))
sub = sub.merge(pd.DataFrame(alb_sub, columns=["oid", "area_5070"]), on="oid", how="left")

def metrics(df, label):
    pid = df["PARCEL_ID"]
    dup_pid_rows = int(pid[pid != ""].duplicated(keep=False).sum())
    dup_geom_rows = int(df["wkb_sha1"].duplicated(keep=False).sum())
    has_bldg = df[["HOUSE_CNT", "BLDG_SQFT", "FLOORS_CNT", "BUILT_YR", "CONST_MATERIAL"]].notna().any(axis=1)
    has_addr = df["PARCEL_ADD"].notna()
    r = df.dropna(subset=["PARCEL_ACRES", "area_5070"])
    r = r[r["area_5070"] > 0]
    ratio = r["PARCEL_ACRES"] * 4046.8564224 / r["area_5070"]
    big = r[r["PARCEL_ACRES"] >= 0.05]
    ratio_big = big["PARCEL_ACRES"] * 4046.8564224 / big["area_5070"]
    print(f"\n[{label}] rows={len(df):,}")
    print(f"  rows with duplicated PARCEL_ID   : {dup_pid_rows:,} ({dup_pid_rows/len(df)*100:.1f}%)")
    print(f"  distinct PARCEL_ID               : {pid[pid!=''].nunique():,}")
    print(f"  blank PARCEL_ID                  : {(pid=='').sum():,}")
    print(f"  rows with duplicated geometry    : {dup_geom_rows:,} ({dup_geom_rows/len(df)*100:.1f}%)")
    print(f"  building data present            : {has_bldg.mean()*100:.1f}%")
    print(f"  address present                  : {has_addr.mean()*100:.1f}%")
    print(f"  median PARCEL_ACRES              : {df['PARCEL_ACRES'].median():.3f}")
    print(f"  acreage within 10% of geometry   : {(ratio.sub(1).abs() <= .10).mean()*100:.1f}% (n={len(r):,})")
    print(f"  acreage within 25% of geometry   : {(ratio.sub(1).abs() <= .25).mean()*100:.1f}%")
    print(f"  acreage >25% off (>=0.05 ac)     : {(ratio_big.sub(1).abs() > .25).mean()*100:.1f}% (n={len(big):,})")
    print(f"  property classes                  : {df['PROP_CLASS'].nunique()}")
    print(f"  top classes                      : {df['PROP_CLASS'].value_counts().head(4).to_dict()}")

metrics(city, "county layer, PARCEL_CITY=Kanarraville")
metrics(sub, "Kanarraville_Parcels subset")

# What differs inside a duplicate-PARCEL_ID group?
print("\n--- Which attributes vary within duplicate-ID groups (subset) ---")
g = sub[sub.PARCEL_ID != ""].groupby("PARCEL_ID")
sizes = g.size()
dups = sizes[sizes > 1]
varying = {}
for pid in dups.index:
    grp = sub[sub.PARCEL_ID == pid]
    for c in attr_fields:
        if c in ("PARCEL_ID", "PARCEL_CITY"):
            continue
        if grp[c].astype(str).nunique(dropna=False) > 1:
            varying[c] = varying.get(c, 0) + 1
print(f"duplicate-ID groups: {len(dups):,}")
for c, n in sorted(varying.items(), key=lambda x: -x[1]):
    print(f"  {c:24s} varies in {n:3d} groups")

print("\nExample duplicate group rows:")
pid = dups.sort_values(ascending=False).index[0]
cols = ["oid", "PARCEL_ID", "SERIAL_NUM", "PARCEL_ACRES", "TOTAL_MKT_VALUE",
        "LAND_MKT_VALUE", "BLDG_SQFT", "HOUSE_CNT", "BUILT_YR", "PARCEL_ADD"]
print(f"PARCEL_ID = {pid}  ({dups[pid]} rows)")
print(sub[sub.PARCEL_ID == pid][cols].to_string(index=False))
