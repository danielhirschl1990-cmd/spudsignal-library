/* Renders the Library and tender list in headless Chrome and checks the audience UI. */
import { spawn } from "child_process";
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outDir = "/opt/cursor/artifacts/audience";
fs.mkdirSync(outDir, { recursive: true });
const port = 8765;
const errors = [];

function fail(message) {
  errors.push(message);
  console.error("FAIL", message);
}

function start(cmd, args) {
  const child = spawn(cmd, args, { cwd: root, stdio: ["ignore", "pipe", "pipe"] });
  child.stdout.on("data", (chunk) => process.stdout.write(chunk));
  child.stderr.on("data", (chunk) => process.stderr.write(chunk));
  return child;
}

async function waitFor(url, tries = 40) {
  for (let i = 0; i < tries; i++) {
    try {
      const response = await fetch(url);
      if (response.ok) return;
    } catch (e) { /* retry */ }
    await new Promise((resolve) => setTimeout(resolve, 250));
  }
  throw new Error("Timed out waiting for " + url);
}

function cdp(ws) {
  let seq = 0;
  const pending = new Map();
  ws.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    if (data.id && pending.has(data.id)) {
      const { resolve, reject } = pending.get(data.id);
      pending.delete(data.id);
      if (data.error) reject(new Error(JSON.stringify(data.error)));
      else resolve(data.result);
    }
  });
  return function send(method, params = {}) {
    const id = ++seq;
    ws.send(JSON.stringify({ id, method, params }));
    return new Promise((resolve, reject) => pending.set(id, { resolve, reject }));
  };
}

async function shot(send, file) {
  const { data } = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(path.join(outDir, file), Buffer.from(data, "base64"));
  console.log("saved", file);
}

async function evalIn(send, expression) {
  const result = await send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}

async function openPage(browser, url, width, height) {
  const created = await browser("Target.createTarget", { url: "about:blank" });
  const list = await (await fetch("http://127.0.0.1:9222/json/list")).json();
  const page = list.find((item) => item.id === created.targetId);
  const socket = new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve) => socket.addEventListener("open", resolve));
  const send = cdp(socket);
  await send("Page.enable");
  await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 500 });
  await send("Page.navigate", { url });
  await evalIn(send, `new Promise((resolve) => { if (document.readyState === "complete") resolve(); else window.addEventListener("load", () => resolve()); })`);
  await new Promise((resolve) => setTimeout(resolve, 200));
  return { send, close: () => socket.close() };
}

function assertLayout(name, report) {
  if (report.rowOverflow) fail(name + " audience row scrolls horizontally");
  if (report.chipClipped) fail(name + " audience chip is clipped: " + report.chipClipped);
  for (const label of ["Drilling", "Equipment", "Engineering & Services", "Project owners & developers"]) {
    if (!report.labels.includes(label)) fail(name + " missing visible label " + label);
  }
  if (!report.selectedWord) fail(name + " selected state has no visible Selected word");
}

const server = start("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"]);
const chrome = start("google-chrome", [
  "--headless=new", "--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage",
  "--remote-allow-origins=*", "--remote-debugging-port=9222", "--user-data-dir=/tmp/chrome-audience", "about:blank"
]);

try {
  await waitFor(`http://127.0.0.1:${port}/`);
  await waitFor("http://127.0.0.1:9222/json/version");
  const version = await (await fetch("http://127.0.0.1:9222/json/version")).json();
  const browserSocket = new WebSocket(version.webSocketDebuggerUrl);
  await new Promise((resolve) => browserSocket.addEventListener("open", resolve));
  const browser = cdp(browserSocket);

  async function layout(send) {
    return evalIn(send, `(() => {
      const row = document.querySelector(".audrow");
      const chips = [...document.querySelectorAll(".audchip")];
      const clipped = chips.filter((chip) => {
        const box = chip.getBoundingClientRect();
        return box.right > window.innerWidth + 1 || chip.scrollWidth > chip.clientWidth + 2;
      }).map((chip) => chip.innerText);
      return {
        rowOverflow: row.scrollWidth > row.clientWidth + 2,
        chipClipped: clipped.join(" | "),
        labels: chips.map((chip) => chip.innerText.replace(" · Selected", "").trim()),
        selectedWord: chips.some((chip) => chip.getAttribute("aria-pressed") === "true" && getComputedStyle(chip, "::after").content.includes("Selected"))
      };
    })()`);
  }

  const library = await openPage(browser, `http://127.0.0.1:${port}/`, 1280, 900);
  let report = await layout(library.send);
  assertLayout("library desktop", report);
  const allCount = await evalIn(library.send, `document.getElementById("aud-count").textContent`);
  if (!allCount.includes("92 sources")) fail("library All count: " + allCount);
  await shot(library.send, "library-desktop-all.png");
  await evalIn(library.send, `document.querySelector('.audchip[data-v="Drilling"]').click()`);
  const drilling = await evalIn(library.send, `({
    count: document.getElementById("aud-count").textContent,
    shown: [...document.querySelectorAll(".libcard")].filter((card) => !card.hidden).length,
    title: (document.querySelector('.libcard[data-audience="Drilling"] h3, .libcard[data-audience="Drilling"] a') || {}).textContent || document.querySelector('.libcard[data-audience="Drilling"]').innerText.slice(0, 180),
    pending: document.querySelector('.libcard[data-audience="Drilling"]').innerText.includes("Proposed, pending review"),
    href: document.querySelector('.libcard[data-audience="Drilling"] a').href,
    summary: document.querySelector('.libcard[data-audience="Drilling"]').innerText.includes("hydrogeological tests")
  })`);
  const kutno = await evalIn(library.send, `(() => { const card = document.querySelector('a[href*="725171-2026"]').closest(".libcard"); return { hidden: card.hidden, pending: card.innerText.includes("Proposed, pending review"), label: card.innerText.includes("Drilling") }; })()`);
  if (drilling.shown < 2 || !drilling.count.includes("any of Drilling") || kutno.hidden || kutno.pending || !kutno.label) fail("library Drilling filter " + JSON.stringify({ drilling, kutno }));
  if (!drilling.count.includes("any of Drilling")) fail("library Drilling wording " + drilling.count);
  await evalIn(library.send, `document.querySelector('.libcard[data-audience="Drilling"]').scrollIntoView()`);
  await shot(library.send, "library-desktop-drilling.png");
  await evalIn(library.send, `document.querySelector('.audchip[data-v="Equipment"]').click()`);
  const anyOf = await evalIn(library.send, `({
    count: document.getElementById("aud-count").textContent,
    shown: [...document.querySelectorAll(".libcard")].filter((card) => !card.hidden).map((card) => card.getAttribute("data-audience"))
  })`);
  if (anyOf.shown.length < 3 || !anyOf.count.includes("any of Drilling, Equipment")) fail("library ANY " + JSON.stringify(anyOf));
  await evalIn(library.send, `document.getElementById("audience-bar").scrollIntoView()`);
  await shot(library.send, "library-desktop-any.png");
  await evalIn(library.send, `document.getElementById("aud-all").click(); document.querySelector('.audchip[data-v="Project owners & developers"]').click()`);
  const owners = await evalIn(library.send, `({
    shown: [...document.querySelectorAll(".libcard")].filter((card) => !card.hidden).length,
    empty: !document.getElementById("aud-empty").hidden,
    federHidden: document.querySelector('a[href*="FEDER2026"]').closest(".libcard").hidden,
    federLabel: document.querySelector('a[href*="FEDER2026"]').closest(".libcard").innerText.includes("Project owners & developers"),
    pending: document.body.innerText.includes("Proposed, pending review")
  })`);
  if (owners.shown < 1 || owners.empty || owners.federHidden || !owners.federLabel) fail("library project owners " + JSON.stringify(owners));
  await shot(library.send, "library-desktop-owners.png");
  await library.close();

  const libraryMobile = await openPage(browser, `http://127.0.0.1:${port}/`, 390, 844);
  await evalIn(libraryMobile.send, `document.getElementById("audience-bar").scrollIntoView({block:"start"})`);
  report = await layout(libraryMobile.send);
  assertLayout("library mobile", report);
  await shot(libraryMobile.send, "library-mobile-filters.png");
  await evalIn(libraryMobile.send, `document.querySelector('.audchip[data-v="Drilling"]').click(); document.querySelector('.libcard[data-audience="Drilling"]').scrollIntoView({block:"center"})`);
  const mobileBadge = await evalIn(libraryMobile.send, `(() => {
    const badge = document.querySelector('.libcard[data-audience="Drilling"] .aud');
    const box = badge.getBoundingClientRect();
    return { text: badge.innerText, right: box.right, width: window.innerWidth, clipped: badge.scrollWidth > badge.clientWidth + 2 || box.right > window.innerWidth + 1 };
  })()`);
  if (mobileBadge.text !== "Drilling" || mobileBadge.clipped) fail("library mobile badge " + JSON.stringify(mobileBadge));
  await shot(libraryMobile.send, "library-mobile-drilling.png");
  await libraryMobile.close();

  const tenders = await openPage(browser, `http://127.0.0.1:${port}/tenders/`, 1280, 1000);
  report = await layout(tenders.send);
  assertLayout("tenders desktop", report);
  const openCount = await evalIn(tenders.send, `document.getElementById("count").textContent`);
  if (!openCount.startsWith("33 of 33")) fail("tenders All " + openCount);
  await evalIn(tenders.send, `document.getElementById("bar").scrollIntoView()`);
  await shot(tenders.send, "tenders-desktop-all.png");
  await evalIn(tenders.send, `document.querySelector('.audchip[data-v="Drilling"]').click(); document.querySelector('.chip[data-v="PL"]').click(); document.querySelector('.chip[data-v="Other"]').click()`);
  const combined = await evalIn(tenders.send, `(() => {
    const cards = [...document.querySelectorAll("#list .card")].filter((card) => !card.hidden);
    const card = cards[0];
    return {
      n: cards.length,
      count: document.getElementById("count").textContent,
      href: card.querySelector("h3 a").href,
      deadline: card.innerText.includes("24 Nov 2026, 10:00 CET"),
      reference: card.innerText.includes("TED 725171-2026"),
      technical: card.innerText.includes("Other"),
      audience: card.innerText.includes("Drilling") && !card.innerText.includes("Proposed, pending review") && !card.innerText.includes("Equipment"),
      selected: getComputedStyle(document.querySelector('.audchip[data-v="Drilling"]'), "::after").content.includes("Selected") && getComputedStyle(document.querySelector('.chip[data-v="PL"]'), "::after").content.includes("Selected")
    };
  })()`);
  if (combined.n !== 1 || !combined.deadline || !combined.reference || !combined.href.includes("725171-2026") || !combined.audience || !combined.selected) {
    fail("tenders combined " + JSON.stringify(combined));
  }
  await evalIn(tenders.send, `document.querySelector("#list .card:not([hidden])").scrollIntoView({block:"center"})`);
  await shot(tenders.send, "tenders-desktop-combined.png");
  await evalIn(tenders.send, `document.getElementById("reset").click()`);
  const reset = await evalIn(tenders.send, `({
    count: document.getElementById("count").textContent,
    pressed: [...document.querySelectorAll(".chip[data-g], .audchip[data-g]")].filter((button) => button.getAttribute("aria-pressed") === "true").map((button) => button.innerText),
    all: document.getElementById("reset").getAttribute("aria-pressed"),
    audAll: document.getElementById("aud-all").getAttribute("aria-pressed")
  })`);
  if (!reset.count.startsWith("33 of 33") || reset.pressed.length || reset.all !== "true" || reset.audAll !== "true") fail("tenders reset " + JSON.stringify(reset));
  await shot(tenders.send, "tenders-desktop-reset.png");
  await evalIn(tenders.send, `document.querySelector('.chip[data-v="FR"]').click()`);
  const feder = await evalIn(tenders.send, `(() => {
    const card = document.querySelector('a[href*="FEDER2026"]').closest("article");
    return { hidden: card.hidden, label: card.innerText.includes("Project owners & developers"), pending: card.innerText.includes("Proposed, pending review"), status: card.getAttribute("data-audience-status"), text: card.innerText.includes("16 Nov 2026") };
  })()`);
  if (feder.hidden || !feder.label || feder.pending || feder.status !== "reviewed" || !feder.text) fail("FEDER " + JSON.stringify(feder));
  await evalIn(tenders.send, `document.querySelector('a[href*="FEDER2026"]').closest("article").scrollIntoView({block:"center"})`);
  await shot(tenders.send, "tenders-desktop-feder.png");
  await evalIn(tenders.send, `document.getElementById("reset").click(); document.querySelector('.audchip[data-v="Drilling"]').click(); document.querySelector('.audchip[data-v="Equipment"]').click()`);
  const multi = await evalIn(tenders.send, `document.getElementById("count").textContent`);
  if (!multi.includes("any of Drilling, Equipment") || multi.startsWith("33 of 33")) fail("tenders ANY " + multi);
  await evalIn(tenders.send, `document.querySelector('a[href="#soon"]').click()`);
  const soon = await evalIn(tenders.send, `document.getElementById("count").textContent`);
  if (!soon.includes("closing within 14 days")) fail("closing soon lost " + soon);
  await tenders.close();

  const tendersMobile = await openPage(browser, `http://127.0.0.1:${port}/tenders/`, 390, 844);
  report = await layout(tendersMobile.send);
  assertLayout("tenders mobile", report);
  await evalIn(tendersMobile.send, `document.getElementById("bar").scrollIntoView()`);
  await shot(tendersMobile.send, "tenders-mobile-filters.png");
  await tendersMobile.close();

  const mapPage = await openPage(browser, `http://127.0.0.1:${port}/map/`, 1280, 900);
  await evalIn(mapPage.send, `new Promise((resolve) => setTimeout(resolve, 900))`);
  const mapState = await evalIn(mapPage.send, `(() => {
    const read = () => document.getElementById("count").textContent;
    const markers = () => window.SSLAYER.getLayers().length;
    const before = read();
    const beforeN = markers();
    document.querySelector('#audrow [data-v="Drilling"]').click();
    const drilled = read();
    const drilledN = markers();
    document.getElementById("aud-all").click();
    const restored = read();
    document.getElementById("clearf").click();
    return { before, beforeN, drilled, drilledN, restored, cleared: read(), markers: markers() };
  })()`);
  if (!mapState.before.endsWith("pins shown") || mapState.beforeN < 10 || mapState.drilledN >= mapState.beforeN || !mapState.drilled.includes("any of Drilling") || mapState.restored !== mapState.before || mapState.cleared !== mapState.before) {
    fail("map audience filter " + JSON.stringify(mapState));
  }
  await evalIn(mapPage.send, `document.querySelector('#audrow [data-v="Drilling"]').click()`);
  await shot(mapPage.send, "map-desktop-drilling.png");
  await mapPage.close();
  const mapMobile = await openPage(browser, `http://127.0.0.1:${port}/map/`, 390, 844);
  await evalIn(mapMobile.send, `document.getElementById("tog").click(); document.getElementById("panel").classList.add("open")`);
  const mapLayout = await evalIn(mapMobile.send, `(() => {
    const row = document.getElementById("audrow");
    const chips = [...row.querySelectorAll("button")];
    return {
      overflow: row.scrollWidth > row.clientWidth + 2,
      labels: chips.map((chip) => chip.innerText.replace(" · Selected", "").trim()),
      short: chips.some((chip) => chip.innerText.includes("Eng.") || chip.innerText.includes("Owners &"))
    };
  })()`);
  if (mapLayout.overflow || mapLayout.short || !mapLayout.labels.includes("Project owners & developers")) fail("map mobile " + JSON.stringify(mapLayout));
  await shot(mapMobile.send, "map-mobile-filters.png");
  await mapMobile.close();

  const preview = await openPage(browser, `http://127.0.0.1:${port}/audience/preview.html`, 390, 800);
  const wrapped = await evalIn(preview.send, `(() => {
    const sample = document.querySelector(".layout-sample .auds");
    const names = [...sample.querySelectorAll(".audname")].map((node) => node.innerText);
    const box = sample.getBoundingClientRect();
    return { names, clipped: box.right > window.innerWidth + 1, height: sample.getBoundingClientRect().height };
  })()`);
  if (wrapped.names.join("|") !== "Drilling|Engineering & Services" || wrapped.clipped || wrapped.height < 40) fail("preview wrap " + JSON.stringify(wrapped));
  await shot(preview.send, "preview-mobile-two-labels.png");
  await preview.close();

  const newsletter = await openPage(browser, `http://127.0.0.1:${port}/audience/newsletter-item.html`, 640, 1100);
  await shot(newsletter.send, "newsletter-with-symbols.png");
  const blocked = await evalIn(newsletter.send, `(() => {
    document.querySelectorAll("img").forEach((img) => { img.style.display = "none"; });
    const text = document.body.innerText;
    return {
      forDrilling: text.includes("For:") && text.includes("Drilling"),
      equipment: text.includes("Equipment"),
      engineering: text.includes("Engineering & Services"),
      owners: text.includes("Project owners & developers"),
      pending: text.includes("Proposed, pending review"),
      feder: text.includes("Project owners & developers"),
      notEdited: text.includes("was not edited"),
      notReady: text.includes("not ready to paste into Beehiiv")
    };
  })()`);
  if (!blocked.forDrilling || !blocked.equipment || !blocked.engineering || !blocked.owners || blocked.pending || !blocked.feder || !blocked.notEdited || !blocked.notReady) {
    fail("newsletter images blocked " + JSON.stringify(blocked));
  }
  await shot(newsletter.send, "newsletter-images-blocked.png");
  await newsletter.close();

  browserSocket.close();
} finally {
  server.kill("SIGTERM");
  chrome.kill("SIGTERM");
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}
console.log("browser checks passed");
