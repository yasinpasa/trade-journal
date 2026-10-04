# GÖRÜLMEMİŞ VERİ SINAVI (bir kez): 2025-09-26 → 2026-09-29, M15'ten H1 kurularak.
# D kilitli: Londra 12:00 açılışında SAT, 13:00'te çık (12:45 M15 kapanışı). Geçme: aynı işaret, brüt ≥1,0, t ≥1,0.
# C: kurum 15:00 H1 küçük mum tersine; stop'suz 3 saat ve SL30/TP30/3 saat. Maliyet 0,7.
import warnings, os; warnings.filterwarnings("ignore")
import yukle as Y
Y.F = os.environ["EURUSD_M15"]
from yukle import *
from birlesik import sim, rapor
m = Y.yukle()
m = m[m.bt >= "2025-09-01"].copy()   # 20 günlük ortanca için ısınma payı; işlemler 2025-09-26'dan itibaren
# M15 → kurum H1
m["hb"] = m.bt.dt.floor("h")
h = m.groupby("hb").agg(open=("open", "first"), high=("high", "max"), low=("low", "min"), close=("close", "last"), n=("open", "size")).reset_index()
h = h[h.n == 4].rename(columns={"hb": "bt"})
ny = h.bt - pd.Timedelta(hours=7)
h["utc"] = ny.dt.tz_localize("America/New_York", ambiguous="NaT", nonexistent="shift_forward").dt.tz_convert("UTC")
h = h.dropna(subset=["utc"]).sort_values("utc").reset_index(drop=True)
h["lon"] = h.utc.dt.tz_convert("Europe/London"); h["lh"] = h.lon.dt.hour; h["bh"] = h.bt.dt.hour
h["r"] = (h.close - h.open) * 1e4; h["rng"] = (h.high - h.low) * 1e4
BAS = pd.Timestamp("2025-09-26")
t = lambda v: v.mean() / (v.std() / np.sqrt(len(v)))

# --- D
x = h[(h.lh == 12) & (h.utc.dt.dayofweek < 5) & (h.bt >= BAS)]
s = -x.r
print(f"D SINAV  n {len(s)} | brüt {s.mean():+.2f} | t {t(s):+.2f} | kazanan %{(s>0).mean()*100:.0f} | net {s.mean()-0.7:+.2f}")
print("   ay ay brüt:", s.groupby(x.bt.dt.to_period("M")).mean().round(1).to_dict())
gecti = s.mean() >= 1.0 and t(s) >= 1.0
print("   KARAR:", "GEÇTİ" if gecti else "KALDI", "(şart: brüt ≥1,0 ve t ≥1,0)")

# --- C
s15 = h[(h.bh == 15) & (h.bt.dt.dayofweek < 5)].copy()
s15["med"] = s15.rng.shift(1).rolling(20).median()
rows = []
for i, r in s15.iterrows():
    if r.bt < BAS or np.isnan(r.med) or r.rng > r.med or r.close == r.open: continue
    if i + 3 >= len(h) or h.at[i + 3, "bt"] - r.bt != pd.Timedelta(hours=3): continue
    yon = -1 if r.close > r.open else 1
    rows.append(dict(zaman=h.at[i + 1, "utc"], ay=r.bt.to_period("M"),
                     stopsuz=yon * (h.at[i + 3, "close"] - h.at[i + 1, "open"]) * 1e4,
                     pip=sim(h, i + 1, yon, 3, 30, 30) - 0.7, kural="C"))
C = pd.DataFrame(rows)
print(f"\nC SINAV  n {len(C)} | stop'suz brüt {C.stopsuz.mean():+.2f} t {t(C.stopsuz):+.2f} | SL30/TP30 net {C.pip.mean():+.2f}")
ek = C[C.zaman < pd.Timestamp("2026-01-01", tz="UTC")]
print(f"   Eki–Ara 2025 (C'nin 'son temiz sınavı'): n {len(ek)} | stop'suz brüt {ek.stopsuz.mean():+.2f} | net {ek.pip.mean():+.2f}")

# --- Birlikte (SL 30)
D = pd.DataFrame([dict(zaman=h.at[i, "utc"], kural="D", pip=sim(h, i, -1, 1, 30, None) - 0.7) for i in x.index])
print()
rapor("C (sınav)", C[["zaman", "kural", "pip"]]); rapor("D (sınav)", D); rapor("C + D (sınav)", pd.concat([C[["zaman", "kural", "pip"]], D]))
