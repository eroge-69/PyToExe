
import tkinter as tk
import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class NasdaqSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("가상 나스닥 차트 시뮬레이터")

        self.cash = 10000
        self.position = 0
        self.price = 100.0
        self.prices = [self.price]

        self.label_info = tk.Label(root, text=f"현금: ${self.cash} | 보유 수량: {self.position}")
        self.label_info.pack()

        self.fig, self.ax = plt.subplots(figsize=(6, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.button_buy = tk.Button(root, text="매수", command=self.buy)
        self.button_buy.pack(side="left", padx=10)
        self.button_sell = tk.Button(root, text="매도", command=self.sell)
        self.button_sell.pack(side="left", padx=10)

        self.update_price()

    def update_price(self):
        change = random.uniform(-1, 1)
        self.price += change
        self.price = round(self.price, 2)
        self.prices.append(self.price)

        if len(self.prices) > 100:
            self.prices.pop(0)

        self.ax.clear()
        self.ax.plot(self.prices, label="NASDAQ")
        self.ax.set_title("가상 나스닥 차트")
        self.ax.legend()
        self.canvas.draw()

        self.label_info.config(text=f"현금: ${self.cash:.2f} | 보유 수량: {self.position} | 현재가: ${self.price}")

        self.root.after(1000, self.update_price)

    def buy(self):
        if self.cash >= self.price:
            self.cash -= self.price
            self.position += 1

    def sell(self):
        if self.position > 0:
            self.cash += self.price
            self.position -= 1

if __name__ == "__main__":
    root = tk.Tk()
    app = NasdaqSimulator(root)
    root.mainloop()
