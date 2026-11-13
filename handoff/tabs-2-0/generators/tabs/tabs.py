"""SpudSignal Library 2.0 – tabs stage (final build stage, runs after the page generators).
Adds the shared shell to every page: tab bar Library | Tenders | Map, What's new + "Update 2.0", shared /assets/spudsignal.css,
URL filters (/assets/ss-url.js), glossary as approved (v2.1), Library search / expired-hidden / header count, Tenders single column,
map presentation #1-#14 (Kartograf), #about-data hash opener, /whats-new/ page.
Usage (from library/):  python3 tabs/tabs.py site            (or any built site dir, e.g. a repo clone)
Idempotent: the first run on a fresh generator page stores it under tabs/pretabs/<page>; pages that already carry
data-ss-tabs are rebuilt from that stored copy. Data files (data.js, testlayers.js, tenders JSON block, data.py) are never touched.
Needs python3 + bs4."""
import re, os, sys, shutil, json, datetime, html as H
from bs4 import BeautifulSoup
HERE=os.path.dirname(os.path.abspath(__file__))
SITE=os.path.abspath(sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,"..","site"))
PRE=os.path.join(HERE,"pretabs"); ASSETS=os.path.join(HERE,"assets")
LOG=[]  # (page, id, kind, old, new)
def log(page, cid, kind, old, new=""): LOG.append({"page":page,"id":cid,"kind":kind,"old":old,"new":new})
MARK='data-ss-tabs="2.0"'
def rd(p):
    cur=open(os.path.join(SITE,p),encoding="utf-8").read(); pre=os.path.join(PRE,p)
    if MARK in cur[:2000]:
        assert os.path.exists(pre), f"{p} already has the tabs shell but no stored pre-tabs copy in {PRE}"
        return open(pre,encoding="utf-8").read()
    os.makedirs(os.path.dirname(pre),exist_ok=True); open(pre,"w",encoding="utf-8").write(cur); return cur
def wr(p,s):
    os.makedirs(os.path.dirname(os.path.join(SITE,p)),exist_ok=True)
    if p!="whats-new/index.html": s=s.replace("<html",'<html '+MARK,1) if MARK not in s[:2000] else s
    open(os.path.join(SITE,p),"w",encoding="utf-8").write(s)
os.makedirs(os.path.join(SITE,"assets"),exist_ok=True)
for f in sorted(os.listdir(ASSETS)): shutil.copyfile(os.path.join(ASSETS,f),os.path.join(SITE,"assets",f))
VER="2.0"
def rep(s, old, new, page, cid, n=None, kind="glossary"):
    c = s.count(old)
    assert c>0, (page,cid,old)
    if n is not None: assert c==n, (page,cid,old,c)
    log(page,cid,kind,old,new); return s.replace(old,new)
# ---------- shared pieces
ICON={"lib":'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M4 19.5V5a2 2 0 0 1 2-2h13v16H6.5A2.5 2.5 0 0 0 4 21.5z"/><path d="M8 7h7"/><path d="M8 11h7"/></svg>',
 "ten":'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M3 12h.01"/><path d="M3 18h.01"/><path d="M3 6h.01"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M8 6h13"/></svg>',
 "map":'<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M20 10c0 5-8 12-8 12s-8-7-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/></svg>'}
def nav(cur, sub=False):
    def a(k,href,label):
        c=(' aria-current="true"' if sub else ' aria-current="page"') if k==cur else ''
        return f'<a class="tab" href="{href}" data-carry="{href}"{c}>{ICON[k]}<span>{label}</span></a>'
    wn=' aria-current="page"' if cur=="wn" else ''
    # brand stays the live "SpudSignal Library" (glossary decision B open)
    return ('<a class="skip" href="#content">Skip to content</a><nav class="appnav" aria-label="Main"><a class="ab" href="/" data-carry="/"><img src="/map/logo-v3-dark.png" alt="" width="32" height="32"><b>SpudSignal Library</b></a>'
            '<div class="al">'+a("lib","/","Library")+a("ten","/tenders/","Tenders")+a("map","/map/","Map")+'</div>'
            f'<a class="wn" href="/whats-new/"{wn}><span>What’s new</span><span class="vtag" data-version>Update {VER}</span></a></nav>')
# footer: identical structure on every page. Liability sentence per page (glossary decision E open for /projects/).
MEDIA="Media owner and publisher: Daniel Hirschl, Ortsstraße 28, 3493 Kammern, Austria. SpudSignal is a neutral, independent briefing on European geothermal news."
LIAB_HOME_LIVE="All documents are linked to their original publishers. Liability: entries are provided for information only, without guarantee of completeness or accuracy; the original document is authoritative."
import re as _re
_m=_re.search(r'Media owner and publisher: Daniel Hirschl, Ortsstraße 28, 3493 Kammern, Austria\. SpudSignal is a neutral, independent briefing on European geothermal news\. (.*?)</p>',rd("projects/index.html"))
assert _m and _m.group(1)==LIAB_HOME_LIVE, "live /projects/ liability differs from approved H05 wording"
LIAB_H05=_m.group(1)  # source: live /projects/ (approved H05); identical to Reviewer v2 wording
LIAB_HOME_NEW=LIAB_TEN_NEW=LIAB_H05
LINKS=('<p class="ss-links"><a href="https://impressum.spudsignal.com">Impressum &amp; disclaimer</a> &nbsp;·&nbsp; <a href="https://privacy.spudsignal.com">Privacy</a> &nbsp;·&nbsp; '
       '<a href="/tenders/#about-data">About &amp; Sources</a> &nbsp;·&nbsp; <a href="/whats-new/">What’s new</a><a class="vtag2" href="/whats-new/" aria-label="Update '+VER+' – what’s new">Update '+VER+'</a> &nbsp;·&nbsp; '
       '<a href="https://spudsignal.beehiiv.com/subscribe">Subscribe free</a></p>')
def footer(liab, extra=""): return f'<footer class="ss-foot" data-ss-footer>{extra}<p>{MEDIA} {liab}</p>{LINKS}</footer>'
AUD="Audience labels are guidance, not eligibility. Check the original source for requirements and deadlines."
INFO_LIST="All shows every entry, including those without an audience label. If you select more than one audience, an entry is shown when it carries any of those labels. These labels combine with other filter groups. The same labels filter the map; a pin is labelled only when its source URL matches an assignment."
INFO_MAP="All shows every pin, including those without an audience label. If you select more than one audience, a pin is shown when it carries any of those labels. A pin is labelled only when its source URL matches an assignment."
CSSLINK='<link rel="stylesheet" href="/assets/spudsignal.css">'
URLJS='<script src="/assets/ss-url.js" defer></script>'
NAVRE=re.compile(r'(<!-- appnav v3 -->)?<nav class="appnav" aria-label="Main">.*?</nav>',re.S)
APPNAV_CSS=re.compile(r'<style id="appnav-css">.*?</style>',re.S)
def shell(s,page,cur,sub=False):
    assert len(NAVRE.findall(s))==1; s=NAVRE.sub("",s); log(page,"S-nav","shell","appnav v3 (Home|Tenders|Map)","tab bar Library|Tenders|Map + What’s new")
    n=len(APPNAV_CSS.findall(s)); assert n==1,(page,n); s=APPNAV_CSS.sub("",s); log(page,"CSS-nav","css-removed","local <style> appnav v3 block","→ assets/spudsignal.css §8")
    s=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+nav(cur,sub),s,count=1)
    s=s.replace("</head>",CSSLINK+URLJS+"</head>",1)
    if 'class="has-appnav"' not in s: s=s.replace("<body>",'<body class="has-appnav">',1)
    return s
def nodata(fn):  # apply fn to everything except the JSON data block (data stays byte-identical)
    def g(s):
        i=s.find('<script type="application/json" id="data">')
        if i<0: return fn(s)
        j=s.find("</script>",i); return fn(s[:i])+s[i:j]+fn(s[j:])
    return g
MON="Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec"
# ======================= HOME (Library) =======================
page="home"; s=rd("index.html")
s=shell(s,page,"lib")
soup=BeautifulSoup(s,"html.parser")
body=soup.body; del body["style"]; log(page,"CSS-body","css-removed","body inline style (margin, background)","→ shared")
outer=body.find("div",recursive=False); assert "max-width:860px" in outer["style"]
del outer["style"]; outer["class"]="ss-wrap"; log(page,"CSS-wrap","css-removed","inline font stack -apple-system… + max-width:860px","→ .ss-wrap (DejaVu stack, 1100px)")
hero=outer.find("div",recursive=False); assert "border-radius:16px" in hero["style"]
hero.name="header"; del hero["style"]; hero["class"]="ss-head"
ps=hero.find_all("p"); ps[0]["class"]="k"; h1=hero.find("h1"); h1["id"]="content"; h1["tabindex"]="-1"
for t in [ps[0],h1,ps[1],ps[2]]: del t["style"]
ps[2]["class"]="s"
assert "102 primary sources" in ps[2].get_text()
_rest=ps[2].get_text().replace("102 primary sources","",1); ps[2].clear(); _sp=soup.new_tag("span",attrs={"id":"ss-hcount"}); _sp.string="102 entries"; ps[2].append(_sp); ps[2].append(_rest)
log(page,"H-count","new","header count = all 102 regardless of what is shown","with JS: “64 current entries (38 expired hidden · show)” from real counts, updates with the toggle; without JS: “102 entries”")
log(page,"G-entry","glossary","102 primary sources · 21 countries + EU · updated weekly","102 entries · 21 countries + EU · updated weekly")
log(page,"CSS-h1","css-removed","H1 inline 34px","→ --h1 28px")
# banners (two big teaser links) – removed; contents logged
for a in outer.find_all("a",class_="tl"):
    log(page,"H-banner","removed",a.get_text(" ",strip=True),"(tab bar Tenders / Map)"); a.decompose()
for st in outer.find_all("style"):
    if ".tl{" in st.text: st.decompose()
# audience text
ah=soup.find(id="aud-help"); log(page,"G-aud","glossary",ah.get_text(),AUD+" ‖ info: "+INFO_LIST); ah.string=AUD
info=soup.new_tag("p",attrs={"class":"audhelp ss-info"}); info.string=INFO_LIST; ah.insert_after(info)
# country chips (flag+name jump links) -> shared chip, names only
chips_p=None
for p in outer.find_all("p",recursive=False):
    if p.find("a",href=re.compile(r"^#lib-")): chips_p=p; break
del chips_p["style"]; chips_p.name="nav"; chips_p["class"]="ss-chips"; chips_p["aria-label"]="Countries"
for a in chips_p.find_all("a"):
    del a["style"]; a["class"]="ss-chip"; old=a.get_text(); new=re.sub(r"^\W+","",old).strip()
    if old!=new: a.string=new
log(page,"G-country","glossary","country jump chips with flag emoji (e.g. “🇦🇹 Austria”)","country name only (“Austria”), shared .ss-chip")
# cards
M={m:i+1 for i,m in enumerate(MON.split("|"))}
def parse_dl(t):
    seg=t.split("closes")[-1] if "closes" in t else t
    zone=None
    for z,off in (("CEST","+02:00"),("TRT","+03:00"),("Iceland time","+00:00"),("Irish time","+00:00")):
        if re.search(z,re.sub(r"\(.*?\)","",seg)): zone=off
    seg2=re.sub(r"\(.*?\)","",seg)
    d=re.search(rf"(\d{{1,2}}) ({MON})(?: (\d{{4}}))?",seg2)
    if not d: return None
    tm=re.search(r"(\d{1,2}):(\d\d)",seg2); y=int(d.group(3) or 2026); mo=M[d.group(2)]; dd=int(d.group(1))
    if not zone: zone="+02:00" if (mo<10 or (mo==10 and dd<25)) else "+01:00"
    hh,mm=(int(tm.group(1)),int(tm.group(2))) if tm else (23,59)
    return f"{y:04d}-{mo:02d}-{dd:02d}T{hh:02d}:{mm:02d}:00{zone}"
deadlines=[]
TYPES={"Tender":"t-tender","Project":"t-project","Funding":"t-funding","Licence":"t-licence","Study/Data":"t-study"}
for c in soup.find_all("div",class_="libcard"):
    del c["style"]; c["class"]=["libcard","ss-card"]
    b=c.find("span",recursive=False); bt=b.get_text().strip(); assert bt in TYPES,bt
    del b["style"]; b["class"]=["ss-badge",TYPES[bt]]; c["data-type"]=TYPES[bt][2:]
    pp=c.find_all("p",recursive=False)
    pp[0]["class"]="ss-ct"; pp[1]["class"]="ss-cd"; pp[-1]["class"]="ss-cm"
    for el in c.find_all(style=True): 
        st=el["style"]
        if "background:#FDEBDD" in st: el["class"]="ss-dl"
        if "background:#ECEFF2" in st and "line-through" in st: el["class"]=["ss-dl","past"]; c["data-past-build"]="1"
        del el["style"]
    chip=c.find("span",class_="ss-dl")
    if chip:
        iso=parse_dl(chip.get_text()); 
        if iso: c["data-deadline"]=iso
        deadlines.append({"title":pp[0].get_text(strip=True)[:90],"chip":chip.get_text(strip=True),"deadline":iso,"past_at_build":c.get("data-past-build")=="1"})
        tag=soup.new_tag("span",attrs={"class":"ss-past","hidden":""}); tag.string="Deadline passed"; chip.insert_after(tag)
log(page,"CSS-card","css-removed","inline styles on 102 cards (card, badge, title, text, meta, deadline chip)","→ .ss-card/.ss-badge/.ss-dl")
log(page,"CSS-badge","css-removed","badge colours inline (Tender #E97828, Project #1F6FB2, Funding #1E8A5A, Licence #6B4FA0, Study/Data #24435A)","→ one colour per type (shared)")
for h2 in outer.find_all("h2",id=re.compile("^lib-")): del h2["style"]; h2["class"]="ss-h2"
# CTA box
cta=[d for d in outer.find_all("div",recursive=False) if d.get("style","").startswith("background:#E97828")][0]
for el in [cta]+cta.find_all(style=True): del el["style"]
cta["class"]="ss-cta"; cta.find("p")["class"]="t"
# layout: sidebar (search, past toggle, audience, countries) + list
side=soup.new_tag("aside",attrs={"class":"ss-side","aria-label":"Filters"}); lst=soup.new_tag("div",attrs={"class":"ss-list","id":"liblist"})
tools=BeautifulSoup('<div id="ss-tools" hidden><div class="ss-search" role="search"><label for="ss-q">Search the Library</label><input id="ss-q" type="search" autocomplete="off" placeholder="Title, place, buyer, notice number"></div>'
 '<label class="ss-toggle"><input type="checkbox" id="ss-past"><span>Show entries whose deadline has passed (<span id="ss-npast">0</span>)</span></label></div>',"html.parser")
lay=soup.new_tag("div",attrs={"class":"ss-lay"})
start=soup.find(string=lambda t: isinstance(t,str) and "audience-notes-start" in t)
nodes=[]; n=start
while n is not None and n is not cta: nodes.append(n); n=n.next_sibling
side.append(tools)
for x in nodes:
    x=x.extract()
    if getattr(x,"name",None)=="div" and "libcard" in (x.get("class") or []) or (getattr(x,"name",None)=="h2" and str(x.get("id","")).startswith("lib-")): lst.append(x)
    else: side.append(x)
h=soup.new_tag("h2"); h.string="Countries"; chips=side.find("nav",class_="ss-chips"); chips.insert_before(h)
lay.append(side); lay.append(lst); cta.insert_before(lay)
# footer
oldf=soup.find("footer"); oldf.replace_with(BeautifulSoup(footer(LIAB_HOME_NEW),"html.parser"))
log(page,"H05-liab","liability","Home footer liability (live)","unchanged: H05 wording copied from live /projects/ (approved)")
for sc in soup.find_all("script",src="/audience/library.js"): sc["src"]="/assets/library.js"
s=str(soup)
s=s.replace('<link rel="stylesheet" href="/assets/spudsignal.css"/>',CSSLINK)
wr("index.html",s)
json.dump(deadlines,open(os.path.join(PRE,"home-deadlines.json"),"w"),indent=1,ensure_ascii=False)
# ======================= TENDERS =======================
page="tenders"; s=rd("tenders/index.html")
s=shell(s,page,"ten")
s=s.replace("<h1>",'<h1 id="content" tabindex="-1">',1)
# remove local styles replaced by shared CSS
for old,new,why in [
 ('font:16px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif;','font-size:16px;line-height:1.5;',"body font stack → shared"),
 ('.wrap{max-width:1100px;margin:0 auto;padding:0 12px}','',"content width → shared"),
 ('.badge{font-size:12px;font-weight:700;padding:2px 8px;border-radius:10px;color:#fff}.badge.tend{background:#2E5E80}.badge.fund{background:#1F6B4F}','',"badge colours (Tender #2E5E80, Funding call #1F6B4F) → shared"),
 ('.hero h1{font-size:28px}','',"H1 size → shared"),
 ('.hero h1{font-size:22px;line-height:1.25;margin:4px 0 8px}','',"H1 size → shared"),
 ('.hero h1{font-size:20px;margin:2px 0 4px}','',"H1 size → shared"),
 ('.hero{padding:18px 24px}.hero h1{font-size:26px}','',"header padding/H1 → shared"),
 ('footer{max-width:1100px;margin:0 auto;padding:8px 12px 32px;font-size:13px;color:#5B6B7A;text-align:center;line-height:1.6}footer a{color:#0F2A3D}','',"footer → shared"),
 (' #list{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}\n','',"2-column grid with gaps → single column (see proposal)"),
 (' #list{grid-template-columns:1fr 1fr}\n','',"2-column grid → single column"),
 ('.cty button,','',"")]:
    if old in s: s=s.replace(old,new); log(page,"CSS-local","css-removed",old[:90],why)
s=s.replace('.lay{display:grid;grid-template-columns:290px 1fr;gap:20px;align-items:start}','.lay{display:grid;grid-template-columns:var(--side) minmax(0,1fr);gap:20px;align-items:start}')
s=s.replace('<span class="badge tend">','<span class="badge tend ss-badge t-tender">').replace('<span class="badge fund">','<span class="badge fund ss-badge t-funding">')
# glossary replacements (visible HTML + JS strings; JSON data untouched)
G=[("G-source","each linked to the original notice","each linked to the original source"),
   ("G-source","Each entry links to the original notice.","Each entry links to the original source."),
   ("G-source","CPV is not in our extract – see the original notice.","CPV is not in our extract – see the original source."),
   ("G-all","stay visible under All","stay in All"),
   ("G-reset",'title="Clear all filters" id="reset" aria-pressed="true">All</button>','title="Clear filters" aria-label="Clear filters" id="reset" aria-pressed="true">Clear filters</button>'),
]
def tg(x):
    for cid,o,n in G:
        if o in x: log(page,cid,"glossary",o,n); x=x.replace(o,n)
    return x
s=nodata(tg)(s)
for cid,o,n in G: assert any(e["old"]==o and e["page"]==page for e in LOG),(cid,o)
# audience texts: filter panel, About this data (F2), About this app
AUD_PANEL_OLD="Audience labels are guidance on who an item is relevant to. They are not eligibility, and they are not a check that a deadline is currently open. All shows every entry. If you select more than one audience, an entry is shown when it carries any of those labels. These labels combine with type, technical category and country. The same labels filter the map by exact source URL."
s=rep(s,f'<p class="audhelp" id="aud-help">{AUD_PANEL_OLD}</p>',f'<p class="audhelp" id="aud-help">{AUD}</p><p class="audhelp ss-info">{INFO_LIST}</p>',page,"G-aud",1)
F2_OLD=re.search(r'<p id="f2">(.*?)</p>',s).group(1)
s=rep(s,f'<p id="f2">{F2_OLD}</p>',f'<p id="f2">{AUD} {INFO_LIST} Audience labels use the same audience assignments on the Library, the Tenders page and the map.</p>',page,"G-aud",1)
APP_OLD="Audience labels use the same assignment record on the Library, the open-tender list and the map. They are guidance, not eligibility, and they are not a check that a deadline is currently open. Several selected labels match an entry that carries any of them. An entry with no label stays visible under All. The map joins a pin only when its source URL is the same URL."
s=rep(s,APP_OLD,f"{AUD} {INFO_LIST}",page,"G-aud",1)
# date without leading zero (visible HTML + JS date format)
s=s.replace('toLocaleDateString("en-GB",{day:"2-digit",','toLocaleDateString("en-GB",{day:"numeric",'); log(page,"G-date","glossary",'JS date format day:"2-digit"','day:"numeric"')
def dz(x):
    x2,n=re.subn(rf'(<strong>)0([1-9]) ({MON}) (20\d\d)',r'\1\2 \3 \4',x)
    if n: log(page,"G-date","glossary",f"{n}× deadline “0D Mon YYYY”","“D Mon YYYY”")
    return x2
s=nodata(dz)(s)
# footer -> shared
oldf=re.search(r'<footer>.*?</footer>',s,re.S).group(0)
s=s.replace(oldf,footer(LIAB_TEN_NEW)); log(page,"S-footer","shell","footer link row: Impressum & disclaimer · Privacy · About & Sources · Source Library · Subscribe free; liability “Liability: listings … the original notice is authoritative.”","shared footer; liability = H05 wording from live /projects/ (approved)")
# About & Sources anchor inside page (dead #about): HOTFIX baseline item
assert '<p><a href="#about-data">About &amp; Sources</a></p>' in s and 'href="#about"' not in s; log(page,"BASE-HOTFIX-2","baseline",'#about-data anchor','already live since 368155e (hotfix PR #7) – not a tabs-package change')
# open About-this-data when linked
s=s.replace("</body>",'<script>/* tabs package (Reviewer PR7 note F-3): open About this data when linked by #about-data */(function(){function o(){if(location.hash==="#about-data"){var d=document.getElementById("about-data");if(d){d.open=true;d.scrollIntoView();}}}o();addEventListener("hashchange",o);})();</script>'
  '</body>',1)
s=s.replace("</head>",'<style>#list{grid-template-columns:minmax(0,1fr)!important;max-width:820px}</style></head>',1)
wr("tenders/index.html",s)
# ======================= MAP =======================
page="map"; s=rd("map/index.html")
s=shell(s,page,"map")
# fonts: local stacks removed → shared
for old in ['html,body{margin:0;height:100%;font-family:"DejaVu Sans",Verdana,system-ui,sans-serif;color:var(--navy)}','.leaflet-popup-content{font-family:inherit;font-size:13px;line-height:1.4;margin:12px 14px}']:
    assert old in s,old
s=s.replace('html,body{margin:0;height:100%;font-family:"DejaVu Sans",Verdana,system-ui,sans-serif;color:var(--navy)}','html,body{margin:0;height:100%;color:var(--navy)}'); log(page,"CSS-font","css-removed","html,body font-family DejaVu stack (local)","→ shared")
s=s.replace('.leaflet-popup-content{font-family:inherit;','.leaflet-popup-content{'); log(page,"CSS-font","css-removed","popup font-family:inherit (= Leaflet Helvetica Neue)","→ shared DejaVu stack")
s=s.replace('.cty{display:flex;flex-wrap:wrap;gap:6px}.cty button{font:inherit;font-size:12px;border:1px solid var(--gb);background:#fff;color:var(--navy);border-radius:14px;padding:3px 9px;cursor:pointer}\n.cty button.on{background:var(--navy);color:#fff;border-color:var(--navy)}','.cty{display:flex;flex-wrap:wrap;gap:6px}'); log(page,"CSS-chip","css-removed","country button style (12px ISO pills)","→ shared .ss-chip")
# panel: title, audience sentence, info, credits behind Sources & credits, B1 visible, footer
s=rep(s,'<aside id="panel">','<aside id="panel"><h1 class="sr-only-m" id="content" tabindex="-1">Geothermal map: projects, tenders &amp; funding</h1>',page,"M-title",1,"map")
AUDNOTE_OLD="Guidance, not eligibility, and not a check that a deadline is currently open. All shows every pin. Several labels match a pin that carries any of them. A pin is labelled only when its source URL is the same URL as an assignment."
s=rep(s,f'<p class="audnote">{AUDNOTE_OLD}</p>',f'<p class="audnote">{AUD}</p>',page,"G-aud",1)
s=rep(s,"No pins carry the selected labels. Pins without a label are hidden while a label is selected. Choose All to see them. This is not a finding that no projects exist.","No pins carry the selected labels. Pins without a label stay in All. This is not a finding that no projects exist.",page,"G-pin",1)
s=rep(s,"Calls without a label stay visible under All.","Calls without a label stay in All.",page,"G-all",1)
DIS_OLD='<p><small>Tender data as published by source, no guarantee – check the original. Pins marked “approx.” sit at town/region level.</small></p>'
assert DIS_OLD in s
NOTICE_OLD=re.search(r'<p class="tnotice">Built from public sources\..*?</p>',s,re.S).group(0)
assert s.count(NOTICE_OLD)==1
s=s.replace(DIS_OLD,'',1); s=s.replace(NOTICE_OLD,'',1)
sect=re.search(r'<section id="about-sources">.*?</section>',s,re.S).group(0)
B1='<p class="tcredh">Locations are approximate unless noted. No coordinate table is offered, and nothing can be downloaded or exported.</p>'
assert B1 in sect
credits=sect.replace(B1,'').replace('<section id="about-sources"><h3>About &amp; Sources</h3>','')[:-len('</section>')]
oldpab='<p class="pab"><small><a href="/tenders/#about-data">About &amp; Sources</a> · <a href="https://impressum.spudsignal.com">Impressum</a> · <a href="https://privacy.spudsignal.com">Privacy</a></small></p>'
assert oldpab in s
s=s.replace(sect,'').replace(oldpab,'')
log(page,"M-pab","map",'panel link row About & Sources · Impressum · Privacy (live, #about-data since 368155e)','moved into the shared footer in the panel')
newinfo=(B1+
 '<details class="minfo" id="map-info"><summary>Info</summary><p><small>Tender data as published by source, no guarantee – check the original. Pins marked “approx.” do not show the exact location.</small></p>'
 f'<p><small>{INFO_MAP}</small></p></details>'
 f'<details class="minfo" id="about-sources"><summary>Sources &amp; credits</summary>{credits}</details>'
 + footer(LIAB_HOME_NEW))
s=s.replace('<p class="pab"><small><a href="/projects/">Project list</a></small></p>','<p class="pab"><small><a href="/projects/">Project list</a></small></p>'+newinfo,1)
log(page,"M-dis","map","Tender data as published by source, no guarantee – check the original. Pins marked “approx.” sit at town/region level.","first sentence unchanged (disclaimer); second sentence per Kartograf #6: Pins marked “approx.” do not show the exact location. (moved behind Info)")
log(page,"M-panel","map","disclaimer + credits + audience mechanics in the open panel","behind Info / Sources & credits; B1 line stays visible; full footer at the end of the panel")
# map head (desktop): title + Tell us + CTA, out of the legend
head=('<header class="ss-maphead"><h1 aria-hidden="true">Geothermal map: projects, tenders &amp; funding</h1>'+NOTICE_OLD+
      '<p class="sscta mh" data-cta="desktop"><span class="ctat">Get map updates in the free SpudSignal briefing.</span> <a class="ctab" href="https://spudsignal.beehiiv.com/subscribe?utm_source=map&amp;utm_medium=cta&amp;utm_content=desktop" target="_blank" rel="noopener">Subscribe free</a></p></header>')
s=rep(s,'<div id="map"></div><div id="legend"></div>','<div id="mapcol">'+head+'<div id="map"></div></div><div id="legend"></div><div id="mnotice">'+NOTICE_OLD+'</div>',page,"M-head",1,"map")
log(page,"M-notice","map","Tell-us notice + desktop CTA inside the legend","Tell-us + CTA in a visible map header (desktop); Tell-us card bottom (mobile); mobile CTA bar unchanged")
# JS: labels, legend, country names, start view, option B, legend collapsed
js_rep=[("M-label","LB={project:'Projects & wells (#1–#7)',","LB={project:'Projects & wells',"),
 ("M-legend","+NOTICE_HTML+CTA_DESKTOP;}",";}"),
 ("M-legend","const LEG0=[['tender','Tender'],['project','Project / news'],['funding','Funding']].map(([t,l])=>`<span>${shp(t,14,false)}${l}</span>`).join('')+'<span><svg width=\"14\" height=\"14\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"9.5\" fill=\"#fff\" stroke=\"#0F2A3D\" stroke-width=\"2.5\" stroke-dasharray=\"4 3\"/></svg>approx. location</span>';",
             "const LEG0='<span class=\"lrow\">'+[['tender','Tender'],['project','Project / news'],['funding','Funding']].map(([t,l])=>`<i>${shp(t,14,false)}${l}</i>`).join('')+'</span>';"),
 ("M-legend","`<span>${hexS('half',14,false,false,false,true)}${opS(14,false,true)}Active project / operating plant, approx. location (dashed outline)</span>`","`<span>${hexS('half',14,false,false,false,true)}${opS(14,false,true)}<svg width=\"14\" height=\"14\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"9.5\" fill=\"#fff\" stroke=\"#0F2A3D\" stroke-width=\"2.5\" stroke-dasharray=\"4 3\"/></svg>approx. location (dashed outline)</span>`"),
 ("M-country","ctys.map(c=>`<button data-c=\"${c}\">${c}</button>`)","ctys.map(c=>`<button data-c=\"${c}\" title=\"${c}\">${CN[c]||c}</button>`)"),
 ("M-start2","window.L.map('map',{zoomControl:true,maxZoom:12})","window.L.map('map',{zoomControl:true,maxZoom:12,zoomSnap:0.25})"),
 ("M-start3","setView([49,10],4);","setView([49,10],3.75);"),
 ("M-start","if(window.innerWidth<=760&&layer.getLayers().length)m.fitBounds(layer.getBounds(),{padding:[24,24]});","if(layer.getLayers().length)m.fitBounds(layer.getBounds(),{padding:[24,24],maxZoom:5});"),
 ("M-attrib","\"<a href=\\\"#about-sources\\\" onclick=\\\"var p=document.getElementById('panel');if(p)p.classList.add('open')\\\">About &amp; Sources</a>\"","\"<a href=\\\"#about-sources\\\" onclick=\\\"var p=document.getElementById('panel');if(p)p.classList.add('open');var d=document.getElementById('about-sources');if(d)d.open=true\\\">Sources &amp; credits</a>\""),
]
for cid,o,n in js_rep: s=rep(s,o,n,page,cid,1,"map")
s=rep(s,"function testCounts(){const pts=new Set(TL.operating.map(o=>o.lat+','+o.lon)).size;return {active:TL.active.length,operating:pts}}","function testCounts(){return {active:TL.active.length,operating:TL.operating.length}}",page,"M-count",1,"map")
CN='const CN={AT:"Austria",CH:"Switzerland",CZ:"Czechia",DE:"Germany",ES:"Spain",FR:"France",HU:"Hungary",IE:"Ireland",IS:"Iceland",IT:"Italy",NL:"Netherlands",PL:"Poland",RO:"Romania",TR:"Türkiye",UA:"Ukraine",UK:"United Kingdom",GB:"United Kingdom",BE:"Belgium",EE:"Estonia",PT:"Portugal",SE:"Sweden",SI:"Slovenia",EU:"EU-wide"};'
s=rep(s,"const C={project:",""+CN+"const C={project:",page,"M-country",1,"map")
CSSMAP="""<style>
#wrap{display:flex}#mapcol{flex:1;display:flex;flex-direction:column;min-width:0}#map{flex:1;min-height:0}
.ss-maphead{height:auto;color:var(--navy);display:grid;grid-template-columns:1fr auto;gap:2px 16px;align-items:center;background:#fff;border-bottom:1px solid var(--gb);padding:8px 16px}
.ss-maphead h1{grid-column:1/3;font-size:22px;margin:0;color:var(--navy)}
.ss-maphead .tnotice{grid-column:1;grid-row:2;margin:0;font-size:13px;line-height:1.4;background:none;border:0;padding:0}.ss-maphead .tnotice a{color:var(--navy);font-weight:700}
.ss-maphead .sscta{grid-column:2;grid-row:2;display:flex;position:static;align-items:center;gap:10px;margin:0;font-size:13px;color:var(--navy)}
.ss-maphead .ctab{display:inline-flex;align-items:center;min-height:44px;background:var(--orange);color:#fff;font-weight:700;text-decoration:none;border-radius:22px;padding:0 16px;white-space:nowrap}
#legend{left:auto!important;right:10px;bottom:28px;padding:6px 8px;max-width:420px}#legend.open .legitems{display:block!important}#legend:not(.open) .legitems{display:none!important}
#legend .lrow{display:flex;gap:10px}#legend .lrow i{font-style:normal;display:flex;align-items:center;gap:4px}
#legend #legtog{display:inline-flex!important;align-items:center;margin:0;font-size:13px;min-height:44px;min-width:44px;font:inherit;font-weight:700;border:1px solid var(--navy);border-radius:22px;background:#fff;color:var(--navy);padding:0 14px;cursor:pointer}
#mnotice{display:none}
.minfo{margin:10px 0;border-top:1px solid var(--gb);padding-top:6px}.minfo>summary{min-height:44px;display:flex;align-items:center;font-weight:700;cursor:pointer}
#panel h1.sr-only-m{font-size:15px;margin:0 0 4px;color:var(--navy)}
@media(min-width:761px){#panel h1.sr-only-m{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}}
@media(max-width:760px){.ss-maphead{display:none}#mnotice{display:block;position:absolute;z-index:900;left:8px;right:8px;bottom:22px}#mnotice .tnotice{margin:0;background:rgba(255,255,255,.96);border:1px solid var(--gb);border-left:4px solid var(--orange);border-radius:8px;padding:8px 10px;font-size:13px}
 #legend{right:8px;bottom:auto;top:10px;left:auto!important;padding:0;border:0;background:none;box-shadow:none;display:block}#legend.open{background:#fff;padding:6px 8px;border:1px solid var(--gb)}
 #panel h1.sr-only-m{display:block}}
</style>"""
s=s.replace("</head>",CSSMAP+"</head>",1)
wr("map/index.html",s)
# ======================= PROJECTS =======================
page="projects"; s=rd("projects/index.html")
s=shell(s,page,"map",sub=True)
s=re.sub(r"<main>\s*<h1>",'<main class="ss-main"> <nav class="crumb" aria-label="Breadcrumb"><a href="/map/">Map</a> › <span aria-current="page">Project list</span></nav><header class="ss-head ss-head-plain"><p class="k">SpudSignal</p><h1 id="content" tabindex="-1">',s,count=1)
s=s.replace("Geothermal projects in Bavaria</h1>","Geothermal projects in Bavaria</h1></header>",1)
log(page,"S-head","shell","plain H1 26px","shared page header (kicker SpudSignal + H1)")
for old,why in [('body{margin:0;font-family:"DejaVu Sans",Verdana,sans-serif;color:var(--navy);background:#F4F6F8}',"body font/background → shared"),
                ('main{max-width:1120px;margin:0 auto;padding:22px 24px 10px} h1{font-size:26px;margin:4px 0 10px}',"width 1120 + H1 26px → shared"),
                ('@media(max-width:600px){main{padding:14px 12px 10px} h1{font-size:21px}','@media(max-width:600px){'),]:
    if isinstance(why,str) and old in s and not why.startswith("@"): s=s.replace(old,""); log(page,"CSS-local","css-removed",old[:90],why)
    elif old in s: s=s.replace(old,why); log(page,"CSS-local","css-removed",old[:60],"H1 mobile → shared")
hf=re.search(r'<footer style="max-width:860px[^>]*>.*?</footer>',s,re.S); assert hf and LIAB_HOME_LIVE in hf.group(0)
s=s.replace(hf.group(0),footer(LIAB_HOME_LIVE).replace('data-ss-footer','data-ss-footer data-hotfix="live-368155e"'),1)
log(page,"S-footer","shell","hotfix legal footer (live since 368155e, inline styles; links Impressum · Privacy · About & Sources · SpudSignal)","shared footer; liability sentence kept verbatim from the hotfix (temporary, P-F1 pending H05)")
s=s.replace("</head>","<style>main.ss-main{padding-top:4px}.ss-head-plain{margin-top:0}</style></head>",1)
wr("projects/index.html",s)
# ======================= WHAT'S NEW =======================
ENT=[("2.0","set at go-live",["New: one tab bar for Library, Tenders and Map on every page, on desktop and mobile."]),
     ("1.2","13 Nov 2026",["New on the map for Bavaria: an Active projects layer (15 projects) and a switchable Operating plants layer (28 plants). Each new pin links to a public source.",
                           "Also new: a slimmer Tenders page on mobile. Key facts stay on each card; the rest sits under \"Details\" and \"About this data\"."]),
     ("1.1","8 Nov 2026",["New: audience filters. Filter the Library, open tenders and the map by Drilling, Equipment, Engineering & Services, or Project owners & developers."]),
     ("1.0","before 8 Nov 2026",["The starting point: the Library, the Tenders page and the map as they were before 8 Nov 2026."])]
items="".join(f'<li class="ss-card"><h2>Update {v} <span class="d">· {d}</span></h2>'+"".join(f"<p>{H.escape(t,quote=False)}</p>" for t in ts)+"</li>" for v,d,ts in ENT)
page_html=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>What’s new – SpudSignal Library</title><meta name="robots" content="noindex"><link rel="icon" href="/favicon.svg">{CSSLINK}{URLJS}
<style>main.ss-main ol{{list-style:none;padding:0;margin:0;max-width:760px}} main.ss-main li h2{{font-size:17px;margin:0 0 4px;color:var(--navy)}} main.ss-main li .d{{font-weight:400;color:#5B6B7A}} main.ss-main li p{{margin:0 0 4px}} .note{{font-size:13px;color:#5B6B7A;max-width:760px}}</style></head>
<body class="has-appnav">{nav("wn")}<div class="ss-wrap"><header class="ss-head"><p class="k">SpudSignal</p><h1 id="content" tabindex="-1">What’s new</h1><p>New features and layout changes, newest first. Each feature release gets an update number.</p></header>
<main class="ss-main" style="padding:0"><ol>{items}</ol><p class="note">Weekly data updates (new entries, expired deadlines, re-checks) get no number. See "last updated" on each page.</p></main></div>{footer(LIAB_HOME_NEW)}</body></html>"""
wr("whats-new/index.html",page_html)
log("home","H-rename","shell","tab label Home","tab label Library (page H1 “Source Library” unchanged – decision B)")
log("home","H-search","new","–","search field “Search the Library” (JS only; hidden without JS)")
log("home","H-past","new","36 expired entries mixed into the list (grey, struck through)","hidden by default; toggle “Show entries whose deadline has passed (N)”; without JS all entries stay visible")
log("home","H-layout","shell","single column 860px","sidebar (search, toggle, audience, countries) + list, 1100px")
log("home","S-footer","shell","home footer","shared footer (same text, plus What’s new link)")
log("tenders","T-hash","new","/tenders/#about-data lands on a closed “About this data”","opens the details when the hash is #about-data (Reviewer PR #7 note F-3)")
log("all","U-params","new","filters not carried between pages","?aud=, ?country=, ?q= in the URL; tab links carry aud/country; without JS the page shows everything")
log("whats-new","W-page","new","–","new page /whats-new/ (W-01, W-02, W-10, W-11, W-12 merged, W-20)")
log("map","M-legend2","map","legend open","legend collapsed by default (“Legend ▸”, 44px)")
json.dump(LOG,open(os.path.join(PRE,"tabs-log.json"),"w"),indent=1,ensure_ascii=False)
print("built; log entries:",len(LOG))
