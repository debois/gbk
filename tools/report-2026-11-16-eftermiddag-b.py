import json,re,sys,html
boards=json.load(open(sys.argv[1])); ref=open(sys.argv[2],encoding='utf-8').read()
css=ref[ref.index('<style>'):ref.index('</style>')+8]
font=re.search(r'<link rel="stylesheet"[^>]*>',ref)[0]
Q='filename=2132/MT493GT1449.XML&amp;tournament=493&amp;section=3'
U='https://resultater.bridge.dk/template/'
P={1:'Brunetti–Brunetti',2:'Frost–Søndergaard',3:'Steen–Nibak',4:'Wille Jensen–Hansen',5:'Guldbech Bjerregaard–Thorup Andersen',6:'Andersen–Kofoed',7:'Stephensen–Lemvigh',8:'Mehlbye–Thost',9:'Mønsted–Mønsted',10:'Grove-Rasmussen–Grove-Rasmussen',11:'Berg–Malmqvist',12:'Plenov–Kok'}
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
        if f[0]=='P': out.append(dict(ns=ns,ew=ew,decl=None,lead='',tricks='–',score=int(f[-5] or 0),pct=f[-2])); continue
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
    if not r['decl']: return '–'
    l=r['lead']; d=boards[str(bn)]['deal']; h=d[LEFT[SEAT[r['decl']]]].split('.')
    if not re.match(r'^[♠♥♦♣][2-9TJQKA]$',l) or l[1] not in h[SI[l[0]]]: return '?'
    return l[0]+card(l[1])
def num(n): return ('+' if n>0 else '−' if n<0 else '')+str(abs(n))
def table(bn,hi):
    o='<div class="tw"><table class="rooms"><thead><tr><th>N-S</th><th>Ø-V</th><th>Kontrakt</th><th>Udspil</th><th class="num">Stik</th><th class="num">Score</th><th class="num">N-S %</th></tr></thead><tbody>'
    for r in rows(bn):
        c='pos' if r['score']>0 else 'neg'
        k=f'{r["lvl"]}{r["st"]}{"×" if r["dbl"] else ""} {r["decl"]}' if r['decl'] else 'Pas'
        o+=f'<tr{" class=\"hi\"" if (r["ns"] in hi or r["ew"] in hi) else ""}><td>{P[r["ns"]]}</td><td>{P[r["ew"]]}</td><td class="nw">{k}</td><td class="nw">{lead(bn,r)}</td><td class="num">{r["tricks"]}</td><td class="num"><span class="{c}">{num(r["score"])}</span></td><td class="num">{r["pct"]}</td></tr>'
    return suits(o+'</tbody></table></div>')
def xr(bn,p):
    if not OTHER: return p
    f,_,row,oq,key=OTHER
    h=f'{f}#b{bn}' if bn in key else f'{U}spilresultater.php?{oq}&amp;round=1&amp;half=1#B{bn}'
    return re.sub(f'{row}|begge rækker|de to rækker',lambda m:f'<a href="{h}">{m[0]}</a>',p,count=1)
def bid(bn,a):
    if not a: return ''
    cap,calls=a; fn=[x[1] for x in calls if isinstance(x,tuple)]; k=iter(range(1,99))
    c=['']*'WNES'.index(boards[str(bn)]['deal']['dealer'])+[f'{x[0]}<sup>{next(k)}</sup>' if isinstance(x,tuple) else x for x in calls]; c+=['']*(-len(c)%4)
    return suits(f'<p class="lbl">{cap}</p><table class="bid"><thead><tr><th>V</th><th>N</th><th>Ø</th><th>S</th></tr></thead><tbody>'+''.join('<tr>'+''.join(f'<td>{x}</td>' for x in c[i:i+4])+'</tr>' for i in range(0,len(c),4))+'</tbody></table>'+''.join(f'<p class="src"><sup>{i+1}</sup> {x}</p>' for i,x in enumerate(fn)))
def board(bn,title,top,toplbl,hi,paras,auction=None):
    ps=''.join(f'<p class="prose">{suits(xr(bn,p))}</p>' for p in paras)
    return (f'<article class="board" id="b{bn}"><header><div><p class="eyebrow">Spil {bn}</p><h3>{title}</h3></div><div class="swing pos">{top}<small>{toplbl}</small></div></header>\n'
      f'<div class="bgrid"><div class="bleft">{deal(bn)}{ddt(bn)}</div><div class="bright">{table(bn,hi)}{"" if auction else ps}</div>{f'<div class="bleft">{bid(bn,auction)}</div><div class="bright">{ps}</div>' if auction else ""}</div></article>')
ROW='B-rækken'; OTHER=('2026-11-16-eftermiddag-a.html','A-rækkens rapport','A-rækken','filename=2132/MT493GT1448.XML&amp;tournament=493&amp;section=3',{24,1,26,23,2,18})
B=[
(24,'28 HP og to par i udgang','+490','Top N-S',{9,2},[
 'N-S har 28 HP, og Syd har seks gående klør. 6♣ har 12 stik på ethvert udspil: seks klør, to spar, ruder es-konge og de små ruder hos Nord, som rejses med en trumfning, når farven sidder 3-2. Sidder ruderne 4-1, er der hjerterknibningen at falde tilbage på. Slemmen står, når blot én af delene lykkes, godt 80 %.',
 '<b>Mønsted–Mønsted</b> valgte 3UT og fik 12 stik efter hjerter es ud: 490 og ren top. <b>Frost–Søndergaard</b> var alene i 5♣ og fik 420 for de samme 12 stik. I parturnering slår sans med overstik minorudgangen.',
 'De fire andre borde spillede delkontrakt i klør. I A-rækken var kun ét par i udgang, og ingen meldte slemmen.']),
(21,'Syv klørstik og to esser','+660','Top N-S',{9,8},[
 'N-S har kun 21 HP, men Syd har syv gående klør, og Nord lægger to esser til. Det er ni stik fra toppen i sans, og i zonen er udgangen 600 værd mod 130 for en delkontrakt i klør.',
 '<b>Mønsted–Mønsted</b> og <b>Mehlbye–Thost</b> var de to par, der meldte 3UT. De fik 11 og 10 stik, 660 og 630. De fire andre borde spillede 2♣ eller 3♣. I A-rækken var ét par i 3UT.']),
(15,'To vundne udgange','+630','Top N-S',{1,8},[
 'N-S har 25 HP og otte hjerter. Med åbne kort er der højst ni stik i hjerter og, efter spar ud, syv i sans.',
 '<b>Brunetti–Brunetti</b> meldte 3UT, fik spar 2 ud og tog ti stik: 630 og ren top. <b>Mehlbye–Thost</b> fik ti stik i 4♥ efter spar dame ud, 620. Ved tre andre borde gik 4♥ eller 4♣ én ned. I A-rækken vandt ingen udgang på spillet.']),
(3,'Otte ruder hos Vest','+420','Top N-S',{7,11},[
 'Vest har otte ruder til E-K-B-10 og ingen hjerter. Ruder dame sidder anden hos Syd og falder under es og konge, så farven giver otte stik. 3UT hos Øst har ni stik på ethvert udspil.',
 '<b>Berg–Malmqvist</b> blev doblet i 3UT og fik ti stik: 950 og ren top til Ø-V. To andre Ø-V-par fik 600 i samme kontrakt.',
 '<b>Stephensen–Lemvigh</b> fik toppen den anden vej: Syd spillede 4♥ og tog ti stik, 420. Med åbne kort er der ni efter ruder es ud. I A-rækken spillede ingen Ø-V-par 3UT; dér blev 5♦ doblet tre ned for 800.']),
(7,'23 HP hos Nord','+650','Top N-S',{10,6},[
 'Nord har 23 HP, og Syd lægger to esser til, i alt 31 HP. Der er 11 stik i både sans og spar. Sparene sidder 4-2 med B-10 fjerde hos Øst, så der er en taber dér og en til i hjerter. Lilleslem står ikke.',
 'To par meldte 6UT og gik ned. Blandt udgangene afgjorde overstikkene: <b>Grove-Rasmussen–Grove-Rasmussen</b> og <b>Andersen–Kofoed</b> spillede 4♠ med 11 stik, 650, og delte toppen foran 4UT med ti stik (630) og 3UT med ni (600). I A-rækken gav 3UT med 11 stik 660 ved tre borde.']),
(2,'Spar mod klør','+620','Top N-S',{4,3,1},[
 'N-S har ti spar og 22 HP, Ø-V 11 klør og 18 HP. Med åbne kort har begge sider ti stik i deres farve: 4♠ står, og 5♣ går én ned. Det bedste, Ø-V kan gøre, er at ofre i 5♣ doblet for 100.',
 '<b>Wille Jensen–Hansen</b> og <b>Steen–Nibak</b> meldte og vandt 4♠: 620 og 90 % til hver.',
 '<b>Brunetti–Brunetti</b> blev doblet i 5♣ og vandt kontrakten med 11 stik: 550 og ren top til Ø-V. <b>Mehlbye–Thost</b> fik lov at spille 3♣ og tog ti stik, 130 og 80 %. I A-rækken spillede kun ét N-S-par 4♠; ved de fire andre borde spillede Ø-V 5♣ eller 6♣.']),
]
ST=[(8,'Jill Mehlbye – Per Thost',58.7,52.4),(9,'Stig Mønsted – Ulla Mønsted',57.1,52.4),(7,'Birthe Stephensen – Birgit Lemvigh',56.4,50.1),(6,'Vicki Andersen – Karsten Kofoed',55.5,45.5),(1,'Marianne Hvirvelkær Brunetti – Luciano Brunetti',53.3,52.8),(4,'Annelise Wille Jensen – Jes Hansen',49.6,50.8),(2,'Ulla Frost – Inger Søndergaard',49.6,52.2),(5,'Thomas Guldbech Bjerregaard (S) – Jens Thorup Andersen',48.7,51.7),(12,'Lise Plenov – Gerda Kok',46.7,43.5),(3,'Merete Steen – Merete Nibak',46.2,50.1),(10,'Steen Grove-Rasmussen – Jytte Grove-Rasmussen',44.2,51.3),(11,'Gyda Berg – Dorte Malmqvist',34.2,47.2)]
TOT=[('Grethe Kjeldsen – Birgit Jørgensen',(62.9,66.2,None),'64,58'),('Ulla Frost – Inger Søndergaard',(55.7,58.2,49.6),'54,46'),('Jill Mehlbye – Per Thost',(52.6,52.1,58.7),'54,43'),('Vicki Andersen – Karsten Kofoed',(None,48.7,55.5),'52,11'),('Steen Grove-Rasmussen – Jytte Grove-Rasmussen',(62.2,48.9,44.2),'51,74'),('Stig Mønsted – Ulla Mønsted',(41.4,54.2,57.1),'50,89'),('Annelise Wille Jensen – Jes Hansen',(42.6,55.6,49.6),'49,25'),('Vibeke Veng Christensen – Jens Thorup Andersen',(51.0,45.0,48.7),'48,25'),('Merete Steen – Merete Nibak',(54.2,42.8,46.2),'47,75'),('Gyda Berg – Dorte Malmqvist',(49.6,57.8,34.2),'47,18'),('Birthe Stephensen – Birgit Lemvigh',(41.8,36.3,56.4),'44,81'),('Lise Plenov – Gerda Kok',(35.0,34.3,46.7),'38,66')]
TOTNOTE='Sektionsresultaterne tæller for turneringsparret, også når der er spillet med substitut. Kjeldsen–Jørgensen spillede i A-rækken denne mandag; resultatet dér indgår ikke her. Andersen–Kofoed spillede ikke 1. sektion. Brunetti–Brunetti spillede med i 3. sektion og indgår ikke i den samlede stilling.'
CARDS=[('Fører samlet','Grethe Kjeldsen – Birgit Jørgensen','64,6','%','54 spil · spillede i A-rækken i dag'),('Nr. 2 samlet','Ulla Frost – Inger Søndergaard','54,5','%','81 spil · 49,6 % i 3. sektion'),('Dagens største handicapgevinst','Vicki Andersen – Karsten Kofoed','−0,76','handicap','55,5 % · forventet 45,5 %')]
SRC='12 par, Howell, 27 spil, top 10 pr. spil.'
LEDE='Kjeldsen–Jørgensen fører B-rækken med 64,6 % før sidste sektion, ti procentpoint foran feltet. Mehlbye–Thost var bedst på dagen med 58,7 % og er nu 0,03 procentpoint fra andenpladsen.'
AFTEN='''<p class="prose"><b>Grethe Kjeldsen – Birgit Jørgensen</b> vandt de to første sektioner med 62,9 % og 66,2 % og fører Novemberpar med 64,6 %. Denne mandag spillede de i A-rækken, og resultatet dér tæller ikke med i B-rækkens stilling. Forspringet til nummer to er ti procentpoint.</p>
<p class="prose">Dagens bedste var <b>Jill Mehlbye – Per Thost</b> med 58,7 %, foran <b>Stig Mønsted – Ulla Mønsted</b> (57,1 %) og <b>Birthe Stephensen – Birgit Lemvigh</b> (56,4 %). Mehlbye–Thost meldte og vandt udgang i <a href="#b15">spil 15</a>, spil 17 og <a href="#b21">spil 21</a>. Mønsted–Mønsted tog rene toppe i <a href="#b21">spil 21</a> og <a href="#b24">spil 24</a>. <b>Vicki Andersen – Karsten Kofoed</b> scorede 55,5 % mod forventet 45,5 % og fik dagens største handicapgevinst (−0,76).</p>
<p class="prose">Sidste sektion spilles mandag 23. november. Kjeldsen–Jørgensen kan tåle en del: scorer de 45 % i sidste sektion, ender de på 58,1 %, og så skal forfølgerne bruge næsten 69 % for at nå forbi. Den åbne kamp gælder andenpladsen, hvor <b>Ulla Frost – Inger Søndergaard</b> har 54,46 % og Mehlbye–Thost 54,43 %. Andersen–Kofoed (52,1 % efter to sektioner), Grove-Rasmussen–Grove-Rasmussen (51,7 %) og Mønsted–Mønsted (50,9 %) er inden for rækkevidde.</p>'''
TOPPE='''<li><b>Birthe Stephensen – Birgit Lemvigh</b> satte 4♥ i spil 1 som eneste N-S-par med plus og købte som Ø-V kontrakten i spil 14 for én bet i 2♥: 50 og ren top, hvor N-S ellers fik mindst 170 i spar.</li>
<li><b>Vicki Andersen – Karsten Kofoed</b> satte 3UT i spil 12 og 5♦ to gange i spil 26 (ren top til Ø-V) og fik 12 stik i 4♥ i spil 11 (480).</li>
<li><b>Steen Grove-Rasmussen – Jytte Grove-Rasmussen</b> tog 12 stik i 3UT i spil 23 (690, ren top), satte 2UT to gange i spil 4 (200) og 3♣ i spil 13 (100), begge rene toppe.</li>
<li><b>Merete Steen – Merete Nibak</b> var det eneste par, der vandt 4♥ i spil 8 (420), og fik ti stik i 3UT i spil 10 (630). Begge var rene toppe til Ø-V.</li>
<li><b>Thomas Guldbech Bjerregaard – Jens Thorup Andersen</b> satte 5♦ tre gange i spil 5 (150) og 3UT i spil 10 (100), begge rene toppe.</li>
<li><b>Lise Plenov – Gerda Kok</b> vandt 2♥ med overstik i spil 20 (140) og satte 5♥ i spil 19, begge rene toppe til Ø-V.</li>
<li><b>Marianne Hvirvelkær Brunetti – Luciano Brunetti</b> tog 12 stik i 4♠ i spil 14: 480 og ren top.</li>
<li><b>Ulla Frost – Inger Søndergaard</b> fik 11 stik i 3UT i spil 23 (660) og 11 stik i 4♠ i spil 14 (450), 80 % på begge.</li>
<li><b>Jill Mehlbye – Per Thost</b> tog rene toppe i delkontrakt i spil 6 (1♠ med ni stik, 140) og spil 16 (3♠ med ti stik, 170).</li>'''
EXTRA='''<li>Spil 24: chancen for 6♣ er regnet som ruderne 3-2 (68 %) eller hjerter dame hos Øst, kontrolleret ved at flytte kortene og regne igen.</li>'''
LEADS=''
GEN='16. november 2026'; NAMES='Andersen i resultattabellerne er Vicki Andersen; Jens Thorup Andersen står som Thorup Andersen.'
names=f'<p class="note">{NAMES}</p>' if NAMES else ''
dk=lambda x:f'{x:.1f}'.replace('.',',')
def diff(a,b):
    d=round(a-b,1); return f'<span class="{"pos" if d>0 else "neg" if d<0 else "zero"}">{num(0) if d==0 else ("+" if d>0 else "−")+dk(abs(d))}</span>'
cards=''.join(f'<div class="match"><p class="eyebrow">{a}</p><p class="vs">{n}</p><p class="score"><b>{s}</b> <span>{u}</span></p><p class="vp">{v}</p></div>' for a,n,s,u,v in CARDS)
stand=''.join(f'<tr><td class="num">{i+1}</td><td>{n}</td><td class="num">{dk(p)}</td><td class="num">{dk(e)}</td><td class="num">{diff(p,e)}</td></tr>' for i,(k,n,p,e) in enumerate(ST))
tot=''.join(f'<tr><td class="num">{i+1}</td><td>{n}</td>'+''.join(f'<td class="num">{dk(x) if x else "–"}</td>' for x in s)+f'<td class="num"><b>{t}</b></td></tr>' for i,(n,s,t) in enumerate(TOT))
out=f'''<!doctype html>
<html lang="da">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gentofte Bridgeklub, {ROW}, mandag eftermiddag 16. november</title>
<meta name="claude:viewport-fit-sides" content="cover">
{font}
{css}
<div class="wrap">
<header class="top">
<p class="eyebrow">Gentofte Bridgeklub · {ROW} · Novemberpar #493 · 3. sektion af 4 · Mandag 16. november 2026</p>
<h1>Mandag eftermiddag, 16. november</h1>
<p class="lede">{LEDE}</p>
<div class="matches">{cards}</div>
<p class="src">{SRC} <a href="{OTHER[0]}">{OTHER[1]}</a></p>
<nav><a href="#aften">Før sidste sektion</a><a href="#boards">Nøglespil</a><a href="#toppe">I øvrigt</a><a href="#stilling">Stilling</a><a href="#method">Noter</a></nav>
</header>
<section id="aften"><h2>Før sidste sektion</h2>
{suits(AFTEN)}
</section>
<section id="boards"><h2>Nøglespil</h2>
{chr(10).join(board(*b) for b in B)}
</section>
<section id="toppe"><h2>I øvrigt</h2>
<ul class="prose">
{suits(TOPPE)}
</ul></section>
<section id="stilling"><h2>Stilling</h2>
<p class="lbl">Samlet efter tre af fire sektioner</p>
<div class="tw"><table><thead><tr><th class="num">Plac.</th><th>Par</th><th class="num">1. sektion</th><th class="num">2. sektion</th><th class="num">3. sektion</th><th class="num">Samlet %</th></tr></thead><tbody>{tot}</tbody></table></div>
<p class="note">{TOTNOTE}</p>
<p class="lbl" style="margin-top:2rem">3. sektion, 16. november</p>
<div class="tw"><table><thead><tr><th class="num">Plac.</th><th>Par</th><th class="num">%</th><th class="num">Forventet %</th><th class="num">Forskel</th></tr></thead><tbody>{stand}</tbody></table></div>
<p class="note">Forventet score er beregnet af arrangøren ud fra parrets handicap. (S) er substitut.</p>
</section>
<section id="method"><details><summary><h2>Noter</h2></summary>
<ul class="prose">
<li>På nøglespillene viser tallet øverst til højre topscoren på spillet, for N-S eller Ø-V som angivet. Den lille tabel under diagrammet giver antal stik med åbne kort for hver linje; to tal (f.eks. 11/10) betyder, at det afhænger af, om Nord eller Syd er spilfører.</li>
<li>Fremhævede rækker i resultattabellerne er de borde, teksten omtaler.</li>
<li>De to rækker spillede de samme kort. "Ren top" er 100 % på spillet.</li>
<li>Den samlede stilling er resultatsidens "fleksible stilling": gennemsnittet af de sektioner, parret har spillet. Regnestykkerne for sidste sektion forudsætter, at turneringen afgøres på samme måde, også for par med færre sektioner; det fremgår ikke af resultatsiden.</li>
<li>Resultater, kortfordelinger og tabeller over stik med åbne kort kommer fra <a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1">Danmarks Bridgeforbunds resultatside</a>. Analyserne med åbne kort, pr. udspil og pr. spillet kort, er beregnet med Dealers medfølgende solver.</li>
{suits(EXTRA)}
<li>Der findes ingen meldeforløb og ingen spilleforløb. Vurderinger af meldingerne bygger alene på slutkontrakterne, og spilleplaner er det, kortene tillader, ikke nødvendigvis det, der skete ved bordet.</li>
<li>Navnene følger parrene, da resultatlisten ikke viser, hvem der sad på hvilken plads.</li>
{suits(LEADS)}
</ul></details>{names}
<p class="note">Danmarks Bridgeforbund: <a href="{U}resultater.php?{Q}">Resultater</a> · <a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1">Spilresultater</a> · <a href="{U}kortfordeling.php?{Q}">Kortfordeling</a> · <a href="{U}pairhacscore.php?{Q}">Handicapscore</a> · <a href="{U}fleksibel.php?{Q}">Samlet stilling</a></p>
</section>
<footer><p>De samme kort blev spillet i begge rækker: <a href="{OTHER[0]}">{OTHER[1]}</a>.</p><p>{GEN} · Søren Debois, assisteret af Claude Code (Fable 5.2)</p></footer>
</div>
</html>
'''
KEY={b[0] for b in B}
def ext(t): return re.sub(r'(?<!">)\b[Ss]pil (\d+)',lambda m:f'<a href="#b{m[1]}">{m[0]}</a>' if int(m[1]) in KEY else f'<a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1#B{m[1]}">{m[0]}</a>',t)
def sect(t,a,b,f): i=t.index(a); j=t.index(b,i); return t[:i]+f(t[i:j])+t[j:]
out=sect(out,'<section id="aften">','<section id="boards">',ext)
out=sect(out,'<section id="toppe">','<section id="stilling">',ext)
open(sys.argv[3],'w',encoding='utf-8').write(out)
for b in B:
    print(b[0],[(r['ns'],r['ew'],r['lead'],lead(b[0],r)) for r in rows(b[0]) if lead(b[0],r)=='?'], len(rows(b[0])))
