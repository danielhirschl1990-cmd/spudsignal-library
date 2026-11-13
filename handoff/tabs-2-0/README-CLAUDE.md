# Task: build SpudSignal Library Update 2.0 (tabs) as a PR (do NOT merge)

Repo: danielhirschl1990-cmd/spudsignal-library. GitHub Pages serves `main`, so **any merge to main goes live**. Only open a PR. Daniel's team (CoS + Reviewer) merges after the review.

## What Daniel approved (13 Nov 2026, 23:52 CET)
Build the v2.1 prototype in `handoff/tabs-2-0/prototype/` into the real site:
- A shared tab bar (Library | Tenders | Map, plus What's new). Each page keeps its **own URL**; this is not a single-page app.
- A new `/whats-new/` page with Update 1.0–1.2 and **Update 2.0** (date set at go-live).
- One shared CSS file (`assets/spudsignal.css`), one font stack (no webfont), the same full legal footer on every page.
- Glossary and the single audience sentence per `glossary-slots-v2.md` / `text-slots-editor-2026-11-13.md`.
- URL filters (`?aud=`, `?country=`, `?q=`) carried across the tabs.
- Map cleanup per `map-changes-v2.md`: Pin **Option A** (keep the current pin coding, NOT option B), legend collapsed, Info/Sources & credits links, OSM attribution visible, country names.
- Library: a search, the two banners removed, and **expired entries hidden by default** ("64 current entries (38 expired hidden · show)"; no-JS shows all).
- Tenders: single column, max 820 px, and `#about-data` opens on hash.

## Hard rules (Reviewer requirements, see review-v1/review-v2)
- **Liability/disclaimer texts stay verbatim.** H05 footer sentence, exactly: "All documents are linked to their original publishers. Liability: entries are provided for information only, without guarantee of completeness or accuracy; the original document is authoritative." Keep "notice" in the Tenders warning line, F1, About this app, the time warning and the saved-entries note.
- Every tender card keeps: Checked date, deadline with time and zone, time-uncertain/correction/stale notes, "As published", and "One-off file" next to Add to calendar.
- Every map popup keeps: source, the approx. note and "Status open – not verified". The B1 line stays verbatim.
- Impressum, Privacy and Medieninhaber (media owner) appear on all pages.
- Data files must stay **byte-identical**: tender JSON block, `map/data.js`, `map/testlayers.js`, data.py.
- Do NOT touch `map/data.geojson`, `audience/map-crosswalk-2026-11-08.*`, `audience/build_crosswalk.py`, `filter.test.mjs`, README.md (PR #8 handles them). The map must not fetch data.geojson.
- Operating-plants toggle label: "Operating plants (28)" (28 plants on 27 pins; Unterföhring I+II share a pin).

## Generators (important)
The weekly builds regenerate the HTML from the Python generators in `handoff/tabs-2-0/generators/` (a copy of the production generators; `tabs/` is the Designer's half-finished start, see PAUSE.md and gen-patch-2026-11-13.diff). Change the **generators** so a rebuild produces the new design. Do not just hand-edit HTML. Put the final generator files in `handoff/tabs-2-0/generators-final/` and write `APPLY.md` (which file goes where).

## Checks before opening the PR
- No horizontal scroll at 390 px, tap targets ≥ 44 px, 0 console errors, works without JS, keyboard skip link.
- Grep: no "[EDITOR", "Clear all filters", "listings", "Projects & wells (#1".
- Screenshots of all 5 pages at 1280 and 390 px into `handoff/tabs-2-0/pr-check/`.
- `git diff --name-only` must not list the PR #8 files.

## Deliver
Branch `library/tabs-2-0`, open a PR against main (do not merge). Report the PR URL, head SHA and the check results to Daniel.
