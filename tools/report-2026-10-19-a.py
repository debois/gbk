import json,re,sys,html
boards=json.load(open(sys.argv[1])); ref=open(sys.argv[2],encoding='utf-8').read()
css=ref[ref.index('<style>'):ref.index('</style>')+8]
font=re.search(r'<link rel="stylesheet"[^>]*>',ref)[0]
Q='filename=2132/MT491GT1439.XML&amp;tournament=491&amp;section=1'
U='https://resultater.bridge.dk/template/'
P={1:'Nord Jørgensen–Suh Nicolaisen',2:'Henrichsen–Kofoed',3:'Debois–Hareskov',4:'Fogel–Guttermann',5:'Fardan–Nodal',6:'Rosenbaum–Vainer',7:'Ipsen–Ingolfsson',8:'Christensen–Husted'}
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
def board(bn,title,top,toplbl,hi,paras):
    ps=''.join(f'<p class="prose">{suits(p)}</p>' for p in paras)
    return (f'<article class="board" id="b{bn}"><header><div><p class="eyebrow">Spil {bn}</p><h3>{title}</h3></div><div class="swing pos">{top}<small>{toplbl}</small></div></header>\n'
      f'<div class="bgrid"><div class="bleft">{deal(bn)}{ddt(bn)}</div><div class="bright">{table(bn,hi)}{ps}</div></div></article>')
B=[
(9,'Lilleslem med 30 HP','+1010','Top N-S',{5},[
 'N-S har 30 HP, ni hjerter og otte spar, og der mangler kun klør es. 6♥ har 12 stik på ethvert udspil: seks i trumf, tre i spar, to i ruder og en rudertrumfning hos Syd. Kun klør ud forhindrer det 13.',
 '<b>Fardan–Nodal</b> var det eneste par, der meldte slemmen. Ruder 2 kom ud, og det blev 13 stik: 1010 og ren top til aftenens vindere. Ved de tre andre borde blev det 12 stik i 4♥ eller 5♥, 480.']),
(5,'Seks eller syv?','+1460','Top N-S',{3,4,6},[
 'N-S har 31 HP og ni spar. Når trumferne er trukket, er der 13 stik: Nords tabere i hjerter og klør forsvinder på Syds ruder eller trumfes. Det eneste spørgsmål er spar dame.',
 'Storeslemmen står, når damen falder under es og konge, eller når den kan knibes hos Øst. Sidder den tredje hos Vest, går 7♠ en ned. Chancen er lidt over 50 %, og her sad trumferne 2-2.',
 '<b>Rosenbaum–Vainer</b>, <b>Debois–Hareskov</b> og <b>Fogel–Guttermann</b> meldte lilleslemmen og fik 13 stik: 1460 og 66,7 % til hver. Ingen i A-rækken gik i syv; i B-rækken blev storeslemmen meldt ved ét bord.']),
(7,'Doblet udgang med 15 HP','+790','Top N-S',{2},[
 'N-S har kun 15 HP, men ni spar og en singleton i hver hånd. 4♠ har ti stik på ethvert udspil, fordi spar konge sidder til knib hos Øst. Sidder kongen hos Vest, kan udgangen sættes.',
 'Ø-V har 25 HP og doblede ved tre borde. <b>Debois–Hareskov</b> og <b>Fogel–Guttermann</b> fik ti stik i 4♠ doblet, 790. <b>Rosenbaum–Vainer</b> blev doblet i 3♠ og fik ni stik: 730.',
 '<b>Henrichsen–Kofoed</b> meldte i stedet 5♣ på Ø-V-linjen og blev ikke doblet. Tre beter i zonen koster 300, mindre end alle tre sparkontrakter, og gav Ø-V toppen. Doblet havde det været 800.']),
(2,'Tre udgange, tre scorer','+690','Top N-S',{3},[
 'N-S har 25 HP og ti klør, og tre af fire borde var i udgang, i hver sin farve. Klør konge sidder til knib, så klørfarven giver syv stik. Efter hjerter ud er der 12 stik i sans og 11 i spar; i klør er der 13.',
 'I parturnering afgør de små forskelle: <b>Debois–Hareskov</b> fik 690 for 3UT med tre overstik, Henrichsen–Kofoed 650 for 4♠ med et, og Christensen–Husted 640 for 5♣ med to.',
 '3UT er ikke uden risiko. Sidder klør konge hos Øst, går kontrakten ned mod hjerter ud, mens 5♣ stadig står. Af samme grund er 6♣ i praksis en knibning, og ingen meldte den.']),
(19,'Udgang med 22 HP','+420','Top N-S',{8,3},[
 'N-S har 22 HP og ni hjerter. 4♥ har ti stik på ethvert udspil; der er kun tre tabere, et sparstik og to i ruder.',
 '<b>Christensen–Husted</b> meldte som de eneste udgangen: 420 og ren top. Ved de tre andre borde stoppede N-S i 1UT eller 2♥.',
 'I 1UT hos Nord kan forsvaret med åbne kort tage de første ni stik efter ruder eller spar ud. <b>Debois–Hareskov</b> tog otte, og 100 til Ø-V blev toppen den vej.']),
(21,'Én bet for meget','+800','Top N-S',{7},[
 'N-S har 28 HP og ni spar, men to trumftabere: Øst har esset single, og Vest har D-3-2 bag Syds K-B. Der er 11 stik, og udgangen giver 650.',
 'Øst har 6-5 i ruder og hjerter og meldte ved ét bord 5♦ uden for zonen. Med åbne kort er der syv stik på ethvert udspil. <b>Ipsen–Ingolfsson</b> doblede og fik 800 for fire beter, 150 mere end udgangen og ren top.',
 'Marginen er ét stik: tre beter, 500, havde givet Ø-V toppen i stedet.']),
]
ST=[(5,'Rolf Fardan – Marianne Nodal',58.3,47.8),(8,'Claus Torben Christensen – Camilla Husted',56.6,52.9),(3,'Søren Debois – Lars Hareskov',52.4,50.8),(4,'Bent Fogel – Erling Guttermann',50.0,50.0),(6,'Eva Rosenbaum – Gert Vainer',49.4,48.9),(1,'Johannes Nord Jørgensen – Lene Suh Nicolaisen',47.6,49.5),(2,'Jørgen Henrichsen – Jannik Kofoed',45.8,49.0),(7,'Maja Ipsen – Jon Ingolfsson',39.9,51.1)]
MP={5:'98,0',8:'95,0',3:'88,0'}
ROW='A-rækken'; EYE='A-rækken – BLÅ'; OTHER=('2026-10-19-b-raekken-roed.html','B-rækkens rapport')
LEDE='Fardan–Nodal vandt med 58,3 %, tre point foran Christensen–Husted, og var alene om lilleslemmen i spil 9. Storeslemmen i spil 5 stod, men blev ikke meldt i A-rækken.'
AFTEN='''<p class="prose"><b>Rolf Fardan – Marianne Nodal</b> vandt med 98 point, tre foran <b>Claus Torben Christensen – Camilla Husted</b>. Vinderne var alene om lilleslemmen i <a href="#b9">spil 9</a> og vandt 3UT med 21 HP i spil 20. De var efter handicap sat til 47,8 % og tog rækkens største handicapgevinst (−0,69).</p>
<p class="prose">Christensen–Husted fik syv rene toppe, flere end noget andet par, bl.a. som eneste par i udgang i <a href="#b19">spil 19</a>. <b>Søren Debois – Lars Hareskov</b> blev nummer tre med 52,4 % og fik toppen i <a href="#b2">spil 2</a>.</p>
<p class="prose">Storeslemmen i <a href="#b5">spil 5</a> stod, men afhang af spar dame, og tre par nøjedes med seks. <b>Maja Ipsen – Jon Ingolfsson</b> hentede 800 i <a href="#b21">spil 21</a>, og <b>Jørgen Henrichsen – Jannik Kofoed</b> fandt den billige vej ud af <a href="#b7">spil 7</a>, hvor tre N-S-par vandt doblede sparkontrakter.</p>'''
TOPPE='''<li><b>Johannes Nord Jørgensen – Lene Suh Nicolaisen</b> fik 11 stik i 3UT i spil 25 (460, ren top), hvor to borde gik ned i samme kontrakt, og satte 3♦ to gange i spil 13 (200, 83,3 %).</li>
<li><b>Jørgen Henrichsen – Jannik Kofoed</b> var alene i 4♥ i spil 28 (620), som med åbne kort kun går ned mod klør 10, 9 eller 8 ud. De fik også 12 stik i 4♥ i spil 4 (680) og vandt 1UT doblet med to overstik i spil 6 (580).</li>
<li><b>Bent Fogel – Erling Guttermann</b> vandt 4♥ i spil 1 som det eneste Ø-V-par med plus i udgang (420) og fik 300 mod 3♥ i spil 13.</li>
<li><b>Eva Rosenbaum – Gert Vainer</b> satte 4♦ i spil 6 som eneste N-S-par med plus (100) og fik 12 stik i 5♥ i spil 11 (480, ren top).</li>
<li><b>Maja Ipsen – Jon Ingolfsson</b> holdt 4♥ på ti stik i spil 4, det eneste bord uden overstik.</li>
<li><b>Claus Torben Christensen – Camilla Husted</b> fik 100 for 5♦ doblet én ned i spil 12 og ni stik i 2UT i spil 27 (150).</li>'''
LEADS='<li>Et spørgsmålstegn i udspilskolonnen betyder, at det noterede udspil ikke findes på udspillerens hånd. I spil 9 er klør 10 noteret mod 5♥, men Øst har ikke kortet. I spil 7 er hjerter es noteret mod 5♣, men esset sidder hos Nord, og Syd har udspillet. I spil 21 er ruder bonde noteret mod 5♠, men Vest har ikke kortet.</li>'
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
