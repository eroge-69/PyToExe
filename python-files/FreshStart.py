import customtkinter as ctk
import tkinter.messagebox as messagebox
import json
import os
from datetime import datetime

DATA_FILE = "stop_smoking_data.json"

ACHIEVEMENTS = [
    {"name": "Gratulace! Každý velký začátek začíná prvním krokem.", "days": 1, "xp": 20, "icon": "🔥"},
    {"name": "Držíš to! Každý den je vítězství.", "days": 2, "xp": 15, "icon": "💨"},
    {"name": "Tvá síla roste – pokračuj!", "days": 3, "xp": 25, "icon": "💪"},
    {"name": "Stavíš pevný základ nové životní cesty.", "days": 4, "xp": 30, "icon": "🧱"},
    {"name": "Pět dní bez cigarety – jsi na správné cestě!", "days": 5, "xp": 40, "icon": "🌟"},
    {"name": "Každý den znamená lepší zdraví a větší svobodu.", "days": 6, "xp": 50, "icon": "🎯"},
    {"name": "Týden bez cigarety – obrovský krok k lepšímu já!", "days": 7, "xp": 70, "icon": "🏆"},
    {"name": "Tvá vůle je silnější než kdy dřív.", "days": 10, "xp": 90, "icon": "🧠"},
    {"name": "Dvě týdny bez kouře – to je úžasný úspěch!", "days": 14, "xp": 120, "icon": "🔥🔥"},
    {"name": "Tři týdny změny – pokračuj v tom!", "days": 21, "xp": 160, "icon": "📅"},
    {"name": "Měsíc bez cigarety znamená lepší život a více energie.", "days": 30, "xp": 250, "icon": "🎉"},
    {"name": "45 dní vítězství, tvé tělo ti děkuje.", "days": 45, "xp": 320, "icon": "🎯"},
    {"name": "Dva měsíce bez kouře – skvělý výkon!", "days": 60, "xp": 400, "icon": "💥"},
    {"name": "Stále silnější, stále lepší.", "days": 75, "xp": 500, "icon": "🧱🔥"},
    {"name": "Tři měsíce – jsi opravdový vítěz.", "days": 90, "xp": 600, "icon": "💎"},
    {"name": "100 dní bez cigarety, nový začátek života.", "days": 100, "xp": 700, "icon": "🌈"},
    {"name": "Čtyři měsíce – udržuješ změnu a sílíš.", "days": 120, "xp": 850, "icon": "🎈"},
    {"name": "Půl roku bez kouře je něco, na co můžeš být hrdý.", "days": 150, "xp": 1000, "icon": "⚡"},
    {"name": "Šest měsíců – jsi příklad pro ostatní.", "days": 180, "xp": 1200, "icon": "👑"},
    {"name": "200 dní vítězství a svobody.", "days": 200, "xp": 1500, "icon": "🚀"},
    {"name": "Devět měsíců, jsi téměř na cílové rovince.", "days": 270, "xp": 2000, "icon": "🛡️"},
    {"name": "300 dní bez cigarety – nepřestávej!", "days": 300, "xp": 2500, "icon": "🧠🔥"},
    {"name": "Rok bez cigarety, nový život začíná dnes.!", "days": 365, "xp": 3000, "icon": "🚭🏆"},
]

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "start_time": None,
            "days_without_cigs": 0,
            "xp": 0,
            "wallet": 0,
            "total_saved": 0,
            "purchased_items": [],
            "achievements_unlocked": []
        }
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

class StopSmokingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("Stop Smoking Tracker")
        self.geometry("700x500")
        self.resizable(False, False)

        self.data = load_data()
        self.cig_price = 145

        self.timer_running = False
        self.timer_id = None

        self.frame_main = ctk.CTkFrame(self)
        self.frame_main.pack(fill="both", expand=True, padx=15, pady=15)

        self.lbl_days = ctk.CTkLabel(self.frame_main, text="", font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_days.pack(pady=(5, 10))

        self.lbl_xp = ctk.CTkLabel(self.frame_main, text="", font=ctk.CTkFont(size=16))
        self.lbl_xp.pack()

        self.lbl_wallet = ctk.CTkLabel(self.frame_main, text="", font=ctk.CTkFont(size=16))
        self.lbl_wallet.pack(pady=(5,15))

        self.lbl_timer = ctk.CTkLabel(self.frame_main, text="Odvykání: Neaktivní", font=ctk.CTkFont(size=18))
        self.lbl_timer.pack(pady=10)

        frame_buttons = ctk.CTkFrame(self.frame_main)
        frame_buttons.pack(pady=10)

        self.btn_start = ctk.CTkButton(frame_buttons, text="Start odvykání", command=self.start_timer)
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = ctk.CTkButton(frame_buttons, text="Stop odvykání", command=self.stop_timer, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=10)

        self.btn_reset_timer = ctk.CTkButton(frame_buttons, text="Resetovat odvykání", command=self.reset_timer)
        self.btn_reset_timer.grid(row=0, column=2, padx=10)

        self.btn_achievements = ctk.CTkButton(self.frame_main, text="Zobrazit achievementy", command=self.show_achievements)
        self.btn_achievements.pack(pady=7)

        self.btn_shop = ctk.CTkButton(self.frame_main, text="Obchod", command=self.show_shop)
        self.btn_shop.pack(pady=7)

        self.btn_purchased = ctk.CTkButton(self.frame_main, text="Zakoupené věci", command=self.show_purchased)
        self.btn_purchased.pack(pady=7)

        self.btn_reset_all = ctk.CTkButton(self.frame_main, text="Resetovat všechna data", command=self.reset_all)
        self.btn_reset_all.pack(pady=15)

        # Bind Ctrl+D for manual day add
        self.bind_all("<Control-d>", self.manual_add_day)

        self.update_ui()

    def update_ui(self):
        days = self.data.get("days_without_cigs", 0)
        xp = self.data.get("xp", 0)
        wallet = self.data.get("wallet", 0)
        total_saved = self.data.get("total_saved", 0)
        level = xp // 100

        self.lbl_days.configure(text=f"Dny bez cigarety: {days}")
        self.lbl_xp.configure(text=f"XP: {xp} | Level: {level}")
        self.lbl_wallet.configure(text=f"Aktuální peněženka: {wallet} Kč\nCelkem ušetřeno: {total_saved} Kč")

        if self.timer_running:
            self.lbl_timer.configure(text="Odvykání běží...")
        else:
            if self.data["start_time"]:
                self.lbl_timer.configure(text="Odvykání zastaveno")
            else:
                self.lbl_timer.configure(text="Odvykání: Neaktivní")

    def start_timer(self):
        if not self.data["start_time"]:
            self.data["start_time"] = datetime.now().isoformat()
            save_data(self.data)
        self.timer_running = True
        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.update_ui()

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.btn_start.configure(state="normal")
            self.btn_stop.configure(state="disabled")
            self.update_ui()

    def reset_timer(self):
        answer = messagebox.askyesno("Reset timer", "Opravdu chcete resetovat odvykání? Data o dnech a XP zůstanou.")
        if answer:
            self.stop_timer()
            self.data["start_time"] = None
            save_data(self.data)
            self.update_ui()

    def reset_all(self):
        answer = messagebox.askyesno("Reset všech dat", "Opravdu chcete vymazat všechna data včetně historie a obchodu?")
        if answer:
            self.stop_timer()
            self.data = {
                "start_time": None,
                "days_without_cigs": 0,
                "xp": 0,
                "wallet": 0,
                "total_saved": 0,
                "purchased_items": [],
                "achievements_unlocked": []
            }
            save_data(self.data)
            self.update_ui()

    def show_achievements(self):
        ach_win = ctk.CTkToplevel(self)
        ach_win.title("Achievementy")
        ach_win.geometry("600x800")

        frame = ctk.CTkFrame(ach_win)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        for ach in ACHIEVEMENTS:
            unlocked = ach["name"] in self.data.get("achievements_unlocked", [])
            text = f"{ach['icon']} {ach['name']} - Odemykáno po {ach['days']} dnech"
            label = ctk.CTkLabel(frame, text=text, fg_color="green" if unlocked else "gray")
            label.pack(anchor="w", pady=3)

    def check_achievements(self):
        days = self.data.get("days_without_cigs", 0)
        unlocked = self.data.get("achievements_unlocked", [])
        changed = False
        for ach in ACHIEVEMENTS:
            if days >= ach["days"] and ach["name"] not in unlocked:
                unlocked.append(ach["name"])
                self.data["xp"] += ach["xp"]
                changed = True
        if changed:
            self.data["achievements_unlocked"] = unlocked
            save_data(self.data)

    def show_shop(self):
        shop_win = ctk.CTkToplevel(self)
        shop_win.title("Obchod")
        shop_win.geometry("350x300")

        ctk.CTkLabel(shop_win, text="Zadej název položky a cenu:", font=ctk.CTkFont(size=16)).pack(pady=10)

        frame_input = ctk.CTkFrame(shop_win)
        frame_input.pack(pady=10)

        self.entry_item_name = ctk.CTkEntry(frame_input, placeholder_text="Název položky")
        self.entry_item_name.grid(row=0, column=0, padx=5)

        self.entry_item_price = ctk.CTkEntry(frame_input, placeholder_text="Cena (Kč)")
        self.entry_item_price.grid(row=0, column=1, padx=5)

        btn_add = ctk.CTkButton(shop_win, text="Přidat do zakoupených", command=self.add_manual_item)
        btn_add.pack(pady=10)

    def add_manual_item(self):
        name = self.entry_item_name.get().strip()
        price_text = self.entry_item_price.get().strip()

        if not name:
            messagebox.showerror("Chyba", "Zadej název položky.")
            return
        if not price_text.isdigit():
            messagebox.showerror("Chyba", "Cena musí být číslo.")
            return

        price = int(price_text)

        if self.data["wallet"] < price:
            messagebox.showerror("Chyba", "Nemáš dost peněz v peněžence.")
            return

        self.data["wallet"] -= price
        self.data["purchased_items"].append({"name": name, "price": price})
        save_data(self.data)
        self.update_ui()
        messagebox.showinfo("Úspěch", f"Položka '{name}' zakoupena za {price} Kč.")

    def show_purchased(self):
        pur_win = ctk.CTkToplevel(self)
        pur_win.title("Zakoupené věci")
        pur_win.geometry("350x300")

        frame = ctk.CTkFrame(pur_win)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        if not self.data["purchased_items"]:
            ctk.CTkLabel(frame, text="Zatím žádné zakoupené položky.").pack()
            return

        for item in self.data["purchased_items"]:
            text = f"{item['name']} - {item['price']} Kč"
            ctk.CTkLabel(frame, text=text).pack(anchor="w")

    def manual_add_day(self, event=None):
        # Manuálně přidat 1 den bez cigarety
        self.data["days_without_cigs"] += 1
        self.data["wallet"] += self.cig_price
        self.data["total_saved"] += self.cig_price
        self.data["xp"] += 10
        self.check_achievements()
        save_data(self.data)
        self.update_ui()
        messagebox.showinfo("Manuální přidání", "Přidán 1 den bez cigarety (Ctrl+D).")

if __name__ == "__main__":
    app = StopSmokingApp()
    app.mainloop()
