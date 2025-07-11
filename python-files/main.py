import numpy as np
import matplotlib.pyplot as plt
import warnings

# Uyarıları kapat (overflow, invalid value vs.)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Sabit parametre c
c = 3j + 2

# Fraktal denklemi: f(a, c) = a^2 + c
def f(a, c):
    return a**2 + c

# İterasyon fonksiyonu: z_{n+1} = f(sin(z^3) + z/c, c)
def iterate(z, c):
    inner = np.sin(z**3) + z / c
    return f(inner, c)

# Fraktalı hesaplayan fonksiyon
def compute_fractal(x_min, x_max, y_min, y_max, width, height, c, max_iter=100, threshold=10):
    image = np.zeros((height, width))
    for ix in range(width):
        for iy in range(height):
            x = x_min + (x_max - x_min) * ix / (width - 1)
            y = y_min + (y_max - y_min) * iy / (height - 1)
            z = complex(x, y)

            for n in range(max_iter):
                try:
                    z = iterate(z, c)
                except:
                    break  # overflow, sıfıra bölme vs. durumlarda kır

                if abs(z) > threshold:
                    image[iy, ix] = n
                    break
            else:
                image[iy, ix] = max_iter  # Uçmadıysa max iterasyon ver

    return image

# Zoom yapılabilen ana fonksiyon
def zoomable_fractal():
    # Başlangıç koordinatları ve çözünürlük
    x_min, x_max = -4, 4
    y_min, y_max = -4, 4
    zoom_factor = 0.5
    width, height = 800, 800

    fig, ax = plt.subplots()
    plt.title("Fireworks of Star Set (Left click for zoom)")

    image = compute_fractal(x_min, x_max, y_min, y_max, width, height, c)
    img = ax.imshow(image, extent=(x_min, x_max, y_min, y_max),
                    cmap="twilight_shifted", origin="lower")
    plt.colorbar(img, ax=ax, label="Divergence speed")

    # Zoom fonksiyonu
    def on_click(event):
        nonlocal x_min, x_max, y_min, y_max, width, height

        if event.button == 1 and event.inaxes:  # Sol tıkla zoom in
            x_range = x_max - x_min
            y_range = y_max - y_min
            center_x = event.xdata
            center_y = event.ydata

            x_min = center_x - x_range * zoom_factor / 2
            x_max = center_x + x_range * zoom_factor / 2
            y_min = center_y - y_range * zoom_factor / 2
            y_max = center_y + y_range * zoom_factor / 2

            # Her zoom'da çözünürlüğü artır
            width += 200
            height += 200

            print(f"🔍 Zoom: x=[{x_min:.3f}, {x_max:.3f}] y=[{y_min:.3f}, {y_max:.3f}]")

            image = compute_fractal(x_min, x_max, y_min, y_max, width, height, c)
            img.set_data(image)
            img.set_extent((x_min, x_max, y_min, y_max))
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("button_press_event", on_click)
    plt.show()

# Programı başlat
zoomable_fractal()
