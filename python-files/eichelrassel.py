import matplotlib.pyplot as plt
import numpy as np
import random

# QBasic Simulation mit matplotlib
plt.figure(figsize=(6, 6))
plt.axis("equal")
plt.axis("off")

x_values = np.arange(1, 100, 0.022)

for x in x_values:
    y = (130 + x) * np.sin(x) + 155 + x
    a = (100 - x) * np.cos(x) + 165
    color_value = 10 * random.random()**3 + 8
    plt.plot(a, y, marker=".", color=plt.cm.hsv(color_value / 18), markersize=2)

plt.show()
