import tkinter as tk
from tkinter import ttk, messagebox

class Enemy:
    def __init__(self, name, hp_zewn, hp_wewn, rp, weaknesses, resistances, immunes):
        self.name = name
        self.hp_zewn = hp_zewn
        self.hp_wewn = hp_wewn
        self.max_hp_zewn = hp_zewn
        self.max_hp_wewn = hp_wewn
        self.rp = rp
        self.weaknesses = weaknesses
        self.resistances = resistances
        self.immunes = immunes

    def receive_damage(self, dmg, dmg_type, target_hp):
        # Nie otrzymuje obrażeń jeśli immune
        if dmg_type in self.immunes:
            actual_dmg = 0
        elif dmg_type in self.weaknesses:
            actual_dmg = dmg * 2
        elif dmg_type in self.resistances:
            actual_dmg = dmg // 2  # zaokrąglamy w dół
        else:
            actual_dmg = dmg

        # Zmniejszamy obrażenia o redukcję obrażeń (rp)
        actual_dmg -= self.rp
        if actual_dmg < 0:
            actual_dmg = 0

        if target_hp == "zewnętrzne":
            self.hp_zewn -= actual_dmg
            if self.hp_zewn < 0:
                # Przekroczenie HP zewnętrznego przechodzi na wewnętrzne
                overflow = -self.hp_zewn
                self.hp_zewn = 0
                self.hp_wewn -= overflow
                if self.hp_wewn < 0:
                    self.hp_wewn = 0
        else:
            self.hp_wewn -= actual_dmg
            if self.hp_wewn < 0:
                self.hp_wewn = 0

    def get_status(self):
        return (f"{self.name}\n"
                f"HP Zewnętrzne: {self.hp_zewn}/{self.max_hp_zewn}\n"
                f"HP Wewnętrzne: {self.hp_wewn}/{self.max_hp_wewn}\n"
                f"RP: {self.rp}")

    def get_details(self):
        return (f"Słabości: {', '.join(self.weaknesses) if self.weaknesses else 'Brak'}\n"
                f"Odporności: {', '.join(self.resistances) if self.resistances else 'Brak'}\n"
                f"Immunitet: {', '.join(self.immunes) if self.immunes else 'Brak'}")

class DTApp:
    damage_types = [
        "kłute", "cięte", "obuchowe", "fire",
        "light", "lightning", "ice", "psychiczne", "wybuchowe"
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("D&T - Menadżer Przeciwników")

        self.enemies = []

        self.create_input_frame()
        self.create_display_frame()

    def create_input_frame(self):
        frame = tk.Frame(self.root, pady=10)
        frame.pack(fill="x")

        tk.Label(frame, text="Nazwa:").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(frame)
        self.name_entry.grid(row=0, column=1, sticky="ew")

        tk.Label(frame, text="HP zewnętrzne:").grid(row=1, column=0, sticky="w")
        self.hp_zewn_entry = tk.Entry(frame)
        self.hp_zewn_entry.grid(row=1, column=1, sticky="ew")

        tk.Label(frame, text="HP wewnętrzne:").grid(row=2, column=0, sticky="w")
        self.hp_wewn_entry = tk.Entry(frame)
        self.hp_wewn_entry.grid(row=2, column=1, sticky="ew")

        tk.Label(frame, text="Redukcja obrażeń (RP):").grid(row=3, column=0, sticky="w")
        self.rp_entry = tk.Entry(frame)
        self.rp_entry.grid(row=3, column=1, sticky="ew")

        # Słabości, odporności, immunitet - dodawanie z przyciskami i oknami
        tk.Label(frame, text="Słabości:").grid(row=0, column=2, sticky="w")
        self.weaknesses = []
        self.weaknesses_var = tk.StringVar(value=[])
        self.weak_btn = tk.Button(frame, text="Dodaj słabości", command=self.add_weaknesses)
        self.weak_btn.grid(row=0, column=3, sticky="ew")

        tk.Label(frame, text="Odporności:").grid(row=1, column=2, sticky="w")
        self.resistances = []
        self.resistances_var = tk.StringVar(value=[])
        self.resist_btn = tk.Button(frame, text="Dodaj odporności", command=self.add_resistances)
        self.resist_btn.grid(row=1, column=3, sticky="ew")

        tk.Label(frame, text="Immunitet:").grid(row=2, column=2, sticky="w")
        self.immunes = []
        self.immunes_var = tk.StringVar(value=[])
        self.immune_btn = tk.Button(frame, text="Dodaj immunitet", command=self.add_immunes)
        self.immune_btn.grid(row=2, column=3, sticky="ew")

        tk.Label(frame, text="Ilość przeciwników:").grid(row=3, column=2, sticky="w")
        self.amount_entry = tk.Entry(frame)
        self.amount_entry.grid(row=3, column=3, sticky="ew")

        self.create_btn = tk.Button(frame, text="Stwórz", command=self.create_enemies)
        self.create_btn.grid(row=4, column=0, columnspan=4, pady=5, sticky="ew")

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(3, weight=1)

    def add_weaknesses(self):
        self.add_damage_types_window("Słabości", self.weaknesses)

    def add_resistances(self):
        self.add_damage_types_window("Odporności", self.resistances)

    def add_immunes(self):
        self.add_damage_types_window("Immunitet", self.immunes)

    def add_damage_types_window(self, title, target_list):
        def save():
            target_list.clear()
            for i, var in enumerate(check_vars):
                if var.get():
                    target_list.append(self.damage_types[i])
            top.destroy()

        top = tk.Toplevel(self.root)
        top.title(title)
        check_vars = []
        for i, dmg_type in enumerate(self.damage_types):
            var = tk.BooleanVar()
            chk = tk.Checkbutton(top, text=dmg_type, variable=var)
            chk.pack(anchor="w")
            check_vars.append(var)

        save_btn = tk.Button(top, text="Zapisz", command=save)
        save_btn.pack(pady=5)

    def create_enemies(self):
        try:
            name = self.name_entry.get()
            hp_zewn = int(self.hp_zewn_entry.get())
            hp_wewn = int(self.hp_wewn_entry.get())
            rp = int(self.rp_entry.get())
            amount = int(self.amount_entry.get())
            if not name:
                messagebox.showerror("Błąd", "Podaj nazwę przeciwnika.")
                return
            if amount < 1:
                messagebox.showerror("Błąd", "Ilość musi być co najmniej 1.")
                return
        except ValueError:
            messagebox.showerror("Błąd", "Wprowadź poprawne liczby.")
            return

        for _ in range(amount):
            enemy = Enemy(name, hp_zewn, hp_wewn, rp, self.weaknesses.copy(), self.resistances.copy(), self.immunes.copy())
            self.enemies.append(enemy)

        self.refresh_display()

    def create_display_frame(self):
        container = tk.Frame(self.root)
        container.pack(padx=10, pady=10, fill="both", expand=True)

        canvas = tk.Canvas(container)
        v_scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)

        self.display_frame = tk.Frame(canvas)

        self.display_frame.bind(
            "<Configure>",
            lambda e: (canvas.configure(scrollregion=canvas.bbox("all")),
                       canvas.configure(xscrollcommand=h_scrollbar.set),
                       canvas.configure(yscrollcommand=v_scrollbar.set))
        )

        canvas.create_window((0, 0), window=self.display_frame, anchor="nw")

        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.canvas = canvas

    def refresh_display(self):
        # Usuwamy stare panele
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        for idx, enemy in enumerate(self.enemies):
            self.create_enemy_panel(enemy, idx)

    def create_enemy_panel(self, enemy, index):
        frame = tk.LabelFrame(self.display_frame, text=f"Przeciwnik {index + 1}", padx=5, pady=5)
        frame.grid(row=index // 4, column=index % 4, padx=5, pady=5, sticky="n")

        status_var = tk.StringVar(value=enemy.get_status())
        status_label = tk.Label(frame, textvariable=status_var, justify="left")
        status_label.pack(anchor="w", pady=2)

        details_button = tk.Button(frame, text="Szczegóły", command=lambda e=enemy: self.show_details(e))
        details_button.pack(fill="x", pady=2)

        dmg_frame = tk.Frame(frame)
        dmg_frame.pack(fill="x", pady=2)

        dmg_label = tk.Label(dmg_frame, text="Obrażenia:")
        dmg_label.pack(anchor="w")

        dmg_entry = tk.Entry(dmg_frame, width=10)
        dmg_entry.pack(fill="x", pady=2)

        dmg_type_label = tk.Label(dmg_frame, text="Typ obrażeń:")
        dmg_type_label.pack(anchor="w")

        dmg_type_var = tk.StringVar(value=self.damage_types[0])
        dmg_type_menu = ttk.Combobox(dmg_frame, values=self.damage_types, textvariable=dmg_type_var, state="readonly")
        dmg_type_menu.pack(fill="x", pady=2)

        target_hp_label = tk.Label(dmg_frame, text="Celuj w HP:")
        target_hp_label.pack(anchor="w")

        target_hp_var = tk.StringVar(value="zewnętrzne")
        rb1 = tk.Radiobutton(dmg_frame, text="Zewnętrzne HP", variable=target_hp_var, value="zewnętrzne")
        rb2 = tk.Radiobutton(dmg_frame, text="Wewnętrzne HP", variable=target_hp_var, value="wewnętrzne")
        rb1.pack(anchor="w")
        rb2.pack(anchor="w")

        def apply_damage():
            try:
                dmg = int(dmg_entry.get())
                if dmg < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Błąd", "Wprowadź poprawną wartość obrażeń (liczba całkowita >= 0).")
                return
            enemy.receive_damage(dmg, dmg_type_var.get(), target_hp_var.get())
            status_var.set(enemy.get_status())
            dmg_entry.delete(0, "end")

        apply_btn = tk.Button(dmg_frame, text="Zadaj obrażenia", command=apply_damage)
        apply_btn.pack(fill="x", pady=3)

    def show_details(self, enemy):
        details = enemy.get_details()
        messagebox.showinfo(f"Szczegóły {enemy.name}", details)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x600")
    app = DTApp(root)
    root.mainloop()
