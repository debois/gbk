import json,re,sys,html
boards=json.load(open(sys.argv[1])); ref=open(sys.argv[2],encoding='utf-8').read()
css=ref[ref.index('<style>'):ref.index('</style>')+8]
font=re.search(r'<link rel="stylesheet"[^>]*>',ref)[0]
Q='filename=2132/MT495GT1450.XML&amp;tournament=495&amp;section=1'
U='https://resultater.bridge.dk/template/'
P={1:'Fogel–Guttermann',2:'Rosenbaum–Vainer',3:'Ipsen–Ingolfsson',4:'Nord Jørgensen–Suh Nicolaisen',5:'Henrichsen–Kofoed',6:'Fardan–Nodal',7:'Dyrekilde–Zeeberg',8:'Egstrup–Veibel Petersen',9:'Koks Andreassen–Øxseth',10:'Lind–Skjøt',11:'Rasmussen–Monberg Aastrup',12:'Lind Jensen–Grossman',13:'Bruun–Klausen',14:'Bruun Rasmussen–Debois',15:'Larsen–Haugaard Jensen'}
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
(30,'Storeslem i sidste spil','+1520','Top N-S',{1,5},[
 'Syd har 23 HP og en semi-gående sekskortsfarve, og Nord lægger to esser til. Der er 13 stik fra toppen i både spar og sans: seks spar, to hjerter, ruder es og klørfarven, hvor bonden falder i anden runde. Intet udspil generer.',
 'Kun to par nåede hele vejen: <b>Henrichsen–Kofoed</b> og <b>Fogel–Guttermann</b>. Ved Fogel–Guttermanns bord åbnede Guttermann med 2♣, og Fogel svarede 2UT, som viser fire kontroller. Guttermann har selv tre af de fire konger, så fire kontroller hos makker måtte være to esser, og han meldte 7UT direkte. Lilleslem gav kun middel eller lidt over: Rosenbaum–Vainers 6UT med overstik (1020) slog 6♠ med 12 stik (980).'],('Meldeforløb, Fogel–Guttermann N-S',['pas','2♣','pas',('2UT','4 kontroller'),'pas','7UT','pas','pas','pas'])),
(13,'Udspillet afgør slemmen','+1430','Top N-S',{4,2},[
 'N-S har 29 HP og otte spar, men to tabere i 6♠: hjerter es og et klørstik. Med åbne kort holder kun et klørudspil fra toppen kontrakten på 11 stik. Alt andet giver 12, fordi klørtaberen forsvinder på hjerterne.',
 'Øst sidder med otte klør til K-D-B og hjerter es. Ved fem af seks borde i spar blev hjerter es spillet ud, og spilfører fik 12 stik. <b>Nord Jørgensen–Suh Nicolaisen</b> var de eneste, der meldte slemmen, og blev belønnet med netop det udspil.',
 '<b>Rosenbaum–Vainer</b> fandt som de eneste klørudspillet og fik en ren top for at holde 5♠ på 11 stik. Var det udspil kommet mod 6♠, var toppen blevet til en bund.',
 'Ved Bruun Rasmussen–Debois\' bord ofrede Øst i 5♣. Det koster tre doblede beter i zonen, 800, og er dyrere end udgangen. Det gav N-S 83 %.']),
(3,'Trumf ud','+200','Top N-S',{14,5},[
 'Vest spillede 4♠ ved to borde. Kontrakten har ni stik: der mangler et klørstik, et hjerterstik og to ruderstik. Med åbne kort er der kun ét udspil, der giver den tiende: en lille ruder fra Nords D-10, som lader spilfører slippe med én rudertaber.',
 '<b>Bruun Rasmussen–Debois</b> lagde ud med trumf, gav intet væk og fik kontrakten to ned til parrets bedste spil på aftenen. Ved det andet bord kom ruder 6 ud, og <b>Henrichsen–Kofoed</b> tog imod gaven: 620 og top til vinderne. Samme kontrakt, 820 points forskel på udspillet.']),
(15,'Sans i stedet for minor','+660','Top N-S',{9},[
 'N-S har ti klør og 25 HP. Der er 11 stik i sans på ethvert udspil og 11–12 i klør, hvor kun hjerter ud holder spilfører på 11. I parturnering er regnestykket enkelt: 3UT med to overstik giver 660, mens 5♣ med et overstik kun giver 620.',
 '<b>Koks Andreassen–Øxseth</b> var det eneste par i 3UT og fik toppen. Det var ét af flere spil, der bar dem op på tredjepladsen.',
 'Vests syvkortsfarve i spar gjorde livet surt for flere N-S-par: to stoppede i 4♣, og Rosenbaum–Vainer fik lov at spille 3♠ udoblet for kun 100, en top til Ø-V.']),
(26,'Dristig 3UT med 5-5','+630','Top N-S',{12},[
 'De fleste Syd-spillere endte i 4♥, som er håbløs: trumferne sidder 4-2, og klørene sidder 4-1. Resultaterne i 4♥ var to, tre og fire beter.',
 '<b>Lind Jensen–Grossman</b> valgte 3UT frem for majorudgangen, selv om Syd har 5-5 og en single spar, og var alene om et plus i udgang. 3UT har kun otte stik mod spar ud; ved det andet 3UT-bord kom sparen, og kontrakten gik tre ned. Her kom hjerter ud, som giver det niende stik, og spilfører hentede selv det tiende. Selv vinderparret måtte notere minus på spillet.']),
(23,'Slemmen man ikke skal melde','+800','Top N-S',{2,14},[
 'Med åbne kort står 6♦ på ethvert udspil, men kun fordi spar konge sidder til knib. Sidder kongen dækket bag esset, går slemmen én ned, og trumferne skal også opføre sig. Det er under 50 %, og med kun 25 HP er det ikke en slem, man skal være i, heller ikke i parturnering. Feltet gjorde ret i at blive i udgang.',
 'Ø-V har ti hjerter og meldte ivrigt med. <b>Rosenbaum–Vainer</b> doblede 5♥ og hentede 800, mere end nogen udgang. <b>Bruun Rasmussen–Debois</b> tog 11 stik i 4♠, det maksimale efter hjerter ud, og fik 83 % mod aftenens vindere.']),
]
ST=[(5,'Jørgen Henrichsen – Jannik Kofoed',61.3,53.3),(2,'Eva Rosenbaum – Gert Vainer',59.1,52.0),(9,'Ulrik Koks Andreassen – Bente Øxseth',56.9,47.0),(6,'Rolf Fardan – Marianne Nodal',55.4,51.9),(3,'Maja Ipsen – Jon Ingolfsson',54.0,54.1),(4,'Johannes Nord Jørgensen – Lene Suh Nicolaisen',53.5,52.9),(13,'Mikkel Bruun – Niels Kristian Klausen',52.0,47.6),(10,'Mogens Lind – Marianne Skjøt',50.4,51.3),(7,'Birgitte Dyrekilde – Lill Zeeberg',48.5,53.9),(1,'Bent Fogel – Erling Guttermann',47.5,54.1),(14,'Christian Bruun Rasmussen – Søren Debois',44.2,47.5),(8,'Christina Egstrup – Bo Veibel Petersen',43.8,47.2),(11,'Nakako Rasmussen – Ulla Monberg Aastrup',43.6,44.1),(15,'Bjarke Larsen – Birgitte Haugaard Jensen',43.4,50.6),(12,'Allan Lind Jensen – Edith Grossman',36.0,42.6)]
MP={5:'220,5',2:'212,8'}
HAC=(9,'−0,92')
GEN='15. november 2026'; NAMES='Rasmussen i resultattabellerne er Nakako Rasmussen; Bruun er Mikkel Bruun.'
names=f'<p class="note">{NAMES}</p>' if NAMES else ''
dk=lambda x:f'{x:.1f}'.replace('.',',')
def diff(a,b):
    d=round(a-b,1); return f'<span class="{"pos" if d>0 else "neg" if d<0 else "zero"}">{num(0) if d==0 else ("+" if d>0 else "−")+dk(abs(d))}</span>'
cards=''.join(f'<div class="match"><p class="eyebrow">{i+1}. plads</p><p class="vs">{n}</p><p class="score"><b>{dk(p)}</b> <span>%</span></p><p class="vp">{MP[k]} MP · forventet {dk(e)} %</p></div>' for i,(k,n,p,e) in enumerate(ST[:2]))
cards+=''.join(f'<div class="match"><p class="eyebrow">Største handicapgevinst</p><p class="vs">{n}</p><p class="score"><b>{HAC[1]}</b> <span>handicap</span></p><p class="vp">{dk(p)} % · forventet {dk(e)} %</p></div>' for k,n,p,e in ST if k==HAC[0])
stand=''.join(f'<tr><td class="num">{i+1}</td><td>{n}</td><td class="num">{dk(p)}</td><td class="num">{dk(e)}</td><td class="num">{diff(p,e)}</td></tr>' for i,(k,n,p,e) in enumerate(ST))
out=f'''<!doctype html>
<html lang="da">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Gentofte Bridgeklub, Mandag aften/åbent hus, 9. november</title>
<meta name="claude:viewport-fit-sides" content="cover">
{font}
{css}
<div class="wrap">
<header class="top">
<p class="eyebrow">Gentofte Bridgeklub · A-rækken · Parturnering #495 · Mandag 9. november 2026</p>
<h1>Mandag aften/åbent hus, 9. november</h1>
<p class="lede">Henrichsen–Kofoed vandt med 61,3 % og meldte storeslemmen i sidste spil. Koks Andreassen–Øxseth blev aftenens overraskelse på tredjepladsen, ti procentpoint over forventet.</p>
<div class="matches">{cards}</div>
<p class="src">15 par, Howell med oversidder, 30 spil, top 12 pr. spil.</p>
<nav><a href="#aften">Aftenen kort</a><a href="#boards">Nøglespil</a><a href="#toppe">I øvrigt</a><a href="#stilling">Slutstilling</a><a href="#method">Noter</a></nav>
</header>
<section id="aften"><h2>Aftenen kort</h2>
<p class="prose"><b>Jørgen Henrichsen – Jannik Kofoed</b> vandt efter en aften, hvor de både meldte storeslemmen i <a href="#b30">spil 30</a> og fik en udgang forærende i <a href="#b3">spil 3</a>. <b>Eva Rosenbaum – Gert Vainer</b> fulgte på 59,1 %, bl.a. takket være aftenens skarpeste udspil i <a href="#b13">spil 13</a> og en dobling til 800 i <a href="#b23">spil 23</a>.</p>
<p class="prose"><b>Ulrik Koks Andreassen – Bente Øxseth</b> var efter handicap sat til 47,0 %, men scorede 56,9 % og tog feltets største handicapgevinst (−0,92). Deres top i <a href="#b15">spil 15</a> er typisk for aftenen.</p>
<p class="prose">Toppene var bredt fordelt. <b>Allan Lind Jensen – Edith Grossman</b> var alene om at vinde udgang i <a href="#b26">spil 26</a>, og <b>Christian Bruun Rasmussen – Søren Debois</b> satte 4<span class="ss">♠</span> to ned med et trumfudspil i <a href="#b3">spil 3</a>.</p>
</section>
<section id="boards"><h2>Nøglespil</h2>
{chr(10).join(board(*b) for b in B)}
</section>
<section id="toppe"><h2>I øvrigt</h2>
<ul class="prose">
<li><b>Nakako Rasmussen – Ulla Monberg Aastrup</b> meldte udgangen i spil 25 (4<span class="sh">♥</span>, 83 %), som fire par missede, og satte 3<span class="ss">♠</span> i spil 20 (92 %).</li>
<li><b>Christina Egstrup – Bo Veibel Petersen</b> fik aftenens eneste hjemgående 4<span class="ss">♠</span> i spil 18, med overstik: 650 og ren top.</li>
<li><b>Mikkel Bruun – Niels Kristian Klausen</b> tog tre toppe: 2<span class="ss">♠</span> hjem som eneste plus i spar på spil 2, 3<span class="ss">♠</span> sat i spil 11, og 1UT hjem i spil 8, hvor alle andre sanskontrakter på Ø-V-linjen gik ned.</li>
<li><b>Allan Lind Jensen – Edith Grossman</b> fik foruden spil 26 også 83 % i spil 8 for 1<span class="ss">♠</span> med syv stik.</li>
</ul></section>
<section id="stilling"><h2>Slutstilling</h2>
<div class="tw"><table><thead><tr><th class="num">Plac.</th><th>Par</th><th class="num">%</th><th class="num">Forventet %</th><th class="num">Forskel</th></tr></thead><tbody>{stand}</tbody></table></div>
<p class="note">Forventet score er beregnet af arrangøren ud fra parrets handicap.</p>
</section>
<section id="method"><details><summary><h2>Noter</h2></summary>
<ul class="prose">
<li>På nøglespillene viser tallet øverst til højre den bedste N-S-score på spillet. Den lille tabel under diagrammet giver antal stik med åbne kort for hver linje; to tal (f.eks. 11/10) betyder, at det afhænger af, om Nord eller Syd er spilfører.</li>
<li>Fremhævede rækker i resultattabellerne er de borde, teksten omtaler.</li>
<li>Resultater, kortfordelinger og tabeller over stik med åbne kort kommer fra <a href="{U}spilresultater.php?{Q}&amp;round=1&amp;half=1">Danmarks Bridgeforbunds resultatside</a>. Udspilsanalyserne med åbne kort er beregnet med Dealers medfølgende solver.</li>
<li>Resultatsiden har ingen meldeforløb. Vurderinger af meldingerne bygger alene på slutkontrakterne. Meldeforløbet i spil 30 er oplyst af spillerne; modstandernes pas er underforstået.</li>
<li>Navnene følger parrene, da resultatlisten ikke viser, hvem der sad på hvilken plads.</li>
<li>Et spørgsmålstegn i udspilskolonnen betyder, at det noterede udspil ikke findes på udspillerens hånd. I spil 13 er hjerter es noteret som udspil mod 5<span class="sc">♣</span>×, men esset sidder hos spilfører selv. I spil 23 er spar es noteret mod 4<span class="sh">♥</span> spillet af Nord, men Nord har selv esset.</li>
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
