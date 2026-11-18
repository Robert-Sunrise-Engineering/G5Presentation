"""Notes + eyebrow consistency pass (2026-11-18).

Fixes the drift introduced by the reorder to 15 slides (safety slide inserted,
Utah County moved after placement + safety, mercator-onward shifted +2):

1. deck_g5.pptx  — slide 5's speaker notes were a stale copy of the spectrum
   slide's notes (wrong beat). Rewrite all content-slide notes to the locked
   slide order with correct beat label + transition. Also collapse the doubled
   eyebrow on slide 5.
2. deck_g5_beats2.pptx — strip the misleading "BEAT N ·" prefixes from the
   eyebrows (they used a different numbering than the n/15 counters) and renumber
   the speaker notes to "Slide N · title (time)".

Run:  "C:\\Program Files\\ArcGIS\\Pro\\bin\\Python\\envs\\arcgispro-py3\\python.exe" slides\\patch5_notes.py
"""
from pptx import Presentation
from pptx.dml.color import RGBColor

FAINT = RGBColor(0x6B, 0x74, 0x80)
F_MONO = "Roboto Mono"

# ————————————————————— deck_g5.pptx (slides 1–7) —————————————————————

g5 = Presentation(r"slides/deck_g5.pptx")
s = list(g5.slides)

g5_notes = {
    1: ("Slide 2 · problem (2:00, slides-only). QC fails because it's priced by the "
        "hours left over, not by the risk. Bad-data costs are diffuse — appraiser, "
        "dispatch, mailbox — never traced back. QC's cost is concentrated: one budget "
        "sentence. Spoken anecdote: I'm hired repeatedly; often the third invoice for "
        "one data issue — once to create it, once to discover it, once to fix it. "
        "Transition: 'So I'm not here to sell a philosophy — here's the pitch.'"),
    2: ("Slide 3 · pitch (~45s). The promise: the LLM collapses the cost of the "
        "language-shaped parts — reading the spec, drafting the check, writing the memo "
        "— so the deterministic checks stop competing with essential projects. Same 20 "
        "hours, 4–5× the checks. Transition: 'The LLM works the edges. The real question "
        "is where, exactly.'"),
    3: ("Slide 4 · spectrum (3:00) — builds ×3: reveal zone 1 'outside' (spec reading), "
        "zone 2 'input edge' (drafts Arcade/SQL, text QC), zone 4 'output edge' (memos, "
        "per-finding notes), then the NEVER stamp on the middle. Key line: 'The LLM "
        "never touches the geometry. Never makes the decision. Ever.' In Slides: add "
        "Appear animations to the zones and the stamp for true builds. Transition: "
        "'Which raises the question everyone asks first — how do you do this safely?'"),
    4: ("Slide 5 · safety (~1:00). Walk the three guardrails fast — each is enforced by "
        "code, not policy: DATA BOUNDARY (the model has to read the data and the specs; "
        "it runs where you control the boundary — your workstation or a private, secure "
        "cloud) · READS, NEVER WRITES (read access yes; write access, network tools, "
        "acting tools no; proposals only — the failed agent-harness anecdote lands live "
        "here) · HUMAN SIGN-OFF + LABELED RECORDS (GRAMA). Close: 'The guardrails aren't "
        "policy — they're the design.' Transition: 'And this isn't hypothetical in Utah "
        "— it already happened next door.'"),
    5: ("Slide 6 · county workflow (2:00, slides-only). Give Nathan the nod in the room. "
        "What the AI did NOT do: value property, decide anything. It drafted the review "
        "queue — the appraiser makes the call. Hold that shape. Transition: 'The numbers.'"),
    6: ("Slide 7 · county numbers (~1:00). Read the tiles fast: 56,993 triaged, 86% "
        "ruled out (48,846), 7,494 desk reviews, 653 field visits, $160K/yr saved. Then "
        "the point: the model narrowed the work; humans did the valuations. Transition: "
        "'That's computer vision — narrow, trained, purpose-built. The LLM is a different "
        "beast. First, the clearest case of a check that must never leave deterministic "
        "code.'"),
}
for idx, text in g5_notes.items():
    s[idx].notes_slide.notes_text_frame.text = text

# — slide 5 · collapse the doubled eyebrow to its first (clean) run —
for sh in s[4].shapes:
    if sh.has_text_frame and "SAFELY" in sh.text_frame.text:
        p0 = sh.text_frame.paragraphs[0]
        runs = list(p0.runs)
        for r in runs[1:]:          # drop the appended " — How do we…?" tail
            r._r.getparent().remove(r._r)
        break

g5.save(r"slides/deck_g5.pptx")
print("deck_g5.pptx: notes + slide-5 eyebrow fixed")

# ————————————————————— deck_g5_beats2.pptx (slides 8–15) ———————————————————

b2 = Presentation(r"slides/deck_g5_beats2.pptx")
b = list(b2.slides)

# strip "BEAT N · " prefixes (the n/15 counter already numbers the slide)
b2_eyebrow = {
    0: "A CHECK THE LLM MUST NEVER DO",
    1: "THE DATA",
    2: "THE GATE",
    3: "THE GATE ISN'T BINARY",
    4: "THE REVIEWER",
    5: "THE FLIP",
}
for idx, label in b2_eyebrow.items():
    for sh in b[idx].shapes:
        if sh.has_text_frame and sh.text_frame.text.strip().startswith("BEAT "):
            p0 = sh.text_frame.paragraphs[0]
            runs = list(p0.runs)
            runs[0].text = label
            for r in runs[1:]:
                r._r.getparent().remove(r._r)
            break

b2_notes = {
    0: ("Slide 8 · Web Mercator (2:00, output/chart slide — NOT live). Key line: 'That "
        "is why ask-the-LLM-what-could-be-wrong is a real, cheap, zero-risk QC step — as "
        "a checklist generator. The LLM's knowledge is free; its arithmetic is a "
        "liability.' Transition: 'Now the harder case — the opinion that is confident, "
        "plausible, and wrong.'"),
    1: ("Slide 9 · duplicate-IDs (2:00, live begins here or cell-output slide). The "
        "duplicate-ID story: one parcel, seven buildings, each row a unit. Design lesson "
        "to say: validate at parcel level; handle near-duplicate geometries (A-0647) "
        "separately. Transition: 'The model looks at this and has an opinion. Watch the "
        "gate.'"),
    2: ("Slide 10 · the gate (1:00). The LLM looked at the 280 S Main St sample and "
        "confidently proposed a merge. The gate rule G1 rejected it: rows are units. Key "
        "line: 'The LLM's confidence is not a QC signal. The check is the signal.' "
        "Transition: 'And the gate isn't a wall — it has nuance. Three outcomes, not two.'"),
    3: ("Slide 11 · the gate isn't binary (3:00). Three outcomes, not two — the gate has "
        "nuance the LLM never sees. Downgrade = the check re-ranked the finding so human "
        "review effort goes where it matters. Legal floor: 58-22-102. Key line: 'Reject, "
        "downgrade, approve-then-review: the LLM never sees or influences any of the "
        "three.' Transition: 'Now what the person on the other end of the gate actually "
        "sees.'"),
    4: ("Slide 12 · the reviewer (2:30, pre-generated notes — never live-prompt on "
        "stage). Failure is visible and harmless: if the prose is wrong, the tech reads "
        "the evidence and overrules it. Worst case is a bad paragraph, not a bad parcel. "
        "This is the part reviewers will love — and the one place the LLM cannot do "
        "damage. Transition: 'Trust but verify — applied to the verifier.'"),
    5: ("Slide 13 · the flip (1:30; FIRST CUT if running hot — one spoken line: 'we also "
        "run the model backwards: it writes plausible-but-wrong parcels, we inject them, "
        "and grade our own checks'). Otherwise the beat nobody in the room has seen. The "
        "checks that missed are found before a resident finds them. Transition: 'So what "
        "can your shop do this month?'"),
    6: ("Slide 14 · take-home (2:00, flexes to 1:30 if hot: read items 1 and 2, point at "
        "the rest). Each item maps to the spectrum: outside (1), input edge (2–4), "
        "output edge (5–6), and 7 is the flip. Close: 'None of this needs permission "
        "beyond a conversation with your county attorney and IT.'"),
    7: ("Slide 15 · close (~1:30). Restate the thesis in one line, then the EO framing: "
        "'we're not asking permission for something edgy; we're implementing stated "
        "policy.' Thank the room; credit Nathan once more if he's still here. → Q&A "
        "block: expected order — what-if-the-model-is-wrong (point at slide 10), legality "
        "(slides 11 + 15), model/cost, why-not-let-it-drive (slide 5, card 2: one time "
        "it drove, it failed on nearly every tool call). Park deep ones to the break."),
}
for idx, text in b2_notes.items():
    b[idx].notes_slide.notes_text_frame.text = text

b2.save(r"slides/deck_g5_beats2.pptx")
print("deck_g5_beats2.pptx: eyebrows + notes fixed")
