"""Details on the rebuilt 508-row Kanarraville subset: boundary parcels, oddities."""
import os, tempfile, hashlib
import arcpy
import pandas as pd
import numpy as np

sub_fc = r"C:\Users\user\projects\G5Presentation\demo\GDBs\demo.gdb\Kanarraville_Parcels"
bnd_fc = r"C:\Users\user\projects\G5Presentation\demo\GDBs\demo.gdb\Kanarraville_Boundary"

fields = ["OID@", "PARCEL_ID", "SERIAL_NUM", "TAX_DISTRICT", "PROP_CLASS",
          "PARCEL_ADD", "PARCEL_ACRES", "HOUSE_CNT", "BLDG_SQFT", "BUILT_YR",
          "TOTAL_MKT_VALUE", "SHAPE@"]
rows = []
with arcpy.da.SearchCursor(sub_fc, fields) as cur:
    for r in cur:
        oid, g = r[0], r[-1]
        rows.append(list(r[:-1]) + [g.area if g else None,
                                     hashlib.sha1(g.WKB).hexdigest() if g else None])
df = pd.DataFrame(rows, columns=[
    "oid", "PARCEL_ID", "SERIAL_NUM", "TAX_DISTRICT", "PROP_CLASS",
    "PARCEL_ADD", "PARCEL_ACRES", "HOUSE_CNT", "BLDG_SQFT", "BUILT_YR",
    "TOTAL_MKT_VALUE", "area_3857", "wkb"])
df["PARCEL_ID"] = df["PARCEL_ID"].fillna("").astype(str).str.strip()

with arcpy.da.SearchCursor(bnd_fc, ["SHAPE@"]) as cur:
    boundary = next(cur)[0]

# classify each row
geom_by_oid = {}
with arcpy.da.SearchCursor(sub_fc, ["OID@", "SHAPE@"]) as cur:
    for oid, g in cur:
        if g.within(boundary):
            geom_by_oid[oid] = "within"
        elif not g.disjoint(boundary):
            geom_by_oid[oid] = "partial"
        else:
            geom_by_oid[oid] = "outside"
df["boundary"] = df["oid"].map(geom_by_oid)
print("boundary classification:", df["boundary"].value_counts().to_dict())

# equal-area acres
tmp = tempfile.mkdtemp(prefix="kan508_")
arcpy.management.CreateFileGDB(tmp, "s.gdb")
proj = os.path.join(tmp, "s.gdb", "p5070")
arcpy.management.Project(sub_fc, proj, arcpy.SpatialReference(5070))
alb = []
with arcpy.da.SearchCursor(proj, ["OID@", "SHAPE@AREA"]) as cur:
    for oid, a in cur:
        alb.append((oid, a))
df = df.merge(pd.DataFrame(alb, columns=["oid", "area_5070"]), on="oid", how="left")
df["geom_acres"] = df["area_5070"] / 4046.8564224
df["ratio"] = df["PARCEL_ACRES"] / df["geom_acres"]

print("\n--- Tax district counts ---")
print(df["TAX_DISTRICT"].value_counts(dropna=False).to_string())
print("\nRows with TAX_DISTRICT other than 03:")
print(df[df["TAX_DISTRICT"].astype(str) != "03"][
    ["oid", "PARCEL_ID", "TAX_DISTRICT", "PROP_CLASS", "PARCEL_ACRES",
     "geom_acres", "PARCEL_ADD", "boundary"]].to_string(index=False))

print("\n--- The big acreage outlier group ---")
for pid in ("A-0714-0000-0000", "A-0714-0001-0000"):
    sub = df[df.PARCEL_ID == pid]
    print(f"\n{pid} ({len(sub)} rows)")
    print(sub[["oid", "TAX_DISTRICT", "PROP_CLASS", "PARCEL_ACRES", "geom_acres",
               "ratio", "PARCEL_ADD", "boundary"]].to_string(index=False))

print("\n--- Duplicate-ID groups with more than one geometry ---")
g = df[df.PARCEL_ID != ""].groupby("PARCEL_ID").agg(
    n=("oid", "size"), n_geom=("wkb", "nunique"))
multi = g[(g.n > 1) & (g.n_geom > 1)]
print(multi.to_string())
for pid in multi.index:
    sub = df[df.PARCEL_ID == pid]
    uniq = sub.drop_duplicates("wkb")
    print(f"\n{pid}  rows={len(sub)}  unique_geoms={len(uniq)}  "
          f"stated_acres={sub.PARCEL_ACRES.iloc[0]}  "
          f"unique_geom_acres={uniq.geom_acres.sum():.3f}")
    print(sub[["oid", "PARCEL_ACRES", "geom_acres", "PARCEL_ADD", "boundary"]]
          .to_string(index=False))

print("\n--- Boundary-straddling (partial) rows ---")
part = df[df.boundary == "partial"]
print(f"count: {len(part)}")
print(part[["oid", "PARCEL_ID", "TAX_DISTRICT", "PROP_CLASS", "PARCEL_ACRES",
            "PARCEL_ADD"]].head(12).to_string(index=False))
print("\nblank IDs among partial :", int((part.PARCEL_ID == "").sum()))
print("no assessor data among partial:",
      int(part[["SERIAL_NUM", "TAX_DISTRICT", "PROP_CLASS"]].isna().all(axis=1).sum()))
print("building data among partial  :", int(part["BLDG_SQFT"].notna().sum()), "/", len(part))
print("building data among within   :",
      int(df[df.boundary == "within"]["BLDG_SQFT"].notna().sum()), "/",
      int((df.boundary == "within").sum()))
