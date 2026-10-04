# TP = ilk tepe (H1 fraktal 2/2). Alis: girisin ustundeki en son onayli tepe; satis: altindaki en son dip. Son 48 H1 mum.
import numpy as np, pandas as pd
exec(open('varyasyon_C.py').read().split("yil = A")[0])
def tepe_tp(H, L, q, d, e, P, geri=48):
    for k in range(q - 2, max(2, q - geri), -1):           # k+2 <= q: onayli
        if d > 0 and H[k] > max(H[k-2], H[k-1], H[k+1], H[k+2]) and H[k] > e + 1 * P: return (H[k] - e) / P
        if d < 0 and L[k] < min(L[k-2], L[k-1], L[k+1], L[k+2]) and L[k] < e - 1 * P: return (e - L[k]) / P
    return None
def kos(G, mod, maxb, sl=30, MAL=0.7):
    H, L, C, P, n = G['H'], G['L'], G['C'], G['P'], G['n']
    out = []; tpler = []; cikis = []
    for q, d in zip(G['q'], G['d']):
        e = C[q]; tp = 30 if mod == 'TP30' else tepe_tp(H, L, q, d, e, P); tpler.append(tp if tp else np.nan); r = None
        for j in range(q + 1, min(n, q + maxb + 1)):
            if ((e - L[j]) if d > 0 else (H[j] - e)) / P >= sl: r = -sl; cikis.append('SL'); break
            if tp and ((H[j] - e) if d > 0 else (e - L[j])) / P >= tp: r = tp; cikis.append('TP'); break
        if r is None:
            j = min(n - 1, q + maxb); r = (C[j] - e) / P * d; cikis.append('sure')
        out.append(r - MAL)
    v = np.array(out); eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max()
    c = pd.Series(cikis).value_counts(normalize=True).mul(100).round(0)
    return v, dict(net=f'{v.mean():+.2f}', t=round(v.mean()/(v.std(ddof=1)/np.sqrt(len(v))), 2), kazanan=f'{(v>0).mean()*100:.0f}%',
                   dusus=round(dd), TP=f"%{c.get('TP',0):.0f}", SL=f"%{c.get('SL',0):.0f}", sure=f"%{c.get('sure',0):.0f}"), np.array(tpler)
rows = []
for mod in ('TP30', 'ilk tepe'):
    for maxb in (3, 4):
        va, a, tp_a = kos(A, mod, maxb); vb, b, _ = kos(B, mod, maxb)
        rows.append({'TP': mod, 'sure': f'{maxb} saat', **{f'5y_{k}': v for k, v in a.items()}, '2026_net': b['net'], '2026_kazanan': b['kazanan']})
        if mod == 'ilk tepe' and maxb == 3: tpd = tp_a
pd.set_option('display.width', 250)
print(pd.DataFrame(rows).to_string(index=False))
print('\nIlk tepe uzakligi (5y, pip): tepe bulunan %', round(np.mean(~np.isnan(tpd))*100),
      '| ceyrekler', np.nanpercentile(tpd, [10, 25, 50, 75, 90]).round(1))
