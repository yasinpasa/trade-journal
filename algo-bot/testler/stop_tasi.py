# Stop tasima: kar +X pipe ulasinca stop -> giris (BE) veya -15 (yari). Mum icinde: once mevcut stop, sonra TP, sonra tasima.
import numpy as np, pandas as pd
def sim_tasi(H, L, C, qs, ds, P, adim, tetik=None, yeni=None, sl=30, tp=30, MAL=0.7):
    out = []
    n = len(C)
    for q, d in zip(qs, ds):
        e = C[q]; stop = -sl; r = None              # stop: giris'e gore pip (negatif = zarar tarafi)
        for j in range(q + 1, min(n, q + 1 + adim)):
            aley = (e - L[j]) / P if d > 0 else (H[j] - e) / P
            lehe = (H[j] - e) / P if d > 0 else (e - L[j]) / P
            if -aley <= stop: r = stop; break
            if tp and lehe >= tp: r = tp; break
            if tetik is not None and lehe >= tetik: stop = max(stop, yeni)
        if r is None:
            j = min(n - 1, q + adim); r = (C[j] - e) / P * d
        out.append(r - MAL)
    return np.array(out)
def ozet(v):
    eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max()
    return f'{v.mean():+.2f}', f'{(v>0).mean()*100:.0f}%', round(dd)
AYAR = [('Yok (C standart)', None, None)] + [(f'{"Girise" if y == 0 else "Yariya (-15)"} @+{t}', t, y) for y in (0, -15) for t in (10, 15, 20)]
# M15 (2 yil)
exec(open('m15_cikis.py').read().split("def kosu")[0])
# H1 (5 yil + 2026)
exec(open('varyasyon_C.py').read().split("yil = A")[0])
rows = []
for ad, t, y in AYAR:
    m15 = ozet(sim_tasi(H, L, C, qs, ds, P, 12, t, y)) if False else None
    rows.append([ad, t, y])
# M15 degiskenleri varyasyon_C exec'i ile ezildi; yeniden yukle
g = {}; exec(open('m15_cikis.py').read().split("def kosu")[0], g)
res = []
for ad, t, y in AYAR:
    a = ozet(sim_tasi(g['H'], g['L'], g['C'], g['qs'], g['ds'], g['P'], 12, t, y))
    b = ozet(sim_tasi(A['H'], A['L'], A['C'], A['q'], A['d'], A['P'], 3, t, y))
    c = ozet(sim_tasi(B['H'], B['L'], B['C'], B['q'], B['d'], B['P'], 3, t, y))
    res.append(dict(ayar=ad, M15_2yil_net=a[0], M15_kazanan=a[1], M15_dusus=a[2],
                    H1_5yil_net=b[0], H1_5yil_kazanan=b[1], H1_5yil_dusus=b[2], H1_2026_net=c[0]))
pd.set_option('display.width', 220)
print(pd.DataFrame(res).to_string(index=False))
