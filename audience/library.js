/* Library audience filter. Reads data-audience written by audience/apply.mjs. */
(function () {
  if (!window.SpudAudience) return;
  var cards = [].slice.call(document.querySelectorAll(".libcard"));
  var buttons = [].slice.call(document.querySelectorAll("#audience-bar .audchip[data-v]"));
  var all = document.getElementById("aud-all");
  var selected = {};

  function labelsOf(card) {
    return (card.getAttribute("data-audience") || "").split("|").filter(Boolean);
  }

  function refresh() {
    var keys = Object.keys(selected);
    cards.forEach(function (card) {
      card.hidden = !window.SpudAudience.audienceMatch(labelsOf(card), keys);
    });
    [].forEach.call(document.querySelectorAll('h2[id^="lib-"]'), function (heading) {
      var node = heading.nextElementSibling;
      var any = false;
      while (node && !(node.tagName === "H2" && node.id && node.id.indexOf("lib-") === 0)) {
        if (node.classList && node.classList.contains("libcard") && !node.hidden) any = true;
        node = node.nextElementSibling;
      }
      heading.hidden = keys.length > 0 && !any;
    });
    if (all) all.setAttribute("aria-pressed", keys.length ? "false" : "true");
    buttons.forEach(function (button) {
      button.setAttribute("aria-pressed", selected[button.dataset.v] ? "true" : "false");
    });
    var shown = cards.filter(function (card) { return !card.hidden; }).length;
    var proposed = cards.filter(function (card) {
      return !card.hidden && card.getAttribute("data-audience-status") === "pending_review";
    }).length;
    var count = document.getElementById("aud-count");
    if (count) {
      var text = keys.length
        ? shown + " of " + cards.length + " sources shown · audience: any of " + keys.join(", ")
        : cards.length + " sources shown · All audiences";
      if (proposed) text += " · " + proposed + " proposed, pending review (not an approved assignment)";
      count.textContent = text;
    }
    var empty = document.getElementById("aud-empty");
    if (empty) empty.hidden = shown > 0;
  }

  buttons.forEach(function (button) {
    button.addEventListener("click", function () {
      var value = button.dataset.v;
      if (selected[value]) delete selected[value];
      else selected[value] = 1;
      refresh();
    });
  });
  if (all) all.addEventListener("click", function () { selected = {}; refresh(); });
  refresh();
})();
