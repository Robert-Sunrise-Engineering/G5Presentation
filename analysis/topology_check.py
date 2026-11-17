"""Topology check: parcel overlaps, classified by identifier/geometry relationship."""
import sys, os, tempfile, time
import arcpy
import numpy as np

fc = sys.argv[1]
t0 = time.time()
tmp = tempfile.mkdtemp(prefix="iron_topo_")
gdb = os.path.join(tmp, "topo.gdb")
arcpy.management.CreateFileGDB(tmp, "topo.gdb")
sr = arcpy.Describe(fc).spatialReference
fd = os.path.join(gdb, "fd")

arcpy.management.CreateFeatureDataset(gdb, "fd", sr)
parcels = os.path.join(fd, "parcels")
arcpy.management.CopyFeatures(fc, parcels)
topo = os.path.join(fd, "topo")
arcpy.management.CreateTopology(fd, "topo", 1)
arcpy.management.AddFeatureClassToTopology(topo, parcels, 1, 1)
arcpy.management.AddRuleToTopology(topo, "Must Not Overlap (Area)", parcels)
print("validating...")
t = time.time()
arcpy.management.ValidateTopology(topo)
print(f"validated in {time.time()-t:.1f}s")
arcpy.management.ExportTopologyErrors(topo, fd, "errs")
poly = os.path.join(fd, "errs_poly")

# OID -> identity on the copied layer (same OIDs as error table)
info = {}
with arcpy.da.SearchCursor(parcels, ["OID@", "PARCEL_ID", "PROP_CLASS", "SHAPE@"]) as cur:
    for oid, pid, cls, g in cur:
        info[oid] = (
            (pid or "").strip(),
            cls,
            g.WKB if g is not None else None,
            g.area if g is not None else 0.0,
        )

errs = []
with arcpy.da.SearchCursor(
    poly, ["OriginObjectID", "DestinationObjectID", "SHAPE@AREA"]
) as cur:
    for o, de, a in cur:
        errs.append((o, de, a))

print(f"overlap error polygons: {len(errs):,}")
classes = {"identical geometry": 0, "same PARCEL_ID, different geometry": 0,
           "different PARCEL_ID": 0, "blank PARCEL_ID involved": 0}
areas = {k: [] for k in classes}
by_class_pair = {}
top = []
for o, de, a in errs:
    p1, c1, g1, _ = info.get(o, ("", None, None, 0.0))
    p2, c2, g2, _ = info.get(de, ("", None, None, 0.0))
    if g1 is not None and g2 is not None and g1 == g2:
        k = "identical geometry"
    elif p1 == "" or p2 == "":
        k = "blank PARCEL_ID involved"
    elif p1 == p2:
        k = "same PARCEL_ID, different geometry"
    else:
        k = "different PARCEL_ID"
    classes[k] += 1
    areas[k].append(a)
    if k == "different PARCEL_ID":
        key = tuple(sorted([c1 or "<null>", c2 or "<null>"]))
        by_class_pair[key] = by_class_pair.get(key, 0) + 1
        top.append((a, p1, p2, c1, c2))

for k, n in classes.items():
    a = np.array(areas[k], dtype=float)
    if len(a):
        print(f"{k:38s} n={n:6,}  median={np.median(a):9,.1f}  max={a.max():14,.1f}  sum={a.sum():16,.1f}")
    else:
        print(f"{k:38s} n=0")

print("\nTop 15 cross-parcel overlaps:")
top.sort(reverse=True)
for a, p1, p2, c1, c2 in top[:15]:
    print(f"  {a:14,.1f} m2  {p1:22s} ({c1})  <->  {p2:22s} ({c2})")

print("\nCross-parcel overlap count by class pair (top 10):")
for key, n in sorted(by_class_pair.items(), key=lambda x: -x[1])[:10]:
    print(f"  {key[0]:45s} <-> {key[1]:45s} {n:,}")

print(f"\nelapsed {time.time()-t0:.1f}s  scratch={tmp}")
