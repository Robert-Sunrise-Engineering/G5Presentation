"""Geometry + identifier integrity checks for the Iron County parcel layer."""
import sys
import os
import time
import tempfile
import hashlib
import arcpy
import numpy as np
import pandas as pd

fc = sys.argv[1]
t0 = time.time()

# ---------------------------------------------------------------- pass 1
rows = []
with arcpy.da.SearchCursor(
    fc, ["OID@", "PARCEL_ID", "SERIAL_NUM", "PARCEL_ACRES", "SHAPE@"]
) as cur:
    for oid, pid, serial, acres, g in cur:
        if g is None:
            rows.append((oid, pid, serial, acres, None, None, None, None, None, None, None))
            continue
        e = g.extent
        rows.append((
            oid, pid, serial, acres,
            g.area, g.length, g.partCount, g.pointCount,
            hashlib.sha1(g.WKB).hexdigest(),
            (round(e.XMin, 3), round(e.YMin, 3), round(e.XMax, 3), round(e.YMax, 3)),
        ))
print(f"Pass 1: {len(rows):,} features read in {time.time()-t0:.1f}s")

df = pd.DataFrame(rows, columns=[
    "oid", "parcel_id", "serial", "acres", "area_m2", "perim_m",
    "parts", "points", "wkb_sha1", "extent",
])
df["parcel_id"] = df["parcel_id"].fillna("").astype(str).str.strip()

print("\n--- Geometry basics ---")
print(f"null geometry                  : {df['wkb_sha1'].isna().sum():,}")
print(f"zero-area geometry             : {(df['area_m2'] == 0).sum():,}")
print(f"area < 1 m2                    : {(df['area_m2'] < 1).sum():,}")
print(f"area < 10 m2                   : {(df['area_m2'] < 10).sum():,}")
print(f"multipart features             : {(df['parts'] > 1).sum():,}")
print(f"part-count distribution        : {df['parts'].value_counts().sort_index().head(10).to_dict()}")
print(f"point-count percentiles        : {df['points'].quantile([.5,.9,.99,.999]).round(0).to_dict()}")
print(f"max vertices in one feature    : {int(df['points'].max()):,}")
print(f"features with >5000 vertices   : {(df['points'] > 5000).sum():,}")

print("\n--- Exact duplicate geometry (identical WKB) ---")
dupgeom = df[df["wkb_sha1"].notna() & df["wkb_sha1"].duplicated(keep=False)]
print(f"rows in duplicate-geometry groups : {len(dupgeom):,}")
print(f"distinct duplicate geometries     : {dupgeom['wkb_sha1'].nunique():,}")
print(f"largest identical-geometry group  : {dupgeom['wkb_sha1'].value_counts().max()}")

print("\n--- Identifier integrity ---")
pid = df["parcel_id"]
pid_dup = pid[(pid != "") & pid.duplicated(keep=False)]
print(f"blank PARCEL_ID                   : {(pid == '').sum():,}")
print(f"rows with duplicated PARCEL_ID    : {len(pid_dup):,}")
print(f"PARCEL_ID groups with >1 row      : {pid_dup.nunique():,}")
grp = df[df["parcel_id"] != ""].groupby("parcel_id")
stats = grp.agg(
    n=("oid", "size"),
    n_geom=("wkb_sha1", "nunique"),
    n_serial=("serial", "nunique"),
    n_area=("area_m2", "nunique"),
)
multi = stats[stats["n"] > 1]
print(f"duplicate-ID groups               : {len(multi):,}")
print(f"  ...all rows identical geometry  : {(multi['n_geom'] == 1).sum():,}")
print(f"  ...multiple distinct geometries : {(multi['n_geom'] > 1).sum():,}")
print(f"  ...group size distribution      : {multi['n'].value_counts().sort_index().head(10).to_dict()}")
print(f"  ...largest group                : {int(multi['n'].max())} rows")

serial = df["serial"].dropna().astype(str).str.strip()
sg = df[df["serial"].notna()].groupby(df["serial"].astype(str).str.strip())
ss = sg.agg(n=("oid", "size"), n_pid=("parcel_id", "nunique"), n_geom=("wkb_sha1", "nunique"))
ss_multi = ss[ss["n"] > 1]
print(f"\nSERIAL_NUM groups with >1 row     : {len(ss_multi):,}")
print(f"  ...with >1 distinct PARCEL_ID   : {(ss_multi['n_pid'] > 1).sum():,}")
print(f"  ...with >1 distinct geometry    : {(ss_multi['n_geom'] > 1).sum():,}")
print(f"  ...largest serial group         : {int(ss_multi['n'].max()) if len(ss_multi) else 0} rows")

# ---------------------------------------------------------------- area vs acreage
print("\n--- Area vs PARCEL_ACRES ---")
valid = df.dropna(subset=["acres", "area_m2"])
valid = valid[valid["area_m2"] > 0]
ratio = valid["acres"] * 4046.8564224 / valid["area_m2"]
print(f"n compared                        : {len(valid):,}")
print(f"acres-derived-area / WebMerc area : p1={ratio.quantile(.01):.3f} "
      f"p50={ratio.median():.3f} p99={ratio.quantile(.99):.3f}")
print(f"ratio within 5% of 1.0 (acres from WebMercator) : "
      f"{((ratio - 1).abs() < .05).mean()*100:.1f}%")
print(f"ratio within 5% of 0.626 (acres geodesic-correct): "
      f"{((ratio - .626).abs() < .05).mean()*100:.1f}%")

# ---------------------------------------------------------------- check geometry
print("\n--- CheckGeometry ---")
tmp = tempfile.mkdtemp(prefix="iron_qc_")
scratch = os.path.join(tmp, "scratch.gdb")
try:
    arcpy.management.CreateFileGDB(tmp, "scratch.gdb")
    out = os.path.join(scratch, "checkgeom")
    t = time.time()
    arcpy.management.CheckGeometry(fc, out)
    bad = [r for r in arcpy.da.SearchCursor(out, ["CLASS", "FEATURE_ID", "PROBLEM"])]
    print(f"CheckGeometry ran in {time.time()-t:.1f}s; problems: {len(bad):,}")
    if bad:
        bdf = pd.DataFrame(bad, columns=["class", "feature_id", "problem"])
        print(bdf["problem"].value_counts().to_string())
        print(bdf.head(10).to_string(index=False))
except Exception as e:
    print(f"CheckGeometry FAILED: {e}")

# ---------------------------------------------------------------- projected area
print("\n--- Projected (NAD83 Conus Albers, EPSG:5070) area ---")
try:
    t = time.time()
    proj = os.path.join(scratch, "parcels_5070")
    arcpy.management.Project(fc, proj, arcpy.SpatialReference(5070))
    oids, areas = [], []
    with arcpy.da.SearchCursor(proj, ["OID@", "SHAPE@AREA"]) as cur:
        for oid, a in cur:
            oids.append(oid)
            areas.append(a)
    pa = pd.DataFrame({"oid": oids, "area_5070": areas})
    print(f"Project+read in {time.time()-t:.1f}s; projected zero-area: {(pa['area_5070'] == 0).sum():,}")
    m = valid.merge(pa, on="oid", how="inner")
    r2 = m["acres"] * 4046.8564224 / m["area_5070"]
    print(f"acres-derived-area / Albers area  : p1={r2.quantile(.01):.3f} "
          f"p50={r2.median():.3f} p99={r2.quantile(.99):.3f}")
    print(f"ratio within 5% of 1.0 (acres equal-area-correct): {((r2-1).abs() < .05).mean()*100:.1f}%")
    merc_over_alb = m["area_m2"] / m["area_5070"]
    print(f"WebMerc area / Albers area        : p50={merc_over_alb.median():.3f} "
          f"(expected ~1.60 at this latitude)")
except Exception as e:
    print(f"Projection stage FAILED: {e}")

print(f"\nTotal elapsed: {time.time()-t0:.1f}s")
print(f"Scratch dir: {tmp}")
