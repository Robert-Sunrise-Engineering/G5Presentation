"""Dump text + speaker notes of pptx files to UTF-8 text files for review.
Run with ArcGIS Pro Python (no -I)."""
import sys, io
from pptx import Presentation

def dump(path, out):
    prs = Presentation(path)
    lines = []
    lines.append("=" * 80)
    lines.append(f"FILE: {path} | slides: {len(prs.slides._sldIdLst)}")
    lines.append("=" * 80)
    for i, slide in enumerate(prs.slides, 1):
        lines.append(f"\n----- SLIDE {i} -----")
        items = []
        for sh in slide.shapes:
            if sh.has_text_frame:
                t = "\n".join(p.text for p in sh.text_frame.paragraphs if p.text.strip())
                if t.strip():
                    items.append((sh.top or 0, sh.left or 0, t))
        items.sort(key=lambda r: (r[0], r[1]))
        for top, left, t in items:
            lines.append(f"  [{t}]")
        if slide.has_notes_slide:
            n = slide.notes_slide.notes_text_frame.text
            if n.strip():
                lines.append("  --- NOTES ---")
                for ln in n.strip().split("\n"):
                    lines.append("  " + ln)
    with io.open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("wrote", out)

if __name__ == "__main__":
    for p in sys.argv[1:]:
        out = p[:-5] + ".dump.txt"
        dump(p, out)
