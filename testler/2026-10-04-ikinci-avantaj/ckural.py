from yukle import *
def c_islemler(d):
    d=d.sort_values("bt").reset_index(drop=True)
    d["gun"]=d.bt.dt.normalize()
    s=d[(d.bh==15)&(d.bt.dt.dayofweek<5)].copy()
    s["med"]=s.rng.shift(1).rolling(20).median()
    out=[]
    for i,row in s.iterrows():
        if np.isnan(row.med) or row.rng>row.med or row.close==row.open: continue
        yon=-1 if row.close>row.open else 1
        bars=[]
        for k in (1,2,3):
            j=i+k
            if j<len(d) and d.at[j,"gun"]==row.gun and d.at[j,"bh"]==15+k: bars.append(d.loc[j])
        if len(bars)<3: continue
        p=[yon*(b.close-b.open)*1e4 for b in bars]
        out.append(dict(gun=row.gun,yon=yon,b16=p[0],b17=p[1],b18=p[2],top=sum(p),lh_sig=row.lh,
                        ayson=(row.gun+pd.offsets.BDay(1)).month!=row.gun.month, nfp=(row.gun.dayofweek==4 and row.gun.day<=7)))
    return pd.DataFrame(out)
