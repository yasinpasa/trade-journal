# C Kuralı Algo Bot — Bilgi Dosyası

Son güncelleme: 2026-10-04 · Sahibi: Yasin · Durum: **backtest doğrulandı, demo öncesi**

Bu klasör C kuralının MT5 robotunu, göstergelerini, test kodlarını ve tüm test sonuçlarını tutar. İleride robot geliştirirken önce bu dosya okunur.

---

## 1. Kural (kesin tanım)

```
EURUSD · H1 · sadece hafta içi
Sinyal mumu: MT5 kurum saatiyle 15:00 mumu  (= Londra 13:00, TR yaz 15:00 / kış 16:00)
             (kurum saati = Londra + 2; kurum 00:00 = Londra 22:00)

1) 15:00 mumu kapanınca (16:00) mum boyunu ölç: tepe − dip (pip)
2) Son 20 iş gününün 15:00 mumlarının boylarının ORTANCASI (bugünkü mum hariç)
3) Boy ≤ ortanca  → işlem
   Boy >  ortanca → işlem yok
   Doji (kapanış = açılış) → işlem yok
4) Yön: mum yeşilse SAT, kırmızıysa AL  (mumun tersine)
5) Giriş: mum kapanışı (16:00 açılışı)
6) SL 30 pip · TP 30 pip · en geç 3 mum sonra kapanışta çık (19:00)
   Aynı mumda hem SL hem TP → SL sayılır (testlerde temkinli varsayım)
```

**Benzetme:** Patlatma sonrası sakin geçen vardiya değişiminden sonra zemin eski yerine oturur. Küçük 15:00 mumu "sakin" demek, fiyat da çoğu zaman geri döner.

**Mekanizma:** Kesin değil. İlk düşünce "ABD verisi küçük sürpriz" idi, ama işlemlerin %85'i haber olmayan günlerde. Muhtemel açıklama New York açılışı (16:30 TR) öncesi ve sırasında likidite. TEST EDİLMEDİ.

---

## 2. Test sonuçları (özet)

Maliyet: 0,7 pip/işlem (spread + komisyon, FTMO'ya yakın). Risk %0,5/işlem.

| Test | Veri | İşlem | Net pip/işlem | Not |
|---|---|---|---|---|
| Python keşif | H1 2020-09 → 2025-09 | 648 | +1,90 | t 2,32 |
| Python ileri (görülmemiş) | H1 2026-01 → 2026-09 | 90 | +1,86 | aynı sonuç |
| Python M15 doğrulama | M15 2024-06 → 2026-06 | 255 | +1,95 | |
| **MT5 robot (maliyetli)** | 2020-10 → 2025-09 | 656 | — | 10.000$ → **11.912$ (+%19,1)**, maliyet 808$ |
| MT5 robot (maliyetsiz) | aynı | 656 | — | +2.825$, max düşüş %5,3 |

- Brüt birleşik: 738 işlem, +2,49 pip, t 2,91 (20 kural denendiği için sıkı eşik ~3,0 → sınırda).
- Yıllar (brüt, stop'suz 3s): 2020 −5,0 (27 işlem) · 2021 +3,7 · 2022 +2,7 · 2023 +2,5 · 2024 +3,0 · 2025 +1,9 · 2026 +2,5.
- Haftanın günleri (5 yıl): Pzt +1,2 · Sal +1,1 · Çar +1,8 · Per +2,2 · Cum +4,2 → 5/5 artı. 2026'da karışık (gün başına 12–29 işlem). Gün filtresi YOK.
- Haftada ortalama 2,5 işlem (257 haftanın 11'i boş). Perşembe az (işsizlik başvurusu → mum büyük).
- En büyük düşüş 5 yılda 338 pip = 11R; en uzun kayıp serisi 10.
- Yaklaşık 0,06R/işlem × 130 işlem = **yılda ~8R ≈ %4** (risk %0,5). FTMO %10 hedefi tek başına ≈ 2,5 yıl.

### Saat plasebosu
Aynı kural günün 24 saatinde denendi: 13:00 Londra açık ara en güçlü (+2,48 brüt, t 2,63). Diğer saatler ortalama ~+0,2.

---

## 3. Denenip REDDEDİLEN değişiklikler (tekrar denemeyin)

| Değişiklik | Sonuç | Neden |
|---|---|---|
| Filtresiz (her gün gir) | MT5: +648$ (+%6,5) vs C +1.912$ | Büyük mum günleri 5 yılda −0,76; iki kat işlem = iki kat maliyet |
| Dar SL (10–15) | 2026'da hepsi eksi | Fiyat önce aleyhe gidip dönüyor |
| Dar TP (10–15) | Kazanç kesiliyor | |
| Takip eden stop 10–15 pip | 5y +2,8 ama 2026 −0,1/−1,3 | H1 ölçüm hatası, sahte başarı |
| Takip eden stop 20–30 pip | = takipsiz | Fayda yok |
| İlk ters M15 mumunda çık | −0,67, %68 zarar | İlk M15 mumu %50 ters |
| Kâra geçince ilk ters M15'te çık | +0,92 (C'nin yarısı) | Kazancı erken kesiyor |
| Stop girişe çek @+10 | 2026 +0,98 | Erken başa baş patlıyor |
| Stop girişe/yarıya @+15/+20 | ≈ aynı (+1,8–2,0) | Etkisiz (isteğe bağlı, zararsız) |
| TP = H1 ilk tepe | 5y +1,40, 2026 +0,05 | Tepe çok yakın (ortanca 25 pip) |
| TP = M15 son tepe/dip | +0,30 (%63 kazanan) | Yüksek kazanma oranı yanılgısı |
| TP = 15:00 mumunun ucu | 5y +0,27 (%69 kazanan) | TP ~9 pip, SL 30 |
| 4 saat tutuş | 5y aynı, 2026 daha iyi | Bilerek değiştirilmedi (2026'ya bakıp seçmek olur) |
| Haber filtresi | Yılda ~18 işleme düşer, 2026'da ters | |

**Ders:** Kazancı giriş üretiyor, çıkıştaki ince ayar değil. Yeni ayar aramak = aşırı uydurma riski.

---

## 4. Dosyalar

```
algo-bot/
├─ README.md                      ← bu dosya
├─ mt5/
│  ├─ C_Kurali_EA.mq5             ← ROBOT (Expert Advisor) v1.20
│  └─ C_Kurali_Gosterge.mq5       ← gösterge: ok + SL/TP çizgisi + uyarı + panel (işlem açmaz)
├─ tradingview/
│  └─ C_Kurali.pine               ← Pine v6 strateji (backtest), margin %1
└─ testler/                       ← Python test kodları (aşağıda)
```

### Robot girdileri (C_Kurali_EA v1.20)

| Girdi | Varsayılan | Açıklama |
|---|---|---|
| SinyalSaati | 15 | Kurum saati. Kurum saati Londra+2 değilse DEĞİŞTİR |
| OrtancaGun | 20 | |
| KucukMumFiltresi | true | false = her gün gir (sadece test için) |
| SL_pip / TP_pip | 30 / 30 | |
| TutusMum | 3 | |
| RiskYuzde | 0,5 | Lot otomatik. 0 ise SabitLot |
| SabitLot | 0,10 | |
| TakipMesafe / TakipBaslat | 0 / 0 | Takip eden stop (kapalı). MT5 tik testi bekliyor |
| Pazartesi…Cuma | true | Kapatma önerilmez |
| MaliyetLotBasi | 7,0 | SADECE testte: lot başı gidiş-dönüş maliyet $ bakiyeden çekilir (MT5 test aracında komisyon alanı yok) |
| GercekHesaptaCalis | false | Gerçek hesapta işlem açmaz. Bilerek kilitli |
| Sihirli | 20261003 | Magic number |

Robot davranışı: her yeni H1 mumunda bakar; açık pozisyon varsa ve 3 mum dolduysa kapatır; tek pozisyon; takip açıksa her tikte stopu sadece lehe taşır. Testte bitişte Bülten'e `C_Kurali_EA OZET: ... islem | toplam maliyet ... $ | maliyet sonrasi bakiye ... $` yazar.

### MT5'e kurulum
1. MetaEditor → Dosya → Yeni → Expert Advisor (şablon) → ad `C_Kurali_EA` → Bitir.
2. İçini sil, `mt5/C_Kurali_EA.mq5` içeriğini yapıştır → Derle (F7) → `0 errors`.
3. Gösterge için aynı yol, "Özel Gösterge" seçilir.

### MT5 backtest ayarları
- Uzman C_Kurali_EA · EURUSD · H1 · 2020.10.01 – 2025.09.26
- Modelleme: 1 dakikalık OHLC (takip eden stop için: Gerçek tiklere dayalı her tik)
- Matematiksel hesaplamalar KULLANMA (fiyat verisi yok)
- Teminat 10.000 USD, 1:100
- Optimizasyon tablosunda "Sonuç" ve "Kâr" sütunları maliyeti (para çekmeyi) GÖSTERMEZ → satıra çift tıkla, tek test, Bülten'deki OZET satırına bak.

---

## 5. Test kodları (algo-bot/testler)

Hepsi Python 3 + pandas/numpy. Temel kodlar `kod/2026-10-03/` içinde (tarti.py, ileri_C.py, varyasyon_C.py); testler bunları `exec` ile okur, aynı klasöre kopyalanmalı. Veri yolları dosya içinde.

| Dosya | Ne test eder |
|---|---|
| ea_sim.py | Robotun Python eşi: 10.000$, %0,5 risk, bileşik, $ / düşüş % |
| hergun_C.py | Filtresiz her gün + haftanın günleri |
| takip_C.py | Takip eden stop ızgarası (H1, temkinli) |
| m15_cikis.py | İlk ters M15 çıkışı (+ M15'ten H1 sinyal üretimi) |
| m15_cikis2.py | Kâra geçince ilk ters M15 |
| stop_tasi.py | Stop girişe / yarıya çekme |
| tepe_tp.py | TP = H1 ilk tepe, 3 ve 4 saat |
| m15_tepe.py, h1_mumtp.py | TP = M15 son tepe/dip, TP = 15:00 mumunun ucu |

Veri dosyaları (MT5 dışa aktarım, sekme ayrılmış, kurum saati):
- EURUSD_H1_202009210000_202509260000.csv (5 yıl)
- EURUSD_H1_202601020000_202609290000.csv (2026)
- EURUSD_M15_202406040000_202606171930.csv (Drive'da)

---

## 6. Açık işler / yol haritası

1. **Demo canlı:** robotu demo hesapta EURUSD H1 grafiğinde çalıştır (Algo Trading açık, bilgisayar 15:00–19:00 açık ya da VPS). En az 6–12 ay kayıt.
2. **Ekim–Aralık 2025 testi** (henüz görülmemiş tek dönem): MT5'te 2025.10.01 – 2025.12.31 tek test.
3. **Takip eden stop MT5 tik testi:** 4 ayar (0/0, 10/0, 10/15, 20/15), "Gerçek tiklere dayalı her tik", 2020.10 – 2026.09.
4. **Risk yönetimi:** FTMO kuralları (günlük %5, toplam %10) için lot, günlük/haftalık kayıp limiti, kayıp serisi planı (5 yılda en uzun seri 10).
5. **İkinci bağımsız avantaj:** C tek başına yılda ~%4. FTMO için yanına 2–3 bağımsız küçük kural gerek.
6. Karar bekleyen: ileri test kuralı (a) demo tek başına t≥2,7, (b) 6–12 ay aynı işaret. Claude (b) önerdi.

## 7. Bilinen riskler / uyarılar
- Kurumun saat dilimi farklıysa SinyalSaati yanlış mumu seçer. Kontrol: haftanın ilk mumu Pazartesi 00:00 olmalı.
- Yeni hesap verilerinde SPREAD sütunu 0 görünüyor; gerçek maliyet 0 değildir.
- Robot kodu Claude tarafından yazıldı, Yasin MT5'te derleyip backtest etti (2026-10-04): sonuçlar Python ile uyumlu.
- 2026-10-04 ekran görüntüsünde robot dışı 5 lot, stop'suz bir pozisyon görüldü — kaynağı belirsiz, kontrol edilecek.
