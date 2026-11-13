# Text slots: Editor texts (Library Tabs 2.0, 13 Nov 2026, ~23:25 CET)

Basis: `text-slots.md` (35c5227c), `versioning-editor-2026-11-13.md`, live pages /, /tenders/, /map/, /projects/ (read only, 13 Nov ~23:20 CET). English, date format "8 Nov 2026". Not live.

| ID | Text (final proposal) | Chars | Note |
|---|---|---|---|
| P-F1 | Liability: entries are provided for information only, without guarantee of completeness or accuracy; the original source is authoritative. | 138 | Modelled on T21 (Tenders) and the Reviewer's H05 proposal; "source" instead of "notice" because the project list cites operator, MaStR and TED sources. **Same open decision as H05 (Daniel/Reviewer); do not use before that.** Media owner line stays visible above it. |
| W-01 | New features and layout changes, newest first. Each feature release gets an update number. | 90 | |
| W-02 | Weekly data updates (new entries, expired deadlines, re-checks) get no number. See "last updated" on each page. | 111 | |
| W-10 | Update 1.0 · before 8 Nov 2026 – "The starting point: the Library, the Tenders page and the map as they were before 8 Nov 2026." | 92 | Optional, more concrete (only if the Git dates match the public go-live dates; the Library date 18 Oct matches my notes, the rest I can't confirm): "The starting point: Library (since 18 Oct), Tenders (since 23 Oct) and map (since 29 Oct 2026)." |
| W-20 | Head: "Update 2.0 · {go-live date}". Text: "New: one tab bar for Library, Tenders and Map on every page, on desktop and mobile." | 83 | No "one page", because the URLs stay separate. The date is set only at go-live. |
| S-08 | Visible: "Clear filters" (title/aria the same). | 13 | Decision: the global reset chip says "Clear filters", the same as the map. "All" stays only as the first chip inside a filter group (e.g. Audience), as it is live today. |

## Decision on 1.2 + 1.3: merge

Same evening, two releases; for readers one entry is clearer and keeps the numbers low. W-13 is dropped; W-12 becomes:

**Update 1.2 · 13 Nov 2026**
- New on the map for Bavaria: an Active projects layer (15 projects) and a switchable Operating plants layer (28 plants). Each new pin links to a public source. (158 chars)
- Also new: a slimmer Tenders page on mobile. Key facts stay on each card; the rest sits under "Details" and "About this data". (124 chars)

**Count updated (Reviewer, 13 Nov):** 28 plants on 27 pins (OP07/OP08 Unterföhring I+II share one pin), so "28 plants" is correct.

## Check of the existing entries
- W-11 (1.1 · 8 Nov 2026): "New: audience filters. Filter the Library, open tenders and the map by Drilling, Equipment, Engineering & Services, or Project owners & developers." (147 chars; "open tenders" added at the Reviewer's request) Matches the map note of 8 Nov (PRs #1–#4) and the four standard names. OK.
- 15 active projects: /projects/ live shows "Active projects (15)". OK.
- Slim Tenders: live since 13 Nov (PR #6, per the Designer/CoS); the CoS confirms it is the approved state.
