# C kurali SL/TP izgarasi. Giris: sinyal mumu kapanisi. Her mumda once SL sonra TP (ayni mumda ikisi -> SL).
# Ne SL ne TP olursa MAXB mum sonra kapanisla cikis. Maliyet: 0,7 pip (spread+komisyon tahmini).
import sys
SRC = open('ileri_C.py').read().split("t = pd.DataFrame")[0]
MALIYET = 0.7
def olaylar(F):
    sys.argv = ['x', F]; g = {}; exec(SRC, g); return g
def sim(g, sl, tp, maxb):
    H, L, C, q, d, P, n = g['H'], g['L'], g['C'], g['q'], g['d'], g['P'], g['n']
    out = []
    for qq, dd in zip(q, d):
        e = C[qq]; r = None
        for j in range(qq + 1, min(n, qq + maxb + 1)):
            adv = (e - L[j]) / P if dd > 0 else (H[j] - e) / P     # aleyhe
            fav = (H[j] - e) / P if dd > 0 else (e - L[j]) / P     # lehe
            if sl and adv >= sl: r = -sl; break
            if tp and fav >= tp: r = tp; break
        if r is None:
            j = min(n - 1, qq + maxb); r = (C[j] - e) / P * dd
        out.append(r - MALIYET)
    return np.array(out)
import numpy as np, pandas as pd
A = olaylar("/root/.claude/uploads/32e92e29-a025-54aa-acd4-754c5bad69e2/9898d3fe-EURUSD_H1_202009210000_202509260000.csv")
B = olaylar("/root/.claude/uploads/32e92e29-a025-54aa-acd4-754c5bad69e2/be3bc389-EURUSD_H1_202601020000_202609290000.csv")
yil = A['df'].kurum.dt.year.values[A['q']]
rows = []
for maxb in (3,):
    for sl in (10, 15, 20, 30, None):
        for tp in (10, 15, 20, 30, None):
            a = sim(A, sl, tp, maxb); b = sim(B, sl, tp, maxb)
            yy = pd.Series(a).groupby(yil).mean(); yy = yy[yy.index >= 2021]
            rows.append(dict(SL=sl or '-', TP=tp or '-', net_5y=round(a.mean(), 2), t_5y=round(a.mean()/(a.std(ddof=1)/np.sqrt(len(a))), 2),
                             kazan=f'{(a>0).mean()*100:.0f}%', arti_yil=f'{(yy>0).sum()}/{len(yy)}',
                             net_2026=round(b.mean(), 2), kazan26=f'{(b>0).mean()*100:.0f}%'))
r = pd.DataFrame(rows)
print('olay sayisi 5y', len(A['q']), ' 2026', len(B['q']))
print(r.to_string(index=False))
# en kotu art arda kayip ve en buyuk dusus (SL20/TP- , SL-/TP- icin)
for sl, tp in ((None, None), (20, None), (15, 30), (20, 20)):
    a = sim(A, sl, tp, 3); eq = np.cumsum(a); dd = (np.maximum.accumulate(eq) - eq).max()
    s = 0; mx = 0
    for v in a:
        s = s + 1 if v < 0 else 0; mx = max(mx, s)
    print(f'SL{sl}/TP{tp}: en buyuk dusus {dd:.0f} pip, en uzun kayip serisi {mx}, toplam {eq[-1]:.0f} pip')
