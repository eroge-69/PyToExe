import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

def plot_lituus(a):
    theta = np.linspace(0.01, 10 * np.pi, 1000)
    r = a / np.sqrt(theta)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def update_plot(val):
    a = scale.get()
    x, y = plot_lituus(a)
    line.set_data(x, y)
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

root = tk.Tk()
root.title("Кривая литуус с динамическим параметром a")

fig, ax = plt.subplots(figsize=(6,6))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Начальное значение a
a0 = 1
x, y = plot_lituus(a0)
line, = ax.plot(x, y, label='r = a / sqrt(θ)')
ax.set_xlabel('x')
ax.set_ylabel('y')
ax.set_title('Кривая литуус')
ax.grid(True)
ax.axis('equal')
ax.legend()

# Ползунок для изменения a
scale = tk.Scale(root, from_=0.1, to=5.0, resolution=0.01, orient=tk.HORIZONTAL,
                 label='Параметр a', length=400, command=update_plot)
scale.set(a0)
scale.pack(side=tk.BOTTOM, pady=10)

root.mainloop()
