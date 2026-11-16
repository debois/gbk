import json,re,sys,html
boards=json.load(open(sys.argv[1])); ref=open(sys.argv[2],encoding='utf-8').read()
css=ref[ref.index('<style>'):ref.index('</style>')+8]
font=re.search(r'<link rel="stylesheet"[^>]*>',ref)[0]
Q='filename=2132/MT493GT1448.XML&amp;tournament=493&amp;section=3'
U='https://resultater.bridge.dk/template/'
P={1:'Dyrekilde–Neis',2:'Nielsen–Jarnit',3:'Balslev–Henrichsen',4:'Schaltz–Stenbjerre',5:'Loft–Harder',6:'Mikkelsen–Jakobsen',7:'Øgaard–Egstrup',8:'Kjeldsen–Jørgensen',9:'Junker Lauritzen–Bay Schmith',10:'Martens–Martens'}
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
ROW='A-rækken'; OTHER=('2026-11-16-eftermiddag-b.html','B-rækkens rapport','B-rækken','filename=2132/MT493GT1449.XML&amp;tournament=493&amp;section=3',{24,21,15,3,7,2})
B=[
(24,'28 HP og ét par i udgang','+420','Top N-S',{3},[
 'N-S har 28 HP, og Syd har seks gående klør. 6♣ har 12 stik på ethvert udspil: seks klør, to spar, ruder es-konge og de små ruder hos Nord, som rejses med en trumfning, når farven sidder 3-2. Sidder ruderne 4-1, er der hjerterknibningen at falde tilbage på. Slemmen står, når blot én af delene lykkes, godt 80 %.',
 '6UT har også 12 stik, men kun fordi hjerter dame sidder hos Øst. Sidder den hos Vest, er der 10–11.',
 '<b>Balslev–Henrichsen</b> var det eneste par i udgang og fik 420 og ren top for 5♣ med 12 stik. Ved de fire andre borde blev der spillet delkontrakt i klør eller ruder. I B-rækken nåede to af seks par udgang, i 3UT og 5♣. Ingen meldte slemmen.']),
(1,'Lilleslem med 22 HP','980','Top Ø-V',{2,7},[
 'Øst har 18 HP og 5-5 i major, Vest fire små hjerter og 4 HP. Med åbne kort er der 12 stik i hjerter på ethvert udspil. Nøglen er sparfarven: Nord har K-D-7, som falder på tre runder, så Østs lange spar bliver stik. Bytter man spar konge over til Syd, er der kun 11.',
 '<b>Nielsen–Jarnit</b> var alene om at melde 6♥, fik klør 9 ud og tog 12 stik: 980 og ren top. Mikkelsen–Jakobsen fik også 12 stik, i 4♥. I B-rækken blev slemmen ikke meldt.',
 '<b>Øgaard–Egstrup</b> fik toppen den anden vej. Nord spillede 4♦ og gik to ned uden for zonen: 100, langt billigere end Ø-V\'s udgang.']),
(26,suits('6♦ og trumfudspillet'),'+630','Top N-S',{2,3,4},[
 'N-S har 25 HP og ni ruder. Med åbne kort har 6♦ 12 stik, også efter trumf ud: spar es, to spartrumfninger hos Syd, klør es-konge med afkast af Nords hjerter, to klørtrumfninger hos Nord, og når trumferne er trukket, afgives en spar til Østs konge. Nords femte spar er det tolvte stik, fordi farven sidder 4-3.',
 '<b>Nielsen–Jarnit</b> meldte også denne slem, som det eneste par i de to rækker. <b>Loft–Harder</b> spillede trumf ud, det udspil, der tager en trumfning fra bordet, og kontrakten gik én ned. Det gav Ø-V 75 %.',
 'Toppen gik til 3UT. Ti stik giver 630, og 5♦ med overstik kun 620, så i parturnering skal ruderkontrakten helt op i slem for at betale sig. <b>Schaltz–Stenbjerre</b> og <b>Balslev–Henrichsen</b> delte toppen.']),
(23,'Det tolvte stik i 3UT','+690','Top N-S',{2,1,5},[
 'N-S har 29 HP, men ingen otte-korts fit. I sans er der 11 stik: fire spar, fire hjerter, fordi damen sidder single hos Øst og Vests 10 kan knibes, ruder es og dame med knibning, og klør es.',
 'Det tolvte stik er en skvis. Øst holder alene ruderne og klør konge, og når majorstikkene bliver taget, kan Øst ikke beholde begge hold. Men skvisen virker kun, hvis spilfører først har afgivet et stik. Efter klør 10 ud, dækket med damen hos Vest, skal Nord derfor lade damen holde stikket. Tager Nord esset med det samme, er der kun 11 stik. Udspil af klør konge holder også spilfører på 11.',
 '<b>Nielsen–Jarnit</b> fik netop klør 10 ud og tog 12 stik: 690 og ren top. I B-rækken spillede alle seks borde 3UT, ét af dem med 12 stik.',
 '<b>Dyrekilde–Neis</b> gik efter slemmen og endte i 6♥ på en 4-3-fit. Set fra N-S-hænderne alene står den slem med åbne kort på 34 % af de mulige fordelinger hos Ø-V: 54 %, når ruder konge sidder til knib, og 13 %, når den ikke gør. Her sad kongen til knib, men trumferne 5-1, og det blev 11 stik. Loft–Harder stoppede i 5UT, også med 11 stik.']),
(2,'Spar mod klør','+620','Top N-S',{7,6},[
 'N-S har ti spar og 22 HP, Ø-V 11 klør og 18 HP. Med åbne kort har begge sider ti stik i deres farve: 4♠ står, og 5♣ går én ned. Det bedste, Ø-V kan gøre, er at ofre i 5♣ doblet for 100.',
 '<b>Øgaard–Egstrup</b> var det eneste N-S-par, der fik lov at spille 4♠: 620 og ren top. Ved de fire andre borde spillede Ø-V klør på fem- eller sekstrinnet. Selv 6♣ doblet to ned kostede kun 300, under det halve af udgangen.',
 '<b>Mikkelsen–Jakobsen</b> blev doblet i 5♣ med Øst som spilfører og vandt kontrakten: 550 og top til Ø-V. Spar es kom ud. Vest er renonce og trumfer, og Østs spar konge er dermed blevet til et stik. Uden et sparudspil er der kun ti. I B-rækken blev 4♠ vundet ved to borde, og også dér gik en doblet 5♣ hjem.']),
(18,suits('Alle i 4♠'),'+680','Top N-S',{9,3,10},[
 'N-S har 27 HP og ni spar, og med åbne kort er der 12 stik på ethvert udspil. Alligevel spillede alle 11 borde i de to rækker 4♠. Slemmen afhænger af ruder es: den sidder hos Øst foran Syds konge, så kongen bliver stik, og Nord kan trumfe to ruder. Sidder esset hos Vest, er der kun 11 stik uden ruder ud. Det er en slem på 50 %, som man ikke taber meget ved at lade ligge.',
 'Kampen stod derfor om overstikket. <b>Junker Lauritzen–Bay Schmith</b>, <b>Balslev–Henrichsen</b> og <b>Martens–Martens</b> tog alle 12 stik og fik 75 % hver.']),
]
ST=[(5,'Jep Loft – Peter Harder',63.3,52.2),(7,'Lars Øgaard – Christina Egstrup (S)',63.0,52.6),(4,'Bente Schaltz – Kirsten Stenbjerre',60.2,48.1),(2,'Maj-Britt Nielsen (S) – Inger Jarnit',52.3,55.4),(6,'Henning V. Mikkelsen – Paula Jakobsen',50.6,51.3),(1,'Birgitte Dyrekilde – Ronny Neis',49.1,51.6),(9,'Peter Junker Lauritzen – Bente Bay Schmith',44.9,48.3),(3,'Kim Balslev – Anders Henrichsen',43.9,49.3),(10,'Ingelise Martens – Poul Martens',40.9,45.0),(8,'Grethe Kjeldsen – Birgit Jørgensen',32.7,46.3)]
TOT=[('Lars Øgaard – Michael Knie-Andersen',(67.4,44.4,63.0),'58,26'),('Jette Fabrin – Helle Lange',(53.2,59.7,None),'56,48'),('Jep Loft – Peter Harder',(54.3,42.6,63.3),'53,38'),('Bente Schaltz – Kirsten Stenbjerre',(50.2,45.8,60.2),'52,08'),('Kim Nørgaard Nielsen – Inger Jarnit',(55.3,47.2,52.3),'51,62'),('Birgitte Dyrekilde – Ronny Neis',(41.3,64.4,49.1),'51,58'),('Henning V. Mikkelsen – Paula Jakobsen',(46.2,54.6,50.6),'50,48'),('Peter Junker Lauritzen – Bente Bay Schmith',(54.4,44.9,44.9),'48,07'),('Kim Balslev – Anders Henrichsen',(42.9,54.6,43.9),'47,15'),('Ingelise Martens – Poul Martens',(34.7,41.7,40.9),'39,09')]
TOTNOTE='Sektionsresultaterne tæller for turneringsparret, også når der er spillet med substitut. Fabrin–Lange spillede ikke 3. sektion. Kjeldsen–Jørgensen fra B-rækken spillede med i A-rækken denne mandag og indgår ikke i A-rækkens samlede stilling.'
CARDS=[('Fører samlet','Lars Øgaard – Michael Knie-Andersen','58,3','%','81 spil · 63,0 % i 3. sektion'),('Nr. 2 samlet','Jette Fabrin – Helle Lange','56,5','%','54 spil · spillede ikke 3. sektion'),('Dagens største handicapgevinst','Bente Schaltz – Kirsten Stenbjerre','−0,86','handicap','60,2 % · forventet 48,1 %')]
SRC='10 par, Howell, 27 spil, top 8 pr. spil.'
LEDE='Øgaard–Knie-Andersen fører Novemberpar med 58,3 % før sidste sektion, 1,8 procentpoint foran Fabrin–Lange. Loft–Harder var bedst på dagen med 63,3 % og er nu nummer tre.'
AFTEN='''<p class="prose"><b>Lars Øgaard – Michael Knie-Andersen</b> fører Novemberpar med 58,3 % efter tre af fire sektioner. Øgaard spillede denne mandag med Christina Egstrup som substitut, og de scorede 63,0 %, bl.a. med rene toppe i <a href="#b2">spil 2</a> og spil 14. <b>Jette Fabrin – Helle Lange</b> førte efter to sektioner og er nu nummer to med 56,5 %. De spillede ikke i dag og står med 54 spil mod de øvriges 81.</p>
<p class="prose">Dagens bedste var <b>Jep Loft – Peter Harder</b> med 63,3 %, 0,7 matchpoint foran Øgaard–Egstrup. De tog fem rene toppe som N-S i spil 3, 5, 6, 8 og 9 og spillede trumf ud mod lilleslemmen i <a href="#b26">spil 26</a>. Det løftede dem fra ottende- til tredjepladsen samlet. <b>Bente Schaltz – Kirsten Stenbjerre</b> scorede 60,2 % mod forventet 48,1 %, dagens største handicapgevinst (−0,86), og gik fra niende- til fjerdepladsen. <b>Maj-Britt Nielsen – Inger Jarnit</b> meldte to lilleslemmer, i <a href="#b1">spil 1</a> og <a href="#b26">spil 26</a>, og tog det tolvte stik i <a href="#b23">spil 23</a>.</p>
<p class="prose">Sidste sektion spilles mandag 23. november. Øgaard–Knie-Andersen har udspillet: Loft–Harder skal score knap 15 procentpoint mere end dem for at gå forbi, Schaltz–Stenbjerre godt 18. Den nærmeste udfordrer er Fabrin–Lange, som har 53,2 % og 59,7 % i deres to sektioner. Scorer førerparret 50 % i sidste sektion, skal Fabrin–Lange bruge knap 56 % for at vinde; scorer førerparret 55 %, skal de bruge godt 59 %. Bag dem er tredjepladsen åben: Loft–Harder, Schaltz–Stenbjerre, Nørgaard Nielsen–Jarnit og Dyrekilde–Neis ligger inden for to procentpoint.</p>'''
TOPPE='''<li><b>Bente Schaltz – Kirsten Stenbjerre</b> fik ren top for fire gange pas i spil 4: alle andre N-S-par gik minus på spillet.</li>
<li><b>Henning V. Mikkelsen – Paula Jakobsen</b> spillede 3UT i spil 11 og tog 12 stik: 490 og ren top, ti point mere end 4♥ med 12 stik.</li>
<li><b>Peter Junker Lauritzen – Bente Bay Schmith</b> var det eneste par i 3UT i spil 21 (600, ren top) og det eneste Ø-V-par, der vandt udgang i spil 5 (4♥, 420).</li>
<li><b>Ingelise Martens – Poul Martens</b> tog to rene toppe i delkontrakt: 2♣ med ti stik i spil 15 (130), hvor tre borde gik ned i 4♥, og 2♠ i spil 16 (110), hvor to borde gik ned i 4♠.</li>
<li><b>Birgitte Dyrekilde – Ronny Neis</b> vandt 3♦ i spil 20 (110, ren top) og fik 11 stik i 4♥ i spil 19 (450).</li>
<li><b>Grethe Kjeldsen – Birgit Jørgensen</b>, der fører B-rækken, satte 3UT to gange i spil 12 (ren top) og 4♥ to gange i spil 10 og vandt 4♠ i spil 17.</li>
<li><b>Kim Balslev – Anders Henrichsen</b> fik ti stik i 3UT i spil 9: 630 og ren top til Ø-V.</li>
<li><b>Lars Øgaard – Christina Egstrup</b> tog 12 stik i 4♠ i spil 14 (480) og satte 4♠ i spil 17, som blev vundet ved to andre borde.</li>'''
EXTRA='''<li>Spil 24: chancen for 6♣ er regnet som ruderne 3-2 (68 %) eller hjerter dame hos Øst. Spil 18: chancen for 6♠ er regnet som ruder es hos Øst.</li>
<li>Spil 1, 18, 24 og 26 er kontrolleret ved at flytte nøglekortet til den anden hånd og regne igen. Skvisen i spil 23 og spilleplanen i spil 26 er fulgt kort for kort.</li>
<li>Spil 23: chancen for 6♥ er fundet ved at dele Ø-V's kort tilfældigt 1.641 gange og regne hver fordeling med åbne kort. Tallet er en øvre grænse, for med åbne kort finder spilfører altid trumf dame.</li>'''
LEADS='<li>Et spørgsmålstegn i udspilskolonnen betyder, at det noterede udspil ikke findes på udspillerens hånd. I spil 1 er ruder es noteret mod 4♥ spillet af Vest, men esset sidder hos Syd; det passer med Øst som spilfører. I spil 24 er spar 7 noteret mod 4♣ spillet af Syd og spar 4 mod 3♦ spillet af Nord; begge kort sidder hos den anden modspiller, så spilføreren kan være noteret på den forkerte plads.</li>'
GEN='16. november 2026'; NAMES='Nielsen i resultattabellerne er Maj-Britt Nielsen, substitut for Kim Nørgaard Nielsen. Øgaard–Egstrup er turneringsparret Øgaard–Knie-Andersen med Christina Egstrup som substitut. Henrichsen er Anders Henrichsen.'
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
