# C girisi + M15 cikis kurallari. Veri: EURUSD M15 2024-06..2026-06 (kurum saati). H1 sinyali M15'ten uretilir.
import pandas as pd, numpy as np
x = pd.read_csv('m15.csv', sep='\t'); x.columns = [c.strip('<>').lower() for c in x.columns]
m = pd.DataFrame({'t': pd.to_datetime(x.date + ' ' + x.time), 'o': x.open, 'h': x.high, 'l': x.low, 'c': x.close})
P = 1e-4; MAL = 0.7
O, H, L, C, T = m.o.values, m.h.values, m.l.values, m.c.values, m.t.values
# H1 15:00 sinyal mumu = 15:00,15:15,15:30,15:45 M15 mumlari
m['saat'] = m.t.dt.floor('h')
h1 = m.groupby('saat').agg(o=('o', 'first'), h=('h', 'max'), l=('l', 'min'), c=('c', 'last'), son=('t', 'idxmax'))
h1 = h1[(h1.index.hour == 15) & (h1.index.dayofweek < 5)]
boy = (h1.h - h1.l) / P; med = boy.rolling(20).median().shift(1)
s = h1[(boy <= med) & (h1.c != h1.o)]
qs = s.son.values.astype(int)                          # sinyal mumunun son M15 mumu (15:45) -> giris onun kapanisi
ds = np.where(s.c < s.o, 1, -1)
# kontrol: H1 dosyasiyla karsilastirma
try:
    y = pd.read_csv('/root/.claude/uploads/32e92e29-a025-54aa-acd4-754c5bad69e2/be3bc389-EURUSD_H1_202601020000_202609290000.csv', sep='\t')
    y.columns = [c.strip('<>').lower() for c in y.columns]; y.index = pd.to_datetime(y.date + ' ' + y.time)
    ort = h1.index.intersection(y.index); print('H1 kontrol: ortak', len(ort), 'kapanis farki max', float((h1.c[ort] - y.close[ort]).abs().max()))
except Exception as e: print('kontrol yok', e)

def kosu(kural, sl=30, tp=None, maxm=12):
    out = []; sure = []
    for q, d in zip(qs, ds):
        e = C[q]; r = None
        for j in range(q + 1, min(len(C), q + 1 + maxm)):
            if (e - L[j] if d > 0 else H[j] - e) / P >= sl: r = -sl; break
            if tp and (H[j] - e if d > 0 else e - L[j]) / P >= tp: r = tp; break
            if kural == 'ilk_ters' and np.sign(C[j] - O[j]) == -d: r = (C[j] - e) / P * d; break
        if r is None:
            j = min(len(C) - 1, q + maxm); r = (C[j] - e) / P * d
        out.append(r - MAL); sure.append(j - q)
    v = np.array(out); eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max()
    return v, dict(N=len(v), net=round(v.mean(), 2), t=round(v.mean() / (v.std(ddof=1) / np.sqrt(len(v))), 2),
                   kazanan=f'{(v>0).mean()*100:.0f}%', zarar_eden=f'{(v<0).mean()*100:.0f}%', ort_kayip=round(v[v<0].mean(), 1),
                   ort_kazanc=round(v[v>0].mean(), 1), en_kotu=round(v.min(), 1), dusus=round(dd), ort_sure_dk=round(np.mean(sure) * 15))
rows = {}
for ad, args in (('C standart (SL30 TP30 3s)', ('sure', 30, 30, 12)),
                 ('Yasin: ilk ters M15 (SL30)', ('ilk_ters', 30, None, 48)),
                 ('Yasin + en gec 3 saat', ('ilk_ters', 30, None, 12)),
                 ('Yasin + TP30 + 3 saat', ('ilk_ters', 30, 30, 12))):
    v, o = kosu(*args); rows[ad] = o
    if ad.startswith('Yasin: '): yv = v
pd.set_option('display.width', 220)
print(pd.DataFrame(rows).T.to_string())
print('\nYasin kurali: ilk M15 mumu ters kapanan islem orani:',
      f"{np.mean([np.sign(C[q+1]-O[q+1]) == -d for q, d in zip(qs, ds)])*100:.0f}%")
print('Yasin kurali en kotu 5 islem:', np.sort(yv)[:5].round(1))
