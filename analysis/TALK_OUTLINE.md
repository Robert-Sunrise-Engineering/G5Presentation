# Talk outline — FULL BUILD (2026-11-18)

**Trust but Verify: LLM-Assisted GIS Data QC**
**10:50–11:20, exactly 30 min, back-to-back after another talk.**
**Last talk before break** — the room can't leave mid-talk, so there is a
**formal 5-minute Q&A block** at the end; questions during content get parked
("hold that — I'll take it in the block"). Overrun, if any, spills into break.
Plan **~2–3 min connect buffer at the top** — the opening runs slides-only so
the room never waits on the system. Audience: municipal/county/state GIS
professionals (Esri-centric). Nathan Thomas (Utah County, UGIC-2026 award
project) is a personal friend — credit him by name in slide 6; confirm his
project details with him before presenting.

Thesis sentence (open it, land it, close it):
> *The LLM never touches the geometry, never makes the decision. It works the
> edges of QC — where the work is language — and deterministic checks and
> humans stay in the middle. Utah's own rules already describe exactly this.*

Timing math: **~24 min content** + connect buffer
absorbed by the slides-only opening + **5:00 formal Q&A** = hard stop 11:20.
Slides 1–8 are the slides-only spine (~9 min); live/notebook content begins at
slide 9 (duplicate-IDs). Slide 13 (negative testing) is the first cut when
running hot.

---

## SLIDE LIST (15 slides — user order, deck_g5.pptx + deck_g5_beats2.pptx)

| # | Slide ID | Slide title | Notes |
|---|----------|-------------|-------|
| 1 | TITLE | Trust but Verify | Holds while connecting |
| 2 | PROBLEM | QC is an afterthought | Single panel: "QC is always the last step" — projects overrun, errors surface years later |
| 3 | ECONOMICS | What if we keep the budget — and do 4–5× the checks? | Deterministic pipeline + "the LLM watches the edges" (incl. domain recommendations + accurate metadata) |
| 4 | SPECTRUM | Good at language. Bad at math — and at your actual workflows. So place it. | 5 stations + NEVER stamp |
| 5 | SAFETY | It's safe because of what it can't do. | 3 guardrail cards: data boundary · reads/never writes · human sign-off + labeled records (GRAMA) |
| 6 | UC-WORKFLOW | It already happened next door — built in-house. | Nathan Thomas credit; county as case study, not hook |
| 7 | UC-NUMBERS | 56,993 properties. 86% never visited. | Stat tiles + $160K/yr |
| 8 | MERCATOR | The LLM can name this trap. It must never do the math. | +59.3% bars; may/never cards |
| 9 | DUPIDS | 71% of rows share a PARCEL_ID — so what? | 280 S MAIN ST: 7 rows, 7 real units |
| 10 | GATE | The proposal is wrong. The gate catches it. | proposal JSON → G1 rejection → review table |
| 11 | GATE-NUANCE | Reject, downgrade, approve-then-review. | E-0337 downgrade + A-0729 pending + 58-22-102 |
| 12 | NOTES | What the 3pm map-tech actually sees | Two flag cards side by side |
| 13 | NEGTEST | Flip it: the LLM audits your QC | **First cut** — ASK / INJECT / RUN |
| 14 | CHECKLIST | Seven things your shop can do this month | List + repriced-QC payoff |
| 15 | CLOSE | The model works the edges; the checks and humans stay in the middle | EO 2026-08 + thesis restate + contact |

---

## RUN OF SHOW — slide by slide

### Slide 1 — Title (0:00)
Holds on screen while the previous talk ends and you plug in. Put
`gemma4:12b · Ollama · ArcGIS Pro 3.7` small at the bottom — your credibility
stack, visible before you speak.

### Slides 2–3 — The problem: priced by leftovers (2:00) *slides-only*
- **Slide 2 (cold open, consultant authority, ~90s script):**
  - "The 5-year cycle is hard — that's true, but it's not the real problem."
  - "The costs of bad data are *diffuse*. A wrong acreage lands on an
    appraiser's desk, a stale address on dispatch, a duplicated parcel in a
    resident's mail. Small each time, almost never traced back."
  - "But the cost of *doing* QC is concentrated. It arrives as a budget
    sentence: *the best you can do in 20 hours.* Not scoped to risk — scoped
    to what's left over."
  - "My worst — favorite — piece of evidence: I'm hired repeatedly for the
    same problems. Often the second or **third invoice** for one data issue:
    once to create it, once to discover it, once to fix it. That's data debt
    compounding — at consultant rates."
  - Transition: "So I'm not here to sell a philosophy — here's the pitch."
- **Slide 3 (the promise, ~30s):** "So I'm not here to sell a philosophy. The
  LLM changes the unit economics: it collapses the cost of the language-shaped
  parts of QC — reading the spec, drafting the check, writing the memo. The
  deterministic checks those feed stop competing with essential projects.
  Same 20 hours, four or five times the checks. That's the whole pitch."
- **Transition:** "The LLM works the edges. The real question is where,
  exactly."
- Deliver the anecdote with anonymized clients ("a mountain-west county").
- Watch: keep this tight; slack is nearly zero.

### Slide 4 — The spectrum: where should the LLM sit? (3:00, builds ×3)
- Build 1 — **Outside the pipeline:** reading documents — state schemas, data
  dictionaries, policy PDFs → gap reports and checklists. No data touched.
- Build 2 — **The input edge:** drafting checks. Analyst says it in English;
  LLM writes candidate Arcade/SQL/Python; a human reviews, versions, owns it.
  Also: normalizing addresses/owner names, adjudicating borderline text pairs.
- Build 3 — **The output edge:** triage memos from verified findings,
  per-finding explanations for reviewers.
- Build 4 — **The middle — mark it, then write NEVER across it:**
  detection and decisions. "The LLM never touches the geometry. Never makes
  the decision. Ever."
- **Key line:** "The LLM is good at language and meaning, bad at math and
  geometry. QC problems that are language problems — give to it. QC problems
  that are math problems — never."
- **Transition:** "Which raises the question everyone asks first — how do you
  do this safely?"

### Slide 5 — Safety (1:00)
Three guardrails, each enforced by code: **data boundary** — the model
*has* to read the data and the specs; it runs where you control the boundary
(workstation **or a private, secure cloud**, e.g. a hosted Ollama) ·
**reads, never writes** — read access yes, write access / network / acting
tools no; proposals only, and the failed agent-harness anecdote lands live
here · **human sign-off + labeled records** (GRAMA). Close with: "The
guardrails aren't policy — they're the design." (Spectrum zone 1 footer
matches: *reads everything — writes nothing*.)
- **Transition:** "And this isn't hypothetical in Utah — it already happened
  next door."

### Slides 6–7 — Utah County: it already happened next door (3:00) *slides-only*
- **Slide 6:** Utah County GIS Division built it themselves, no vendor:
  aerial imagery → AI building-footprint detection → compare against assessor
  building sketches → match scores in ArcGIS Pro → green/yellow/red →
  web app (Maps SDK for JavaScript). **"My friend Nathan Thomas built this"** —
  give him the nod in the room.
- **Slide 7:** 56,993 properties approaching reassessment · 48,846 strong
  matches (86% ruled out) · 7,494 flagged for review · 653 field-inspection
  candidates · ~$160K/yr outsourcing eliminated · UGIC 2026 award.
- **Land the pattern, ~30s:** "Notice what the AI did *not* do: it didn't
  value property. It didn't decide anything. It drafted the review queue —
  the appraiser still makes the call. Hold that shape; it's everything."
- **Transition:** "That's computer vision — narrow, trained, purpose-built.
  The LLM is a different beast with different powers and different failure
  modes. First, the clearest case of a check that must never leave
  deterministic code."

### Slide 8 — Web Mercator trap (2:00) *output/chart slide, not live*
- State the fact: countywide parcels in native CRS inflate area **+59.3%**
  vs EPSG:5070 (Albers). Acreage comparisons against stated values are garbage
  until reprojected.
- The point on the spectrum: the *knowledge* of this trap is language —
  an LLM can tell you "your native CRS area is not defensible, check it in
  equal-area." But the *verification* is arithmetic in arcpy. The LLM flags
  the possibility; the code proves it.
- **Key line:** "This is why 'ask the LLM what could be wrong with your data'
  is a real, cheap, zero-risk QC step — as a checklist generator. The LLM's
  knowledge is free. Its arithmetic is a liability."
- **Transition:** "Now the harder case — the one where the LLM has an
  opinion, and the opinion is *confident, plausible, and wrong.*"

### Slide 9 — Duplicate-ID ≠ duplicate parcel (2:00) *live begins here*
- **Evidence:** Kanarraville subset, 508 rows: **71.3% share a
  PARCEL_ID**, 69.7% duplicate geometries — but the parcel is fine. 280 S
  MAIN ST: 7 rows, same parcel, `HOUSE_CNT = 7`, each row a real unit
  (varying `BLDG_SQFT`, `BUILT_YR`, `CONST_MATERIAL`). Zero cross-parcel
  overlaps. Design lesson: validate at parcel level (dissolve unique
  geometries by PARCEL_ID), not row level.
- **Live notebook (or pre-run cell-output slides):** local model
  (`gemma4:12b`, Ollama, JSON-schema output, ~11 s a batch) sees the sample
  rows and confidently proposes `merge_rows` on the 280 S MAIN ST group.
- **Transition:** "The model looks at this and has an opinion. Watch the
  gate."

### Slide 10 — The gate catches it (1:00 — slides 9–10 are one 3:00 beat)
- Gate rule **G1 rejects it** — the 7 rows are real units, not
  duplicates. Show the review table: 1 G1 rejection, 1 G5 downgrade, 5 G7
  accepts.
- **Key line:** "A wrong proposal costs seconds to generate and one review
  row to discard — *because the gate stood between it and the data.* The
  LLM's confidence is not a QC signal. The check is the signal."
- **Transition:** "And the gate isn't a wall — it has nuance. Three outcomes,
  not two."

### Slide 11 — The gate isn't binary (3:00)
- **E-0337-0002-00R1:** stated 10.11 ac vs 0.885 mapped (11.4×) — the gate
  doesn't reject, it **downgrades** (G5): pattern matches a clipped/part
  footprint, so "fix the acreage" is the *wrong* fix. Human review order
  changed by the gate's reasoning.
- **A-0729-0002-0002:** stated 0.988 vs geometric 0.491 ac — accepted as a
  real inconsistency, but the edit **waits for human approval** (one click)
  rather than applying.
- **The legal floor (one slide line):** surveying practice — Utah Code
  58-22-102. Boundary/acreage corrections route through the County Surveyor
  (filed survey) and County Recorder. "The gate refusing to touch geometry
  isn't just a design choice — *anything else is unlicensed practice.*"
- **Key line:** "Reject, downgrade, approve-then-review: three outcomes the
  LLM never sees or influences. That's what 'deterministic gate' means in
  practice."

### Slide 12 — What the 3pm map-tech sees (2:30) *pre-generated*
- Show two flag cards side by side, prose **pre-generated from the real audit
  CSV** (not live):
  - **A-0729** (real entry error): "stated 0.988 ≈ 2× mapped 0.491; boundary
    uncontested; looks like transposed/duplicated digits; confirm with
    assessor record — if geometry matches the plat, fix the source record,
    not the geometry."
  - **E-0337** (looks like a bug, isn't): "0.885 vs 10.11 with no neighbor
    overlap — matches clipped/excluded footprint; do NOT 'correct' acreage to
    stated; verify footprint against the survey first."
- Same check fired both times; same threshold; the deterministic checker can
  never produce these two different explanations. That's the LLM's output-edge
  value: it makes flags *meaningful to the human who acts on them.*
- **Guardrails, said on screen on the slide:** deterministic facts stamped
  above the prose; LLM output is advisory-only, one structured field;
  labeled **"AI-drafted, human-reviewed"**; and the note is a *record* under
  GRAMA — archive it like any other record.
- **Key line:** "This is the part your reviewers will use and love — and it
  is the one place in the pipeline where the LLM literally cannot do damage."
- **Transition:** "Trust but verify — applied to the verifier."

### Slide 13 — Flip it: the LLM audits your QC (1:30; FIRST CUT if hot)
- Invert the pipeline: LLM generates plausible-but-corrupted parcels (swapped
  acreages, impossible build dates, missing units, transposed digits),
  injected programmatically, and you check: did the checks catch them?
- Negative testing is a *language* task — generating realistic-looking wrong
  data is exactly what these models are dangerous at. Nothing else generates
  adversarial test data this cheaply.
- **Key line:** "Trust but verify — applied to the verifier."
- HOT: compress to one spoken line + slide left unread.

### Slide 14 — Take-home: QC scoped by risk, priced in minutes (2:00; flexes to 1:30)
- Seven adoptable-Monday items, each mapped to the spectrum:
  1. **Spec reconciliation** — feed the state schema / your data dictionary to
     the LLM → gap report (missing fields, population rates vs requirements).
  2. **English → Arcade** — plain-language check described; candidate Arcade
     attribute rule drafted; human reviews and owns it.
  3. **Text QC** — situs addresses, owner names: normalization and borderline
     pair adjudication, suggestions-with-evidence only.
  4. **Domain + metadata** — better domain recommendations and accurate
     metadata from verified usage.
  5. **Triage memos** — verified findings → readable, prioritized English for
     the supervisor.
  6. **Per-finding notes** — slide 12's card in every review queue.
  7. **Negative testing** — one adversarial pass against your own checks.
- **Payoff line (closes slide 3's promise):** "The 20-hour cap stops being the
  ceiling. The language-shaped parts stopped being hourly labor. QC finally
  gets scoped by risk, priced in minutes — and stops losing the budget fight."
- **Transition:** "None of this needs permission beyond a conversation with
  your county attorney and IT."

### Slide 15 — Compliance in one slide + close (1:30) — thesis lands here, then hand off to the Q&A block
- **EO 2026-08 (Oct 2026, Gov. Cox):** human-guided, documented AI
  integration, human-in-the-loop review for determinations affecting rights.
  "Utah's rules already describe this architecture. We're not asking
  permission — we're implementing stated policy."
- One line on posture: local Ollama model (Apache 2.0), CC BY 4.0 data, data
  never leaves the box; first step anywhere: 15 min with county attorney + IT.
- **Restate the thesis; thank the room; credit Nathan again if he's present.**
- Contact + repo pointer on the slide.

---

## Q&A block — formal, 5:00 (≈11:14–11:19, hard stop 11:20)

- Run it plainly: repeat each question for the room, answer short, and park
  the deep ones ("find me at the break — I'm buying coffee"). Being last
  before break means no one leaves: you can safely run to 11:19.
- **Most likely questions, in asking order:**
  1. *"What if the model is wrong?"* — slide 10 already answered this on
     stage; point back at the gate rejection rather than re-theorizing.
  2. *"Is this legal in Utah?"* — answer in three clauses: surveying law
     gates geometry (58-22-102), GRAMA/GDPA makes the notes records (label
     and archive), DTS approved-tools applies to state employees (local
     model avoids it; get 15-min IT/attorney sign-off anyway).
  3. *"Which model / what does it cost?"* — one GPU-class workstation, open
     weights, no per-token spend; see back-pocket for model numbers.
  4. *"Why not let it drive the whole session?"* — the bounded-subroutine
     anecdote (full version in back-pocket).
- One question deserves a sharp answer because it's the counter-thesis:
  *"Isn't this what Utah County's CV model does without any LLM?"* — Yes, and
  CV is the right tool for imagery. The LLM takes the parts CV can't: text,
  specs, prose, code drafts. "AI-in-QC is a placement question, not one
  technology."
- If silence: don't fill it — ask yourself one ("the question I get most is
  'can it just do the edits?' — here's why no") and answer it, then close.
- Close the block by restating the thesis in one line, thank the room,
  credit Nathan once more, done by 11:20.

## Q&A back-pocket (detail prep for the block)

- **"Why not let the LLM drive the whole session?"** — Bounded-subroutine
  anecdote: the same local model, run as an agent driver inside Claude Code
  against an Ollama gateway, failed repeatedly on tool-call parsing and
  context (n_ctx_slot 4096 vs what agent harnesses need); native single-turn
  JSON calls at `num_ctx 8192`, temp 0, `think false` are schema-valid every
  run. Agent bench scores (tools 100) did not transfer to an agent harness.
- **"Which model?"** — gemma4:12b primary (Apache 2.0, 8 GB, ~93 tok/s on this
  12 GB laptop GPU); qwen3.5:9b fallback. Local-first for records/data posture.
- **"Is this legal in Utah?"** — Surveying law (58-22-102) gates geometry;
  GRAMA/GDPA: notes are records, label them; DTS approved-tools applies to
  state employees (Gemini/NotebookLM), counties vary → 15-min attorney/IT
  sign-off. Parcel owner data is largely public under GRAMA (63A-19-408
  narrow opt-outs).
- **"What does this cost?"** — One GPU-class workstation (12 GB VRAM class
  runs it), open weights, no per-token spend; the cost is prompt engineering
  and review discipline, which you can see in the notebook.
- **"What if the model is wrong?"** — It was (slide 10). Show the gate doing its
  job; that *is* the answer to the question.

## Contingencies

| Risk | Response |
|------|----------|
| Pro/arcpy won't cooperate | Slides 9–10 hold pre-run cell outputs; they become a narrated slide walk |
| Running hot (>2 min behind by slide 8) | Slide 13 (negative testing) → one line with slide unread; slide 14 (take-home) → two items + payoff line; connect buffer already covered at the top |
| Room is skeptical/hostile on AI | Lean harder on slides 6–7 (Utah County precedent) and slide 11 (surveying law); LLM shown only in gated/advisory roles |
| "Can I get this?" | Notebook, audit CSV/patch JSON, and all docs are in the repo; DATA_LICENSE covers redistribution (CC BY 4.0) |

## Demo plan

- **First ~9 minutes (slides 1–8) are slides-only** — the connect buffer never
  delays the room; live/notebook content begins at slide 9.
- Primary: `qc_demo.ipynb` slides 9–10 in ArcGIS Pro; slide 8 is a chart slide.
- Slide 12 notes pre-generated from `analysis/qc_audit_20261117_143020.csv`.
- **Backup: screen-capture recording of the notebook run** + cell-output
  slides for slides 9–10, ready to switch mid-sentence.

## Build checklist (ordered, talk at 10:50)

1. Slides 1–8 — the no-live-content spine.
2. Slide 12's two flag cards generated from the audit CSV.
3. Slides 9–10 with pre-run cell outputs as the fallback variant.
4. Slide 13's negative-testing beat (or its one-line fallback).
5. Slides 14–15 + Q&A back-pocket one-pager.
6. Screen-capture backup of the notebook run.
7. Optional: verify notebook runs in Pro's Notebooks pane.

## Decisions this outline locks

- **Formal 5:00 Q&A at the end** — content is ~24 min; questions during content
  get parked to the block. Last-before-break placement makes 11:20 the soft
  edge (overrun = break time), but plan against it.
- **User narrative order (2026-11-18):** Utah County is a *case study after
  the placement + safety questions*, not a lead. New **Safety slide** (5)
  drafted from the compliance scan; deck total is now **15 slides**, counters
  `n / 15`.
- Keep the existing notebook as-is; proposals→gate flow presented as designed
  (hypothesis vs decision), not rebuilt as rule-authoring.
- Rule-authoring reframe lives in slide 14 as a take-home, not a notebook
  rebuild.
- Per-finding explanations pre-generated; no live prompting on stage.
- Nathan's Utah County project is slides 6–7 with on-stage credit.
