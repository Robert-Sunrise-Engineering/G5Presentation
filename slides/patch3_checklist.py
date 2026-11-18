"""Expand slide 3's deterministic-checks card with the data-grounded checks."""
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

ACCENT = RGBColor(0xE8, 0x86, 0x2B)

prs = Presentation(r"slides/deck_g5.pptx")
s = list(prs.slides)[2]  # slide 3 · pitch

for sh in s.shapes:
    if sh.has_text_frame and "Validate addresses" in sh.text_frame.text:
        base_name = "Lato"
        tf = sh.text_frame
        tf.clear()
        checks = [
            "Check stated acres against equal-area geometry.",
            "Validate addresses, phone numbers, owner names.",
            "Flag blank, placeholder, and all-zero IDs.",
            "Count rows per parcel ID — one parcel, many buildings.",
            "Find duplicated footprints and sliver polygons.",
            "Cross-check the rest — contradictions, ranges, snapshot age.",
        ]
        first = True
        for line in checks:
            p = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            p.space_after = Pt(5)
            p.line_spacing = 1.12
            b = p.add_run(); b.text = "•   "
            b.font.name, b.font.size, b.font.bold, b.font.color.rgb = base_name, Pt(12.5), True, ACCENT
            r = p.add_run(); r.text = line
            r.font.name, r.font.size, r.font.color.rgb = base_name, Pt(12.5), RGBColor(0xEC, 0xE7, 0xDE)
        break
else:
    raise SystemExit("slide 3 check card not found")

prs.save(r"slides/deck_g5.pptx")
print("slide 3: 6 deterministic checks in place")
