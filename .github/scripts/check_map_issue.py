#!/usr/bin/env python3
"""Map gate: run after every SpudSignal send and on every map data change.

FAILS (exit 1 in strict mode) if
  1. the most recently published SpudSignal issue has no "Read in SpudSignal #N"
     link on the map (no pin or side-panel row in map/data.js with issue == N),
     or a pin's issue_url does not match that issue's URL in the Library;
  2. map/data.js still shows a tender/funding ID listed as superseded in
     map/superseded-tenders.json (old -> new pairs, maintained by the Kartograf);
  3. map/superseded-tenders.json is malformed.
WARNS only: tender/funding pins whose deadline has passed (the map hides them
in the browser; they drop out at the next map build), a superseding notice that
is not on the map, and all issue-N items having expired.

"Latest issue" comes from the repo itself, so CI needs no network: the highest
N among beehiiv issue links (spudsignal.beehiiv.com/p/spudsignal-N-...) in the
Library pages (index.html, tenders/index.html, whats-new/index.html). These are
added by the Library "Featured in" PR after each send. With --online the script
also reads https://spudsignal.beehiiv.com/sitemap.xml (15 s timeout). If that
fails, it prints a warning and keeps the repo-local result (fail-safe). CI does
not use --online.

An issue with nothing mappable (e.g. policy only) can be exempted in
map/superseded-tenders.json -> "issues_without_map_items": [{"issue": N, "reason": "..."}].

Modes: --mode strict (default; exit 1 on failure) or --mode advisory (failures
are printed as warnings, exit 0). CI uses advisory only for pull requests that
do not touch the map data or this gate, so the weekly tender refresh and the
Library featured-links PRs are never blocked by a map that is one issue behind.

Usage:
  python3 .github/scripts/check_map_issue.py [site_dir] [--mode strict|advisory] [--online] [--now ISO]
  python3 .github/scripts/check_map_issue.py --selftest
"""
import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.request

ISSUE_RE = re.compile(r"https://spudsignal\.beehiiv\.com/p/spudsignal-(\d+)-[a-z0-9-]+")
LIBRARY_PAGES = ["index.html", "tenders/index.html", "whats-new/index.html"]
SUPERSEDED = "map/superseded-tenders.json"
SITEMAP = "https://spudsignal.beehiiv.com/sitemap.xml"
NUM_RE = re.compile(r"(?<!\d)\d{5,6}-20\d\d(?!\d)|(?<!\d)\d{2}-\d{5,6}(?!\d)")  # TED 725171-2026, BOAMP 26-103155


def load_datajs(path):
    s = open(path, encoding="utf-8").read()
    a = s.index("=", s.index("window.SS_DATA")) + 1
    data, end = json.JSONDecoder().raw_decode(s[a:].lstrip())
    rest = s[a:].lstrip()[end:]
    extra = {"nationwide": []}
    if "window.SS_EXTRA" in rest:
        b = rest.index("=", rest.index("window.SS_EXTRA")) + 1
        extra, _ = json.JSONDecoder().raw_decode(rest[b:].lstrip())
    return data, extra


def issue_urls_in_repo(root):
    found = {}
    for rel in LIBRARY_PAGES:
        p = os.path.join(root, rel)
        if os.path.exists(p):
            for m in ISSUE_RE.finditer(open(p, encoding="utf-8").read()):
                found.setdefault(int(m.group(1)), set()).add(m.group(0))
    return found


def issue_urls_online(timeout=15):
    with urllib.request.urlopen(urllib.request.Request(SITEMAP, headers={"User-Agent": "spudsignal-map-gate"}), timeout=timeout) as r:
        s = r.read().decode("utf-8", "replace")
    found = {}
    for m in ISSUE_RE.finditer(s):
        found.setdefault(int(m.group(1)), set()).add(m.group(0))
    return found


def check(root, now=None, online=False):
    """Returns (errors, warnings, info)."""
    errors, warnings, info = [], [], []
    now = now or dt.datetime.now(dt.timezone.utc)
    dj = os.path.join(root, "map", "data.js")
    if not os.path.exists(dj):
        return ["map/data.js not found"], warnings, info
    try:
        data, extra = load_datajs(dj)
    except (ValueError, KeyError) as e:
        return [f"map/data.js: cannot parse ({e})"], warnings, info
    items = [("pin", f.get("properties", {})) for f in data.get("features", [])]
    items += [("side panel", p) for p in extra.get("nationwide", [])]

    # --- superseded list (also holds exemptions)
    sup, exempt = [], {}
    sp = os.path.join(root, SUPERSEDED)
    if os.path.exists(sp):
        try:
            doc = json.load(open(sp, encoding="utf-8"))
            sup = doc.get("superseded", [])
            for e in doc.get("issues_without_map_items", []):
                exempt[int(e["issue"])] = e.get("reason", "")
            for i, e in enumerate(sup):
                miss = [k for k in ("old", "new", "source") if not e.get(k)]
                if miss or not NUM_RE.search(e.get("old", "")):
                    errors.append(f"{SUPERSEDED}: entry {i} malformed (missing {miss or 'notice number in old'})")
        except (ValueError, KeyError, TypeError) as e:
            errors.append(f"{SUPERSEDED}: invalid ({e})")
    else:
        warnings.append(f"{SUPERSEDED} not found: superseded-tender check skipped")

    # --- 1. latest issue has a Read-in link
    urls = issue_urls_in_repo(root)
    src = "Library pages in the repo"
    if online:
        try:
            on = issue_urls_online()
            if on and (not urls or max(on) > max(urls)):
                info.append(f"beehiiv sitemap lists #{max(on)}, newer than the Library's latest #{max(urls) if urls else '-'}")
                for n, u in on.items():
                    urls.setdefault(n, set()).update(u)
                src = "beehiiv sitemap"
        except Exception as e:  # fail-safe: never fail on network trouble
            warnings.append(f"--online: beehiiv sitemap not reachable ({e.__class__.__name__}); using repo-local issue list")
    for n, u in sorted(urls.items()):
        if len(u) > 1:
            errors.append(f"issue #{n} has more than one URL in the Library: {sorted(u)}")
    if not urls:
        errors.append("no SpudSignal issue links found in the Library pages; cannot tell the latest issue")
    else:
        latest = max(urls)
        lurl = sorted(urls[latest])[0]
        info.append(f"latest published issue: #{latest} ({lurl}), from the {src}")
        mine = [(w, p) for w, p in items if p.get("issue") == latest]
        if not mine:
            if latest in exempt:
                info.append(f"issue #{latest} exempted: {exempt[latest] or 'no reason given'}")
            else:
                errors.append(f"map has no 'Read in SpudSignal #{latest}' link: no pin or side-panel row with issue {latest} in map/data.js")
        else:
            def is_open(p):
                d = p.get("deadline_iso")
                if not d:
                    return True
                try:
                    t = dt.datetime.fromisoformat(d.replace("Z", "+00:00"))
                except ValueError:
                    return True
                if t.tzinfo is None:
                    t = t.replace(tzinfo=dt.timezone(dt.timedelta(hours=1)))
                return t > now
            vis = [x for x in mine if is_open(x[1])]
            info.append(f"#{latest}: {len(mine)} map items carry the Read-in link ({len(vis)} visible now)")
            if not vis:
                warnings.append(f"all #{latest} map items have passed their deadline; the Read-in link is no longer visible")
        for w, p in items:
            n = p.get("issue")
            if n in urls and p.get("issue_url") not in urls[n]:
                errors.append(f"{w} '{p.get('title', '')[:60]}': issue_url {p.get('issue_url')!r} does not match the Library's URL for #{n}")

    # --- 2. no superseded IDs on the map
    on_map = set()
    for w, p in items:
        for k in ("id", "source_url", "title"):
            on_map.update(NUM_RE.findall(str(p.get(k) or "")))
    for e in sup:
        m = NUM_RE.search(e.get("old", ""))
        if not m:
            continue
        old = m.group(0)
        hits = [f"{w} '{p.get('title', '')[:60]}'" for w, p in items
                if old in NUM_RE.findall(" ".join(str(p.get(k) or "") for k in ("id", "source_url", "title")))]
        if hits:
            errors.append(f"superseded {e['old']} (replaced by {e.get('new')}) still on the map: {'; '.join(hits)}")
        nm = NUM_RE.search(e.get("new", ""))
        if nm and nm.group(0) not in on_map:
            warnings.append(f"{e.get('new')} (replaces {e['old']}) is not on the map (expired, or not added yet)")

    # --- warning only: tender/funding pins past their deadline
    past = []
    for w, p in items:
        d = p.get("deadline_iso")
        if p.get("type") in ("tender", "funding") and d:
            try:
                t = dt.datetime.fromisoformat(d.replace("Z", "+00:00"))
                if t.tzinfo is None:
                    t = t.replace(tzinfo=dt.timezone(dt.timedelta(hours=1)))
                if t <= now:
                    past.append(f"{p.get('id')} ({d[:10]})")
            except ValueError:
                pass
    if past:
        warnings.append(f"{len(past)} tender/funding pin(s) past their deadline (hidden in the browser, drop out at the next map build): {', '.join(past)}")
    return errors, warnings, info


def selftest():
    """Synthetic site, independent of today's data: proves each rule passes and fails as intended."""
    U = "https://spudsignal.beehiiv.com/p/spudsignal-{n}-slug-{n}"
    now = dt.datetime(2026, 11, 23, 12, tzinfo=dt.timezone.utc)

    def site(features, nationwide=(), issues=(1, 2), superseded=(), exempt=()):
        d = tempfile.mkdtemp()
        os.makedirs(os.path.join(d, "map"))
        open(os.path.join(d, "index.html"), "w").write("".join(f'<a href="{U.format(n=n)}">#{n}</a>' for n in issues))
        js = "window.SS_DATA=" + json.dumps({"type": "FeatureCollection", "features": [{"type": "Feature", "properties": p} for p in features]}) \
             + ";\nwindow.SS_EXTRA=" + json.dumps({"nationwide": list(nationwide)}) + ";\n"
        open(os.path.join(d, "map", "data.js"), "w").write(js)
        json.dump({"superseded": list(superseded), "issues_without_map_items": list(exempt)}, open(os.path.join(d, SUPERSEDED), "w"))
        return d

    proj = lambda n: {"type": "project", "title": f"P{n}", "issue": n, "issue_url": U.format(n=n), "id": "X release, 1 Nov 2026"}
    tend = lambda n, i, dl: {"type": "tender", "title": f"T{i}", "issue": n, "issue_url": U.format(n=n), "id": f"TED {i}", "source_url": f"https://ted.europa.eu/en/notice/-/detail/{i}", "deadline_iso": dl}
    pair = {"old": "TED 725171-2026", "new": "TED 801779-2026", "source": "https://ted.europa.eu/en/notice/-/detail/801779-2026"}
    cases = [
        ("latest issue #2 has a project pin: must PASS", site([proj(1), proj(2)]), False),
        ("latest issue #2 has no map item: must FAIL", site([proj(1)]), True),
        ("#2 only on an expired tender: must PASS (warning only)", site([proj(1), tend(2, "700000-2026", "2026-11-20T10:00:00+01:00")]), False),
        ("#2 only in the side panel: must PASS", site([proj(1)], nationwide=[tend(2, "NL-SDE-2026", "2026-11-26T17:00:00+01:00")]), False),
        ("#2 exempted (nothing mappable): must PASS", site([proj(1)], exempt=[{"issue": 2, "reason": "policy only"}]), False),
        ("issue_url slug wrong: must FAIL", site([proj(1), dict(proj(2), issue_url=U.format(n=2) + "-x")]), True),
        ("superseded TED 725171-2026 still a tender pin: must FAIL", site([proj(2), tend(1, "725171-2026", "2026-11-24T10:00:00+01:00")], superseded=[pair]), True),
        ("superseded ID only in a project pin's source: must FAIL", site([dict(proj(2), id="TED 725171-2026, 20 Oct 2026")], superseded=[pair]), True),
        ("successor 801779 on the map, 725171 gone: must PASS", site([proj(2), tend(2, "801779-2026", "2026-12-08T10:00:00+01:00")], superseded=[pair]), False),
        ("similar number 1725171-2026 is not 725171-2026: must PASS", site([proj(2), dict(proj(1), id="TED 1725171-2026")], superseded=[pair]), False),
        ("malformed superseded entry: must FAIL", site([proj(2)], superseded=[{"old": "Kutno", "new": "x"}]), True),
        ("no issue links in the Library: must FAIL", site([proj(2)], issues=()), True),
    ]
    ok = True
    for name, d, must_fail in cases:
        errs, _, _ = check(d, now=now)
        good = bool(errs) == must_fail
        ok &= good
        print(f"{'ok  ' if good else 'BAD '} {name}" + ("" if good else f" -> errors: {errs}"))
        shutil.rmtree(d, ignore_errors=True)
    print("Self-test passed" if ok else "Self-test FAILED")
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    mode = "strict"
    if "--mode" in argv:
        mode = argv[argv.index("--mode") + 1]
    now = None
    if "--now" in argv:
        now = dt.datetime.fromisoformat(argv[argv.index("--now") + 1])
    skip = {"--mode", "--now"}
    pos = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] not in skip)]
    root = pos[0] if pos else "."
    errors, warnings, info = check(root, now=now, online="--online" in argv)
    gh = os.environ.get("GITHUB_ACTIONS") == "true"
    for i in info:
        print(f"info: {i}")
    for w in warnings:
        print(f"::warning::{w}" if gh else f"WARNING: {w}")
    for e in errors:
        if mode == "advisory":
            print(f"::warning::map gate (advisory): {e}" if gh else f"ADVISORY FAIL: {e}")
        else:
            print(f"::error::{e}" if gh else f"FAIL: {e}")
    if errors and mode != "advisory":
        print(f"Map gate FAILED ({len(errors)} problem(s)).")
        return 1
    print("Map gate passed" + (" (advisory mode: problems reported as warnings)" if errors else "") + ".")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
