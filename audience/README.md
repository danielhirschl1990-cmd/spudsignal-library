# Audience categories

Status: rules and four historical examples reviewed GREEN at 00:57 CET on 8 November 2026. This file is the shared rule sheet for the newsletter editor and the Library. It does not authorise a live change or a Beehiiv send. Other Library items stay unclassified.

The newsletter itself lives outside this repository and has not been edited. `audience/newsletter-item.html` is a reusable excerpt. Use the same labels, on the same source, as `audience/assignments.json`.

## Exact public labels

- Drilling
- Equipment
- Engineering & Services
- Project owners & developers

Write the names in full. Do not shorten them to “Eng. & Services” or “Owners & developers”. A symbol or a colour may sit beside the name. It does not replace the name. On a narrow screen the full name wraps or the controls stack. They do not scroll sideways.

## What a tag means

A tag says who the item is directly relevant to. It is an orientation aid. It is not bidder eligibility, not the identity of the buyer, not a personalised feed, and not every possible later sale.

- **Drilling.** The item explicitly procures or reports drilling, well construction, completion or well intervention.
- **Equipment.** The item explicitly procures supply of identifiable equipment or components. Equipment that a drilling contractor merely uses does not add a second tag.
- **Engineering & Services.** The item explicitly procures or reports design, engineering, studies, testing or specialist services. Routine tests inside a drilling package do not add a second tag.
- **Project owners & developers.** Only a project-development instrument or decision, such as exploration or development rights, or funding whose stated applicants or beneficiaries are project owners or developers. A project update, an award notice, or a policy story does not qualify on its own.

Add a second tag only when that tag has its own explicit basis in the source. Record the basis and the original notice in `audience/assignments.json`. An integrated drilling package does not gain Equipment or Engineering & Services from casing or routine tests. Design, engineering, manufacture and delivery that are part of supplying a product do not add Engineering & Services or Drilling. A second tag needs a deliverable beyond that ordinary supply work. This is an editorial convention, not a legal procurement class. Leave an uncertain item untagged. Untagged does not mean irrelevant. Do not invent a tag to fill a filter, and do not assign tags by scanning titles for keywords.

Historical badge mockups are style references only. They are not approved mappings.

## Assignment record

`audience/assignments.json` is the only list of labels. The Library, the open-tender list, and the newsletter excerpt all read it. After an edit, run:

```bash
node audience/apply.mjs
```

The script checks the record before it writes. It refuses a keyword method, a second tag with no separate basis, an extra Equipment or Engineering & Services tag on an integrated drilling package, an extra Drilling or Engineering & Services tag on an equipment-supply package, and any FEDER label other than Project owners & developers.

`status` is one of:

- `reviewed` — checked against the original. `approved` is true, and each label has its own `bases` entry. The public badge is the full name only.
- `pending_review` — not used for the four historical examples.
- `untagged` — no audience badge. `labels` is empty.

## Reviewed historical examples

These four rows are the independently checked examples. The check was GREEN at 00:57 CET on 8 November 2026. They are historical items, not a new deadline briefing. Every other source stays unclassified.

| Item | Notice | Label | Basis |
| --- | --- | --- | --- |
| ECO Kutno wells GT-1 and GT-2 | [TED 725171-2026](https://ted.europa.eu/en/notice/-/detail/725171-2026) | Drilling | Drilling, casing, cementing and completion, with integral tests and site restoration. A thermal-water discharge tank in the same package does not add Equipment. |
| HVC heat-exchanger framework | [TED 726565-2026](https://ted.europa.eu/en/notice/-/detail/726565-2026) | Equipment | Supply in two portfolio lots, Westland and Slochteren, not a count of exactly two plants. Integral product engineering does not add Engineering & Services. |
| Energies du Grand Paris design and supervision framework | [TED 755201-2026](https://ted.europa.eu/en/notice/-/detail/755201-2026) | Engineering & Services | Conception and supervision. Later drilling or equipment is not tagged from this notice. |
| Île-de-France ERDF geothermal call | [FR-IDF-FEDER-geothermie-2026](https://www.europeidf.fr/sites/default/files/AAP_FEDER2026_G%C3%A9othermie.pdf) | Project owners & developers | PDF §2 (printed pages 5–6) and §3.1 (printed page 6) name the funded installations and the project proponents. The tag is not a statement that any particular reader is eligible. |

No reviewed multi-tag example is included. A layout sample with two names exists only in `audience/preview.html` and in the newsletter excerpt, and it is marked as not a source.

Every other Library source and open tender stays untagged. That is deliberate. Their scope was not reviewed into this record.

## Filters

The default is **All**. Every entry stays visible, including untagged entries.

On the open-tender list, the existing controls stay: type (Tenders / Funding calls), technical category (Deep well, Shallow BHE, Planning, Other), country, and the Closing soon view. Those technical categories are not audience tags.

Behaviour, covered by `audience/filter.test.mjs`:

- Inside the audience group, several selected labels match an entry that carries **any** of them (ANY / OR).
- Inside type, technical category and country, several selected values also match any of those values, as they did before.
- An entry must satisfy every group that has a selection (AND). Drilling plus Poland plus Other shows an entry only when it is Drilling and Poland and Other.
- Press a selected audience again to clear that one label. **All** in the audience row clears audience only. The **All** button above the audience row on the tender list clears type, technical category, country and audience.
- An untagged entry, including the ERDF call, remains visible under All and drops out when any audience label is selected.
- An entry with no audience label remains visible under All and drops out when any audience label is selected.

The selected state shows the word “Selected” and `aria-pressed="true"`. Colour is extra, not the only signal.

## Map

The map has no audience filters in this stage. Weekly map maintenance, project pins, BVG expansion, tender deduplication and auto-return are unchanged. Do not describe the newsletter, the Library and the map as one complete set of audience filters.

## Newsletter excerpt

The “For:” line in `audience/newsletter-item.html` uses the same labels as the Library. The words stay if images are blocked. The Library uses the original SVG files `symbols/aud-drilling.svg`, `symbols/aud-equipment.svg`, `symbols/aud-engineering.svg` and `symbols/aud-owners.svg`.

The template’s image addresses are root-relative (`/symbols/…`). They are for this site. They are not ready to paste into Beehiiv. At insertion, replace each `src` and `srcset` with the absolute public URL of that file, for example `https://library.spudsignal.com/symbols/aud-drilling.png` and `https://library.spudsignal.com/symbols/aud-drilling@2x.png`, once the file is on the public site. The Beehiiv newsletter has not been edited.

Do not start a segmented mailing from these tags. Do not present a pending label as a finished newsletter tag.

## Reviewer handoff

1. Check each row in `audience/assignments.json` against the original notice.
2. For the ERDF call, leave `labels` empty until the applicant or beneficiary wording is confirmed.
3. For Kutno, do not add Equipment or Engineering & Services unless a separate scope, outside the drilling package, is in the notice.
4. To publish a label, set `status` to `reviewed`, `approved` to true, and add a `bases` sentence for each label. Run `node audience/apply.mjs`.
5. Keep the Library and the newsletter on that same record.
