# 2026-10-03 Oturum 5 — 4 fikri tek tabloda tartma (Kahin 2. adim)
# Tanimlar sonuclara bakmadan yazildi. Olcu: stop'suz, giris mumu kapanisindan
# h=1..4 mum sonraki kapanisa yonlu getiri, BRUT pip (spread dusulmemis).
# Plasebo: ayni olaylarda yonler 5000 kez karistirilir (permutasyon).
# Saat: kurum saati = Londra + 2 (Oturum 4: kurum 00:00 = Londra 22:00).
import pandas as pd, numpy as np, sys
F = sys.argv[1]
x = pd.read_csv(F, sep='\t')
x.columns = [c.strip('<>').lower() for c in x.columns]
df = pd.DataFrame({'kurum': pd.to_datetime(x.date + ' ' + x.time, format='%Y.%m.%d %H:%M:%S'),
                   'open': x.open, 'high': x.high, 'low': x.low, 'close': x.close, 'spread': x.spread / 10})
df['lon'] = df.kurum - pd.Timedelta(hours=2)
df['utc'] = df.lon.dt.tz_localize('Europe/London', ambiguous=np.zeros(len(x), bool), nonexistent='shift_forward').dt.tz_convert('UTC').dt.tz_localize(None)
df['lh'] = df.lon.dt.hour; df['ld'] = df.lon.dt.normalize()
P = 1e-4
O, H, L, C = (df[c].values for c in ('open', 'high', 'low', 'close'))
n = len(C); HS = (1, 2, 3, 4)
YIL = (df.kurum.iloc[-1] - df.kurum.iloc[0]).days / 365.25
ORTA = df.kurum.iloc[0] + (df.kurum.iloc[-1] - df.kurum.iloc[0]) / 2

def fwd(q, d, h):
    return (C[q + h] - C[q]) / P * d

def olc(ad, qs, ds):
    qs = np.asarray(qs); ds = np.asarray(ds, float)
    ok = (qs + 4 < n) & (ds != 0); qs, ds = qs[ok], ds[ok]
    rng = np.random.default_rng(11); satir = []
    for h in HS:
        r = (C[qs + h] - C[qs]) / P            # yonsuz hareket
        v = r * ds; m = v.mean(); sd = v.std(ddof=1); t = m / (sd / np.sqrt(len(v)))
        perm = np.array([(r * rng.permutation(ds)).mean() for _ in range(5000)])
        p = (np.abs(perm) >= abs(m)).mean()
        ilk = df.kurum.values[qs] < np.datetime64(ORTA)
        m1, m2 = v[ilk].mean(), v[~ilk].mean()
        yil_olay = len(v) / YIL
        if m > 0:
            gerek = (2.7 * sd / m) ** 2; ay = gerek / yil_olay * 12
        else:
            gerek = ay = np.inf
        satir.append(dict(fikir=ad, h=h, N=len(v), yil=round(yil_olay), brut=round(m, 2), sd=round(sd, 1),
                          t=round(t, 2), p_perm=round(p, 3), yari1=round(m1, 2), yari2=round(m2, 2),
                          gerek_N=(round(gerek) if np.isfinite(gerek) else '-'),
                          ay=(round(ay, 1) if np.isfinite(ay) else '-'),
                          spread=round(df.spread.values[qs].mean(), 2)))
    return satir

out = []

# A1) Gun ici momentum: 07:00-08:00 UTC mumu yonunde, mum kapanisinda giris.
qa = np.where(df.utc.dt.hour.values == 7)[0]
out += olc('A1 momentum 07-08 UTC', qa, np.sign(C[qa] - O[qa]))

# A2) Gece momentumu: onceki gun 21:00 UTC kapanisindan 08:00 UTC'ye getiri yonunde (Elaut tipi).
utc = df.utc.values; idx = pd.Series(np.arange(n), index=df.utc)
q2, d2 = [], []
for q in qa:
    t0 = utc[q] - np.timedelta64(11, 'h')    # 07:00 mumu kapanisi 08:00; 08:00-11h = 21:00 dun
    j = np.searchsorted(utc, t0, side='right') - 1   # 20:00 UTC mumu (kapanisi 21:00)
    if j >= 0 and (utc[q] - utc[j]) <= np.timedelta64(13, 'h'):
        q2.append(q); d2.append(np.sign(C[q] - C[j]))
out += olc('A2 gece momentumu 21->08 UTC', q2, d2)

# B) Gunluk aralik tukenmesi: Londra gunu 00:00'dan. Ort. gunluk aralik = onceki 20 gun.
# Londra 07-20 arasi, gun araligi ilk kez >= ortalama oldugu VE o mum yeni gun ucu yaptigi anda,
# ucun tersine giris. Gunde en fazla 1.
g = df.groupby('ld').agg(hi=('high', 'max'), lo=('low', 'min'))
g['avg'] = (g.hi - g.lo).rolling(20).mean().shift(1)
avg = df.ld.map(g.avg).values
qb, db = [], []
for ld, grp in df.groupby('ld'):
    ii = grp.index.values; hi = -1e9; lo = 1e9
    for q in ii:
        yh, yl = H[q] > hi, L[q] < lo
        hi, lo = max(hi, H[q]), min(lo, L[q])
        if 7 <= df.lh.values[q] <= 20 and not np.isnan(avg[q]) and (hi - lo) >= avg[q] and (yh or yl):
            if yh and yl: break                  # iki uc birden: belirsiz, gun atlanir
            qb.append(q); db.append(-1 if yh else 1); break
out += olc('B aralik tukenmesi (fade)', qb, db)

# C) Haber fade (VEKIL, surpriz verisi yok): Londra 13:00 mumu (13:30 ABD verisi),
# mum araligi son 20 gunun ayni saat medyaninin altindaysa ("kucuk surpriz"), mum yonunun tersine.
c13 = np.where((df.lh.values == 13) & (df.lon.dt.dayofweek.values < 5))[0]
rg = pd.Series((H[c13] - L[c13]) / P)
med = rg.rolling(20).median().shift(1).values
sec = ~np.isnan(med) & (rg.values <= med)
qc = c13[sec]
out += olc('C haber fade vekil 13:30 kucuk mum', qc, -np.sign(C[qc] - O[qc]))

# D) Ay sonu fix sonrasi donus: ayin son islem gunu, Londra 15:00 mumu (kapanis 16:00 = fix),
# 13:00->16:00 hareketinin tersine.
d15 = df[df.lh == 15].copy(); d15['ay'] = d15.lon.dt.to_period('M')
son = d15.groupby('ay').tail(1).index.values
qd, dd = [], []
for q in son:
    j = q - 2
    if j >= 0 and df.lh.values[j] == 13:
        qd.append(q); dd.append(-np.sign(C[q] - O[j]))
out += olc('D ay sonu fix sonrasi donus', qd, dd)

pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30)
print(f'Veri: {df.kurum.iloc[0]} .. {df.kurum.iloc[-1]}  ({YIL:.2f} yil), yari sinir {ORTA.date()}')
print(pd.DataFrame(out).to_string(index=False))
