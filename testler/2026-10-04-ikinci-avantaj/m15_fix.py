# D: M15 ile fix çevresine çeyrek saat çeyrek saat bakış. SADECE keşif dönemi (2025-09-26 öncesi).
import warnings, os; warnings.filterwarnings("ignore")
import yukle as Y
Y.F = os.environ["EURUSD_M15"]
from yukle import *
d = Y.yukle()
d = d[(d.utc.dt.dayofweek < 5) & (d.bt < "2025-09-26")].copy()
d["dk"] = d.lon.dt.hour * 60 + d.lon.dt.minute
d["gun"] = d.lon.dt.date
print("aralık:", d.bt.min(), "→", d.bt.max(), "| mum", len(d))
# saat kontrolü: NFP cuması en büyük M15 mumu Londra 13:30 olmalı
fr = d[(d.lon.dt.dayofweek == 4) & (d.lon.dt.day <= 7)]
top = fr.loc[fr.groupby("gun").rng.idxmax()]
print("NFP en büyük mum Londra:", (top.dk // 60).astype(str).str.cat((top.dk % 60).astype(str), ":").value_counts().head(3).to_dict())
t = lambda v: v.mean() / (v.std() / np.sqrt(len(v)))
o = d.pivot_table(index="gun", columns="dk", values="open"); c = d.pivot_table(index="gun", columns="dk", values="close")
def sat(bas, son):  # bas dakikası açılışında SAT, son dakikası açılışında (= son-15 mumunun kapanışı) çık
    return (-(c[son - 15] - o[bas]) * 1e4).dropna()
hm = lambda m: f"{m//60:02d}:{m%60:02d}"
print("\n== Çeyrek saat çeyrek saat (11:00–14:30), tek M15 mumu SAT, brüt pip ==")
for m in range(11 * 60, 14 * 60 + 45, 15):
    x = sat(m, m + 15); print(f"{hm(m)}  n {len(x)} {x.mean():+5.2f}  t {t(x):+5.2f}")
print("\n== Çıkış zamanı (giriş 12:00) ==")
for son in (12*60+45, 13*60, 13*60+15, 13*60+30):
    x = sat(12*60, son); print(f"12:00 → {hm(son)}  n {len(x)} brüt {x.mean():+5.2f} t {t(x):+5.2f} σ {x.std():4.1f}  net/σ {(x.mean()-0.7)/x.std():.3f}")
print("\n== Giriş zamanı (çıkış 13:15) ==")
for bas in (11*60+45, 12*60, 12*60+15, 12*60+30):
    x = sat(bas, 13*60+15); print(f"{hm(bas)} → 13:15  n {len(x)} brüt {x.mean():+5.2f} t {t(x):+5.2f} σ {x.std():4.1f}  net/σ {(x.mean()-0.7)/x.std():.3f}")
