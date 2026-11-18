"""Fix 'field survey' -> 'filed survey' on the reviewer slide (the phrase is
split across two runs: 'field' + ' survey…')."""
from pptx import Presentation

prs = Presentation(r"slides/deck_g5_full.pptx")

for slide in prs.slides:
    if "3pm map-tech" not in " ".join(sh.text_frame.text for sh in slide.shapes if sh.has_text_frame):
        continue
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        for p in sh.text_frame.paragraphs:
            runs = p.runs
            for i in range(len(runs) - 1):
                if runs[i].text == "field" and runs[i + 1].text.startswith(" survey"):
                    runs[i].text = "filed"
                    break

prs.save(r"slides/deck_g5_full.pptx")
print("field survey -> filed survey")
