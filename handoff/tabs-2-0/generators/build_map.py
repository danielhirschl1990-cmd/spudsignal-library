"""Weekly build of the LIVE map data (library/site/map/data.geojson + data.js). Derived from growth/map-prototype/src/build.py (29 Oct).
Issue #7 update 8 Nov 2026: adds #7 items (issue-7-final.md / -final-sources.md / -map-locations.md, issues/src/issue7_content.PLACES; Croze via OSM Nominatim 8 Nov), current tenders.json.
Issue #6 update 1 Nov 2026: adds #6 items (issue-6-final.md / -final-sources.md / -map-locations.md), current tenders.json. No BVG candidates.
Sources: issues/src map scripts (verified coords), issues/*-final.md, library/site/tenders/tenders.json,
src/geocode_cache.json (OSM Nominatim, 29 Oct 2026, town level -> always marked approx)."""
import json, re, glob, os, datetime as dt
R='/workspace/geothermie'; H=R+'/growth/map-prototype/src'; OUT=R+'/library/site/map'
NOW=dt.datetime.now(dt.timezone(dt.timedelta(hours=1))).replace(second=0,microsecond=0)
# verified coords from our map scripts (lon,lat)
import sys; sys.path.insert(0,R+'/issues/src')
from i2_map import PLACES as P2
import importlib; import issue4_content as c4, issue5_content as c5, issue6_content as c6, issue7_content as c7
V=dict(P2); V.update({'ferney':(6.1096,46.2567),'linnich':(6.2676,50.9806),'seaham':(-1.3356,54.8372),'vaud':(6.6327,46.5218),'solotvyno':(23.8747,47.9470)})  # make_issue3_map.py
V.update(c4.PLACES if hasattr(c4,'PLACES') else {}); V.update(c5.PLACES if hasattr(c5,'PLACES') else {})
# #6 coords (OSM Nominatim 1 Nov, issue6_content.PLACES); paris/geretsried keep their existing pins' coords
V.update({k:v for k,v in c6.PLACES.items() if k not in ('paris','geretsried')}); V['paris_egp']=c6.PLACES['paris']
V['krafla']=(-16.778,65.704)  # Krafla power station (Kröflustöð), IS - plant named in TED 754152
# #7 coords (8 Nov 2026). Own keys: c7 uses 'kutno'/'muenster' for other points (Kutno keeps its #5 coords; 'muenster' = research well).
V['munich_michaelibad']=c7.PLACES['munich']   # Heinrich-Wieland-Str. 16 (address in TED 766383) -> exact
# town/district-level #7 points -> always approx: key -> (lon,lat,loc_source)
APX={'szeged':c7.PLACES['szeged']+('issues/src/issue7_content.py: Szeged town centroid',),
 'amstelveen':c7.PLACES['amsterdam']+('issues/src/issue7_content.py: midpoint Amsterdam/Amstelveen (region marker)',),
 'germencik':c7.PLACES['germencik']+('issues/src/issue7_content.py: Germencik town',),
 'muenster_handorf':c7.PLACES['muenster']+('issues/src/issue7_content.py: Handorf district, Münster',),
 'croze':(2.1609,45.8177,'OSM Nominatim 8 Nov 2026, village: Croze, Aubusson, Creuse (relation 118574)')}
G=json.load(open(H+'/geocode_cache.json'))
URL={1:'https://spudsignal.beehiiv.com/p/spudsignal-1-prenzlau-plant-kaba-well-erzurum-licences',2:'https://spudsignal.beehiiv.com/p/spudsignal-2-synergys-kit-alsace-well-geiselbullach',3:'https://spudsignal.beehiiv.com/p/spudsignal-3-ferney-well-linnich-boreholes-seaham-heat',4:'https://spudsignal.beehiiv.com/p/spudsignal-4-antony-concession-romanian-wells-nigde',5:'https://spudsignal.beehiiv.com/p/spudsignal-5-kutno-wells-hvc-framework-berlin-la-palma',6:'https://spudsignal.beehiiv.com/p/spudsignal-6-alton-paused-paris-heat-italys-fer-2',7:'https://spudsignal.beehiiv.com/p/spudsignal-7-munich-works-kaba-reset-kutno-funding'}
MD={i:open(f'{R}/issues/issue-{i}-final.md').read() for i in URL}
def loc(k):
    if k in V: lon,lat=V[k]; return lon,lat,False,'map script (issues/src)'
    if k in APX: lon,lat,src=APX[k]; return lon,lat,True,src
    g=G[k]; return g['lon'],g['lat'],True,'OSM Nominatim, town centre: '+g['osm']
# --- projects/wells: (key, issue, country, title from the issue headline, note)
PROJ=[('askale',1,'TR','Erzurum auctions two geothermal exploration licences (Aşkale field)','Licence field ~4,800 ha; pin at town, not field'),
 ('pasinler',1,'TR','Erzurum auctions two geothermal exploration licences (Pasinler field)','Licence field ~4,800 ha; pin at town, not field'),
 ('buldan',1,'TR',"New EIA notice for Margün's exploration drilling near Buldan",'"near Buldan"; pin at town'),
 ('aulnay',1,'FR','Drilling done at Aulnay-sous-Bois, heat due by year-end',None),
 ('litomerice',2,'CZ','Charles University orders wellheads and frac trees for SYNERGYS',None),
 ('preuschdorf',2,'FR','Sauer-Pechelbronn studies turning an existing well into a deep geothermal probe',None),
 ('geiselbullach',2,'DE','Geiselbullach tests confirm about 10 MW of geothermal heat',None),
 ('aschheim',2,'DE','Daldrup reports order backlog, Aschheim wells due in November',None),
 ('gross_schoenebeck',2,'DE','Vacuum-insulated closed loop delivers heat at Groß Schönebeck',None),
 ('kalisz',2,'PL','Kalisz prepares to drill its GT-1 thermal-water well',None),
 ('ferney',3,'FR','Ferney-Voltaire seeks a designer for a geothermal exploration well',None),
 ('linnich',3,'DE','Gelsenwasser tenders a 30-borehole field for a cold heat network in Linnich',None),
 ('seaham',3,'UK','Seaham mine-water heat network completes commissioning',None),
 ('vaud',3,'CH','Vaud approves funds to explore its subsurface','Canton-wide; pin at Lausanne (cantonal capital)'),
 ('solotvyno',3,'UA','UK-led team models a pilot geothermal plant at Solotvyno',None),
 ('antony',4,'FR','Antony puts a deep Dogger geothermal heat concession out to tender',None),
 ('calimanesti',4,'RO','Călimănești tenders design-and-build of two geothermal wells and heat networks',None),
 ('nigde',4,'TR','Niğde auctions six geothermal exploration licence areas','Six licence areas; pin at Niğde city'),
 ('jelenia',4,'PL','Jelenia Góra starts drilling the 2,500 m C-3 geothermal well',None),
 # Kutno: existing GT-1/GT-2 project pin, UPDATED for #7 (financing news); the #5 drilling tender stays a separate tender pin while open
 ('kutno',7,'PL','Kutno secures more than PLN 59m for geothermal heat',None,'NFOŚiGW release, 4 Nov 2026','https://www.gov.pl/web/nfosigw/geotermia-dla-kutna-dzieki-srodkom-z-nfosigw-powstanie-nowoczesna-cieplownia-wykorzystujaca-energie-z-wnetrza-ziemi-'),
 ('westland',5,'NL','HVC heat-exchanger framework – lot 1 (Westland)',None),
 ('slochteren',5,'NL','HVC heat-exchanger framework – lot 2 (Slochteren)',None),
 ('muenster',5,'DE','Geological Survey NRW tenders Münster research-well drilling',None),
 ('marzahn',5,'DE','Berlin awards its first exploration right to BEW (Marzahn)',None),
 ('lapalma',5,'ES','La Palma test drilling exempted from simplified EIA','Island-level pin'),
 ('lahe',5,'DE','enercity and Eavor drop Hannover-Lahe',None),
 ('graefelfing',5,'DE','Gräfelfing to start deep drilling on 2 Nov',None),
 ('frauenfeld',5,'CH','Geothermie Thurgau – 3D seismic over about 430 km², winter 2027/28','Survey area; pin at Frauenfeld (cantonal capital)'),
 # --- #6 (1 Nov 2026): optional 6th/7th field = (source label incl. date, source url)
 ('vienna',6,'AT','Vienna awards surface works for its first deep-geothermal plant','Plant site not in the notice; pin at Vienna','TED 749142-2026, 29 Oct 2026','https://ted.europa.eu/en/notice/-/detail/749142-2026'),
 ('eden',6,'UK','Eden Geothermal seeks more wells within its Cornwall site',None,'BBC News (LDRS), 28 Oct 2026','https://www.bbc.co.uk/news/articles/crjwe84lqj10o'),
 ('jolanda',6,'IT','First FER 2 geothermal auction: Jolanda di Savoia admitted (24.4 MW)','Municipality named by GSE; pin at town','GSE news, 23 Oct 2026','https://www.gse.it/servizi-per-te/news/fer-2-pubblicate-le-graduatorie-del-terzo-bando'),
 ('castelgiorgio',6,'IT','First FER 2 geothermal auction: Castel Giorgio admitted (5 MW)','Municipality named by GSE; pin at town','GSE news, 23 Oct 2026','https://www.gse.it/servizi-per-te/news/fer-2-pubblicate-le-graduatorie-del-terzo-bando'),
 ('heerhugowaard',6,'NL','HVC pauses Alton after weak well test','Dijk en Waard; well site not in the source, pin at Heerhugowaard','HVC news, 29 Oct 2026','https://www.hvcgroep.nl/ons-verhaal/nieuws/aardwarmte-alton-op-pauze-na-tegenvallende-testresultaten'),
 ('geretsried',6,'DE','Geretsried heat buyer leaves Eavor contract',None,'City press release 21/2026, 26 Oct 2026','https://www.geretsried.de/user_uploads/de/rathaus/presse/medienmitteilungen/2026-10-26-MM-21-2026-ILN-Ruecktritt-Waermeliefervertrag-EAVOR.pdf'),
 ('brabant',6,'NL','North Brabant maps its geothermal potential','Province-wide; pin at province centre','Province of North Brabant, 26 Oct 2026','https://www.brabant.nl/actueel/nieuws/kansen-aardwarmte-brabant-in-kaart-gebracht/'),
 # --- #7 (8 Nov 2026). Munich/Kaba/Szeged/Croze come in as tender pins from tenders.json. No pin: Estonia STEIGER (no verified site), ADEME (nationwide, no open call).
 ('amstelveen',7,'NL','OMV selected for Amsterdam–Amstelveen development','Drilling site still to be selected; pin between Amsterdam and Amstelveen','TED 769576-2026 (award), 5 Nov 2026','https://ted.europa.eu/en/notice/-/detail/769576-2026'),
 ('germencik',7,'TR','Exergy signs a 33 MWe geothermal plant contract','Mehmet Ege plant, Germencik district (Aydın); pin at town','Exergy release, 5 Nov 2026','https://exergyint.com/wp-content/uploads/2026/11/Exergy-Signs-New-Contract-With-Maren-Elektrik-Uretim-Final.pdf'),
 ('muenster_handorf',7,'DE','Münster investigates another cold heat-network site','Kötterstraße, Handorf; pin at district','Stadtwerke Münster release, 2 Nov 2026','https://www.stadtwerke-muenster.de/unternehmen/presse/pressemitteilungen/434621/stadtwerke-suchen-nach-erdwarme-an-der-kotterstrasse'),
]
# #1-#5 project pins: source + date (2 Nov 2026, Daniel). Only links printed in the published issue (issue-<n>-final.md),
# date from issue-<n>-final-sources.md. Format like #6: "label, date".
OLDSRC={
 'askale':('Official Gazette notice, 27 Sep 2026','https://www.resmigazete.gov.tr/ilanlar/eskiilanlar/2026/09/20260927-3-4.pdf'),
 'pasinler':('Official Gazette notice, 27 Sep 2026','https://www.resmigazete.gov.tr/ilanlar/eskiilanlar/2026/09/20260927-3-4.pdf'),
 'buldan':('EIA notice (Foreks), 21 Sep 2026','https://www.foreks.com/haber/detay/6ab0f12895016b5817e5d7eb/FRKS/tr/ced-duyurusu-margun-jeotermal-enerji-21-09-26/'),
 'aulnay':('Coriance release, 25 Sep 2026','https://groupe-coriance.fr/2026/09/25/aulnay-sous-bois-clap-de-fin-pour-le-forage-de-la-geothermie/'),
 'litomerice':('TED 674260-2026, 1 Oct 2026','https://ted.europa.eu/en/notice/-/detail/674260-2026'),
 'preuschdorf':('BOAMP 26-95181, 2 Oct 2026','https://www.boamp.fr/pages/avis/?q=idweb:26-95181'),
 'geiselbullach':('GfA release, 1 Oct 2026','https://www.gfa-online.com/geothermiebohrungen-erfolgreich-abgeschlossen/'),
 'aschheim':('Daldrup release (EQS), 30 Sep 2026','https://www.eqs-news.com/de/news/corporate/daldrup-sohne-ag-publishes-2026-group-half-year-report-significant-growth-and-high-order-backlog/6cbeae35-3692-4399-b2a2-0cb1db4def58'),
 'gross_schoenebeck':('GFZ release, 29 Sep 2026','https://www.gfz.de/en/press/news/details/erfolgreicher-einsatz-einer-neuen-geothermie-technologie-fuer-stabile-lokale-und-erneuerbare-waerme'),
 'kalisz':('Radio Poznań, 1 Oct 2026','https://radiopoznan.fm/informacje/pozostale/beda-wiercic-szukaja-wod-termalnych'),
 'ferney':('BOAMP 26-97695, 10 Oct 2026','https://www.boamp.fr/pages/avis/?q=idweb:26-97695'),
 'linnich':('TED 698651-2026, 9 Oct 2026','https://ted.europa.eu/en/notice/-/detail/698651-2026'),
 'seaham':('GOV.UK release, 6 Oct 2026','https://www.gov.uk/government/news/flicking-the-switch-to-heat-seaham-homes-with-mine-water-energy'),
 'vaud':('Grand Conseil agenda item, 6 Oct 2026','https://www.vd.ch/gc/seances-du-grand-conseil/point-seance/point/c6b492e5-4106-4305-be07-3ef168f3e949/meeting/1033712'),
 'solotvyno':('Aberystwyth University release, 8 Oct 2026','https://www.aber.ac.uk/en/news/archive/2026/10/title-290122-en.html'),
 'antony':('BOAMP 26-100285, 17 Oct 2026','https://www.boamp.fr/pages/avis/?q=idweb:26-100285'),
 'calimanesti':('TED 716179-2026, 16 Oct 2026','https://ted.europa.eu/en/notice/-/detail/716179-2026'),
 'nigde':('Official Gazette notice, 18 Oct 2026','https://www.resmigazete.gov.tr/ilanlar/eskiilanlar/2026/10/20261018-3-1.pdf'),
 'jelenia':('Jelenia Góra Nasze Miasto, 16 Oct 2026','https://jeleniagora.naszemiasto.pl/woda-geotermalna-u-podnoza-karkonoszy-rozpoczeli-wiercenie-na-glebokosc-2500-metrow/ar/c7p2-29445853'),
 'kutno':('TED 725171-2026, 20 Oct 2026','https://ted.europa.eu/en/notice/-/detail/725171-2026'),
 'westland':('TED 726565-2026, 21 Oct 2026','https://ted.europa.eu/en/notice/-/detail/726565-2026'),
 'slochteren':('TED 726565-2026, 21 Oct 2026','https://ted.europa.eu/en/notice/-/detail/726565-2026'),
 'muenster':('TED 734244-2026, 23 Oct 2026','https://ted.europa.eu/en/notice/-/detail/734244-2026'),
 'marzahn':('Senate press release, 19 Oct 2026','https://www.berlin.de/sen/uvk/presse/pressemitteilungen/2026/pressemitteilung.1727603.php'),
 'lapalma':('Gobierno de Canarias release, 19 Oct 2026','https://www3.gobiernodecanarias.org/noticias/el-gobierno-de-canarias-da-luz-verde-a-los-sondeos-para-investigar-el-potencial-geotermico-de-la-palma/'),
 'lahe':('enercity release, 22 Oct 2026','https://www.enercity.de/presse/pressemitteilungen/2026/tiefengeothermieprojekt-in-lahe-wird-nicht-umgesetzt-hannovers-kohleausstieg-bleibt-abgesichert'),
 'graefelfing':('Gräfelfing news (bit blessing), 19 Oct 2026','https://www.graefelfing.de/aktuelles/artikel/2622.html'),
 'frauenfeld':('Canton Thurgau release, 22 Oct 2026','https://www.tg.ch/news.html/485/news/80508'),
}
# --- tenders/funding uid -> place key ; None = no point location (nationwide/EU) -> list only
TLOC={'389f89d14d614826':'pessac','ffefc6bd40ec17bb':'kaba','7b5311b7bce42b93':'winterthur','4d8245a64661a9ca':'vendome',
 'cdd0f1c5dd4de2ff':'grangegorman','00be19d0c9c0cbfd':'litomerice','59eca9045bac22e1':'aussac','41cabab7a5f09b40':'villiersbel',
 'fbe0bf1d339c6850':'litomerice','7095f2787aa83db3':'litomerice','3a5d2c3eb36bebba':'linnich','4100e4cedb042af9':'ferney',
 '7bded30fa2266c1c':'aschheim','253e005b3f55f334':'wroclaw','798e608fb28b08cb':'waldrach','803c662051981e98':'monteleger',
 'd6aceeed5e1cf4bd':'paris','f0353bf382e57b2b':'montpellier','6b774d72bcf5d7f5':'pantin','3942db59a0569a17':'marzahn',
 'd1a2305da5242137':'laufzorn','0c87fc4157e326c0':'villetaneuse','82be64efeab79612':'sille','4fd50c9eb94424d6':'calimanesti',
 '06fd138aa75e9be4':'kutno','c063c46f5a23a0b2':'preuschdorf','a18fef83c1e2ddc5':'muenster','dadbf94b3d55275a':'westland',
 # #6 update: new notices for known sites + new #6 tenders (SDE++ NL / Horizon EU have no site -> nationwide list)
 '3c97938c6f31d0cc':'grangegorman','0dc12863fa50d657':'muenster','ed4f6d6f9dde823e':'paris_egp','134f041368647f35':'stgallen',
 '5fbc2426027d65b6':'galway','50fb456c6fff3b64':'krafla',
 # #7 update: Kaba new notice 763136 (same procedure, existing Kaba site), Szeged heat supply, Munich Michaelibad, Croze
 '71a5f9ee90af9d4f':'kaba','33fedeabccf98de1':'szeged','9bb8bc940f00ee6c':'munich_michaelibad','76d3e3d4f7f4b6c3':'croze'}
FORCE_APPROX={'paris':'Regional call (Île-de-France); pin at Paris','pantin':'UniGéo spans Pantin, Les Lilas, Le Pré-Saint-Gervais, Romainville; pin at Pantin',
 'aschheim':'Aschheim/Feldkirchen/Kirchheim network; pin at Aschheim','westland':'Framework covers lots in Westland and Slochteren; pin at Westland',
 'wroclaw':'University buyer; pin at city','kaba':None,'monteleger':'CH Drôme Vivarais (Montéléger)',
 'paris_egp':'Network across Paris and inner suburbs (NUTS FR101/105/106/107); pin at Paris',
 'krafla':"Repair at the contractor's workshop; pin at Krafla power plant",
 'szeged':'Heat supply for the Csonka János school premises; pin at town, not a drilling site','croze':'Town hall (mairie) renovation; pin at village'}
# manual issue match (id not cited verbatim): FEDER IDF call listed as 'Île-de-France ERDF call 2026' in #3 l.97 (first mention), also #4, #5
ISSUE_FIX={'d6aceeed5e1cf4bd':3,'0dc12863fa50d657':5}  # Münster: new notice 754784 in same TED procedure as #5's 734244 (issue-6-final-sources.md l.92)
feats=[];dropped=[];nationwide=[]
def F(lon,lat,props): feats.append({'type':'Feature','geometry':{'type':'Point','coordinates':[lon,lat]},'properties':props})
for row in PROJ:
    k,i,c,t,n=row[:5]
    lon,lat,ap,src=loc(k); ap=ap or bool(n)
    p=dict(type='project',country=c,title=t,issue=i,issue_url=URL[i],approx=ap,loc_note=n,loc_source=src)
    if len(row)>5: p.update(id=row[5],source_url=row[6])
    elif k in OLDSRC: p.update(id=OLDSRC[k][0],source_url=OLDSRC[k][1])
    else: print('NO SOURCE',k)
    F(lon,lat,p)
T=json.load(open(R+'/library/site/tenders/tenders.json'))
for e in T['entries']:
    d=dt.datetime.fromisoformat(e['deadline_iso'].replace('.000',''))
    if d.tzinfo is None: d=d.replace(tzinfo=NOW.tzinfo)
    base=dict(type=e['kind'],country=e['country'],title=e['title'],buyer=e['buyer'],id=e['id'],deadline=e['deadline_txt'],
              deadline_iso=e['deadline_iso'],source_url=e['url'],checked=e['checked'])
    if d<NOW: dropped.append({'item':e['id']+' '+e['title'][:60],'reason':'deadline passed ('+e['deadline_txt']+')'}); continue
    num=re.search(r'(\d{2,3}[-]\d{4,6}|\d{6}-2026)',e['id']); num=num.group(1) if num else e['id']
    iss=[i for i in URL if num in MD[i] or e['id'] in MD[i]]
    if not iss and e['uid'] in ISSUE_FIX: iss=[ISSUE_FIX[e['uid']]]
    base.update(issue=iss[0] if iss else None,issue_url=URL[iss[0]] if iss else None)
    k=TLOC.get(e['uid'])
    if not k: nationwide.append(base); continue
    lon,lat,ap,src=loc(k); n=FORCE_APPROX.get(k)
    base.update(approx=ap or bool(n),loc_note=n,loc_source=src); F(lon,lat,base)
# Dedupe rule (2 Nov 2026, Daniel): hide a PROJECT pin only while an OPEN tender pin at the same site points to the
# exact same notice number (e.g. TED 725171-2026). Computed each build from the open tenders, so when the tender's
# deadline passes (tender dropped above) the project pin comes back automatically. Different notices at one site stay.
def NUMS(*ss): return set(x for s in ss for x in re.findall(r'\d{5,6}-20\d\d|\b\d{2}-\d{5,6}\b',s or ''))
TPINS=[f for f in feats if f['properties']['type']!='project']
hidden=[]
for f in [f for f in feats if f['properties']['type']=='project']:
    p=f['properties']; n=NUMS(p.get('id'),p.get('source_url'))
    hit=[t for t in TPINS if t['geometry']['coordinates']==f['geometry']['coordinates'] and n&NUMS(t['properties']['id'],t['properties']['source_url'])]
    if hit: feats.remove(f); hidden.append({'project':p['title'],'issue':p['issue'],'notice':sorted(n),'tender':hit[0]['properties']['id'],'tender_deadline':hit[0]['properties']['deadline'],'tender_issue':hit[0]['properties'].get('issue')})
for h in hidden: print('HIDDEN (dup of open tender):',h)
# (one-pin-per-site merge removed 2 Nov 2026, Daniel: keep separate pins, cluster spiderfy spreads same-site entries)
json.dump({'type':'FeatureCollection','generated':NOW.isoformat(),'tender_data':T['generated'],'features':feats},open(OUT+'/data.geojson','w'),ensure_ascii=False,indent=1)
json.dump({'nationwide':nationwide,'dropped':dropped,'hidden_projects':hidden},open(OUT+'/extra.json','w'),ensure_ascii=False,indent=1)
from collections import Counter
print(Counter(f['properties']['type'] for f in feats),'approx',sum(f['properties']['approx'] for f in feats),'nationwide',len(nationwide),'dropped',len(dropped))
open(OUT+'/data.js','w').write('window.SS_DATA='+json.dumps(json.load(open(OUT+'/data.geojson')),ensure_ascii=False)+';\nwindow.SS_EXTRA='+json.dumps({'nationwide':nationwide},ensure_ascii=False)+';\n')
