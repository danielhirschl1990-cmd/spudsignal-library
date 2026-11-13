# Glossar-Slots v2 – Begriffe, Varianten, Fundstellen, angewandter Begriff

Stand 13 Nov 2026. Quelle der Regeln: `glossar.md` (sha ad93fa22…, read-only). Basis live `368155e`.
„Angewandt“ = so steht es im Prototyp v2 (`prototype/`). `[EDITOR]` steht **nur in dieser Datei** (Wunsch-Slots für spätere Texte); im Prototyp 0 Treffer (grep).

| # | Sache | Live-Varianten (Fundstelle) | Angewandt im Prototyp | Log-ID | Slot |
|---|---|---|---|---|---|
| 1 | Listenzeile | „primary sources“ (Home-Zähler, Meta), „sources shown“ (Home-Zähler), „listings“ (Tenders-Footer), „items“ (Audience-Texte) | **entry / entries** (Kopf „64 current entries (38 expired hidden · show)“, ohne JS „102 entries“; „X of 102 entries shown“) | G-entry, H-count | – |
| 2 | Original | „original notice“ (Tenders), „original document(s)“ (Home-Footer, Meta), „original publishers“ (Footer), „the originals“ (Home-Intro) | **original source** nur in Intro, T01 und CPV-Hinweis. **Ausnahme Haftung/Disclaimer:** Live-Wortlaut bleibt („notice“; Footer = H05 aus live /projects/ „… original publishers … original document is authoritative.“) | G-source, H05-liab | – |
| 3 | Punkt auf der Karte | „pin“, „item“, „point“ | **pin** (nur auf der Karte) | G-pin | – |
| 4 | Filter zurücksetzen | sichtbar „All“ + title „Clear all filters“ (Tenders), „Clear filters“ (Karte), keine (Home) | **Clear filters** = sichtbares Label, `title`, `aria-label`; „All“ nur als erster Chip einer Gruppe | G-reset (S-08) | S-08 |
| 5 | Audience-Satz | 3+ Fassungen (Home `aud-help`, Tenders Panel + F2 + About this app, Karte `audnote`) | überall: „Audience labels are guidance, not eligibility. Check the original source for requirements and deadlines.“ | G-aud | – |
| 6 | Leerer Audience-Filter | „stay visible under All“ (Tenders), „are hidden while a label is selected. Choose All to see them.“ (Karte) | „… stay in All.“ | G-all, G-pin | – |
| 7 | Typ Förderung | „Funding“ (Home-Badge), „Funding call“ (Tenders-Badge, Karten-Layer) | unverändert; **Entscheidung A offen** | – | [EDITOR] A |
| 8 | Produktname | „SpudSignal Library“, „Source Library“, „SpudSignal Source Library“, „Home“ | Marke „SpudSignal Library“, H1 „Source Library“, Tenders-Kicker „SpudSignal Source Library“ (live); nur der **Tab** heißt „Library“ statt „Home“. **Entscheidung B offen** | H-rename | [EDITOR] B |
| 9 | Home-Meta / Intro | Meta „Open … 102 primary sources …“, Intro „The primary documents … funding calls …“ | live-Wortlaut unverändert. **Entscheidung C offen** | – | [EDITOR] C |
| 10 | Legende Projekt | „Project / news“ (Karte) vs. „Project“ (Library) | „Project / news“ (live). **Entscheidung D offen** | – | [EDITOR] D |
| 11 | Haftungssatz (Footer) | Home/Projects: H05 „All documents … original publishers … original document is authoritative.“; Tenders: „Liability: listings … original notice is authoritative.“ | **H05 wortgleich aus live /projects/ (approved) auf allen 5 Seiten**; Abgleich mit Reviewer v2: identisch | H05-liab, S-footer | [EDITOR] E / P-F1 (nicht benutzt) |
| 12 | Zähler Karte vs. Tenders | Karte 20 + 1 + 2 nationwide, Tenders 23 | unverändert. **Entscheidung F offen** (optionaler Hinweis) | – | [EDITOR] F |
| 13 | Datum | „01 Dec 2026“ (Tenders, 5 Fristen + JS `2-digit`) | „1 Dec 2026“; JS `day:"numeric"`. JSON-Datenblock unverändert | G-date | – |
| 14 | Kalender | „One-off file · no updates“ | Option A: live; Option B: „One-off file“ neben dem Button (Reviewer: kürzer erlaubt) | T-optB | – |
| 15 | Ländernamen | Flagge+Name (Home), Name (Tenders), ISO (Karte) | Name ohne Flagge überall (Karte: ISO als `title`) | G-country, M-country | – |

## Grep-Ergebnis im Prototyp (sichtbarer Text, außerhalb des Tenders-JSON-Blocks)
| Muster | Treffer | Bewertung |
|---|---|---|
| `[EDITOR` | 0 | ok (Reviewer-Bedingung) |
| `original notice` | 5 | Tenders: Meta (C) + Warnzeile, F1, About this app, Zeit-Warnung, gespeicherte Einträge (Haftung/Disclaimer = Live-Wortlaut) |
| `primary source` / `original document` | 3 / 3 | nur Home-Meta/og/twitter (Entscheidung C) |
| `original document` / `original publishers` im Footer | je 1 pro Seite | H05-Satz (approved) |
| `Clear all filters`, `listings`, `assignment record`, `open-tender list`, `stay visible under All`, `Projects & wells (#1` | 0 | ok |
| führende Null `0D Mon YYYY` | 0 außerhalb JSON | ok (JSON byte-identisch, Absicht) |
| `Source Library` | Home 4, Tenders 2 | Entscheidung B (live behalten) |
| `Project / news` | Karte 1 | Entscheidung D |
| `Funding call` | Tenders 4, Karte 1 | Entscheidung A (echte Calls) |

## [EDITOR]-Slots (nur hier)
- [EDITOR] A – Typ-Label Funding vs. Funding call bestätigen.
- [EDITOR] B – Produktname/H1 („Library“ vs. „Source Library“).
- [EDITOR] C – Home-Meta und Intro ohne „Open … funding calls“.
- [EDITOR] D – Legende „Project / news“ → „Project“?
- [EDITOR] E – /projects/-Haftungssatz (P-F1, wartet auf H05).
- [EDITOR] F – Hinweis zur Zähloptik Karte vs. Tenders.
- G – Label des Betriebsanlagen-Schalters „Operating plants (28)“: kommt im eigenen Delta des Kartografen, kein Editor-Slot mehr.
