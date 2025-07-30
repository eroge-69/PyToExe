import tkinter as tk
from tkinter import messagebox
import requests
import webbrowser
import threading
import time
import random
import winsound

class TicketChecker:
    def __init__(self, master):
        self.master = master
        self.master.title("Ticket Resale Alert")
        self.running = False
        self.check_count = 0

        # UI
        tk.Label(master, text="Etkinlik Sayfası (Ticketmaster):").grid(row=0, column=0, sticky="w")
        self.url_entry = tk.Entry(master, width=60)
        self.url_entry.grid(row=0, column=1)

        tk.Label(master, text="Bilet Adedi:").grid(row=1, column=0, sticky="w")
        self.qty_entry = tk.Entry(master)
        self.qty_entry.grid(row=1, column=1, sticky="w")

        tk.Label(master, text="Saniyede bir kontrol (örnek: 30):").grid(row=2, column=0, sticky="w")
        self.delay_entry = tk.Entry(master)
        self.delay_entry.grid(row=2, column=1, sticky="w")

        self.start_button = tk.Button(master, text="Başlat", command=self.start_checking)
        self.start_button.grid(row=3, column=0, pady=10)

        self.stop_button = tk.Button(master, text="Durdur", command=self.stop_checking, state="disabled")
        self.stop_button.grid(row=3, column=1, pady=10)

        self.status_label = tk.Label(master, text="Durum: Beklemede")
        self.status_label.grid(row=4, column=0, columnspan=2)

    def start_checking(self):
        self.event_url = self.url_entry.get().strip()
        qty = self.qty_entry.get().strip()
        delay = self.delay_entry.get().strip()

        if not self.event_url or not qty.isdigit() or not delay.isdigit():
            messagebox.showerror("Hata", "Lütfen tüm alanları doğru girin.")
            return

        self.qty = int(qty)
        self.delay = int(delay)
        self.event_id = self.extract_event_id(self.event_url)

        if not self.event_id:
            messagebox.showerror("Hata", "Etkinlik ID alınamadı.")
            return

        self.api_url = f"https://www.ticketmaster.ie/api/quickpicks/{self.event_id}/resale?qty={self.qty}&offset=0&limit=20"

        self.running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.url_entry.config(state="disabled")
        self.qty_entry.config(state="disabled")
        self.delay_entry.config(state="disabled")
        self.status_label.config(text="Durum: Takip Başladı")

        threading.Thread(target=self.check_loop, daemon=True).start()

    def stop_checking(self):
        self.running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.url_entry.config(state="normal")
        self.qty_entry.config(state="normal")
        self.delay_entry.config(state="normal")
        self.status_label.config(text=f"Durum: Durduruldu ({self.check_count} deneme yapıldı)")

    def extract_event_id(self, url):
        parts = url.split("/")
        if parts and len(parts) >= 1:
            return parts[-1]
        return None

    def check_loop(self):
        while self.running:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                r = requests.get(self.api_url, headers=headers, timeout=10)
                if r.status_code == 200:
                    data = r.json()
                    offers = data.get("resale_offers", [])
                    self.check_count += 1
                    if offers:
                        winsound.PlaySound("SystemAsterisk", winsound.SND_ALIAS)
                        webbrowser.open(self.event_url)
                        messagebox.showinfo("🎟️ Bilet Bulundu!", f"{len(offers)} adet resale bilet bulundu!")
                        self.stop_checking()
                        return
                    self.status_label.config(text=f"Durum: {self.check_count}. deneme - bilet yok")
            except Exception as e:
                self.status_label.config(text=f"Durum: Hata - {e}")

            wait = self.delay + random.randint(-5, 5)
            time.sleep(max(1, wait))


if __name__ == "__main__":
    root = tk.Tk()
    app = TicketChecker(root)
    root.mainloop()
