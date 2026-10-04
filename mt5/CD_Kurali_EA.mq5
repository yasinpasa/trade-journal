//+------------------------------------------------------------------+
//| CD_Kurali_EA.mq5                                                  |
//| C + D kurallari tek robotta (Expert Advisor) - backtest ve demo.  |
//|                                                                    |
//| D: her is gunu LONDRA 12:00 H1 mumu acilisinda SAT, mum           |
//|    kapanisinda (Londra 13:00) kapat. SL 30 pip (guvenlik).        |
//|    (ECB fix'i 13:15 Londra oncesi dolar talebi - hipotez)         |
//| C: kurum saatiyle 15:00 H1 mumu kapaninca, mum boyu son 20 is     |
//|    gununun ayni saat mumlarinin ortancasindan kucuk/esitse mumun  |
//|    TERSINE gir. SL 30 / TP 30, en gec 3 mum sonra kapat.          |
//| Iki kural zamanda cakismaz (D 13:00 Londra'da kapanir, C en erken |
//| 13:00 Londra'da acilir; ayni tikte once D kapanir).               |
//|                                                                    |
//| Python testi 2020-09..2025-09 (maliyet 0,7 pip, %0,5 risk):       |
//|   C 647 islem +1,88 pip | D 1302 islem +0,78 pip |                |
//|   birlikte 1949 islem +1,14 pip, yillik ~+%7,6, max dusus ~%6,3   |
//+------------------------------------------------------------------+
#property copyright   "Yasin"
#property version     "1.00"
#property description "C + D: 12:00 Londra SAT (D) + 15:00 kurum kucuk mum tersine (C)."

#include <Trade\Trade.mqh>

input group "Kurallar"
input bool   C_Acik           = true;    // C kurali acik
input bool   D_Acik           = true;    // D kurali acik
input group "C kurali"
input int    C_SinyalSaati    = 15;      // C sinyal mumu (KURUM saati; 15 = Londra 13:00)
input int    OrtancaGun       = 20;      // Ortanca icin gecmis gun sayisi
input double C_TP_pip         = 30;      // C hedef (pip)
input int    C_TutusMum       = 3;       // C en gec kac mum sonra kapat
input group "D kurali"
input int    D_LondraSaati    = 12;      // D mumu (LONDRA saati). Plasebo icin baska saat dene
input int    KurumNYFarki     = 7;       // Kurum saati = New York + bu kadar (cogu MT5 kurumu: 7)
input group "Ortak"
input double SL_pip           = 30;      // Stop (pip), iki kural
input double RiskYuzde        = 0.5;     // Islem basi risk (% bakiye). 0 ise SabitLot
input double SabitLot         = 0.10;    // RiskYuzde=0 iken lot
input double MaliyetLotBasi   = 7.0;     // SADECE TESTTE: lot basi gidis-donus maliyet $ (komisyon+spread ~0,7 pip)
input bool   GercekHesaptaCalis = false; // false: gercek hesapta islem acmaz (sadece demo/test)
input long   Sihirli          = 20261004;// Magic number: C = bu sayi, D = bu sayi + 1

CTrade   trade;
datetime sonBar = 0;
datetime cGirisZamani = 0;
datetime dGirisZamani = 0;
double   pip;
double   maliyetC = 0, maliyetD = 0;
int      islemC = 0, islemD = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
   pip = (_Digits == 5 || _Digits == 3) ? 10 * _Point : _Point;
   trade.SetDeviationInPoints(20);
   if(_Period != PERIOD_H1)
      Print("CD_Kurali_EA: UYARI - grafik H1 degil. Robot H1 mumlarina gore calisir, test H1 ile yapilmali.");
   if(!GercekHesaptaCalis && AccountInfoInteger(ACCOUNT_TRADE_MODE) == ACCOUNT_TRADE_MODE_REAL)
      Print("CD_Kurali_EA: GERCEK hesap. GercekHesaptaCalis=false oldugu icin islem acilmayacak.");
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
//| Ozet: her kuralin net sonucu (kar + komisyon + swap - test maliyeti)|
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(!MQLInfoInteger(MQL_TESTER))
      return;
   double karC = 0, karD = 0;
   int kazC = 0, kazD = 0;
   HistorySelect(0, TimeCurrent() + 86400);
   for(int i = 0; i < HistoryDealsTotal(); i++)
     {
      ulong d = HistoryDealGetTicket(i);
      if(HistoryDealGetInteger(d, DEAL_ENTRY) != DEAL_ENTRY_OUT) continue;
      long mg = HistoryDealGetInteger(d, DEAL_MAGIC);
      double k = HistoryDealGetDouble(d, DEAL_PROFIT) + HistoryDealGetDouble(d, DEAL_COMMISSION) + HistoryDealGetDouble(d, DEAL_SWAP);
      if(mg == Sihirli)          { karC += k; if(k > 0) kazC++; }
      else if(mg == Sihirli + 1) { karD += k; if(k > 0) kazD++; }
     }
   PrintFormat("CD OZET  C: %d islem | brut %.0f $ | maliyet %.0f $ | NET %.0f $ | kazanan (maliyet oncesi) %%%.0f",
               islemC, karC, maliyetC, karC - maliyetC, islemC > 0 ? 100.0 * kazC / islemC : 0);
   PrintFormat("CD OZET  D: %d islem | brut %.0f $ | maliyet %.0f $ | NET %.0f $ | kazanan (maliyet oncesi) %%%.0f",
               islemD, karD, maliyetD, karD - maliyetD, islemD > 0 ? 100.0 * kazD / islemD : 0);
   PrintFormat("CD OZET  TOPLAM: %d islem | NET %.0f $ | son bakiye %.2f $",
               islemC + islemD, karC + karD - maliyetC - maliyetD, AccountInfoDouble(ACCOUNT_BALANCE));
  }

//+------------------------------------------------------------------+
//| Yaz saati yardimcilari                                            |
//+------------------------------------------------------------------+
datetime AyinPazari(int yil, int ay, int kacinci)   // kacinci: 1,2.. = n. pazar; -1 = son pazar
  {
   MqlDateTime s;
   s.year = yil; s.mon = ay; s.day = 1; s.hour = 0; s.min = 0; s.sec = 0;
   datetime ilk = StructToTime(s);
   MqlDateTime t; TimeToStruct(ilk, t);
   int ilkPazar = 1 + (7 - t.day_of_week) % 7;
   if(kacinci > 0)
      return(ilk + (ilkPazar - 1 + 7 * (kacinci - 1)) * 86400);
   MqlDateTime s2 = s; s2.mon = (ay == 12) ? 1 : ay + 1; s2.year = (ay == 12) ? yil + 1 : yil;
   int gunSay = (int)((StructToTime(s2) - ilk) / 86400);
   int son = ilkPazar;
   while(son + 7 <= gunSay) son += 7;
   return(ilk + (son - 1) * 86400);
  }

// New York yaz saati: Mart 2. pazar - Kasim 1. pazar (gun duzeyinde)
bool NYYaz(datetime t)
  {
   MqlDateTime d; TimeToStruct(t, d);
   return(t >= AyinPazari(d.year, 3, 2) && t < AyinPazari(d.year, 11, 1));
  }

// Ingiltere yaz saati: Mart son pazar - Ekim son pazar
bool UKYaz(datetime t)
  {
   MqlDateTime d; TimeToStruct(t, d);
   return(t >= AyinPazari(d.year, 3, -1) && t < AyinPazari(d.year, 10, -1));
  }

// Kurum saatinden Londra saatine: Londra = kurum - (KurumNYFarki - 5 + NYyaz - UKyaz)
int LondraSaati(datetime kurum)
  {
   datetime ny = kurum - KurumNYFarki * 3600;
   int fark = KurumNYFarki - 5 + (NYYaz(ny) ? 1 : 0) - (UKYaz(ny) ? 1 : 0);
   MqlDateTime d; TimeToStruct(kurum - fark * 3600, d);
   return(d.hour);
  }

//+------------------------------------------------------------------+
double Ortanca(double &a[], int adet)
  {
   ArraySort(a);
   if(adet % 2 == 1)
      return(a[adet / 2]);
   return((a[adet / 2 - 1] + a[adet / 2]) / 2.0);
  }

ulong Pozisyon(long magic)
  {
   for(int i = PositionsTotal() - 1; i >= 0; i--)
     {
      ulong tk = PositionGetTicket(i);
      if(tk == 0) continue;
      if(PositionGetString(POSITION_SYMBOL) == _Symbol && PositionGetInteger(POSITION_MAGIC) == magic)
         return(tk);
     }
   return(0);
  }

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

// Test maliyeti: MT5 testinde komisyon alani yok -> bakiyeden cek (sadece Strateji Test Araci)
double MaliyetCek(double lot)
  {
   if(!MQLInfoInteger(MQL_TESTER) || MaliyetLotBasi <= 0)
      return(0);
   double m = NormalizeDouble(lot * MaliyetLotBasi, 2);
   if(m > 0 && TesterWithdrawal(m))
      return(m);
   return(0);
  }

bool IslemIzni()
  {
   return(GercekHesaptaCalis || AccountInfoInteger(ACCOUNT_TRADE_MODE) != ACCOUNT_TRADE_MODE_REAL);
  }

//+------------------------------------------------------------------+
void OnTick()
  {
   datetime t0 = iTime(_Symbol, PERIOD_H1, 0);
   if(t0 == 0 || t0 == sonBar)
      return;
   sonBar = t0;   // yeni H1 mumu acildi; bir onceki mum (shift 1) kapandi
   int h1 = PeriodSeconds(PERIOD_H1);

   // 1) Suresi dolanlari kapat (once D, sonra C)
   ulong dTk = Pozisyon(Sihirli + 1);
   if(dTk != 0 && dGirisZamani > 0 && t0 >= dGirisZamani + h1)
     { trade.SetExpertMagicNumber(Sihirli + 1); trade.PositionClose(dTk); dTk = 0; }
   ulong cTk = Pozisyon(Sihirli);
   if(cTk != 0 && cGirisZamani > 0 && t0 >= cGirisZamani + C_TutusMum * h1)
     { trade.SetExpertMagicNumber(Sihirli); trade.PositionClose(cTk); cTk = 0; }

   MqlDateTime dt0; TimeToStruct(t0, dt0);

   // 2) D: yeni acilan mum Londra D saati mi? -> SAT
   if(D_Acik && dTk == 0 && cTk == 0 && IslemIzni()
      && dt0.day_of_week >= 1 && dt0.day_of_week <= 5 && LondraSaati(t0) == D_LondraSaati)
     {
      double lot = LotHesapla();
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      trade.SetExpertMagicNumber(Sihirli + 1);
      bool ok = trade.Sell(lot, _Symbol, bid, NormalizeDouble(bid + SL_pip * pip, _Digits), 0, "D SAT");
      if(ok) { dGirisZamani = t0; islemD++; maliyetD += MaliyetCek(lot); }
      PrintFormat("CD_Kurali_EA %s: D SAT %.2f lot %s", TimeToString(t0), lot, (ok ? "acildi" : "HATA"));
     }

   // 3) C: az once kapanan mum C sinyal mumu mu?
   if(!C_Acik || cTk != 0 || Pozisyon(Sihirli + 1) != 0)
      return;
   MqlRates r[];
   ArraySetAsSeries(r, true);
   int adet = CopyRates(_Symbol, PERIOD_H1, 1, 24 * (OrtancaGun * 2 + 10), r);
   if(adet < 50)
      return;
   MqlDateTime dt;
   TimeToStruct(r[0].time, dt);
   if(dt.hour != C_SinyalSaati || dt.day_of_week < 1 || dt.day_of_week > 5)
      return;

   double boylar[];
   ArrayResize(boylar, OrtancaGun);
   int bulunan = 0;
   for(int i = 1; i < adet && bulunan < OrtancaGun; i++)
     {
      MqlDateTime d2;
      TimeToStruct(r[i].time, d2);
      if(d2.hour == C_SinyalSaati && d2.day_of_week >= 1 && d2.day_of_week <= 5)
        {
         boylar[bulunan] = (r[i].high - r[i].low) / pip;
         bulunan++;
        }
     }
   if(bulunan < OrtancaGun)
      return;
   double med = Ortanca(boylar, OrtancaGun);
   double boy = (r[0].high - r[0].low) / pip;
   if(r[0].close == r[0].open || boy > med)
      return;                                   // doji veya buyuk mum -> islem yok
   if(!IslemIzni())
      return;

   double lot = LotHesapla();
   bool al = (r[0].close < r[0].open);          // kirmizi mum -> AL, yesil mum -> SAT
   bool ok;
   trade.SetExpertMagicNumber(Sihirli);
   if(al)
     {
      double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
      ok = trade.Buy(lot, _Symbol, ask, NormalizeDouble(ask - SL_pip * pip, _Digits),
                     NormalizeDouble(ask + C_TP_pip * pip, _Digits), "C AL");
     }
   else
     {
      double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);
      ok = trade.Sell(lot, _Symbol, bid, NormalizeDouble(bid + SL_pip * pip, _Digits),
                      NormalizeDouble(bid - C_TP_pip * pip, _Digits), "C SAT");
     }
   if(ok) { cGirisZamani = t0; islemC++; maliyetC += MaliyetCek(lot); }
   PrintFormat("CD_Kurali_EA %s: C mum %.1f pip, ortanca %.1f -> %s %.2f lot %s",
               TimeToString(r[0].time), boy, med, (al ? "AL" : "SAT"), lot, (ok ? "acildi" : "HATA"));
  }
//+------------------------------------------------------------------+
