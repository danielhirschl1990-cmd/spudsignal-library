#!/usr/bin/env python3
"""Builds site/tenders/index.html (+ tenders.json, manifest) for library.spudsignal.com.

Data rules (strategie/lizenzpruefung-2026-10-23.md):
- Reviewed allowlist = notice URLs that appeared in a published, reviewed issue (pipeline/issue_*_final_content.py),
  excluding rows marked as awarded. Fields (verbatim title, buyer, country, deadline, CPV) come from the raw
  pipeline API pulls in data/w*/ (TED API v3, BOAMP/simap/ANAC national.json, UK FTS). Never from news/RSS.
- Funding calls: data/funding_watchlist.json entries with verified=true (original programme pages) plus
  EU F&T topics that appeared in a reviewed issue (data/w*/eu_funding.json).
- Only deadline in the future (Europe/Berlin "now"); no awards, no contacts, no full texts, no logos.
- Every run: live correction check per entry (TED: all notices of the same procedure-identifier; BOAMP: annonce_lie
  rectificatifs/attributions). Deadline changes are adopted automatically where machine-readable, otherwise marked.
  Entries not successfully checked within 7 days are removed (state: tenders/checks.json).
- Manual review fixes: tenders/overrides.json (survive the weekly rebuild).
Usage: python3 tenders/build_tenders.py [--today YYYY-MM-DD] [--offline]   (run from library/, after build_site.py)
"""
import json, glob, re, os, sys, html, datetime as dt
from zoneinfo import ZoneInfo
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))   # /workspace/geothermie
LIB = os.path.join(ROOT, "library"); OUT = os.path.join(LIB, "site", "tenders")
TZ = ZoneInfo("Europe/Berlin")
now = dt.datetime.now(TZ)
if "--today" in sys.argv: now = dt.datetime.fromisoformat(sys.argv[sys.argv.index("--today")+1]).replace(tzinfo=TZ)
ACCESS_NOTE = "As published by source, no guarantee – check the original."
ISO3 = {"ROU":"RO","DEU":"DE","FRA":"FR","CHE":"CH","HUN":"HU","ISL":"IS","CZE":"CZ","POL":"PL","IRL":"IE","ITA":"IT","BEL":"BE","GBR":"UK","AUT":"AT","NLD":"NL","ESP":"ES","PRT":"PT","SVK":"SK","HRV":"HR","SVN":"SI","DNK":"DK","SWE":"SE","FIN":"FI","NOR":"NO","GRC":"GR","TUR":"TR","SRB":"RS","BGR":"BG","LTU":"LT","LVA":"LV","EST":"EE"}
CN = {"RO":"Romania","DE":"Germany","FR":"France","CH":"Switzerland","HU":"Hungary","IS":"Iceland","CZ":"Czechia","PL":"Poland","IE":"Ireland","IT":"Italy","BE":"Belgium","UK":"United Kingdom","NL":"Netherlands","AT":"Austria","EU":"EU-wide","SK":"Slovakia","HR":"Croatia","ES":"Spain","PT":"Portugal","DK":"Denmark","SE":"Sweden","SI":"Slovenia","TR":"Türkiye","RS":"Serbia","UA":"Ukraine"}
SRC = {"TED":"TED (EU)","BOAMP":"BOAMP (DILA)","simap":"simap.ch","ANAC":"ANAC","FTS":"UK Find a Tender","EUFT":"EU Funding & Tenders Portal","PROG":"Programme page"}

# ---- 1. reviewed allowlist from published issues
allow = {}   # url -> issue no
award_urls = set()
for f in sorted(glob.glob(os.path.join(ROOT, "pipeline", "issue_[0-9]*_final_content.py"))):
    n = int(re.search(r"issue_(\d+)_", f).group(1)); txt = open(f, encoding="utf-8").read()
    for line in txt.splitlines():
        for u in re.findall(r'(?:TED \+ "|BOAMP \+ "|["\'])((?:https?://)?[^"\']*?(?:\d{5,6}-20\d\d|\d\d-\d{5,6}|simap\.ch/[^"\']+|anticorruzione\.it/[^"\']+|find-tender[^"\']+|topic-details/[^"\']+))["\']', line):
            if 'TED + "' + u in line: u = "https://ted.europa.eu/en/notice/-/detail/" + u
            elif 'BOAMP + "' + u in line: u = "https://www.boamp.fr/pages/avis/?q=idweb:" + u
            if not u.startswith("http"): continue
            if re.search(r"\bAwarded\b|ATTRIBUTION|\baward\b", line): award_urls.add(u)
            allow.setdefault(u, n)
allow = {u: n for u, n in allow.items() if u not in award_urls}

# ---- 2. raw records (latest week wins)
weeks = sorted(glob.glob(os.path.join(ROOT, "data", "w*")))
raw = {}
def put(url, rec): raw[url] = rec
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
import boamp_time
def boamp_iso(x):
    """Resolved BOAMP deadline (pipeline/boamp_time.py rule): the raw FNS/MAPA clock time is Europe/Paris local time,
    whether it carries no zone or a misleading 'Z' (fix 13 Nov 2026, Croze 26-103155: 12:00Z had been read as UTC = 13:00 Paris).
    national.json from 13 Nov on stores the resolved value as deadline_iso; older week files are resolved here from deadline_basis."""
    if x.get("deadline_iso"): return x["deadline_iso"]
    r, basis = x.get("deadline_raw"), x.get("deadline_basis") or ""
    if r and (basis.startswith("local Paris clock") or basis.startswith("fallback: API clock as Paris")):
        d = boamp_time._paris_clock(r); return d.isoformat() if d else r
    return r
for w in weeks:
    acc = "2026-" + os.path.basename(w)[1:3] + "-" + os.path.basename(w)[3:5]
    for p in sorted(glob.glob(os.path.join(w, "ted*.json")), key=lambda q: q.endswith("/ted.json")):
        for x in json.load(open(p)).get("notices", []):
            if x.get("winners") or str(x.get("type","")).startswith("can"): continue
            dl = [d for d in x.get("deadlines", []) if d.get("iso")]
            put("https://ted.europa.eu/en/notice/-/detail/" + x["id"], dict(src="TED", id="TED " + x["id"], title=x["title"], buyer=x["buyer"], bproc=x.get("procedure_id"),
                country=ISO3.get(x.get("country"), x.get("country")), deadline_iso=dl[0]["iso"] if dl else None, deadline_txt=dl[0]["cet"] if dl else None,
                deadline_kind=dl[0]["kind"] if dl else None, cpv=x.get("cpv", []), procedure=x.get("procedure_type"), proc_id=x.get("procedure_id"), published=x.get("date"), accessed=acc, kind="tender"))
    p = os.path.join(w, "national.json")
    if os.path.exists(p):
        for x in json.load(open(p)).get("items", []):
            if x.get("portal") == "BOAMP": x["deadline_raw"] = boamp_iso(x)
            if x.get("type") in ("award", "RISULTATI") or (x.get("extra") or {}).get("titulaire") or (x.get("extra") or {}).get("award"): continue
            put(x["url"], dict(src=x["portal"], id=x["portal"] + " " + x["id"], title=x["title"], buyer=x["buyer"], country=x["country"],
                deadline_iso=x.get("deadline_raw"), deadline_txt=x.get("deadline_cet"), deadline_kind=x.get("deadline_kind"), cpv=[], procedure=x.get("procedure"),
                published=x.get("date"), accessed=acc, kind="tender"))
    p = os.path.join(w, "fts.json")
    if os.path.exists(p):
        for x in json.load(open(p)).get("hits", []):
            if "award" in (x.get("tag") or []): continue
            u = "https://www.find-tender.service.gov.uk/Notice/" + x["id"]
            put(u, dict(src="FTS", id="FTS " + x["id"], title=x["title"], buyer=x["buyer"], country="UK", deadline_iso=x.get("deadline"), deadline_txt=x.get("deadline"),
                deadline_kind="tender submission", cpv=x.get("cpv", []) or [], procedure=None, published=x.get("date"), accessed=acc, kind="tender"))
    p = os.path.join(w, "eu_funding.json")
    if os.path.exists(p):
        for x in json.load(open(p)).get("calls", []):
            put(x["url"], dict(src="EUFT", id=x["id"], title=x["title"], buyer="European Commission (" + x.get("call", "") + ")", country="EU",
                deadline_iso=(sorted(x.get("deadlines") or [None])[-1]), deadline_txt=", ".join(x.get("deadlines") or []) + " (per portal; stage times on the topic page)",
                deadline_kind="submission", cpv=[], procedure=x.get("deadline_model"), published=x.get("opening"), accessed=acc, kind="funding"))

def parse(iso):
    if not iso: return None
    try:
        d = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError: return None
    if d.tzinfo is None: d = d.replace(tzinfo=TZ)
    if len(iso) == 10: d = d.replace(hour=23, minute=59)
    return d

# run/check date for funding entries: pipeline 'fetched_at' if present, else min(newest week folder date, today). Never in the future.
_fa = []
for w in weeks:
    for fn in ("eu_funding.json", "funding_deadlines.json"):
        p = os.path.join(w, fn)
        if os.path.exists(p): _fa.append((json.load(open(p)).get("fetched_at") or "")[:10])
_fa = [x for x in _fa if x]
PIPE_RUN = max(_fa) if _fa else max(("2026-" + os.path.basename(w)[1:3] + "-" + os.path.basename(w)[3:5]) for w in weeks)
PIPE_RUN = min(PIPE_RUN, now.date().isoformat())
entries, skipped = [], []
for u, n in allow.items():
    r = raw.get(u)
    if not r: skipped.append((u, "no raw API record (not shown)")); continue
    d = parse(r["deadline_iso"])
    if not d: skipped.append((u, "no deadline in source data")); continue
    if d <= now: skipped.append((u, "deadline passed " + str(r["deadline_txt"]))); continue
    entries.append(dict(r, url=u, issue=n, key=u))

# ---- 3. verified funding watchlist (original programme pages)
wl = json.load(open(os.path.join(ROOT, "data", "funding_watchlist.json")))
fchk = {}
for w in weeks:
    p = os.path.join(w, "funding_deadlines.json")
    if os.path.exists(p):
        for c in json.load(open(p)).get("candidates", []):
            if c.get("status") == "CONFIRMED" and c.get("checked"): fchk[c["id"]] = c["checked"]
for c in wl["calls"]:
    if not c.get("verified"): continue
    d = parse(c.get("deadline_date"))
    if not d or d <= now: continue
    entries.append(dict(src="PROG", id=c["id"], title=c["call"], buyer=c["programme"], country=c["region"], deadline_iso=c["deadline_date"],
        deadline_txt=c["deadline_as_stated"], deadline_kind="submission", cpv=[], procedure=None, published=None, accessed=c["last_verified"],
        kind="funding", url=c["url"], issue=None, key=c["id"], checked=fchk.get(c["id"], c["last_verified"])))

# same TED procedure (original + change notices): keep only the latest notice
byproc = {}
for e in entries:
    if e.get("proc_id"):
        k = e["proc_id"]
        if k not in byproc or (e["published"] or "") > (byproc[k]["published"] or ""): byproc[k] = e
for e in list(entries):
    if e.get("proc_id") and byproc[e["proc_id"]] is not e:
        entries.remove(e); skipped.append((e["url"], "superseded by later notice " + byproc[e["proc_id"]]["id"]))
seen = set(); uniq = []
for e in sorted(entries, key=lambda e: e["deadline_iso"]):
    if e["url"] in seen: continue
    seen.add(e["url"]); uniq.append(e)
entries = uniq

# ---- 3b. live correction check (TED procedure / BOAMP annonce_lie); state in checks.json
import urllib.request, urllib.parse
sys.path.insert(0, os.path.join(ROOT, "pipeline"))
CHK_P = os.path.join(os.path.dirname(__file__), "checks.json")
chk = json.load(open(CHK_P)) if os.path.exists(CHK_P) else {}
OFFLINE = "--offline" in sys.argv
today = now.date().isoformat()
def ted_check(e):
    from tedlib import search, texts, deadlines
    F = ["publication-number", "notice-type", "publication-date", "buyer-name", "deadline-receipt-tender-date-lot", "deadline-receipt-tender-time-lot", "BT-1311(d)-Lot", "BT-1311(t)-Lot"]
    ns = search(f'procedure-identifier="{e["proc_id"]}"', F, limit=50).get("notices", [])
    if not ns: raise RuntimeError("procedure not found")
    ns.sort(key=lambda n: (n.get("publication-date", ""), n["publication-number"]))
    res = {"notices": [n["publication-number"] for n in ns]}
    if any(str(n.get("notice-type", "")).startswith(("can", "veat")) for n in ns): res["award"] = True
    last = ns[-1]; res["buyers"] = list(dict.fromkeys(texts(last.get("buyer-name"))))
    if last["publication-number"] != e["id"].split()[-1] and str(last.get("notice-type", "")).startswith(("cn", "pin", "corr")):
        dl = deadlines(last)
        res["newer"] = last["publication-number"]; res["newer_date"] = str(last.get("publication-date", ""))[:10]
        if dl: res.update(deadline_iso=dl[0]["iso"], deadline_txt=dl[0]["cet"], deadline_kind=dl[0]["kind"])
    return res
def boamp_check(e):
    idw = e["id"].split()[-1]
    q = urllib.parse.urlencode({"where": f'annonce_lie="{idw}"', "select": "idweb,nature,dateparution,donnees", "limit": 50})
    d = json.load(urllib.request.urlopen(urllib.request.Request("https://boamp-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets/boamp/records?" + q, headers={"User-Agent": "spudsignal-library/1.0"}), timeout=60))
    res = {"linked": []}
    for r in sorted(d.get("results", []), key=lambda r: r["dateparution"]):
        res["linked"].append(r["idweb"] + " " + str(r["nature"]))
        if "ATTRIBUTION" in str(r["nature"]).upper(): res["award"] = True
        if "RECTIF" in str(r["nature"]).upper():
            info = json.dumps(json.loads(r.get("donnees") or "{}"), ensure_ascii=False)
            m = re.search(r"limites? de r\\u00e9ception|limites? de réception", info)
            n = re.search(r"lire (\d\d)/(\d\d)/(\d{4}) à (\d\d)h(\d\d)", info)
            if m and n:
                dd, mm, yy, hh, mi = n.groups()
                loc = dt.datetime(int(yy), int(mm), int(dd), int(hh), int(mi), tzinfo=ZoneInfo("Europe/Paris"))
                res.update(deadline_iso=loc.isoformat(), deadline_txt=loc.strftime("%d %b %Y, %H:%M ") + ("CEST" if loc.dst() else "CET") + f" (Paris time; rectificatif {r['idweb']})", newer=r["idweb"], newer_date=r["dateparution"])
            elif "lire" in info:
                res.setdefault("rectif_other", []).append(r["idweb"])
    return res
OVE = json.load(open(os.path.join(os.path.dirname(__file__), "overrides.json")))["entries"]
for e in list(entries):
    k = e["key"]; st = chk.get(k, {})
    if e["src"] in ("TED", "BOAMP") and not OFFLINE:
        try:
            st = {"last_checked": today, "result": ted_check(e) if e["src"] == "TED" else boamp_check(e)}
            chk[k] = st
        except Exception as ex:
            print("  CHECK FAILED", k, ex); st = dict(st, last_error=f"{today}: {ex}"); chk[k] = st
    elif e["src"] in ("PROG", "EUFT"):
        st = {"last_checked": e.get("checked") or PIPE_RUN, "result": {"via": "funding_deadlines.py" if e["src"] == "PROG" else "eu_funding_pull.py"}}
        chk[k] = st
    lc = max(filter(None, [st.get("last_checked"), OVE.get(k, {}).get("manual_check")]), default=None)
    if not lc or (now.date() - dt.date.fromisoformat(lc)).days > 7:
        entries.remove(e); skipped.append((e["url"], f"not checked within 7 days (last {lc}; no automated follow-up check for {e['src']})" if e["src"] not in ("TED","BOAMP") else f"not checked within 7 days (last {lc})")); continue
    lc = min(lc, today)   # guard: no check/accessed date after today
    r = st.get("result", {}); e["checked"] = lc
    if r.get("award"): entries.remove(e); skipped.append((e["url"], "award/attribution notice found")); continue
    if r.get("buyers"): e["buyer"] = " · ".join(r["buyers"])
    if r.get("newer"):
        if r.get("deadline_iso"):
            if parse(r["deadline_iso"]) != parse(e["deadline_iso"]):
                nurl = ("https://ted.europa.eu/en/notice/-/detail/" if e["src"] == "TED" else "https://www.boamp.fr/pages/avis/?q=idweb:") + r["newer"]
                e["published"] = r.get("newer_date") or e.get("published"); e["change"] = {"date": r.get("newer_date") or today, "field": "deadline", "old": e["deadline_txt"], "old_iso": e["deadline_iso"], "notice": r["newer"], "notice_url": nurl}
            e.update(deadline_iso=r["deadline_iso"], deadline_txt=r["deadline_txt"] + (f" (updated; TED {r['newer']})" if e["src"] == "TED" else ""))
            if r.get("deadline_kind"): e["deadline_kind"] = r["deadline_kind"]
        else: e["flag"] = f"Newer notice {r['newer']} found – not yet reviewed, check the original."
        if e["src"] == "TED": e["url"] = "https://ted.europa.eu/en/notice/-/detail/" + r["newer"]; e["id"] = "TED " + r["newer"] + " (orig. " + e["id"].split()[-1] + ")"
        else: e["id"] += " + rectificatif " + r["newer"]
    ack = OVE.get(e["key"], {}).get("ack_rectif", [])
    if [x for x in r.get("rectif_other", []) if x not in ack]: e["flag"] = "Correction notice(s) " + ", ".join(x for x in r["rectif_other"] if x not in ack) + " published – check the original."
json.dump(chk, open(CHK_P, "w"), ensure_ascii=False, indent=1)

# ---- 3c. manual overrides (review)
OV = json.load(open(os.path.join(os.path.dirname(__file__), "overrides.json")))
for e in list(entries):
    o = OV["entries"].get(e["key"], {})
    if "drop" in o: entries.remove(e); skipped.append((e["url"], "override drop: " + o["drop"])); continue
    for f in ("title", "buyer", "deadline_txt", "deadline_iso", "url", "deadline_label", "tags", "title_official", "time_note"):
        if f in o: e[f] = o[f]
    if e["src"] == "PROG" and "title_official" not in e: e["title_official"] = False
    if (e.get("deadline_kind") or "").startswith("request") and "deadline_label" not in e: e["deadline_label"] = "Requests to participate"
    e.setdefault("tags", [] if e["kind"] == "funding" else ["Other"])
    d = parse(e["deadline_iso"])
    if d <= now: entries.remove(e); skipped.append((e["url"], "deadline passed (after corrections) " + e["deadline_txt"]))
entries.sort(key=lambda e: parse(e["deadline_iso"]))

# ---- 4. feed state (first_seen / changes / ICS UID+SEQUENCE), persisted in checks.json["_feed"]
import hashlib
def fmt_access(d): return dt.date.fromisoformat(d).strftime('%d %b %Y') if d else ''
TZC = {"FR":"Europe/Paris","DE":"Europe/Berlin","CZ":"Europe/Prague","SE":"Europe/Stockholm","CH":"Europe/Zurich","IE":"Europe/Dublin","PL":"Europe/Warsaw",
       "RO":"Europe/Bucharest","HU":"Europe/Budapest","NL":"Europe/Amsterdam","EU":"Europe/Brussels","UK":"Europe/London","IT":"Europe/Rome","AT":"Europe/Vienna",
       "BE":"Europe/Brussels","IS":"Atlantic/Reykjavik","SK":"Europe/Bratislava","HR":"Europe/Zagreb","SI":"Europe/Ljubljana","ES":"Europe/Madrid","PT":"Europe/Lisbon","DK":"Europe/Copenhagen"}
feed = chk.setdefault("_feed", {})
cur = set()
for e in entries:
    uid = hashlib.sha1(e["key"].encode()).hexdigest()[:16]; e["uid"] = uid; cur.add(uid)
    e["tz"] = TZC.get(e["country"], "Europe/Brussels")
    if len(e["deadline_iso"]) == 10:   # no time stated: end of day in the official zone, never browser-local
        e["deadline_iso"] = dt.datetime.fromisoformat(e["deadline_iso"] + "T23:59:00").replace(tzinfo=ZoneInfo(e["tz"])).isoformat()
        e.setdefault("time_note", "No time stated – end of day (23:59 local time) assumed; submit earlier to be safe.")
    if e.get("change"): e["change"]["new"] = e["deadline_txt"]
    sig = json.dumps([e["deadline_iso"], e["title"], e["url"], e["deadline_txt"], e.get("time_note")], ensure_ascii=False)
    f = feed.get(uid)
    if not f:
        f = feed[uid] = {"key": e["key"], "first_seen": today, "seq": 0, "sig": sig}
    elif f.get("sig") != sig or f.get("status") == "CANCELLED":
        f["seq"] = f.get("seq", 0) + 1; f["sig"] = sig; f.pop("status", None); f.pop("gone", None)
    if e.get("change"): f["change"] = e["change"]
    elif f.get("change") and (now.date() - dt.date.fromisoformat(f["change"]["date"])).days <= 14: e["change"] = f["change"]
    f["last"] = {k: e.get(k) for k in ("title", "url", "deadline_iso", "deadline_txt", "deadline_label", "src", "id", "country", "checked", "kind")}
    f["last"]["tz"] = e["tz"]; f["last"]["published"] = (e.get("published") or "")[:10] or None; f["last"]["time_note"] = e.get("time_note")
    if f.get("mod_seq") != f["seq"]: f["mod"] = now.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); f["mod_seq"] = f["seq"]
    e["first_seen"] = f["first_seen"]; e["seq"] = f["seq"]
cancelled = []
for uid, f in list(feed.items()):
    if uid in cur: continue
    if f.get("status") != "CANCELLED":
        why = next((w for u2, w in skipped if u2 in (f["key"], f.get("last", {}).get("url"))), "no longer listed (not re-verifiable or withdrawn)")
        f["status"] = "CANCELLED"; f["gone"] = today; f["seq"] = f.get("seq", 0) + 1; f["reason"] = why
        f["mod"] = now.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"); f["mod_seq"] = f["seq"]
    if (now.date() - dt.date.fromisoformat(f["gone"])).days > 30: del feed[uid]; continue
    cancelled.append((uid, f))
json.dump(chk, open(CHK_P, "w"), ensure_ascii=False, indent=1)

# ---- 5. ICS (feed + one file per entry)
SRCLONG = {"TED":"TED","BOAMP":"BOAMP","simap":"simap.ch","ANAC":"ANAC","FTS":"UK Find a Tender","EUFT":"EU Funding & Tenders Portal","PROG":"the programme page"}
SIMAP_NOTE = "Dies ist keine amtliche Veröffentlichung. Massgebend sind die auf der Plattform www.simap.ch veröffentlichten Daten."
def vtz(tzid):
    z = ZoneInfo(tzid); y = now.year
    std = dt.datetime(y, 1, 15, tzinfo=z).utcoffset(); dst = dt.datetime(y, 7, 15, tzinfo=z).utcoffset()
    o = lambda td: ("+" if td >= dt.timedelta(0) else "-") + f"{abs(int(td.total_seconds()))//3600:02d}{abs(int(td.total_seconds()))%3600//60:02d}"
    loc_h = lambda td: f"{(1 + int(td.total_seconds())//3600) % 24:02d}"   # EU switch at 01:00 UTC
    out = [f"BEGIN:VTIMEZONE", f"TZID:{tzid}"]
    if std != dst:
        out += ["BEGIN:DAYLIGHT", f"TZOFFSETFROM:{o(std)}", f"TZOFFSETTO:{o(dst)}", f"DTSTART:19700329T{loc_h(std)}0000", "RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU", "END:DAYLIGHT",
                "BEGIN:STANDARD", f"TZOFFSETFROM:{o(dst)}", f"TZOFFSETTO:{o(std)}", f"DTSTART:19701025T{loc_h(dst)}0000", "RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU", "END:STANDARD"]
    else:
        out += ["BEGIN:STANDARD", f"TZOFFSETFROM:{o(std)}", f"TZOFFSETTO:{o(std)}", "DTSTART:19700101T000000", "END:STANDARD"]
    return out + ["END:VTIMEZONE"]
def esc(t): return str(t).replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
def fold(line):
    b = line.encode("utf-8"); out = []
    while len(b) > 74:
        cut = 74
        while (b[cut] & 0xC0) == 0x80 or b[cut-1] == 92: cut -= 1
        out.append(b[:cut].decode()); b = b" " + b[cut:]
    out.append(b.decode()); return "\r\n".join(out)
def vevent(L, uid, seq, status, feed_mode, changed, reason=None, mod=None):
    d = parse(L["deadline_iso"]); tzid = L["tz"]; dateonly = len(L["deadline_iso"]) == 10
    src = L["id"] if str(L["id"]).startswith(L["src"]) else f'{SRCLONG.get(L["src"], L["src"])}, {L["id"]}'
    chkd = fmt_access(min(L.get("checked") or today, today))
    pubd = ("page as of " + chkd) if L["src"] in ("PROG",) else (fmt_access(L["published"]) if L.get("published") else "see original")
    upd = ("This calendar feed is refreshed by SpudSignal on each weekly check, but your calendar app may show changes with a delay."
           if feed_mode else "This calendar entry does NOT update itself. For automatic updates, subscribe to the feed: https://library.spudsignal.com/tenders/deadlines.ics.")
    desc = (f'Source: {src}. Published by source: {pubd} · Last checked by SpudSignal: {chkd}. Deadlines can change through corrigenda. {upd} '
            f'Only the original notice is binding: {L["url"]}. No guarantee of completeness or accuracy.')
    if reason: desc = f"CANCELLED – removed from the SpudSignal list on {fmt_access(reason[1])}: {reason[0]}. " + desc
    if L.get("time_note"): desc += " " + L["time_note"]
    if L["src"] == "simap": desc += " " + SIMAP_NOTE
    desc += f' As published: {L["deadline_txt"].rstrip(".")}.'
    pre = ("[CANCELLED] " if status == "CANCELLED" else "[CHANGED] " if (changed and feed_mode) else "")
    lab = "Requests to participate" if (L.get("deadline_label") or "").startswith("Requests") else "Deadline"
    ev = ["BEGIN:VEVENT", f"UID:{uid}@library.spudsignal.com", f"SEQUENCE:{seq}", "DTSTAMP:" + now.astimezone(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
          *([f"LAST-MODIFIED:{mod}"] if mod else []), f"SUMMARY:{esc(pre + '[Check source] ' + lab + ': ' + L['title'][:150])}"]
    if dateonly:
        dd = dt.date.fromisoformat(L["deadline_iso"]); ev += [f"DTSTART;VALUE=DATE:{dd:%Y%m%d}", f"DTEND;VALUE=DATE:{dd + dt.timedelta(days=1):%Y%m%d}"]
    else:
        loc = d.astimezone(ZoneInfo(tzid)); ev += [f"DTSTART;TZID={tzid}:{loc:%Y%m%dT%H%M%S}", f"DTEND;TZID={tzid}:{loc + dt.timedelta(minutes=30):%Y%m%dT%H%M%S}"]
    ev += [f"DESCRIPTION:{esc(desc)}", f"URL:{L['url']}", f"STATUS:{status}", "TRANSP:TRANSPARENT"]
    for trg in ("-P7D", "-P1D"):
        ev += ["BEGIN:VALARM", "ACTION:DISPLAY", f"TRIGGER:{trg}", "DESCRIPTION:Re-check the deadline on the original notice before submitting", "END:VALARM"]
    return ev + ["END:VEVENT"]
def cal(events, tzids, name):
    L = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//SpudSignal//Tender deadlines//EN", "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
         f"X-WR-CALNAME:{name}", "X-WR-TIMEZONE:Europe/Brussels", "REFRESH-INTERVAL;VALUE=DURATION:PT12H", "X-PUBLISHED-TTL:PT12H"]
    for t in sorted(tzids): L += vtz(t)
    return "\r\n".join(fold(x) for x in L + events + ["END:VCALENDAR"]) + "\r\n"
os.makedirs(os.path.join(OUT, "ics"), exist_ok=True)
for f in glob.glob(os.path.join(OUT, "ics", "*.ics")): os.remove(f)
fe, tz_used = [], set()
for e in entries:
    L = dict(feed[e["uid"]]["last"], time_note=e.get("time_note")); tz_used.add(e["tz"])
    m = feed[e["uid"]].get("mod")
    fe += vevent(L, e["uid"], e["seq"], "CONFIRMED", True, bool(e.get("change")), mod=m)
    open(os.path.join(OUT, "ics", e["uid"] + ".ics"), "w", newline="").write(cal(vevent(L, e["uid"], e["seq"], "CONFIRMED", False, False, mod=m), {e["tz"]}, "SpudSignal deadline"))
for uid, f in cancelled:
    tz_used.add(f["last"]["tz"]); fe += vevent(f["last"], uid, f["seq"], "CANCELLED", True, False, reason=(f.get("reason", "no longer listed"), f["gone"]), mod=f.get("mod"))
open(os.path.join(OUT, "deadlines.ics"), "w", newline="").write(cal(fe, tz_used, "SpudSignal – geothermal tender & funding deadlines"))

# ---- 6. JSON + page
os.makedirs(OUT, exist_ok=True)
FIELDS = ("uid","kind","src","id","title","title_official","buyer","country","tz","deadline_iso","deadline_utc","deadline_txt","deadline_label","time_note","tags","cpv","url","checked","flag","first_seen","change")
assert all(e["checked"] <= today for e in entries), "future check date"
for e in entries:   # absolute instant for client-side auto-expiry; a deadline without offset is read in the official zone (same rule as the countdown/ICS)
    _d = dt.datetime.fromisoformat(e["deadline_iso"].replace("Z", "+00:00"))
    if _d.tzinfo is None: _d = _d.replace(tzinfo=ZoneInfo(e["tz"]))
    e["deadline_utc"] = _d.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
pub = [dict({k: e.get(k) for k in FIELDS}, accessed=e["checked"]) for e in entries]
gone = [dict(uid=u, status="removed", gone=f["gone"], reason=f.get("reason"), **{k: f["last"].get(k) for k in ("title","url","deadline_iso","deadline_txt","src","id","country","kind")}) for u, f in cancelled]
DATA = {"generated": now.isoformat(timespec="minutes"), "note": ACCESS_NOTE, "entries": pub, "removed": gone}
json.dump(DATA, open(os.path.join(OUT, "tenders.json"), "w"), ensure_ascii=False, indent=1)
H = lambda s: html.escape(str(s or ""), quote=True)
IC = {  # Lucide icons (ISC licence), inline
 "list": '<path d="M3 12h.01"/><path d="M3 18h.01"/><path d="M3 6h.01"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M8 6h13"/>',
 "alarm": '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2"/><path d="M5 3 2 6"/><path d="m22 6-3-3"/><path d="M6.38 18.7 4 21"/><path d="M17.64 18.67 20 21"/>',
 "bookmark": '<path d="m19 21-7-4-7 4V5a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v16z"/>',
 "info": '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>',
 "calplus": '<path d="M8 2v4"/><path d="M16 2v4"/><path d="M21 13V6a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h8"/><path d="M3 10h18"/><path d="M16 19h6"/><path d="M19 16v6"/>',
 "rss": '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/>'}
def svg(n, cls=""): return f'<svg class="ic {cls}" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{IC[n]}</svg>'
def chg_html(e):
    ch = e.get("change")
    if not ch: return '<span class="chg" hidden></span>'
    d = dt.date.fromisoformat(ch["date"])
    return (f'<span class="chg"><strong>CHANGED {d:%d %b}:</strong> {H(ch["field"])} {H(ch["old"])} → {H(ch["new"])} · '
            f'<a href="{H(ch["notice_url"])}" rel="noopener">correction notice {H(ch["notice"])}</a></span>')
cards = []
for e in entries:
    cpv = " ".join(e["cpv"]) if e["cpv"] else ""
    cpvshow = " ".join(e["cpv"][:3]) + (f' <span class="more">+{len(e["cpv"])-3} more</span>' if len(e["cpv"]) > 3 else "")
    tagp = "".join(f'<span class="tag">{H(t)}</span>' for t in e["tags"])
    lbl = ("Title as published (original language, unedited)" if e.get("title_official", True) else "Our own short description (edited) – see the programme page for the official title")
    flag = f'<p class="flag">⚠ {H(e["flag"])}</p>' if e.get("flag") else ""
    note = f'<p class="flag">{H(e["time_note"])}</p>' if e.get("time_note") else ""
    badge = ("fund", "Funding call") if e["kind"] == "funding" else ("tend", "Tender")
    cards.append(f'''<article class="card" id="e-{e["uid"]}" data-uid="{e["uid"]}" data-country="{H(e["country"])}" data-kind="{e["kind"]}" data-deadline="{H(e["deadline_iso"][:10])}" data-cpv="{H(cpv)}" data-tags="{H("|".join(e["tags"]))}">
<button class="star" type="button" aria-pressed="false" aria-label="Save: {H(e["title"][:80])}">{svg("bookmark")}</button>
<p class="top"><span class="badge {badge[0]}">{badge[1]}</span>{tagp}<span class="dyn"></span></p>
<p class="meta"><span class="ctry">{H(CN.get(e["country"], e["country"]))}</span> · <span class="src">{H(SRC[e["src"]])}</span></p>
<h3><a href="{H(e["url"])}" rel="noopener">{H(e["title"])}</a></h3>
<p class="lbl">{lbl}</p>{flag}
<dl><dt>{"Programme" if e["kind"]=="funding" else "Buyer"}</dt><dd>{H(e["buyer"])}</dd>
<dt>{H(e.get("deadline_label") or "Deadline")}</dt><dd><strong>{H(e["deadline_txt"])}</strong><br><span class="cd" aria-live="off"></span>{chg_html(e)}</dd>
<dt>CPV</dt><dd>{cpvshow if cpv else '<span class="muted">not in our extract – see original</span>'}</dd>
<dt>Reference</dt><dd>{H(e["id"])}</dd></dl>{note}
<p class="acts"><a class="btn2" href="ics/{e["uid"]}.ics" download="spudsignal-{e["uid"]}.ics" type="text/calendar">{svg("calplus")}<span>Add to calendar</span></a><span class="hint">One-off file, does not update. For automatic updates, subscribe to the feed.</span></p>
<p class="acc">Accessed {H(fmt_access(e["checked"]))} (last check) · {ACCESS_NOTE}</p>
</article>''')
countries = sorted({e["country"] for e in entries}, key=lambda c: CN.get(c, c))
alltags = [t for t in OV["tags_allowed"] if any(t in e["tags"] for e in entries)]
chip = lambda grp, v, lab: f'<button type="button" class="chip" data-g="{grp}" data-v="{H(v)}" aria-pressed="false">{H(lab)}</button>'
chips = ('<div class="chiprow" role="group" aria-label="Type">' + chip("kind", "tender", "Tenders") + chip("kind", "funding", "Funding calls") + "</div>"
         + '<div class="chiprow" role="group" aria-label="Category">' + "".join(chip("tag", t, t) for t in alltags) + "</div>"
         + '<div class="chiprow" role="group" aria-label="Country">' + "".join(chip("country", c, CN.get(c, c)) for c in countries) + "</div>")
gen = now.strftime("%-d %b %Y, %H:%M ") + ("CEST" if now.dst() else "CET")
page = open(os.path.join(os.path.dirname(__file__), "template.html"), encoding="utf-8").read()
R = {"{{CARDS}}": "\n".join(cards) or '<p>No open entries right now.</p>', "{{CHIPS}}": chips, "{{N}}": str(len(entries)), "{{NC}}": f'{len([c for c in countries if c != "EU"])} countries' + (" + EU" if "EU" in countries else ""),
     "{{GEN}}": gen, "{{TODAY}}": now.date().isoformat(), "{{BOAMP_DATE}}": fmt_access(PIPE_RUN),
     "{{DATA}}": json.dumps(DATA, ensure_ascii=False).replace("</", "<\\/"),
     "{{I_LIST}}": svg("list"), "{{I_ALARM}}": svg("alarm"), "{{I_BOOK}}": svg("bookmark"), "{{I_INFO}}": svg("info"), "{{I_CAL}}": svg("calplus"), "{{I_RSS}}": svg("rss")}
for k, v in R.items(): page = page.replace(k, v)
if len(entries) == 1: page = page.replace('open <span id="n-word">entries</span>', 'open <span id="n-word">entry</span>')
open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(page)
from PIL import Image
logo = Image.open(os.path.join(LIB, "site", "apple-touch-icon.png")).convert("RGBA")
for sz in (192, 512): logo.resize((sz, sz), Image.LANCZOS).save(os.path.join(OUT, f"icon-{sz}.png"))
# manifest: designer icons in site/tenders/icons/ if present, else fallback
DI = os.path.join(OUT, "icons"); icons = []
for fn, sz, purpose in (("icon-180.png", "180x180", "any"), ("icon-192.png", "192x192", "any"), ("icon-512.png", "512x512", "any"), ("icon-maskable-512.png", "512x512", "maskable")):
    if os.path.exists(os.path.join(DI, fn)): icons.append({"src": "/tenders/icons/" + fn, "sizes": sz, "type": "image/png", "purpose": purpose})
if not any(i["purpose"] == "any" for i in icons):
    icons += [{"src": "/tenders/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"}, {"src": "/tenders/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
              {"src": "/apple-touch-icon.png", "sizes": "180x180", "type": "image/png", "purpose": "any"}]
man = {"name": "SpudSignal – Open geothermal tenders & funding calls", "short_name": "SpudSignal Tenders", "id": "/tenders/", "start_url": "/tenders/?source=pwa", "scope": "/tenders/",
       "display": "standalone", "orientation": "portrait", "background_color": "#0F2A3D", "theme_color": "#0F2A3D", "lang": "en", "icons": icons}
json.dump(man, open(os.path.join(OUT, "manifest.webmanifest"), "w"), ensure_ascii=False, indent=1)
apple = "/tenders/icons/apple-touch-icon.png" if os.path.exists(os.path.join(DI, "apple-touch-icon.png")) else "/apple-touch-icon.png"
fav = "/tenders/icons/favicon-32.png" if os.path.exists(os.path.join(DI, "favicon-32.png")) else "/favicon-32.png"
p = open(os.path.join(OUT, "index.html"), encoding="utf-8").read().replace("{{APPLE_ICON}}", apple).replace("{{FAV32}}", fav); open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(p)
sw = open(os.path.join(os.path.dirname(__file__), "sw.js")).read().replace("{{VERSION}}", now.strftime("%Y%m%d%H%M"))
open(os.path.join(OUT, "sw.js"), "w").write(sw)
ip = os.path.join(LIB, "site", "index.html"); ih = open(ip, encoding="utf-8").read()
ih2 = re.sub(r'(<span data-tenders-count>)\d+(</span>)', lambda m: m.group(1) + str(len(entries)) + m.group(2), ih)
if ih2 != ih: open(ip, "w", encoding="utf-8").write(ih2)
print(f"{len(entries)} entries, {len(countries)} countries; skipped {len(skipped)}; feed: {len(entries)} active + {len(cancelled)} cancelled")
for e in entries: print(f'  {e["country"]:3} {e["kind"]:8} {e["deadline_txt"][:60]:60} | {e["title"][:70]} | {",".join(e["tags"])} | {e["url"]}' + (" | FLAG " + e["flag"] if e.get("flag") else "") + (" | CHANGED " + e["change"]["old"] + " -> " + e["change"]["new"] if e.get("change") else ""))
for u, why in skipped: print("  SKIP", why, u)
