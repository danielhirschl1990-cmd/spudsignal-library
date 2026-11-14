// Opens the 5 pages in headless Chromium, with and without JavaScript, and checks:
// no horizontal scroll at 390 px and 1280 px, no page script errors, tab bar and footer visible,
// Library and Tenders show as many entries as their data, "Skip to content" is the first Tab stop.
// External requests (map tiles, fonts) are blocked so the check needs no network.
// Usage: node .github/scripts/browser_check.mjs [site_dir]
import http from "http";
import fs from "fs";
import path from "path";
import { chromium } from "playwright";

const root = path.resolve(process.argv[2] || ".");
const PAGES = ["/", "/tenders/", "/map/", "/projects/", "/whats-new/"];
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".css": "text/css",
  ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png", ".ics": "text/calendar",
  ".webmanifest": "application/manifest+json" };

const server = http.createServer((req, res) => {
  let p = decodeURIComponent(new URL(req.url, "http://x").pathname);
  if (p.endsWith("/")) p += "index.html";
  const f = path.join(root, p);
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end(); }
  res.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(res);
});
await new Promise((r) => server.listen(0, "127.0.0.1", r));
const base = `http://127.0.0.1:${server.address().port}`;

const errors = [];
const fail = (m) => { errors.push(m); console.log("ERROR " + m); if (process.env.GITHUB_ACTIONS) console.log("::error::" + m); };

const libCount = (fs.readFileSync(path.join(root, "index.html"), "utf8").match(/class="libcard\b/g) || []).length;
const tenderEntries = JSON.parse(fs.readFileSync(path.join(root, "tenders/tenders.json"), "utf8")).entries;
const tenderCount = tenderEntries.length;
// With JS the page hides entries whose deadline has passed; without JS it shows all of them.
const tenderOpen = tenderEntries.filter((e) => !e.deadline_utc || Date.parse(e.deadline_utc) > Date.now()).length;

const browser = await chromium.launch();
for (const js of [true, false]) {
  for (const width of [390, 1280]) {
    const ctx = await browser.newContext({ viewport: { width, height: 900 }, javaScriptEnabled: js });
    await ctx.route("**/*", (route) => route.request().url().startsWith(base) ? route.continue() : route.abort());
    for (const p of PAGES) {
      const page = await ctx.newPage();
      const tag = `${p} (${width}px${js ? "" : ", no JS"})`;
      page.on("pageerror", (e) => fail(`${tag}: script error: ${e.message}`));
      const resp = await page.goto(base + p, { waitUntil: "load" });
      if (!resp || resp.status() !== 200) { fail(`${tag}: HTTP ${resp && resp.status()}`); await page.close(); continue; }
      await page.waitForTimeout(300);
      const r = await page.evaluate(() => ({
        sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
        footer: !!document.querySelector("[data-ss-footer]") && document.querySelector("[data-ss-footer]").offsetHeight > 0,
        tabs: [...document.querySelectorAll('a[href="/whats-new/"]')].some((a) => a.offsetHeight > 0),
        libVisible: [...document.querySelectorAll(".libcard")].filter((c) => !c.hidden && c.offsetHeight > 0).length,
        cards: [...document.querySelectorAll("article.card:not(.gone)")].filter((c) => !c.hidden && c.offsetHeight > 0).length,
      }));
      if (r.sw > r.cw + 1) fail(`${tag}: horizontal scroll (${r.sw}px content in ${r.cw}px)`);
      if (!r.footer) fail(`${tag}: shared footer not visible`);
      if (!r.tabs) fail(`${tag}: no visible link to What's new (tab bar)`);
      if (p === "/" && !js && r.libVisible !== libCount) fail(`${tag}: shows ${r.libVisible} of ${libCount} Library entries`);
      const expected = js ? tenderOpen : tenderCount;
      if (p === "/tenders/" && r.cards !== expected) fail(`${tag}: ${r.cards} tender cards visible, data has ${expected}${js ? " open" : ""}`);
      if (js && width === 1280) {
        await page.keyboard.press("Tab");
        const first = await page.evaluate(() => (document.activeElement && document.activeElement.textContent || "").trim());
        if (!/skip to content/i.test(first)) fail(`${tag}: first Tab stop is "${first.slice(0, 40)}", expected "Skip to content"`);
      }
      await page.close();
    }
    await ctx.close();
  }
}
await browser.close();
server.close();
console.log(errors.length ? `${errors.length} problem(s) found` : "All browser checks passed");
process.exit(errors.length ? 1 : 0);
