# Submission Email — Draft

> Paste into Gmail (recipient: `talha@ideabuilders.studio`). Update the **bracketed** sections before sending. Don't include the "Notes for the sender" footer when you send.

---

**To:** `talha@ideabuilders.studio`
**Subject:** AI Engineer Take-Home Submission — [Your name]

---

Hi Talha,

Submitting my take-home for the AI Engineer role.

A short intro: [1–2 sentences — who you are, what you've built recently, why this role interests you. Mention any prior work that's directly relevant — RAG, document AI, agentic systems, etc.].

**Repo:** https://github.com/sufian07/legal-ai-assessment

Collaborators `tsensei` and `abubakarsiddik31` have been invited.

**What I built.** An internal workflow for processing messy legal-style documents end-to-end: OCR + structured extraction (clean PDFs, scanned PDFs, images, handwriting via TrOCR) → grounded retrieval over a Chroma vector store with stable citation IDs → a Case Fact Summary draft generator with inline `[doc_id:chunk_id]` citations and a post-generation validator that strips unresolved citations → an edit-learning loop that captures operator edits, classifies them into reusable patterns, and feeds them back into the next draft as rules + few-shot examples. There's an admin dashboard (Streamlit) that wraps every stage so the operator never needs to drop to a terminal.

**Most interesting tradeoff.** I deliberately kept the learning loop at the prompting layer rather than reaching for fine-tuning. It adapts within a session, needs no training infrastructure, and the rubric weights *meaningful improvement* — which is observable in edit-distance reduction between v1 and v2 — over training rigor. Full reasoning in `ASSUMPTIONS.md`.

**Reviewer fast-path.** Start at `README.md`. Architecture in `ARCHITECTURE.md`, tradeoffs in `ASSUMPTIONS.md`, evaluation methodology in `eval/README.md`. The repo ships pre-computed `processed/` and `outputs/` so the dashboard runs end-to-end without an API key (review mode).

Happy to walk through any part of it.

— [Your name]
GitHub: [github.com/sufian07](https://github.com/sufian07)
[Optional: phone / Calendly link]

---

## Notes for the sender — don't email these

- **Late by one day** — brief deadline was Friday, May 15 2026; current date is May 16. If you've negotiated an extension, no need to mention. Otherwise, acknowledge briefly ("apologies for the day's slip — happy to discuss") and don't over-explain.
- **Keep it under ~200 words.** Reviewers scan, they don't read. The current draft is ~180 words excluding signature and notes — fine.
- **Don't list features.** The repo lists features. The email gives context the repo can't: who you are, what's interesting, where to start.
- **Tone.** Confident, terse, no hedging. The work speaks for itself.
- **Before sending:**
  - [ ] Filled the `[bracketed]` placeholders
  - [ ] Re-read the repo's `README.md` to make sure setup instructions are accurate
  - [ ] Confirmed both collaborators show as Pending or Accepted on the GitHub repo settings page
  - [ ] Removed this entire `## Notes for the sender` section
