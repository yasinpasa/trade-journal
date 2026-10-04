# 2026-10-04 Kahin sonrası testler: 24 saatlik profil, 12:00 Londra SAT, C ayrıştırma, Asya dönüşü.
# Çalıştırma: EURUSD_H1=<csv yolu> python3 profil_ve_testler.py
from ckural import *

t = lambda v: round(v.mean() / (v.std() / np.sqrt(len(v))), 2)

d = yukle()
w = d[d.utc.dt.dayofweek < 5].copy()
w["yil"] = w.utc.dt.year

print("== 1) Londra saatine göre tek mum ortalaması (pip), t, artı yıl ==")
for h in range(24):
    x = w[w.lh == h]
    print(h, len(x), round(x.r.mean(), 2), t(x.r), (x.groupby("yil").r.mean() > 0).sum())

print("\n== 2) 12:00 Londra SAT (ECB fix 13:15 Londra öncesi) ==")
x = w[w.lh == 12]
s = -x.r
print("n", len(s), "brüt", round(s.mean(), 2), "t", t(s), "yıllar", s.groupby(x.yil).mean().round(2).to_dict())

print("\n== 3) C ayrıştırma ==")
c = c_islemler(d)
print("C n", len(c), "brüt", round(c.top.mean(), 2), "t", t(c.top))
x = x.assign(gun=x.bt.dt.normalize())
m = c.merge(x[["gun", "r"]], on="gun")
for k, g in m.groupby(m.r < 0):
    print("12:00 düştü" if k else "12:00 yükseldi", len(g), round(g.top.mean(), 2), t(g.top))
gun = pd.DataFrame({"gun": x.gun.unique()})
g2 = gun.merge(c[["gun", "top"]], on="gun", how="left").merge(x[["gun", "r"]], on="gun", how="left").fillna(0)
g2["s12"] = -g2.r
print("günlük PnL korelasyonu C vs 12:00 SAT", round(g2[["top", "s12"]].corr().iloc[0, 1], 3))
