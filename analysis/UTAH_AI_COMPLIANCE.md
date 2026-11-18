# Using LLMs for GIS QC in Utah — compliance scan (2026-11-18)

Research pass on legal/policy hindrances for the talk's proposed LLM-assisted QC
architecture (LLM at the edges of the pipeline, deterministic checks and humans
in the middle, local model, data untouched by the LLM).

**Verdict: no showstoppers.** Three real constraints (surveying practice, records
law, approved-tools policy) — all of which the proposed architecture already
satisfies by design.

## 1. Surveying practice law — the one that bites

- Only a Utah-licensed PLS may retrace/establish boundaries: **Utah Code
  58-22-102** (practice of land surveying), UCLS Standards of Practice.
- GIS parcel boundaries and *legal* acreage change only via a survey filed with
  the County Surveyor plus action through the County Recorder. Cache County
  Surveyor FAQ states this directly; GIS boundaries only get adjusted to match
  filed surveys.
- Consequence: a QC pipeline may *flag* acreage/geometry drift and explain it,
  but the fix route is assessor/recorder records — never auto-editing geometry.
- Talk line: *"Our gate rejects geometry edits not just as a design choice —
  anything else is unlicensed practice."*

## 2. Records law — GRAMA + Government Data Privacy Act (GDPA)

- Utah local governments with adopted AI policies (Salt Lake City policy 52-13E;
  Greater Salt Lake Municipal Services District; Huntington City) converge on:
  **AI prompts, inputs and outputs may themselves be government records** —
  subject to GRAMA classification, retention and disclosure (Utah Code 63G-2).
- If an LLM-drafted note is used in county business (e.g. per-finding review
  notes), it is a record: archive it, apply retention, expect it in records
  requests.
- Mitigation (matches our design): stamp deterministic facts above the prose,
  label "AI-drafted, human-reviewed", keep the audit trail (we already emit
  `qc_audit_*.csv` / `qc_patch_*.json`).
- Parcel owner data is largely **public under GRAMA** (63G-2-201/-301); narrow
  opt-outs only (at-risk individuals 63A-19-408; `PROTECTED_RECORD`/`PRIVATEFLAG`
  flags — Utah County's land records API exposes both). So data sensitivity is
  not the barrier; tool authorization is (below).

## 3. Approved-tools policy for state employees

- **DTS Enterprise Generative AI Policy** (revised Aug 2025): executive-branch
  employees use only approved tools (Gemini / NotebookLM on utah.gov accounts);
  never enter private/controlled/confidential/restricted data into public AI
  tools; annual responsible-use training; label AI-generated products.
- Counties/cities are not bound by DTS policy but several mirror it locally.
- A local Ollama model (open weights, data never leaves the box) avoids the
  "public cloud tool" problem; still recommend a 15-minute IT/legal sign-off at
  any shop. Say this on stage — it preempts the most common objection.

## Explicitly cleared

- **Data licensing**: SGID/UUGRC parcels are CC BY 4.0 (documented in
  `DATA_LICENSE.md`).
- **Model licensing**: gemma4 and qwen3.5 are Apache 2.0.
- **Consumer-disclosure regime** (SB 149 AI Policy Act; Title 13-77 as amended
  2025): applies to consumer-facing/regulated-occupation interactions — an
  internal QC pipeline is out of scope; transparency obligations that do apply
  are met by labeling outputs.
- **Cloud vendor procurement**: not needed for the local-model posture.

## Statutory vs policy note

- As of 2025 the *statutory* written generative-AI-use-policy mandate applies to
  **law enforcement agencies** (SB 180 → Utah Code 53-25-902, effective
  2025-05-07; police-report AI disclaimers + author certification). Other
  executive-branch agencies follow DTS/EO policy, not statute.

## Governor's EO 2026-08 — "Pro-Human Approach to AI" (signed 2026-10-06)

Executive-branch requirements: AI-literacy training for employees; evaluate
cost-effective AI optimizations of business functions; document how AI systems
(inputs, outputs, decision-making roles) are integrated; **human-in-the-loop
review for determinations affecting individual rights**; GovOps leads
safeguards (incl. defense against rogue AI agents); annual progress report,
first due 2027-07-01. Preserves GRAMA/GDPA obligations explicitly.

**Kicker for the talk:** *"Utah's rules already describe our architecture.
Human-guided, documented, LLM-never-touches-the-data. We're not asking
permission for something edgy — we're implementing the stated policy."*

## Practical first step at any Utah shop

15 minutes with the county attorney / records officer + IT: confirm records
handling for AI-drafted notes, and whether an agency-specific approved-tools
policy applies. Patchy county-level coverage — some counties/municipalities
have adopted policies, many have none.

## Sources

- EO 2026-08: https://governor.utah.gov/wp-content/uploads/2026.10.06-Pro-Human-AI-Executive-Order-1.pdf
- Gov. Cox news release: https://governor.utah.gov/uncategorized/news-release-gov-cox-signs-executive-order-establishing-utahs-pro-human-approach-to-ai-in-state-government/
- GovOps implementation: https://govops.utah.gov/gov-cox-signs-executive-order-establishing-utahs-pro-human-approach-to-ai-in-state-government-govops-to-play-a-lead-role-in-implementation/
- GovTech coverage: https://www.govtech.com/artificial-intelligence/utah-governor-signs-executive-order-for-pro-human-ai
- DTS AI initiatives: https://dts.utah.gov/what-we-are-doing/our-initiatives/artificial-intelligence/
- UDOT responsible-use guidance: https://employeeresources.udot.utah.gov/news/archive-news/december-2025/responsible-use-of-ai-tools-and-data
- Title 13 Ch. 77 (consumer AI disclosures): https://le.utah.gov/xcode/Title13/Chapter77/C13-77_2025050820250508.pdf
- Utah Code 53-25-902 (SB 180, law-enforcement AI policy): https://le.utah.gov/xcode/Title53/Chapter25/C53-25-S902_2025050720250507.html
- Salt Lake City AI policy (Art. E): https://codelibrary.amlegal.com/codes/slc_utpolicy/latest/saltlakecity_manual_ut/0-0-0-12721
- Salt Lake County Assessor privacy (GRAMA/GDPA): https://www.saltlakecounty.gov/assessor/privacy-notice/
- Cache County Surveyor FAQ: https://cachecounty.gov/surveyor/faq.html
- UCLS Standards of Practice: https://www.ucls.org/assets/documents/UCLS%20Standards%2020100910.pdf
- UGRC Utah Parcels: https://gis.utah.gov/products/sgid/cadastre/parcels/
