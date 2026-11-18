# Working the deck — who does what

The deck is **PowerPoint / Google Slides** (the old HTML deck in `deck.html`
is kept only as a design reference — don't edit it for the talk).

- `deck_g5.pptx` — **slides 1–7** (title, problem, pitch, spectrum, safety,
  Utah County ×2). This is the file you've been editing and syncing back.
- `deck_g5_beats2.pptx` — **slides 8–15** (Mercator, duplicate-IDs, gate,
  gate nuance, reviewer, negative testing, take-home, close). Generated; to
  bring it into the Google deck use **File → Import slides**.
- `deck_g5_full.pptx` — **all 15 slides, already combined** (built by
  `merge_decks.py`). Import this one file and you're done — no manual slide
  import needed.

## Division of labor

**You — the words.** Edit slide text natively in Google Slides (upload / edit /
download the `.pptx` via Drive; PowerPoint is on the host machine only). Change
what sounds wrong. Don't worry about renumbering or re-laying-out — that's mine.

**Claude — the machinery.** Ask me for anything structural: new slides,
shapes/diagrams, re-laying-out a slide, renumbering, colors/sizes, speaker
notes. After you've made a batch of wording changes, send one message
("changed slides 2, 3, 7 — wording only") and I'll re-sync the outline
(`analysis/TALK_OUTLINE.md`) and the speaker notes to match — don't describe
the edits, they're already in the file.

## Conventions

- **Slide number = beat number.** Slide 7 is beat 7; the counter on every
  slide is `n / 15`. Cross-references in the outline and notes use slide
  numbers, so they stay unambiguous when slides move.
- Speaker notes carry the beat script (timing + key line + transition).

## Scripts (run with ArcGIS Pro's Python)

```powershell
$py = "C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"
& $py slides\build_deck_pptx.py      # rebuild deck_g5.pptx (overwrites hand edits — don't re-run blindly)
& $py slides\build_deck_beats2.py    # rebuild deck_g5_beats2.pptx (overwrites hand edits)
& $py slides\patch5_notes.py        # notes + eyebrow consistency pass (safe to re-run)
& $py analysis\dump_pptx.py  slides\deck_g5.pptx slides\deck_g5_beats2.pptx  # text dump for review
```

**Do not use the `-I` flag** for these — `python-pptx` lives in this
environment's user site-packages and `-I` breaks that import.

If something breaks, the files are in git — nothing is ever lost.
