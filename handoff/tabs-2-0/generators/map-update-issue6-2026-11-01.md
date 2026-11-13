# Live map – issue #6 weekly update (1 Nov 2026, ~23:58 CET)
Commit 7924a9d on top of 217c94e (spudsignal-library, main). Build: library/build_map.py (copy of growth/map-prototype/src/build.py + #6 rows; output straight to site/map). Backup of previous live data: /tmp/data.js.live, /tmp/data.geojson.live (also in git 217c94e).
Inputs only: issue-6-final.md, issue-6-final-sources.md, issue-6-map-locations.md / issues/src/issue6_content.py coords, site/tenders/tenders.json (33 entries, 2026-11-01 23:19). No BVG / map-test data.

Totals: 66 pins (35 project, 30 tender, 1 funding) + 2 nationwide calls in side panel (SDE++ NL, Horizon EU). Before: 57 pins.

Added project pins (#6, popup shows source + date + "Read in SpudSignal #6"):
- HVC pauses Alton after weak well test – NL, approx (Heerhugowaard), HVC news 29 Oct
- Geretsried heat buyer leaves Eavor contract – DE, city press release 21/2026, 26 Oct (REPLACES the #4 Geretsried pin; one pin per site)
- Vienna awards surface works for its first deep-geothermal plant – AT, approx (city), TED 749142, 29 Oct
- Eden Geothermal seeks more wells within its Cornwall site – UK, BBC/LDRS 28 Oct (no well count in popup title)
- First FER 2 geothermal auction: Jolanda di Savoia admitted (24.4 MW) – IT, approx (town), GSE 23 Oct
- First FER 2 geothermal auction: Castel Giorgio admitted (5 MW) – IT, approx (town), GSE 23 Oct
- North Brabant maps its geothermal potential – NL, approx (province centre), brabant.nl 26 Oct
Added tender pins (from tenders.json): Energies du Grand Paris TED 755201 (approx, Paris), St. Gallen HOCH TED 752632, Galway HSE TED 738167, Krafla Landsvirkjun TED 754152 (approx, plant; work at contractor's workshop), Grangegorman new notice TED 737356 (12 Nov; replaces 689259), Münster new notice TED 754784 (replaces 734244, still linked to #5).
Removed: Pessac BOAMP 26-93304 (deadline 30 Oct passed), old Grangegorman 689259, old Münster 734244, #4 Geretsried pin. Nationwide panel: HU KEHOP and DE Explorationsinitiative gone (removed from tender app), SDE++ NL and Horizon EU added.
Changed: legend "Projects & wells (#1–#6)"; all tender 'checked' dates 2026-11-01.
Not mapped (not in final text): GeoHardt/Schwetzingen, Ribeira Grande.
Checks: JSON valid; local headless render 66 markers, popups open, no JS errors; 44/45 links 200; #6 issue link 404 until #6 is published (slug confirmed in beehiiv draft). Live: /map/, data.js, data.geojson 200; data.js byte-identical to commit; all #6 items present.

## Follow-up 2 Nov 2026 (Daniel's decisions 00:00): sources for #1–#5 pins + one pin per site
- 28 older project pins (#1–#5) now show "Source (label, date) ↗" like #6. Link = the link printed in the published issue (issue-<n>-final.md), date = issue-<n>-final-sources.md. No new research, no BVG, nothing from map-test. Kalisz uses the dated Radio Poznań link (PGI note is undated). Jelenia Góra link (Nasze Miasto) answers 403 Cloudflare "Just a moment" to curl/headless – same link as published in #4 and in the Library.
- Geretsried replacement confirmed by Daniel.
- One pin per site: features with identical coordinates are merged into one pin; properties = primary entry + `entries` (all entries). Symbol rule: project if the site has a project entry, else tender, else funding (AFK combined-pin mockup: project symbol + badge); a small count badge shows the number of entries; popup lists every entry ("Same site · open tender / funding call") with title, type, source, date, deadline, checked date, issue link. Type/country filters work per entry (projects off -> merged tenders still show as tender pins). Expired tenders drop out per entry.
- Merged (11 sites, 66 -> 53 pins): Litoměřice SYNERGYS (project + 3 tenders), Preuschdorf, Aschheim/AFK, Ferney-Voltaire, Linnich, Călimănești, Kutno, Westland, Münster, Berlin-Marzahn, Paris (EGP tender 755201 + FEDER IDF funding call, both approx Paris pins).
- Builder: build_map.py (OLDSRC + merge step); backup build_map.py.bak-pre-merge-20261102. Previews: library/preview/map-merge/.
