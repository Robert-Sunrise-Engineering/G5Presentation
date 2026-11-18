"""Guardrail rewording per user feedback 2026-11-18:
the model CAN and MUST read data/specs; it runs local OR in a private/secure
cloud; what it never gets is write access / acting tools."""
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

FG     = RGBColor(0xEC, 0xE7, 0xDE)
MUTED  = RGBColor(0x99, 0xA2, 0xAD)
ACCENT = RGBColor(0xE8, 0x86, 0x2B)
GOOD   = RGBColor(0x4F, 0xA8, 0x62)
F_BODY, F_MONO = "Lato", "Roboto Mono"

prs = Presentation(r"slides/deck_g5.pptx")
slides = list(prs.slides)

def find_all(slide, needle):
    return [sh for sh in slide.shapes if sh.has_text_frame and needle in sh.text_frame.text]

def rewrite_framed(sh, tag, tcolor, paras):
    """Card text frame: para0 = mono tag, then body paragraphs (str or run-lists)."""
    tf = sh.text_frame
    tf.clear()
    p0 = tf.paragraphs[0]
    r = p0.add_run(); r.text = tag
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = F_MONO, Pt(10.5), True, tcolor
    p0.space_after = Pt(10)
    for para in paras:
        p = tf.add_paragraph(); p.line_spacing = 1.2; p.space_after = Pt(4)
        items = [(para, {})] if isinstance(para, str) else para
        for text, st in items:
            rr = p.add_run(); rr.text = text
            rr.font.name = st.get("font", F_BODY)
            rr.font.size = Pt(st.get("size", 12))
            rr.font.bold = st.get("bold", False)
            rr.font.color.rgb = st.get("color", FG)

# — safety slide · card 1 —
sh = find_all(slides[4], "RUNS LOCAL")[0]
rewrite_framed(sh, "DATA BOUNDARY", GOOD, [
    [("The model has to read the data and the specs — that’s its input. It runs where you control the boundary: ", {}),
     ("your workstation or a private, secure cloud (a hosted Ollama, for example).", {"bold": True})],
    [("Open weights, no API keys — nothing crosses out of it.", {"color": MUTED})],
])
# — safety slide · card 2 —
sh = find_all(slides[4], "NO TOOLS")[0]
rewrite_framed(sh, "READS · NEVER WRITES", ACCENT, [
    [("It gets the read access it needs — data, specs, schemas. What it never gets: ", {}),
     ("write access, network tools, anything that acts.", {"bold": True})],
    [("It returns proposals; deterministic code acts on them. The one time it drove an agent harness, it failed on nearly every tool call — and it doesn’t get that job anyway.", {"color": MUTED})],
])
# — safety slide · bottom line —
for sh in find_all(slides[4], "guardrails aren"):
    tf = sh.text_frame
    p0 = tf.paragraphs[0]
    for r in list(p0.runs):
        r._r.getparent().remove(r._r)
    for text, st in [("The guardrails aren’t policy documents — they’re ", {"color": MUTED}),
                     ("the design.", {"color": FG, "bold": True}),
                     (" The model sees everything it needs to see; it just can’t write, ship, or decide.", {"color": MUTED})]:
        r = p0.add_run(); r.text = text
        r.font.name, r.font.size = F_BODY, Pt(12.5)
        r.font.color.rgb = st["color"]; r.font.bold = st.get("bold", False)

# — spectrum slide · zone 1 footer: read vs write, precisely —
for sh in find_all(slides[3], "no data touched"):
    sh.text_frame.paragraphs[0].runs[0].text = "reads everything — writes nothing"

prs.save(r"slides/deck_g5.pptx")
print("guardrails reworded; zone-1 footer fixed")
