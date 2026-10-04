import numpy as np, pandas as pd
g = {}; exec(open('m15_cikis.py').read().split("def kosu")[0], g)
H, L, C, O, P, qs, ds, s = g['H'], g['L'], g['C'], g['O'], g['P'], g['qs'], g['ds'], g['s']
def frak(q, d, e, geri=48):
    for k in range(q - 2, max(2, q - geri), -1):
        if d > 0 and H[k] > max(H[k-2], H[k-1], H[k+1], H[k+2]) and H[k] > e + P: return (H[k] - e) / P
        if d < 0 and L[k] < min(L[k-2], L[k-1], L[k+1], L[k+2]) and L[k] < e - P: return (e - L[k]) / P
    return None
mum_h, mum_l = s.h.values, s.l.values
def kos(mod, sl=30, adim=12, MAL=0.7):
    out = []; tps = []; tpv = 0
    for i, (q, d) in enumerate(zip(qs, ds)):
        e = C[q]
        tp = 30 if mod == 'TP30' else frak(q, d, e) if mod == 'A' else ((mum_h[i] - e) / P if d > 0 else (e - mum_l[i]) / P)
        if tp is not None and tp < 0.5: tp = None
        tps.append(tp if tp else np.nan); r = None
        for j in range(q + 1, min(len(C), q + 1 + adim)):
            if ((e - L[j]) if d > 0 else (H[j] - e)) / P >= sl: r = -sl; break
            if tp and ((H[j] - e) if d > 0 else (e - L[j])) / P >= tp: r = tp; tpv += 1; break
        if r is None:
            j = min(len(C) - 1, q + adim); r = (C[j] - e) / P * d
        out.append(r - MAL)
    v = np.array(out); eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max(); t = np.array(tps)
    return dict(N=len(v), net=f'{v.mean():+.2f}', kazanan=f'{(v>0).mean()*100:.0f}%', dusus=round(dd),
                TP_vurdu=f'%{tpv/len(v)*100:.0f}', TP_ortanca_pip=round(np.nanmedian(t), 1), TP_yok=f'%{np.isnan(t).mean()*100:.0f}')
print('M15 verisi 2024-06..2026-06')
print(pd.DataFrame({'C standart TP30': kos('TP30'), '(A) M15 son tepe/dip': kos('A'), '(B) 15:00 mumunun tepe/dibi': kos('B')}).T.to_string())
