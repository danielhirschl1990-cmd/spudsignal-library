import html
from collections import OrderedDict
from data import E
I={1:"https://spudsignal.beehiiv.com/p/spudsignal-1-prenzlau-plant-kaba-well-erzurum-licences",2:"https://spudsignal.beehiiv.com/p/spudsignal-2-synergys-kit-alsace-well-geiselbullach",3:"https://spudsignal.beehiiv.com/p/spudsignal-3-ferney-well-linnich-boreholes-seaham-heat",4:"https://spudsignal.beehiiv.com/p/spudsignal-4-antony-concession-romanian-wells-nigde",5:"https://spudsignal.beehiiv.com/p/spudsignal-5-kutno-wells-hvc-framework-berlin-la-palma",6:"https://spudsignal.beehiiv.com/p/spudsignal-6-alton-paused-paris-heat-italys-fer-2",7:"https://spudsignal.beehiiv.com/p/spudsignal-7-munich-works-kaba-reset-kutno-funding"}
UNV={"simap.ch"}
intro=["This library collects the primary sources behind every SpudSignal item: tender notices, licence decisions, funding calls and project releases from across Europe.",
"Entries are sorted by country, and each one links straight to the original document, so you can always read the full official text.",
"The library is updated weekly with every new issue. Deadlines marked (expired) have passed; always check the original notice for the latest dates."]
cs=sorted({e[0] for e in E},key=lambda c:(c!="Europe / EU-wide",c))
def dl(d):
  if not d: return None
  t,iso=d; return t+(" (expired)" if iso<__import__("datetime").date.today().isoformat() else "")
md=["# SpudSignal Source Library: European geothermal tenders, licences and funding",""]+[" ".join(intro),""]
h=[f"<p>{html.escape(' '.join(intro))}</p>"]
for c in cs:
  md+=[f"## {c}",""]; h.append(f"<h2>{html.escape(c)}</h2>\n<ul>")
  for e in [x for x in E if x[0]==c]:
    _,title,links,typ,line,d,iss=e
    main=links[0][1]; extra=links[1:]
    feat=", ".join(f"[#{n}]({I[n]})" for n in iss); hfeat=", ".join(f'<a href="{I[n]}">#{n}</a>' for n in iss)
    ex=" · ".join(f"[{l}]({u})" for l,u in extra); hex_=" · ".join(f'<a href="{html.escape(u)}">{html.escape(l)}</a>' for l,u in extra)
    D=dl(d)
    md.append(f"- **[{title}]({main})** `{typ}`  \n  {line}"+(f"  \n  Also: {ex}" if ex else "")+(f"  \n  Deadline: {D}" if D else "")+f"  \n  Featured in {feat}")
    h.append(f'<li><p><strong><a href="{html.escape(main)}">{html.escape(title)}</a></strong> [{typ}]<br>{html.escape(line)}'+(f"<br>Also: {hex_}" if ex else "")+(f"<br>Deadline: {html.escape(D)}" if D else "")+f"<br>Featured in {hfeat}</p></li>")
  md.append(""); h.append("</ul>")
sub="Get new sources every week: [subscribe to SpudSignal for free](https://spudsignal.beehiiv.com/subscribe)."
md+=["---","",sub,""]
h.append('<p>Get new sources every week: <a href="https://spudsignal.beehiiv.com/subscribe">subscribe to SpudSignal for free</a>.</p>')
open("source-library.md","w").write("\n".join(md)); open("source-library-body.html","w").write("\n".join(h))
for c in cs: print(c,sum(1 for x in E if x[0]==c))
print(len(E))
