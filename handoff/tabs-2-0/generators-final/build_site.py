# Library 2.0 (13 Nov 2026): the tabs shell is added afterwards by tabs/tabs.py (last build stage), not here.
# Wraps source-library-styled.html into site/index.html: keeps the SEO/OG <head> and footer of the live page, refreshes counts.
import re
from data import E
from build import cs
nc=len([c for c in cs if c!="Europe / EU-wide"])
st=open("source-library-styled.html").read()
body=st.split('<body style="margin:0;background:#F5F7F9;">\n',1)[1].rsplit("\n</body></html>",1)[0]
cur=open("site/index.html").read()
# Library 2.0: if site/index.html already went through tabs/tabs.py, take the stored pre-tabs page as the base
# (live <head>, <body> tag, footer), so this rebuild produces a fresh pre-tabs page and tabs.py then re-applies the shell.
if 'data-ss-tabs="2.0"' in cur[:2000]:
  import os as _os0; cur=open(_os0.path.join(_os0.path.dirname(_os0.path.abspath(__file__)),"tabs","pretabs","index.html")).read()
_bm=re.search(r'<body[^>]*>',cur); head=cur[:_bm.start()]; BODY=_bm.group(0)  # keep live <body> tag (appnav v3 adds class="has-appnav")
head=re.sub(r"\d+ primary sources from \d+ countries plus EU",f"{len(E)} primary sources from {nc} countries plus EU",head)
foot=re.search(r"\n<footer.*?</footer>",cur,re.S).group(0)
import json as _j, os as _o
_tj="site/tenders/tenders.json"; _n=len(_j.load(open(_tj))["entries"]) if _o.path.exists(_tj) else 0
TL=('<style>.tl{display:block;background:#fff;border:2px solid #E97828;border-radius:12px;padding:14px 16px;margin:0 0 20px;color:#0F2A3D;text-decoration:none;transition:background .15s}.tl:hover,.tl:focus{background:#FDEBDD;outline:none}.tl:focus-visible{outline:3px solid #0F2A3D;outline-offset:2px}</style>'
 '<a class="tl" href="/tenders/"><strong style="font-size:17px;">Open geothermal drilling &amp; project tenders and funding calls &rarr;</strong><br>'
 f'<span style="font-size:14px;color:#24435A;"><span data-tenders-count>{_n}</span> open entries · filter by country, type, category, deadline and CPV.</span></a>\n'
 '<a class="tl" href="/map/" style="background:#0F2A3D;color:#fff;border-color:#E97828"><strong style="font-size:17px;">Explore the interactive map &rarr;</strong><br><span style="font-size:14px;color:#C8D2DC;">Projects and wells from SpudSignal issues, open tenders and funding calls on one map.</span></a>\n')
body=re.sub(r'(border-bottom:5px solid #E97828;">.*?</div>\n)',lambda m:m.group(1)+TL,body,count=1,flags=re.S)
open("site/index.html","w").write(head+BODY+"\n"+body+foot+"\n</body></html>\n")
print(len(E),nc)
