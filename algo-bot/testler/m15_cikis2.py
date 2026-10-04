exec(open('m15_cikis.py').read().split("def kosu")[0])
def kosu2(esik=0.0, sl=30, maxm=12):
    out = []; sure = []; tip = []
    for q, d in zip(qs, ds):
        e = C[q]; r = None; aktif = False
        for j in range(q + 1, min(len(C), q + 1 + maxm)):
            if (e - L[j] if d > 0 else H[j] - e) / P >= sl: r = -sl; tip.append('SL'); break
            kar = (C[j] - e) / P * d
            if aktif and np.sign(C[j] - O[j]) == -d: r = kar; tip.append('ters mum'); break
            if not aktif and kar > esik: aktif = True
        if r is None:
            j = min(len(C) - 1, q + maxm); r = (C[j] - e) / P * d; tip.append('sure')
        out.append(r - MAL); sure.append(j - q)
    v = np.array(out); eq = np.cumsum(v); dd = (np.maximum.accumulate(eq) - eq).max()
    tp_ = pd.Series(tip).value_counts(normalize=True).mul(100).round(0).to_dict()
    return v, dict(N=len(v), net=round(v.mean(), 2), t=round(v.mean() / (v.std(ddof=1) / np.sqrt(len(v))), 2),
                   kazanan=f'{(v>0).mean()*100:.0f}%', ort_kazanc=round(v[v>0].mean(), 1), ort_kayip=round(v[v<0].mean(), 1),
                   dusus=round(dd), ort_sure_dk=round(np.mean(sure) * 15), cikis=tp_)
exec(open('m15_cikis.py').read().split("rows = {}")[0].split("def kosu")[1].join(["def kosu", ""]) if False else "")
rows = {}
v0, rows['C standart (SL30 TP30 3s)'] = (lambda: None, None)
# C standart yeniden (ayni kod)
src = open('m15_cikis.py').read(); exec("def kosu" + src.split("def kosu")[1].split("rows = {}")[0])
rows['C standart (SL30 TP30 3s)'] = kosu('sure', 30, 30, 12)[1]
va, rows['(a) Yasin: kara gecince ilk ters M15, 3s'] = kosu2(0, 30, 12)
rows['(b) ayni, en gec 12s'] = kosu2(0, 30, 48)[1]
rows['(c) +10 pip kara gecince, 3s'] = kosu2(10, 30, 12)[1]
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print(pd.DataFrame(rows).T.to_string())
yil = pd.to_datetime(T[qs]).year
print('\n(a) yil yil:', pd.Series(va).groupby(yil).agg(['count', 'mean']).round(2).T.to_string())
