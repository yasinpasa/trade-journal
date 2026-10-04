# C kurali, tarti.py ile birebir ayni tanim, gorulmemis veride. Her islem listelenir.
exec(open('tarti.py').read().split("out = []")[0])
c13 = np.where((df.lh.values == 13) & (df.lon.dt.dayofweek.values < 5))[0]
c13 = c13[c13 + 3 < n]
rg = pd.Series((H[c13] - L[c13]) / P); med = rg.rolling(20).median().shift(1).values
sec = ~np.isnan(med) & (rg.values <= med)
q = c13[sec]; d = -np.sign(C[q] - O[q]); k = d != 0; q, d = q[k], d[k]
v = (C[q + 3] - C[q]) / P * d
t = pd.DataFrame({'kurum': df.kurum.values[q], 'mum_pip': ((H[q]-L[q])/P).round(1),
                  'medyan': med[sec][k].round(1), 'yon': np.where(d > 0, 'AL', 'SAT'), 'h3_pip': v.round(1)})
print(t.to_string(index=False))
print(f'\nN {len(v)}  ort {v.mean():+.2f}  kazanan {np.mean(v>0)*100:.0f}%  toplam {v.sum():+.1f}  '
      f'SE ±{v.std(ddof=1)/np.sqrt(len(v)):.1f}  ilk 13:00 mumu {df.kurum.values[c13[0]]}  bos (isinma) {np.isnan(med).sum()} gun')
print('spread 13:00 mumunda ort', round(df.spread.values[q].mean(), 2))
