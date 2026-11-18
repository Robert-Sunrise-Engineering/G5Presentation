# Working the deck — who does what

**File:** `slides/deck.html` — open in any text editor (VS Code, Notepad++).
**To present:** open in a browser → `F` for fullscreen → arrow keys navigate.
Each save just needs an `F5` in the browser.

## Division of labor

**You — the words.** Edit text directly inside the marked sections of
`deck.html`. The header comment at the top of the slide markup lists exactly
what is safe to touch: `<h2>`, `<li>`, `<p>`, `<span>`, `<h3>`, pull quotes.
Change what sounds wrong, save, refresh. No chat round-trip needed.

**Claude — the machinery.** Ask me for anything structural: new slides,
re-laying-out a slide, the SVG diagrams, renumbering, colors/sizes, and
building the remaining beats (8–14). Also: after you've made a batch of
wording changes, send one message ("changed slides 2, 3, 7 — wording only")
and I'll sync the outline (`analysis/TALK_OUTLINE.md`) and speaker script to
match — don't describe the edits, they're already in the file.

## Editing rules (short version)

1. Change text between tags, not the tags themselves.
2. One bullet = one `<li>`; keep it on one line.
3. Leave `style="…"`, `cqw` numbers, the `<script>` block, and the slide-4
   `<svg>` alone.
4. `<em>` inside an `<h2>` = the orange accent — use it for the one phrase
   the slide is really about.

## If something breaks

Reopen a broken slide in the browser (`F5`); if layout breaks, revert your
last edit — or just tell me what you changed and I'll fix it. The file is in
git, so nothing is ever lost.
