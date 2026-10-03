//+------------------------------------------------------------------+
//| C_Kurali_EA.mq5                                                   |
//| C kurali robotu (Expert Advisor) - backtest ve demo icin.         |
//| Kurum saatiyle 15:00 H1 mumu kapaninca: mum boyu son 20 is gununun|
//| ayni saat mumlarinin ortancasindan kucuk/esitse mumun TERSINE gir.|
//| SL 30 / TP 30 pip, en gec 3 mum sonra kapat.                      |
//| KucukMumFiltresi=false -> her gun girer ("her gun" testi).        |
//| Test (2026-10-03 Oturum 5/6): C 5 yil +1,90 net; her gun +0,59.   |
//+------------------------------------------------------------------+
#property copyright   "Yasin"
#property version     "1.00"
#property description "C kurali: 15:00 mumu kucukse tersine. SL30 / TP30 / 3 saat."

#include <Trade\Trade.mqh>

input int    SinyalSaati      = 15;      // Sinyal mumu saati (kurum saati)
input int    OrtancaGun       = 20;      // Ortanca icin gecmis gun sayisi
input bool   KucukMumFiltresi = true;    // true = C kurali, false = her gun gir
input double SL_pip           = 30;      // Stop (pip)
input double TP_pip           = 30;      // Hedef (pip)
input int    TutusMum         = 3;       // En gec kac mum sonra kapat
input double RiskYuzde        = 0.5;     // Islem basi risk (% bakiye). 0 ise SabitLot
input double SabitLot         = 0.10;    // RiskYuzde=0 iken lot
input bool   Pazartesi        = true;
input bool   Sali             = true;
input bool   Carsamba         = true;
input bool   Persembe         = true;
input bool   Cuma             = true;
input double MaliyetLotBasi   = 7.0;     // SADECE TESTTE: lot basi gidis-donus maliyet $ (komisyon+spread, FTMO ~7)
input bool   GercekHesaptaCalis = false; // false: gercek hesapta islem acmaz (sadece demo/test)
input long   Sihirli          = 20261003;// Magic number

CTrade   trade;
datetime sonBar = 0;
datetime girisBarZamani = 0;
double   pip;
double   topMaliyet = 0;
int      islemSay = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   pip = (_Digits == 5 || _Digits == 3) ? 10 * _Point : _Point;
   trade.SetExpertMagicNumber(Sihirli);
   trade.SetDeviationInPoints(20);
   if(!GercekHesaptaCalis && AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
      Print("C_Kurali_EA: GERCEK hesap. GercekHesaptaCalis=false oldugu icin islem acilmayacak.");
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(MQLInfoInteger(MQL_TESTER))
      PrintFormat("C_Kurali_EA OZET: %d islem | toplam maliyet %.2f $ | maliyet sonrasi bakiye %.2f $",
                  islemSay, topMaliyet, AccountInfoDouble(ACCOUNT_BALANCE));
  }

//+------------------------------------------------------------------+
bool GunAcik(int dow)
  {
   if(dow == 1) return(Pazartesi);
   if(dow == 2) return(Sali);
   if(dow == 3) return(Carsamba);
   if(dow == 4) return(Persembe);
   if(dow == 5) return(Cuma);
   return(false);
  }

//+------------------------------------------------------------------+
double Ortanca(double &a[], int adet)
  {
   ArraySort(a);
   if(adet % 2 == 1)
      return(a[adet / 2]);
   return((a[adet / 2 - 1] + a[adet / 2]) / 2.0);
  }

//+------------------------------------------------------------------+
//| Pozisyon bu robota ait mi, varsa ticket dondur                    |
//+------------------------------------------------------------------+
ulong BenimPozisyon()
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == Sihirli)
         return(tk);
     }
   return(0);
  }

//+------------------------------------------------------------------+
double LotHesapla()
  {
   double lot = SabitLot;
   if(RiskYuzde > 0)
     {
      double tickDeger = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
      double tickBoy   = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
      double pipDeger  = (tickBoy > 0) ? tickDeger * pip / tickBoy : 0;   // 1 lot icin 1 pip degeri
      if(pipDeger > 0)
         lot = AccountInfoDouble(ACCOUNT_BALANCE) * RiskYuzde / 100.0 / (SL_pip * pipDeger);
     }
   double adim = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   double mn   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double mx   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   lot = MathFloor(lot / adim) * adim;
   return(MathMax(mn, MathMin(mx, lot)));
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime t0 = iTime(_Symbol, PERIOD_H1, 0);
   if(t0 == 0 || t0 == sonBar)
      return;
   sonBar = t0;   // yeni H1 mumu acildi; bir onceki mum (shift 1) kapandi

   // 1) Sure doldu mu? Giris mumu + TutusMum saat sonra kapat (sinyal mumundan 3 mum sonraki kapanis).
   ulong tk = BenimPozisyon();
   if(tk != 0 && girisBarZamani > 0 && t0 >= girisBarZamani + TutusMum * PeriodSeconds(PERIOD_H1))
     {
      trade.PositionClose(tk);
      tk = 0;
     }
   if(tk != 0)
      return;

   // 2) Az once kapanan mum sinyal mumu mu?
   MqlRates r[];
   ArraySetAsSeries(r, true);
   int adet = CopyRates(_Symbol, PERIOD_H1, 1, 24 * (OrtancaGun * 2 + 10), r);
   if(adet < 50)
      return;
   MqlDateTime dt;
   TimeToStruct(r[0].time, dt);
   if(dt.hour != SinyalSaati || dt.day_of_week < 1 || dt.day_of_week > 5)
      return;
   if(!GunAcik(dt.day_of_week))
      return;

   // 3) Onceki OrtancaGun adet ayni saat, hafta ici mumlarin boyu
   double boylar[];
   ArrayResize(boylar, OrtancaGun);
   int bulunan = 0;
   for(int i = 1; i < adet && bulunan < OrtancaGun; i++)
     {
      MqlDateTime d2;
      TimeToStruct(r[i].time, d2);
      if(d2.hour == SinyalSaati && d2.day_of_week >= 1 && d2.day_of_week <= 5)
        {
         boylar[bulunan] = (r[i].high - r[i].low) / pip;
         bulunan++;
        }
     }
   if(bulunan < OrtancaGun)
      return;
   double med = Ortanca(boylar, OrtancaGun);
   double boy = (r[0].high - r[0].low) / pip;
   if(r[0].close == r[0].open)
      return;                                   // doji
   if(KucukMumFiltresi && boy > med)
      return;                                   // mum buyuk -> islem yok

   // 4) Guvenlik kilidi
   if(!GercekHesaptaCalis && AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
      return;

   // 5) Giris: yesil mum -> SAT, kirmizi mum -> AL
   double lot = LotHesapla();
   bool al = (r[0].close < r[0].open);
   bool ok;
   if(al)
     {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      ok = trade.Buy(lot, _Symbol, ask,
                     NormalizeDouble(ask - SL_pip * pip, _Digits),
                     NormalizeDouble(ask + TP_pip * pip, _Digits), "C AL");
     }
   else
     {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      ok = trade.Sell(lot, _Symbol, bid,
                      NormalizeDouble(bid + SL_pip * pip, _Digits),
                      NormalizeDouble(bid - TP_pip * pip, _Digits), "C SAT");
     }
   if(ok)
     {
      girisBarZamani = t0;
      islemSay++;
      // MT5 testinde komisyon alani yok: maliyeti bakiyeden cekerek uygula (sadece Strateji Test Araci)
      if(MQLInfoInteger(MQL_TESTER) && MaliyetLotBasi > 0)
        {
         double m = NormalizeDouble(lot * MaliyetLotBasi, 2);
         if(m > 0 && TesterWithdrawal(m))
            topMaliyet += m;
        }
     }
   PrintFormat("C_Kurali_EA %s: mum %.1f pip, ortanca %.1f pip -> %s %.2f lot %s",
               TimeToString(r[0].time), boy, med, (al ? "AL" : "SAT"), lot, (ok ? "acildi" : "HATA"));
  }
//+------------------------------------------------------------------+
