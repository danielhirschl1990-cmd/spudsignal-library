# Review – Library page "Open deep-drilling tenders & funding calls" (draft, not live)
Reviewer, 23 Oct 2026, 14:xx Berlin (CEST). Sources: TED Search API v3 (all 15 TED notices plus every notice sharing their procedure-identifier), BOAMP open data (raw eForms `donnees` and linked RECTIFICATIF notices), the official programme pages. Nothing invented; anything unverifiable is marked as such.
DST: Europe switches to winter time on 25 Oct 2026 at 01:00 UTC, so every deadline on or after 25 Oct is in CET (+01:00), EET (+02:00) for RO, and GMT (+00:00) for IE.

## Verdict: NOT READY. 2 RED, 6 YELLOW, 19 GREEN. Publish only after the RED items are fixed.

## RED
1. **TED 670200-2026 (CZ, ČGS/Univerzita Karlova, BTES boreholes).** A new notice in the same procedure, **TED 730837-2026**, was published on 22 Oct 2026. Its deadline is **06 Nov 2026, 15:00 CET** (15:00+01:00). The page still shows 30 Oct.
   Fix: deadline_iso `2026-11-06T15:00:00+01:00`; text "06 Nov 2026, 15:00 CET (extended; TED 730837-2026)"; URL to https://ted.europa.eu/en/notice/-/detail/730837-2026. Also add Univerzita Karlova as co-buyer: the notice lists both.
2. **BOAMP 26-93304 (Pessac, Bellegrave).** Correction notice **BOAMP 26-101172** (19 Oct 2026) says: "Au lieu de 26/10/2026 à 13h00, lire **30/10/2026 à 12h00**". The page shows 26 Oct 13:00.
   Fix: "30 Oct 2026, 12:00 CET (rectificatif 26-101172)". A second correction, 26-94401 (30 Sep), only changes the lot-1 information (PSE acid injection) and does not touch the deadline.

## YELLOW
3. **TED 664748-2026 (SGU, Borrtjänster).** The notice encodes `2026-10-26` `00:00:00+02:00`. That is the summer offset on a winter-time date. Read literally it is 25 Oct 2026 22:00 UTC = **25 Oct 23:00 CET**. Read nominally (local midnight) it is 26 Oct 00:00 CET = the end of 25 Oct. Earlier notice 652643-2026 had 22 Oct, so this is already the extension.
   Fix: "Ends 25 Oct 2026 (end of day, Swedish time). The notice encodes 26 Oct 00:00 +02:00, which taken literally is 23:00 CET on 25 Oct. Submit by 23:00 to be safe." Note that the deadline falls on a Sunday and is effectively expired by publication; if the page goes live after 25 Oct, remove the entry.
4. **TED 660087-2026 (Szeged).** The notice says `11:00:00+02:00` on 26 Oct, again a summer offset on a winter date. Read literally that is 09:00 UTC = **10:00 CET**. The nominal clock time is 11:00. The EKR (Hungarian procurement portal) was not checked because it needs a login, so this is not verifiable.
   Fix: "26 Oct 2026, 11:00 local as entered (notice offset +02:00 = 10:00 CET if taken literally; check EKR)". Expires on Monday; remove after that. Scope: purchase of geothermal **heat** (CPV 09320000), so it is not a drilling job (see Scope).
5. **BOAMP 26-100440 (CNRS DR13).** Raw eForms: EndDate `2026-11-17+01:00`, EndTime `12:00:00.000+02:00`. The date and time offsets contradict each other. The BOAMP field shows 12:00 "+00:00", which is unreliable. The nominal value is **12:00 Paris**; read literally it is **11:00 CET**. The consultation rules (RC) are only on the buyer profile behind a login and were not checked.
   Fix: "17 Nov 2026, 12:00 Paris time as entered (notice offset inconsistent; literally 11:00 CET; check RC)". The page currently shows only "11:00 CET", which is defensible but hides the conflict.
6. **TED 689259-2026 (Grangegorman, IE).** The notice gives `15:00:00+01:00`. In November Ireland is on GMT (+00:00), so the literal value is **14:00 Irish time = 15:00 CET**. The nominal value would be 15:00 Irish time. eTenders was not checked (login), so this is not verifiable.
   Fix: "05 Nov 2026, 15:00 CET = 14:00 Irish time (notice +01:00; eTenders may state 15:00 local; check)". The present "15:00 CET" is correct as an instant but misleading for Irish readers.
7. **TED 669195 (Prenzlau), 701161 (AFK), 704493 (Beauvaisis).** These are **requests to participate**, not tender deadlines: the API has no tender-receipt date, only a deadline-receipt-request date. The dates and times match (27 Oct 12:00 CET, 11 Nov 12:00 CET, 02 Nov 11:00 CET).
   Fix: label them "Requests to participate: …".
8. **HU KEHOP.** The official title is "**Geotermikus fúrási kockázatok csökkentése**", code **KEHOP-Plusz-4.2.4-25** (Széchenyi Terv Plusz). Sources: https://www.palyazat.gov.hu/programok/szechenyi-terv-plusz/kehop-plusz/kehop_plusz-4.2.4-25 and the felhívás PDF (cover: "Felhívás geotermikus fúrási kockázatok csökkentésének előkészítésére"). The latest notice (közlemény) found is the amendment of 27 Feb 2026; no later change was found. Phase 2 runs 14 Sep 14:00 to 30 Oct 2026 23:59 (Hungarian time, CET). The PDF link returned no response from the box on 23 Oct but is indexed; link instead to the programme page.
   Fix: title "Geotermikus fúrási kockázatok csökkentése (KEHOP-Plusz-4.2.4-25) – phase 2"; text "30 Oct 2026, 23:59 (Hungarian time)".

## SDE++ official title (GREEN, with an addition)
The official name is "**Stimulering Duurzame Energieproductie en Klimaattransitie (SDE++)**", round 2026. RVO https://www.rvo.nl/subsidies-financiering/sde/aanvragen confirms: start Tue 27 Oct 2026 09:00, end Thu 26 Nov 2026 17:00, budget EUR 8bn, phases ending 2/…/16/23/26 Nov 17:00. Suggested text: "SDE++ 2026 (Stimulering Duurzame Energieproductie en Klimaattransitie) – opens 27 Oct 09:00, closes 26 Nov 2026 17:00 CET (phased)".

## GREEN (deadline, time, buyer, country and link match; no change notice found)
- BOAMP 26-92772 St Pierre d'Eyraud: 26 Oct 12:00
- BOAMP 26-95465 ValDem: 5 Nov 12:00
- BOAMP 26-101091 Aussac-Vadalle: 6 Nov 12:00
- BOAMP 26-97695 Ferney: raw eForms gives 10 Nov 16:00+01:00 (the BOAMP field "15:00Z" is consistent)
- BOAMP 26-95181 Sauer-Pechelbronn: 24 Nov 12:00
- TED 643535 Zurich Langwiesen: 4 Nov 12:00
- TED 679859 Liner hanger: 6 Nov 10:00
- TED 684005 Wellhead: 9 Nov 10:00. The earlier 674260 (5 Nov) has been superseded, so the page is correct.
- TED 698651 Linnich: 9 Nov 12:00
- TED 691583 Wrocław DTS: 13 Nov 10:00
- TED 709263 Waldrach: 13 Nov 10:00
- TED 696202 UniGéo: 18 Nov 12:00
- TED 716179 Călimănești: 15:00+02:00 is correct EET in winter, i.e. 14:00 CET; the page is right.
- Explorationsinitiative Geothermie: 31 Oct 2026 cut-off (page loads, HTTP 200)
- IDF FEDER: 16 Nov 17:00 (PDF loads, HTTP 200)
- HORIZON-CL5-2026-11-D3-06: status Open, deadline 1 Dec 2026 per the portal JSON. The exact time is not in the JSON; Horizon calls normally close at 17:00 Brussels, but that was **not verified** for this topic.
- SDE++: see above

None of the 27 deadlines had passed as of 23 Oct 2026 14:00. SGU (25 Oct) and Szeged and St Pierre (26 Oct) expire within 3 days, so they should be removed or marked "closing" when the page goes live. Links: all TED and BOAMP IDs resolve via the API. TED web pages were not fetched (they return 202 to scripts).

## Scope vs title "Open deep-drilling tenders & funding calls"
- Shallow BHE fields: Aussac, Waldrach, Linnich, Winterthur/Zurich Langwiesen, plus St Pierre d'Eyraud, ValDem and the CZ BTES boreholes. These are drilling, but not deep drilling.
- Szeged is a heat purchase. Planning and engineering services are Prenzlau "Anlagentechnik", AFK Wärmenetz, UniGéo, CNRS, Ferney MOE, Grangegorman and Sauer-Pechelbronn.
- Strictly deep-drilling-relevant are only about 8: SGU, Ferney well, Prenzlau, SYNERGYS LLI x2, Wrocław DTS, Sauer-Pechelbronn wells, Călimănești, plus the funding calls.
- **Recommendation:** broaden the title rather than cut. Proposal: "**Open geothermal drilling & project tenders and funding calls**". Add a type filter with tags "Deep well", "Shallow BHE field", "Planning/engineering", "Heat supply".
- **Drop Szeged** (heat purchase, no supplier relevance, and it expires on 26 Oct anyway).
- Beauvaisis (absorption heat pumps) is also off-scope; tag it "Plant" or drop it.

## Count check
After the fixes there are 27 entries, minus Szeged and SGU once they have expired.

---
## Delta check (23 Oct), 14:20 Berlin (CEST)
Basis: the new tenders.json (25 entries, generated 14:13), index.html and the homepage, checked against TED API, BOAMP open data, RVO, energieforschung.de, the IDF PDF, CINEA and the F&T portal API.

**Verdict: GREEN with 4 small YELLOWs. No RED left. The page can be released once the yellow points are fixed.**

### Earlier fixes, all applied correctly ✅
- **670200 → 730837-2026:** 06 Nov 2026, 15:00 CET. Link and co-buyer are correct.
- **Pessac:** 30 Oct 2026, 12:00 CET, rectificatif 26-101172. ✅
- **KEHOP:** title, "30 Oct 2026, 23:59 (Hungarian time)" and the programme page link. ✅
- **SDE++:** official title; opens 27 Oct 09:00, closes 26 Nov 17:00 CET. ✅
- **SGU, CNRS and Grangegorman:** wording as recommended. Szeged and Beauvaisis are removed. ✅
- **Requests to participate:** Prenzlau and AFK carry the label. ✅
- **Homepage:** shows "25 open entries", matching the JSON (25) and the 25 cards. ✅
- **Impressum:** https://impressum.spudsignal.com redirects with 302 to https://spudsignal.beehiiv.com/p/legal-notice-impressum, which returns HTTP 200. ✅
- **Other entries:** none of the other deadlines, titles or links changed. No new change notices were found in TED (procedure check) or BOAMP (linked notices) since the first check.

### YELLOW (remaining)
1. **Accessed dates.** All 25 entries say `accessed: 2026-10-18`. That cannot be right for 730837 (published 22 Oct) or for the Pessac rectificatif (19 Oct).
   Fix: set accessed to 2026-10-23 for every entry re-checked today, i.e. all entries with checked = 2026-10-23.
2. **Pessac category.** It currently says "Other". See item (1) below.
3. **Explorationsinitiative and FEDER IDF.** Title and text need fixing. See items (2) and (3).
4. **Horizon.** The text "2026-12-01 (per portal; stage times on the topic page)" needs fixing. See item (4).
- Minor: the deadline_iso values for St Pierre, ValDem and Aussac have no time-zone offset, so the browser reads them in local time. Add `+01:00` for consistency.

### Open items, resolved against the original sources
1. **Pessac category.** BOAMP 26-93304 (raw notice) has 5 lots: "01 : Forages", "02 : Equipements", "03 : VRD", "04 : CVC-Pb / Elec", "05 : Gros Oeuvre". Lot 1 requires the Qualit'EnR "**Certification Forage Module Nappe**", which covers aquifer, i.e. open-loop, wells. The optional extra PSE 1 is acid injection.
   So this is a shallow aquifer well system (open loop) with a heat network, not BHEs and not deep geothermal. The depth is not stated in the notice (not verifiable).
   Fix: tag **"Shallow (aquifer wells)"**. If no new tag is wanted, use "Shallow BHE" with the note "open-loop aquifer wells".
2. **Explorationsinitiative.**
   - Official title: **Förderaufruf „Explorationsinitiative Geothermie“** (page title and H1 on energieforschung.de; updated 22 May 2026). It falls under the BMWE funding announcement of 25 Apr 2024 (8th Energy Research Programme).
   - Fix: title "Förderaufruf „Explorationsinitiative Geothermie“ (BMWE, 8. Energieforschungsprogramm)". Text: "Next submission cut-off: 31 Oct 2026 (project outlines via easy-Online; no time stated)".
3. **FEDER Île-de-France.** The official title per the PDF cover is: **"Appel à projets FEDER 2026 – Création ou extension des installations de distribution et production de chaleur et de froid par géothermie"**. Code: AAP_FEDER_géothermie_22062026_16112026. Programme: "Programme régional Île-de-France et bassin de la Seine FEDER-FSE+ 2021-2027".
   - The page currently says "installations de distribution…" and is missing "Création ou extension des".
   - Text: "16 Nov 2026, 17:00 (Paris time) – submission via e-Synergie". Source: PDF p.1, "Date limite de dépôt des candidatures : 16 novembre 2026", and the timetable "Lundi 16 novembre à 17h00 : clôture de l'appel à projets".
4. **Horizon HORIZON-CL5-2026-11-D3-06.** The F&T portal API (topicDetails and search API) gives only the date: 2026-12-01, single-stage, opening 4 Aug 2026.
   - The time comes from CINEA: "Deadline date: **1 December 2026, 17:00 (CET)**" (https://cinea.ec.europa.eu/funding-opportunities/calls-proposals/eur-1315-million-available-horizon-europe-energy-call_en). FFG gives the same: "01.12.2026, 17:00 Uhr".
   - Fix: "01 Dec 2026, 17:00 CET (Brussels time), single-stage". deadline_iso `2026-12-01T17:00:00+01:00`.

---
## App review (23 Oct), 15:10 Berlin (CEST)
Read-only review. Checked: deadlines.ics (feed), ics/*.ics (25 per-entry files), library/tenders/checks.json (_feed), overrides.json, tenders.json, index.html/JS, and the screenshots app-*.png. The feed was parsed with python icalendar 7.3.0.

**Verdict: YELLOW, 1 RED. Fix before go-live; the fixes are small.**

### RED
1. **Horizon entry has a future check date.** HORIZON-CL5-2026-11-D3-06 shows `checked`/`accessed` = **2026-10-25** in tenders.json and checks.json (eu_funding_pull.py → "last_checked": "2026-10-25"). The page card says "Accessed 25 Oct 2026". The .ics DESCRIPTION says "published … on 25 Oct 2026, last checked by SpudSignal on 25 Oct 2026". Today is 23 Oct, so this is a false claim.
   Fix: set it to 2026-10-23. Also find out why eu_funding_pull.py writes a future date (clock or timezone bug, or a hard-coded value).

### YELLOW
2. **DESCRIPTION has no real publication date.** "Deadline as published in <source> on 23 Oct 2026" gives the retrieval date, not the notice's publication date.
   Fix: "Published by source: <date> · Retrieved/last checked by SpudSignal: 23 Oct 2026". Dates verified so far:
   - TED (publication-date per API): 664748 28 Sep; 669195 29 Sep; 643535 18 Sep; 689259 7 Oct; 679859 2 Oct; 730837 22 Oct; 684005 5 Oct; 698651 9 Oct; 701161 12 Oct; 691583 7 Oct; 709263 14 Oct; 696202 8 Oct; 716179 16 Oct.
   - Rectificatif 26-101172: 19 Oct.
   - BOAMP initial notices: take dateparution from the API.
   - Programme pages: "page as of 23 Oct" instead of a publication date.
3. **"does NOT update itself".** Correctly present in all 25 single .ics files (the text is folded, but intact). In the feed, the wording "refreshed by SpudSignal on each weekly check…" is correct, since the feed does update. No change needed, just confirming.
4. **simap wording missing in the calendar.** simap only appears in index.html. The Zurich entry (TED 643535, Schulhaus Langwiesen) has no simap hint in its DESCRIPTION.
   Fix: add the same wording as on the page (e.g. "Swiss tender: binding documents and Q&A on simap.ch") to the Zurich .ics and the feed event.
5. **SEQUENCE.** It is 0 for all events, including the changed ones, Pessac (389f89…) and 670200/730837 (d46da9…). Formally acceptable, because the feed has never been published (first_seen 2026-10-23, so there is no older version on any client). But the generator must increment SEQUENCE and LAST-MODIFIED on any future change; please test that logic once with a dummy change.
6. **No STATUS:CANCELLED for Szeged and Beauvaisis.** Also acceptable, since they were never in a published feed. From go-live on, every entry that is removed or withdrawn must stay in the feed for at least 14 days as STATUS:CANCELLED with a reason, e.g. "Removed: off-scope" or "Withdrawn per notice X".
7. **Countdown for date-only deadlines.** inst() turns "2026-10-31" (Explorationsinitiative) into "2026-10-31T23:59:00" **in the browser's local time zone**, not in e.tz (Europe/Berlin). For readers outside CET the countdown is off by hours.
   Fix: compute it in e.tz, or set deadline_iso to "2026-10-31T23:59:00+01:00" and label it "(no time stated)".
8. **Alarms.** The VALARMs are -P7D and -P1D (ACTION:DISPLAY), consistent on all 25 events. That matches my spec (7d/1d), but the Chief of Staff wrote 7d/2d. Pick one and use the same wording on the page/About ("reminders 7 days and 1 day before").
9. **Header count.** "11 countries/EU" is ambiguous; it is actually 10 countries (SE, FR, DE, HU, CH, IE, CZ, PL, RO, NL) plus EU.
   Fix: "10 countries + EU".

### GREEN (checked and OK)
- **DTSTART and TZID.** All 25 match the verified deadlines.
  - SGU 20261025T230000 Europe/Stockholm (= 23:00 CET) ✅
  - CNRS 20261117T110000 Europe/Paris ✅
  - Grangegorman 20261105T140000 Europe/Dublin (= 14:00 Irish) ✅
  - 730837 20261106T150000 Prague ✅
  - Pessac 20261030T120000 Paris ✅
  - Călimănești 15:00 Europe/Bucharest (= 14:00 CET) ✅
  - KEHOP 23:59 Budapest ✅
  - SDE++ 17:00 Amsterdam ✅
  - Horizon 17:00 Brussels ✅
  - FEDER 17:00 Paris ✅
  - Explorationsinitiative is an all-day VALUE=DATE (no time stated) ✅
  - No UTC or floating errors. All post-25-Oct dates fall under STANDARD +0100 (Bucharest +0200, Dublin +0000).
- **VTIMEZONE.** One per TZID used (11), with DAYLIGHT/STANDARD and RRULE BYMONTH=3/10 BYDAY=-1SU. Transition times are correct: 02:00→03:00 and 03:00→02:00 local, Dublin 01:00/02:00, Bucharest 03:00/04:00.
- **RFC 5545.** CRLF only (923/923). Maximum line length 74 octets. VERSION:2.0, PRODID, CALSCALE, METHOD:PUBLISH, DTSTAMP on all 25. No unescaped , or ; in SUMMARY/DESCRIPTION. icalendar parses without errors. The 25 single files are identical to the feed in DTSTART and TZID; the only difference is that the single files carry no "[CHANGED]" prefix in SUMMARY, which is fine.
- **SUMMARY.** "[Check source] Deadline: <official title>". For participation entries: "[Check source] Requests to participate: …" ✅. KEHOP, FEDER, SDE++ and Explorationsinitiative carry the official titles.
- **DESCRIPTION.** Source + ID, last-checked date, "Only the original notice is binding: <link>", "No guarantee of completeness or accuracy", the time note on uncertain entries (SGU, CNRS, Grangegorman), plus URL ✅. The publication date is missing (see Yellow 2).
- **CHANGED.** Only Pessac and 670200 are flagged. Both are backed by corrections: Pessac by 26-101172 (19 Oct; old 26 Oct 13:00 → new 30 Oct 12:00), 670200 by 730837-2026 (22 Oct; old 30 Oct 15:00 → new 06 Nov 15:00). Each shows old → new and links the correction notice. The 14-day window is implemented in the JS (`<=14*DAY`). The Pessac rectificatif 26-94401 is listed in ack_rectif (lot information only) ✅.
- **Countdown.** Formatted with Intl in e.tz and shows the time zone, e.g. "23:00 CET (Europe/Stockholm)". Under 48 h the class .hot gives solid orange with white bold text, plus "Check the original – times may differ." From 7 days, a warn state. The screenshots confirm this ✅.
- **Delta-check yellows, all fixed.**
  - accessed/checked = 2026-10-23, except Horizon (see RED).
  - Pessac tag "Shallow (aquifer wells)".
  - Explorationsinitiative title "Förderaufruf „Explorationsinitiative Geothermie“" and text.
  - FEDER title "…Création ou extension des installations…", 17:00 Paris.
  - Horizon "01 Dec 2026, 17:00 CET (Brussels time)".
  - +01:00 on St Pierre, ValDem and Aussac.
- **overrides.json.** Consistent with my review: drops with reasons, time_note on the three uncertain entries, ack_rectif.

---
## Delta re-check (23 Oct, 2), 15:20 Berlin (CEST)
Read-only check. **Verdict: GREEN.** The RED from the app review is fixed. Two notes remain, neither blocking.

1. **No future dates.** None in accessed / last_checked / checked / fetched_at / first_seen / generated / DTSTAMP / LAST-MODIFIED across all json/html/ics, including checks.json and overrides.json. D3-06 is 23 Oct everywhere ✅
2. **DESCRIPTION.** All 25 events contain "Published by source: …" and "Last checked by SpudSignal: 23 Oct 2026" ✅. Spot checks against the TED API: 664748 = 28 Sep, 689259 = 07 Oct, 716179 = 16 Oct; 643535 = 18 Sep also matches ✅. Programme pages say "page as of 23 Oct 2026" ✅
3. **Explorationsinitiative.** DTSTART 20261031T235900, TZID Europe/Berlin, SEQUENCE 1. Note: "No time stated in the call – end of day (23:59 German time) assumed; submit earlier to be safe." ✅
4. **VALARMs.** All 25 events have -P7D and -P1D. About and the subscribe box say "7 days and 1 day before" ✅. The tenders header says "10 countries + EU" ✅. (The homepage hero says "17 countries + EU"; that is the whole Source Library, not the tenders page, so it is OK as long as it is meant that way.)
5. **Pessac old → new.** The static HTML has only an empty `<span class="chg" hidden>`. The line is filled by JS from the embedded JSON: change = 19 Oct, "26 Oct 2026, 13:00 CET → 30 Oct 2026, 12:00 CET …", link to rectificatif 26-101172. It shows within 14 days (the JS logic is correct). Same for 730837. ✅ with JS.
   - Note: without JS (noscript, crawlers) the line is missing. Optional: render it into the HTML statically.
6. **Feed.** icalendar re-parse OK, 25 VEVENTs. All 24 timed DTSTARTs are identical to the verified values from the app review. The only intended change is the Explorationsinitiative (VALUE=DATE → 23:59 Berlin) ✅
7. **simap.** There is still no simap hint on the Zurich card or in its .ics (7b5311…); simap appears only in Coverage and Licences.
   - Since the entry comes from TED (643535), the simap licence notice is not strictly required for it.
   - Recommended, optional: "Swiss tender – binding documents and Q&A on simap.ch". Not blocking.
