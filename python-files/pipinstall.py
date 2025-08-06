import tkinter as tk
import random

days = ['Pon', 'Wto', 'Śro', 'Czw', 'Pią', 'Sob', 'Nie']
num_days = 7

WIDTH = 600
HEIGHT = 400
MARGIN = 50

def generate_prices(min_price, max_price):
    start_price = random.randint(int(min_price + (max_price - min_price)*0.3), int(min_price + (max_price - min_price)*0.7))
    prices = [start_price]
    for _ in range(1, num_days):
        change = random.uniform(-0.05, 0.05)  # ±5%
        new_price = prices[-1] * (1 + change)
        new_price = max(min(new_price, max_price), min_price)
        prices.append(round(new_price, 2))
    return prices

def price_to_y(price, min_price, max_price):
    return HEIGHT - MARGIN - ((price - min_price) / (max_price - min_price)) * (HEIGHT - 2 * MARGIN)

def draw_chart():
    canvas.delete("all")  # Czyścimy poprzedni wykres

    # Pobierz wartości z pól tekstowych
    try:
        min_price = float(min_price_entry.get())
        max_price = float(max_price_entry.get())
        if min_price >= max_price:
            result_label.config(text="Błąd: min price musi być < max price", fg="red")
            return
    except ValueError:
        result_label.config(text="Błąd: wpisz poprawne liczby", fg="red")
        return

    prices = generate_prices(min_price, max_price)

    # Rysuj osie
    canvas.create_line(MARGIN, HEIGHT - MARGIN, WIDTH - MARGIN, HEIGHT - MARGIN, width=2)  # X
    canvas.create_line(MARGIN, HEIGHT - MARGIN, MARGIN, MARGIN, width=2)                   # Y

    x_spacing = (WIDTH - 2 * MARGIN) / (num_days - 1)

    # Dni na osi X
    for i, day in enumerate(days):
        x = MARGIN + i * x_spacing
        canvas.create_text(x, HEIGHT - MARGIN + 20, text=day)

    # Etykiety cen na osi Y (5 kroków)
    y_steps = 5
    price_step = (max_price - min_price) / y_steps
    y_spacing = (HEIGHT - 2 * MARGIN) / y_steps
    for i in range(y_steps + 1):
        price_label = min_price + i * price_step
        y = HEIGHT - MARGIN - i * y_spacing
        canvas.create_text(MARGIN - 30, y, text=f"{price_label:.0f}")

    # Punkty i linie
    points = []
    for i, price in enumerate(prices):
        x = MARGIN + i * x_spacing
        y = price_to_y(price, min_price, max_price)
        points.append((x, y))
        canvas.create_oval(x-4, y-4, x+4, y+4, fill='blue')
        canvas.create_text(x, y - 15, text=str(price))

    for i in range(len(points) - 1):
        canvas.create_line(points[i][0], points[i][1], points[i+1][0], points[i+1][1], fill='blue', width=2)

    result_label.config(text="Wykres wygenerowany!", fg="green")

# Okno
root = tk.Tk()
root.title("Wykres cen Quities - 7 dni")

# Pola do wpisywania min i max price
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Min price:").grid(row=0, column=0, padx=5)
min_price_entry = tk.Entry(frame, width=10)
min_price_entry.grid(row=0, column=1, padx=5)
min_price_entry.insert(0, "500")

tk.Label(frame, text="Max price:").grid(row=0, column=2, padx=5)
max_price_entry = tk.Entry(frame, width=10)
max_price_entry.grid(row=0, column=3, padx=5)
max_price_entry.insert(0, "600")

generate_btn = tk.Button(root, text="Generuj wykres", command=draw_chart)
generate_btn.pack()

result_label = tk.Label(root, text="")
result_label.pack()

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg='white')
canvas.pack(pady=10)

root.mainloop()
