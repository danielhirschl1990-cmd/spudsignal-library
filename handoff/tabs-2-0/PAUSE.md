# PAUSE – Library Update 2.0 (Tabs)

Paused: 13 Nov 2026, 23:58 CET, by Daniel's decision at 23:56 (passed on by the CoS). Reason: usage limit; Sunday's newsletter takes priority. Resume no earlier than Monday.

## State at the pause
- Prototype v2.1: done, Reviewer GREEN (review-v2-2026-11-13.md, ac7895e3). Kartograf confirmed #1–#5 and #7–#14; #6 uses his wording.
- Daniel's approval (23:52, via CoS):
  - tab bar with separate URLs
  - What's new and Update 2.0
  - pin Option A
  - Tenders in a single column
  - liability texts verbatim
  - open Editor decisions A–F stay at the live wording
  - no webfont
  - expired entries hidden by default
  - PR #8 is merged together with the package
- Generator rebuild: started, NOT finished, NOT tested.
  - Generator copy: work/gen/ (new: work/gen/tabs/tabs.py, tabs/assets/*, tabs/pretabs/*). /workspace/geothermie/library/ untouched.
  - work/gen-patch-2026-11-13.diff: an interim state, not final.
  - PR clone work/pr-src/: branch library/tabs-2-0-2026-11-13 created locally off main 368155e. Changes are staged only: assets/*, index.html, map/index.html. NOTHING committed, NOTHING pushed, NO PR opened.
- Backup: work/snapshot-pause-2026-11-13-2358.tgz (gen, pr-src, patch).
- Nothing live, no merge.

## Next steps (Monday, only after the CoS gives the go)
1. Re-fetch main and check whether PR #8 or other changes have come in; rebase the branch if so.
2. Finish the generator rebuild across all pages to match the v2.1 prototype. Data files (data.py, tender JSON, data.js, testlayers.js) stay byte-identical.
3. Kartograf requirements:
   - toggle label: testCounts operating = TL.operating.length (28), pin grouping OP07/OP08 unchanged
   - do NOT change or regenerate map/data.geojson, audience/map-crosswalk-2026-11-08.{csv,json,md}, audience/build_crosswalk.py, filter.test.mjs or README.md (PR #8 conflict); check with git diff --name-only
   - the map must not fetch data.geojson
4. Tests:
   - inventory diff against live (60 must-say items)
   - console, 390 px without horizontal scrolling, tap targets ≥ 44 px, keyboard, no-JS
   - URL filter carry-over, #about-data opener, grep for [EDITOR] and old terms, check.py
5. Parity check against the prototype (desktop 1280 and mobile 390, all 5 pages) into library-tabs/pr-check/.
6. Final generator patch plus APPLY.md for the CoS; commit, push, `gh pr create` (do not merge).
7. Reviewer check against the prototype; the Kartograf confirms the label (path and sha).
8. Deliver to the CoS: PR URL, head SHA, tests, screenshots.
