"""Library slim layout for site/tenders/index.html (go-live 13 Nov 2026; Daniel's OK 22:10 CET).
Generator stage, runs on EVERY build, after build_tenders.py and `node audience/apply.mjs`:
    python3 tenders/build_tenders.py && node site/audience/apply.mjs ... && python3 tenders/slim.py      (from library/)
Library 2.0 (13 Nov 2026): after ALL page generators (incl. the map/projects builder) run the tabs stage last:
    python3 tabs/tabs.py <built site or repo dir>      (shared shell/CSS/JS on every page, idempotent; see tabs/tabs.py)
Source: library-slim/proposal-2026-11-13-v2.md (Designer v2), texte.md sha 5c8eb857 (Editor), texte-review.md (Reviewer GREEN).
Placement/markup only; texts per Editor IDs T01–T23, F1, F2. T08/T10/T12 implemented here for the generator (not in the prototype).
Refuses to run twice on the same file (marker id="slim-css")."""
import re, sys, os, json, pathlib
HERE = pathlib.Path(__file__).resolve().parent
SRC = DST = pathlib.Path(os.environ.get("SLIM_FILE") or HERE.parent / "site" / "tenders" / "index.html")   # SLIM_FILE: test fixtures only
s = SRC.read_text()
if 'id="slim-css"' in s: sys.exit("slim.py: already applied – rebuild with build_tenders.py + apply.mjs first")
N_ENTRIES = len(json.load(open(os.environ.get("SLIM_JSON") or HERE.parent / "site" / "tenders" / "tenders.json"))["entries"])
def sub1(pat, rep, s, flags=re.S):
    n = len(re.findall(pat, s, flags))
    assert n == 1, (pat[:60], n)
    return re.sub(pat, rep, s, flags=flags)

ICON_INFO = '<svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>'
ICON_FILTER = '<svg class="ic" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M3 5h18"/><path d="M6 12h12"/><path d="M10 19h4"/></svg>'
CHEV = '<svg class="chev" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="m6 9 6 6 6-6"/></svg>'

# ---------- v2: Editor texts (texte.md sha 5c8eb857…, Reviewer 13 Nov 21:47/21:55) ----------
import json as _json
ED = _json.load(open(HERE / "slim_texts.json"))
F1 = ED["F1"].replace("{DD Mon YYYY}", "DD Mon YYYY")   # template placeholder rendered as a format pattern (open question for Editor)
F2 = ED["F2"]
T01_LONG = "Only entries whose deadline has not passed and that were reviewed for a SpudSignal issue or verified on the programme's own page."
def esc(x): return x.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
INFO_SM = ICON_INFO.replace('width="20" height="20"', 'width="16" height="16"').replace('class="ic"', 'class="ic sm"')

# ---------- 1. hero: T01 – sentence 1 stays visible, inclusion rule behind "What’s on this list?" ----------
m = re.search(r'<p>(Open geothermal tenders and funding calls across Europe, each linked to the original notice\.)<span class="long">( Only entries whose deadline has not passed and that were reviewed for a SpudSignal issue or verified on the programme\'s own page\.)</span></p>', s)
assert m
s = s.replace(m.group(0),
  '<details class="intro" id="t01"><summary><span class="lead1">' + m.group(1) + '</span> <span class="mo">' + INFO_SM.replace('class="ic sm"', 'class="ic sm lt"') + 'What’s on this list?' + CHEV + '</span></summary>'
  '<p>' + m.group(2).strip() + ' Each entry links to the original notice.</p></details>')

# ---------- 2. T02 page note: visible warning line; F1 + F2 behind it ----------
m = re.search(r'<p class="note"><strong>No guarantee\.</strong> (.*?)</p>', s)
assert m
s = s.replace(m.group(0),
  '<details class="note" id="about-data"><summary>' + ICON_INFO + '<span><strong>No guarantee – check the original notice.</strong> <span class="mo">About this data' + CHEV + '</span></span></summary>'
  '<div class="f1"><h2 class="fh2">About this data</h2><p id="f1">' + esc(F1) + '</p>'
  '<h2 class="fh2">Audience labels</h2><p id="f2">' + esc(F2) + '</p>'
  '<p><a href="#about-data">About &amp; Sources</a></p></div></details>')

# ---------- 3. map link: slimmer, moved below list ----------
m = re.search(r'<a class="maplink" href="/map/" style="[^"]*">(.*?)</a>\n', s)
assert m
maplink = '<a class="maplink" href="/map/">' + m.group(1).replace('<span style="font-weight:400;color:#C8D2DC">', '<span class="ml2">') + '</a>\n'
s = s.replace(m.group(0), '')

# ---------- 4. feed box (T17): heading + short body visible, full body behind Options ----------
m = re.search(r'<div class="feed" id="feedbox">(.*?)</div></div>\n<!-- audience-notes-start -->', s, re.S)
assert m
fb = m.group(1)
mini_btn = re.search(r'<a class="btn1 sm".*?</a>', fb).group(0)
h2 = re.search(r'<h2>(.*?)</h2>', fb).group(1)
p1 = re.search(r'</h2>\n(<p>Subscribe once.*?</p>)', fb, re.S).group(1)
big = re.search(r'<p><a class="btn1" id="sub".*?</p>', fb).group(0)
alt = re.search(r'<div class="feedalt">.*', fb, re.S).group(0) + '</div>'
s = s.replace(m.group(0),
  '<section class="feed" id="feedbox" aria-label="Deadline feed"><div class="feedmini"><span class="fh">' + h2 + '</span>' + mini_btn + '</div>'
  '<p class="fshort">Subscribe once. Reminders 7 days and 1 day before.</p>'
  '<details class="feedopt"><summary>Options' + CHEV + '</summary>' + p1 +
  '<p>Google Calendar often refreshes subscribed feeds only after 12 to 24 hours.</p>' + big + alt + '</details></section>\n<!-- audience-notes-start -->')

# ---------- 4b. iOS install hint (T18) ----------
m = re.search(r'(<div class="ioshint" id="ioshint" hidden><button class="x" type="button" aria-label="Dismiss install hint">×</button>)(.*?)</div>', s, re.S)
assert m
s = s.replace(m.group(0), m.group(1) + '<details class="iosd"><summary><strong>Install:</strong> Share → Add to Home Screen.' + CHEV + '</summary><p>' + m.group(2) + '</p></details></div>')

# ---------- 5. filters into a sheet; T14 short + F2, T15 short + full ----------
m = re.search(r'<!-- audience-notes-start -->\n(<p class="audhelp".*?</p>)\n(<p class="audempty".*?</p>)\n<!-- audience-notes-end -->\n<div class="bar" id="bar"><div class="chiprow">(<button type="button" class="chip reset" id="reset" aria-pressed="true">All</button>)</div>\n<!-- audience-bar-start -->\n(.*?)<!-- audience-bar-end -->(.*?)</div>\n<p id="count" role="status"></p>', s, re.S)
assert m
audhelp, audempty, reset, audbar, rest = m.groups()
t14 = ('<details class="audhelp2" id="aud-help"><summary>Guidance, not eligibility. ' + INFO_SM + '</summary>'
       '<p class="audhelp">' + esc(F2) + '</p></details>')
audbar = audbar.replace('<h2 class="audheading" id="aud-heading">Audience</h2>\n', '<h2 class="audheading" id="aud-heading">Audience</h2>\n' + t14 + '\n')
assert 'No entries carry the selected audience labels.' in audempty
audempty = audempty.replace('<p class="audempty"', '<div class="audempty"').replace('</p>', '</div>')
audempty = audempty.replace('No entries carry the selected audience labels. Entries without an audience label stay in All.',
  '<details><summary>No entries for these audience labels.' + CHEV + '</summary>No entries carry the selected audience labels. Entries without an audience label stay visible under All.</details>')
rows = re.findall(r'<div class="chiprow" role="group" aria-label="([^"]+)">(.*?)</div>', rest)
assert len(rows) == 3, rows
groups = ''.join('<h2 class="fgh" id="fg-%d">%s</h2><div class="chiprow wrapr" role="group" aria-labelledby="fg-%d">%s</div>' % (i, lab, i, inner) for i, (lab, inner) in enumerate(rows))
sheet = ('<div class="bar" id="bar"><details class="fsheet" id="fsheet"><summary class="fbtn">' + ICON_FILTER +
  '<span>Filters</span> <span class="fn" id="fn">(0 active)</span>' + CHEV + '</summary>'
  '<div class="sheet" role="group" aria-label="Filters"><div class="sheethead"><h2 class="sheett">Filters</h2>' + reset.replace('class="chip reset"', 'class="chip reset" title="Clear all filters"') +
  '<button type="button" class="done" id="fdone">Done</button></div>\n<!-- audience-notes-start --><!-- audience-notes-end -->\n<!-- audience-bar-start -->\n' + audbar + '<!-- audience-bar-end -->' + groups + '</div></details>'
  '<p id="count" role="status"></p></div>\n' + audempty)
s = s.replace(m.group(0), sheet)

# ---------- 6. cards ----------
i_data = s.find('<script type="application/json"')
head, tail = s[:i_data], s[i_data:]
F1LINK = '<a class="ib" href="#about-data" data-f1 aria-label="About this data">' + INFO_SM + '</a>'
def card(mm):
    a = mm.group(0)
    lbl_m = re.search(r'<p class="lbl">([^<]*)</p>', a)
    lbl = lbl_m.group(0)
    if lbl_m.group(1) == 'Title as published (original language, unedited)':                                   # T07
        lbl_short, lbl_full = 'As published', 'Title as published (original language, unedited).'
    else:                                                                                                       # T08
        assert lbl_m.group(1) == 'Our own short description (edited) – see the programme page for the official title', lbl_m.group(1)
        lbl_short, lbl_full = 'Our short description', 'Our own short description (edited) – see the programme page for the official title.'

    dl = re.search(r'<dl>(.*?)</dl>', a, re.S)
    pairs = re.findall(r'(<dt>(.*?)</dt><dd>(.*?)</dd>)', dl.group(1), re.S)
    assert len(pairs) == 4, pairs
    key = ''.join(p for p, t, d in pairs if t not in ('CPV', 'Reference'))   # buyer/programme + deadline row (any deadline_label) stay visible
    sec = ''; t06 = ''
    for p, t, d in pairs:
        if t not in ('CPV', 'Reference'): continue
        if t == 'CPV' and 'not in our extract – see original' in d:          # T06
            p = '<dt>CPV</dt><dd>Not in extract</dd>'; t06 = '<p class="hint">CPV is not in our extract – see the original notice.</p>'
        sec += p
    acts = re.search(r'<p class="acts">(<a class="btn2".*?</a>)(<span class="hint">.*?</span>)</p>\n', a, re.S)
    acc_m = re.search(r'<p class="acc">Accessed (\d\d \w\w\w \d{4}) \(last check\) · As published by source, no guarantee – check the original\.</p>\n', a)
    assert acc_m
    flags = re.findall(r'<p class="flag">(.*?)</p>', a, re.S)
    new = a.replace(lbl, '').replace(acc_m.group(0), '')
    # T04 checked date + T07 short label, visible
    new = re.sub(r'(<p class="meta"><span class="ctry">.*?</span> · <span class="src">.*?</span>)</p>',
                 r'\1 · <span class="chk">Checked ' + acc_m.group(1) + '</span>' + F1LINK.replace('\\', '\\\\') + '</p>', new, count=1)
    new = new.replace('</a></h3>\n', '</a> <span class="lbls">' + lbl_short + '</span></h3>\n', 1)
    new = new.replace(dl.group(0), '<dl class="key">' + key + '</dl>')
    # T11 time-uncertain flags: short visible summary, case note verbatim in body
    # T10 default time note, T12 correction / newer-notice flags (short visible summary incl. notice id; full text in body)
    for fl in flags:
        if fl.startswith('Time uncertain:'): short = 'Time uncertain – confirm on the notice'                       # T11
        elif fl.startswith('No time stated'): short = 'No time stated – 23:59 local assumed, submit earlier'        # T10
        elif fl.startswith('⚠ Newer notice '):                                                                       # T12
            short = '⚠ Newer notice ' + re.match(r'⚠ Newer notice (\S+)', fl).group(1) + ' – not yet reviewed'
        elif fl.startswith('⚠ Correction notice(s) '):                                                               # T12
            short = '⚠ Correction notice(s) ' + re.match(r'⚠ Correction notice\(s\) (.*?) published', fl).group(1) + ' published'
        else: continue   # unknown flag: stays a visible <p class="flag"> unchanged (never hidden)
        new = new.replace('<p class="flag">' + fl + '</p>',
          '<details class="flag"><summary><strong>' + short + '</strong>' + CHEV + '</summary><p>' + fl + '</p></details>')
    det = ('<details class="cdet"><summary>Details' + CHEV + '</summary>'
           '<p class="lbl">' + lbl_full + '</p>'
           '<dl>' + sec + '</dl>' + t06 + '<p class="dynfull"></p>'
           '<p class="hint"><a href="#about-data" data-f1>About this data</a></p></details>')
    new = new.replace(acts.group(0), '<div class="acts">' + acts.group(1) + '<span class="hint t03">One-off file · no updates' + F1LINK + '</span>' + det + '</div>\n')
    return new
head, n = re.subn(r'<article class="card".*?</article>', card, head, flags=re.S)
assert n == N_ENTRIES, (n, N_ENTRIES)
head = head.replace('<details class="abbr">', maplink + '<details class="abbr">', 1)
s = head + tail

# ---------- 7. view-list layout wrapper (desktop side bar) ----------
s = sub1(r'(<div id="view-list">\n)(<div class="views".*?</section>\n)', r'\1<div class="lay-top">\2</div>\n', s)
s = sub1(r'(<div class="bar" id="bar">)', r'<div class="lay"><aside class="lay-side">\1', s)
s = s.replace('<p id="count" role="status"></p></div>\n<div class="audempty"', '<p id="count" role="status"></p></div></aside>\n<div class="lay-main"><div class="audempty"', 1)
s = sub1(r'(</dl></details>\n)(</div>\n<div id="view-about")', r'\1</div></div>\n\2', s)

# ---------- 8. CSS ----------
CSS = r'''<style id="slim-css">
/* library-slim proposal 2026-11-13 – placement only */
summary{list-style:none;cursor:pointer}summary::-webkit-details-marker{display:none}
.chev{flex:none;transition:transform .15s}details[open]>summary .chev{transform:rotate(180deg)}
.hero{padding-top:calc(14px + env(safe-area-inset-top));padding-bottom:12px}
.hero h1{font-size:20px;margin:2px 0 4px}
.hero .k{margin:0}
.intro>summary{display:flex;align-items:center;gap:8px;min-height:44px;color:#DCE5EC;font-size:14px}
.intro .lead{flex:1;outline:1px dashed rgba(233,120,40,.7);outline-offset:2px;border-radius:2px}
.mo{display:inline-flex;align-items:center;gap:2px;color:#FFD2AE;font-size:13px;white-space:nowrap;text-decoration:underline;text-underline-offset:2px}
.intro p{font-size:14px;margin:0 0 6px}
.hero .s{font-size:12px;margin:0}
details.note{background:none;border:0;border-bottom:1px solid var(--line);padding:0;margin:0 0 4px;border-radius:0;font-size:13px}
details.note>summary{display:flex;align-items:center;gap:8px;min-height:44px;color:var(--mut)}
details.note>summary .ic{color:var(--or)}
details.note .mo{color:var(--navy);margin-left:4px}
details.note p{margin:0 0 10px;padding:8px 10px;background:#FFF4EA;border-left:3px solid var(--or);border-radius:4px;color:#1B2B38}
.views{margin:8px 0 6px;flex-wrap:nowrap;overflow-x:auto;scrollbar-width:none}.views::-webkit-scrollbar{display:none}
.views a{min-height:44px;padding:6px 14px;font-size:14px;flex:none}
.feed{position:relative;border:1px solid var(--line);padding:2px 130px 0 12px;margin:6px 0 8px;min-height:64px}
.feed .feedmini .btn1.sm{position:absolute;top:8px;right:8px}
.feedopt[open]{margin-right:-118px}
.feed .feedmini{display:block!important;margin:6px 0 0;font-weight:600;font-size:14px}
.feed .feedmini .fh{flex:1;line-height:1.3}
.feedopt>summary{display:inline-flex;align-items:center;gap:4px;min-height:44px;font-size:13px;color:var(--navy);text-decoration:underline;text-underline-offset:2px}
.feedopt p{font-size:13px;margin:0 0 8px;padding-right:8px}.feedopt .feedalt{font-size:13px;margin:0 0 8px}
.feedmini .btn1.sm{min-height:44px;padding:6px 12px;font-size:14px}
.feed.compact>*{display:revert}
/* filter bar */
.bar{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid var(--line);z-index:20}
.bar #count{margin:0;font-size:13px;flex:1;text-align:right}
.fbtn{display:inline-flex;align-items:center;gap:6px;min-height:44px;padding:6px 14px;border:1px solid var(--navy);border-radius:22px;background:#fff;color:var(--navy);font-weight:700;font-size:14px;white-space:nowrap}
.fbtn .fn{font-weight:400;color:var(--mut)}.fsheet.on .fbtn{background:var(--navy);color:#fff}.fsheet.on .fbtn .fn{color:#FFD2AE;font-weight:700}
.sheet{background:#fff}
.sheethead{display:flex;align-items:center;gap:8px;position:sticky;top:0;background:#fff;padding:10px 0;border-bottom:1px solid var(--line);z-index:1}
.sheett{flex:1;margin:0;font-size:17px;color:var(--navy)}
.done{min-height:44px;padding:6px 18px;border:0;border-radius:22px;background:var(--or);color:#fff;font:inherit;font-weight:700;cursor:pointer}
.sheet .chip{min-height:44px}
.fgh{font-size:15px;color:var(--navy);margin:14px 0 6px}
.chiprow.wrapr{flex-wrap:wrap;overflow:visible;gap:8px}.chiprow.wrapr.fade{-webkit-mask-image:none;mask-image:none}
.sheet .audblock{margin-top:12px}.sheet .audhelp{font-size:13px;color:var(--mut);margin:0 0 10px}
.sheet .audchip{font-size:15px;padding:6px 12px}
@media (max-width:899px){
 .lay,.lay-side,.lay-main{display:contents}
 .fsheet[open]>.sheet{position:fixed;left:0;right:0;bottom:0;max-height:82vh;overflow:auto;z-index:1300;padding:0 16px calc(20px + env(safe-area-inset-bottom));border-radius:16px 16px 0 0;box-shadow:0 0 0 100vmax rgba(15,42,61,.55);overscroll-behavior:contain}
}
/* cards */
#list{gap:10px;grid-template-columns:minmax(0,1fr)}
.card{min-width:0;overflow-wrap:break-word}
.card .top .auds{flex:0 1 auto;width:auto}
.card{padding:12px 12px 6px}
.card .top{gap:4px 6px}
.card .auds{margin:2px 0 0;gap:4px}
.card .audfor{font-size:12px}.card .aud{font-size:12px;padding:1px 8px 1px 4px;gap:4px}.card .aud .audsym{width:18px;height:18px}
.card h3{font-size:16px;margin:4px 48px 6px 0}
.meta{font-size:12px}
dl.key{margin:4px 0;font-size:14px;gap:2px 10px;grid-template-columns:fit-content(7.5em) minmax(0,1fr)}
dl.key strong{font-weight:700}
dl.key dd br{display:none}
.cd{font-size:12px;margin:2px 0 0 0;padding:1px 8px}.cd.past{background:#EEF1F4;color:#5B6B7A;border:1px solid #C8D2DC}
dl.key .cd{display:inline-block}dl.key .chg:not([hidden]){display:block}
.acts{display:flex;flex-wrap:wrap;align-items:center;gap:4px 8px;margin:6px 0 4px}
.acts .btn2{min-height:44px}
.cdet{flex:1 1 auto}
.cdet>summary{display:inline-flex;align-items:center;gap:4px;min-height:44px;padding:0 8px;font-size:14px;color:var(--navy);text-decoration:underline;text-underline-offset:2px}
.cdet[open]{flex-basis:100%;order:2;border-top:1px solid var(--line);margin-top:4px}
.cdet .lbl{margin:6px 0 4px}.cdet dl{font-size:13px;margin:4px 0}.cdet .hint{display:block;margin:4px 0}.cdet .acc{margin:4px 0 8px}
.maplink{display:flex;flex-wrap:wrap;align-items:center;gap:2px 6px;min-height:48px;background:var(--navy);color:#fff;border-left:5px solid var(--or);border-radius:10px;padding:10px 14px;margin:12px 0;text-decoration:none;font-weight:700;font-size:14px}
.maplink:hover{color:#fff}.maplink .ml2{font-weight:400;color:#C8D2DC}
.abbr summary{min-height:44px}
@media (min-width:900px){
 body{font-size:16px}
 .hero{padding:18px 24px}.hero h1{font-size:26px}
 .intro>summary{display:none}.intro p{font-size:15px;color:#DCE5EC;margin:4px 0}
 details.note[open]>summary .mo{display:none}
 .lay-top{display:flex;align-items:flex-start;gap:16px;flex-wrap:wrap}.lay-top .views{flex:1}.lay-top .feed{flex:0 1 520px;margin-top:8px}
 .lay{display:grid;grid-template-columns:290px 1fr;gap:20px;align-items:start}
 .lay-side{position:sticky;top:64px;max-height:calc(100vh - 72px);overflow:auto;background:#fff;border:1px solid var(--line);border-radius:10px;padding:4px 14px 12px}
 .bar{position:static;flex-direction:column;align-items:stretch;border:0;background:none;padding:0}
 .bar #count{text-align:left;order:-1;margin:8px 0 0}
 .fbtn{border:0;padding:6px 0;border-radius:0;background:none!important;color:var(--navy)!important}
 .sheethead{display:none}
 .sheet{padding:0}.sheet .audblock{margin-top:4px}
 #list{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}
 .feed{padding-top:8px}
}
/* v2 */
.intro>summary{display:block!important;padding:4px 0}.lead1{color:#DCE5EC;font-size:14px;line-height:1.45}.intro .mo{display:inline-flex;vertical-align:baseline;gap:3px;min-height:24px}
.intro>summary{min-height:44px}.intro .lt{color:#FFD2AE}
details.note>summary strong{color:#1B2B38}
.f1{margin:0 0 10px;padding:8px 10px;background:#FFF4EA;border-left:3px solid var(--or);border-radius:4px}
details.note .f1 p{margin:0 0 8px;padding:0;background:none;border:0;border-radius:0}.fh2{font-size:14px;margin:4px 0 4px;color:var(--navy)}
.ic.sm{width:16px;height:16px;vertical-align:-3px}
.ib{display:inline-flex;align-items:center;justify-content:center;min-width:44px;min-height:44px;margin:-14px -10px -14px -6px;color:var(--navy)}
.meta .chk{white-space:nowrap}
.lbls{display:inline-block;font-size:11px;font-weight:400;color:var(--mut);border:1px solid var(--line);border-radius:8px;padding:0 6px;vertical-align:2px;white-space:nowrap}
.t03{flex:1 1 90px;font-size:12px;line-height:1.3;color:var(--mut)}.t03 .ib{margin:-12px -10px -12px -8px}
.acts{gap:4px 6px}
.cdet>summary{padding:0 4px}
.cdet .dynfull:empty{display:none}.cdet .dynfull{font-size:12px;color:#8A3E05;margin:4px 0}
details.flag{padding:0;margin:6px 0}details.flag>summary{display:flex;align-items:center;gap:6px;min-height:44px;padding:0 8px;color:#7A3B00}details.flag p{margin:0;padding:0 8px 8px;font-size:13px}
.feed{padding:8px 12px 2px!important}.feed .feedmini .btn1.sm{top:auto!important;bottom:6px}.feedopt[open]{margin-right:0!important;padding-bottom:52px}.fshort{margin:2px 0 0;font-size:12px;color:var(--mut)}
.audhelp2>summary{display:inline-flex;align-items:center;gap:6px;min-height:44px;font-size:14px;color:var(--navy);font-weight:600}
.sheet .audhelp{margin:0 0 10px}
.audempty details>summary{display:inline-flex;align-items:center;gap:4px;min-height:44px}
.iosd>summary{display:flex;align-items:center;gap:6px;min-height:44px;flex-wrap:wrap}.iosd p{margin:4px 0 0}
.ioshint{padding:4px 44px 4px 12px;margin:8px 0}
@media (min-width:900px){.lead1{font-size:15px}.intro>summary{display:block!important;min-height:0;padding:0}.hero .intro p{margin:2px 0 6px}.intro[open] .mo{display:none}}
</style>'''
s = s.replace('</head>', CSS + '\n</head>', 1)

# ---------- 9. JS (minimal) ----------
old_tick = 'cd.className="cd "+cls;cd.textContent=t+(tzn?" · "+tzn+" ("+e.tz.replace("_"," ")+")":"");'
assert old_tick in s
s = s.replace(old_tick, 'if(ms<=0)cls="past";cd.className="cd "+cls;cd.textContent=t+(tzn?" · "+tzn+" ("+e.tz.replace("_"," ")+")":"");')
old_t05 = 'if(ms<=0)t="Deadline passed – check the original";'
assert old_t05 in s
s = s.replace(old_t05, 'if(ms<=0)t="Deadline passed";/* T05: short visible label + time zone; "check the original" lives in F1 */')
old_t09 = 'x.textContent="Check the original – times may differ.";}else if(x)x.remove();'
assert old_t09 in s
s = s.replace(old_t09, 'x.textContent="Times may differ";}else if(x)x.remove();var df=c.querySelector(".dynfull");if(df){var st0=df.dataset.stale||"";df.textContent=(cls==="hot"?"Check the original notice – times may differ. ":"")+st0;}')
old_t13 = "h='<span class=\"stale\">Not re-checked since '+esc(fdate(e.checked))+' – verify on the original</span>';"
assert old_t13 in s, old_t13
s = s.replace(old_t13, "h='<span class=\"stale\">Not re-checked since '+esc(fdate(e.checked))+'</span>';var dfs=c.querySelector('.dynfull');if(dfs)dfs.dataset.stale='Not re-checked since '+fdate(e.checked)+' – verify on the original.';")
old_fb = 'var fb=document.getElementById("feedbox");if(prev.last&&!get("ss_feedopen",0))fb.classList.add("compact");\ndocument.getElementById("feedmore").addEventListener("click",function(){fb.classList.remove("compact");});'
assert old_fb in s
s = s.replace(old_fb, '''/* --- filter sheet (slim) --- */
var fs=document.getElementById("fsheet"),wide=matchMedia("(min-width:900px)");
function syncWide(){if(wide.matches){fs.open=true;document.querySelectorAll(".hero .intro").forEach(function(d){d.open=true;});}}
syncWide();wide.addEventListener("change",syncWide);
document.getElementById("fdone").addEventListener("click",function(){fs.open=false;fs.querySelector("summary").focus();});
document.addEventListener("click",function(ev){if(!wide.matches&&fs.open&&!fs.contains(ev.target))fs.open=false;});
[].forEach.call(document.querySelectorAll("a[data-f1]"),function(l){l.addEventListener("click",function(){var d=document.getElementById("about-data");d.open=true;});});
document.addEventListener("keydown",function(ev){if(ev.key==="Escape"&&fs.open&&!wide.matches){fs.open=false;fs.querySelector("summary").focus();}});''')
old_rc = ' if(audAll)audAll.setAttribute("aria-pressed",audKeys.length?"false":"true");\n/* audience-count-end */'
assert old_rc in s
s = s.replace(old_rc, old_rc + '\n var na=Object.keys(sel).reduce(function(t,g){return t+Object.keys(sel[g]).length;},0),fnx=document.getElementById("fn");if(fnx){fnx.textContent="("+na+" active)";document.getElementById("fsheet").classList.toggle("on",na>0);}')
DST.write_text(s)
print("ok", len(s))
