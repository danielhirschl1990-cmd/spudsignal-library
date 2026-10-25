/* SpudSignal Tenders – offline cache. Network first, cache fallback. Build 202610251858 */
const C = "ss-tenders-202610251858";
const PRE = ["/tenders/", "/tenders/tenders.json", "/tenders/deadlines.ics", "/tenders/manifest.webmanifest", "/tenders/icon-192.png", "/favicon.svg"];
self.addEventListener("install", e => { e.waitUntil(caches.open(C).then(c => c.addAll(PRE)).catch(() => {})); self.skipWaiting(); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k.startsWith("ss-tenders") && k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin) return;
  e.respondWith(fetch(e.request).then(r => { if (r.ok) { const cp = r.clone(); caches.open(C).then(c => c.put(e.request, cp)); } return r; })
    .catch(() => caches.match(e.request, { ignoreSearch: true }).then(r => r || (e.request.mode === "navigate" ? caches.match("/tenders/") : Response.error()))));
});
