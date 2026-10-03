# 1) C sonuclari haftanin gunune gore  2) filtresiz: her gun 15:00 (kurum) mumunun tersine. SL30/TP30/3 mum, net 0,7.
exec(open('varyasyon_C.py').read().split("yil = A")[0])
GUN = ['Pzt', 'Sal', 'Car', 'Per', 'Cum']
def hergun(G):
    g = dict(G); df, H, L, C, O, P = G['df'], G['H'], G['L'], G['C'], G['O'], G['P']
    c = np.where((df.lh.values == 13) & (df.lon.dt.dayofweek.values < 5))[0]
    c = c[c + 3 < G['n']]
    rg = pd.Series((H[c] - L[c]) / P); med = rg.rolling(20).median().shift(1).values
    c = c[~np.isnan(med)]                      # ayni donem (isinma sonrasi) karsilastirilsin
    d = -np.sign(C[c] - O[c]); k = d != 0
    g['q'], g['d'] = c[k], d[k]
    return g
for ad, G in (('5 yil', A), ('2026', B)):
    Ghep = hergun(G)
    for nm, X in (('C (kucuk mum)', G), ('HER GUN (filtresiz)', Ghep)):
        v = sim(X, 30, 30, 3); dow = X['df'].lon.dt.dayofweek.values[X['q']]
        eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max()
        print(f'\n{ad} | {nm}: N {len(v)} net {v.mean():+.2f} t {v.mean()/(v.std(ddof=1)/np.sqrt(len(v))):.2f} '
              f'kazanan %{(v>0).mean()*100:.0f} toplam {eq[-1]:+.0f} pip dusus {dd:.0f}')
        s = pd.Series(v).groupby(dow).agg(['count', 'mean'])
        print('   ' + ' | '.join(f'{GUN[i]} {int(r["count"])} {r["mean"]:+.2f}' for i, r in s.iterrows()))
    # buyuk mum gunleri ayrica
    qset = set(G['q']); m = np.array([q not in qset for q in Ghep['q']])
    Gb = dict(Ghep); Gb['q'], Gb['d'] = Ghep['q'][m], Ghep['d'][m]
    v = sim(Gb, 30, 30, 3); print(f'   {ad} | sadece BUYUK mum gunleri: N {len(v)} net {v.mean():+.2f}')
