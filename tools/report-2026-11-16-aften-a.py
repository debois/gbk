import json,re,sys,html
boards=json.load(open(sys.argv[1])); ref=open(sys.argv[2],encoding='utf-8').read()
css=ref[ref.index('<style>'):ref.index('</style>')+8]
font=re.search(r'<link rel="stylesheet"[^>]*>',ref)[0]
Q='filename=2132/MT496GT1451.XML&amp;tournament=496&amp;section=1'
U='https://resultater.bridge.dk/template/'
P={1:"Boysen–Krogh",2:"Christensen–Husted",3:"Serritzlew–Eckstrøm",4:"Ipsen–Ingolfsson",5:"Henrichsen–Kofoed",6:"Debois–Dyrekilde",7:"Nord Jørgensen–Suh Nicolaisen",8:"Bruun Rasmussen–Dyrekilde Sommerlund",9:"Koks Andreassen–Øxseth",10:"Egstrup–Veibel Petersen",11:"Neergaard–Lykke Hansen",12:"Fardan–Nodal",13:"Rosenbaum–Vainer",14:"Nielsen–Brix"}
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
OTHER=None
B=[
(2,'13 stik i kortene, én lilleslem','920','Top Ø-V',{2,11},[
 'Ø-V har 30 HP. Øst har seks spar med E-K-D, og Vest lægger bonden og tre esser til. Med åbne kort er der 13 stik i sans, spar og ruder på ethvert udspil: seks spar, fordi Nords 10 falder i fjerde runde, fire ruder, fordi Syd har D-B alene, hjerter es og klør es-konge.',
 'Skal man være i slem? Ser man kun Ø-V\'s kort og fordeler N-S\'s kort tilfældigt 3000 gange, står 6♦ i 95 % af tilfældene, 6♠ i 91 % og 6UT i 70 %. Lilleslem i spar eller ruder skal altså meldes. Storeslemmen skal man lade ligge: 7♠ står i 49 %, 7♦ i 17 % og 7UT i 15 %, og når kun to par af syv melder lilleslem, er der intet at vinde ved at gå videre.',
 '<b>Christensen–Husted</b> var det eneste par, der meldte og vandt en slem: 6♦ med 12 stik gav 920 og ren top. Ved et andet bord gik 6UT én ned, så <b>Neergaard–Lykke Hansen</b> fik toppen den anden vej. De fem øvrige borde spillede udgang, tre af dem med 13 stik.']),
(5,'30 HP uden fit','460','Top Ø-V',{2,10,14},[
 'Ø-V har igen 30 HP, og fire par gik i slem, i fire forskellige kontrakter: 6UT, 6♣, 6♥ og 6♦. Ingen af dem gik hjem. Hænderne passer dårligt sammen: Øst er renonce i Vests femkortsfarve i klør, og der er ingen otte-korts fit. Med åbne kort er der 12 stik i hjerter på en 4-3-fit og i ruder på en 5-2-fit, men kun 11 i klør og 11 i sans, når klør ikke kommer ud.',
 'Som kortene sidder, kan 6♥ vindes ved bordet. Efter spar ud: spar es, ruder konge og es, en ruder trumfet lavt, og tre gange trumf med hjerter konge til sidst. Øst tager sine to rejste ruder, og Vest kommer ind på spar konge med E-D-10 i klør tilbage. Nord har nu kun klør. Knibningen kan ikke tages, for Øst har ingen klør, så Vest spiller klør 10, og Nord må stikke og spille klør tilbage til es-dame. I 6♦ tager Øst ruder konge og es og spiller en tredje trumf, så dame og bonde falder i samme stik. Hjerterne giver fire stik, og klør 10 og dame spilles gennem Nord og trumfes, når Nord dækker, så otteren bliver det tolvte stik.',
 'Gode slemmer er det ikke. Begge planer kræver, at hjerter og ruder sidder 3-3, hvilket sker i 13 % af tilfældene, og desuden at Nord har klørhonnørerne. Samlet er det under 7 %. Feltet, der blev i udgang, gjorde ret.',
 '<b>Christensen–Husted</b> blev i 3UT og tog 11 stik: 460 og ren top til Ø-V. <b>Egstrup–Veibel Petersen</b> fik toppen den anden vej med 200 mod 6UT, og <b>Nielsen–Brix</b> fik 150 mod 6♣.']),
(6,'Slemmen, ingen meldte','+480','Bedste N-S',set(),[
 'N-S har 27 HP og ni spar, og Syd har alle fire esser. 6♠ har 12 stik på ethvert udspil, og slemmen afhænger ikke af trumfknibningen: sidder spar konge bag esset, afgives den, og der er stadig 12 stik. Nord kaster to klør på hjerter es-konge, og Syd trumfer sin tredje klør på bordet.',
 'Alle syv borde spillede 4♠. Seks af dem tog 12 stik og delte 58,3 %. I spil 20 var der også 12 stik og ingen i slem, men dér skal klør konge sidde rigtigt.']),
(11,suits('To par i 6♥'),'+980','Top N-S',{2,6,13,3,12},[
 'N-S har 28 HP og ni hjerter, og Ø-V kan kun tage spar es. Der er 12 stik i både hjerter og klør på ethvert udspil.',
 '<b>Christensen–Husted</b> og <b>Debois–Dyrekilde</b> meldte slemmen og delte toppen med 980. <b>Rosenbaum–Vainer</b> spillede 4♥ og fik klør ud i stedet for spar: 13 stik og 510.',
 'Øst har syv spar og god grund til at melde videre. Med åbne kort går 4♠ doblet to ned for 300, billigere end N-S\'s udgang. <b>Serritzlew–Eckstrøm</b> og <b>Fardan–Nodal</b> fik lov at spille den og scorede 91,7 % som Ø-V. Mod en meldt slem kan Ø-V gå helt til 6♠: fire doblede beter koster 800.']),
(19,'Spar ud mod 6UT','+990','Top N-S',{13,12},[
 'N-S har 30 HP og 11 stik: fem klør, tre hjerter, spar es og to ruder, når esset er drevet ud. Spar konge og ruder es sidder begge hos Øst, og det tolvte stik findes ved at udnytte netop det.',
 'Nøglen er ruder 10 fra Nord. Lægger Øst lavt, vinder tieren, og ruderne giver tre stik. Dækker Øst med bonden, eller tager Øst esset, er der kun to ruderstik, men nu holder Øst alene både ruderne og spar konge. Spilfører tager spar es og spiller Nords klør til ende. På den sidste klør må Øst kaste spar konge eller sit ruderhold, og Syd kaster efter Øst. Spiller man i stedet en lille ruder til kongen, lægger Øst lavt og beholder E-B bag Syds små ruder, og så er der kun 11 stik.',
 'Spar ud ødelægger planen. Stikker Nord med esset, kan Øst tage spar konge, når Øst kommer ind på ruder es. Lægger Nord lavt, tager Øst kongen med det samme. Med Nord som spilfører har Øst udspillet og kan ikke spille spar uden at give Syd stik for damen, så dér står 6UT på ethvert udspil. Med Syd som spilfører står den kun, hvis Vest ikke spiller spar ud.',
 'Begge slemmer blev spillet af Syd. <b>Rosenbaum–Vainer</b> fik ruder 8 ud og tog 12 stik: 990 og ren top. Ved det andet bord spillede <b>Henrichsen–Kofoed</b> spar 3 ud, og kontrakten gik én ned. De fem andre borde stoppede under slem og tog 10 eller 11 stik.']),
(13,'Doblet spar mod udgang','+1100','Top N-S',{7,12,11},[
 'Vest har 5-5 i spar og klør og finder fire spar hos Øst, men Nord sidder med E-D-B-6 bag Vest, og Syd er renonce. Med åbne kort får Vest seks stik i spar. N-S har 25 HP og udgang: 3UT og 4♥ har ti stik.',
 'Regnestykket i parturnering: N-S\'s udgang i zonen giver 630, så en doblet sparkontrakt skal tre ned for at betale mere. <b>Fardan–Nodal</b> doblede 3♠ og fik netop de tre beter, 800. <b>Nord Jørgensen–Suh Nicolaisen</b> doblede 4♠ og fik 1100 og ren top.',
 '<b>Neergaard–Lykke Hansen</b> var det eneste par, der meldte og vandt udgangen: 3UT med ti stik, 630 og 66,7 %. 2♠ doblet gik én ned, og de 200 gav 33,3 %.']),
]
ST=[(2,'Claus Torben Christensen – Camilla Husted',65.8,53.3),(13,'Eva Rosenbaum – Gert Vainer',62.5,55.3),(7,'Johannes Nord Jørgensen – Lene Suh Nicolaisen',57.2,50.2),(9,'Ulrik Koks Andreassen – Bente Øxseth',53.3,49.2),(6,'Søren Debois – Birgitte Dyrekilde',53.0,49.1),(10,'Christina Egstrup – Bo Veibel Petersen',50.3,49.4),(5,'Jørgen Henrichsen – Jannik Kofoed',49.3,49.3),(3,'Anja Serritzlew – Ole Eckstrøm',49.1,50.6),(4,'Maja Ipsen – Jon Ingolfsson',49.1,50.6),(12,'Rolf Fardan – Marianne Nodal',48.7,54.8),(14,'Bente Nielsen – Karin Brix',47.2,39.5),(8,'Christian Bruun Rasmussen – Benjamin Dyrekilde Sommerlund',39.7,46.3),(1,'Asbjørn Boysen – Peter Krogh',39.0,54.8),(11,'Kirsten Neergaard – Hans Lykke Hansen',35.9,47.7)]
MP={2:'221,2',13:'209,8'}
HAC=(14,'−0,65'); HACLBL='Næststørste handicapgevinst'
GRP=7  # indvævet Howell: par 1..GRP mødes indbyrdes, resten ligeså; None for almindelig Howell
GEN='16. november 2026'; NAMES='Dyrekilde i resultattabellerne er Birgitte Dyrekilde; Dyrekilde Sommerlund er Benjamin Dyrekilde Sommerlund.'
names=f'<p class="note">{NAMES}</p>' if NAMES else ''
dk=lambda x:f'{x:.1f}'.replace('.',',')
def diff(a,b):
    d=round(a-b,1); return f'<span class="{"pos" if d>0 else "neg" if d<0 else "zero"}">{num(0) if d==0 else ("+" if d>0 else "−")+dk(abs(d))}</span>'
grp=lambda k:f'par 1–{GRP}' if k<=GRP else f'par {GRP+1}–{len(ST)}'
GW={} if not GRP else {next(s for s in ST if (s[0]<=GRP)==a)[0] for a in (True,False)}
cards=''.join(f'<div class="match"><p class="eyebrow">{i+1}. plads{" · bedst blandt "+grp(k) if k in GW else ""}</p><p class="vs">{n}</p><p class="score"><b>{dk(p)}</b> <span>%</span></p><p class="vp">{MP[k]} MP · forventet {dk(e)} %</p></div>' for i,(k,n,p,e) in enumerate(ST[:2]))
cards+=''.join(f'<div class="match"><p class="eyebrow">{HACLBL}</p><p class="vs">{n}</p><p class="score"><b>{HAC[1]}</b> <span>handicap</span></p><p class="vp">{dk(p)} % · forventet {dk(e)} %</p></div>' for k,n,p,e in ST if k==HAC[0])
stand=''.join(f'<tr><td class="num">{i+1}</td><td class="num">{k}</td><td>{n}</td><td class="num">{dk(p)}</td><td class="num">{dk(e)}</td><td class="num">{diff(p,e)}</td></tr>' for i,(k,n,p,e) in enumerate(ST))
AFTEN='''<p class="prose"><b>Claus Torben Christensen – Camilla Husted</b> vandt med 65,8 %, 11,4 matchpoint foran nummer to. De tog syv rene toppe, og i halvdelen af aftenens 28 spil fik de mindst 83 %. De var alene om at melde og vinde slem i spil 2, meldte 6♥ i spil 11 og blev i 3UT i spil 5, hvor fire slemmer gik ned. De havde også feltets største handicapgevinst (−1,05).</p>
<p class="prose"><b>Eva Rosenbaum – Gert Vainer</b> blev nummer to med 62,5 %. De meldte og vandt 6UT i spil 19 og satte 3UT tre gange i både spil 15 og spil 24. <b>Johannes Nord Jørgensen – Lene Suh Nicolaisen</b> tog tredjepladsen med 57,2 % og tre rene toppe: 1100 i spil 13, 3UT i spil 4, som gik ned ved fire andre borde, og 3UT med 13 stik i spil 20.</p>
<p class="prose">Det var slemmernes aften. I seks spil, 2, 5, 6, 11, 19 og 20, havde den ene side 12 eller 13 stik med åbne kort. På de seks spil blev der meldt ti slemmer, og fire gik hjem. <b>Bente Nielsen – Karin Brix</b> scorede 47,2 % mod forventet 39,5 % og fik den næststørste handicapgevinst (−0,65), bl.a. med 150 mod 6♣ i spil 5.</p>'''
TOPPE='''<li><b>Ulrik Koks Andreassen – Bente Øxseth</b> tog to rene toppe i træk: de var eneste par i udgang i spil 27 (4♠ med 11 stik, 450) og satte som de eneste 4♠ i spil 28.</li>
<li><b>Jørgen Henrichsen – Jannik Kofoed</b> meldte og vandt 4♠ i spil 22: 420 og ren top. Ingen andre fik ti stik i spar.</li>
<li><b>Anja Serritzlew – Ole Eckstrøm</b> var eneste par, der vandt udgang i spil 23 (3UT med ti stik, 630), og vandt 1UT i spil 3 (120): to rene toppe.</li>
<li><b>Maja Ipsen – Jon Ingolfsson</b> tog ni stik i 1UT i spil 16 (150, ren top) og satte 4♠ to gange i både spil 22 og spil 24.</li>
<li><b>Asbjørn Boysen – Peter Krogh</b> satte som de eneste 4♠ i spil 7, hvor fire borde vandt udgangen, og satte 3UT i spil 23: to rene toppe.</li>
<li><b>Christina Egstrup – Bo Veibel Petersen</b> fik foruden spil 5 rene toppe i spil 8 (2♠ tre ned, 150) og spil 26, hvor de holdt 1♥ på syv stik.</li>
<li><b>Christian Bruun Rasmussen – Benjamin Dyrekilde Sommerlund</b> satte 3UT tre gange i spil 15 (300, 91,7 %) og 3♦ to gange i spil 25 (200, 83,3 %).</li>
<li><b>Kirsten Neergaard – Hans Lykke Hansen</b> satte 4♥ i spil 1 og vandt 1UT i spil 21, begge til 91,7 %.</li>
<li><b>Bente Nielsen – Karin Brix</b> satte 4♠ i spil 10 og tog ni stik i 2♥ i spil 3, begge til 91,7 %.</li>'''
LEADS='<li>Et spørgsmålstegn i udspilskolonnen betyder, at det noterede udspil ikke findes på udspillerens hånd. I spil 2 er klør 4 noteret mod 4♠ spillet af Øst og ruder 6 mod 6♦ spillet af Vest, og i spil 13 klør 6 mod 5♥ spillet af Syd; alle tre kort sidder hos spilfører selv.</li>'
gwin='' if not GRP else '<p class="prose">Turneringen blev spillet som indvævet Howell: par 1–7 mødte hinanden indbyrdes, par 8–14 ligeså, og hvert par spillede én runde mod et par fra den anden gruppe. Scorerne er regnet over hele feltet.</p><p class="prose">'+' '.join(f'Bedst blandt {grp(k)}: <b>{n}</b>, {dk(p)} %.' for k,n,p,e in ST if k in GW)+'</p>'
out=f'''<!doctype html>
<html lang="da">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gentofte Bridgeklub, Mandag aften, 16. november</title>
<meta name="claude:viewport-fit-sides" content="cover">
{font}
{css}
<div class="wrap">
<header class="top">
<p class="eyebrow">Gentofte Bridgeklub · A-rækken · Parturnering #496 · Mandag 16. november 2026</p>
<h1>Mandag aften, 16. november</h1>
<p class="lede">Christensen–Husted vandt med 65,8 % og syv rene toppe. Kortene bød på slem i seks spil; ti blev meldt, og fire gik hjem.</p>
<div class="matches">{cards}</div>
<p class="src">14 par, indvævet Howell, 28 spil, top 12 pr. spil.</p>
<nav><a href="#aften">Aftenen kort</a><a href="#boards">Nøglespil</a><a href="#toppe">I øvrigt</a><a href="#stilling">Slutstilling</a><a href="#method">Noter</a></nav>
</header>
<section id="aften"><h2>Aftenen kort</h2>
{suits(AFTEN)}
</section>
<section id="boards"><h2>Nøglespil</h2>
{chr(10).join(board(*b) for b in B)}
</section>
<section id="toppe"><h2>I øvrigt</h2>
<ul class="prose">
{suits(TOPPE)}
</ul></section>
<section id="stilling"><h2>Slutstilling</h2>
{gwin}
<div class="tw"><table><thead><tr><th class="num">Plac.</th><th class="num">Nr.</th><th>Par</th><th class="num">%</th><th class="num">Forventet %</th><th class="num">Forskel</th></tr></thead><tbody>{stand}</tbody></table></div>
<p class="note">Forventet score er beregnet af arrangøren ud fra parrets handicap.</p>
</section>
<section id="method"><details><summary><h2>Noter</h2></summary>
<ul class="prose">
<li>På nøglespillene viser tallet øverst til højre topscoren på spillet, for N-S eller Ø-V som angivet. Den lille tabel under diagrammet giver antal stik med åbne kort for hver linje; to tal (f.eks. 12/11) betyder, at det afhænger af, om Nord eller Syd er spilfører.</li>
<li>Fremhævede rækker i resultattabellerne er de borde, teksten omtaler. "Ren top" er 100 % på spillet.</li>
<li>Kortet øverst viser den næststørste handicapgevinst, fordi den største gik til vinderne.</li>
<li>Resultater, kortfordelinger og tabeller over stik med åbne kort kommer fra <a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1">Danmarks Bridgeforbunds resultatside</a>. Udspilsanalyserne med åbne kort er beregnet med Dealers medfølgende solver.</li>
<li>Spil 6 er kontrolleret ved at flytte spar konge til Vest og regne igen: stadig 12 stik. I spil 20 giver klør konge hos Vest højst 11 stik i spar og klør, når der ikke kommer trumf ud. </li>
<li>Procenterne i spil 2 er antal stik med åbne kort over 3000 tilfældige fordelinger af N-S's kort. Det er lidt gunstigere end ved bordet, hvor spilfører ikke kan se, hvordan farverne sidder. I spil 5 er det meget gunstigere: med åbne kort står 6♥ i 60 % af 1500 tilfældige fordelinger, men kun fordi spilfører kan vælge plan efter kortenes placering. Tallene i teksten gælder derfor de to beskrevne planer. Spilleplanerne i spil 5 og 19 er fulgt kort for kort med solveren mod bedste modspil.</li>
<li>Resultatsiden har ingen meldeforløb og ingen spilleforløb. Vurderinger af meldingerne bygger alene på slutkontrakterne.</li>
<li>Navnene følger parrene, da resultatlisten ikke viser, hvem der sad på hvilken plads.</li>
{suits(LEADS)}
</ul></details>{names}
<p class="note">Danmarks Bridgeforbund: <a href="{U}resultater.php?{Q}">Resultater</a> · <a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1">Spilresultater</a> · <a href="{U}kortfordeling.php?{Q}">Kortfordeling</a> · <a href="{U}pairhacscore.php?{Q}">Handicapscore</a></p>
</section>
<footer><p>{GEN} · Søren Debois, assisteret af Claude Code (Fable 5.2)</p></footer>
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
