import numpy as np
import matplotlib.pyplot as plot


figure = plot.figure(figsize=(8, 4.125))

l=np.pi

x=np.linspace(-1, 1, 500)
y=x #f(x)

a_0 = 1/l*np.trapezoid(y, x, dx=1/100)

y_fourier = np.zeros(len(x)) + a_0/2


for n in range(1, 100):

    figure.clear()

    axis = figure.subplots()

    axis.plot(x, y_fourier)
    axis.grid()
    plot.draw()
    plot.pause(0.05)


    a_n =1/l*np.trapezoid(y*np.cos(np.pi*n*x/l), x, dx =1/100)
    b_n =1/l*np.trapezoid(y*np.sin(np.pi*n*x/l), x, dx =1/100)

    fourier_term = a_n*np.cos(np.pi*n*x/l) + b_n*np.sin(np.pi*n*x/l)

    y_fourier = np.add(fourier_term, y_fourier)

 
    plot.show()
