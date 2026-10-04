# D geliştirme: sadece mekanizmadan (ECB fix 13:15 Londra öncesi dolar talebi) türetilen denemeler.
# Veri 2020-09..2025-09 (keşif). 2025-10 sonrası dokunulmaz. Brüt pip, stop'suz.
import warnings; warnings.filterwarnings("ignore")
from yukle import *
d = yukle().sort_values("utc").reset_index(drop=True)
d = d[d.utc.dt.dayofweek < 5].reset_index(drop=True)
d["gun"] = d.lon.dt.date
t = lambda v: v.mean() / (v.std() / np.sqrt(len(v)))
g = d.pivot_table(index="gun", columns="lh", values=["open", "close", "high", "low"])
def pencere(bas, son):           # Londra bas:00 açılışından son:00 açılışına (= son-1 mumunun kapanışı) SAT
    return -(g["close"][son - 1] - g["open"][bas]) * 1e4
def yaz(ad, x):
    x = x.dropna(); yy = x.groupby(pd.to_datetime(x.index).year).mean()
    print(f"{ad:42s} n {len(x):5d} brüt {x.mean():+5.2f} t {t(x):+5.2f} σ {x.std():4.1f} | artı yıl {(yy[yy.index>2020]>0).sum()}/5")
print("== 1) ZAMANLAMA: ne zaman girmeli? (çıkış hep 13:00 = fix'ten 15 dk önce son H1 kapanışı)")
for b in (9, 10, 11, 12):
    yaz(f"SAT {b}:00 → 13:00", pencere(b, 13))
yaz("SAT 11:00 → 12:00 (sadece önceki saat)", pencere(11, 12))
yaz("SAT 12:00 → 14:00 (fix'i ve sonrasını da tut)", pencere(12, 14))

base = pencere(12, 13)
print("\n== 2) MEKANİZMA TESTİ: ECB fix'in OLMADIĞI günler (TARGET tatili) — etki kaybolmalı")
gunler = pd.to_datetime(pd.Series(base.index))
def target_tatil(t):
    from datetime import date, timedelta
    y = t.year
    a = y % 19; b = y // 100; c = y % 100; dd = b // 4; e = b % 4; f = (b + 8) // 25; gg = (b - f + 1) // 3
    h = (19 * a + b - dd - gg + 15) % 30; i = c // 4; k = c % 4; l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451; ay = (h + l - 7 * m + 114) // 31; gn = ((h + l - 7 * m + 114) % 31) + 1
    paskalya = date(y, ay, gn)
    tat = {date(y, 1, 1), paskalya - timedelta(2), paskalya + timedelta(1), date(y, 5, 1), date(y, 12, 25), date(y, 12, 26)}
    return t.date() in tat
tt = gunler.apply(target_tatil).values
yaz("Fix VAR günler (normal)", base[~tt]); yaz("Fix YOK günler (TARGET tatili)", base[tt])

print("\n== 3) OYNAKLIK: etki sakin mi hareketli günlerde mi büyük? (dünkü günlük aralığa göre 3 dilim)")
gunluk = (g["high"].max(axis=1) - g["low"].min(axis=1)) * 1e4
dun = gunluk.shift(1).rolling(20).mean()
q = pd.qcut(dun, 3, labels=["sakin", "orta", "hareketli"])
for k in ["sakin", "orta", "hareketli"]: yaz(f"12→13 SAT, {k}", base[q == k])

print("\n== 4) AY SONU (son iş günü) — fix akışı büyük olmalı")
ix = pd.to_datetime(pd.Series(base.index))
ayson = ((ix + pd.offsets.BDay(1)).dt.month != ix.dt.month).values
yaz("ay sonu", base[ayson]); yaz("diğer", base[~ayson])

print("\n== 5) SABAH HAREKETİ: 07→12 EUR yükseldiyse mi düştüyse mi?")
sabah = (g["close"][11] - g["open"][7]) * 1e4
yaz("sabah EUR yükseldi", base[sabah > 0]); yaz("sabah EUR düştü", base[sabah < 0])
print("\nDeneme sayısı bu dosyada: 6 zamanlama + 2 tatil + 3 oynaklık + 2 ay sonu + 2 sabah = 15")
