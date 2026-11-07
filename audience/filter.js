/* Shared audience matching and assignment checks.
   Classic script in the browser (window.SpudAudience) and CommonJS in Node.
   Labels are read only from audience/assignments.json. Nothing here guesses from keywords. */
(function (root, factory) {
  var api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.SpudAudience = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  var LABELS = [
    "Drilling",
    "Equipment",
    "Engineering & Services",
    "Project owners & developers"
  ];
  var SYMBOLS = {
    "Drilling": "/symbols/drilling.svg",
    "Equipment": "/symbols/equipment.svg",
    "Engineering & Services": "/symbols/engineering-services.svg",
    "Project owners & developers": "/symbols/project-owners.svg"
  };
  var PNG = {
    "Drilling": "/symbols/drilling.png",
    "Equipment": "/symbols/equipment.png",
    "Engineering & Services": "/symbols/engineering-services.png",
    "Project owners & developers": "/symbols/project-owners.png"
  };

  function escapeHtml(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  /* Empty selection means All. Several labels match if the entry carries any of them. */
  function audienceMatch(labels, selected) {
    var have = labels || [];
    var want = selected || [];
    if (!want.length) return true;
    return want.some(function (label) { return have.indexOf(label) >= 0; });
  }

  /* Across groups, every group that has a selection must match (AND).
     Inside tag, country, kind and audience, any selected value is enough (OR / ANY). */
  function entryMatch(entry, sel) {
    sel = sel || {};
    var kind = sel.kind || [];
    var tag = sel.tag || [];
    var country = sel.country || [];
    var audience = sel.audience || [];
    if (kind.length && kind.indexOf(entry.kind) < 0) return false;
    if (country.length && country.indexOf(entry.country) < 0) return false;
    if (tag.length && !tag.some(function (t) { return (entry.tags || []).indexOf(t) >= 0; })) return false;
    if (!audienceMatch(entry.audience || [], audience)) return false;
    return true;
  }

  function badgeHtml(assignment) {
    if (!assignment) return "";
    if (assignment.status !== "reviewed" && assignment.status !== "pending_review") return "";
    if (!assignment.labels || !assignment.labels.length) return "";
    var chips = assignment.labels.map(function (label) {
      return '<span class="aud"><img class="audsym" src="' + SYMBOLS[label] + '" alt="" width="18" height="18"><span class="audname">' + escapeHtml(label) + '</span></span>';
    }).join("");
    var state = assignment.status === "pending_review"
      ? '<span class="audstate">Proposed, pending review</span>'
      : "";
    return '<span class="auds" data-audience-status="' + assignment.status + '"><span class="audfor">For:</span>' + chips + state + '</span>';
  }

  function validateAssignments(doc) {
    var errors = [];
    var expected = LABELS;
    if (!doc || !Array.isArray(doc.assignments)) {
      errors.push("assignments array missing");
      return errors;
    }
    if (JSON.stringify(doc.labels) !== JSON.stringify(expected)) {
      errors.push("labels must be the four exact public names, in order");
    }
    if (!doc.filter || doc.filter.within_audience !== "any" || doc.filter.default !== "All") {
      errors.push("filter must default to All and use any/or inside the audience group");
    }
    if (!doc.filter || doc.filter.across_groups !== "and") {
      errors.push("audience must combine with other filter groups using and");
    }
    if (!doc.map || doc.map.audience_filters !== false) {
      errors.push("map audience filters must stay off");
    }
    var seen = {};
    doc.assignments.forEach(function (a) {
      var where = a && (a.notice_id || a.url || "(assignment)");
      if (!a || !a.url) {
        errors.push(where + " needs a source url");
        return;
      }
      if (seen[a.url]) errors.push("duplicate url " + a.url);
      seen[a.url] = 1;
      if (["pending_review", "reviewed", "untagged"].indexOf(a.status) < 0) errors.push(where + " has an unknown status");
      if (!Array.isArray(a.labels)) errors.push(where + " labels must be an array");
      (a.labels || []).forEach(function (label) {
        if (expected.indexOf(label) < 0) errors.push(where + " has an unknown label " + label);
      });
      if (a.labels && new Set(a.labels).size !== a.labels.length) errors.push(where + " repeats a label");
      if (a.method === "keyword") errors.push(where + " keyword guesses are not accepted");
      if (a.status === "untagged" && a.labels && a.labels.length) errors.push(where + " is untagged and must have no labels");
      if (a.status === "pending_review") {
        if (a.approved !== false) errors.push(where + " is pending review and must not be marked approved");
        if (!a.labels || !a.labels.length) errors.push(where + " pending review needs a proposed label");
      }
      if (a.status === "reviewed") {
        if (a.approved !== true) errors.push(where + " reviewed must set approved true");
        if (!a.labels || !a.labels.length) errors.push(where + " reviewed needs a label");
        (a.labels || []).forEach(function (label) {
          if (!a.bases || !String(a.bases[label] || "").trim() || String(a.bases[label]).trim().length < 12) {
            errors.push(where + " reviewed label needs its own basis: " + label);
          }
        });
      }
      if (a.labels && a.labels.length > 1) {
        a.labels.forEach(function (label) {
          if (!a.bases || !String(a.bases[label] || "").trim()) errors.push(where + " needs a separate basis for " + label);
        });
      }
      if (a.integrated_package) {
        ["Equipment", "Engineering & Services"].forEach(function (extra) {
          if (a.labels && a.labels.indexOf(extra) >= 0 && !(a.separate_basis && String(a.separate_basis[extra] || "").trim())) {
            errors.push(where + " is an integrated package and cannot add " + extra + " without a separate basis");
          }
        });
      }
      if (a.withhold && a.labels && a.labels.indexOf(a.withhold) >= 0) errors.push(where + " still includes the withheld label");
      if (a.notice_id === "FR-IDF-FEDER-geothermie-2026" || /FEDER2026_G/.test(a.url || "")) {
        if ((a.labels && a.labels.length) || a.status !== "untagged") {
          errors.push("FEDER must remain untagged until beneficiary evidence is confirmed");
        }
      }
      if (!a.basis || String(a.basis).trim().length < 12) errors.push(where + " needs a written basis");
      if (!Array.isArray(a.provenance) || !a.provenance.length) errors.push(where + " needs provenance");
    });
    return errors;
  }

  return {
    LABELS: LABELS,
    SYMBOLS: SYMBOLS,
    PNG: PNG,
    escapeHtml: escapeHtml,
    audienceMatch: audienceMatch,
    entryMatch: entryMatch,
    badgeHtml: badgeHtml,
    validateAssignments: validateAssignments
  };
});
