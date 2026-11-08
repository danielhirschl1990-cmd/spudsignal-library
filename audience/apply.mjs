/* Stamp Library and open-tender pages from audience/assignments.json.
   Run: node audience/apply.mjs
   Does not read titles for keywords and does not write map files. */
import fs from "fs";
import path from "path";
import { createRequire } from "module";
import { fileURLToPath, pathToFileURL } from "url";

const require = createRequire(import.meta.url);
const api = require("./filter.js");
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function read(rel) {
  return fs.readFileSync(path.join(root, rel), "utf8");
}
function write(rel, text) {
  fs.writeFileSync(path.join(root, rel), text);
}

function escapeAttr(s) {
  return api.escapeHtml(s);
}

function indexByUrl(assignments) {
  const map = new Map();
  for (const assignment of assignments) {
    map.set(assignment.url, assignment);
    try { map.set(decodeURIComponent(assignment.url), assignment); } catch (e) { /* keep raw */ }
  }
  return map;
}

function lookup(map, href) {
  if (map.has(href)) return map.get(href);
  try {
    const decoded = decodeURIComponent(href);
    if (map.has(decoded)) return map.get(decoded);
  } catch (e) { /* ignore */ }
  return null;
}

function visible(assignment) {
  return assignment && (assignment.status === "reviewed" || assignment.status === "pending_review");
}

function dataAttrs(assignment) {
  const labels = visible(assignment) ? assignment.labels : [];
  const status = assignment ? assignment.status : "unassigned";
  const approved = assignment && assignment.approved ? "true" : "false";
  return ` data-audience="${escapeAttr(labels.join("|"))}" data-audience-status="${status}" data-audience-approved="${approved}"`;
}

function chip(label) {
  return `<button type="button" class="audchip" data-g="audience" data-v="${escapeAttr(label)}" aria-pressed="false"><img class="audsym" src="${api.SYMBOLS[label]}" alt="" width="24" height="24"><span class="audname">${api.escapeHtml(label)}</span></button>`;
}

function audienceNotes(help) {
  return `<!-- audience-notes-start -->
<p class="audhelp" id="aud-help">${help}</p>
<p class="audempty" id="aud-empty" hidden>No entries carry the selected audience labels. Entries without an audience label stay in All.</p>
<!-- audience-notes-end -->`;
}

function audienceControls() {
  return `<!-- audience-bar-start -->
<div class="audblock" id="audience-bar">
<h2 class="audheading" id="aud-heading">Audience</h2>
<div class="audrow" role="group" aria-labelledby="aud-heading">
<button type="button" class="audchip audall" id="aud-all" aria-pressed="true">All</button>
${api.LABELS.map(chip).join("\n")}
</div>
<p class="audcount" id="aud-count" role="status"></p>
</div>
<!-- audience-bar-end -->`;
}

const LIBRARY_HELP = "Audience labels are guidance on who an item is relevant to. They are not eligibility. All shows every source. If you select more than one audience, a source is shown when it carries any of those labels. The same labels filter the map.";
const TENDERS_HELP = "Audience labels are guidance on who an item is relevant to. They are not eligibility. All shows every entry. If you select more than one audience, an entry is shown when it carries any of those labels. These labels combine with type, technical category and country. The same labels filter the map.";

function replaceBlock(html, start, end, original, replacement) {
  const block = `${start}\n${replacement}\n${end}`;
  if (html.includes(start)) {
    const re = new RegExp(start.replace(/[.*+?^${}()|[\]\\]/g, "\\$&") + "[\\s\\S]*?" + end.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    return html.replace(re, block);
  }
  if (!html.includes(original)) throw new Error("Missing expected markup:\n" + original.slice(0, 180));
  return html.replace(original, block);
}

function stampLibrary(html, byUrl) {
  if (!html.includes('href="/audience/badges.css"')) {
    html = html.replace('<meta name="theme-color" content="#0F2A3D">', '<meta name="theme-color" content="#0F2A3D">\n<link rel="stylesheet" href="/audience/badges.css">');
  }
  const blurbFrom = "open entries · filter by country, type, category, deadline and CPV.";
  const blurbTo = "open entries · filter by country, type, technical category, deadline, CPV and audience.";
  if (html.includes(blurbFrom)) html = html.replace(blurbFrom, blurbTo);
  else if (!html.includes(blurbTo)) throw new Error("Library tender blurb not found");
  const notes = audienceNotes(LIBRARY_HELP);
  const controls = audienceControls();
  const mapNote = "<!-- map-audience-limit --><p class=\"maplimit\">The map does not filter by audience.</p>";
  if (!html.includes("<!-- map-audience-limit -->")) {
    const marker = 'href="/map/" style="background:#0F2A3D;color:#fff;border-color:#E97828"';
    const at = html.indexOf(marker);
    if (at < 0) throw new Error("Library map link not found");
    const end = html.indexOf("</a>", at);
    html = html.slice(0, end + 4) + "\n" + mapNote + "\n" + notes + "\n" + controls + "\n" + html.slice(end + 4);
  } else if (html.includes("<!-- audience-notes-start -->")) {
    html = html.replace(/<!-- audience-notes-start -->[\s\S]*?<!-- audience-notes-end -->/, notes);
    html = html.replace(/<!-- audience-bar-start -->[\s\S]*?<!-- audience-bar-end -->/, controls);
  } else {
    html = html.replace(/<!-- audience-bar-start -->[\s\S]*?<!-- audience-bar-end -->/, notes + "\n" + controls);
  }
  html = html.replace(/<div class="libcard"[^>]*style="background:#fff;border:1px solid #C8D2DC;border-left:4px solid/g, '<div style="background:#fff;border:1px solid #C8D2DC;border-left:4px solid');
  html = html.replace(/ data-audience="[^"]*"/g, "");
  html = html.replace(/ data-audience-status="[^"]*"/g, "");
  html = html.replace(/ data-audience-approved="[^"]*"/g, "");
  html = html.replace(/<!--auds-->[\s\S]*?<!--\/auds-->/g, "");
  html = html.replace(/<div style="background:#fff;border:1px solid #C8D2DC;border-left:4px solid [^"]+">[\s\S]*?(?=<div style="background:#fff;border:1px solid #C8D2DC;border-left:4px solid|<h2 |<div style="background:#E97828)/g, function (card) {
    const href = card.match(/<a href="([^"]+)"/);
    if (!href) return card;
    const assignment = lookup(byUrl, href[1]);
    let next = card.replace("<div ", "<div class=\"libcard\"" + dataAttrs(assignment) + " ");
    const badge = visible(assignment) ? "<!--auds-->" + api.badgeHtml(assignment) + "<!--/auds-->" : "";
    const cut = next.indexOf("</span>");
    if (cut < 0) throw new Error("Library card has no kind badge");
    next = next.slice(0, cut + 7) + badge + next.slice(cut + 7);
    return next;
  });
  if (!html.includes("/audience/library.js")) {
    html = html.replace("</body>", '<script src="/audience/filter.js"></script>\n<script src="/audience/library.js"></script>\n</body>');
  }
  return html.replace(/<!-- map-audience-limit --><p class="maplimit">The map does not filter by audience\.<\/p>\n?/g, "");
}

const SEL_ORIGINAL = 'var sel={kind:{},tag:{},country:{}},tab="open";\n[].forEach.call(document.querySelectorAll(".chip[data-g]"),function(b){b.addEventListener("click",function(){var g=b.dataset.g,v=b.dataset.v;if(sel[g][v])delete sel[g][v];else sel[g][v]=1;b.setAttribute("aria-pressed",!!sel[g][v]);refresh();});});\ndocument.getElementById("reset").addEventListener("click",function(){sel={kind:{},tag:{},country:{}};[].forEach.call(document.querySelectorAll(".chip[data-g]"),function(b){b.setAttribute("aria-pressed","false");});refresh();});';
const SEL_NEXT = `var sel={kind:{},tag:{},country:{},audience:{}},tab="open";
function chipButtons(){return document.querySelectorAll(".chip[data-g], .audchip[data-g]");}
[].forEach.call(chipButtons(),function(b){b.addEventListener("click",function(){var g=b.dataset.g,v=b.dataset.v;if(!sel[g])return;if(sel[g][v])delete sel[g][v];else sel[g][v]=1;b.setAttribute("aria-pressed",sel[g][v]?"true":"false");refresh();});});
document.getElementById("reset").addEventListener("click",function(){sel={kind:{},tag:{},country:{},audience:{}};[].forEach.call(chipButtons(),function(b){b.setAttribute("aria-pressed","false");});refresh();});
var audAll=document.getElementById("aud-all");if(audAll)audAll.addEventListener("click",function(){sel.audience={};[].forEach.call(document.querySelectorAll('.audchip[data-g="audience"]'),function(b){b.setAttribute("aria-pressed","false");});refresh();});`;

const MATCH_ORIGINAL = 'function match(c){var e=E[c.dataset.uid];if(!e)return true;\n for(var g in sel){var ks=Object.keys(sel[g]);if(!ks.length)continue;\n  if(g==="tag"){if(!ks.some(function(k){return e.tags.indexOf(k)>=0;}))return false;}else if(ks.indexOf(e[g])<0)return false;}\n if(tab==="soon"&&!soon(e))return false;if(tab==="saved"&&!saved[e.uid])return false;return true;}';
const MATCH_NEXT = `function match(c){var e=E[c.dataset.uid];if(!e)return true;
 for(var g in sel){var ks=Object.keys(sel[g]);if(!ks.length)continue;
  if(g==="tag"){if(!ks.some(function(k){return (e.tags||[]).indexOf(k)>=0;}))return false;}
  else if(g==="audience"){if(!window.SpudAudience.audienceMatch(e.audience||[],ks))return false;}
  else if(ks.indexOf(e[g])<0)return false;}
 if(tab==="soon"&&!soon(e))return false;if(tab==="saved"&&!saved[e.uid])return false;return true;}`;

const COUNT_ORIGINAL = 'document.getElementById("count").textContent=n+" of "+D.entries.length+" entries shown"+(tab==="soon"?" · closing within 14 days":tab==="saved"?" · saved on this device":"");';
const COUNT_NEXT = `var audKeys=Object.keys(sel.audience);
 document.getElementById("count").textContent=n+" of "+D.entries.length+" entries shown"+(tab==="soon"?" · closing within 14 days":tab==="saved"?" · saved on this device":"")+(audKeys.length?" · audience: any of "+audKeys.join(", "):"");
 var audCount=document.getElementById("aud-count");if(audCount)audCount.textContent=audKeys.length?("Audience: any of "+audKeys.join(", ")):"All audiences";
 if(audAll)audAll.setAttribute("aria-pressed",audKeys.length?"false":"true");`;

function stampTenders(html, byUrl, data) {
  if (!html.includes('href="/audience/badges.css"')) {
    html = html.replace('<link rel="manifest"', '<link rel="stylesheet" href="/audience/badges.css">\n<link rel="manifest"');
  }
  html = html.replace('class="chip reset" id="reset" aria-pressed="false"', 'class="chip reset" id="reset" aria-pressed="true"');
  const bar = audienceControls();
  const notes = audienceNotes(TENDERS_HELP);
  if (html.includes("<!-- audience-notes-start -->")) {
    html = html.replace(/<!-- audience-notes-start -->[\s\S]*?<!-- audience-notes-end -->/, notes);
  } else {
    html = html.replace('<div class="bar" id="bar">', notes + '\n<div class="bar" id="bar">');
  }
  if (!html.includes("<!-- audience-bar-start -->")) {
    const anchor = 'id="reset" aria-pressed="true">All</button></div>';
    const at = html.indexOf(anchor);
    if (at < 0) throw new Error("Tenders All row not found");
    const end = at + anchor.length;
    html = html.slice(0, end) + "\n" + bar + html.slice(end);
  } else {
    html = html.replace(/<!-- audience-bar-start -->[\s\S]*?<!-- audience-bar-end -->/, bar);
  }
  if (!html.includes("<!-- map-audience-limit -->")) {
    const marker = '<a class="maplink" href="/map/"';
    const at = html.indexOf(marker);
    if (at < 0) throw new Error("Tenders map link not found");
    const end = html.indexOf("</a>", at);
    html = html.slice(0, end + 4) + '\n<!-- map-audience-limit --><p class="maplimit">The map does not filter by audience.</p>' + html.slice(end + 4);
  }
  html = html.replace(/ data-audience="[^"]*"/g, "");
  html = html.replace(/ data-audience-status="[^"]*"/g, "");
  html = html.replace(/ data-audience-approved="[^"]*"/g, "");
  html = html.replace(/<!--auds-->[\s\S]*?<!--\/auds-->/g, "");
  html = html.replace(/<article class="card"[\s\S]*?<\/article>/g, function (article) {
    const href = article.match(/<h3><a href="([^"]+)"/);
    if (!href) return article;
    const assignment = lookup(byUrl, href[1]);
    let next = article.replace('<article class="card"', '<article class="card"' + dataAttrs(assignment));
    if (visible(assignment)) {
      const badge = "<!--auds-->" + api.badgeHtml(assignment) + "<!--/auds-->";
      if (!next.includes('<span class="dyn"></span>')) throw new Error("Tender card missing dyn slot");
      next = next.replace('<span class="dyn"></span>', badge + '<span class="dyn"></span>');
    }
    return next;
  });
  html = replaceBlock(html, "/* audience-sel-start */", "/* audience-sel-end */", SEL_ORIGINAL, SEL_NEXT);
  html = replaceBlock(html, "/* audience-match-start */", "/* audience-match-end */", MATCH_ORIGINAL, MATCH_NEXT);
  html = replaceBlock(html, "/* audience-count-start */", "/* audience-count-end */", COUNT_ORIGINAL, COUNT_NEXT);
  html = html.replace(/<!-- map-audience-limit --><p class="maplimit">The map does not filter by audience\.<\/p>\n?/g, "");
  if (!html.includes('src="/audience/filter.js"')) {
    html = html.replace("<script>\n(function(){", '<script src="/audience/filter.js"></script>\n<script>\n(function(){');
  }
  const about = '<p id="audience-about">Audience labels use the same assignment record on the Library, the open-tender list and the map. They are guidance, not eligibility. Several selected labels match an entry that carries any of them. An entry with no label stays visible under All.</p>';
  if (!html.includes('id="audience-about"')) {
    html = html.replace('<section class="box"><h2>About this app</h2>', '<section class="box"><h2>About this app</h2>\n' + about);
  } else {
    html = html.replace(/<p id="audience-about">[\s\S]*?<\/p>/, about);
  }
  const json = JSON.stringify(data).replace(/</g, "\\u003c");
  if (!html.includes('<script type="application/json" id="data">')) throw new Error("Tender data script missing");
  html = html.replace(/<script type="application\/json" id="data">[\s\S]*?<\/script>/, '<script type="application/json" id="data">' + json + "</script>");
  return html;
}

function newsletter(doc) {
  const legend = api.LABELS.map(function (label) {
    return `<li>${api.emailImg(label)}<span>${api.escapeHtml(label)}</span></li>`;
  }).join("");
  const blocks = doc.assignments.map(function (assignment) {
    const body = assignment.labels.length
      ? `<p class="forline"><span class="audfor">For:</span> ${assignment.labels.map(function (label) {
          return `<span class="aud">${api.emailImg(label)}<span class="audname">${api.escapeHtml(label)}</span></span>`;
        }).join(" ")}</p>`
      : `<p class="forline">No audience tag.</p>`;
    return `<article>
<h2>${api.escapeHtml(assignment.library_title)}</h2>
<p>Notice ${api.escapeHtml(assignment.notice_id)}. <a href="${api.escapeHtml(assignment.url)}">${api.escapeHtml(assignment.url)}</a></p>
${body}
<p>${api.escapeHtml(assignment.library_summary)}</p>
</article>`;
  }).join("\n");
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Newsletter audience excerpt – not a published issue</title>
<link rel="stylesheet" href="/audience/badges.css">
</head><body style="margin:0;background:#fff;color:#1B2B38;font:16px/1.45 -apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Arial,sans-serif">
<main style="max-width:640px;margin:0 auto;padding:16px">
<p><strong>Template excerpt only.</strong> The Beehiiv newsletter was not edited. Words stay readable if the images are blocked. Do not shorten the names.</p>
<p>Image addresses in this file are root-relative (<code>/symbols/…</code>). They work on this Library site. They are not portable in Beehiiv. When a label is inserted there, replace each <code>src</code> and <code>srcset</code> with the absolute public URL of the same file, such as <code>https://library.spudsignal.com/symbols/aud-drilling.png</code> and its <code>@2x</code> file, after that file is on the public site. This excerpt is not ready to paste into Beehiiv.</p>
<h1 style="font-size:22px;color:#0F2A3D">Audience legend</h1>
<img class="audlegendimg" src="/symbols/legend.png" srcset="/symbols/legend.png 1x, /symbols/legend@2x.png 2x" width="594" height="59" alt="">
<ul class="newsletter-legend">${legend}</ul>
<p>Tags are editorial guidance, always check the notice scope.</p>
${blocks}
<aside class="layout-sample">
<p><strong>Layout sample only.</strong> Not a source and not an assignment. Two full names wrap in a narrow column.</p>
<p class="forline"><span class="audfor">For:</span> <span class="aud">${api.emailImg("Drilling")}<span class="audname">Drilling</span></span> <span class="aud">${api.emailImg("Engineering & Services")}<span class="audname">Engineering &amp; Services</span></span></p>
</aside>
<p>Web pages use the original SVG symbols. This template uses the PNG and @2x files. The map has no audience filter.</p>
</main></body></html>
`;
}

function stampData(data, byUrl) {
  for (const entry of data.entries) {
    const assignment = lookup(byUrl, entry.url);
    const labels = visible(assignment) ? assignment.labels.slice() : [];
    entry.audience = labels;
    entry.audience_status = assignment ? assignment.status : "unassigned";
  }
  return data;
}

export function apply() {
  const doc = JSON.parse(read("audience/assignments.json"));
  const errors = api.validateAssignments(doc);
  if (errors.length) throw new Error("Assignment record failed validation:\n" + errors.join("\n"));
  const byUrl = indexByUrl(doc.assignments);
  write("index.html", stampLibrary(read("index.html"), byUrl));
  const data = stampData(JSON.parse(read("tenders/tenders.json")), byUrl);
  write("tenders/tenders.json", JSON.stringify(data, null, 1) + "\n");
  let tenders = stampTenders(read("tenders/index.html"), byUrl, data);
  write("tenders/index.html", tenders);
  write("audience/newsletter-item.html", newsletter(doc));
  let sw = read("tenders/sw.js");
  sw = sw.replace(/const C = "ss-tenders-[^"]+";/, 'const C = "ss-tenders-20261108audsymbols";');
  const symbolPre = '"/symbols/aud-drilling.svg", "/symbols/aud-equipment.svg", "/symbols/aud-engineering.svg", "/symbols/aud-owners.svg"';
  if (sw.includes("/symbols/drilling.svg")) {
    sw = sw.replace('"/symbols/drilling.svg", "/symbols/equipment.svg", "/symbols/engineering-services.svg", "/symbols/project-owners.svg"', symbolPre);
  } else if (!sw.includes("/symbols/aud-drilling.svg")) {
    sw = sw.replace('"/favicon.svg"', '"/favicon.svg", "/audience/badges.css", "/audience/filter.js", ' + symbolPre);
  }
  write("tenders/sw.js", sw);
  return doc;
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  apply();
  console.log("Applied audience assignments");
}
