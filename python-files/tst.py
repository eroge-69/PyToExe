import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


from scipy.signal import argrelextrema
from statsmodels.nonparametric.smoothers_lowess import lowess


'''
parameters for optimization
e1, e2, fit(deg), peaks(order), extra(order)
'''
n = 3.42
e1 = 600
e2 = 1400

files = glob.glob('*.csv')
result = pd.DataFrame()

for file in files:

    df = pd.read_csv(file, sep=';', header=None)
    m = (df[0] > e1) & (df[0] < e2)
    df = df.loc[m].reset_index(drop=True)

    x = np.linspace(e1, e2, num=len(df[0]))
    fit = np.poly1d(np.polyfit(df[0], df[1], deg=3))
    y = fit(x)

#    bg = lowess(df[1], df[0], frac=0.35)
#    x = bg[:, 0]
#    y = bg[:, 1]

    df[1] = df[1] - y

    plt.plot(df[0], df[1])
    plt.plot(x, y - np.mean(y), ls='--')

    peaks = argrelextrema(df.values, np.greater, order=10)[0]
    peaks = df[0].loc[peaks]

    t = np.diff(peaks)

    t = 10000 / t
    h = t / 2 / n
    h = np.mean(h)

#    extra = argrelextrema(y, np.greater, order=500)[0]
#    extra = x[extra]

#    t1 = extra * 2

#    t1 = 10000 / t1
#    h1 = t1 / 2 / n
#    h1 = np.mean(h1)

    result = result.append({'file': file,
                            'n': np.round(h, decimals=2)},
#                            'n': np.round(h - h1, decimals=2),
#                            'n+': np.round(h1, decimals=2)},
                            ignore_index=True).dropna()

#result['file'] = result['file'].str[:-6]
#result = result.groupby('file').mean().reset_index().round(2)

result.to_csv('result_tst.txt', sep='\t')
