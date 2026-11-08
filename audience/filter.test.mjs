import test from "node:test";
import assert from "node:assert/strict";
import fs from "fs";
import path from "path";
import { createRequire } from "module";
import { execSync } from "child_process";
import { apply } from "./apply.mjs";

const require = createRequire(import.meta.url);
const api = require("./filter.js");
const root = path.resolve(import.meta.dirname, "..");

apply();
const doc = JSON.parse(fs.readFileSync(path.join(root, "audience/assignments.json"), "utf8"));
const indexHtml = fs.readFileSync(path.join(root, "index.html"), "utf8");
const tendersHtml = fs.readFileSync(path.join(root, "tenders/index.html"), "utf8");
const tenders = JSON.parse(fs.readFileSync(path.join(root, "tenders/tenders.json"), "utf8"));
const newsletter = fs.readFileSync(path.join(root, "audience/newsletter-item.html"), "utf8");
const preview = fs.readFileSync(path.join(root, "audience/preview.html"), "utf8");

function byNotice(id) {
  return doc.assignments.find((row) => row.notice_id === id);
}

test("the shared record matches the review draft and stays unapproved", () => {
  assert.deepEqual(api.validateAssignments(doc), []);
  assert.equal(doc.assignments.filter((row) => row.status === "reviewed" && row.approved).length, 4);
  assert.ok(doc.assignments.filter((row) => row.status === "pending_review" && row.approved === false).length > 20);
  const kutno = byNotice("TED 725171-2026");
  const hvc = byNotice("TED 726565-2026");
  const paris = byNotice("TED 755201-2026");
  const feder = byNotice("FR-IDF-FEDER-geothermie-2026");
  assert.deepEqual(kutno.labels, ["Drilling"]);
  assert.equal(kutno.status, "reviewed");
  assert.equal(kutno.integrated_package, true);
  assert.deepEqual(hvc.labels, ["Equipment"]);
  assert.equal(hvc.supply_package, true);
  assert.match(hvc.bases.Equipment, /two portfolio lots/);
  assert.deepEqual(paris.labels, ["Engineering & Services"]);
  assert.deepEqual(feder.labels, ["Project owners & developers"]);
  assert.equal(feder.status, "reviewed");
  assert.match(feder.bases["Project owners & developers"], /§2/);
  assert.match(feder.bases["Project owners & developers"], /§3\.1/);
  assert.match(feder.eligibility_caveat, /not mean that every reader/);
  assert.equal(doc.assignments.some((row) => row.status === "pending_review" && row.labels.length > 1), true);
});

test("integrated packages, equipment supply and FEDER cannot pick up an extra label", () => {
  const kutno = structuredClone(byNotice("TED 725171-2026"));
  kutno.labels = ["Drilling", "Equipment"];
  kutno.bases.Equipment = "not a separate supply";
  const broken = structuredClone(doc);
  broken.assignments = broken.assignments.map((row) => row.notice_id === kutno.notice_id ? kutno : row);
  assert.ok(api.validateAssignments(broken).some((error) => error.includes("integrated package")));

  const hvc = structuredClone(byNotice("TED 726565-2026"));
  hvc.labels = ["Equipment", "Engineering & Services"];
  hvc.bases["Engineering & Services"] = "integral product engineering is not a separate service";
  const supplyDoc = structuredClone(doc);
  supplyDoc.assignments = supplyDoc.assignments.map((row) => row.notice_id === hvc.notice_id ? hvc : row);
  assert.ok(api.validateAssignments(supplyDoc).some((error) => error.includes("equipment supply")));

  const feder = structuredClone(byNotice("FR-IDF-FEDER-geothermie-2026"));
  feder.labels = ["Project owners & developers", "Drilling"];
  feder.bases.Drilling = "a funded project might later drill";
  const federDoc = structuredClone(doc);
  federDoc.assignments = federDoc.assignments.map((row) => row.notice_id === feder.notice_id ? feder : row);
  assert.ok(api.validateAssignments(federDoc).some((error) => error.includes("FEDER example cannot add Drilling")));
});

test("ANY/OR inside audience and AND across the existing filters", () => {
  const kutno = { kind: "tender", country: "PL", tags: ["Other"], audience: ["Drilling"] };
  const hvc = { kind: "tender", country: "NL", tags: ["Other"], audience: ["Equipment"] };
  const paris = { kind: "tender", country: "FR", tags: ["Other"], audience: ["Engineering & Services"] };
  const feder = { kind: "funding", country: "FR", tags: [], audience: ["Project owners & developers"] };
  const unknown = { kind: "tender", country: "DE", tags: ["Other"], audience: [] };
  const multi = { kind: "tender", country: "DE", tags: ["Deep well", "Planning"], audience: ["Drilling", "Equipment"] };

  assert.equal(api.entryMatch(kutno, {}), true);
  assert.equal(api.entryMatch(feder, {}), true);
  assert.equal(api.entryMatch(unknown, {}), true);
  assert.equal(api.entryMatch(unknown, { audience: ["Drilling"] }), false);
  assert.equal(api.entryMatch(feder, { audience: ["Project owners & developers"] }), true);
  assert.equal(api.entryMatch(feder, { audience: ["Project owners & developers"], country: ["FR"], kind: ["funding"] }), true);
  assert.equal(api.entryMatch(feder, { audience: ["Project owners & developers"], kind: ["tender"] }), false);
  assert.equal(api.entryMatch(feder, { audience: ["Drilling"] }), false);
  assert.equal(api.entryMatch(kutno, { audience: ["Drilling", "Equipment"] }), true);
  assert.equal(api.entryMatch(hvc, { audience: ["Drilling", "Equipment"] }), true);
  assert.equal(api.entryMatch(paris, { audience: ["Drilling"] }), false);
  assert.equal(api.entryMatch(multi, { audience: ["Equipment"] }), true);
  assert.equal(api.entryMatch(multi, { audience: ["Engineering & Services"] }), false);
  assert.equal(api.entryMatch(kutno, { audience: ["Drilling"], country: ["PL"], tag: ["Other"], kind: ["tender"] }), true);
  assert.equal(api.entryMatch(kutno, { audience: ["Drilling"], country: ["FR"] }), false);
  assert.equal(api.entryMatch(kutno, { audience: ["Drilling"], tag: ["Deep well"] }), false);
  assert.equal(api.entryMatch(paris, { audience: ["Engineering & Services"], country: ["FR"], kind: ["funding"] }), false);
  assert.equal(api.audienceMatch([], []), true);
  assert.equal(api.audienceMatch(["Drilling"], []), true);
});

test("badges use the full names and say when a proposal is not approved", () => {
  const html = api.badgeHtml(byNotice("TED 725171-2026"));
  assert.match(html, /For:/);
  assert.match(html, />Drilling</);
  assert.doesNotMatch(html, /Proposed, pending review/);
  assert.doesNotMatch(html, /Equipment/);
  const federHtml = api.badgeHtml(byNotice("FR-IDF-FEDER-geothermie-2026"));
  assert.match(federHtml, /Project owners &amp; developers/);
  assert.doesNotMatch(federHtml, /Proposed, pending review/);
  const pending = { status: "pending_review", labels: ["Equipment"] };
  assert.match(api.badgeHtml(pending), /Proposed, pending review/);
});

test("Library and tender pages share the record and keep full labels", () => {
  for (const label of api.LABELS) {
    const encoded = label.replaceAll("&", "&amp;");
    assert.ok(indexHtml.includes(encoded), label);
    assert.ok(tendersHtml.includes(encoded), label);
    assert.ok(newsletter.includes(encoded), label);
  }
  for (const banned of ["Eng. & Services", "Owners & developers", "Eng & Services"]) {
    assert.equal(indexHtml.includes(banned), false, banned);
    assert.equal(tendersHtml.includes(banned), false, banned);
    assert.equal(newsletter.includes(banned), false, banned);
    assert.equal(preview.includes(banned), false, banned);
  }
  assert.match(indexHtml, /id="e-library-kutno"|data-audience="Drilling"/);
  assert.match(indexHtml, /Proposed, pending review/);
  assert.doesNotMatch(indexHtml.slice(indexHtml.indexOf("725171-2026") - 400, indexHtml.indexOf("725171-2026")), /Proposed, pending review/);
  assert.doesNotMatch(indexHtml, /stays untagged until/);
  assert.doesNotMatch(indexHtml, /does not filter by audience/);
  assert.match(indexHtml, /The same labels filter the map/);
  assert.match(tendersHtml, /data-audience="Drilling"/);
  assert.match(tendersHtml, /data-audience="Equipment"/);
  assert.match(tendersHtml, /data-audience="Engineering &amp; Services"/);
  const federAt = tendersHtml.indexOf('id="e-d6aceeed5e1cf4bd"');
  const federCard = tendersHtml.slice(federAt - 280, federAt + 900);
  assert.match(federCard, /data-audience="Project owners &amp; developers"/);
  assert.match(federCard, /data-audience-status="reviewed"/);
  assert.match(federCard, /class="audname">Project owners &amp; developers</);
  assert.match(tendersHtml, /audienceMatch/);
  assert.match(tendersHtml, /tab==="soon"/);
  assert.doesNotMatch(indexHtml, /does not filter by audience/);
  assert.match(indexHtml, /The same labels filter the map/);
  assert.doesNotMatch(tendersHtml, /does not filter by audience/);
  assert.match(tendersHtml, /The same labels filter the map/);
  assert.match(newsletter, /was not edited/);
  assert.match(newsletter, /For:/);
  assert.match(preview, /Layout sample only/);
  assert.match(preview, /Engineering &amp; Services/);
  assert.match(preview, /Project owners &amp; developers/);
});

test("open-tender facts and the map files stay unchanged", () => {
  const before = JSON.parse(execSync("git show main:tenders/tenders.json", { cwd: root }));
  assert.equal(tenders.entries.length, before.entries.length);
  assert.deepEqual(tenders.removed, before.removed);
  const base = ["uid", "kind", "src", "id", "title", "title_official", "buyer", "country", "tz", "deadline_iso", "deadline_txt", "deadline_label", "time_note", "tags", "cpv", "url", "checked", "flag", "first_seen", "change", "accessed"];
  tenders.entries.forEach((entry, i) => {
    const prior = before.entries[i];
    for (const key of base) assert.deepEqual(entry[key], prior[key], entry.uid + " " + key);
    assert.deepEqual(Object.keys(entry).slice(0, base.length), base);
    assert.ok(["unassigned", "pending_review", "untagged", "reviewed"].includes(entry.audience_status));
  });
  const kutno = tenders.entries.find((entry) => entry.id === "TED 725171-2026");
  assert.deepEqual(kutno.audience, ["Drilling"]);
  assert.equal(kutno.audience_status, "reviewed");
  assert.equal(kutno.tags.includes("Other"), true);
  const feder = tenders.entries.find((entry) => entry.id === "FR-IDF-FEDER-geothermie-2026");
  assert.deepEqual(feder.audience, ["Project owners & developers"]);
  assert.equal(feder.audience_status, "reviewed");
  const tagged = tenders.entries.filter((entry) => entry.audience.length);
  assert.ok(tagged.length > 4);
  const kaba = tenders.entries.find((entry) => entry.id === "TED 729019-2026");
  assert.deepEqual(kaba.audience, ["Drilling"]);
  assert.equal(kaba.audience_status, "pending_review");
  const blocked = tenders.entries.find((entry) => entry.id === "TED 729199-2026");
  assert.deepEqual(blocked.audience, []);
  assert.equal(blocked.audience_status, "unassigned");
  const files = execSync("git ls-files map tenders/deadlines.ics tenders/ics", { cwd: root, encoding: "utf8" }).trim().split("\n").filter((file) => file !== "map/index.html");
  for (const file of files) {
    const disk = fs.readFileSync(path.join(root, file));
    const git = execSync(`git show main:${file}`, { cwd: root });
    assert.deepEqual(disk, git, file);
  }
  const mapHtml = fs.readFileSync(path.join(root, "map/index.html"), "utf8");
  assert.match(mapHtml, /\/symbols\/aud-drilling\.svg/);
  assert.match(mapHtml, /audienceMatch/);
  assert.match(mapHtml, /markerClusterGroup/);
  assert.doesNotMatch(mapHtml, /file:\/\//);
});

test("Library summaries and source links for the four examples are intact", () => {
  const quotes = [
    ["725171-2026", "Drilling, casing, cementing, completion and hydrogeological tests"],
    ["726565-2026", "Plate-and-frame heat exchangers"],
    ["755201-2026", "Framework for maîtrise d"],
    ["AAP_FEDER2026_G%C3%A9othermie.pdf", "Regional ERDF call for geothermal heat and cold"]
  ];
  for (const [url, quote] of quotes) {
    assert.ok(indexHtml.includes(url), url);
    assert.ok(indexHtml.includes(quote), quote);
  }
  assert.equal((indexHtml.match(/class="libcard"/g) || []).length, 92);
});

test("web uses the original SVG symbols and email uses PNG with a 2x source", () => {
  const pages = [indexHtml, tendersHtml, preview, newsletter];
  for (const page of pages) {
    assert.equal(page.includes("file://"), false);
    assert.equal(page.includes("/symbols/drilling.svg"), false);
    assert.equal(page.includes("/symbols/project-owners.svg"), false);
  }
  for (const file of ["aud-drilling.svg", "aud-equipment.svg", "aud-engineering.svg", "aud-owners.svg"]) {
    assert.ok(indexHtml.includes("/symbols/" + file), file);
    assert.ok(tendersHtml.includes("/symbols/" + file), file);
    const svg = fs.readFileSync(path.join(root, "symbols", file), "utf8");
    assert.match(svg, /viewBox="0 0 24 24"/);
  }
  assert.match(fs.readFileSync(path.join(root, "symbols/aud-drilling.svg"), "utf8"), /M12 2\.5/);
  assert.match(fs.readFileSync(path.join(root, "symbols/aud-equipment.svg"), "utf8"), /<circle /);
  assert.match(fs.readFileSync(path.join(root, "symbols/aud-engineering.svg"), "utf8"), /M3\.5 20\.5V3\.5l17 17Z/);
  assert.match(fs.readFileSync(path.join(root, "symbols/aud-owners.svg"), "utf8"), /M6\.5 21\.8V2\.6/);
  assert.match(newsletter, /src="\/symbols\/aud-drilling\.png"/);
  assert.match(newsletter, /srcset="\/symbols\/aud-drilling\.png 1x, \/symbols\/aud-drilling@2x\.png 2x"/);
  assert.match(newsletter, /srcset="\/symbols\/legend\.png 1x, \/symbols\/legend@2x\.png 2x"/);
  assert.match(newsletter, />Drilling</);
  assert.doesNotMatch(newsletter, /Proposed, pending review/);
  assert.match(newsletter, /not ready to paste into Beehiiv/);
  assert.match(newsletter, /https:\/\/library\.spudsignal\.com\/symbols\/aud-drilling\.png/);
  assert.equal(byNotice("TED 725171-2026").status, "reviewed");
  assert.equal(byNotice("TED 725171-2026").approved, true);
});
