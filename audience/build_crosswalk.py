#!/usr/bin/env python3
"""Map pin crosswalk. Joins only on the exact source URL string.

Documented content identities from the 8 Nov 2026 review are recorded as notes.
They are not approved alternate map links.
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP_JS = ROOT / "map" / "data.js"
ASSIGN = ROOT / "audience" / "assignments.json"
OUT_JSON = ROOT / "audience" / "map-crosswalk-2026-11-08.json"
OUT_CSV = ROOT / "audience" / "map-crosswalk-2026-11-08.csv"
OUT_MD = ROOT / "audience" / "map-crosswalk-2026-11-08.md"

IDENTITIES = {
    "https://www.boamp.fr/pages/avis/?q=idweb:26-93304": (
        "Reviewer documented that correction notice 26-101172 (AUD-f59d58e6a09e, row 29) "
        "names this initial avis idWeb 26-93304 (AUD-8b3e581f8bbf, row 12). "
        "That is a content identity for those two records, not an approved alternate map link, "
        "and not a deadline clearance."
    ),
    "https://www.boamp.fr/pages/avis/?q=idweb:26-101172": (
        "Reviewer documented avisInitial/idWeb=26-93304 on this correction notice. "
        "That identity is not an approved alternate map link and not a deadline clearance. "
        "This row is joined only if a pin uses this exact URL."
    ),
    "https://www.palyazat.gov.hu/api/download/69a18cf18ea1644956cd37e1": (
        "Reviewer documented the same programme identifier KEHOP-Plusz-4.2.4-25 on this PDF "
        "(AUD-e54fb7f3ecf8, row 57) and the programme page (AUD-8f5807026097, row 58). "
        "That is not an approved alternate map link and not a statement about document version or current deadlines."
    ),
    "https://www.palyazat.gov.hu/programok/szechenyi-terv-plusz/kehop-plusz/kehop_plusz-4.2.4-25": (
        "Reviewer documented the same programme identifier KEHOP-Plusz-4.2.4-25 on this page "
        "and the KEHOP PDF. That is not an approved alternate map link and not a deadline clearance."
    ),
}

KALISZ_PIN = "https://radiopoznan.fm/informacje/pozostale/beda-wiercic-szukaja-wod-termalnych"
KALISZ_PGI = "https://www.pgi.gov.pl/geotermia/wm-aktualnosci/16917-kalisz-rozpoczyna-projekt-geotermalny-powstanie-otwor-badawczy"


def parse_js_object(text, name):
    key = "window." + name + "="
    start = text.index(key) + len(key)
    if text[start] != "{":
        raise SystemExit("expected object for " + name)
    depth = 0
    in_str = False
    esc = False
    for i in range(start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            continue
        if c == '"':
            in_str = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise SystemExit("unclosed " + name)


def assignment_fields(row):
    if not row:
        return {
            "assignment_reviewer_id": "",
            "assignment_row": "",
            "assignment_url": "",
            "assignment_status": "",
            "assignment_review_status": "",
            "tags": "",
            "withheld": "",
            "intentionally_untagged": "",
        }
    return {
        "assignment_reviewer_id": row["reviewer_id"],
        "assignment_row": row["reviewer_row"],
        "assignment_url": row["url"],
        "assignment_status": row["status"],
        "assignment_review_status": row["review_status"],
        "tags": " | ".join(row["labels"]),
        "withheld": "yes" if row.get("withheld") else "",
        "intentionally_untagged": "yes" if row.get("intentionally_untagged") else "",
    }


def main():
    text = MAP_JS.read_text()
    data = parse_js_object(text, "SS_DATA")
    extra = parse_js_object(text, "SS_EXTRA")
    assignments = json.loads(ASSIGN.read_text())["assignments"]
    by_url = {row["url"]: row for row in assignments}
    if len(by_url) != len(assignments):
        raise SystemExit("duplicate assignment urls")

    pins = []
    for index, feature in enumerate(data["features"], start=1):
        props = feature["properties"]
        url = props.get("source_url") or ""
        row = by_url.get(url)
        if row:
            basis = "exact_url"
            reason = ""
        else:
            basis = "unlinked"
            if url == KALISZ_PIN:
                reason = (
                    "No assignment uses this Radio Poznań URL. "
                    "The PGI Kalisz record AUD-a34b4517197f is a different URL, was not readable, "
                    "and stays untagged. The town name was not used as a match."
                )
            else:
                reason = "No assignment record uses this exact source URL. Title and place name were not used as a match."
        item = {
            "record_kind": "pin",
            "feature_index": index,
            "pin_id": props.get("id") or "",
            "type": props.get("type") or "",
            "title": props.get("title") or "",
            "country": props.get("country") or "",
            "source_url": url,
            "issue": props.get("issue") or "",
            "issue_url": props.get("issue_url") or "",
            "matching_basis": basis,
            "unlinked_reason": reason,
            "alternate_link_note": IDENTITIES.get(url, ""),
            "alternate_link_approved": "no",
        }
        item.update(assignment_fields(row))
        pins.append(item)

    nationwide = []
    for index, props in enumerate(extra.get("nationwide") or [], start=1):
        url = props.get("source_url") or ""
        row = by_url.get(url)
        item = {
            "record_kind": "nationwide",
            "feature_index": index,
            "pin_id": props.get("id") or "",
            "type": props.get("type") or "",
            "title": props.get("title") or "",
            "country": props.get("country") or "",
            "source_url": url,
            "issue": props.get("issue") or "",
            "issue_url": props.get("issue_url") or "",
            "stored_deadline": props.get("deadline") or "",
            "stored_deadline_note": "Stored map text only. Not revalidated and not an eligibility statement.",
            "matching_basis": "exact_url" if row else "unlinked",
            "unlinked_reason": "" if row else "No assignment record uses this exact source URL.",
            "alternate_link_note": IDENTITIES.get(url, ""),
            "alternate_link_approved": "no",
        }
        item.update(assignment_fields(row))
        nationwide.append(item)

    pin_urls = {item["source_url"] for item in pins}
    nw_urls = {item["source_url"] for item in nationwide}
    orphans = []
    for row in assignments:
        if row["url"] in pin_urls or row["url"] in nw_urls:
            continue
        note = IDENTITIES.get(row["url"], "")
        if row["url"].startswith(KALISZ_PGI):
            note = (
                "This PGI URL is not a map pin. The map pin uses a Radio Poznań URL and is listed separately as unlinked. "
                "Same town name is not a link. The reviewer left this record untagged because the source was not readable."
            )
        orphans.append({
            "record_kind": "assignment_without_map_pin",
            "feature_index": "",
            "pin_id": "",
            "type": "",
            "title": row.get("library_title") or "",
            "country": "",
            "source_url": "",
            "issue": "",
            "issue_url": "",
            "matching_basis": "not_a_pin",
            "unlinked_reason": "This assignment URL is not the source URL of any map pin or nationwide row.",
            "alternate_link_note": note,
            "alternate_link_approved": "no",
            **assignment_fields(row),
        })

    exact = sum(1 for item in pins if item["matching_basis"] == "exact_url")
    unlinked = sum(1 for item in pins if item["matching_basis"] == "unlinked")
    doc = {
        "schema": "spudsignal.map.audience.crosswalk.v1",
        "generated": "2026-11-08",
        "method": (
            "Each map feature in map/data.js and each nationwide row in SS_EXTRA is listed. "
            "A link exists only when the pin source URL is character-for-character the assignment URL. "
            "No shortened title, place name, or alternate URL was treated as a match. "
            "Reviewer notes on the Pessac initial avis and the KEHOP programme identifier are recorded and are not approved map joins."
        ),
        "reviewer": "Independent full audit, 8 November 2026, 01:22 CET. Assignments were reconciled by those exact URLs.",
        "counts": {
            "pins": len(pins),
            "pins_exact_url": exact,
            "pins_unlinked": unlinked,
            "nationwide_rows": len(nationwide),
            "nationwide_exact_url": sum(1 for item in nationwide if item["matching_basis"] == "exact_url"),
            "assignments_without_map_pin": len(orphans),
            "assignments": len(assignments),
        },
        "documented_identities_not_approved_as_map_joins": [
            {
                "pair": "Pessac row 29 to row 12",
                "urls": [
                    "https://www.boamp.fr/pages/avis/?q=idweb:26-101172",
                    "https://www.boamp.fr/pages/avis/?q=idweb:26-93304",
                ],
                "reviewer_note": "Correction notice cites initial avis idWeb 26-93304. Not a blanket alternate map approval and not a deadline clearance.",
                "applied_to_map": False,
            },
            {
                "pair": "KEHOP row 58 and row 57",
                "urls": [
                    "https://www.palyazat.gov.hu/programok/szechenyi-terv-plusz/kehop-plusz/kehop_plusz-4.2.4-25",
                    "https://www.palyazat.gov.hu/api/download/69a18cf18ea1644956cd37e1",
                ],
                "reviewer_note": "Same programme identifier KEHOP-Plusz-4.2.4-25. Not a blanket alternate map approval and not a deadline clearance.",
                "applied_to_map": False,
            },
        ],
        "pins": pins,
        "nationwide_not_pins": nationwide,
        "assignments_without_map_pin": orphans,
    }
    OUT_JSON.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

    columns = [
        "record_kind", "feature_index", "pin_id", "type", "title", "country",
        "source_url", "issue", "issue_url", "matching_basis", "unlinked_reason",
        "assignment_reviewer_id", "assignment_row", "assignment_url",
        "assignment_status", "assignment_review_status", "tags",
        "withheld", "intentionally_untagged", "alternate_link_note", "alternate_link_approved",
        "stored_deadline", "stored_deadline_note",
    ]
    with OUT_CSV.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for item in pins + nationwide + orphans:
            writer.writerow(item)

    lines = [
        "# Map audience crosswalk, 8 November 2026",
        "",
        "Joins use the exact source URL only. Place names and shortened titles were not used.",
        "Pessac initial-avis identity and the KEHOP programme identifier are noted below and are not approved alternate map links.",
        "",
        f"Pins: {len(pins)}. Exact URL: {exact}. Unlinked: {unlinked}.",
        f"Nationwide rows that are not pins: {len(nationwide)}.",
        f"Assignment records with no map pin: {len(orphans)}.",
        "",
        "## Pins",
        "",
    ]
    for item in pins:
        tags = item["tags"] or "(no tags)"
        lines.append(f"### {item['feature_index']}. {item['type']} · {item['pin_id']}")
        lines.append("")
        lines.append(f"- Title: {item['title']}")
        lines.append(f"- Source URL: {item['source_url']}")
        if item["issue_url"]:
            lines.append(f"- Issue URL: {item['issue_url']}")
        lines.append(f"- Match: {item['matching_basis']}")
        if item["assignment_reviewer_id"]:
            lines.append(
                f"- Assignment: {item['assignment_reviewer_id']} row {item['assignment_row']} · {item['assignment_status']} · {tags}"
            )
            lines.append(f"- Assignment URL: {item['assignment_url']}")
        if item["unlinked_reason"]:
            lines.append(f"- Unlinked: {item['unlinked_reason']}")
        if item["alternate_link_note"]:
            lines.append(f"- Not an approved alternate: {item['alternate_link_note']}")
        lines.append("")
    lines.append("## Nationwide rows (not pins)")
    lines.append("")
    for item in nationwide:
        tags = item["tags"] or "(no tags)"
        lines.append(f"### N{item['feature_index']}. {item['pin_id']}")
        lines.append("")
        lines.append(f"- Title: {item['title']}")
        lines.append(f"- Source URL: {item['source_url']}")
        lines.append(f"- Stored deadline text: {item['stored_deadline']} ({item['stored_deadline_note']})")
        lines.append(f"- Match: {item['matching_basis']}")
        lines.append(
            f"- Assignment: {item['assignment_reviewer_id']} row {item['assignment_row']} · {item['assignment_status']} · {tags}"
        )
        lines.append("")
    lines.append("## Documented identities that are not map joins")
    lines.append("")
    lines.append("- Pessac: row 29 cites initial avis 26-93304 (row 12). Neither URL is a map pin in this data file. Not approved as an alternate map link.")
    lines.append("- KEHOP: programme page row 58 and PDF row 57 share programme id KEHOP-Plusz-4.2.4-25. Neither URL is a map pin. Not a deadline clearance.")
    lines.append("- Kalisz: the map pin is the Radio Poznań URL and is unlinked. The PGI record stays untagged. The town name was not used.")
    lines.append("")
    OUT_MD.write_text("\n".join(lines))
    print(json.dumps(doc["counts"]))


if __name__ == "__main__":
    main()
