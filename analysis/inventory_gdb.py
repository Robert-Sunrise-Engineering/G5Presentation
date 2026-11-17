"""Inventory a File Geodatabase: datasets, schema, domains, subtypes, row counts."""
import sys
import arcpy

gdb = sys.argv[1]
arcpy.env.workspace = gdb

print(f"Workspace: {gdb}")
print("=" * 80)

print("\n--- Feature classes ---")
for fc in arcpy.ListFeatureClasses():
    d = arcpy.Describe(fc)
    sr = d.spatialReference
    print(f"\n{fc}")
    print(f"  shapeType : {d.shapeType}")
    print(f"  sr        : {sr.name} (wkid {sr.factoryCode})")
    try:
        print(f"  rows      : {arcpy.management.GetCount(fc)[0]}")
    except Exception as e:
        print(f"  rows      : ERROR {e}")
    try:
        print(f"  subtypes  : {[(s.name, s.subtypeField) for s in d.subtypes]}")
    except Exception as e:
        print(f"  subtypes  : ERROR {e}")
    print("  fields:")
    for f in d.fields:
        extra = f" len={f.length}" if f.type in ("String",) else ""
        dom = f" domain={f.domain}" if getattr(f, "domain", None) else ""
        print(f"    {f.name:28s} {f.type:12s} alias={f.aliasName!r}{extra}{dom}")

print("\n--- Tables ---")
for t in arcpy.ListTables():
    d = arcpy.Describe(t)
    print(f"\n{t}  rows={arcpy.management.GetCount(t)[0]}")
    for f in d.fields:
        print(f"    {f.name:28s} {f.type:12s}")

print("\n--- Domains ---")
try:
    for dom in arcpy.da.ListDomains(gdb):
        vals = dom.codedValues if dom.domainType == "CodedValue" else list(dom.range or [])
        print(f"  {dom.name:30s} {dom.domainType:20s} field={dom.type!r} values={vals}")
except Exception as e:
    print(f"  ERROR: {e}")
