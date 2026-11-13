#!/usr/bin/env python3
"""Build the audience audit and merge proposed rows into assignments.json.

Reviewed rows already in assignments.json are kept. New labels are pending_review.
Unclassified rows are recorded in the audit and are not given a public label.
"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = json.loads(Path("/tmp/lib-entries.json").read_text())
TED = {r["id"]: r for r in json.loads(Path("/tmp/ted-desc.json").read_text())}
ASSIGN_PATH = ROOT / "audience" / "assignments.json"

def ted_id(url):
    m = re.search(r"detail/(\d{6}-2026)", url or "")
    return m.group(1) if m else None

def excerpt_for(url):
    i = ted_id(url)
    if not i or i not in TED:
        return "", "not_fetched"
    r = TED[i]
    text = (r.get("lot") or r.get("proc") or "").strip()
    if not text or text in {"-", "Befindet sich derzeit in Bearbeitung."}:
        return text, "ted_api_empty"
    return text[:700], "ted_api_2026-11-08"

# url -> proposal. labels None means unclassified.
# Only explicit scope. pending_review, never approved.
P = {}

def add(url, labels, rationale, uncertainty="", integrated=False, supply=False, bases=None, excluded=None, title=None):
    P[url] = {
        "labels": labels,
        "rationale": rationale,
        "uncertainty": uncertainty,
        "integrated_package": integrated,
        "supply_package": supply,
        "bases": bases or {},
        "excluded": excluded or [],
        "title": title,
    }

# --- TED, fetched 8 Nov 2026 ---
add("https://ted.europa.eu/en/notice/-/detail/620241-2026", ["Engineering & Services"],
    "The notice is a contract to carry out gravimetric and magnetotelluric measurements.",
    bases={"Engineering & Services": "TED description: carrying out gravimetric and magnetotelluric measurements in the Brabant Massif as part of geological exploration."})
add("https://ted.europa.eu/en/notice/-/detail/637856-2026", ["Drilling"],
    "The notice procures drilling services with a rig and crew. Ancillary equipment stays inside that package.",
    integrated=True,
    bases={"Drilling": "TED description: provision of drilling services, including the provision and operation of a drilling rig, ancillary equipment, qualified drilling crew and related services for the SYNERGYS deep geothermal drilling."},
    excluded=[{"label": "Equipment", "reason": "Ancillary equipment is named as part of the drilling service, not as a separate supply."}])
add("https://ted.europa.eu/en/notice/-/detail/638913-2026", ["Equipment"],
    "The notice is the supply of pre-insulated bonded steel pipe for a geothermal heating main.",
    bases={"Equipment": "TED description: DN500/DN400 pre-insulated bonded steel pipes for the main geothermal heating pipeline, length about 8.5 km."})
add("https://ted.europa.eu/en/notice/-/detail/643535-2026", ["Drilling"],
    "The notice is 40 borehole heat exchangers of 135 m. Two heat pumps are named in the same works description and are not split out as a supply lot.",
    integrated=True,
    bases={"Drilling": "TED description: 40 Erdwärmesonden à 135 m, together with two brine/water heat pumps, for the Langwiesen school."},
    excluded=[{"label": "Equipment", "reason": "The heat pumps are named inside the same borehole-works description, not as a separate supply contract."}],
    uncertainty="The heat pumps are in the same sentence. A reviewer may still see a separate equipment scope.")
add("https://ted.europa.eu/en/notice/-/detail/649322-2026", ["Engineering & Services"],
    "The notice procures hydrogeological supervision for three production and two injection wells.",
    bases={"Engineering & Services": "TED description: hydrogeological expert, supervision and administrative services to monitor three pumping wells and two injection wells in Kranj."})
add("https://ted.europa.eu/en/notice/-/detail/649808-2026", ["Engineering & Services"],
    "The notice procures wireline-logging services for two deep wells.",
    bases={"Engineering & Services": "TED description: provision of wireline logging services for two deep geothermal wells near Wörth am Rhein."})
add("https://ted.europa.eu/en/notice/-/detail/652643-2026", ["Drilling", "Engineering & Services"],
    "The framework splits core drilling and groundwater wells from a separate borehole-logging lot.",
    bases={
        "Drilling": "TED description: framework lots for core drilling (Delområde 1) and groundwater wells (Delområde 2).",
        "Engineering & Services": "TED description: a separate lot, Delområde 3, for borehole logging.",
    })
add("https://ted.europa.eu/en/notice/-/detail/660910-2026", ["Drilling"],
    "The notice is drilling a new thermal well of about 1,000 m at Zsóry spa.",
    bases={"Drilling": "TED description: a new 1,000 m thermal well (VIII-as kút) for the Mezőkövesd Zsóry spa."})
add("https://ted.europa.eu/en/notice/-/detail/664782-2026", ["Drilling"],
    "The notice expressly includes drilling a new thermal well. The heat centre and network are surface works and are not a second audience label.",
    bases={"Drilling": "TED description: new thermal well by drilling at the Kaba spa, together with a 300 kW heat block and a heat network."},
    uncertainty="The same notice also builds a heat centre and network. Those works are not given a second label.")
add("https://ted.europa.eu/en/notice/-/detail/669195-2026", ["Equipment"],
    "The lots are supply and installation of heat pumps and thermal-water plant equipment. Installation is part of that supply.",
    supply=True,
    bases={"Equipment": "TED lot text: delivery and installation of heat pumps of about 4.4 MW, and thermal-water equipment including filters, a plate heat exchanger and an injection pump."},
    excluded=[{"label": "Engineering & Services", "reason": "Installation is described with the equipment supply, not as a separate design contract."}])
add("https://ted.europa.eu/en/notice/-/detail/670200-2026", ["Drilling"],
    "The notice is execution of 100 shallow geothermal boreholes, plus an optional 30.",
    bases={"Drilling": "TED description: realisation of shallow geothermal boreholes at Litoměřice, 100 boreholes of 100 m, with an option for 30 more."})
add("https://ted.europa.eu/en/notice/-/detail/674260-2026", ["Equipment"],
    "The notice is supply of wellhead and frac-tree systems. Installation is part of that supply.",
    supply=True,
    bases={"Equipment": "TED description: supply of long-lead wellhead and frac-tree systems, with rental of installation tools and installation services, for SYNERGYS."},
    excluded=[{"label": "Engineering & Services", "reason": "Installation is the ordinary work of supplying the wellhead, not a separate engineering contract."}])
add("https://ted.europa.eu/en/notice/-/detail/679859-2026", ["Equipment"],
    "The notice is supply of liner-hanger systems, with running tools and installation.",
    supply=True,
    bases={"Equipment": "TED description: supply of liner-hanger systems, with rental of running and installation tools and installation services, for SYNERGYS."},
    excluded=[{"label": "Engineering & Services", "reason": "Installation is part of supplying the liner hanger."}])
add("https://ted.europa.eu/en/notice/-/detail/681445-2026", ["Engineering & Services"],
    "The notice procures general planning (HOAI phases) for a hydrothermal doublet, not the drilling contract itself.",
    bases={"Engineering & Services": "TED description: general planning of a hydrothermal doublet, HOAI phases 2–4 for the subsurface and 1–4 for the surface plant."},
    excluded=[{"label": "Drilling", "reason": "The new reinjection well is the subject of the planning, not a drilling contract in this notice."}])
add("https://ted.europa.eu/en/notice/-/detail/684005-2026", ["Equipment"],
    "Change notice for the same wellhead and frac-tree supply.",
    supply=True,
    bases={"Equipment": "TED description: supply of wellhead and frac-tree systems with installation services."},
    excluded=[{"label": "Engineering & Services", "reason": "Installation remains part of the equipment supply."}])
add("https://ted.europa.eu/en/notice/-/detail/689259-2026", ["Engineering & Services"],
    "The notice is a geothermal engineering consultancy framework.",
    bases={"Engineering & Services": "TED description: single-party framework for geothermal engineering consultancy, first project the GEMINI geothermal design."})
add("https://ted.europa.eu/en/notice/-/detail/691583-2026", ["Equipment"],
    "The notice is delivery of a fibre-optic temperature-measurement system for geothermal wells.",
    bases={"Equipment": "TED description: delivery of a system to measure temperature distribution and change in geothermal wells, with an automatic calibration rig for distributed fibre-optic sensors."})
add("https://ted.europa.eu/en/notice/-/detail/692185-2026", ["Engineering & Services"],
    "Award of a 2D seismic survey. The library summary states the survey scope; the TED excerpt confirms an exploration programme in the Aachen-Weisweiler licence.",
    bases={"Engineering & Services": "Library summary, confirmed in kind by the TED text: 2D seismic profiles of about 23 km and 12 km in the Aachen-Weisweiler licence, awarded to Smart Seismic Solutions."},
    uncertainty="The retrieved TED field describes the exploration programme and does not repeat the kilometre figures; those figures are the stored Library summary.")
add("https://ted.europa.eu/en/notice/-/detail/696202-2026", ["Engineering & Services"],
    "Framework for project management of surface installations, expressly excluding the geothermal wells.",
    bases={"Engineering & Services": "TED description: maîtrise d'oeuvre for surface production plant, distribution networks and substations of UniGéo, outside the geothermal wells."},
    excluded=[{"label": "Drilling", "reason": "The notice says the scope is outside the geothermal wells."}])
add("https://ted.europa.eu/en/notice/-/detail/698651-2026", ["Drilling"],
    "The notice is 30 geothermal boreholes and installation of the probes. Materials are included in that works package.",
    integrated=True,
    bases={"Drilling": "TED description: 30 geothermal boreholes, including placing the probes, and supply and installation of all required materials, for a cold heat network in Linnich."},
    excluded=[{"label": "Equipment", "reason": "Materials are included in the borehole works, not bought as a separate supply."}])
add("https://ted.europa.eu/en/notice/-/detail/701161-2026", ["Engineering & Services"],
    "The notice procures HOAI design and site supervision for heat-network sections.",
    bases={"Engineering & Services": "TED description: object planning of civil works, HOAI phases 2–8, including site supervision, and technical-equipment planning for distribution pipes and house connections, 2027–2029."},
    excluded=[{"label": "Drilling", "reason": "The planning is for the heat network, not a drilling contract."}])
add("https://ted.europa.eu/en/notice/-/detail/704493-2026", ["Equipment"],
    "Supply, installation and commissioning of absorption heat pumps. Installation is part of the supply.",
    supply=True,
    bases={"Equipment": "TED description: supply, installation and commissioning of absorption heat pumps recovering 7.3 MWth from geothermal and 2.8 MWth from biomass condensers."},
    excluded=[{"label": "Engineering & Services", "reason": "Installation and commissioning are described with the heat-pump supply."}])
add("https://ted.europa.eu/en/notice/-/detail/709263-2026", ["Drilling"],
    "The notice is 22 boreholes of 200 m and the geothermal probes for a school.",
    bases={"Drilling": "TED description: 22 boreholes of 200 m and complete construction of the borehole heat exchangers for the Ruwertalschule in Waldrach."})
add("https://ted.europa.eu/en/notice/-/detail/716179-2026", ["Drilling"],
    "The notice is design and construction of geothermal production, including two production wells in the Library summary. Design is part of that design-build.",
    integrated=True,
    bases={"Drilling": "Library summary, consistent with the TED title: two geothermal production wells, heat substations and transport pipelines. TED text: design and execution of works to increase geothermal heat production."},
    excluded=[{"label": "Engineering & Services", "reason": "Design is described as part of the same design-build, not as a separate consultancy."}],
    uncertainty="The TED extract does not repeat the well count. The well count is the stored Library summary. Substations and pipelines are in the same contract and are not given a second label.")
add("https://ted.europa.eu/en/notice/-/detail/729019-2026", ["Drilling"],
    "Same Kaba scope as TED 664782-2026: a new thermal well by drilling, plus heat centre and network.",
    bases={"Drilling": "TED description matches 664782-2026: new thermal well by drilling at the Kaba spa, with a heat block and heat network."},
    uncertainty="Surface heat centre and network are in the same notice and are not a second label.")
add("https://ted.europa.eu/en/notice/-/detail/730837-2026", ["Drilling"],
    "Same Litoměřice borehole scope as TED 670200-2026, with Charles University as co-buyer.",
    bases={"Drilling": "TED description: realisation of shallow geothermal boreholes, 100 boreholes of 100 m, with an option for 30 more."})
add("https://ted.europa.eu/en/notice/-/detail/734244-2026", ["Drilling"],
    "The notice is only part 1, the drilling contractor, for the Münster research well.",
    bases={"Drilling": "TED description: execution of a research borehole; the competition concerns only part 1, the drilling contractor."})
add("https://ted.europa.eu/en/notice/-/detail/737356-2026", ["Engineering & Services"],
    "Later notice for the same Grangegorman geothermal engineering consultancy framework.",
    bases={"Engineering & Services": "TED description: single-party framework for geothermal engineering consultancy, first project the GEMINI geothermal design."})
add("https://ted.europa.eu/en/notice/-/detail/738167-2026", ["Engineering & Services"],
    "The notice is a geothermal heat-pump feasibility study and a thermal response test.",
    bases={"Engineering & Services": "TED description: feasibility study and thermal response test for horizontal-loop, vertical-loop and aquifer options at University Hospital Galway."})
add("https://ted.europa.eu/en/notice/-/detail/739829-2026", ["Engineering & Services"],
    "The notice is planning of up to three doublets and help procuring the later drilling contract.",
    bases={"Engineering & Services": "TED description: planning of up to three geothermal doublets in the Hardt licence, then support for tendering the drilling contractor, service firms and equipment."},
    excluded=[{"label": "Drilling", "reason": "The drilling contractor is a later procurement this consultant would help tender, not this contract."}])
add("https://ted.europa.eu/en/notice/-/detail/751496-2026", ["Equipment"],
    "The contract is supply and assembly of electromechanical substation equipment. Design and manufacture are part of that supply.",
    supply=True,
    bases={"Equipment": "TED description: design, manufacture, transport, insurance, assembly, tests and commissioning of electrical and mechanical equipment for the Pico Vermelho geothermal-plant substation."},
    excluded=[{"label": "Engineering & Services", "reason": "Design and commissioning are described as part of supplying the substation equipment."}])
add("https://ted.europa.eu/en/notice/-/detail/752632-2026", ["Drilling"],
    "The notice covers drilling and installation of geothermal probes. Probe supply is inside that works package.",
    integrated=True,
    bases={"Drilling": "TED description: site establishment, drilling, and supply, installation and backfilling of geothermal probes, plus horizontal connection pipes, for Building 07B at St. Gallen Cantonal Hospital."},
    excluded=[{"label": "Equipment", "reason": "Probe supply is part of the drilling and installation works."}])
add("https://ted.europa.eu/en/notice/-/detail/754784-2026", ["Drilling"],
    "Replacement notice for the Münster research-well drilling contractor.",
    bases={"Drilling": "TED description: execution of a research borehole; the competition concerns only part 1, the drilling contractor."})

# Stored Library wording, original page not re-opened on 8 Nov 2026.
def lib(url, labels, rationale, uncertainty, bases, excluded=None, integrated=False, supply=False):
    add(url, labels, rationale, uncertainty=uncertainty, bases=bases, excluded=excluded or [], integrated=integrated, supply=supply)

U = "Original page was not re-opened on 8 Nov 2026. The excerpt is the stored Library summary."
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-97695", ["Engineering & Services"],
    "Stored summary: maîtrise d'oeuvre for an exploration well.", U,
    {"Engineering & Services": "Library summary: maîtrise d'oeuvre for an exploration well at Ferney-Voltaire, for a future doublet."},
    [{"label": "Drilling", "reason": "The summary is project management for the well, not the drilling contract."}])
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-95181", ["Engineering & Services"],
    "Stored summary: a 13-month study of two existing wells.", U,
    {"Engineering & Services": "Library summary: 13-month study on the Hélions 2 well and reuse options for the Les Cybéliades well."})
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-100440", ["Engineering & Services"],
    "Stored summary: full maîtrise d'oeuvre in tranches for a campus geothermal plant.", U,
    {"Engineering & Services": "Library summary: full maîtrise d'oeuvre in tranches for geothermal heat production at Campus Route de Mende."})
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-100285", ["Project owners & developers"],
    "Stored summary: a concession to design, finance, build and operate a Dogger heat network.", U,
    {"Project owners & developers": "Library summary: design, finance, build and operate a Dogger geothermal heat network; concession of about 27.5 years."},
    [{"label": "Engineering & Services", "reason": "Design is one part of the concession, not a separate services contract."}])
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-103297", ["Equipment"],
    "Stored summary: supply of an electrical submersible pump.", U,
    {"Equipment": "Library summary: supply of an ESP, with optional pressure sensor and connection box."},
    supply=True)
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-99761", ["Drilling"],
    "Stored summary: award of a vertical borehole field.", U,
    {"Drilling": "Library summary: award of lot 1, a vertical borehole field, to Geotec Energie."})
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-101091", ["Drilling"],
    "Stored summary: three boreholes of 80 m with a heat pump in the same works.", U,
    {"Drilling": "Library summary: 3 boreholes of 80 m, plus 3 optional, with a reversible water/water heat pump and surface distribution."},
    [{"label": "Equipment", "reason": "The heat pump is described inside the same borehole works."}],
    integrated=True)
lib("https://www.boamp.fr/pages/avis/?q=idweb:26-92903", ["Drilling", "Equipment"],
    "Stored summary names two lots: drilling and a geothermal heat pump.", U,
    {"Drilling": "Library summary: a drilling lot.", "Equipment": "Library summary: a separate geothermal heat-pump lot."})
lib("https://www.resmigazete.gov.tr/ilanlar/eskiilanlar/2026/09/20260927-3-4.pdf", ["Project owners & developers"],
    "Stored summary: auction of two three-year geothermal exploration licences.", U,
    {"Project owners & developers": "Library summary: auction of two exploration-licence fields of about 4,800 ha, three-year licences."})
lib("https://www.resmigazete.gov.tr/ilanlar/eskiilanlar/2026/10/20261018-3-1.pdf", ["Project owners & developers"],
    "Stored summary: auction of six three-year geothermal exploration licences.", U,
    {"Project owners & developers": "Library summary: auction of six exploration-licence areas, three-year licences."})
lib("https://groupe-coriance.fr/2026/09/25/aulnay-sous-bois-clap-de-fin-pour-le-forage-de-la-geothermie/", ["Drilling"],
    "Stored summary reports that the Dogger well was drilled. Completion news, not a drilling tender.", U,
    {"Drilling": "Library summary: Dogger well of about 2,000 m finished."})
lib("https://jeleniagora.naszemiasto.pl/woda-geotermalna-u-podnoza-karkonoszy-rozpoczeli-wiercenie-na-glebokosc-2500-metrow/ar/c7p2-29445853", ["Drilling"],
    "Stored summary reports that drilling of the 2,500 m research well has started. News report, not a tender.", U,
    {"Drilling": "Library summary: research well at Cieplice/Sobieszów, drilling started, about 12 months including tests."})
lib("https://www.veitur.is/en/bilanir/borad_laugarnes_2026-27", ["Drilling"],
    "Stored summary reports that hot-water drilling has started. Operator news, not a tender.", U,
    {"Drilling": "Library summary: five wells of 800–1,500 m; drilling started 16 Oct 2026."})

# Explicit non-proposals for items whose fetched text is not enough.
BLOCKED = {
    "https://ted.europa.eu/en/notice/-/detail/729199-2026": "TED API returned 'Befindet sich derzeit in Bearbeitung' for the description. Not tagged from the title Bohrplatzerrichtung.",
    "https://ted.europa.eu/en/notice/-/detail/749142-2026": "TED description of the building contract was retrieved and is surface building works, not a drilling, equipment or engineering scope. Left unclassified.",
    "https://ted.europa.eu/en/notice/-/detail/750816-2026": "TED description field was empty. Not tagged.",
}

def main():
    doc = json.loads(ASSIGN_PATH.read_text())
    reviewed = [a for a in doc["assignments"] if a["status"] == "reviewed"]
    reviewed_urls = {a["url"] for a in reviewed}
    proposed = []
    for url, spec in P.items():
        if url in reviewed_urls:
            continue
        text, access = excerpt_for(url)
        if access == "not_fetched":
            access = "library_summary_not_refetched"
            text = spec["bases"][spec["labels"][0]]
        labels = spec["labels"]
        proposed.append({
            "key": ("ted:" + ted_id(url)) if ted_id(url) else re.sub(r"[^a-z0-9]+", "-", url.lower())[:80],
            "notice_id": ("TED " + ted_id(url)) if ted_id(url) else url,
            "url": url,
            "library_title": spec.get("title") or "",
            "labels": labels,
            "status": "pending_review",
            "approved": False,
            "method": "manual",
            "integrated_package": spec["integrated_package"],
            "supply_package": spec["supply_package"],
            "bases": spec["bases"],
            "excluded": spec["excluded"],
            "basis": spec["rationale"],
            "uncertainty": spec["uncertainty"],
            "evidence_access": access,
            "evidence_excerpt": text[:700],
            "library_summary": "",
            "provenance": [
                {"type": "evidence", "access": access, "excerpt": text[:700], "url": url},
                {"type": "proposal", "result": "pending_independent_review", "note": "Not a reviewer approval."},
            ],
        })
    # fill titles and summaries from library
    by_url = {e["url"]: e for e in LIB}
    for row in proposed:
        src = by_url.get(row["url"])
        if src:
            row["library_title"] = src["title"]
            row["library_summary"] = src["summary"]
            if row["evidence_access"] == "library_summary_not_refetched" and src["summary"]:
                row["evidence_excerpt"] = src["summary"]
    doc["assignments"] = reviewed + proposed
    doc["status"] = "reviewed-examples-plus-pending-proposals"
    doc["updated"] = "2026-11-08"
    ASSIGN_PATH.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n")

    audit = []
    seen = set()
    for e in LIB:
        url = e["url"]
        seen.add(url)
        if url in reviewed_urls:
            rec = next(a for a in reviewed if a["url"] == url)
            audit.append(row_out(e["title"], url, "reviewed", rec["labels"], "independent_review_green", rec["basis"], "", e["summary"]))
        elif url in P:
            spec = P[url]
            text, access = excerpt_for(url)
            if access == "not_fetched":
                access = "library_summary_not_refetched"
                text = e["summary"]
            audit.append(row_out(e["title"], url, "pending_review", spec["labels"], access, spec["rationale"], spec["uncertainty"], text or e["summary"]))
        else:
            reason = BLOCKED.get(url) or unclassified_reason(e, excerpt_for(url))
            access = excerpt_for(url)[1]
            if url in BLOCKED and access == "ted_api_empty":
                kind = "blocked"
            elif access == "not_fetched" and not e["summary"]:
                kind = "blocked"
            else:
                kind = "unclassified"
            audit.append(row_out(e["title"], url, kind, [], access, reason, reason, excerpt_for(url)[0] or e["summary"]))
    # tender-only URLs are covered if they are also library URLs; add none extra here.
    out_json = ROOT / "audience" / "audit-2026-11-08.json"
    out_json.write_text(json.dumps({"generated": "2026-11-08", "items": audit}, ensure_ascii=False, indent=2) + "\n")
    fields = ["title", "url", "status", "labels", "evidence_access", "rationale", "uncertainty", "excerpt"]
    with (ROOT / "audience" / "audit-2026-11-08.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for row in audit:
            w.writerow({k: row[k] if k != "labels" else "|".join(row[k]) for k in fields})
    counts = {}
    for row in audit:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    lines = ["# Audience audit, 8 November 2026", "", "New labels are proposals for independent review. They are not reviewer approvals. The four GREEN examples stay reviewed.", "", "## Totals", ""]
    for k in ("reviewed", "pending_review", "unclassified", "blocked"):
        lines.append(f"- {k}: {counts.get(k, 0)}")
    lines += ["", "TED descriptions were read from the TED Search API on 8 November 2026. Where the API text was empty or only a placeholder, the row is blocked or unclassified and was not tagged from the title. BOAMP and other non-TED pages were not re-opened; a proposal from those rows uses the stored Library summary and says so.", "", "## Rows", ""]
    for row in audit:
        labels = ", ".join(row["labels"]) or "—"
        lines.append(f"### {row['title']}")
        lines.append(f"- Status: {row['status']}")
        lines.append(f"- Labels: {labels}")
        lines.append(f"- URL: {row['url']}")
        lines.append(f"- Evidence: {row['evidence_access']}")
        lines.append(f"- Rationale: {row['rationale']}")
        if row["uncertainty"]:
            lines.append(f"- Uncertainty: {row['uncertainty']}")
        if row["excerpt"]:
            lines.append(f"- Excerpt: {row['excerpt'][:500]}")
        lines.append("")
    (ROOT / "audience" / "audit-2026-11-08.md").write_text("\n".join(lines))
    print(counts, "proposed", len(proposed))

def unclassified_reason(e, fetched):
    text, access = fetched
    if access == "ted_api_empty":
        return "Fetched TED description was empty or only a placeholder. Not tagged from the title."
    if access == "ted_api_2026-11-08":
        return "Fetched TED description does not state a single drilling, equipment, engineering or project-development scope clearly enough to tag. Lot titles alone were not used."
    if e["kind"] in {"Project", "Licence", "Study/Data"}:
        return "Stored item is a project, licence or study announcement. It was not re-fetched, and it is not treated as a drilling, equipment, engineering or funding instrument without a clearer scope."
    if not e["summary"]:
        return "No stored summary, and the original page was not re-opened. Not tagged from the title."
    return "Stored summary does not state one audience scope clearly enough. Original page was not re-opened. Not tagged from keywords in the title."

def row_out(title, url, status, labels, access, rationale, uncertainty, excerpt):
    return {
        "title": title,
        "url": url,
        "status": status,
        "labels": labels,
        "evidence_access": access,
        "rationale": rationale,
        "uncertainty": uncertainty,
        "excerpt": (excerpt or "")[:700],
    }

if __name__ == "__main__":
    main()
