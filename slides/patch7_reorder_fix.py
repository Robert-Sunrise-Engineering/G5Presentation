"""Reorder Utah County before the Close, renumber counters, drop the
"exact footprint" bullet on the duplicate-IDs slide, and fix typos.

Run:  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" slides\\patch7_reorder_fix.py
"""
import re
from pptx import Presentation

prs = Presentation(r"slides/deck_g5_full.pptx")

# ————— 1. move the Close slide (index 12) to the end —————
sldIdLst = prs.slides._sldIdLst
close = sldIdLst[12]           # "THE RULES ALREADY SAY THIS" slide
sldIdLst.remove(close)
sldIdLst.append(close)

# ————— 2. renumber counters to match physical order —————
COUNTER = re.compile(r"\d{2} / 15")
for i, slide in enumerate(prs.slides):
    if i == 0:                 # title slide has no counter
        continue
    num = f"{i+1:02d} / 15"
    for sh in slide.shapes:
        if sh.has_text_frame and COUNTER.fullmatch(sh.text_frame.text.strip()):
            p = sh.text_frame.paragraphs[0]
            if p.runs:
                p.runs[0].text = num
                for extra in p.runs[1:]:
                    extra.text = ""
            break

# ————— 3. drop the "share an exact footprint" bullet (duplicate-IDs slide) —————
for slide in prs.slides:
    for sh in slide.shapes:
        if sh.has_text_frame and "share an exact footprint" in sh.text_frame.text:
            for p in list(sh.text_frame.paragraphs):
                if "share an exact footprint" in p.text:
                    p._p.getparent().remove(p._p)
                    break
            break

# ————— 4. fix typos (run-level replacements) —————
RUN_REPLACEMENTS = [
    ("makes the decisions", "make the decisions"),      # slide 3
    ("lets it acts", "lets it act"),                    # slide 5
    ("executed a change", "executes a change"),         # slide 5
    ("once its approved", "once it\u2019s approved"),   # slide 5
    ("keeps angles", "keep angles"),                    # mercator
    ("field survey", "filed survey"),                   # reviewer
]
APOS = r"[\u2019'\u0027]"
DOESNT = re.compile(r"DOESNT(" + APOS + r")")

for slide in prs.slides:
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            for r in p.runs:
                t = r.text
                for old, new in RUN_REPLACEMENTS:
                    t = t.replace(old, new)
                t = DOESNT.sub(lambda m: "DOESN" + m.group(1) + "T", t)
                if t != r.text:
                    r.text = t

prs.save(r"slides/deck_g5_full.pptx")
print("reordered + renumbered + dropped bullet + fixed typos")
