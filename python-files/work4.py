

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import random
import threading
import time
from datetime import datetime, timedelta

DB = "game.db"
ENERGY_RECOVER_INTERVAL_SEC = 3600  # 1 час
BOX_OPEN_STEPS = 100
REPAIR_COST = 10
coins_cost = 10

# -----------------------
# База данных
# -----------------------
def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    coins INTEGER DEFAULT 0,
                    energy INTEGER DEFAULT 100,
                    last_energy_ts INTEGER DEFAULT 0,
                    steps INTEGER DEFAULT 0,
                    equipped_shoe_id INTEGER
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS shoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER,
                    name TEXT,
                    luck INTEGER,
                    durability INTEGER,
                    level INTEGER DEFAULT 1,
                    FOREIGN KEY(player_id) REFERENCES players(id)
                )""")
    c.execute("""CREATE TABLE IF NOT EXISTS boxes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_id INTEGER,
                    steps_required INTEGER,
                    created_at INTEGER,
                    opened INTEGER DEFAULT 0,
                    FOREIGN KEY(player_id) REFERENCES players(id)
                )""")
    conn.commit()
    conn.close()

# -----------------------
# Утилиты работы с БД
# -----------------------
def get_player_by_name(name):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, coins, energy, last_energy_ts, steps, equipped_shoe_id FROM players WHERE name = ?", (name,))
    row = c.fetchone()
    conn.close()
    return row

def create_player(name):
    now = int(time.time())
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO players(name, coins, energy, last_energy_ts, steps) VALUES (?, ?, ?, ?, ?)",
              (name, 50, 100, now, 0))  # стартовые монеты 50, энергия 100
    pid = c.lastrowid
    conn.commit()
    conn.close()
    return get_player_by_name(name)

def update_player_field(player_id, field, value):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(f"UPDATE players SET {field} = ? WHERE id = ?", (value, player_id))
    conn.commit()
    conn.close()

def list_shoes(player_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, luck, durability, level FROM shoes WHERE player_id = ?", (player_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_shoe(player_id, name, luck, durability):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO shoes(player_id, name, luck, durability) VALUES (?, ?, ?, ?)",
              (player_id, name, luck, durability))
    conn.commit()
    conn.close()

def get_shoe(shoe_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, name, luck, durability, level, player_id FROM shoes WHERE id = ?", (shoe_id,))
    r = c.fetchone()
    conn.close()
    return r

def update_shoe(shoe_id, field, value):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute(f"UPDATE shoes SET {field} = ? WHERE id = ?", (value, shoe_id))
    conn.commit()
    conn.close()

def delete_shoe(shoe_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM shoes WHERE id = ?", (shoe_id,))
    conn.commit()
    conn.close()

def create_box_for_player(player_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    now = int(time.time())


    c.execute("INSERT INTO boxes(player_id, steps_required, created_at, opened) VALUES (?, ?, ?, 0)",
              (player_id, BOX_OPEN_STEPS, now))
    conn.commit()
    conn.close()

def get_player_boxes(player_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT id, steps_required, opened FROM boxes WHERE player_id = ? AND opened = 0", (player_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def open_box(box_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE boxes SET opened = 1 WHERE id = ?", (box_id,))
    conn.commit()
    conn.close()

# -----------------------
# Логика игровая
# -----------------------
def random_shoe_name():
    models = ["Flash", "Sprint", "Comet", "Phantom", "Stride", "Bolt"]
    return random.choice(models) + "-" + str(random.randint(100, 999))

def create_random_shoe_for(player_id):
    name = random_shoe_name()
    luck = random.randint(1, 50)
    durability = random.randint(20, 100)
    add_shoe(player_id, name, luck, durability)
    return (name, luck, durability)

def ensure_energy_recovery(player):
    # игрок: tuple (id, name, coins, energy, last_energy_ts, steps, equipped_shoe_id)
    pid = player[0]
    last_ts = player[4]
    now = int(time.time())
    elapsed = now - last_ts
    if elapsed >= ENERGY_RECOVER_INTERVAL_SEC:
        recovered = elapsed // ENERGY_RECOVER_INTERVAL_SEC
        new_energy = min(100, player[3] + int(recovered * 10))  # +10 энергии в час
        update_player_field(pid, "energy", new_energy)
        update_player_field(pid, "last_energy_ts", now)
        return new_energy
    return player[3]

# -----------------------
# GUI
# -----------------------
class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Runner Game")
        self.geometry("640x420")
        self.resizable(False, False)

        init_db()

        self.player = None  # текущий игрок tuple
        self.equipped_shoe = None  # tuple shoe
        self.walking = False
        self.walk_thread = None
        self.stop_walk_flag = threading.Event()

        self.create_widgets()
        self.update_status_labels_periodically()

    def create_widgets(self):
        frame = ttk.Frame(self)
        frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Меню кнопки
        btns = [
            ("Создать персонажа", self.create_character),
            ("Загрузить персонажа", self.load_character),
            ("Магазин", self.shop),
            ("Одеть кроссовки", self.equip_shoes),
            ("Починить кроссовки", self.repair_shoes),
            ("Идти", self.toggle_walk),
            ("Восстановить энергию", self.recover_energy_now),
            ("Сохранить прогресс", self.save_progress),
            ("Выйти", self.quit),
        ]
        for i, (txt, cmd) in enumerate(btns):
            b = ttk.Button(frame, text=txt, command=cmd)
            b.grid(row=i, column=0, sticky="ew", pady=3)

        # Статусы игрока
        right = ttk.Frame(frame)
        right.grid(row=0, column=1, rowspan=9, padx=20, sticky="n")

        self.lbl_name = ttk.Label(right, text="Игрок: —")
        self.lbl_name.pack(anchor="w")
        self.lbl_coins = ttk.Label(right, text="Монеты: 0")
        self.lbl_coins.pack(anchor="w")
        self.lbl_energy = ttk.Label(right, text="Энергия: 0")
        self.lbl_energy.pack(anchor="w")
        self.lbl_steps = ttk.Label(right, text="Шаги: 0")
        self.lbl_steps.pack(anchor="w")
        self.lbl_shoe = ttk.Label(right, text="Кроссовки: —")
        self.lbl_shoe.pack(anchor="w")
        self.lbl_shoe_dur = ttk.Label(right, text="Прочность: —")
        self.lbl_shoe_dur.pack(anchor="w")
        self.lbl_shoe_luck = ttk.Label(right, text="Удача: —")
        self.lbl_shoe_luck.pack(anchor="w")
        self.log = tk.Text(right, height=10, width=30, state="disabled")
        self.log.pack(pady=5)

    def log_msg(self, txt):
        self.log.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")


        self.log.insert("end", f"[{ts}] {txt}\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    # -----------------------
    # Меню-функции
    # -----------------------
    def create_character(self):
        name = simpledialog.askstring("Создать", "Имя персонажа:")
        if not name:
            return
        existing = get_player_by_name(name)
        if existing:
            messagebox.showinfo("Info", "Такой персонаж уже есть. Загрузите его.")
            return
        player = create_player(name)
        self.player = player
        self.equipped_shoe = None
        self.log_msg(f"Персонаж {name} создан")
        self.refresh_ui()

    def load_character(self):
        # попросим имя; если нет — создадим
        name = simpledialog.askstring("Загрузить", "Имя персонажа:")
        if not name:
            return
        p = get_player_by_name(name)
        if not p:
            if messagebox.askyesno("Нет персонажа", "Персонаж не найден. Создать?"):
                p = create_player(name)
            else:
                return
        # применим восстановление энергии автоматически
        new_energy = ensure_energy_recovery(p)
        # обновим объект p
        p = get_player_by_name(name)
        self.player = p
        self.equipped_shoe = get_shoe(p[6]) if p[6] else None
        self.log_msg(f"Персонаж {p[1]} загружен (энергия {p[3]})")
        self.refresh_ui()

    def shop(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
        shop_win = tk.Toplevel(self)
        shop_win.title("Магазин")
        shop_win.geometry("400x300")
        lbl = ttk.Label(shop_win, text=f"Монеты: {self.player[2]}")
        lbl.pack()
        listbox = tk.Listbox(shop_win)
        listbox.pack(fill="both", expand=True)
        items = []
        for i in range(6):
            name = random_shoe_name()
            luck = random.randint(1, 100)
            dur = random.randint(30, 120)
            price = (luck ** 2 + dur // 10) * 5
            items.append((name, luck, dur, price))
            listbox.insert("end", f"{i+1}. {name}  Luck:{luck} Dur:{dur} Price:{price}")
        def buy():
            sel = listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            name, luck, dur, price = items[idx]
            if self.player[2] < price:
                messagebox.showwarning("Недостаточно", "Не хватает монет")
                return
            # списываем монеты и даём кроссовки
            new_coins = self.player[2] - price
            update_player_field(self.player[0], "coins", new_coins)
            add_shoe(self.player[0], name, luck, dur)
            self.player = get_player_by_name(self.player[1])
            lbl.config(text=f"Монеты: {self.player[2]}")
            self.log_msg(f"Куплены {name} за {price}")
            self.refresh_ui()
        btn = ttk.Button(shop_win, text="Купить", command=buy)
        btn.pack(pady=5)

    def equip_shoes(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
        shoes = list_shoes(self.player[0])
        if not shoes:
            messagebox.showinfo("Инфо", "У вас нет кроссовок")
            return
        win = tk.Toplevel(self)
        win.title("Выбрать кроссовки")
        lb = tk.Listbox(win)
        for s in shoes:
            lb.insert("end", f"{s[0]}. {s[1]} Luck:{s[2]} Dur:{s[3]} Lv:{s[4]}")
        lb.pack(fill="both", expand=True)
        def do_equip():
            sel = lb.curselection()
            if not sel:
                return
            idx = sel[0]
            shoe_id = shoes[idx][0]
            update_player_field(self.player[0], "equipped_shoe_id", shoe_id)
            self.player = get_player_by_name(self.player[1])
            self.equipped_shoe = get_shoe(shoe_id)
            self.log_msg(f"Экипированы {self.equipped_shoe[1]}")
            self.refresh_ui()
            win.destroy()


        b = ttk.Button(win, text="Экипировать", command=do_equip)
        b.pack(pady=4)

    def repair_shoes(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
        if not self.equipped_shoe:
            messagebox.showwarning("Ошибка", "Нет экипированных кроссовок")
            return
        if self.player[2] < REPAIR_COST:
            messagebox.showwarning("Ошибка", "Не хватает монет на починку")
            return
        # починить кроссовки: установим прочность до 100
        new_coins = self.player[2] - REPAIR_COST
        update_player_field(self.player[0], "coins", new_coins)
        update_shoe(self.equipped_shoe[0], "durability", 100)
        self.player = get_player_by_name(self.player[1])
        self.equipped_shoe = get_shoe(self.player[6])
        self.log_msg(f"Кроссовки {self.equipped_shoe[1]} починены за {REPAIR_COST} монет")
        self.refresh_ui()

    def toggle_walk(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
        if not self.equipped_shoe:
            messagebox.showwarning("Ошибка", "Наденьте кроссовки")
            return
        if self.walking:
            self.stop_walk_flag.set()
            self.walking = False
            self.log_msg("Остановлено")
            return
        # запустить ходьбу в отдельном потоке
        if self.player[3] <= 0:
            messagebox.showwarning("Нет энергии", "Энергия кончилась")
            return
        self.stop_walk_flag.clear()
        self.walking = True
        self.walk_thread = threading.Thread(target=self.walk_loop, daemon=True)
        self.walk_thread.start()
        self.log_msg("Начали идти")

    def walk_loop(self):
        # шаг каждые 1..2 секунды (симуляция), расход энергии и прочности, шанс найти предметы
        while not self.stop_walk_flag.is_set():
            time.sleep(random.uniform(0.8, 1.5))
            # заново загрузим свежие данные игрока и обуви
            self.player = get_player_by_name(self.player[1])
            if self.player[3] <= 0:
                self.log_msg("Энергия закончилась")
                self.walking = False
                break
            shoe = get_shoe(self.player[6]) if self.player[6] else None
            if not shoe:
                self.log_msg("Кроссовки пропали")
                self.walking = False
                break
            shoe_id, sname, luck, dur, level, owner = shoe
            # шаг
            new_steps = self.player[5] + 1
            update_player_field(self.player[0], "steps", new_steps)
            # расход энергии: 1 + уровень кроссовок // 2
            energy_cost = 1 + level//2
            new_energy = max(0, self.player[3] - energy_cost)
            update_player_field(self.player[0], "energy", new_energy)
            # уменьшение прочности
            new_dur = max(0, dur - 1)
            update_shoe(shoe_id, "durability", new_dur)
            # повышение удачи (немного)
            new_luck = min(100, luck + 0.0001)
            update_shoe(shoe_id, "luck", new_luck)
            # обновить локальные переменные
            self.player = get_player_by_name(self.player[1])
            self.equipped_shoe = get_shoe(shoe_id)
            # лог
            self.log_msg(f"Шаг +1 (энергия -{energy_cost}, прочность -1)")
            # шанс найти монеты/bank/box
            # базовый шанс увеличивается с luck
            find_roll = random.randint(1, 100)
            if find_roll <= 4 + new_luck//5:  # найдена банка (энергия)
                gain = random.randint(3, 5)
                new_energy2 = min(100, self.player[3] + gain)
                update_player_field(self.player[0], "energy", new_energy2)
                self.player = get_player_by_name(self.player[1])
                self.log_msg(f"Найдена банка: +{gain} энергии")
            elif find_roll <= 55 + new_luck//4:  # монеты
                coins_found = random.randint(1, 2)
                new_coins = self.player[2] + coins_found


                update_player_field(self.player[0], "coins", new_coins)
                self.player = get_player_by_name(self.player[1])
                self.log_msg(f"Найдены монеты: +{coins_found}")
            elif find_roll <= 10 + new_luck//6:  # коробка
                create_box_for_player(self.player[0])
                self.log_msg("Найдена коробка! Откройте её за 100 шагов")
            # если прочность упала до 0 — кроссовки нельзя использовать для ходьбы (они сломаны)
            if new_dur <= 0:
                self.log_msg("Кроссовки сломались!")
                # автоматическое снять: оставим экипированными, но при попытке идти надо заново проверить
                self.walking = False
                break
            # обновить UI
            self.refresh_ui()
        self.walking = False

    def recover_energy_now(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
            
            
        
        new_coins = self.player[2] - coins_cost
        update_player_field(self.player[0], "coins", new_coins)   
        
        
        # мгновенное восстановление (за реал-тайм мы предоставляем опцию)
        new_energy = min(100, self.player[3] + 20)
        update_player_field(self.player[0], "energy", new_energy)
        update_player_field(self.player[0], "last_energy_ts", int(time.time()))
        self.player = get_player_by_name(self.player[1])
        self.log_msg("Энергия восстановлена на +20 (ручное)")
        self.refresh_ui()

    def save_progress(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
        # все изменения в БД уже применяются в реальном времени
        messagebox.showinfo("Сохранено", "Прогресс сохранён (данные в SQLite)")
        self.log_msg("Прогресс сохранён")

    # -----------------------
    # UI обновления
    # -----------------------
    def refresh_ui(self):
        if not self.player:
            self.lbl_name.config(text="Игрок: —")
            self.lbl_coins.config(text="Монеты: 0")
            self.lbl_energy.config(text="Энергия: 0")
            self.lbl_steps.config(text="Шаги: 0")
            self.lbl_shoe.config(text="Кроссовки: —")
            self.lbl_shoe_dur.config(text="Прочность: —")
            self.lbl_shoe_luck.config(text="Удача: —")
            return
        # получить свежие данные
        self.player = get_player_by_name(self.player[1])
        self.lbl_name.config(text=f"Игрок: {self.player[1]}")
        self.lbl_coins.config(text=f"Монеты: {self.player[2]}")
        self.lbl_energy.config(text=f"Энергия: {self.player[3]}")
        self.lbl_steps.config(text=f"Шаги: {self.player[5]}")
        if self.player[6]:
            shoe = get_shoe(self.player[6])
            if shoe:
                self.equipped_shoe = shoe
                self.lbl_shoe.config(text=f"Кроссовки: {shoe[1]} (Lv{shoe[4]})")
                self.lbl_shoe_dur.config(text=f"Прочность: {shoe[3]}")
                self.lbl_shoe_luck.config(text=f"Удача: {shoe[2]}")
            else:
                self.lbl_shoe.config(text="Кроссовки: —")
                self.lbl_shoe_dur.config(text="Прочность: —")
                self.lbl_shoe_luck.config(text="Удача: —")
        else:
            self.lbl_shoe.config(text="Кроссовки: —")
            self.lbl_shoe_dur.config(text="Прочность: —")
            self.lbl_shoe_luck.config(text="Удача: —")

    def update_status_labels_periodically(self):
        # проверяем восстановление энергии каждый запуск цикла
        if self.player:
            p = get_player_by_name(self.player[1])
            new_e = ensure_energy_recovery(p)
            self.player = get_player_by_name(self.player[1])
            self.refresh_ui()
        # каждые 5 секунд обновлять индикаторы
        self.after(5000, self.update_status_labels_periodically)

    # -----------------------
    # Доп. действия с коробками и продажа обуви
    # -----------------------
    def open_boxes_menu(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
        boxes = get_player_boxes(self.player[0])


        if not boxes:
            messagebox.showinfo("Инфо", "Нет доступных закрытых коробок")
            return
        win = tk.Toplevel(self)
        win.title("Коробки")
        lb = tk.Listbox(win)
        for b in boxes:
            lb.insert("end", f"{b[0]}. Требуется шагов: {b[1]}")
        lb.pack(fill="both", expand=True)
        def try_open():
            sel = lb.curselection()
            if not sel: return
            idx = sel[0]
            box_id, steps_req, opened = boxes[idx]
            # проверим, выполнены ли шаги
            if self.player[5] >= BOX_OPEN_STEPS:             

                # открыть и выдать награду
                open_box(box_id)
                roll = random.randint(1, 100)
                
                
                
                
                if roll <= 40:
                    gain = random.randint(10, 30)
                    new_energy = min(100, self.player[3] + gain)
                    
                    
                    new_steps = self.player[5] - 100
                    update_player_field(self.player[0], "steps", new_steps)
                    
                    
                    
                    update_player_field(self.player[0], "energy", new_energy)
                    self.log_msg(f"В коробке: энергия +{gain}")
                elif roll <= 80:
                    coins = random.randint(10, 50)
                    
                    
                    new_steps = self.player[5] - 100
                    update_player_field(self.player[0], "steps", new_steps)
                    
                    
                    
                    update_player_field(self.player[0], "coins", self.player[2] + coins)
                    self.log_msg(f"В коробке: монеты +{coins}")
                else:
                    name, luck, dur = create_random_shoe_for(self.player[0])
                    
                    
                    new_steps = self.player[5] - 100
                    update_player_field(self.player[0], "steps", new_steps)
                    
                    
                    self.log_msg(f"В коробке выпали кроссовки: {name}")
                self.player = get_player_by_name(self.player[1])
                self.refresh_ui()
                win.destroy()
            else:
                messagebox.showwarning("Ещё рано", f"Нужно пройти {BOX_OPEN_STEPS} шагов (всего {self.player[5]})")
        ttk.Button(win, text="Открыть", command=try_open).pack(pady=4)

    def sell_shoes_menu(self):
        if not self.player:
            messagebox.showwarning("Ошибка", "Сначала загрузите персонажа")
            return
        shoes = list_shoes(self.player[0])
        if not shoes:
            messagebox.showinfo("Инфо", "Нет кроссовок для продажи")
            return
        win = tk.Toplevel(self)
        win.title("Продать кроссовки")
        lb = tk.Listbox(win)
        for s in shoes:
            lb.insert("end", f"{s[0]}. {s[1]} Luck:{s[2]} Dur:{s[3]}")
        lb.pack(fill="both", expand=True)
        def sell():
            sel = lb.curselection()
            if not sel: return
            idx = sel[0]
            s = shoes[idx]
            price = (s[2] + s[3]//10) * 3
            if messagebox.askyesno("Продать", f"Продать {s[1]} за {price}?"):
                delete_shoe(s[0])
                update_player_field(self.player[0], "coins", self.player[2] + price)
                self.player = get_player_by_name(self.player[1])
                self.log_msg(f"Проданы {s[1]} за {price}")
                self.refresh_ui()
                win.destroy()
        ttk.Button(win, text="Продать", command=sell).pack(pady=4)

# -----------------------
# Запуск
# -----------------------
if __name__ == "__main__":
    app = GameApp()
    # добавим пункты меню для коробок и продажи через правую кнопку (или горячие)
    menubar = tk.Menu(app)
    action_menu = tk.Menu(menubar, tearoff=0)
    action_menu.add_command(label="Открыть коробки", command=app.open_boxes_menu)
    action_menu.add_command(label="Продать кроссовки", command=app.sell_shoes_menu)
    menubar.add_cascade(label="Другое", menu=action_menu)
    app.config(menu=menubar)
    app.mainloop()
