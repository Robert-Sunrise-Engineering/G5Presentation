"""Patch the user-edited deck_g5.pptx: polish draft text, draft the safety
slide, renumber counters to /15. Run with arcgispro-py3 python."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# palette / fonts (same as build script)
FG     = RGBColor(0xEC, 0xE7, 0xDE)
MUTED  = RGBColor(0x99, 0xA2, 0xAD)
FAINT  = RGBColor(0x6B, 0x74, 0x80)
LINE   = RGBColor(0x2B, 0x33, 0x3D)
PANEL  = RGBColor(0x1A, 0x1F, 0x26)
ACCENT = RGBColor(0xE8, 0x86, 0x2B)
ADIM   = RGBColor(0x8A, 0x53, 0x20)
GOOD   = RGBColor(0x4F, 0xA8, 0x62)
F_BODY, F_MONO, F_DISP = "Lato", "Roboto Mono", "Oswald"

prs = Presentation(r"slides/deck_g5.pptx")
slides = list(prs.slides)

def find(slide, needle):
    """text frame whose text contains needle"""
    for sh in slide.shapes:
        if sh.has_text_frame and needle in sh.text_frame.text:
            return sh
    raise KeyError(f"not found: {needle!r}")

def first_run_style(tf):
    for p in tf.paragraphs:
        for r in p.runs:
            if r.text.strip():
                f = r.font
                return dict(
                    name=f.name or F_BODY,
                    size=f.size.pt if f.size else 14,
                    bold=bool(f.bold),
                    color=(f.color.rgb if f.color and f.color.type is not None else FG),
                )
    return dict(name=F_BODY, size=14, bold=False, color=FG)

def rewrite(shape, paras, size=None, font=None, spacing=None, line_spacing=None,
            align=None, bullet=False):
    """paras: list of paragraphs; each = str or list of (text, style-dict) runs.
    Preserves per-shape base font unless overridden."""
    base = first_run_style(shape.text_frame)
    base_name = font or base["name"]
    base_size = size or base["size"]
    tf = shape.text_frame
    tf.word_wrap = True
    tf.clear()
    first = True
    for para in paras:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        if align is not None: p.alignment = align
        if spacing is not None: p.space_after = Pt(spacing)
        if line_spacing is not None: p.line_spacing = line_spacing
        items = [(para, {})] if isinstance(para, str) else para
        if bullet:
            pr = p.add_run(); pr.text = "•   "
            pr.font.name, pr.font.size, pr.font.bold = base_name, Pt(base_size), True
            pr.font.color.rgb = ACCENT
        for text, st in items:
            r = p.add_run(); r.text = text
            f = r.font
            f.name = st.get("font", base_name)
            f.size = Pt(st.get("size", base_size))
            f.bold = st.get("bold", base["bold"])
            f.color.rgb = st.get("color", base["color"])
            f.color.rgb = st.get("color", base["color"])

def set_counter(slide, n):
    for sh in slide.shapes:
        if sh.has_text_frame and "/ 14" in sh.text_frame.text:
            base = first_run_style(sh.text_frame)
            rewrite(sh, [f"{n:02d} / 15"], font=F_MONO, size=base["size"], align=PP_ALIGN.RIGHT)
            return True
    return False

# ————— SLIDE 2 · problem —————
s = slides[1]
sh = find(s, "seen for years to come")
rewrite(sh, [
    "A project never goes as planned. Deadlines and budgets near an end.",
    "Some mistakes are caught. Others aren’t seen for years to come.",
], size=14.5, spacing=12, line_spacing=1.2, bullet=True)
set_counter(s, 2)

# ————— SLIDE 3 · pitch —————
s = slides[2]
sh = find(s, "What if we could keep the budget")
rewrite(sh, [[("What if we keep the budget — and do ", {"color": FG}),
              ("4–5× the checks.", {"color": ACCENT})]],
        font=F_DISP, size=40)
sh = find(s, "deterministic Pipeline")
rewrite(sh, ["Build a deterministic pipeline to verify what we normally couldn’t"],
        font=F_MONO, size=10.5)
sh = find(s, "phone numbers,")
rewrite(sh, ["Check acreage.", "Validate addresses, phone numbers, owner names."],
        size=13, spacing=8, line_spacing=1.15, bullet=True)
sh = find(s, "Can Watch THE EDGES")
rewrite(sh, ["The LLM watches the edges"], font=F_MONO, size=10.5)
sh = find(s, "memos, written")
rewrite(sh, [
    "it reads the spec and reviews our schema → gap report, in minutes",
    "recommends better domains",
    "writes accurate metadata",
    "drafts new checks → a human reviews, owns it",
    "verified findings → memos, written",
    "deterministic checks stop competing — they run",
], size=12.5, spacing=5, line_spacing=1.15, bullet=True)
sh = find(s, "stob")
rewrite(sh, [[("The language-shaped parts stop being as slow and tedious to check. ", {"color": FG}),
              ("QC improves the data immediately, and gets better each time we run through it.", {"color": FG, "bold": True}),
              ("  The model never touches the geometry, never makes the decisions.", {"color": MUTED})]],
        size=13.5, line_spacing=1.25)
set_counter(s, 3)

# ————— SLIDE 4 · spectrum —————
s = slides[3]
sh = find(s, "Bad at Math")
rewrite(sh, [[("Good at language. Bad at math — and at your actual workflows.", {"color": FG}),
              ("  So place it.", {"color": ACCENT})]], font=F_DISP, size=32)
set_counter(s, 4)

# ————— SLIDE 5 · safety (drafted) —————
s = slides[4]
sh = find(s, "Good at language. Bad at math. So place it.")
rewrite(sh, [[("It’s safe because of what it ", {"color": FG}),
              ("can’t do.", {"color": ACCENT})]], font=F_DISP, size=40)
find(s, "Things like:")._element.getparent().remove(find(s, "Things like:")._element)

def safety_card(x, tag, color, lines):
    card = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.0), Inches(3.93), Inches(3.3))
    card.fill.solid(); card.fill.fore_color.rgb = PANEL
    card.line.color.rgb = LINE; card.line.width = Pt(1.0)
    card.shadow.inherit = False
    try: card.adjustments[0] = 0.04
    except Exception: pass
    txt = card.text_frame
    txt.word_wrap = True
    txt.margin_left = txt.margin_right = Inches(0.22)
    txt.margin_top = Inches(0.18); txt.margin_bottom = Inches(0.12)
    p0 = txt.paragraphs[0]; p0.alignment = PP_ALIGN.LEFT
    r = p0.add_run(); r.text = tag
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = F_MONO, Pt(10.5), True, color
    p0.space_after = Pt(10)
    for line in lines:
        p = txt.add_paragraph(); p.line_spacing = 1.2; p.space_after = Pt(4)
        runs = [(line, {})] if isinstance(line, str) else line
        for t, st in runs:
            rr = p.add_run(); rr.text = t
            rr.font.name = st.get("font", F_BODY)
            rr.font.size = Pt(st.get("size", 12))
            rr.font.bold = st.get("bold", False)
            rr.font.color.rgb = st.get("color", FG)

safety_card(0.6, "RUNS LOCAL", GOOD, [
    [("One workstation, one open-weights model (gemma4:12b, Apache 2.0). ", {"color": MUTED}),
     ("No cloud, no API keys — the data never leaves the box.", {"color": FG, "bold": True})],
])
safety_card(4.7, "NO TOOLS · NO INTERNET", ACCENT, [
    "The model gets no buttons and no browsing. It returns proposals; deterministic code acts on them.",
    [("The one time it was handed an agent harness, it failed on nearly every tool call.", {"color": MUTED})],
])
safety_card(8.8, "HUMAN SIGN-OFF · LABELED RECORDS", ACCENT, [
    "Every proposed edit waits for a person’s approval.",
    [("Anything the LLM wrote is labeled “AI-drafted, human-reviewed” and kept as a government record (GRAMA).", {"color": MUTED})],
])
txt = None  # noqa
tb = s.shapes.add_textbox(Inches(0.6), Inches(5.6), Inches(12.13), Inches(0.5))
tf = tb.text_frame; tf.word_wrap = True
p = tf.paragraphs[0]
for t, st in [("The guardrails aren’t policy documents — they’re ", {"color": MUTED}),
              ("the design", {"color": FG, "bold": True}),
              (". Each one is enforced by code that doesn’t care what the model says.", {"color": MUTED})]:
    r = p.add_run(); r.text = t
    r.font.name, r.font.size = F_BODY, Pt(12.5)
    r.font.color.rgb = st["color"]; r.font.bold = st.get("bold", False)
set_counter(s, 5)

# ————— SLIDES 6–7 · county (renumber) —————
set_counter(slides[5], 6)
set_counter(slides[6], 7)

prs.save(r"slides/deck_g5.pptx")
print("patched: slides 2-7 polished/drafted, counters n/15")
