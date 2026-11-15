import json,re,sys,html
boards=json.load(open(sys.argv[1])); ref=open(sys.argv[2],encoding='utf-8').read()
css=ref[ref.index('<style>'):ref.index('</style>')+8]
font=re.search(r'<link rel="stylesheet"[^>]*>',ref)[0]
Q='filename=2132/MT491GT1440.XML&amp;tournament=491&amp;section=1'
U='https://resultater.bridge.dk/template/'
P={1:'Nielsen–Brix',2:'Egstrup–Veibel Petersen',3:'Lind Jensen–Grossman',4:'Meldgaard–Christensen',5:'Steiner–Thygesen',6:'Rasmussen–Haugaard Jensen',7:'Koks Andreassen–Øxseth',8:'Dyrekilde–Dyrekilde Sommerlund'}
SC={'♠':'ss','♥':'sh','♦':'sd','♣':'sc'}
def suits(t): return re.sub('[♠♥♦♣]',lambda m:f'<span class="{SC[m[0]]}">{m[0]}</span>',t)
DK={'A':'E','K':'K','Q':'D','J':'B','T':'10'}
def card(c): return DK.get(c,c)
def hand(h,cls,lab):
    r=''.join(f'<div><span class="{c}">{s}</span> {" ".join(card(x) for x in hh) or "—"}</div>' for s,c,hh in zip('♠♥♦♣',['ss','sh','sd','sc'],h.split('.')))
    return f'<div class="hand {cls}"><i>{lab}</i>{r}</div>'
DL={'N':'N','E':'Ø','S':'S','W':'V'}; VL={'None':'Ingen i zonen','NS':'N-S i zonen','EW':'Ø-V i zonen','All':'Alle i zonen'}
def rows(bn):
    r=boards[str(bn)]['rows']; i=0; out=[]
    isb=lambda j: re.match(r'^\d+$',r[j]) and j+1<len(r) and re.match(r'^(Nord|Syd|Øst|Vest)/$',r[j+1])
    while i+3<len(r) and (' - ' in r[i] or r[i]=='(Oversidder)'):
        ns,ew=int(r[i+1]),int(r[i+3]); i+=4; j=i
        while j<len(r) and not (' - ' in r[j] or r[j]=='(Oversidder)' or isb(j)): j+=1
        f=[x.replace("\xa0"," ").strip() for x in r[i:j]]; i=j
        if f[0]=='M': continue
        m=re.match(r'^([NSØV]) (\d)(UT|[♠♥♦♣])( D)?$',f[0]); assert m,f
        out.append(dict(ns=ns,ew=ew,decl=m[1],lvl=m[2],st=m[3],dbl=bool(m[4]),lead=f[1],tricks=int(f[2]),score=int(f[3]),pct=f[6]))
    return out
def deal(bn):
    d=boards[str(bn)]['deal']
    return (f'<div class="deal"><div class="dmeta"><b>{bn}</b><span>Giver {DL[d["dealer"]]}</span><span>{VL[d["vul"]]}</span></div>'
      +hand(d['N'],'hn','N')+hand(d['W'],'hw','V')+'<div class="compass" aria-hidden="true"><b>N</b><b>V</b><b>Ø</b><b>S</b></div>'+hand(d['E'],'he','Ø')+hand(d['S'],'hs','S')+'</div>')
def ddt(bn):
    dd=boards[str(bn)]['dd'][6:]; t={dd[i]:dd[i+1:i+6] for i in range(0,28,7)}
    def row(a,b,l): return f'<tr><th>{l}</th>'+''.join(f'<td>{x if x==y else x+"/"+y}</td>' for x,y in zip(t[a],t[b]))+'</tr>'
    return suits('<table class="dd"><thead><tr><th></th><th>UT</th><th>♠</th><th>♥</th><th>♦</th><th>♣</th></tr></thead><tbody>')+row('N','S','N-S')+row('Ø','V','Ø-V')+'</tbody></table>'
LEFT={'N':'E','E':'S','S':'W','W':'N'}; SEAT={'N':'N','S':'S','Ø':'E','V':'W'}; SI={'♠':0,'♥':1,'♦':2,'♣':3}
def lead(bn,r):
    l=r['lead']; d=boards[str(bn)]['deal']; h=d[LEFT[SEAT[r['decl']]]].split('.')
    if not re.match(r'^[♠♥♦♣][2-9TJQKA]$',l) or l[1] not in h[SI[l[0]]]: return '?'
    return l[0]+card(l[1])
def num(n): return ('+' if n>0 else '−' if n<0 else '')+str(abs(n))
def table(bn,hi):
    o='<div class="tw"><table class="rooms"><thead><tr><th>N-S</th><th>Ø-V</th><th>Kontrakt</th><th>Udspil</th><th class="num">Stik</th><th class="num">Score</th><th class="num">N-S %</th></tr></thead><tbody>'
    for r in rows(bn):
        c='pos' if r['score']>0 else 'neg'
        k=f'{r["lvl"]}{r["st"]}{"×" if r["dbl"] else ""} {r["decl"]}'
        o+=f'<tr{" class=\"hi\"" if (r["ns"] in hi or r["ew"] in hi) else ""}><td>{P[r["ns"]]}</td><td>{P[r["ew"]]}</td><td class="nw">{k}</td><td class="nw">{lead(bn,r)}</td><td class="num">{r["tricks"]}</td><td class="num"><span class="{c}">{num(r["score"])}</span></td><td class="num">{r["pct"]}</td></tr>'
    return suits(o+'</tbody></table></div>')
def xr(bn,p):
    if not OTHER: return p
    f,_,row,oq,key=OTHER
    h=f'{f}#b{bn}' if bn in key else f'{U}spilresultater.php?{oq}&amp;round=1&amp;half=1#B{bn}'
    return re.sub(f'{row}|begge rækker|de to rækker',lambda m:f'<a href="{h}">{m[0]}</a>',p,count=1)
def board(bn,title,top,toplbl,hi,paras):
    ps=''.join(f'<p class="prose">{suits(xr(bn,p))}</p>' for p in paras)
    return (f'<article class="board" id="b{bn}"><header><div><p class="eyebrow">Spil {bn}</p><h3>{title}</h3></div><div class="swing pos">{top}<small>{toplbl}</small></div></header>\n'
      f'<div class="bgrid"><div class="bleft">{deal(bn)}{ddt(bn)}</div><div class="bright">{table(bn,hi)}{ps}</div></div></article>')
B=[
(5,'Storeslem i spar','+2210','Top N-S',{8,3},[
 'N-S har 31 HP og ni spar. Når trumferne er trukket, er der 13 stik: Nords tabere i hjerter og klør forsvinder på Syds ruder eller trumfes. Det eneste spørgsmål er spar dame.',
 'Storeslemmen står, når damen falder under es og konge, eller når den kan knibes hos Øst. Sidder den tredje hos Vest, går 7♠ en ned. Chancen er lidt over 50 %, og her sad trumferne 2-2.',
 '<b>Dyrekilde–Dyrekilde Sommerlund</b> meldte 7♠ som det eneste par i begge rækker: 2210 og ren top. <b>Lind Jensen–Grossman</b> meldte lilleslemmen og fik 1460 og 66,7 %. I A-rækken stoppede tre af fire par i 6♠.']),
(21,'Slem og delkontrakt på samme kort','+1430','Top N-S',{8,5},[
 'N-S har 28 HP og ni spar, men med åbne kort to trumftabere: Øst har esset single, og Vest har D-3-2 bag Syds K-B. Det giver 11 stik på ethvert udspil.',
 '<b>Dyrekilde–Dyrekilde Sommerlund</b> meldte 6♠. Spar es kom ud, og ved bordet blev det til 12 stik: 1430 og ren top. Slemmen kræver normalt, at spar dame sidder foran K-B, og at forsvaret ikke får en hjertertrumfning.',
 '<b>Steiner–Thygesen</b> fik toppen den anden vej. Øst har 6-5 i ruder og hjerter og fik lov at spille 3♦: otte stik, én ned, 50 til N-S mod en udgang til 650. I A-rækken gik Øst i 5♦ doblet på de samme kort; det kostede 800.']),
(11,'Otte spar hos Syd','+140','Top N-S',{7,6},[
 'Syd har otte spar og blev spilfører ved alle fire borde. Ø-V har 26 HP og kan med åbne kort vinde udgang i hjerter med 11 eller 12 stik, 450 eller 480.',
 'I spar er der otte stik med åbne kort. 4♠ én ned koster 50, og selv to doblede beter, 300, er billigere end udgangen. <b>Koks Andreassen–Øxseth</b> fik lov at spille 3♠, fik ni stik og toppen: 140.',
 'På femtrinnet vender regnestykket. <b>Rasmussen–Haugaard Jensen</b> doblede 5♠, og fire beter gav 800, mere end udgangen.']),
(17,'Syv klør fra toppen','+570','Top N-S',{7,2},[
 'Nord har syv klør med E-K-D, og farven går, fordi de fire sidste sidder 2-2. Vest har 18 HP, og med åbne kort kan Ø-V vinde 4♥, men det blev N-S, der fik de store plusser.',
 '<b>Egstrup–Veibel Petersen</b> meldte 3UT med 19 HP og Nords klørfarve. Med åbne kort er der otte stik mod de fleste udspil; en lille hjerter giver det niende. Hjerter 8 kom ud: 400.',
 '<b>Koks Andreassen–Øxseth</b> blev doblet i 3♣. Med åbne kort er der otte eller ni stik; ved bordet blev det ti. Doblet er 3♣ en udgang, og med overstik giver det 570 og ren top.',
 'Dyrekilde–Dyrekilde Sommerlund tog otte stik mod Vests 1UT: 100.']),
(13,'3UT på en knibning','630','Top Ø-V',{2,5},[
 'Ø-V har 23 HP. 3UT har ni stik med åbne kort: fem i spar, fordi kongen sidder til knib hos Syd, ruder es, to i klør og et i hjerter. Sidder spar konge hos Nord, går kontrakten ned.',
 '<b>Egstrup–Veibel Petersen</b> var det eneste par i 3UT i begge rækker. Hjerter es kom ud, og det blev ti stik: 630 og ren top til Ø-V.',
 'Syd spillede 2♥ ved to borde og gik to ned i zonen, 200 til Ø-V. <b>Steiner–Thygesen</b> forsvarede i stedet mod 2♠ og holdt Øst på ni stik, det maksimale efter hjerter es ud. 140 til Ø-V var toppen for N-S.']),
(23,'Stop i tide','+140','Top N-S',{1,4},[
 'N-S har 24 HP og 4-4 i spar, men Vest har D-10-9-7 i trumf, og ruderne sidder 5-1. Med åbne kort er der otte stik mod hjerter ud. 4♠ gik ned ved alle fem borde, der meldte den i de to rækker.',
 '<b>Nielsen–Brix</b> stoppede i 2♠, fik ni stik og var det eneste N-S-par med plus: 140 og ren top.',
 '<b>Meldgaard–Christensen</b> fik Ø-V-toppen: syv stik i forsvaret mod 4♠, fire ned i zonen, 400.']),
]
ST=[(8,'Birgitte Dyrekilde – Benjamin Dyrekilde Sommerlund',73.8,57.0),(5,'Boy Steiner – Susan Thygesen',57.7,43.7),(2,'Christina Egstrup – Bo Veibel Petersen',50.0,54.7),(7,'Ulrik Koks Andreassen – Bente Øxseth',48.8,54.0),(3,'Allan Lind Jensen – Edith Grossman',48.2,48.2),(6,'Nakako Rasmussen – Birgitte Haugaard Jensen',47.6,54.8),(1,'Bente Nielsen – Karin Brix',39.9,45.2),(4,'Karen Meldgaard – Lars Bo Christensen',33.9,42.4)]
MP={8:'124,0',5:'97,0',2:'84,0'}
ROW='B-rækken'; EYE='B-rækken – RØD'; OTHER=('2026-10-19-a-raekken-blaa.html','A-rækkens rapport','A-rækken','filename=2132/MT491GT1439.XML&amp;tournament=491&amp;section=1',{9,5,7,2,19,21})
LEDE='Dyrekilde–Dyrekilde Sommerlund vandt med 73,8 % og ti rene toppe, blandt dem aftenens eneste storeslem. Steiner–Thygesen blev nummer to, 14 procentpoint over forventet.'
AFTEN='''<p class="prose"><b>Birgitte Dyrekilde – Benjamin Dyrekilde Sommerlund</b> vandt med 124 point, 27 foran nummer to. De fik ti rene toppe i 28 spil og meldte både storeslemmen i <a href="#b5">spil 5</a> og lilleslemmen i <a href="#b21">spil 21</a>.</p>
<p class="prose"><b>Boy Steiner – Susan Thygesen</b> var efter handicap sat til 43,7 % og scorede 57,7 %. De fik toppe på begge linjer, bl.a. i <a href="#b13">spil 13</a> og <a href="#b21">spil 21</a>. <b>Christina Egstrup – Bo Veibel Petersen</b> blev nummer tre på præcis middel og meldte to udgange i sans, som ingen andre fandt: <a href="#b13">spil 13</a> og <a href="#b17">spil 17</a>.</p>
<p class="prose">Toppene var bredt fordelt. <b>Ulrik Koks Andreassen – Bente Øxseth</b> fik syv, bl.a. i <a href="#b11">spil 11</a> og <a href="#b17">spil 17</a>, og <b>Bente Nielsen – Karin Brix</b> var alene om plus på N-S-kortene i <a href="#b23">spil 23</a>.</p>'''
TOPPE='''<li><b>Boy Steiner – Susan Thygesen</b> vandt 3UT i spil 7 som Ø-V (600), hvor de tre andre borde spillede delkontrakt, og var eneste N-S-par med plus i både spil 14 (50) og spil 16 (90).</li>
<li><b>Christina Egstrup – Bo Veibel Petersen</b> tog alle 13 stik i 3UT i spil 2: 720 og ren top foran 5♣ med overstik (620).</li>
<li><b>Ulrik Koks Andreassen – Bente Øxseth</b> vandt 4♥ i spil 19 (420) og 3UT som Ø-V i både spil 1 (430) og spil 3 (600), alle tre rene toppe.</li>
<li><b>Allan Lind Jensen – Edith Grossman</b> fik ti stik i 2UT i spil 18 (180), det maksimale med åbne kort, og 300 mod 3♦ i spil 26.</li>
<li><b>Nakako Rasmussen – Birgitte Haugaard Jensen</b> satte 4♥ to gange i spil 18 (100) og hentede 300 i forsvaret i både spil 10 og spil 12.</li>
<li><b>Bente Nielsen – Karin Brix</b> var det eneste par, der meldte og vandt 4♥ på Ø-V-kortene i spil 8 (450).</li>
<li><b>Karen Meldgaard – Lars Bo Christensen</b> satte 5♦ i spil 4 (100, ren top).</li>'''
LEADS=''
dk=lambda x:f'{x:.1f}'.replace('.',',')
def diff(a,b):
    d=round(a-b,1); return f'<span class="{"pos" if d>0 else "neg" if d<0 else "zero"}">{num(0) if d==0 else ("+" if d>0 else "−")+dk(abs(d))}</span>'
cards=''.join(f'<div class="match"><p class="eyebrow">{i+1}. plads</p><p class="vs">{n}</p><p class="score"><b>{dk(p)}</b> <span>%</span></p><p class="vp">{MP[k]} MP · forventet {dk(e)} %</p></div>' for i,(k,n,p,e) in enumerate(ST[:3]))
stand=''.join(f'<tr><td class="num">{i+1}</td><td>{n}</td><td class="num">{dk(p)}</td><td class="num">{dk(e)}</td><td class="num">{diff(p,e)}</td></tr>' for i,(k,n,p,e) in enumerate(ST))
out=f'''<!doctype html>
<html lang="da">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gentofte Bridgeklub, {ROW}, 19. oktober</title>
<meta name="claude:viewport-fit-sides" content="cover">
{font}
{css}
<div class="wrap">
<header class="top">
<p class="eyebrow">Gentofte Bridgeklub · {EYE} · Parturnering #491 · Mandag 19. oktober 2026</p>
<h1>Mandag aften, 19. oktober</h1>
<p class="lede">{LEDE}</p>
<div class="matches">{cards}</div>
<p class="src">8 par, Howell, 28 spil, top 6 pr. spil. <a href="{U}resultater.php?{Q}">Resultater</a> · <a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1">Spilresultater</a> · <a href="{U}kortfordeling.php?{Q}">Kortfordeling</a> · <a href="{U}pairhacscore.php?{Q}">Handicapscore</a> · <a href="{OTHER[0]}">{OTHER[1]}</a></p>
<nav><a href="#aften">Aftenen kort</a><a href="#stilling">Slutstilling</a><a href="#boards">Nøglespil</a><a href="#toppe">Blandede toppe</a><a href="#method">Noter</a></nav>
</header>
<section id="aften"><h2>Aftenen kort</h2>
{suits(AFTEN)}
</section>
<section id="stilling"><h2>Slutstilling</h2>
<div class="tw"><table><thead><tr><th class="num">Plac.</th><th>Par</th><th class="num">%</th><th class="num">Forventet %</th><th class="num">Forskel</th></tr></thead><tbody>{stand}</tbody></table></div>
<p class="note">Forventet score er beregnet af arrangøren ud fra parrets handicap.</p>
</section>
<section id="boards"><h2>Nøglespil</h2>
{chr(10).join(board(*b) for b in B)}
</section>
<section id="toppe"><h2>Blandede toppe</h2>
<ul class="prose">
{suits(TOPPE)}
</ul></section>
<section id="method"><h2>Noter</h2>
<ul class="prose">
<li>På nøglespillene viser tallet øverst til højre topscoren på spillet, for N-S eller Ø-V som angivet. Den lille tabel under diagrammet giver antal stik med åbne kort for hver linje; to tal (f.eks. 11/10) betyder, at det afhænger af, om Nord eller Syd er spilfører.</li>
<li>Fremhævede rækker i resultattabellerne er de borde, teksten omtaler.</li>
<li>De to rækker spillede de samme kort. "Ren top" er 100 % på spillet.</li>
<li>Resultater, kortfordelinger og tabeller over stik med åbne kort kommer fra <a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1">Danmarks Bridgeforbunds resultatside</a>. Udspilsanalyserne med åbne kort er beregnet med Dealers medfølgende solver.</li>
<li>Chancen for storeslemmen i spil 5 er regnet som 2-2-sits eller single dame, 53 %.</li>
<li>Der findes ingen meldeforløb. Vurderinger af meldingerne bygger alene på slutkontrakterne.</li>
<li>Navnene følger parrene, da resultatlisten ikke viser, hvem der sad på hvilken plads.</li>
{suits(LEADS)}
</ul></section>
<footer>De samme kort blev spillet i begge rækker: <a href="{OTHER[0]}">{OTHER[1]}</a>.</footer>
</div>
</html>
'''
KEY={b[0] for b in B}
def ext(t): return re.sub(r'(?<!">)\b[Ss]pil (\d+)',lambda m:f'<a href="#b{m[1]}">{m[0]}</a>' if int(m[1]) in KEY else f'<a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1#B{m[1]}">{m[0]}</a>',t)
def pairs(t):
    for k,n,*_ in ST: t=t.replace(f'<b>{n}</b>',f'<b><a href="{U}personligt_regnskab.php?{Q}&amp;pairno={k}">{n}</a></b>')
    return t
def sect(t,a,b,f): i=t.index(a); j=t.index(b,i); return t[:i]+f(t[i:j])+t[j:]
out=sect(out,'<section id="aften">','<section id="stilling">',ext)
out=sect(out,'<section id="toppe">','<section id="method">',lambda t:pairs(ext(t)))
open(sys.argv[3],'w',encoding='utf-8').write(out)
for b in B:
    print(b[0],[(r['ns'],r['ew'],r['lead'],lead(b[0],r)) for r in rows(b[0]) if lead(b[0],r)=='?'], len(rows(b[0])))
