# Map – Darstellungsänderungen im Tabs-Prototyp v2 (zur Bestätigung durch den Kartografen)

Stand 13 Nov 2026, Basis live `368155e` (inkl. Hotfix PR #7). Prototyp: `prototype/map/index.html` (+ `/assets/spudsignal.css`, `/assets/ss-url.js`).
**Nur Darstellung.** `data.js`, `testlayers.js`, Pin-Daten, Popups-Inhalte, Zählungen: byte-identisch zu live (cmp geprüft). Nichts live, kein Merge.
Log-IDs = Einträge in `work/v2/changelog-v2.json`.

| # | Log-ID | Vorher (live) | Nachher (Prototyp) | Bitte bestätigen |
|---|---|---|---|---|
| 1 | CSS-font | DejaVu-Stack lokal; Leaflet-Controls/Popups „Helvetica Neue“, Arial (`font-family:inherit` von `.leaflet-container`); Zoom ± Lucida Console | Ein Stack für Seite, Popups und Zoom-Buttons (`/assets/spudsignal.css` §1). Popup gemessen: `"DejaVu Sans", Verdana, system-ui` | Popup-Lesbarkeit OK? |
| 2 | M-title / M-head | Kein H1 | H1 „Geothermal map: projects, tenders & funding“ (= live `<title>` ohne Suffix). Desktop: Kopfzeile über der Karte; mobil im Panel, Desktop-Panel sr-only | Höhe der Kopfzeile (~80 px) OK? |
| 3 | M-notice | Tell-us-Hinweis und Desktop-CTA in der Legende | Tell-us + CTA in der Kopfzeile (Desktop). Mobil: Tell-us als Karte unten über der Attribution, CTA-Leiste oben (live-Element `#ctabar`). Text unverändert, nichts gelöscht | – |
| 4 | M-legend / M-legend2 | Legende offen, mit Notice/CTA, Zeilen einzeln | Legende **eingeklappt** („Legend ▸“, 44 px), unten rechts; Typ-Zeilen Tender/Project / news/Funding in einer Zeile; „Active project / operating plant, approx. location (dashed outline)“ → Symbole + „approx. location (dashed outline)“ | Kürzung der Approx-Zeile OK? |
| 5 | M-panel | Panel: Filter, Liste, Disclaimer, Credits, Audience-Mechanik | Panel: Filter + Ergebnisliste. **B1 bleibt sichtbar:** „Locations are approximate unless noted. No coordinate table is offered, and nothing can be downloaded or exported.“ Dahinter `details#map-info` „Info“ (Disclaimer, Audience-Mechanik) und `details#about-sources` „Sources & credits“ (LfU, MaStR, TED, OSM-Koordinaten-Credit, unverändert) | Reviewer-Regel erfüllt; Reihenfolge OK? |
| 6 | M-dis | „Tender data as published by source, no guarantee – check the original.“ | „Tender data as published by source, no guarantee – check the original. Pins marked “approx.” do not show the exact location.“ (erster Satz = live-Disclaimer, unverändert) (**Kartograf-Korrektur 13 Nov, umgesetzt**; kein Glossar-Eingriff in Disclaimer) | erledigt |
| 7 | M-attrib | Attribution-Link „About & Sources“ | Link-Text „Sources & credits“, öffnet `#about-sources`. **OSM-Attribution bleibt sichtbar in der Ecke** | – |
| 8 | M-pab / S-footer | Linkzeile About & Sources · Impressum · Privacy (seit Hotfix `#about-data`) | Voller gemeinsamer Footer im Panel (Medieninhaber, Haftung, Impressum, Privacy, About & Sources, What’s new, Subscribe) | – |
| 9 | M-start / M-start2 / M-start3 | Start `setView([49,10],4)`, fitBounds nur mobil | Start-Rahmung Europa: `fitBounds` über alle Pins auf allen Viewports, Padding 24, maxZoom 5, `zoomSnap 0.25`, Startzoom 3.75. Island bis Türkei im Bild | Rahmung OK? |
| 10 | M-label | „Projects & wells (#1–#7)“ | „Projects & wells“ | Ausgaben-Nummern woanders nötig? |
| 11 | M-country / CSS-chip | ISO-Codes (AT, CH …) als 12-px-Pills | Ländernamen (Austria, Czechia, United Kingdom, Türkiye …), ISO als `title`; gemeinsamer `.ss-chip`; Single-Select wie live | Namensliste `CN` prüfen |
| 12 | G-aud / G-pin / G-all | Eigener Audience-Satz; Leertext „Pins without a label are hidden while a label is selected. Choose All to see them.“ | Ein Audience-Satz überall; „Pins without a label stay in All.“; „Calls without a label stay in All.“. „This is not a finding that no projects exist.“ bleibt | – |
| 13 | U-params | Filter nicht in der URL | `?aud=` und `?country=` werden gelesen/geschrieben (replaceState), Tab-Links tragen sie weiter. Ohne JS: Karte wie live (keine Filter) | – |
| 14 | §12 Tap targets | Typ-Checkboxen 26 px, „All“ 43 px, ☰ Filters 36 px, CTA 28 px, „Project list“ 13 px | alle ≥ 44 px (Ausnahme: Inline-Link „Sources & credits“ in der Attributionszeile, WCAG-Inline-Ausnahme) | Panel wird dadurch etwas länger |
| 15 | M-optB / M-optB2 | – | **Nur Option B, nur per `?pins=b`:** ein Symbol je Typ (Hexagon voll, kein Ring, kein Grau „paused“, keine Strichelung „approx“); Status nur im Popup. **Kollidiert mit Daniels Entscheidung 31 Oct** (3 Stufen per Füllung, grau „paused“ nach 18 Monaten, gelb „Status open – not verified“) → Daniel-Entscheidung, Default bleibt A | Kartograf: Meinung zu B |

## Nicht geändert
Pins, Cluster, Farben/Kodierung (Option A = live), Popups (Quelle, Approx-Hinweis, „Status open – not verified“ bleiben in jedem Popup), Zählungen, Layer-Schalter, kein Download/Export.

## Follow-ups für den Kartografen (nicht im Paket)
- **27 vs 28:** Schalter „Operating plants (27)“ zählt Pins; es sind 28 Anlagen (OP07/OP08 Unterföhring I+II auf einem Pin). Das Label „Operating plants (28)“ kommt im eigenen Delta des Kartografen; der Prototyp ändert es nicht.
- `/map/data.geojson` (8 Nov, nicht verlinkt) liegt noch im Deploy. Das ist eine eigene Daniel-Entscheidung, nicht Teil des Tabs-Pakets (siehe Proposal 7a). Der Prototyp übernimmt die Datei unverändert.
- OSM-Kacheln: hellere Rechtecke in Screenshots bei Zoom 3.75 kommen vom Kachelserver (gleiche Kacheln, die Leaflet beim Zoomwechsel abbricht und neu lädt), kein Layoutfehler.
- „Project / news“ (Entscheidung D) bleibt live-Wortlaut.
- „Funding calls (1)“ + 2 „Nationwide / EU calls“ + 20 Tender = 23 wie auf Tenders (Entscheidung F, optionaler Hinweis).
