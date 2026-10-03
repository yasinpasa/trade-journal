# C icin saat plasebosu: ayni kural (kucuk mumu tersle, h=3) her Londra saatinde.
exec(open('tarti.py').read().split("out = []")[0])
rows=[]
for hh in range(24):
    c = np.where((df.lh.values == hh) & (df.lon.dt.dayofweek.values < 5))[0]
    c = c[c + 4 < n]
    rg = pd.Series((H[c] - L[c]) / P); med = rg.rolling(20).median().shift(1).values
    q = c[~np.isnan(med) & (rg.values <= med)]; d = -np.sign(C[q] - O[q]); q, d = q[d != 0], d[d != 0]
    v = (C[q + 3] - C[q]) / P * d
    rows.append((hh, len(v), round(v.mean(), 2), round(v.mean() / (v.std(ddof=1) / np.sqrt(len(v))), 2)))
print(pd.DataFrame(rows, columns=['lon_saat', 'N', 'brut_h3', 't']).to_string(index=False))
# Buyuk mumlar (medyan ustu) 13:00'te ne yapiyor? (ayni kuralin diger yarisi, yeni secim degil)
c13 = np.where((df.lh.values == 13) & (df.lon.dt.dayofweek.values < 5))[0]
rg = pd.Series((H[c13] - L[c13]) / P); med = rg.rolling(20).median().shift(1).values
for ad, s in (('kucuk', rg.values <= med), ('buyuk', rg.values > med)):
    q = c13[~np.isnan(med) & s]; d = -np.sign(C[q] - O[q]); v = (C[q + 3] - C[q]) / P * d
    print(ad, len(v), round(v.mean(), 2), round(v.mean() / (v.std(ddof=1) / np.sqrt(len(v))), 2))
# Yil yil (h=3)
q = c13[~np.isnan(med) & (rg.values <= med)]; d = -np.sign(C[q] - O[q]); v = (C[q + 3] - C[q]) / P * d
print(pd.Series(v).groupby(df.kurum.dt.year.values[q]).agg(['count', 'mean']).round(2).T.to_string())
