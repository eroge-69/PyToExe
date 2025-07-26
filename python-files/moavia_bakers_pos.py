# Moavia Bakers POS Software (Bakery Shop Desktop App)
# Features: Item selection, auto total, invoice print, WhatsApp send, language toggle

import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import webbrowser

# --- CONFIGURATION ---
ITEMS = {
    "Cake Slice": 200,
    "Bread Loaf": 150,
    "Cream Roll": 120,
    "Biscuit Pack": 100,
    "Patties": 80
}
LANGUAGES = {
    "English": {
        "title": "Moavia Bakers POS",
        "print": "Print Invoice",
        "send": "Send via WhatsApp",
        "new": "New Order",
        "total": "Total",
        "language": "Language",
    },
    "Roman": {
        "title": "Moavia Bakers POS",
        "print": "Print Bill",
        "send": "WhatsApp se bhejo",
        "new": "Naya Order",
        "total": "Total",
        "language": "Zuban",
    },
    "Urdu": {
        "title": "معاویہ بیکرز POS",
        "print": "بل پرنٹ کریں",
        "send": "واٹس ایپ پر بھیجیں",
        "new": "نیا آرڈر",
        "total": "کل",
        "language": "زبان",
    }
}

bakery_name = "Moavia Bakers"
contact_info = "📞 03005381116\n📍 Al Sadiq Plaza, Jughi Stop, Islamabad"
current_language = "English"

# --- MAIN APPLICATION ---
class POSApp:
    def __init__(self, root):
        self.root = root
        self.root.title(LANGUAGES[current_language]["title"])

        self.items = {}
        self.total = tk.IntVar(value=0)

        self.language_menu = tk.StringVar(value=current_language)
        self.language_menu.trace_add('write', self.update_language)

        self.build_ui()

    def build_ui(self):
        row = 0
        tk.Label(self.root, text=bakery_name, font=("Arial", 16, "bold")).grid(row=row, column=0, columnspan=3)
        row += 1

        for item, price in ITEMS.items():
            tk.Label(self.root, text=f"{item} (Rs. {price})").grid(row=row, column=0, sticky='w')
            qty = tk.IntVar()
            self.items[item] = qty
            tk.Entry(self.root, textvariable=qty, width=5).grid(row=row, column=1)
            row += 1

        tk.Label(self.root, text=LANGUAGES[current_language]['total']).grid(row=row, column=0, sticky='w')
        self.total_label = tk.Label(self.root, textvariable=self.total)
        self.total_label.grid(row=row, column=1, sticky='w')
        row += 1

        tk.Button(self.root, text=LANGUAGES[current_language]['print'], command=self.print_invoice).grid(row=row, column=0)
        tk.Button(self.root, text=LANGUAGES[current_language]['send'], command=self.send_whatsapp).grid(row=row, column=1)
        row += 1

        tk.Button(self.root, text=LANGUAGES[current_language]['new'], command=self.new_order).grid(row=row, column=0)
        tk.OptionMenu(self.root, self.language_menu, *LANGUAGES.keys()).grid(row=row, column=1)

    def update_language(self, *_):
        global current_language
        current_language = self.language_menu.get()
        self.root.destroy()
        main()

    def new_order(self):
        for qty in self.items.values():
            qty.set(0)
        self.total.set(0)

    def calculate_total(self):
        total = 0
        for item, qty in self.items.items():
            total += ITEMS[item] * qty.get()
        self.total.set(total)
        return total

    def build_invoice_text(self):
        now = datetime.now().strftime("%d %B %Y, %I:%M %p")
        lines = [f"{bakery_name}\n{contact_info}\n🕒 {now}\n"]
        for item, qty in self.items.items():
            if qty.get() > 0:
                lines.append(f"{item} x{qty.get()} = Rs. {ITEMS[item] * qty.get()}")
        lines.append(f"---------------------\n{LANGUAGES[current_language]['total']}: Rs. {self.calculate_total()}")
        return "\n".join(lines)

    def print_invoice(self):
        invoice = self.build_invoice_text()
        messagebox.showinfo("Invoice", invoice)

    def send_whatsapp(self):
        invoice = self.build_invoice_text()
        message = invoice.replace("\n", "%0A")
        url = f"https://wa.me/?text={message}"
        webbrowser.open(url)


# --- RUN ---
def main():
    root = tk.Tk()
    app = POSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
