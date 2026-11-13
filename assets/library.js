/* Library (home) v2 prototype: audience filter (as live audience/library.js) + search + hide entries whose deadline has passed.
   Without JS: every entry is shown, search and toggle stay hidden (live behaviour). */
(function () {
  if (!window.SpudAudience) return;
  var cards = [].slice.call(document.querySelectorAll(".libcard"));
  var buttons = [].slice.call(document.querySelectorAll("#audience-bar .audchip[data-v]"));
  var all = document.getElementById("aud-all");
  var q = document.getElementById("ss-q"), tog = document.getElementById("ss-past");
  var tools = document.getElementById("ss-tools"); if (tools) tools.hidden = false;
  var selected = {}, now = Date.now();
  cards.forEach(function (c) {
    var d = c.getAttribute("data-deadline");
    var past = c.getAttribute("data-past-build") === "1" || !!(d && Date.parse(d) < now);
    c.classList.toggle("is-past", past);
    var t = c.querySelector(".ss-past"); if (t) t.hidden = !past;
    c._past = past; c._txt = c.textContent.toLowerCase();
  });
  var nPast = cards.filter(function (c) { return c._past; }).length;
  var hc = document.getElementById("ss-hcount");
  function header() {
    if (!hc) return;
    var current = cards.length - nPast, showPast = tog && tog.checked;
    hc.textContent = "";
    if (!nPast) { hc.textContent = cards.length + " entries"; return; }
    hc.appendChild(document.createTextNode(showPast ? cards.length + " entries (" + nPast + " expired shown · " : current + " current entries (" + nPast + " expired hidden · "));
    var b = document.createElement("button"); b.type = "button"; b.className = "ss-hbtn";
    b.textContent = showPast ? "hide" : "show"; b.setAttribute("aria-controls", "liblist");
    b.setAttribute("aria-label", (showPast ? "Hide " : "Show ") + nPast + " expired entries");
    b.addEventListener("click", function () { tog.checked = !tog.checked; refresh(); var nb = hc.querySelector("button"); if (nb) nb.focus(); });
    hc.appendChild(b); hc.appendChild(document.createTextNode(")"));
  }
  var np = document.getElementById("ss-npast"); if (np) np.textContent = nPast;
  function labelsOf(card) { return (card.getAttribute("data-audience") || "").split("|").filter(Boolean); }
  function refresh() {
    var keys = Object.keys(selected), term = q ? q.value.trim().toLowerCase() : "", showPast = tog && tog.checked;
    cards.forEach(function (card) {
      var ok = window.SpudAudience.audienceMatch(labelsOf(card), keys);
      if (ok && term) ok = card._txt.indexOf(term) >= 0;
      if (ok && card._past && !showPast) ok = false;
      card.hidden = !ok;
    });
    [].forEach.call(document.querySelectorAll('h2[id^="lib-"]'), function (heading) {
      var node = heading.nextElementSibling, any = false;
      while (node && !(node.tagName === "H2" && node.id && node.id.indexOf("lib-") === 0)) {
        if (node.classList && node.classList.contains("libcard") && !node.hidden) any = true;
        node = node.nextElementSibling;
      }
      heading.hidden = !any;
    });
    if (all) all.setAttribute("aria-pressed", keys.length ? "false" : "true");
    buttons.forEach(function (b) { b.setAttribute("aria-pressed", selected[b.dataset.v] ? "true" : "false"); });
    var shown = cards.filter(function (c) { return !c.hidden; }).length;
    var count = document.getElementById("aud-count");
    if (count) count.textContent = shown + " of " + cards.length + " entries shown" + (keys.length ? " · audience: any of " + keys.join(", ") : " · All audiences");
    var empty = document.getElementById("aud-empty"); if (empty) empty.hidden = shown > 0;
    header();
  }
  buttons.forEach(function (b) { b.addEventListener("click", function () { var v = b.dataset.v; if (selected[v]) delete selected[v]; else selected[v] = 1; refresh(); }); });
  if (all) all.addEventListener("click", function () { selected = {}; refresh(); });
  if (q) q.addEventListener("input", refresh);
  if (tog) tog.addEventListener("change", refresh);
  refresh();
})();
