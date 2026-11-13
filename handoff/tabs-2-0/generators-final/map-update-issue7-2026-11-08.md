# Live map – issue #7 weekly update (8 Nov 2026, ~21:30 CET)
Build: library/build_map.py (backup build_map.py.bak-pre-issue7-20261108), output straight to site/map (data.geojson, data.js; extra.json local only, untracked as before). Previous live data: /tmp/data.js.live, /tmp/data.geojson.live (also in git 88a2198).
Base: origin/main 88a2198 (includes the 8 Nov audience-filter PRs #1–#4; map/index.html audience UI kept, only the legend label changed). Audience labels on the map are still joined at runtime from /audience/assignments.json by exact source URL; the new #7 pins have no assignment (visible under "All", hidden when an audience label is selected).
Inputs only: issue-7-final.md, issue-7-final-sources.md, issue-7-map-locations.md, issues/src/issue7_content.py PLACES, site/tenders/tenders.json (30 entries, generated 2026-11-08 21:21 CET, live correction check). Croze village coords: OSM Nominatim 8 Nov 2026 (approx). No BVG candidates, nothing from map-test/.

Totals: 61 pins (33 project, 27 tender, 1 funding) + 2 nationwide calls in side panel (SDE++ NL, Horizon EU). Before: 60 pins. (Client-side, tenders whose deadline passes drop out automatically: on 9 Nov Charles Univ. wellheads 684005 and Linnich 698651 → 59.)

Added project pins (#7; popup: source label + date, "Read in SpudSignal #7"):
- OMV selected for Amsterdam–Amstelveen development – NL, approx (midpoint Amsterdam/Amstelveen; drilling site still to be selected), TED 769576-2026 (award), 5 Nov
- Exergy signs a 33 MWe geothermal plant contract – TR, approx (Germencik town, Mehmet Ege plant; not Exergy HQ), Exergy release, 5 Nov
- Münster investigates another cold heat-network site – DE, approx (Handorf district, Kötterstraße), Stadtwerke Münster release, 2 Nov. Separate from the Münster research-well pins; no borehole-count in title (one 300 m exploratory borehole per source; Kirschgarten 39 boreholes = context only, no pin)
Updated (not duplicated):
- Kutno: existing GT-1/GT-2 project pin (same coordinates) now carries the #7 financing news (NFOŚiGW release, 4 Nov, "Kutno secures more than PLN 59m for geothermal heat"). Because it no longer cites TED 725171, the same-notice dedupe no longer hides it: the open #5 drilling tender TED 725171 (24 Nov) stays a separate tender pin at the same site (spiderfy, as decided 2 Nov).
- Kaba: new notice TED 763136-2026 (same procedure, deadline 24 Nov 2026, 11:00 CET) at the existing Kaba location; old notice 729019 (3 Nov) dropped as expired.
Added tender pins (from tenders.json, now allowlisted from issue #7):
- Munich Michaelibad heat-station excavation, TED 766383-2026 – exact (Heinrich-Wieland-Str. 16), requests to participate by 7 Dec 2026, 13:00 CET
- Szeged geothermal heat supply, TED 759601-2026 – approx (town; heat supply, not a drilling site), 2 Dec 2026, 10:00 CET
- Croze town-hall renovation (geothermal drilling + GHP lots), BOAMP 26-103155 – approx (village), 18 Nov 2026, 12:00 CET
- Kaba TED 763136-2026 (see above)
Removed (deadline passed / dropped from tenders.json): Kaba 729019 (3 Nov), Winterthur 643535 (4 Nov), ValDem Vendôme 26-95465 (5 Nov), SYNERGYS liner hanger 679859 (6 Nov), Aussac-Vadalle 26-101091 (6 Nov), Villiers-le-Bel/Gonesse AMO 26-102183 (6 Nov), Litoměřice BTES 730837 (6 Nov).
Changed: legend "Projects & wells (#1–#7)"; all tender 'checked' dates 2026-11-08; Grangegorman TED 737356 deadline text now "12 Nov 2026, 15:00 CET as encoded in TED; confirm the buyer portal's closing time" (Reviewer 8 Nov, via tenders/overrides.json). Charles University project pin keeps the 8 Nov title correction ("wellheads and frac trees") – ported into build_map.py.
Not mapped: Estonia STEIGER award TED 770504 (no verified borehole sites; notice names Tõrva/Põlva/Rõuge only – no pin, no region marker), ADEME Fonds Chaleur suspension (nationwide, not an open call), FEDER IDF / SDE++ / Horizon unchanged (Paris pin + nationwide panel).
Checks: data.geojson / data.js / extra.json / tenders.json valid JSON; local headless Chrome render: "61 pins shown" (33/27/1), no JS errors; map links 65/67 HTTP 200 – Jelenia Góra Nasze Miasto 403 (Cloudflare to curl, known since 2 Nov), "Read in SpudSignal #7" 404 until #7 is published (slug spudsignal-7-munich-works-kaba-reset-kutno-funding, same convention as #6, whose link now answers 200).
Note: audience/filter.test.mjs snapshot assertions (92 library cards, 33 tenders, 60 pins, "unchanged vs main") now fail because of the content update; functional filter tests unaffected. Not edited.
