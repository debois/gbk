import sys,re,json
t=[l.strip() for l in open(sys.argv[1],encoding='utf-8') if l.strip()]
html=open(sys.argv[2],encoding='utf-8-sig').read()
deals={}
for m in re.finditer(r'ddummy\.htm\?board=(\d+)&dealer=(\w)&vul=(\w+)&[^"]*?north=([^&]*)&south=([^&]*)&east=([^&]*)&west=([^&"]*)',html):
    deals[int(m[1])]=dict(dealer=m[2],vul=m[3],N=m[4],S=m[5],E=m[6],W=m[7])
# split on 'Bridge Solver'
idx=[i for i,x in enumerate(t) if x=='Bridge Solver']
out={}
for k,i in enumerate(idx):
    # board number: search back for '-->' then the DD table between
    j=i
    while t[j]!='-->': j-=1
    dd=t[j+1:i]
    # find board no: go back to find dealer line like 'Nord/'
    b=j
    while not re.match(r'^(Nord|Syd|Øst|Vest)/$',t[b]): b-=1
    bn=int(t[b-1])
    end=idx[k+1] if k+1<len(idx) else len(t)
    seg=t[i+1:end]
    hdr=' '.join(seg[:seg.index('NS')])
    # rows: after second 'ØV' following 'Pct'
    p=seg.index('Pct')+3
    rows=seg[p:]
    # trim trailing next-board header
    res=[];cur=[]
    for x in rows:
        cur.append(x)
    out[bn]=dict(deal=deals.get(bn),dd=dd,hdr=hdr,rows=rows)
json.dump(out,open(sys.argv[3],'w'),ensure_ascii=False)
for bn in sorted(out):
    o=out[bn]; print('#',bn,o['deal']); print(' DD',' '.join(o['dd'])); print(' ',o['hdr']); print('  '+' | '.join(o['rows']))
