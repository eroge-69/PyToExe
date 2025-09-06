import numpy as np
import matplotlib.pyplot as plt
import scipy as sp


# Define model function to be used to fit to the data above:
# Lumilass G9 messen mit FC1 und speichern. Auf Fläche normieren und in LumilassGreenGeraete.xls kopieren
# LumilassGreenGeraete.txt gererieren, komma durch punkt ersetzen
# E ergänzen und device_count anpassen
# SigmasQ sind die Werte die in der FLUOSP Software mit devDeltas verwendet werden
def gauss(x, *p):
    A, mu, sigma = p
    return A*np.exp(-(x-mu)**2/(2.*sigma**2))


data = np.loadtxt("LumilassGreen1Geraet.txt",skiprows=1)

peak_count = 3
device_count = 1
peak_pos = [[475,505],[530,560],[575,600]]
E = [1]


#for i in range(device_count):
#    plt.plot(data[:,2*i], data[:,2*i+1])
#plt.show()


b = np.zeros((peak_count, device_count))

for i in range(device_count):
    x = data[:,2*i]
    y = data[:,2*i+1]
    print('sn{0}'.format(E[i]))
    for j in range(peak_count):
        k1 = np.searchsorted(x,peak_pos[j][0], side='left')
        k2 = np.searchsorted(x,peak_pos[j][1], side='right')+1
        p0 = [0.001, 0.5*(peak_pos[j][0]+peak_pos[j][1]), 0.5*(peak_pos[j][1]-peak_pos[j][0])]
        coeff, var_matrix = sp.optimize.curve_fit(gauss, x[k1:k2],y[k1:k2],p0=p0)
        b[j,i] = coeff[2]**2
        print(coeff)

sigmas = b.mean(axis=0)-0.5*b.mean()
peaks = b.mean(axis=1)-0.5*b.mean()
c = 6.742299631
sigmasq = np.sqrt(sigmas+c)


print("Peaks: {0}".format(peaks))
print("Sigmas: {0}".format(sigmas))
print("SigmasQ: {0}".format(sigmasq))

## Open a file in write mode
output_file = open("LumilassRes.txt", "w")

## Redirect print output to the file
print("SigmasQ: {0}".format(sigmasq), file=output_file)

## Close the file
output_file.close()
