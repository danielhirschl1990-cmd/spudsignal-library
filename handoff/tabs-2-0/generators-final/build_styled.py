import html
from data import E
from build import I, cs, dl
O="#E97828";N="#0F2A3D";N2="#24435A";G="#C8D2DC"
F={"Europe / EU-wide":"🇪🇺","Estonia":"🇪🇪","Austria":"🇦🇹","Portugal":"🇵🇹","Belgium":"🇧🇪","Czechia":"🇨🇿","France":"🇫🇷","Germany":"🇩🇪","Hungary":"🇭🇺","Iceland":"🇮🇸","Ireland":"🇮🇪","Italy":"🇮🇹","Netherlands":"🇳🇱","Poland":"🇵🇱","Romania":"🇷🇴","Slovenia":"🇸🇮","Spain":"🇪🇸","Sweden":"🇸🇪","Switzerland":"🇨🇭","Türkiye":"🇹🇷","Ukraine":"🇺🇦","United Kingdom":"🇬🇧"}
B={"Tender":(O,"#fff"),"Licence":("#6B4FA0","#fff"),"Funding":("#1E8A5A","#fff"),"Project":("#1F6FB2","#fff"),"Study/Data":(N2,"#fff")}
e_=html.escape
slug=lambda c:"lib-"+"".join(ch for ch in c.lower() if ch.isalnum())
nc=len([c for c in cs if c!="Europe / EU-wide"])
font="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;"
o=[f'<div style="{font}max-width:860px;margin:0 auto;padding:0 12px;color:{N};line-height:1.5;">']
o.append(f'<div style="background:{N};border-radius:16px;padding:36px 24px;margin:16px 0 20px;border-bottom:5px solid {O};">'
f'<p style="margin:0 0 6px;color:{O};font-size:13px;font-weight:700;letter-spacing:2px;text-transform:uppercase;">SpudSignal</p>'
f'<h1 style="margin:0 0 10px;color:#fff;font-size:34px;line-height:1.15;">Source Library</h1>'
f'<p style="margin:0 0 16px;color:{G};font-size:17px;">The primary documents behind every SpudSignal item: geothermal tenders, licences and funding calls across Europe, linked to the originals.</p>'
f'<p style="margin:0;color:#fff;font-size:14px;font-weight:600;">{len(E)} primary sources &nbsp;·&nbsp; {nc} countries + EU &nbsp;·&nbsp; updated weekly</p></div>')
o.append('<p style="margin:0 0 20px;">'+"".join(f'<a href="#{slug(c)}" style="display:inline-block;margin:0 6px 8px 0;padding:6px 12px;border:1px solid {G};border-radius:999px;background:#F5F7F9;color:{N};text-decoration:none;font-size:14px;white-space:nowrap;">{F[c]} {e_(c)}</a>' for c in cs)+'</p>')
for c in cs:
  o.append(f'<h2 id="{slug(c)}" style="margin:28px 0 12px;font-size:22px;color:{N};border-bottom:2px solid {O};padding-bottom:6px;">{F[c]} {e_(c)}</h2>')
  for _,t,links,typ,line,d,iss in [x for x in E if x[0]==c]:
    bg,fg=B[typ];D=dl(d)
    card=f'<div style="background:#fff;border:1px solid {G};border-left:4px solid {bg};border-radius:12px;padding:14px 16px;margin:0 0 12px;box-shadow:0 1px 3px rgba(15,42,61,0.06);">'
    card+=f'<span style="display:inline-block;background:{bg};color:{fg};font-size:11px;font-weight:700;letter-spacing:1px;text-transform:uppercase;padding:3px 9px;border-radius:999px;">{typ}</span>'
    card+=f'<p style="margin:8px 0 4px;font-size:17px;font-weight:700;line-height:1.3;"><a href="{e_(links[0][1])}" style="color:{N};text-decoration:underline;text-decoration-color:{O};">{e_(t)}</a></p>'
    card+=f'<p style="margin:0 0 10px;font-size:15px;color:{N2};">{e_(line)}</p><p style="margin:0;font-size:13px;">'
    if D:
      if "(expired)" in D: card+=f'<span style="display:inline-block;margin:0 8px 6px 0;padding:3px 10px;border-radius:999px;background:#ECEFF2;color:#8A96A3;text-decoration:line-through;">⏱ {e_(D.replace(" (expired)",""))}</span><span style="color:#8A96A3;margin-right:8px;">expired</span>'
      else: card+=f'<span style="display:inline-block;margin:0 8px 6px 0;padding:3px 10px;border-radius:999px;background:#FDEBDD;color:#A84E10;font-weight:600;">⏱ {e_(D)}</span>'
    card+='<span style="color:#5B6B7A;white-space:nowrap;">Featured in '+", ".join(f'<a href="{I[n]}" style="color:{O};font-weight:700;text-decoration:none;">#{n}</a>' for n in iss)+'</span>'
    if len(links)>1: card+='<br><span style="color:#5B6B7A;">Also: '+" · ".join(f'<a href="{e_(u)}" style="color:{N2};">{e_(l)}</a>' for l,u in links[1:])+'</span>'
    o.append(card+'</p></div>')
o.append(f'<div style="background:{O};border-radius:16px;padding:28px 22px;margin:32px 0 24px;text-align:center;"><p style="margin:0 0 6px;color:#fff;font-size:22px;font-weight:800;">New sources every week</p><p style="margin:0 0 16px;color:#fff;font-size:15px;">Get open geothermal tenders, licences and funding deadlines across Europe in your inbox. Free.</p><a href="https://spudsignal.beehiiv.com/subscribe" style="display:inline-block;background:{N};color:#fff;padding:12px 26px;border-radius:999px;font-weight:700;text-decoration:none;">Subscribe free</a></div></div>')
body="\n".join(o)
open("source-library-styled.html","w").write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Source Library | SpudSignal</title></head><body style="margin:0;background:#F5F7F9;">\n'+body+"\n</body></html>")
