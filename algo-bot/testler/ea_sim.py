# C_Kurali_EA'nin Python esi: 10.000$, islem basi risk %0,5 (SL 30 pip = 1R), bilesik, maliyet 0,7 pip.
exec(open('hergun_C.py').read().split("for ad, G in")[0])
def rapor(ad, X):
    v = sim(X, 30, 30, 3)                    # net pip
    bak = 10000.0; tepe = bak; ddmax = 0; kaz = kay = 0.0; seri = 0; mseri = 0
    for p in v:
        k = bak * 0.005 * p / 30; bak += k
        kaz += max(k, 0); kay += max(-k, 0)
        tepe = max(tepe, bak); ddmax = max(ddmax, (tepe - bak) / tepe)
        seri = seri + 1 if p < 0 else 0; mseri = max(mseri, seri)
    yil = (X['df'].kurum.iloc[-1] - X['df'].kurum.iloc[0]).days / 365.25
    print(f'{ad:34s} islem {len(v):5d} | net kar {bak-10000:+8.0f}$ ({(bak/10000-1)*100:+5.1f}%) | yillik {((bak/10000)**(1/yil)-1)*100:+4.1f}% '
          f'| max dusus %{ddmax*100:4.1f} | kazanan %{(v>0).mean()*100:.0f} | kar faktoru {kaz/kay:.2f} | en uzun kayip serisi {mseri}')
for ad, G in (('5 yil (2020-10..2025-09)', A), ('2026 (Oca-Eyl)', B)):
    rapor(f'{ad} C (filtre acik)', G)
    rapor(f'{ad} HER GUN (filtre kapali)', hergun(G))
