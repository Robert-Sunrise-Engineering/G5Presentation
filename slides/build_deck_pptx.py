"""
Build the G5 talk deck as a .pptx for Google Slides import.
Run:  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" slides\\build_deck_pptx.py
Output: slides\\deck_g5.pptx  (slides 1-7 of 14)
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ——— palette (single dark look, matches slides/deck.html) ———
BG     = RGBColor(0x12, 0x15, 0x1A)
PANEL  = RGBColor(0x1A, 0x1F, 0x26)
PANEL2 = RGBColor(0x22, 0x29, 0x33)
FG     = RGBColor(0xEC, 0xE7, 0xDE)
MUTED  = RGBColor(0x99, 0xA2, 0xAD)
FAINT  = RGBColor(0x6B, 0x74, 0x80)
LINE   = RGBColor(0x2B, 0x33, 0x3D)
ACCENT = RGBColor(0xE8, 0x86, 0x2B)
ADIM   = RGBColor(0x8A, 0x53, 0x20)
GOOD   = RGBColor(0x4F, 0xA8, 0x62)
WARN   = RGBColor(0xDF, 0xAF, 0x3B)
BAD    = RGBColor(0xD4, 0x57, 0x4E)
BASEBAR= RGBColor(0x39, 0x42, 0x4E)
TINT   = RGBColor(0x21, 0x1D, 0x1B)   # accent ~7% over bg

F_DISP = "Oswald"        # display / headings
F_BODY = "Lato"          # body
F_MONO = "Roboto Mono"   # eyebrows, data, tags

W, H   = 13.333, 7.5
PAD    = 0.6
CW     = W - 2 * PAD     # 12.13 content width

prs = Presentation()
prs.slide_width  = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]

TOTAL = 14

# ——————————————————————— helpers ———————————————————————

def new_slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    return s

def no_line(shape):
    shape.line.fill.background()
    return shape

def solid(shape, fill=None, line=None, width=1.0):
    if fill is None:
        shape.fill.background()
    else:
        shape.fill.solid()
        shape.fill.fore_color.rgb = fill
    if line is None:
        shape.line.fill.background()
    else:
        shape.line.color.rgb = line
        shape.line.width = Pt(width)
    try:
        shape.shadow.inherit = False
    except Exception:
        pass
    return shape

def rect(s, x, y, w, h, fill=PANEL, line=LINE, width=1.0, round_=0.0):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE
    sh = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if round_:
        try: sh.adjustments[0] = round_
        except Exception: pass
    sh.text_frame.paragraphs[0].text = ""
    return solid(sh, fill, line, width)

def txt(s, x, y, w, h, runs, size=14, color=FG, font=F_BODY, bold=False,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, line_spacing=None,
        wrap=True):
    """runs: str, or list of paragraphs; each paragraph str or list of (text, dict) runs."""
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = wrap
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if isinstance(runs, str):
        runs = [runs]
    first = True
    for para in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        if spacing is not None:
            p.space_after = Pt(spacing)
        if line_spacing is not None:
            p.line_spacing = line_spacing
        items = [(para, {})] if isinstance(para, str) else para
        for text, style in items:
            r = p.add_run()
            r.text = text
            f = r.font
            f.name  = style.get("font", font)
            f.size  = Pt(style.get("size", size))
            f.bold  = style.get("bold", bold)
            f.color.rgb = style.get("color", color)
            if style.get("italic"): f.italic = True
    return tb

def eyebrow(s, label, n):
    txt(s, PAD, 0.32, 8.0, 0.3, label.upper(), size=11, color=FAINT, font=F_MONO, wrap=False)
    txt(s, W - PAD - 1.4, 0.32, 1.4, 0.3, f"{n:02d} / {TOTAL}", size=11, color=ACCENT,
        font=F_MONO, wrap=False, align=PP_ALIGN.RIGHT)

def footer(s):
    ln = rect(s, PAD, 6.98, CW, 0.005, fill=LINE, line=None)
    txt(s, PAD, 7.1, 7.5, 0.3, "TRUST BUT VERIFY", size=9, color=FAINT, font=F_MONO, wrap=False)
    txt(s, W - PAD - 5.5, 7.1, 5.5, 0.3, "gemma4:12b · Ollama · ArcGIS Pro 3.7 · UGRC parcels (CC BY 4.0)",
        size=9, color=FAINT, font=F_MONO, wrap=False, align=PP_ALIGN.RIGHT)

def headline(s, runs, size=40, y=0.85, h=1.0, align=PP_ALIGN.LEFT):
    txt(s, PAD, y, CW, h, runs, size=size, font=F_DISP, bold=True, align=align)
    return y + h

def bullets(s, x, y, w, items, size=13.5, gap=6, line_h=0.42, color=FG):
    tb = txt(s, x, y, w, 0.4 * len(items) * (size / 13.5) + 0.1,
             [[("•  ", {"color": ACCENT, "bold": True}), (it, {})] for it in items],
             size=size, spacing=gap, line_spacing=1.15)
    return tb

def notes(s, text):
    s.notes_slide.notes_text_frame.text = text

def card(s, x, y, w, h, title=None, title_color=ACCENT, fill=PANEL):
    c = rect(s, x, y, w, h, fill=fill, line=LINE, width=1.0, round_=0.04)
    if title:
        txt(s, x + 0.25, y + 0.22, w - 0.5, 0.3, title.upper(),
            size=10.5, color=title_color, font=F_MONO, wrap=False)
    return c

# ——————————————————————— slide 1 · TITLE ———————————————————————
s = new_slide()
rect(s, 0.25, 0.25, W - 0.5, H - 0.5, fill=None, line=LINE, width=1.0)
txt(s, PAD + 0.35, 1.55, 10.0, 0.4, "37°39′N  113°15′W  ·  KANARRAVILLE, UTAH",
    size=13, color=ACCENT, font=F_MONO, wrap=False)
txt(s, PAD + 0.3, 2.15, 11.5, 2.6, ["TRUST", "BUT VERIFY"],
    size=66, font=F_DISP, bold=True)
txt(s, PAD + 0.32, 4.85, 8.6, 0.8,
    ["LLM-assisted GIS data QC — the model works the edges.",
     "The checks and the humans stay in the middle."],
    size=16, color=MUTED, spacing=2)
ln = rect(s, PAD + 0.3, 6.55, CW - 0.6, 0.005, fill=LINE, line=None)
txt(s, PAD + 0.3, 6.72, 6.0, 0.3, "Robert McCleary · GIS Analyst, Sunrise Engineering",
    size=11, color=MUTED, font=F_BODY, wrap=False)
txt(s, W - PAD - 6.2, 6.72, 6.2, 0.3, "gemma4:12b · Ollama · ArcGIS Pro 3.7 · UGRC parcels (CC BY 4.0)",
    size=11, color=FAINT, font=F_MONO, wrap=False, align=PP_ALIGN.RIGHT)
notes(s, "Hold this slide while the previous talk ends. Credential stack is visible before you speak. → to begin; mention Nathan is in the room when you reach the Utah County beat.")

# ——————————————————————— slide 2 · PROBLEM ———————————————————————
s = new_slide()
eyebrow(s, "The problem", 2)
headline(s, [[("QC is an afterthought", {"color": ACCENT}), (".", {})]])
cw2, ch2 = 5.96, 4.75
card(s, PAD, 2.0, cw2, ch2, "The cost of bad data")
bullets(s, PAD + 0.3, 2.7, cw2 - 0.55, [
    "A wrong acreage sends the appraiser back out.",
    "A stale address sends dispatch to the wrong door.",
    "A duplicate parcel puts two bills in a resident's mailbox.",
], size=14.5, gap=14)
txt(s, PAD + 0.3, 4.65, cw2 - 0.55, 1.6,
    [[("Different desks absorb all of it. ", {}),
      ("No one adds it up.", {"bold": True, "color": FG})]],
    size=14.5, line_spacing=1.2)
x2 = PAD + cw2 + 0.2
card(s, x2, 2.0, cw2, ch2, "The cost of doing QC")
txt(s, x2 + 0.3, 2.62, cw2 - 0.55, 1.1, ["“Do the best you can", "do in 20 hours.”"],
    size=20, font=F_DISP, bold=True)
txt(s, x2 + 0.3, 3.62, cw2 - 0.55, 0.3, "— the scope, every time", size=10, color=FAINT, font=F_MONO)
bullets(s, x2 + 0.3, 4.15, cw2 - 0.55, [
    "20 hours was the leftover. Never the size of the problem.",
    "Essential projects go first. QC waits.",
    "Next quarter, nothing has changed.",
], size=13, gap=8)
r = rect(s, PAD + 0.3, 2.55, 0.05, 0.95, fill=ACCENT, line=None)
notes(s, "Beat 1 (2:00, slides-only). QC fails because it's priced by the hours left over, not by the risk. Bad-data costs are diffuse — appraiser, dispatch, mailbox — never traced back. QC's cost is concentrated: one budget sentence. Spoken anecdote: I'm hired repeatedly; often the third invoice for one data issue — once to create it, once to discover it, once to fix it. Transition: 'And this isn't hypothetical in Utah. It already happened next door.'")

# ——————————————————————— slide 3 · ECONOMICS ———————————————————————
s = new_slide()
eyebrow(s, "The pitch — economics, not philosophy", 3)
headline(s, [[("Same 20 hours. ", {}), ("4–5× the checks.", {"color": ACCENT})]])
cw3 = 5.55
card(s, PAD, 2.0, cw3, 3.35, "Today — QC sized to slack")
bullets(s, PAD + 0.3, 2.65, cw3 - 0.55, [
    "specs read by eye, if ever",
    "Arcade & SQL checks hand-written",
    "findings explained from scratch, after hours",
    "so the checks compete with every essential project",
], size=13, gap=8)
card(s, W - PAD - cw3, 2.0, cw3, 3.35, "With the LLM at the edges", title_color=ACCENT)
bullets(s, W - PAD - cw3 + 0.3, 2.65, cw3 - 0.55, [
    "it reads the spec → gap report, in minutes",
    "drafts the check → a human reviews, owns it",
    "verified findings → memos, written",
    "so the deterministic checks stop competing — they run",
], size=13, gap=8)
ar = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(6.55), Inches(3.35), Inches(0.9), Inches(0.5))
solid(ar, fill=ACCENT, line=None)
v = rect(s, PAD, 5.75, CW, 0.95, fill=TINT, line=ADIM, width=1.0, round_=0.08)
txt(s, PAD + 0.3, 5.98, CW - 0.6, 0.6,
    [[("The language-shaped parts stop being hourly labor. ", {}),
      ("QC finally gets scoped by risk — priced in minutes.", {"bold": True, "color": ACCENT}),
      ("  And the deal stays closed: the model never touches the geometry, never makes the decision.", {"color": MUTED})]],
    size=13.5, line_spacing=1.25)
notes(s, "Beat 1b (~45s). The promise: LLM collapses the cost of the language-shaped parts — reading the spec, drafting the check, writing the memo — so deterministic checks stop competing with essential projects. Same 20 hours, 4-5x the checks. Transition to Utah County.")

# ——————————————————————— slide 4 · UTAH COUNTY WORKFLOW ———————————————————————
s = new_slide()
eyebrow(s, "Utah County · property assessment", 4)
headline(s, [[("It already happened ", {}), ("next door", {"color": ACCENT}), (" — built in-house.", {})]], size=34)

def flowbox(x, w, tag, title, sub, accent=False):
    b = rect(s, x, 2.0, w, 1.15, fill=PANEL, line=ACCENT if accent else LINE, width=1.2, round_=0.05)
    txt(s, x + 0.14, 2.14, w - 0.28, 0.25, tag, size=8, color=FAINT, font=F_MONO, wrap=False)
    txt(s, x + 0.14, 2.42, w - 0.28, 0.35, title, size=12.5, color=FG, font=F_BODY, bold=True, wrap=False)
    txt(s, x + 0.14, 2.78, w - 0.28, 0.3, sub, size=9.5, color=MUTED, wrap=True)
    return x + w

bw = [2.35, 2.95, 2.75, 3.24]
x = PAD
x = flowbox(x, bw[0], "INPUT", "High-res aerial imagery", "countywide, current year") + 0.28
x = flowbox(x, bw[1], "IN-HOUSE MODEL · NO VENDOR", "Building-footprint detection", "computer vision on imagery", accent=True) + 0.28
x = flowbox(x, bw[2], "IN ARCGIS PRO", "Compare vs sketches", "sketches set taxable sq ft") + 0.28
x = flowbox(x, bw[3], "OUTCOME · PRO + ONLINE", "Green / yellow / red", "", accent=False)
txt(s, x - bw[3] + 0.14, 2.72, bw[3] - 0.28, 0.35,
    [[("● ", {"color": GOOD}), ("● ", {"color": WARN}), ("●", {"color": BAD}),
      ("  match scores", {"color": MUTED, "size": 10})]],
    size=12)
for ax in (PAD + bw[0], PAD + bw[0] + bw[1] + 0.28, PAD + bw[0] + bw[1] + bw[2] + 0.56):
    a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(ax), Inches(2.4), Inches(0.26), Inches(0.34))
    solid(a, fill=ACCENT, line=None)

# down to the appraiser
da = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, Inches(11.0), Inches(3.2), Inches(0.3), Inches(0.75))
solid(da, fill=ACCENT, line=None)
txt(s, 7.3, 3.35, 3.6, 0.5, "published to ArcGIS Online →\nstaff web app (Maps SDK for JS)",
    size=9.5, color=MUTED, align=PP_ALIGN.RIGHT)
b = rect(s, 8.4, 4.1, 4.3, 1.15, fill=PANEL, line=ACCENT, width=1.2, round_=0.05)
txt(s, 8.56, 4.24, 4.0, 0.25, "THE DETERMINATION", size=8, color=FAINT, font=F_MONO, wrap=False)
txt(s, 8.56, 4.52, 4.0, 0.35, "The appraiser decides", size=12.5, color=FG, bold=True, wrap=False)
txt(s, 8.56, 4.88, 4.0, 0.3, "valuation · inspection · sign-off", size=9.5, color=MUTED, wrap=False)

# boundary annotation
rect(s, 2.2, 3.05, 0.012, 1.4, fill=FAINT, line=None)
rect(s, 2.2, 4.43, 6.1, 0.012, fill=FAINT, line=None)
txt(s, 2.35, 4.12, 5.6, 0.3, "the determination stays human — no model, ever", size=10.5, color=FAINT, font=F_MONO, wrap=False)

txt(s, PAD, 5.6, CW, 0.5,
    [[("The AI drafted the review queue; a human made the call.  ", {"bold": True, "color": FG}),
      ("Utah County GIS built the whole chain themselves. ", {"color": MUTED}),
      ("Nathan Thomas — 2026 UGIC Excellence in GIS Award.", {"color": ACCENT})]],
    size=12.5, line_spacing=1.3)
footer(s)
notes(s, "Beat 2 (2:00, slides-only). Give Nathan the nod in the room. What the AI did NOT do: value property, decide anything. It drafted the review queue — the appraister makes the call. Hold that shape. Transition: CV, narrow, purpose-built. The LLM is a different beast — which raises the real question: where should it sit?")

# ——————————————————————— slide 5 · UTAH COUNTY NUMBERS ———————————————————————
s = new_slide()
eyebrow(s, "Utah County · what it bought", 5)
headline(s, "56,993 properties. 86% never visited.")
stats = [
    ("56,993", "parcels approaching reassessment, triaged by the model", False),
    ("86%",    "strong matches — 48,846 parcels ruled out of further review", True),
    ("7,494",  "flagged yellow — a discrepancy worth a desk review", False),
    ("653",    "high-priority candidates for a field inspection", False),
]
tw, gap = 2.95, 0.11
for i, (n, lab, hot) in enumerate(stats):
    x = PAD + i * (tw + gap)
    card(s, x, 2.0, tw, 2.0)
    txt(s, x + 0.25, 2.15, tw - 0.5, 0.8, n,
        size=34, color=ACCENT if hot else FG, font=F_DISP, bold=True, wrap=False)
    txt(s, x + 0.25, 3.05, tw - 0.5, 0.85, lab, size=10.5, color=MUTED, line_spacing=1.15)
card(s, PAD, 4.3, 6.6, 1.95)
txt(s, PAD + 0.3, 4.55, 2.2, 0.8, "$160K/yr", size=30, color=ACCENT, font=F_DISP, bold=True, wrap=False)
txt(s, PAD + 2.6, 4.62, 3.8, 1.4,
    [[("outsourced verification work ", {"color": MUTED}),
      ("eliminated", {"bold": True, "color": FG}),
      (" — staff time shifted from hunting for changes to making valuation decisions.", {"color": MUTED})]],
    size=12, line_spacing=1.25)
card(s, W - PAD - 5.33, 4.3, 5.33, 1.95)
txt(s, W - PAD - 5.03, 4.55, 4.7, 1.5,
    [[("Utah's 5-year state-mandated reassessment cycle", {"bold": True, "color": FG}),
      (" over 284,000+ parcels — manually inspecting everything is impossible.  Source: Esri case study; UGIC 2026 award.", {"color": MUTED})]],
    size=12, line_spacing=1.25)
footer(s)
notes(s, "The money slide of beat 2. Read the tiles fast: 56,993 triaged, 86% ruled out (48,846), 7,494 desk reviews, 653 field visits, $160K/yr saved. Then the point: the model narrowed the work; humans did the valuations.")

# ——————————————————————— slide 6 · SPECTRUM ———————————————————————
s = new_slide()
eyebrow(s, "The question — where should the LLM sit?", 6)
headline(s, [[("Good at language. Bad at math. ", {}), ("So place it.", {"color": ACCENT})]])

# braces (outline rects, no fill)
brA = rect(s, PAD, 1.95, 4.55, 0.55, fill=None, line=ACCENT, width=1.2, round_=0.5)
txt(s, PAD, 2.05, 4.55, 0.3, "the LLM may work here", size=9, color=ACCENT, font=F_MONO, align=PP_ALIGN.CENTER, wrap=False)
brB = rect(s, 7.9, 1.95, 2.3, 0.55, fill=None, line=ACCENT, width=1.2, round_=0.5)
txt(s, 7.9, 2.05, 2.3, 0.3, "and here", size=9, color=ACCENT, font=F_MONO, align=PP_ALIGN.CENTER, wrap=False)

stations = [
    ("ZONE 1 · OUTSIDE", "Read the documents", "state schema, data dictionaries, policy PDFs → gap reports, checklists", "no data touched", True),
    ("ZONE 2 · INPUT EDGE", "Draft the checks", "English → candidate Arcade / SQL; text & address QC; human reviews and owns it", "code is reviewed first", True),
    ("THE MIDDLE", "Data + deterministic checks", "geometry, area math, topology, duplicates, thresholds — proven, reproducible", "", False),
    ("ZONE 4 · OUTPUT EDGE", "Explain the findings", "triage memos from verified findings; per-finding notes for reviewers", "advisory only — facts above the prose", True),
    ("ZONE 5 · ALWAYS", "Humans decide", "accept, reject, route to the recorder — sign-off is a person's", "every time", False),
]
sw, sgap = 2.31, 0.145
for i, (tag, name, desc, who, llm) in enumerate(stations):
    x = PAD + i * (sw + sgap)
    card(s, x, 2.7, sw, 3.35, tag, title_color=ACCENT if llm else FG,
         fill=PANEL2 if not llm else PANEL)
    txt(s, x + 0.2, 3.15, sw - 0.4, 0.75, name, size=13, color=FG, bold=True, line_spacing=1.05)
    txt(s, x + 0.2, 3.95, sw - 0.4, 1.5, desc, size=9.5, color=MUTED, line_spacing=1.15)
    if who:
        txt(s, x + 0.2, 5.6, sw - 0.4, 0.4, who, size=8, color=ACCENT if llm else FAINT, font=F_MONO, line_spacing=1.1)
# NEVER stamp on the middle station
st = rect(s, PAD + 2 * (sw + sgap) + 0.32, 5.25, 1.65, 0.6, fill=None, line=BAD, width=2.0)
st.rotation = 354
txt(s, PAD + 2 * (sw + sgap) + 0.32, 5.38, 1.65, 0.4, "NEVER", size=17, color=BAD, font=F_DISP, bold=True, align=PP_ALIGN.CENTER, wrap=False)
txt(s, PAD, 6.35, CW, 0.4,
    [[("Zones 1, 2 and 4 are work, not worship. ", {"color": MUTED}),
      ("Same shape as Utah County: AI drafts the queue, the check proves it, a human decides.", {"color": FG, "bold": True})]],
    size=12, align=PP_ALIGN.CENTER, line_spacing=1.2)
footer(s)
notes(s, "Beat 3 (3:00) — builds: reveal zone 1 'outside' (spec reading), zone 2 'input edge' (drafts Arcade/SQL, text QC), zone 4 'output edge' (memos, per-finding notes), then the NEVER stamp on the middle. Key line: 'The LLM never touches the geometry. Never makes the decision. Ever.' In Slides: add Appear animations to brA, brB stations and the stamp if you want true builds. Transition: 'First, the clearest case of a check that must never leave deterministic code.'")

# ——————————————————————— slide 7 · WEB MERCATOR ———————————————————————
s = new_slide()
eyebrow(s, "Beat 1 · a check the LLM must never do", 7)
headline(s, [[("The LLM can ", {}), ("name", {"color": ACCENT}), (" this trap. It must never ", {}), ("do", {"color": ACCENT}), (" the math.", {})]], size=32)
txt(s, PAD, 2.0, 7.0, 0.35, "Parcel area, Kanarraville demo subset (508 rows), indexed to the equal-area projection:",
    size=11.5, color=MUTED, line_spacing=1.2)

TRACK_X, TRACK_W = 2.75, 4.9
# 5070 bar (100 vs 159.3 scale → 30.8%)
txt(s, PAD, 2.62, 2.05, 0.55,
    [[("EPSG:5070", {"bold": True, "color": FG}),
      ("\nALBERS · EQUAL-AREA", {"size": 8.5, "color": FAINT, "font": F_MONO})]],
    size=11, align=PP_ALIGN.RIGHT)
rect(s, TRACK_X, 2.6, TRACK_W, 0.5, fill=PANEL, line=LINE, width=1.0)
rect(s, TRACK_X, 2.6, TRACK_W * 100 / 159.3, 0.5, fill=BASEBAR, line=None)
txt(s, TRACK_X + TRACK_W * 100 / 159.3 + 0.12, 2.68, 1.0, 0.3, "100", size=12, color=FG, font=F_MONO, bold=True, wrap=False)
# 3857 bar (full)
txt(s, PAD, 3.32, 2.05, 0.55,
    [[("EPSG:3857", {"bold": True, "color": FG}),
      ("\nWEB MERCATOR · NATIVE CRS", {"size": 8.5, "color": FAINT, "font": F_MONO})]],
    size=11, align=PP_ALIGN.RIGHT)
rect(s, TRACK_X, 3.3, TRACK_W, 0.5, fill=PANEL, line=LINE, width=1.0)
rect(s, TRACK_X, 3.3, TRACK_W, 0.5, fill=ACCENT, line=None)
txt(s, TRACK_X + TRACK_W - 0.85, 3.38, 0.72, 0.3, "159.3", size=12, color=BG, font=F_MONO, bold=True, wrap=False, align=PP_ALIGN.RIGHT)
txt(s, PAD, 4.15, 7.1, 1.4,
    [[("Every acreage compared in the native CRS is ", {}),
      ("+59.3% off the map.", {"bold": True, "color": ACCENT}),
      (" Web Mercator is conformal — it keeps angles, not area — and the distortion grows with latitude. ", {}),
      ("37.6° N is exactly where it bites.", {"color": FAINT}),
      (" Stated-assessment acres are measured against the wrong Earth.", {"color": FAINT})]],
    size=12.5, line_spacing=1.3)

card(s, 8.0, 1.95, 4.73, 2.1)
txt(s, 8.25, 2.15, 4.2, 0.3, "THE LLM MAY", size=10.5, color=GOOD, font=F_MONO, wrap=False)
txt(s, 8.25, 2.5, 4.25, 1.4,
    [[("know the trap and put it on your checklist — “your native-CRS areas are not defensible; verify in an equal-area projection.” Knowledge like this is free.", {})]],
    size=12, line_spacing=1.25)
card(s, 8.0, 4.2, 4.73, 2.1)
txt(s, 8.25, 4.4, 4.2, 0.3, "IT MUST NEVER", size=10.5, color=BAD, font=F_MONO, wrap=False)
txt(s, 8.25, 4.75, 4.25, 1.4,
    [[("run the arithmetic, reproject, or “fix” an acreage. The LLM flags the ", {}),
      ("possibility", {"bold": True, "color": FG}),
      ("; deterministic code in ArcGIS proves the ", {}),
      ("fact", {"bold": True, "color": FG}), (".", {})]],
    size=12, line_spacing=1.25)
footer(s)
notes(s, "Beat 4 (2:00, output/chart slide — NOT live). Key line: 'This is why ask-the-LLM-what-could-be-wrong is a real, cheap, zero-risk QC step — as a checklist generator. The LLM's knowledge is free. Its arithmetic is a liability.' Transition: 'Now the harder case — where the opinion is confident, plausible, and wrong.'")

prs.core_properties.title = "Trust but Verify"
prs.core_properties.author = "Robert McCleary"
prs.core_properties.subject = "LLM-assisted GIS data QC"

prs.save("slides/deck_g5.pptx")
print("saved slides/deck_g5.pptx —", len(prs.slides._sldIdLst), "slides")
