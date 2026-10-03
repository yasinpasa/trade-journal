exec(open('tarti.py').read().split("out = []")[0])
c13 = np.where((df.lh.values == 13) & (df.lon.dt.dayofweek.values < 5))[0]
rg = pd.Series((H[c13] - L[c13]) / P); med = rg.rolling(20).median().shift(1).values
q = c13[~np.isnan(med) & (rg.values <= med)]; d = -np.sign(C[q] - O[q]); q = q[d != 0]
wk_all = df.lon.dt.to_period('W').unique()
cnt = pd.Series(df.lon.values[q]).dt.to_period('W').value_counts().reindex(wk_all, fill_value=0)
cnt = cnt.iloc[5:-1]  # ilk 20 gun isinma + son yarim hafta haric
print('hafta sayisi', len(cnt), 'ort', round(cnt.mean(),2))
print(cnt.value_counts().sort_index().to_string())
