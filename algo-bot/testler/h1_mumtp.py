exec(open('varyasyon_C.py').read().split("yil = A")[0])
def kosB(G, MAL=0.7, sl=30, maxb=3):
    H, L, C, P, n = G['H'], G['L'], G['C'], G['P'], G['n']; out = []
    for q, d in zip(G['q'], G['d']):
        e = C[q]; tp = (H[q] - e) / P if d > 0 else (e - L[q]) / P; tp = tp if tp >= 0.5 else None; r = None
        for j in range(q + 1, min(n, q + maxb + 1)):
            if ((e - L[j]) if d > 0 else (H[j] - e)) / P >= sl: r = -sl; break
            if tp and ((H[j] - e) if d > 0 else (e - L[j])) / P >= tp: r = tp; break
        if r is None: j = min(n - 1, q + maxb); r = (C[j] - e) / P * d
        out.append(r - MAL)
    v = np.array(out); return f'{v.mean():+.2f} (kazanan %{(v>0).mean()*100:.0f})'
print('(B) H1 5 yil:', kosB(A), ' | 2026:', kosB(B), ' | C standart 5y +1.90, 2026 +1.86')
