import numpy as np
import math

m = np.array([[0, 0, 50, 75, 100, 150, 200, 250,
                3, 0,  0.03,   0.05,   0.09,   0.18,   0.15,   0.25, 
                5, 0,  0.05,   0.09,   0.15,   0.28,   0.25,   0.42, 
                10, 0,  0.08,   0.15,   0.27,   0.43,   0.45,   0.74, 
                30, 0,  0.14,   0.29,   0.53,   0.72,   0.88,   1.45, 
                50,  0, 0.16,   0.37,   0.67,   0.87,   1.12,   1.86, 
                100,  0, 0.21,   0.48,   0.89,   1.09,   1.49,   2.48, 
                300,  0, 0.28,   0.68,   1.28,   1.49,   2.15,   3.56, 
                500,  0, 0.32,   0.78,   1.48,   1.69,   2.47,   4.09, 
                1000,  0, 0.37,   0.92,   1.74,   1.98,   2.91,   4.83, 
                3000,  0, 0.47,   1.15,   2.17,   2.46,   3.63,   6.02, 
                5000,  0, 0.51,   1.26,   2.37,   2.7,   3.96,   6.57, 
                10000, 0,  0.58,   1.4,   2.65,   3.04,   4.42,   7.34, 
                30000, 0,  0.68,   1.64,   3.09,   3.59,   5.15,   8.55, 
                50000, 0,  0.73,   1.75,   3.29,   3.85,   5.5,   9.11, 
                100000, 0,  0.8,   1.9,   3.57,   4.21,   5.96,   9.88, 
                300000, 0,  0.92,   2.13,   4.01,   4.8,   6.69,   11.1, 
                500000, 0,  0.97,   2.24,   4.21,   5.08,   7.03,   11.7, 
                1000000, 0,  1.05,   2.39,   4.49,   5.46,   7.49,   12.4, 
                3000000, 0,  1.17,   2.62,   4.93,   6.06,   8.23,   13.7, 
                5000000, 0,  1.22,   2.73,   5.13,   6.35,   8.57,   14.2, 
                10000000, 0,  1.3,   2.88,   5.41,   6.73,   9.03,   15, 
                30000000, 0,  1.42,   3.12,   5.85,   7.35,   9.77,   16.2, 
                100000000, 0,  1.56,   3.38,   6.33,   8.03,   10.6,   17.5, 
                300000000, 0,  1.68,   3.61,   6.77,   8.65,   11.3,   18.8, 
                1000000000, 0,  1.82,   3.87,   7.25,   9.33,   12.1,   20.1
               ]])
m = np.reshape(m, (26, 8))

kvp = int(input('Введите kVp: '))

running = int(input('Сколько раз ввести K: '))
for v in range(running):
    if v != running:
        k = int(input('Введите K: '))
        kvlist = (m[0, :]).tolist()

        for kv in range(len(kvlist)):
            if kvlist[kv] >= kvp:
                break
        kvp1 = kvlist[kv - 1]
        kvp2 = kvlist[kv]

        klist = (m[:, 0]).tolist()

        for i in range(len(klist)):
            if klist[i] >= k:
                break
        k1 = klist[i - 1]
        k2 = klist[i]

        kvp1list = (m[1:, kv - 1:kv]).tolist()
        kvp2list = (m[1:, kv:kv + 1]).tolist()


        def kv_interpolation(kvp1list, kvp2list):
            kvplist = []
            for i in range(len(kvp1list)):
                for k in range(len(kvp2list)):
                    if i == k:
                        d = kvp1list[i][0] - (kvp1list[i][0] - kvp2list[k][0]) * (kvp - kvp1) / (kvp2 - kvp1)
                        kvplist.append(d)
            return kvplist


        def k_interpolation(klist, kv_interpolation):
            for w in range(len(kv_interpolation)):
                if klist.index(k1) == w + 1:
                    thickness = kv_interpolation[w] - (kv_interpolation[w] - kv_interpolation[w + 1]) * (k - k1) / (k2 - k1)
            return thickness


        print(math.ceil((k_interpolation(klist, kv_interpolation(kvp1list, kvp2list)))*100)/100, 'mm Pb')
print(input('Для выхода нажмите Enter...'))
