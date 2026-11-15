import json,re,sys
d=json.load(open(sys.argv[1]))
out={}
for bn in sorted(d,key=int):
    o=d[bn]; r=o['rows']
    print(f"#{bn} {o['deal']['dealer']}/{o['deal']['vul']}  N:{o['deal']['N']} E:{o['deal']['E']} S:{o['deal']['S']} W:{o['deal']['W']}")
    dd=o['dd'][6:]
    print('  DD(NT S H D C hp): '+' '.join(dd[i]+':'+','.join(dd[i+1:i+6])+'('+dd[i+6]+')' for i in range(0,28,7)),'|',o['hdr'])
    i=0
    while i+3<len(r) and ' - ' in r[i] or (i<len(r) and r[i]=='(Oversidder)'):
        ns,ew=r[i+1],r[i+3]; i+=4
        j=i
        while j<len(r) and not (' - ' in r[j] or r[j]=='(Oversidder)' or (re.match(r'^\d+$',r[j]) and j+1<len(r) and re.match(r'^(Nord|Syd|Øst|Vest)/$',r[j+1]))): j+=1
        print(f"   {ns:>2}-{ew:<2} "+' '.join(r[i:j])); i=j
