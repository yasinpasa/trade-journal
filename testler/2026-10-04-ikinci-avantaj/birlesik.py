# C + D birleşik test. C: SL 30 / TP 30 / en geç 3 mum (aynı mumda ikisi → SL). D: 12:00 Londra SAT, 1 mum.
import warnings; warnings.filterwarnings("ignore")
# D için SL 30 (C ile aynı, ayar aranmadı) ve stop'suz iki hal. Maliyet 0,7 pip/işlem.
# Para: 10.000$, işlem başı %0,5 risk, 1R = 30 pip (iki kural aynı lot), bileşik.
from yukle import *
MAL = 0.7

def sim(d, i, yon, nbar, sl, tp):
    """i: giriş mumunun indeksi (açılışında gir). nbar mum tut. sl/tp pip (None=yok)."""
    g = d.at[i, "open"]
    for k in range(nbar):
        b = d.loc[i + k]
        ters = (b.high - g) * 1e4 if yon < 0 else (g - b.low) * 1e4
        lehe = (g - b.low) * 1e4 if yon < 0 else (b.high - g) * 1e4
        if sl is not None and ters >= sl: return -sl
        if tp is not None and lehe >= tp: return tp
    return yon * (d.at[i + nbar - 1, "close"] - g) * 1e4

def c_listesi(d, sl=30, tp=30):
    s = d[(d.bh == 15) & (d.bt.dt.dayofweek < 5)].copy()
    s["med"] = s.rng.shift(1).rolling(20).median()
    out = []
    for i, r in s.iterrows():
        if np.isnan(r.med) or r.rng > r.med or r.close == r.open: continue
        if i + 3 >= len(d) or d.at[i + 3, "bt"] - r.bt != pd.Timedelta(hours=3): continue
        yon = -1 if r.close > r.open else 1
        out.append(dict(zaman=d.at[i + 1, "utc"], kural="C", pip=sim(d, i + 1, yon, 3, sl, tp) - MAL))
    return pd.DataFrame(out)

def d_listesi(d, sl):
    s = d[(d.lh == 12) & (d.utc.dt.dayofweek < 5)]
    return pd.DataFrame([dict(zaman=d.at[i, "utc"], kural="D", pip=sim(d, i, -1, 1, sl, None) - MAL) for i in s.index])

def rapor(ad, X):
    X = X.sort_values("zaman").reset_index(drop=True)
    p = X.pip
    eq = p.cumsum(); dd = (eq.cummax() - eq).max()
    bak = 10000.0; tepe = bak; ddp = 0
    for v in p:
        bak += bak * 0.005 * v / 30; tepe = max(tepe, bak); ddp = max(ddp, (tepe - bak) / tepe)
    yil = (X.zaman.iloc[-1] - X.zaman.iloc[0]).days / 365.25
    ay = p.groupby(X.zaman.dt.to_period("M")).sum()
    yy = p.groupby(X.zaman.dt.year).sum().round(0).astype(int).to_dict()
    t = p.mean() / (p.std() / np.sqrt(len(p)))
    print(f"{ad:24s} işlem {len(p):5d} | net {p.mean():+.2f} pip/işlem t {t:4.2f} | toplam {p.sum():+6.0f} pip | "
          f"max düşüş {dd:4.0f} pip ({dd/30:.1f}R) | para {(bak/1e4-1)*100:+5.1f}% (yıllık {((bak/1e4)**(1/yil)-1)*100:+4.1f}%) "
          f"max düşüş %{ddp*100:4.1f} | eksi ay {(ay<0).sum()}/{len(ay)}")
    print(f"{'':24s} yıllar (pip): {yy}")
    return ay

if __name__ == "__main__":
    d = yukle().sort_values("utc").reset_index(drop=True)
    C = c_listesi(d)
    for etiket, sl in (("SL 30", 30), ("stop'suz", None)):
        D = d_listesi(d, sl)
        print(f"\n===== D {etiket} =====")
        ac = rapor("C tek başına", C)
        ad = rapor(f"D tek başına", D)
        rapor("C + D birlikte", pd.concat([C, D]))
        aa = pd.concat([ac, ad], axis=1).fillna(0)
        print(f"{'':24s} aylık korelasyon C-D {aa.corr().iloc[0,1]:.2f} | ikisi birlikte eksi ay {((aa.iloc[:,0]<0)&(aa.iloc[:,1]<0)).sum()}")
