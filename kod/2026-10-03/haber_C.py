# C kurali x ABD haber takvimi (TradingView, importance=1). Olcu: SL30/TP30/3 mum, net (0,7 maliyet).
exec(open('varyasyon_C.py').read().split("yil = A")[0])
import pandas as pd, numpy as np
k = pd.read_csv('takvim_tam.csv'); k['t'] = pd.to_datetime(k.date, utc=True)
k['lon'] = k.t.dt.tz_convert('Europe/London')
k = k[k.lon.dt.hour == 13]                     # sinyal mumunun icinde (Londra 13:xx)
k['gun'] = k.lon.dt.tz_localize(None).dt.normalize()
ANA = {'Non Farm Payrolls': 'NFP', 'Inflation Rate YoY': 'CPI', 'Core Inflation Rate YoY': 'CPI',
       'Retail Sales MoM': 'RS', 'Durable Goods Orders MoM': 'DGO', 'Personal Income MoM': 'PI', 'Personal Spending MoM': 'PI'}
SURP = ['Non Farm Payrolls', 'Core Inflation Rate YoY', 'Inflation Rate YoY', 'Retail Sales MoM', 'Durable Goods Orders MoM']
ana = k[k.title.isin(ANA)]
genis = set(k.gun)
s = k[k.title.isin(SURP)].dropna(subset=['actual', 'forecast']).copy()
s['d'] = s.actual - s.forecast
s['z'] = s.d / s.groupby('title').d.transform(lambda v: v.abs().median() * 1.4826 + 1e-9)
zgun = s.groupby('gun').z.apply(lambda v: v.abs().max())
# Haber 12:30 Londra'da (ABD/UK yaz saati kaymasi): sinyal mumundan ONCE
k2 = pd.read_csv('takvim_tam.csv'); k2['t'] = pd.to_datetime(k2.date, utc=True); k2['lon'] = k2.t.dt.tz_convert('Europe/London')
once = set(k2[(k2.lon.dt.hour == 12) & (k2.lon.dt.minute == 30)].lon.dt.tz_localize(None).dt.normalize())

def tablo(G, ad):
    v = sim(G, 30, 30, 3); g = G['df'].lon.dt.normalize().values[G['q']]
    g = pd.to_datetime(g)
    grp = np.where(g.isin(set(ana.gun)), 'ana haber', np.where(g.isin(genis), 'diger haber', np.where(g.isin(once), 'haber mumdan once', 'bos gun')))
    t = pd.DataFrame({'grp': grp, 'v': v})
    o = t.groupby('grp').v.agg(N='count', net='mean', sd='std'); o['t'] = o.net / (o.sd / np.sqrt(o.N)); o['kazan%'] = t.groupby('grp').v.apply(lambda x: (x > 0).mean() * 100)
    print(f'\n== {ad} =='); print(o.drop(columns='sd').round(2).to_string())
    z = pd.Series(g).map(zgun).values
    m = ~np.isnan(z)
    if m.sum() > 10:
        med = np.nanmedian(z)
        for nm, sel in (('kucuk surpriz', m & (z <= med)), ('buyuk surpriz', m & (z > med))):
            print(f'  {nm}: N {sel.sum()} net {v[sel].mean():+.2f}  (|z| esik {med:.2f})')
    return t
tA = tablo(A, '5 yil 2020-09..2025-09')
tB = tablo(B, '2026 Oca-Eyl')
