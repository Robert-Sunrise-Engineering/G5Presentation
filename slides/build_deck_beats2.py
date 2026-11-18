"""Slides 8-15 of the G5 talk as a separate pptx for Google Slides import.
Run:  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" slides\\build_deck_beats2.py
Output: slides\\deck_g5_beats2.pptx  (import via File > Import slides)
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

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
TINT   = RGBColor(0x21, 0x1D, 0x1B)

F_DISP, F_BODY, F_MONO = "Oswald", "Lato", "Roboto Mono"
W, H   = 13.333, 7.5
PAD    = 0.6
CW     = W - 2 * PAD
TOTAL  = 15

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]

def new_slide():
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = BG
    return s

def solid(sh, fill=None, line=None, width=1.0):
    if fill is None: sh.fill.background()
    else: sh.fill.solid(); sh.fill.fore_color.rgb = fill
    if line is None: sh.line.fill.background()
    else: sh.line.color.rgb = line; sh.line.width = Pt(width)
    try: sh.shadow.inherit = False
    except Exception: pass
    return sh

def rect(s, x, y, w, h, fill=PANEL, line=LINE, width=1.0, round_=0.0):
    kind = MSO_SHAPE.ROUNDED_RECTANGLE if round_ else MSO_SHAPE.RECTANGLE
    sh = s.shapes.add_shape(kind, Inches(x), Inches(y), Inches(w), Inches(h))
    if round_:
        try: sh.adjustments[0] = round_
        except Exception: pass
    sh.text_frame.paragraphs[0].text = ""
    return solid(sh, fill, line, width)

def txt(s, x, y, w, h, runs, size=13, color=FG, font=F_BODY, bold=False,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=None, line_spacing=None,
        wrap=True):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = wrap; tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    if isinstance(runs, str): runs = [runs]
    first = True
    for para in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.alignment = align
        if spacing is not None: p.space_after = Pt(spacing)
        if line_spacing is not None: p.line_spacing = line_spacing
        items = [(para, {})] if isinstance(para, str) else para
        for text, st in items:
            r = p.add_run(); r.text = text
            f = r.font
            f.name  = st.get("font", font); f.size  = Pt(st.get("size", size))
            f.bold  = st.get("bold", bold); f.color.rgb = st.get("color", color)
    return tb

def bullets(s, x, y, w, items, size=13, gap=5, line_spacing=1.15, color=FG):
    tb = txt(s, x, y, w, 0.4 * len(items),
             [[("\u2022   ", {"color": ACCENT, "bold": True}), (it, {"color": color})] for it in items],
             size=size, spacing=gap, line_spacing=line_spacing)
    return tb

def eyebrow(s, label, n):
    txt(s, PAD, 0.32, 8.5, 0.3, label.upper(), size=11, color=FAINT, font=F_MONO, wrap=False)
    txt(s, W - PAD - 1.4, 0.32, 1.4, 0.3, f"{n:02d} / {TOTAL}", size=11, color=ACCENT,
        font=F_MONO, wrap=False, align=PP_ALIGN.RIGHT)

def footer(s):
    rect(s, PAD, 6.98, CW, 0.005, fill=LINE, line=None)
    txt(s, PAD, 7.1, 7.5, 0.3, "TRUST BUT VERIFY", size=9, color=FAINT, font=F_MONO, wrap=False)
    txt(s, W - PAD - 5.5, 7.1, 5.5, 0.3, "gemma4:12b · Ollama · ArcGIS Pro 3.7 · UGRC parcels (CC BY 4.0)",
        size=9, color=FAINT, font=F_MONO, wrap=False, align=PP_ALIGN.RIGHT)

def headline(s, runs, size=36, y=0.85, h=1.0):
    txt(s, PAD, y, CW, h, runs, size=size, font=F_DISP, bold=True)

def card(s, x, y, w, h, title=None, title_color=ACCENT, fill=PANEL):
    c = rect(s, x, y, w, h, fill=fill, line=LINE, width=1.0, round_=0.04)
    if title:
        txt(s, x + 0.25, y + 0.2, w - 0.5, 0.3, title.upper(),
            size=10.5, color=title_color, font=F_MONO, wrap=False)
    return c

def notes(s, text):
    s.notes_slide.notes_text_frame.text = text

# ——————————————————— 08 · WEB MERCATOR ———————————————————
s = new_slide()
eyebrow(s, "Beat 1 · a check the LLM must never do", 8)
headline(s, [[("The LLM can ", {}), ("name", {"color": ACCENT}),
              (" this trap. It must never ", {}), ("do", {"color": ACCENT}), (" the math.", {})]], size=32)
txt(s, PAD, 2.0, 7.0, 0.35, "Parcel area, Kanarraville demo subset (508 rows), indexed to the equal-area projection:",
    size=11.5, color=MUTED, line_spacing=1.2)
TX, TW = 2.75, 4.9
txt(s, PAD, 2.62, 2.05, 0.55,
    [[("EPSG:5070", {"bold": True, "color": FG}),
      ("\nALBERS · EQUAL-AREA", {"size": 8.5, "color": FAINT, "font": F_MONO})]], size=11, align=PP_ALIGN.RIGHT)
rect(s, TX, 2.6, TW, 0.5, fill=PANEL, line=LINE); rect(s, TX, 2.6, TW * 100 / 159.3, 0.5, fill=BASEBAR, line=None)
txt(s, TX + TW * 100 / 159.3 + 0.12, 2.68, 1.0, 0.3, "100", size=12, color=FG, font=F_MONO, bold=True, wrap=False)
txt(s, PAD, 3.32, 2.05, 0.55,
    [[("EPSG:3857", {"bold": True, "color": FG}),
      ("\nWEB MERCATOR · NATIVE CRS", {"size": 8.5, "color": FAINT, "font": F_MONO})]], size=11, align=PP_ALIGN.RIGHT)
rect(s, TX, 3.3, TW, 0.5, fill=PANEL, line=LINE); rect(s, TX, 3.3, TW, 0.5, fill=ACCENT, line=None)
txt(s, TX + TW - 0.85, 3.38, 0.72, 0.3, "159.3", size=12, color=BG, font=F_MONO, bold=True, wrap=False, align=PP_ALIGN.RIGHT)
txt(s, PAD, 4.15, 7.1, 1.4,
    [[("Every acreage compared in the native CRS is ", {}), ("+59.3% off the map.", {"bold": True, "color": ACCENT}),
      (" Web Mercator is conformal — it keeps angles, not area — and the distortion grows with latitude. ", {}),
      ("37.6° N is exactly where it bites.", {"color": FAINT}),
      (" Stated-assessment acres are measured against the wrong Earth.", {"color": FAINT})]],
    size=12.5, line_spacing=1.3)
card(s, 8.0, 1.95, 4.73, 2.1)
txt(s, 8.25, 2.15, 4.2, 0.3, "THE LLM MAY", size=10.5, color=GOOD, font=F_MONO, wrap=False)
txt(s, 8.25, 2.5, 4.25, 1.4, [[("know the trap and put it on your checklist — “your native-CRS areas are not defensible; verify in an equal-area projection.” Knowledge like this is free.", {})]], size=12, line_spacing=1.25)
card(s, 8.0, 4.2, 4.73, 2.1)
txt(s, 8.25, 4.4, 4.2, 0.3, "IT MUST NEVER", size=10.5, color=BAD, font=F_MONO, wrap=False)
txt(s, 8.25, 4.75, 4.25, 1.4,
    [[("run the arithmetic, reproject, or “fix” an acreage. The LLM flags the ", {}),
      ("possibility", {"bold": True}), ("; deterministic code in ArcGIS proves the ", {}), ("fact", {"bold": True}), (".", {})]],
    size=12, line_spacing=1.25)
footer(s)
notes(s, "Beat (2:00, output/chart slide — NOT live). Key line: 'That is why ask-the-LLM-what-could-be-wrong is a real, cheap, zero-risk QC step — as a checklist generator. The LLM's knowledge is free; its arithmetic is a liability.' Transition: 'Now the harder case — the opinion that is confident, plausible, and wrong.'")

# ——————————————————— 09 · DUPLICATE IDS ———————————————————
s = new_slide()
eyebrow(s, "Beat 2 · the data", 9)
headline(s, [[("71% of rows share a PARCEL_ID.", {"color": ACCENT}), ("  So what?", {})]], size=34)
card(s, PAD, 2.0, 5.3, 3.6, "Kanarraville · 508 rows")
bullets(s, PAD + 0.3, 2.55, 4.75, [
    "362 rows (71.3%) share a PARCEL_ID with other rows",
    "354 rows share an exact footprint",
    "zero overlaps between different parcels",
    "9 blank IDs · 12 rows with no assessor data",
], size=12.5)
c = card(s, 6.2, 2.0, 6.53, 3.6, "280 S Main St · A-0646-0001-0000 · HOUSE_CNT = 7")
rows = [("1,322 sq ft", "1970"), ("1,283 sq ft", "1996"), ("1,120 sq ft", "2013"),
        ("576 sq ft", "1996"), ("320 sq ft", "1970"), ("96 sq ft", "1970"), ("64 sq ft", "1970")]
for i, (sq, yr) in enumerate(rows):
    txt(s, 6.55, 2.52 + i * 0.36, 3.2, 0.3, sq, size=11.5, color=FG, font=F_MONO, wrap=False)
    txt(s, 10.2, 2.52 + i * 0.36, 2.3, 0.3, yr, size=11.5, color=MUTED, font=F_MONO, wrap=False)
txt(s, PAD + 0.3, 5.5, CW, 0.45,
    [[("Same parcel, same acreage, same market value — seven different buildings.", {"color": FG, "bold": True}),
      ("  Deleting “duplicates” here deletes real homes.", {"color": ACCENT})]],
    size=13, line_spacing=1.25)
txt(s, PAD, 6.15, CW, 0.35, "The row is not the unit of analysis. The parcel is — dissolve unique geometries by PARCEL_ID before you compare anything.",
    size=12, color=MUTED, font=F_BODY, line_spacing=1.2)
footer(s)
notes(s, "Beat (3:00, live begins here or cell-output slide). The duplicate-ID story: one parcel, seven buildings, each row a unit. Design lesson to say: validate at parcel level; handle near-duplicate geometries (A-0647) separately. Transition: 'The model looks at this and has an opinion. Watch the gate.'")

# ——————————————————— 10 · THE GATE ———————————————————
s = new_slide()
eyebrow(s, "Beat 2 · the gate", 10)
headline(s, [[("The proposal is wrong. ", {}), ("The gate catches it.", {"color": ACCENT})]], size=36)
card(s, PAD, 2.0, 5.7, 2.9, "What the local model proposed")
txt(s, PAD + 0.3, 2.5, 5.1, 2.2,
    ["{",
     "'proposal':  'merge_rows',",
     "'target':    'A-0646-0001-0000',",
     "'rows':      7,",
     "'reason':    '7 rows share PARCEL_ID'",
     "}"],
    size=11.5, color=MUTED, font=F_MONO, line_spacing=1.3)
a = s.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(6.45), Inches(3.1), Inches(0.55), Inches(0.4))
solid(a, fill=ACCENT, line=None)
card(s, 7.15, 2.0, 5.58, 2.9, "What the gate returned")
txt(s, 7.45, 2.42, 5.0, 0.5, [[("REJECTED", {"color": BAD, "bold": True, "size": 20, "font": F_DISP}),
                               ("   rule G1", {"color": FAINT, "size": 11, "font": F_MONO})]])
txt(s, 7.45, 3.05, 5.0, 1.6,
    [[("7 rows = 7 real, occupied units (HOUSE_CNT = 7). Merging them would delete homes, not duplicates.", {"color": FG})],
     [("The proposal dies here — it never reached the data.", {"color": MUTED})]],
    size=12.5, line_spacing=1.25, spacing=6)
rect(s, PAD, 5.25, CW, 0.75, fill=TINT, line=ADIM, round_=0.08)
txt(s, PAD + 0.3, 5.42, CW - 0.6, 0.4,
    [[("Audit line:  ", {"color": FAINT, "font": F_MONO, "size": 11}),
      ("1 REJECTED (G1)", {"color": BAD, "bold": True, "size": 12}),
      ("   ·   1 DOWNGRADED (G5)", {"color": WARN, "bold": True, "size": 12}),
      ("   ·   5 ACCEPTED (G7)", {"color": GOOD, "bold": True, "size": 12}),
      ("   ·   1 EDIT AWAITING A HUMAN", {"color": ACCENT, "bold": True, "size": 12})]])
txt(s, PAD, 6.25, CW, 0.5,
    [[("A wrong proposal costs seconds to generate and one review row to discard — ", {"color": MUTED}),
      ("because the gate stood between it and the data.", {"color": FG, "bold": True})]],
    size=13, line_spacing=1.25)
footer(s)
notes(s, "Beat (3:00). The LLM looked at the 280 S Main St sample and confidently proposed a merge. The gate rule G1 rejected it: rows are units. Key line: 'The LLM's confidence is not a QC signal. The check is the signal.'")

# ——————————————————— 11 · GATE ISN'T BINARY ———————————————————
s = new_slide()
eyebrow(s, "Beat 3 · the gate isn't binary", 11)
headline(s, "Reject, downgrade, approve-then-review.")
def outcome(x, tag, tcolor, body):
    card(s, x, 2.0, 3.93, 2.6)
    txt(s, x + 0.25, 2.2, 3.4, 0.35, tag, size=13, color=tcolor, font=F_DISP, bold=True, wrap=False)
    txt(s, x + 0.25, 2.65, 3.45, 1.8, body, size=11.5, color=FG, line_spacing=1.22)
outcome(PAD,    "REJECTED", BAD,  [[("280 S Main St merge — ", {"bold": True}),
                                    ("7 rows are 7 real units. A merge would delete occupied dwellings.", {})]])
outcome(4.7,    "DOWNGRADED", WARN, [[("E-0337-0002-00R1 — ", {"bold": True}),
                                      ("stated 10.11 ac vs 0.885 ac mapped (11.4×). Pattern matches a clipped footprint — “fix the acreage” is the wrong fix; verify against the survey.", {})]])
outcome(8.8,    "APPROVED · PENDING", GOOD, [[("A-0729-0002-0002 — ", {"bold": True}),
                                              ("stated 0.988 ac vs 0.491 ac mapped, boundary uncontested. Real inconsistency. Applies only after one human click.", {})]])
card(s, PAD, 4.95, CW, 1.55)
txt(s, PAD + 0.3, 5.15, CW - 0.6, 0.3, "WHY EDITS ARE GATED", size=10.5, color=ACCENT, font=F_MONO)
txt(s, PAD + 0.3, 5.5, CW - 0.6, 0.9,
    [[("Utah Code 58-22-102:", {"bold": True}),
      (" boundary and legal acreage corrections route through the County Surveyor and the County Recorder. ", {"color": MUTED}),
      ("The gate refusing to touch geometry isn’t a design choice — anything else is unlicensed practice.", {"bold": True, "color": FG})]],
    size=12.5, line_spacing=1.3)
footer(s)
notes(s, "Beat (3:00). Three outcomes, not two — the gate has nuance the LLM never sees. Downgrade = the check re-ranked the finding so human review effort goes where it matters. Legal floor: 58-22-102. Key line: 'Reject, downgrade, approve-then-review: the LLM never sees or influences any of the three.'")

# ——————————————————— 12 · THE 3PM MAP-TECH ———————————————————
s = new_slide()
eyebrow(s, "Beat 4 · the reviewer", 12)
headline(s, [[("What the ", {}), ("3pm map-tech", {"color": ACCENT}), (" actually sees.", {})]], size=36)
card(s, PAD, 2.0, 5.9, 3.0, "A-0729-0002-0002 · flag + edit pending")
txt(s, PAD + 0.3, 2.5, 5.3, 2.3,
    [[("Stated acreage 0.988 is about 2× the mapped 0.491. No boundary overlap — the boundary itself is uncontested.", {})],
     [("Looks like transposed or doubled digits in the assessed acreage.", {"bold": True})],
     [("Action: confirm with the assessor record before touching GIS acreage; if the geometry matches the plat, the fix belongs to the source record — not the geometry.", {"color": MUTED})]],
    size=12, line_spacing=1.22, spacing=6)
card(s, 6.83, 2.0, 5.9, 3.0, "E-0337-0002-00R1 · flag, no edit")
txt(s, 7.13, 2.5, 5.3, 2.3,
    [[("Stated 10.11 ac vs mapped 0.885 ac, no neighbor overlap.", {})],
     [("Matches a clipped / excluded footprint — do not “correct” the acreage to the stated value.", {"bold": True})],
     [("Action: verify the footprint against the filed survey before touching either.", {"color": MUTED})]],
    size=12, line_spacing=1.22, spacing=6)
txt(s, PAD, 5.35, CW, 0.5,
    [[("Same check fired twice. Same threshold. A deterministic checker can never produce these two different explanations — ", {"color": MUTED}),
      ("the LLM makes flags meaningful to the human who acts on them.", {"color": FG, "bold": True})]], size=13, line_spacing=1.25)
rect(s, PAD, 6.0, CW, 0.6, fill=TINT, line=ADIM, round_=0.08)
txt(s, PAD + 0.3, 6.14, CW - 0.6, 0.35,
    "Facts stamped above the prose   ·   advisory only   ·   labeled “AI-drafted, human-reviewed”   ·   the note is a GRAMA record — archive it",
    size=11, color=MUTED, font=F_MONO)
footer(s)
notes(s, "Beat (2:30, pre-generated notes — never live-prompt on stage). Failure is visible and harmless: if the prose is wrong, the tech reads the evidence and overrules it. Worst case is a bad paragraph, not a bad parcel. This is the part reviewers will love — and the one place the LLM cannot do damage.")

# ——————————————————— 13 · NEGATIVE TESTING ———————————————————
s = new_slide()
eyebrow(s, "Beat 5 · the flip", 13)
headline(s, [[("Flip it: ", {}), ("the LLM audits your QC.", {"color": ACCENT})]], size=38)
steps = [
    ("ASK", "the local model: “write 50 parcels that look right but are wrong.”"),
    ("INJECT", "them into a scratch copy — programmatically, not by hand."),
    ("RUN", "the checks. Anything the model sneaks past is a hole in your QC."),
]
for i, (tag, body) in enumerate(steps):
    x = PAD + i * 4.06
    card(s, x, 2.1, 3.9, 1.7)
    txt(s, x + 0.25, 2.3, 3.4, 0.3, f"{i+1} · {tag}", size=11, color=ACCENT, font=F_MONO, wrap=False)
    txt(s, x + 0.25, 2.65, 3.4, 1.0, body, size=12, color=FG, line_spacing=1.2)
card(s, PAD, 4.15, CW, 2.25, "The kind of wrong it is uniquely good at")
for x, line in ((0, "acres swapped digit-by-digit — plausible, still wrong"),
                (4.06, "“PRIMARY_RES = Y” with no building record"),
                (8.12, "effective-age values that pass a year-range check")):
    txt(s, PAD + x + 0.25, 4.65, 3.7, 0.6, [[("\u2022   ", {"color": ACCENT, "bold": True}), (line, {})]],
        size=12, line_spacing=1.2)
txt(s, PAD + 0.3, 5.6, CW - 0.6, 0.6,
    [[("Trust but verify — applied to the verifier. ", {"color": FG, "bold": True}),
      ("Generating realistic-looking wrong data is a language task, and nothing else does it this cheaply.", {"color": MUTED})]],
    size=12.5, line_spacing=1.25)
footer(s)
notes(s, "FIRST CUT if running hot: one spoken line ('we also run the model backwards — it writes plausible-but-wrong parcels, we inject them, and grade our own checks') over this slide unread. Otherwise the beat nobody in the room has seen. The checks that missed are found before a resident finds them.")

# ——————————————————— 14 · CHECKLIST ———————————————————
s = new_slide()
eyebrow(s, "Take-home", 14)
headline(s, [[("Seven things your shop can do ", {}), ("this month.", {"color": ACCENT})]], size=38)
items = [
    "Feed the state schema to the model → gap report against your fields.",
    "Describe a check in English → candidate Arcade rule; a human reviews and owns it.",
    "Validate addresses and owner names; adjudicate the borderline pairs.",
    "Draft domain recommendations and accurate metadata from verified usage.",
    "Turn verified findings into one-page triage memos for supervision.",
    "Attach a per-finding note to every flag — facts above the prose.",
    "Run one negative-testing pass against your own checks.",
]
for i, line in enumerate(items):
    col, row = i // 4, i % 4
    x = PAD + col * 6.2
    y = 2.05 + row * 0.78
    txt(s, x, y, 0.5, 0.4, f"{i+1}", size=16, color=ACCENT, font=F_DISP, bold=True, wrap=False)
    txt(s, x + 0.42, y + 0.02, 5.55, 0.72, line, size=12, color=FG, line_spacing=1.15)
rect(s, PAD, 5.35, CW, 1.05, fill=TINT, line=ADIM, round_=0.08)
txt(s, PAD + 0.3, 5.52, CW - 0.6, 0.7,
    [[("The 20-hour cap stops being the ceiling. ", {"color": MUTED}),
      ("QC finally gets scoped by risk — priced in minutes.", {"bold": True, "color": ACCENT})]],
    size=14, line_spacing=1.25)
footer(s)
notes(s, "Flexes to 1:30 if hot: read items 1 and 2, point at the rest. Each item maps to the spectrum: outside (1), input edge (2-4), output edge (5-6), and 7 is the flip. Close: 'None of this needs permission beyond a conversation with your county attorney and IT.'")

# ——————————————————— 15 · CLOSE ———————————————————
s = new_slide()
eyebrow(s, "The rules already say this", 15)
txt(s, PAD, 2.1, CW, 2.4,
    [[("The model works the edges.", {"color": FG})],
     [("The checks and the humans stay in the middle.", {"color": ACCENT})]],
    size=44, font=F_DISP, bold=True, line_spacing=1.15)
card(s, PAD, 4.7, CW, 1.6, "Why this is legal in Utah — already")
txt(s, PAD + 0.3, 5.08, CW - 0.6, 1.1,
    [[("EO 2026-08 asks state agencies for human-guided, documented, human-in-the-loop AI — ", {"color": MUTED}),
      ("exactly the architecture above.", {"bold": True, "color": FG}),
      ("  Local model, Apache 2.0 weights, CC BY 4.0 data, no per-token spend. First step anywhere: 15 minutes with the county attorney and IT.", {"color": MUTED})]],
    size=12.5, line_spacing=1.3)
txt(s, PAD, 6.55, 8.0, 0.3, "Robert McCleary · GIS Analyst, Sunrise Engineering",
    size=11, color=MUTED, font=F_BODY, wrap=False)
txt(s, W - PAD - 6.0, 6.55, 6.0, 0.3, "Thank you — and thanks to Nathan Thomas.",
    size=11, color=MUTED, font=F_MONO, wrap=False, align=PP_ALIGN.RIGHT)
notes(s, "Close (~1:30). Restate thesis in one line, then the EO framing: 'we're not asking permission for something edgy; we're implementing stated policy.' Thank the room; credit Nathan once more if he's still here. → Q&A block: expected order — what-if-the-model-is-wrong (point at slide 10), legality (slides 11+15), model/cost, why-not-let-it-drive (slide 5 card 2: one time it drove, it failed on nearly every tool call). Park deep ones to the break.")

prs.core_properties.title = "Trust but Verify — beats 8-15"
prs.core_properties.author = "Robert McCleary"
prs.save("slides/deck_g5_beats2.pptx")
print("saved slides/deck_g5_beats2.pptx —", len(prs.slides._sldIdLst), "slides")
