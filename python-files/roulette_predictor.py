
import tkinter as tk
from tkinter import messagebox

# Red numbers on American roulette
RED_NUMBERS = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
BLACK_NUMBERS = set(range(1, 37)) - RED_NUMBERS
GREEN_NUMBERS = {0, 37}  # 37 represents 00

class RouletteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("American Roulette Predictor")

        self.history = []

        # Entry and Submit
        self.entry = tk.Entry(root, width=10)
        self.entry.pack(pady=5)

        tk.Button(root, text="Submit", command=self.add_number).pack()

        # Output Area
        self.output = tk.Text(root, height=20, width=60)
        self.output.pack(pady=10)

        self.update_display()

    def add_number(self):
        num_str = self.entry.get().strip()
        self.entry.delete(0, tk.END)

        if num_str == "00":
            num = 37
        elif num_str.isdigit():
            num = int(num_str)
        else:
            messagebox.showerror("Invalid Input", "Enter number between 0–36 or 00.")
            return

        if num < 0 or num > 37:
            messagebox.showerror("Out of Range", "Number must be between 0–36 or 00.")
            return

        self.history.append(num)
        if len(self.history) > 50:
            self.history.pop(0)

        self.update_display()

    def update_display(self):
        self.output.delete("1.0", tk.END)

        # Show history
        self.output.insert(tk.END, "Last Spins: " + ", ".join("00" if n == 37 else str(n) for n in self.history[-20:]) + "\n\n")

        # Count frequency
        freq = {}
        for n in self.history:
            freq[n] = freq.get(n, 0) + 1

        hot = sorted(freq.items(), key=lambda x: -x[1])[:5]
        missing = [n for n in range(38) if n not in self.history[-20:]]

        self.output.insert(tk.END, f"🔥 Hot Numbers: {', '.join('00' if n==37 else str(n) for n,_ in hot)}\n")
        self.output.insert(tk.END, f"❌ Missing (Last 20): {', '.join('00' if n==37 else str(n) for n in missing)}\n\n")

        # Show Color Stats
        red = sum(1 for n in self.history if n in RED_NUMBERS)
        black = sum(1 for n in self.history if n in BLACK_NUMBERS)
        green = sum(1 for n in self.history if n in GREEN_NUMBERS)

        self.output.insert(tk.END, f"🟥 Red: {red} | ⬛ Black: {black} | 🟩 Green: {green}\n")

        # Even/Odd
        even = sum(1 for n in self.history if n != 37 and n != 0 and n % 2 == 0)
        odd = sum(1 for n in self.history if n != 37 and n % 2 == 1)
        self.output.insert(tk.END, f"➗ Even: {even} | Odd: {odd}\n")

        # Column (1st, 2nd, 3rd)
        col1 = sum(1 for n in self.history if n in range(1, 37) and (n - 1) % 3 == 0)
        col2 = sum(1 for n in self.history if n in range(1, 37) and (n - 2) % 3 == 0)
        col3 = sum(1 for n in self.history if n in range(1, 37) and n % 3 == 0)
        self.output.insert(tk.END, f"📊 Column 1: {col1} | Column 2: {col2} | Column 3: {col3}\n")

        # Rows
        low = sum(1 for n in self.history if 1 <= n <= 12)
        mid = sum(1 for n in self.history if 13 <= n <= 24)
        high = sum(1 for n in self.history if 25 <= n <= 36)
        self.output.insert(tk.END, f"📈 1–12: {low} | 13–24: {mid} | 25–36: {high}\n")

        # Prediction
        predicted = self.predict_next()
        self.output.insert(tk.END, f"\n🔮 Predicted: {', '.join('00' if n == 37 else str(n) for n in predicted)}\n")

    def predict_next(self):
        # Simple prediction: return top 3 most frequent numbers
        freq = {}
        for n in self.history[-20:]:
            freq[n] = freq.get(n, 0) + 1
        sorted_freq = sorted(freq.items(), key=lambda x: -x[1])
        return [n for n, _ in sorted_freq[:3]]

if __name__ == "__main__":
    root = tk.Tk()
    app = RouletteApp(root)
    root.mainloop()
