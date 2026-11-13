import sys
def load(path):
    ids={}; t=0; ev=[]
    for line in open(path):
        l=line.strip()
        if l.startswith('$var'): p=l.split(); ids[p[3]]=p[4]
        elif l.startswith('#'): t=int(l[1:])
        elif l and l[0] in '01' and l[1:] in ids: ev.append((t,ids[l[1:]],int(l[0])))
    # same timestamp: SCL fall -> SDA/FAULT -> SCL rise
    def key(e):
        t,ch,v=e
        return (t, 0 if (ch=='SCL' and v==0) else 2 if ch=='SCL' else 1)
    return sorted(ev,key=key)
def decode(ev):
    sda=scl=1; fault=0; tx=[]; cur=None; bits=[]; fault_edges=[]
    for t,ch,v in ev:
        if ch=='FAULT':
            if v!=fault: fault_edges.append((t/1e9,v))
            fault=v; continue
        if ch=='SDA':
            if scl==1 and sda==1 and v==0:   # START / repeated START
                if cur: tx.append(cur)
                cur={'t':t/1e9,'bytes':[],'acks':[],'stop':None}; bits=[]
            elif scl==1 and sda==0 and v==1 and cur:  # STOP
                cur['stop']=t/1e9; tx.append(cur); cur=None
            sda=v
        elif ch=='SCL':
            if v==1 and scl==0 and cur is not None:
                bits.append(sda)
                if len(bits)==9:
                    b=0
                    for x in bits[:8]: b=(b<<1)|x
                    cur['bytes'].append(b); cur['acks'].append('ACK' if bits[8]==0 else 'NACK'); bits=[]
            scl=v
    if cur: tx.append(cur)
    return tx, fault_edges
if __name__=='__main__':
    for path in sys.argv[1:]:
        ev=load(path); tx,fe=decode(ev); end=ev[-1][0]/1e9
        print('##',path,'end %.3f'%end,'FAULT edges(first/last):',fe[:1],fe[-1:])
        for x in tx:
            if not x['bytes']: continue
            a=x['bytes'][0]; addr=a>>1; rw='R' if a&1 else 'W'
            print('  %.6f 0x%02X %s data=%s acks=%s'%(x['t'],addr,rw,[hex(b) for b in x['bytes'][1:]],x['acks']))
