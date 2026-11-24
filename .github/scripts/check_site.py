#!/usr/bin/env python3
"""Checks the published site (the repo root is what GitHub Pages serves).

Runs on every pull request against main. No network access needed.
Every count is derived from the files themselves, nothing is hard-wired,
so a week with more or fewer entries passes as long as the pages agree
with their own data.

Usage:
  python3 .github/scripts/check_site.py [site_dir]
  python3 .github/scripts/check_site.py --selftest
"""
import html
import json
import os
import re
import shutil
import sys
import tempfile
from html.parser import HTMLParser

PAGES = ["index.html", "tenders/index.html", "map/index.html",
         "projects/index.html", "whats-new/index.html"]
TABBED = ["index.html", "tenders/index.html", "map/index.html", "projects/index.html"]

# Must never be published (GitHub Pages serves the whole repo).
FORBIDDEN_PATHS = [
    (re.compile(r"(^|/)handoff(/|$)"), "handoff/ folder (internal build notes)"),
    (re.compile(r"(^|/)pretabs(/|$)"), "pretabs/ folder (generator state)"),
    (re.compile(r"(^|/)generators[^/]*(/|$)"), "generator folder"),
    (re.compile(r"(^|/)pr-check(/|$)"), "PR screenshot folder"),
    (re.compile(r"data\.geojson$"), "map/data.geojson (ODbL: display only, no download)"),
    (re.compile(r"crosswalk[^/]*\.(csv|json|md)$", re.I), "map crosswalk (contains pin coordinates)"),
    (re.compile(r"(^|/)(PAUSE|README-CLAUDE|APPLY)\.md$"), "internal bot notes"),
    (re.compile(r"(^|/)\.env|\.(pem|key)$"), "secret/credential file"),
]

# Placeholders and leftovers that must not go live. Case-sensitive on purpose
# ("placeholder=" is a normal HTML attribute).
PLACEHOLDERS = [
    re.compile(r"set at go-live", re.I),
    re.compile(r"\bTODO\b"), re.compile(r"\bFIXME\b"), re.compile(r"\bTBD\b"),
    re.compile(r"\bXXX\b"), re.compile(r"\bPLACEHOLDER\b"),
    re.compile(r"\[EDITOR"), re.compile(r"lorem ipsum", re.I),
]
# Old texts that Update 2.0 removed (README checklist). Checked on the 5 pages.
REMOVED_TEXTS = ["Clear all filters", "listings", "Projects &amp; wells (#1", "Projects & wells (#1",
                 "?pins=b", "?hdr=b", "?past=show"]

H05 = ("Liability: entries are provided for information only, without guarantee of "
       "completeness or accuracy; the original document is authoritative.")

def first_difference(page, want, ctx=40):
    """Show where two HTML snippets first differ: position plus context on both sides."""
    i = next((k for k, (x, y) in enumerate(zip(page, want)) if x != y), min(len(page), len(want)))
    start = max(0, i - ctx)
    def cut(s):
        return ("…" if start else "") + s[start:i + ctx] + ("…" if len(s) > i + ctx else "")
    return f"first difference at character {i + 1}: page {cut(page)!r} vs map {cut(want)!r}"


# One project row on /projects/: Name, Stage, Region, Status, Source
PROJECT_ROW = re.compile(r"<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>")

TEXT_EXT = (".html", ".js", ".mjs", ".css", ".json", ".ics", ".webmanifest", ".xml", ".txt", ".svg")
SKIP_DIRS = {".git", ".github", "node_modules"}
SKIP_TEXT_SCAN = ("map/vendor/", "audience/")  # third-party code; audience/ holds audit notes


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        for k, v in attrs:
            if v and k in ("href", "src") and not (tag == "a" and k == "src"):
                self.refs.append(v)


class Check:
    def __init__(self, root):
        self.root = root
        self.errors = []

    def err(self, msg):
        self.errors.append(msg)

    def read(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as f:
            return f.read()

    def exists(self, rel):
        return os.path.exists(os.path.join(self.root, rel))

    def files(self):
        for d, dirs, fs in os.walk(self.root):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in fs:
                yield os.path.relpath(os.path.join(d, f), self.root).replace(os.sep, "/")

    # 1. nothing internal gets published
    def forbidden_paths(self):
        for rel in self.files():
            for rx, why in FORBIDDEN_PATHS:
                if rx.search(rel):
                    self.err(f"{rel}: must not be published ({why})")

    # 2. no placeholders in published text files
    def placeholders(self):
        for rel in self.files():
            if not rel.endswith(TEXT_EXT) or rel.startswith(SKIP_TEXT_SCAN):
                continue
            try:
                s = self.read(rel)
            except UnicodeDecodeError:
                continue
            for rx in PLACEHOLDERS:
                for m in rx.finditer(s):
                    line = s.count("\n", 0, m.start()) + 1
                    self.err(f"{rel}:{line}: placeholder left in output: {m.group(0)!r}")
        for rel in PAGES:
            if not self.exists(rel):
                continue
            s = self.read(rel)
            for t in REMOVED_TEXTS:
                if t in s:
                    self.err(f"{rel}: old text that Update 2.0 removed is back: {t!r}")

    # 3. every page has the shell: tabs, footer, legal text, skip link
    def pages(self):
        for rel in PAGES:
            if not self.exists(rel):
                self.err(f"{rel}: page missing")
                continue
            s = self.read(rel)
            if not re.search(r'<meta[^>]+name="?viewport', s):
                self.err(f"{rel}: no viewport meta tag")
            if not re.search(r"<title>[^<]+</title>", s):
                self.err(f"{rel}: empty or missing <title>")
            if s.count("data-ss-footer") != 1:
                self.err(f"{rel}: expected exactly 1 shared footer, found {s.count('data-ss-footer')}")
            n = s.count(H05)
            if n != 1:
                self.err(f"{rel}: liability sentence (H05) must appear exactly once, found {n}")
            for t in ("Impressum", "Privacy", "Skip to content", 'href="/whats-new/"'):
                if t not in s:
                    self.err(f"{rel}: missing {t!r}")
        for rel in TABBED:
            if self.exists(rel) and 'data-ss-tabs="2.0"' not in self.read(rel)[:3000]:
                self.err(f'{rel}: tab bar marker data-ss-tabs="2.0" missing')

    # 4. counts on the pages match the data (derived, never fixed numbers)
    def counts(self):
        if self.exists("index.html"):
            s = self.read("index.html")
            n = len(re.findall(r'class="libcard\b', s))
            if n == 0:
                self.err("index.html: no Library entries (.libcard) found")
            heads = re.findall(r'<h2 class="ss-h2" id="lib-([^"]+)"', s)
            countries = len([h for h in heads if h != "europeeuwide"])
            m = re.search(r'id="ss-hcount">(\d+) entries<', s)
            if not m:
                self.err("index.html: header count '<N> entries' not found")
            elif int(m.group(1)) != n:
                self.err(f"index.html: header says {m.group(1)} entries, page has {n}")
            for m in re.finditer(r"(\d+) primary sources from (\d+) countries", s):
                if int(m.group(1)) != n:
                    self.err(f"index.html: meta text says {m.group(1)} sources, page has {n}")
                if int(m.group(2)) != countries:
                    self.err(f"index.html: meta text says {m.group(2)} countries, page has {countries}")
            m = re.search(r"(\d+) countries \+ EU", s)
            if m and int(m.group(1)) != countries:
                self.err(f"index.html: header says {m.group(1)} countries, page has {countries}")

        if self.exists("tenders/tenders.json") and self.exists("tenders/index.html"):
            tj = json.loads(self.read("tenders/tenders.json"))
            entries = tj.get("entries", [])
            s = self.read("tenders/index.html")
            cards = re.findall(r'<article class="card"[^>]*data-uid="([^"]+)"', s)
            m = re.search(r'<script type="application/json" id="data">(.*?)</script>', s, re.S)
            embedded = json.loads(m.group(1)).get("entries", []) if m else None
            if embedded is None:
                self.err("tenders/index.html: embedded #data JSON not found")
            elif embedded != entries:
                diff = [e["uid"] for e, f in zip(embedded, entries) if e != f]
                self.err("tenders/index.html: embedded data differs from tenders/tenders.json"
                         + (f" (entries {', '.join(diff[:5])})" if diff else f" ({len(embedded)} vs {len(entries)} entries)"))
            if sorted(cards) != sorted(e["uid"] for e in entries):
                self.err(f"tenders/index.html: {len(cards)} cards, tenders.json has {len(entries)} entries")
            for e in entries:
                if not self.exists(f"tenders/ics/{e['uid']}.ics"):
                    self.err(f"tenders/ics/{e['uid']}.ics missing (calendar file for {e.get('id')})")

        if self.exists("map/testlayers.js") and self.exists("projects/index.html"):
            raw = self.read("map/testlayers.js")
            try:
                tl = json.JSONDecoder().raw_decode(raw.split("=", 1)[1].strip())[0]
            except (ValueError, IndexError) as e:
                self.err(f"map/testlayers.js: cannot parse ({e})")
                tl = None
            if tl:
                p = self.read("projects/index.html")
                for key, label in (("active", "Active projects"), ("operating", "Operating plants")):
                    for m in re.finditer(re.escape(label) + r" \((\d+)\)", p):
                        if int(m.group(1)) != len(tl.get(key, [])):
                            self.err(f"projects/index.html: '{label} ({m.group(1)})' but map data has {len(tl.get(key, []))}")
                self.projects_vs_map(tl, p)

    # 4b. /projects/ is static HTML next to the map data: every pin's row must
    # show the same stage, status line (+ location note) and sources as
    # map/testlayers.js (added 24 Nov 2026 after PR #23 left five rows behind)
    def projects_vs_map(self, tl, page):
        def a(u, n):
            return f'<a href="{html.escape(u)}" target="_blank" rel="noopener">{html.escape(n, quote=False)}</a>'
        rows = {}
        for m in PROJECT_ROW.finditer(page):
            name = html.unescape(m.group(1))
            if name in rows:
                line = page.count("\n", 0, m.start()) + 1
                self.err(f"projects/index.html: duplicate row '{name}' (line {line}); each map pin needs exactly one row")
                continue
            rows[name] = m
        pins = tl.get("active", []) + tl.get("operating", [])
        names = set()
        for pin in pins:
            pid, name = pin.get("id", "?"), pin.get("name", "")
            names.add(name)
            m = rows.get(name)
            if not m:
                self.err(f"projects/index.html: no row for map pin {pid} '{name}' (map/testlayers.js)")
                continue
            stage = html.escape(pin.get("stage") or "", quote=False)
            if pin.get("status_open") and pin.get("status_label"):
                stage += ' <span class="open">' + html.escape(pin["status_label"], quote=False) + "</span>"
            status = html.escape(pin.get("status_line") or "", quote=False)
            if pin.get("location_note"):
                status += "<br><small>" + html.escape(pin["location_note"], quote=False) + "</small>"
            more = pin.get("sources") or []
            src = "Source: " + a(pin.get("source_url", ""), pin.get("source_name", ""))
            if more:
                src += (f"<details><summary>More sources ({len(more)})</summary><ul>"
                        + "".join("<li>" + a(x["url"], x["name"]) + "</li>" for x in more) + "</ul></details>")
            for field, shown, want in (("stage", m.group(2), stage), ("status line", m.group(4), status),
                                       ("sources", m.group(5), src)):
                if shown != want:
                    self.err(f"projects/index.html: {pid} '{name}': {field} differs from map/testlayers.js, "
                             + first_difference(shown, want))
        for name in rows:
            if name not in names:
                self.err(f"projects/index.html: row '{name}' has no pin in map/testlayers.js")

    # 5. map shows data, never offers it as a download
    def map_data(self):
        for rel in ("map/index.html", "projects/index.html"):
            if self.exists(rel) and "data.geojson" in self.read(rel):
                self.err(f"{rel}: still references data.geojson")
        if self.exists("map/data.js"):
            raw = self.read("map/data.js")
            try:
                json.JSONDecoder().raw_decode(raw.split("=", 1)[1].strip())
            except (ValueError, IndexError) as e:
                self.err(f"map/data.js: cannot parse ({e})")

    # 6. internal links and assets point to files that exist
    def links(self):
        for rel in self.files():
            if not rel.endswith(".html") or rel.startswith(SKIP_TEXT_SCAN):
                continue
            p = Links()
            p.feed(self.read(rel))
            base = os.path.dirname(rel)
            for ref in p.refs:
                ref = html.unescape(ref).strip()
                if re.match(r"^([a-z][a-z0-9+.-]*:|#|//)", ref, re.I) or "${" in ref:
                    continue
                path = ref.split("#")[0].split("?")[0]
                if not path:
                    continue
                target = path.lstrip("/") if path.startswith("/") else os.path.normpath(os.path.join(base, path))
                if target in ("", "."):
                    target = "index.html"
                elif path.endswith("/") or os.path.isdir(os.path.join(self.root, target)):
                    target = target.rstrip("/") + "/index.html"
                if not self.exists(target):
                    self.err(f"{rel}: broken internal link {ref!r}")

    # 7. data files are well formed
    def data_files(self):
        for rel in self.files():
            if rel.endswith((".json", ".webmanifest")):
                try:
                    json.loads(self.read(rel))
                except ValueError as e:
                    self.err(f"{rel}: invalid JSON ({e})")
            elif rel.endswith(".ics"):
                s = self.read(rel)
                if not (s.lstrip().startswith("BEGIN:VCALENDAR") and "END:VCALENDAR" in s):
                    self.err(f"{rel}: not a valid calendar file")
        if not self.exists("CNAME") or self.read("CNAME").strip() != "library.spudsignal.com":
            self.err("CNAME must be library.spudsignal.com")

    def run(self):
        for step in (self.forbidden_paths, self.placeholders, self.pages,
                     self.counts, self.map_data, self.links, self.data_files):
            step()
        return self.errors


def selftest():
    """Proves the checks are not tied to today's numbers and do catch mistakes."""
    src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    ok = True

    def copy():
        d = tempfile.mkdtemp()
        dst = os.path.join(d, "site")
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git"))
        return dst

    def edit(root, rel, fn):
        p = os.path.join(root, rel)
        with open(p, encoding="utf-8") as f:
            s = f.read()
        with open(p, "w", encoding="utf-8") as f:
            f.write(fn(s))

    def drop_libcard(s):
        # remove one Library entry and update every count consistently,
        # like a correct weekly build with one entry fewer would
        # pick an entry inside a country that has more entries, so no heading goes
        starts = [m.start() for m in re.finditer(r'<div class="libcard', s)]
        i, j = next((a, b) for a, b in zip(starts, starts[1:]) if "<h2" not in s[a:b])
        n = len(re.findall(r'class="libcard\b', s))
        s = s[:i] + s[j:]
        s = s.replace(f'id="ss-hcount">{n} entries<', f'id="ss-hcount">{n - 1} entries<')
        return re.sub(rf"\b{n} primary sources", f"{n - 1} primary sources", s)

    def drop_tender(root):
        tj = json.load(open(os.path.join(root, "tenders/tenders.json"), encoding="utf-8"))
        gone = tj["entries"].pop()
        json.dump(tj, open(os.path.join(root, "tenders/tenders.json"), "w", encoding="utf-8"))
        def fix(s):
            s = re.sub(r'<article class="card"[^>]*data-uid="%s".*?</article>' % gone["uid"], "", s, flags=re.S)
            m = re.search(r'(<script type="application/json" id="data">)(.*?)(</script>)', s, re.S)
            d = json.loads(m.group(2)); d["entries"] = [e for e in d["entries"] if e["uid"] != gone["uid"]]
            return s[:m.start(2)] + json.dumps(d) + s[m.end(2):]
        edit(root, "tenders/index.html", fix)

    def map_edit(root, fn):
        # edit map/testlayers.js like a weekly map delta would (JSON in, JSON out)
        def go(s):
            pre, body = s.split("=", 1)
            d, end = json.JSONDecoder().raw_decode(body.strip())
            fn(d)
            return pre + "=" + json.dumps(d, ensure_ascii=False) + body.strip()[end:]
        edit(root, "map/testlayers.js", go)

    def first_active(d):
        return d["active"][0]

    def add_source_both(root):
        # map gets one more source AND /projects/ row is updated the same way: consistent
        box = {}
        def fn(d):
            p = first_active(d); box["p"] = dict(p)
            p["sources"] = p["sources"] + [{"name": "Selftest source", "url": "https://example.org/selftest"}]
            box["n"] = p
        map_edit(root, fn)
        old, new = box["p"], box["n"]
        def fix(s):
            m = next(m for m in PROJECT_ROW.finditer(s) if html.unescape(m.group(1)) == new["name"])
            cell = m.group(5)
            if old["sources"]:
                cell = cell.replace(f"More sources ({len(old['sources'])})", f"More sources ({len(new['sources'])})")
                cell = cell.replace("</ul></details>", '<li><a href="https://example.org/selftest" target="_blank" rel="noopener">Selftest source</a></li></ul></details>')
            else:
                cell += '<details><summary>More sources (1)</summary><ul><li><a href="https://example.org/selftest" target="_blank" rel="noopener">Selftest source</a></li></ul></details>'
            return s[:m.start(5)] + cell + s[m.end(5):]
        edit(root, "projects/index.html", fix)

    cases = [
        ("map source added and /projects/ row updated the same way: must PASS", add_source_both, False),
        ("map status line changed, /projects/ left behind: must FAIL",
         lambda r: map_edit(r, lambda d: first_active(d).update(status_line=first_active(d)["status_line"] + " Selftest.")), True),
        ("map source added, /projects/ left behind: must FAIL",
         lambda r: map_edit(r, lambda d: first_active(d).update(sources=first_active(d)["sources"] + [{"name": "x", "url": "https://example.org/x"}])), True),
        ("duplicate /projects/ row (same project twice, other stage): must FAIL",
         lambda r: edit(r, "projects/index.html", lambda s: (lambda m: s[:m.end()] + "\n" + m.group(0).replace("</td><td>In preparation</td>", "</td><td>In execution</td>", 1) + s[m.end():])(
             next(m for m in PROJECT_ROW.finditer(s) if "</td><td>In preparation</td>" in m.group(0)))), True),
        ("stage changed on /projects/ only: must FAIL",
         lambda r: edit(r, "projects/index.html", lambda s: s.replace("</td><td>In execution</td>", "</td><td>In preparation</td>", 1)), True),
        ("one Library entry and one tender fewer, counts updated: must PASS",
         lambda r: (edit(r, "index.html", drop_libcard), drop_tender(r)), False),
        ("one Library entry fewer, header count left unchanged: must FAIL",
         lambda r: edit(r, "index.html", lambda s: re.sub(r'<div class="libcard.*?(?=<div class="libcard)', "", s, count=1, flags=re.S)), True),
        ("handoff/ folder added: must FAIL",
         lambda r: (os.makedirs(os.path.join(r, "handoff")), open(os.path.join(r, "handoff", "x.md"), "w").write("x")), True),
        ("'set at go-live' placeholder: must FAIL",
         lambda r: edit(r, "whats-new/index.html", lambda s: s.replace("</h1>", "</h1><p>set at go-live</p>", 1)), True),
        ("map/data.geojson added: must FAIL",
         lambda r: open(os.path.join(r, "map", "data.geojson"), "w").write("{}"), True),
    ]
    base = Check(src).run()
    for name, mutate, expect_fail in cases:
        root = copy()
        mutate(root)
        errs = [e for e in Check(root).run() if e not in base]
        failed = bool(errs)
        good = failed == expect_fail
        ok &= good
        print(("ok   " if good else "FAIL ") + name + ("" if good else f" -> {errs or 'no error raised'}"))
        shutil.rmtree(os.path.dirname(root))
    return ok


def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    root = sys.argv[1] if len(sys.argv) > 1 else "."
    errors = Check(root).run()
    for e in errors:
        print("ERROR " + e)
        if os.environ.get("GITHUB_ACTIONS"):
            print(f"::error::{e}")
    print(f"{len(errors)} problem(s) found" if errors else "All site checks passed")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
