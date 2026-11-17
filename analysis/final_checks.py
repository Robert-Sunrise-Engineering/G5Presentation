"""Final targeted checks: blank/unattributed rows, duplicate geometry vs acreage, building outliers."""
import sys, os, tempfile, hashlib
import arcpy
import numpy as np
import pandas as pd

fc = sys.argv[1]
d = arcpy.Describe(fc)
fields = [f.name for f in d.fields if f.type not in ("Geometry", "OID", "Blob")]

rows = []
with arcpy.da.SearchCursor(fc, ["OID@", "SHAPE@"] + fields) as cur:
    for r in cur:
        oid, g = r[0], r[1]
        rows.append([oid, hashlib.sha1(g.WKB).hexdigest() if g else None] + list(r[2:]))
df = pd.DataFrame(rows, columns=["oid", "wkb_sha1"] + fields)
df["PARCEL_ID"] = df["PARCEL_ID"].fillna("").astype(str).str.strip()

# ---------- blank-ID geometry relationship ----------
nonblank_hash = set(df.loc[df.PARCEL_ID != "", "wkb_sha1"].dropna())
blank = df[df.PARCEL_ID == ""]
blank_match = blank["wkb_sha1"].isin(nonblank_hash).sum()
print(f"Blank-ID rows                        : {len(blank):,}")
print(f"  ...geometry also used by an attributed row: {blank_match:,} "
      f"({blank_match/len(blank)*100:.1f}%)")
print(f"  ...geometry unique to blank rows           : {len(blank)-blank_match:,}")

# ---------- rows with ID but no assessor attributes ----------
assessor = ["SERIAL_NUM", "TAXEXEMPT_TYPE", "TAX_DISTRICT", "PROP_CLASS", "PRIMARY_RES"]
noattr = df[(df.PARCEL_ID != "") & df[assessor].isna().all(axis=1)]
print(f"\nRows with ID but all assessor fields null: {len(noattr):,}")
print(noattr[["PARCEL_ID", "SERIAL_NUM", "PARCEL_ADD", "PARCEL_ACRES"]].head(5).to_string(index=False))

# ---------- placeholder ID rows ----------
ph = df[df.PARCEL_ID == "9999999"]
print(f"\nRows with PARCEL_ID '9999999'          : {len(ph):,}")
print(ph[["PARCEL_ID", "PROP_CLASS", "PARCEL_ACRES", "SUBDIV_NAME"]].head(5).to_string(index=False))

# ---------- duplicate geometry vs acreage consistency ----------
tmp = tempfile.mkdtemp(prefix="iron_final_")
arcpy.management.CreateFileGDB(tmp, "s.gdb")
proj = os.path.join(tmp, "s.gdb", "p5070")
arcpy.management.Project(fc, proj, arcpy.SpatialReference(5070))
ao = []
with arcpy.da.SearchCursor(proj, ["OID@", "SHAPE@AREA"]) as cur:
    for oid, a in cur:
        ao.append((oid, a))
alb = pd.DataFrame(ao, columns=["oid", "area_5070"])
df = df.merge(alb, on="oid", how="left")
df["ratio"] = df["PARCEL_ACRES"] * 4046.8564224 / df["area_5070"]

gh = df.groupby("wkb_sha1").size()
df["geom_copies"] = df["wkb_sha1"].map(gh)
df["severe"] = (df["ratio"] > 1.25) | (df["ratio"] < 0.8)
ok = df.dropna(subset=["ratio", "geom_copies"])
ok = ok[ok.PARCEL_ACRES >= 0.05]
print("\nAcreage mismatch rate by geometry-copy count:")
for label, subset in [
    ("unique geometry", ok[ok.geom_copies == 1]),
    ("geometry shared by 2", ok[ok.geom_copies == 2]),
    ("geometry shared by 3-9", ok[ok.geom_copies.between(3, 9)]),
    ("geometry shared by 10+", ok[ok.geom_copies >= 10]),
]:
    print(f"  {label:26s} n={len(subset):6,}  severe mismatch={subset.severe.mean()*100:5.1f}%")

print("\nTotal area overcount from repeated geometry:")
df["a5070"] = df["area_5070"]
dup_rows = df[df.geom_copies > 1]
uniq_area = df.drop_duplicates("wkb_sha1")["a5070"].sum()
all_area = df["a5070"].sum()
print(f"  sum of all polygon areas : {all_area/1e6:,.1f} km2")
print(f"  sum over unique geometries: {uniq_area/1e6:,.1f} km2")
print(f"  overcount                 : {(all_area-uniq_area)/1e6:,.1f} km2 "
      f"({(all_area/uniq_area-1)*100:.1f}%)")

# ---------- same-PID duplicate-geometry examples ----------
g2 = df[df.PARCEL_ID != ""].groupby("PARCEL_ID")
stats = g2.agg(n=("oid", "size"), n_geom=("wkb_sha1", "nunique"), n_attr=("PARCEL_ACRES", "nunique"))
cand = stats[(stats.n_geom < stats.n) & (stats.n > 1)]
print(f"\nExample groups with repeated geometry but differing rows "
      f"({len(cand):,} candidate groups):")
for pid in cand.sort_values("n", ascending=False).head(2).index:
    sub = df[df.PARCEL_ID == pid]
    print(f"\n  PARCEL_ID={pid}  rows={len(sub)}  distinct geometry={sub.wkb_sha1.nunique()}")
    print(sub[["PARCEL_ID", "SERIAL_NUM", "PROP_CLASS", "PARCEL_ACRES", "PARCEL_ADD",
               "SUBDIV_NAME", "geom_copies"]].head(8).to_string(index=False))

# ---------- building outliers ----------
print("\n--- Building-value outliers ---")
print(f"BLDG_SQFT <= 10 sqft      : {(df.BLDG_SQFT <= 10).sum():,}")
print(f"BLDG_SQFT > 100,000 sqft  : {(df.BLDG_SQFT > 100000).sum():,}")
print(f"BLDG_SQFT 1 sqft          : {(df.BLDG_SQFT == 1).sum():,}")
big = df[df.BLDG_SQFT > 100000]
print(big[["PARCEL_ID", "PROP_CLASS", "BLDG_SQFT", "HOUSE_CNT", "BUILT_YR"]].head(5).to_string(index=False))

# ---------- EFFBUILT_YR semantics ----------
print("\n--- EFFBUILT_YR vs BUILT_YR ---")
b = df.dropna(subset=["BUILT_YR", "EFFBUILT_YR"])
print(f"rows with both: {len(b):,}")
print("EFFBUILT_YR percentiles:", {p: float(b.EFFBUILT_YR.quantile(p)) for p in (.01,.5,.99)})
print("BUILT_YR percentiles   :", {p: float(b.BUILT_YR.quantile(p)) for p in (.01,.5,.99)})
print(f"EFFBUILT_YR would be a year <1980: {(b.EFFBUILT_YR < 1980).sum():,} "
      f"({(b.EFFBUILT_YR < 1980).mean()*100:.1f}% of non-null)")
