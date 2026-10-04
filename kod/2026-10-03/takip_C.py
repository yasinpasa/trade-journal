# C + takip eden stop. H1 mumla temkinli simulasyon: her mumda once MEVCUT stop/TP kontrol, sonra stop guncellenir
# (mum icinde yeni tepe sonrasi geri donus o mumda yakalanmaz, sonraki mumda stop seviyesinden cikar).
exec(open('varyasyon_C.py').read().split("yil = A")[0])
def sim_takip(g, sl, tp, tr, bas, maxb=3):
    H, L, C, q, d, P, n = g['H'], g['L'], g['C'], g['q'], g['d'], g['P'], g['n']
    out = []
    for qq, dd in zip(q, d):
        e = C[qq]; stop = e - dd * sl * P; r = None
        for j in range(qq + 1, min(n, qq + maxb + 1)):
            lo, hi = (L[j], H[j]) if dd > 0 else (-H[j], -L[j])   # yonu normalize et
            ee, ss = dd * e, dd * stop
            if lo <= ss: r = (ss - ee) / P; break
            if tp and hi >= ee + tp * P: r = tp; break
            if tr and (hi - ee) / P >= bas:
                ss = max(ss, hi - tr * P); stop = dd * ss
        if r is None:
            j = min(n - 1, qq + maxb); ee, ss = dd * e, dd * stop
            r = max((dd * C[j] - ee) / P, (ss - ee) / P) if tr else (dd * C[j] - ee) / P
        out.append(r - MALIYET)
    return np.array(out)
def ozet(v):
    eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max()
    return v.mean(), v.mean() / (v.std(ddof=1) / np.sqrt(len(v))), (v > 0).mean() * 100, dd
rows = []
for tp in (30, None):
    for tr, bas in [(None, 0)] + [(t, b) for t in (10, 15, 20, 25, 30) for b in (0, 10, 15)]:
        a = ozet(sim_takip(A, 30, tp, tr, bas)); b = ozet(sim_takip(B, 30, tp, tr, bas))
        rows.append(dict(TP=tp or '-', takip=tr or 'yok', baslat=f'+{bas}' if tr else '-',
                         net5y=round(a[0], 2), t5y=round(a[1], 2), kazan5y=f'{a[2]:.0f}%', dusus5y=round(a[3]),
                         net26=round(b[0], 2), kazan26=f'{b[2]:.0f}%'))
pd.set_option('display.width', 200)
print(pd.DataFrame(rows).to_string(index=False))
