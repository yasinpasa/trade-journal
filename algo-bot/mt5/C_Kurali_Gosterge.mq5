//+------------------------------------------------------------------+
//| C_Kurali.mq5                                                      |
//| C kurali: kurum saatiyle 15:00 H1 mumu, son 20 gunun ayni saat    |
//| mumlarinin ortanca boyundan kucuk/esitse mumun tersine giris.     |
//| SL 30 pip, TP 30 pip, en gec 3 mum sonra kapanisla cikis.         |
//| Test: 2026-10-03 Yasin Oturum 5 (5 yil +1,90 net, 2026 +1,86 net) |
//| Not: Islem acmaz. Sadece isaretler, cizer, uyarir, sayar.         |
//+------------------------------------------------------------------+
#property copyright   "Yasin"
#property version     "1.00"
#property description "C kurali: 15:00 mumu kucukse tersine. SL30 / TP30 / 3 saat."
#property indicator_chart_window
#property indicator_buffers 2
#property indicator_plots   2
#property indicator_label1  "C AL"
#property indicator_type1   DRAW_ARROW
#property indicator_color1  clrDodgerBlue
#property indicator_width1  3
#property indicator_label2  "C SAT"
#property indicator_type2   DRAW_ARROW
#property indicator_color2  clrOrangeRed
#property indicator_width2  3

input int      SinyalSaati      = 15;                      // Sinyal mumu saati (kurum saati)
input int      OrtancaGun       = 20;                      // Ortanca icin gecmis gun sayisi
input double   SL_pip           = 30;                      // Stop (pip)
input double   TP_pip           = 30;                      // Hedef (pip)
input int      TutusMum         = 3;                       // En gec kac mum sonra cikis
input double   Maliyet_pip      = 0.7;                     // Istatistik icin maliyet (spread+komisyon)
input datetime IstatistikBasi   = D'2026.01.01 00:00';     // Panel istatistigi bu tarihten itibaren
input bool     Uyari            = true;                    // Sinyalde ekran uyarisi
input bool     TelefonBildirimi = false;                   // Sinyalde MT5 telefon bildirimi
input int      CizgiSayisi      = 30;                      // Son kac sinyalin giris/SL/TP cizgisi

double BufAl[], BufSat[];
string PFX = "CKURAL_";
datetime sonUyari = 0;
double pip;

//+------------------------------------------------------------------+
int OnInit()
  {
   if(_Period != PERIOD_H1)
     {
      Alert("C_Kurali sadece H1 grafikte calisir.");
      return(INIT_PARAMETERS_INCORRECT);
     }
   pip = (_Digits == 5 || _Digits == 3) ? 10 * _Point : _Point;
   SetIndexBuffer(0, BufAl, INDICATOR_DATA);
   SetIndexBuffer(1, BufSat, INDICATOR_DATA);
   PlotIndexSetInteger(0, PLOT_ARROW, 233);
   PlotIndexSetInteger(1, PLOT_ARROW, 234);
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(1, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   IndicatorSetString(INDICATOR_SHORTNAME, "C Kurali");
   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   ObjectsDeleteAll(0, PFX);
   Comment("");
  }

//+------------------------------------------------------------------+
double Ortanca(const double &a[], int bas, int adet)
  {
   double t[];
   ArrayResize(t, adet);
   for(int k = 0; k < adet; k++)
      t[k] = a[bas + k];
   ArraySort(t);
   if(adet % 2 == 1)
      return(t[adet / 2]);
   return((t[adet / 2 - 1] + t[adet / 2]) / 2.0);
  }

//+------------------------------------------------------------------+
void Cizgi(string ad, datetime t1, datetime t2, double fiyat, color renk, ENUM_LINE_STYLE stil)
  {
   if(ObjectFind(0, ad) < 0)
      ObjectCreate(0, ad, OBJ_TREND, 0, t1, fiyat, t2, fiyat);
   ObjectSetInteger(0, ad, OBJPROP_TIME, 0, t1);
   ObjectSetInteger(0, ad, OBJPROP_TIME, 1, t2);
   ObjectSetDouble(0, ad, OBJPROP_PRICE, 0, fiyat);
   ObjectSetDouble(0, ad, OBJPROP_PRICE, 1, fiyat);
   ObjectSetInteger(0, ad, OBJPROP_COLOR, renk);
   ObjectSetInteger(0, ad, OBJPROP_STYLE, stil);
   ObjectSetInteger(0, ad, OBJPROP_RAY_RIGHT, false);
   ObjectSetInteger(0, ad, OBJPROP_SELECTABLE, false);
   ObjectSetInteger(0, ad, OBJPROP_BACK, true);
  }

//+------------------------------------------------------------------+
//| Sonuc (pip, maliyet haric). Her mumda once SL sonra TP; ayni      |
//| mumda ikisi -> SL. Hicbiri olmazsa TutusMum sonra kapanis.        |
//+------------------------------------------------------------------+
double Sonuc(int i, int yon, const double &high[], const double &low[], const double &close[])
  {
   double e = close[i];
   for(int j = i + 1; j <= i + TutusMum; j++)
     {
      double aleyhe = (yon > 0) ? (e - low[j]) / pip : (high[j] - e) / pip;
      double lehe   = (yon > 0) ? (high[j] - e) / pip : (e - low[j]) / pip;
      if(aleyhe >= SL_pip)
         return(-SL_pip);
      if(lehe >= TP_pip)
         return(TP_pip);
     }
   return((close[i + TutusMum] - e) / pip * yon);
  }

//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
   if(rates_total < 100)
      return(0);
   // Sadece yeni mumda (veya ilk yuklemede) bastan hesapla.
   if(prev_calculated == rates_total)
      return(rates_total);

   ArrayInitialize(BufAl, EMPTY_VALUE);
   ArrayInitialize(BufSat, EMPTY_VALUE);
   ObjectsDeleteAll(0, PFX);

   // 1) Hafta ici, sinyal saatindeki tum mumlar (kapanmis olanlar).
   int    idx[];
   double boy[];
   ArrayResize(idx, 0, 4000);
   ArrayResize(boy, 0, 4000);
   MqlDateTime dt;
   for(int i = 0; i < rates_total - 1; i++)   // son mum hala olusuyor, alinmaz
     {
      TimeToStruct(time[i], dt);
      if(dt.hour == SinyalSaati && dt.day_of_week >= 1 && dt.day_of_week <= 5)
        {
         int k = ArraySize(idx);
         ArrayResize(idx, k + 1, 4000);
         ArrayResize(boy, k + 1, 4000);
         idx[k] = i;
         boy[k] = (high[i] - low[i]) / pip;
        }
     }

   // 2) Sinyaller + istatistik.
   int    sinyal[];  ArrayResize(sinyal, 0, 2000);
   int    yonler[];  ArrayResize(yonler, 0, 2000);
   int    N = 0, kazanan = 0;
   double toplam = 0;
   double sonOrtanca = 0, sonBoy = 0;
   int    sonDurum = 0;          // 0 yok, 1 AL, -1 SAT, 2 buyuk mum
   datetime sonSaat = 0;

   int m = ArraySize(idx);
   for(int k = OrtancaGun; k < m; k++)
     {
      int i = idx[k];
      double med = Ortanca(boy, k - OrtancaGun, OrtancaGun);
      sonOrtanca = med; sonBoy = boy[k]; sonSaat = time[i];
      if(boy[k] > med || close[i] == open[i])
        {
         sonDurum = (boy[k] > med) ? 2 : 0;
         continue;
        }
      int yon = (close[i] > open[i]) ? -1 : 1;   // yesil -> SAT, kirmizi -> AL
      sonDurum = yon;
      if(yon > 0)
         BufAl[i] = low[i] - 5 * pip;
      else
         BufSat[i] = high[i] + 5 * pip;

      int s = ArraySize(sinyal);
      ArrayResize(sinyal, s + 1, 2000);
      ArrayResize(yonler, s + 1, 2000);
      sinyal[s] = i;
      yonler[s] = yon;

      if(time[i] >= IstatistikBasi && i + TutusMum < rates_total - 1)
        {
         double r = Sonuc(i, yon, high, low, close) - Maliyet_pip;
         N++;
         toplam += r;
         if(r > 0)
            kazanan++;
        }
     }

   // 3) Son sinyallerin giris / SL / TP cizgileri.
   int ns = ArraySize(sinyal);
   for(int s = MathMax(0, ns - CizgiSayisi); s < ns; s++)
     {
      int i = sinyal[s];
      int yon = yonler[s];
      datetime t1 = time[i] + PeriodSeconds();
      datetime t2 = time[i] + (TutusMum + 1) * PeriodSeconds();
      double e = close[i];
      string n = PFX + IntegerToString((long)time[i]);
      Cizgi(n + "_G", t1, t2, e, clrSilver, STYLE_SOLID);
      Cizgi(n + "_SL", t1, t2, e - yon * SL_pip * pip, clrRed, STYLE_DOT);
      Cizgi(n + "_TP", t1, t2, e + yon * TP_pip * pip, clrLime, STYLE_DOT);
     }

   // 4) Uyari: az once kapanan mum sinyalse.
   int son = rates_total - 2;
   if(ns > 0 && sinyal[ns - 1] == son && time[son] != sonUyari && prev_calculated > 0)
     {
      sonUyari = time[son];
      int yon = yonler[ns - 1];
      string msj = StringFormat("C kurali %s: %s @ %s | SL %s | TP %s | en gec %s'de kapat",
                                _Symbol, (yon > 0 ? "AL" : "SAT"),
                                DoubleToString(close[son], _Digits),
                                DoubleToString(close[son] - yon * SL_pip * pip, _Digits),
                                DoubleToString(close[son] + yon * TP_pip * pip, _Digits),
                                TimeToString(time[son] + (TutusMum + 1) * PeriodSeconds(), TIME_MINUTES));
      if(Uyari)
         Alert(msj);
      if(TelefonBildirimi)
         SendNotification(msj);
     }

   // 5) Panel.
   string durum;
   if(sonDurum == 1)       durum = "AL sinyali";
   else if(sonDurum == -1) durum = "SAT sinyali";
   else if(sonDurum == 2)  durum = "Mum buyuk -> islem yok";
   else                    durum = "Doji -> islem yok";
   double ort = (N > 0) ? toplam / N : 0;
   Comment(StringFormat(
      "C KURALI  (%02d:00 mumu, SL %.0f / TP %.0f / %d saat)\n"
      "Son %02d:00 mumu: %s  boy %.1f pip  ortanca %.1f pip  -> %s\n"
      "Istatistik (%s'den beri): %d islem | net ort %+.2f pip | kazanan %%%.0f | toplam %+.0f pip\n"
      "Test referansi: 5 yil +1,90 | 2026 +1,86 net pip/islem",
      SinyalSaati, SL_pip, TP_pip, TutusMum,
      SinyalSaati, TimeToString(sonSaat, TIME_DATE), sonBoy, sonOrtanca, durum,
      TimeToString(IstatistikBasi, TIME_DATE), N, ort, (N > 0 ? 100.0 * kazanan / N : 0), toplam));

   return(rates_total);
  }
//+------------------------------------------------------------------+
