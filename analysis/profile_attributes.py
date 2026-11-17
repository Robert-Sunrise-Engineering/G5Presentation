"""Profile attributes of a parcel feature class for QC assessment."""
import sys
import re
import arcpy
import numpy as np
import pandas as pd

fc = sys.argv[1]
d = arcpy.Describe(fc)
attr_fields = [
    f.name for f in d.fields
    if f.type not in ("Geometry", "OID") and f.name not in ("SHAPE_Length", "SHAPE_Area")
]
with arcpy.da.SearchCursor(fc, attr_fields) as cur:
    df = pd.DataFrame.from_records(cur, columns=attr_fields)

str_cols = [
    c for c in df.columns
    if not pd.api.types.is_numeric_dtype(df[c])
    and not pd.api.types.is_datetime64_any_dtype(df[c])
]

print(f"Rows: {len(df):,}   Fields: {len(df.columns)}")
print("=" * 90)

print("\n--- Per-field completeness ---")
rows = []
for c in df.columns:
    s = df[c]
    nulls = s.isna().sum()
    if c in str_cols:
        as_str = s.astype("string")
        blank = as_str.str.strip().eq("").fillna(False).sum()
        kind = f"str distinct={s.nunique(dropna=True):,}"
    else:
        blank = 0
        kind = str(s.dtype)
    rows.append((c, len(df), nulls, 100 * nulls / len(df), blank, 100 * blank / len(df), kind))
comp = pd.DataFrame(rows, columns=["field", "n", "nulls", "null_%", "blanks", "blank_%", "dtype/distinct"])
print(comp.to_string(index=False, float_format=lambda x: f"{x:.1f}"))

print("\n--- Numeric summaries ---")
num = df.select_dtypes(include=[np.number])
summary = num.describe(percentiles=[0.01, 0.5, 0.99]).T
summary["zeros"] = (num == 0).sum()
summary["negatives"] = (num < 0).sum()
print(summary.to_string(float_format=lambda x: f"{x:,.2f}"))

print("\n--- Dates ---")
for c in df.columns:
    if pd.api.types.is_datetime64_any_dtype(df[c]):
        s = pd.to_datetime(df[c], errors="coerce")
        print(f"{c}: min={s.min()} max={s.max()} nulls={s.isna().sum():,} distinct={s.nunique():,}")

print("\n--- String values (low cardinality, <= 60) ---")
for c in str_cols:
    s = df[c].dropna().astype(str).str.strip()
    n = s.nunique()
    if 0 < n <= 60:
        print(f"\n[{c}] distinct={n:,}")
        print(s.value_counts(dropna=False).to_string())

print("\n--- High-cardinality string samples ---")
for c in str_cols:
    s = df[c].dropna().astype(str)
    n = s.nunique()
    if n > 60:
        print(f"\n[{c}] distinct={n:,}  sample: {s.head(5).tolist()}")

print("\n" + "=" * 90)
print("TARGETED QC CHECKS")
print("=" * 90)

def show(name, value):
    print(f"{name:62s} {value}")

# --- Identity fields ---
pid = df["PARCEL_ID"].astype(str).str.strip()
show("PARCEL_ID null", df["PARCEL_ID"].isna().sum())
show("PARCEL_ID duplicate rows (beyond first)", pid.duplicated().sum())
show("PARCEL_ID distinct", pid.nunique())
show("PARCEL_ID with leading/trailing whitespace", (df["PARCEL_ID"].astype(str) != pid).sum())
show("PARCEL_ID length distribution", dict(pid.str.len().value_counts().head(8)))
show("PARCEL_ID examples", pid.head(8).tolist())
dup_ids = pid[pid.duplicated(keep=False)].unique()
show("PARCEL_ID values appearing >1 time", len(dup_ids))
if len(dup_ids):
    show("  example duplicate IDs", list(dup_ids[:10]))

serial = df["SERIAL_NUM"].dropna().astype(str).str.strip()
show("SERIAL_NUM distinct (non-null)", serial.nunique())
show("SERIAL_NUM duplicate values", serial.duplicated().sum())
show("SERIAL_NUM examples", serial.head(5).tolist())

# --- County fields ---
for c in ("COUNTY_NAME", "COUNTY_ID"):
    show(f"{c} values", dict(df[c].astype(str).str.strip().value_counts(dropna=False)))

# --- Assessor block co-nullity ---
assessor_fields = ["SERIAL_NUM", "TAXEXEMPT_TYPE", "TAX_DISTRICT", "PROP_CLASS", "PRIMARY_RES"]
all_null = df[assessor_fields].isna().all(axis=1)
show("Rows with ALL assessor fields null", int(all_null.sum()))
show("Rows with SOME (not all) assessor fields null", int((df[assessor_fields].isna().any(axis=1) & ~all_null).sum()))

# --- Building block ---
bldg_fields = ["HOUSE_CNT", "BLDG_SQFT", "FLOORS_CNT", "BUILT_YR", "CONST_MATERIAL"]
bldg_all_null = df[bldg_fields].isna().all(axis=1)
bldg_any = df[bldg_fields].notna().any(axis=1)
show("Rows with ALL building fields null", int(bldg_all_null.sum()))
show("Rows with ANY building field present", int(bldg_any.sum()))
hc_num = pd.to_numeric(df["HOUSE_CNT"], errors="coerce")
show("HOUSE_CNT non-null, non-numeric", int((df["HOUSE_CNT"].notna() & hc_num.isna()).sum()))
show("HOUSE_CNT numeric values", dict(hc_num.value_counts(dropna=False).head(10)))
show("BLDG_SQFT > 0 but HOUSE_CNT null", int(((df["BLDG_SQFT"] > 0) & df["HOUSE_CNT"].isna()).sum()))
show("HOUSE_CNT > 0 but BLDG_SQFT null/0", int(((hc_num > 0) & (df["BLDG_SQFT"].isna() | (df["BLDG_SQFT"] == 0))).sum()))
show("BUILT_YR < 1850 or > 2024", int(((df["BUILT_YR"] < 1850) | (df["BUILT_YR"] > 2024)).sum()))
show("EFFBUILT_YR value range", (df["EFFBUILT_YR"].min(), df["EFFBUILT_YR"].max()))
show("EFFBUILT_YR < 1000 count (looks like age, not year)", int((df["EFFBUILT_YR"] < 1000).sum()))

# --- Value relationships ---
show("LAND_MKT_VALUE > TOTAL_MKT_VALUE", int((df["LAND_MKT_VALUE"] > df["TOTAL_MKT_VALUE"]).sum()))
show("LAND_MKT_VALUE == TOTAL_MKT_VALUE", int((df["LAND_MKT_VALUE"] == df["TOTAL_MKT_VALUE"]).sum()))
show("TOTAL_MKT_VALUE null but LAND_MKT_VALUE present", int((df["TOTAL_MKT_VALUE"].isna() & df["LAND_MKT_VALUE"].notna()).sum()))
show("LAND_MKT_VALUE null but TOTAL_MKT_VALUE present", int((df["LAND_MKT_VALUE"].isna() & df["TOTAL_MKT_VALUE"].notna()).sum()))
show("PARCEL_ACRES == 0 exactly", int((df["PARCEL_ACRES"] == 0).sum()))
show("PARCEL_ACRES < 0.001", int((df["PARCEL_ACRES"] < 0.001).sum()))
show("PARCEL_ACRES percentiles",
     {p: round(float(df["PARCEL_ACRES"].quantile(p)), 4) for p in (0.01, 0.1, 0.5, 0.9, 0.99)})

# --- Address ---
addr = df["PARCEL_ADD"].dropna().astype(str).str.strip()
show("PARCEL_ADD non-null", len(addr))
show("PARCEL_ADD duplicate normalized values (beyond first)",
     addr.str.upper().str.replace(r"\s+", " ", regex=True).duplicated().sum())
top_addr = addr.str.upper().str.replace(r"\s+", " ", regex=True).value_counts()
show("Most repeated addresses", top_addr.head(5).to_dict())
city = df["PARCEL_CITY"].astype(str).str.strip()
show("PARCEL_CITY values", dict(city.value_counts().head(25)))
show("PARCEL_ADD present but PARCEL_CITY null/blank", int((df["PARCEL_ADD"].notna() & city.isin(["", "nan", "None"])).sum()))

# --- Address format oddities ---
show("Addresses with no digits", int((~addr.str.contains(r"\d", regex=True)).sum()))
show("Addresses ending in unusual punctuation", int(addr.str.endswith((".", ",")).sum()))

# --- Tax district / exemption ---
td = df["TAX_DISTRICT"].dropna().astype(str).str.strip()
show("TAX_DISTRICT distinct", td.nunique())
show("TAX_DISTRICT length distribution", dict(td.str.len().value_counts()))
show("TAX_DISTRICT examples", td.head(10).tolist())

# --- Metadata fields ---
show("CURRENT_ASOF distinct values", sorted(map(str, df["CURRENT_ASOF"].dropna().unique())))
show("ASSESSOR_SRC unique", df["ASSESSOR_SRC"].nunique(dropna=False))
show("ASSESSOR_SRC sample", df["ASSESSOR_SRC"].dropna().astype(str).head(1).tolist())
