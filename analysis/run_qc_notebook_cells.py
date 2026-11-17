import json, sys, traceback

nb_path = r"C:\Users\user\projects\G5Presentation\demo\Pro Projects\Notebooks\qc_demo.ipynb"
with open(nb_path, encoding="utf-8") as f:
    nb = json.load(f)

ns = {"__name__": "__main__"}
for i, cell in enumerate(nb["cells"], 1):
    if cell["cell_type"] != "code":
        continue
    src = "".join(cell["source"])
    print(f"\n===== CELL {i} =====", flush=True)
    try:
        exec(compile(src, f"<cell {i}>", "exec"), ns)
    except Exception:
        traceback.print_exc()
        print(f"FAILED at cell {i}")
        sys.exit(1)
print("\nALL CELLS RAN")
