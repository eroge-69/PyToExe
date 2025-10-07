"""
Tablica punktacji BJJ (Tkinter) — Niebieski vs Biały

W tej wersji:
- Czerwony zamieniony na Biały (white), blue pozostaje jako Niebieski
- Interfejs, logi i eksport po polsku
- Przyciski punktów wyśrodkowane w dwóch kolumnach
- Obsługa cofania punktów, przewag i kar
- Zegary z możliwością ustawienia czasu
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import time
import csv

# Domyślne punkty
DEFAULT_POINTS = {
    'Obalenie': 2,
    'Sweep': 2,
    'Kolano na brzuchu': 2,
    'Przejście gardy': 3,
    'Dosiad': 4,
    'Kontrola pleców': 4,
    'Przewaga': 1,
    'Kara': 1
}

class MatchState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.blue_name = ''
        self.white_name = ''
        self.blue_points = 0
        self.white_points = 0
        self.blue_adv = 0
        self.white_adv = 0
        self.blue_pen = 0
        self.white_pen = 0
        self.history = []
        self.match_length = 300
        self.remaining = self.match_length
        self.running = False
        self.points_map = DEFAULT_POINTS.copy()

    def record(self, action):
        self.history.append(action)

    def undo(self):
        if not self.history:
            return False
        act = self.history.pop()
        typ = act.get('type')
        if typ == 'points':
            who = act.get('who')
            val = act.get('value', 0)
            if who == 'blue':
                self.blue_points -= val
            else:
                self.white_points -= val
        elif typ == 'adv':
            who = act.get('who')
            val = act.get('value', 1)
            if who == 'blue':
                self.blue_adv -= val
            else:
                self.white_adv -= val
        elif typ == 'pen':
            who = act.get('who')
            if who == 'blue':
                self.blue_pen -= act.get('value',1)
            else:
                self.white_pen -= act.get('value',1)
            effect = act.get('effect')
            if effect:
                etype = effect.get('type')
                target = effect.get('target')
                val = effect.get('value',0)
                if etype == 'adv':
                    if target == 'blue':
                        self.blue_adv -= val
                    else:
                        self.white_adv -= val
                elif etype == 'points':
                    if target == 'blue':
                        self.blue_points -= val
                    else:
                        self.white_points -= val
        elif typ == 'time':
            self.remaining = act.get('prev', self.remaining)
        return True

class ScoreboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Tablica punktacji BJJ')
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.state = MatchState()
        self.fullscreen = False

        self.create_ui()
        self.bind_all('<space>', lambda e: self.start_pause())
        self.bind_all('r', lambda e: self.reset_match())
        self.bind_all('u', lambda e: self.undo_action())
        self.bind_all('<Control-e>', lambda e: self.export_csv())
        self.bind_all('<F11>', lambda e: self.toggle_fullscreen())
        self.bind_all('<Control-t>', lambda e: self.set_time_dialog())

    def create_ui(self):
        self.content = ttk.Frame(self, padding=10)
        self.content.grid(row=0, column=0, sticky='nsew')
        self.content.rowconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=1)

        self.main = ttk.Frame(self.content)
        self.main.grid(row=0, column=0, sticky='nsew')
        self.main.columnconfigure(0, weight=1)
        self.main.columnconfigure(1, weight=1)
        self.main.columnconfigure(2, weight=1)

        # Lewy panel - niebieski
        self.left = tk.Frame(self.main, bg='blue', padx=10, pady=10)
        self.left.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        tk.Label(self.left, text='Zawodnik Niebieski', bg='blue', fg='white', font=('Helvetica',14,'bold')).grid(row=0,column=0,pady=(0,6))
        self.blue_name_var = tk.StringVar(value=self.state.blue_name)
        tk.Entry(self.left, textvariable=self.blue_name_var, justify='center').grid(row=1,column=0,pady=(0,6))
        self.blue_points_var = tk.IntVar(value=self.state.blue_points)
        tk.Label(self.left, textvariable=self.blue_points_var, font=('Helvetica',48,'bold'), bg='blue', fg='white').grid(row=2,column=0)

        advpen_left = tk.Frame(self.left, bg='blue')
        advpen_left.grid(row=3,column=0,pady=(8,0))
        self.blue_adv_var = tk.IntVar(value=self.state.blue_adv)
        self.blue_pen_var = tk.IntVar(value=self.state.blue_pen)
        self.blue_adv_label = tk.Label(advpen_left, textvariable=self.blue_adv_var, bg='yellow', fg='black', width=6, font=('Helvetica',14,'bold'))
        self.blue_adv_label.pack(side='left', padx=(0,10))
        self.blue_pen_label = tk.Label(advpen_left, textvariable=self.blue_pen_var, bg='red', fg='white', width=6, font=('Helvetica',14,'bold'))
        self.blue_pen_label.pack(side='left')

        # Środek
        self.center = tk.Frame(self.main, bg='black', padx=10, pady=10)
        self.center.grid(row=0,column=1,sticky='nsew', padx=5, pady=5)
        self.center.columnconfigure(0, weight=1)
        self.time_var = tk.StringVar(value=self.format_time(self.state.remaining))
        tk.Label(self.center, textvariable=self.time_var, font=('Helvetica',56,'bold'), fg='white', bg='black').grid(row=0,column=0,pady=(0,10))
        ttk.Button(self.center, text='Start / Pauza (Spacja)', command=self.start_pause).grid(row=1,column=0,pady=6,sticky='ew')
        ttk.Button(self.center, text='Reset (r)', command=self.reset_match).grid(row=2,column=0,pady=6,sticky='ew')

        # Prawy panel - biały
        self.right = tk.Frame(self.main, bg='white', padx=10, pady=10)
        self.right.grid(row=0,column=2,sticky='nsew', padx=5, pady=5)
        tk.Label(self.right, text='Zawodnik Biały', bg='white', fg='black', font=('Helvetica',14,'bold')).grid(row=0,column=0,pady=(0,6))
        self.white_name_var = tk.StringVar(value=self.state.white_name)
        tk.Entry(self.right, textvariable=self.white_name_var, justify='center').grid(row=1,column=0,pady=(0,6))
        self.white_points_var = tk.IntVar(value=self.state.white_points)
        tk.Label(self.right, textvariable=self.white_points_var, font=('Helvetica',48,'bold'), bg='white', fg='black').grid(row=2,column=0)

        advpen_right = tk.Frame(self.right, bg='white')
        advpen_right.grid(row=3,column=0,pady=(8,0))
        self.white_adv_var = tk.IntVar(value=self.state.white_adv)
        self.white_pen_var = tk.IntVar(value=self.state.white_pen)
        self.white_adv_label = tk.Label(advpen_right, textvariable=self.white_adv_var, bg='yellow', fg='black', width=6, font=('Helvetica',14,'bold'))
        self.white_adv_label.pack(side='left', padx=(0,10))
        self.white_pen_label = tk.Label(advpen_right, textvariable=self.white_pen_var, bg='red', fg='white', width=6, font=('Helvetica',14,'bold'))
        self.white_pen_label.pack(side='left')

        # Kontrolki punktacji (wyśrodkowane 2 kolumny)
        self.controls = ttk.Frame(self.content, padding=(5,8))
        self.controls.grid(row=1, column=0, sticky='ew')
        self.controls.columnconfigure(0, weight=1)
        self.controls.columnconfigure(1, weight=1)

        for idx, (name,val) in enumerate(self.state.points_map.items()):
            if name in ('Przewaga','Kara'):
                continue
            btn_b = ttk.Button(self.controls, text=f"Niebieski +{val} {name}", command=lambda n=name: self.add_points('blue',n))
            btn_w = ttk.Button(self.controls, text=f"Biały +{val} {name}", command=lambda n=name: self.add_points('white',n))
            btn_b.grid(row=idx, column=0, padx=3, pady=2, sticky='ew')
            btn_w.grid(row=idx, column=1, padx=3, pady=2, sticky='ew')

        # Przewagi / kary
        ttk.Button(self.controls, text='Niebieski +Przewaga', command=lambda:self.add_adv('blue')).grid(row=50,column=0,pady=4, sticky='ew')
        ttk.Button(self.controls, text='Biały +Przewaga', command=lambda:self.add_adv('white')).grid(row=50,column=1,pady=4, sticky='ew')
        ttk.Button(self.controls, text='Niebieski +Kara', command=lambda:self.add_pen('blue')).grid(row=51,column=0,pady=4, sticky='ew')
        ttk.Button(self.controls, text='Biały +Kara', command=lambda:self.add_pen('white')).grid(row=51,column=1,pady=4, sticky='ew')

        # Cofnięcia specyficzne
        ttk.Button(self.controls, text='Cofnij ostatni punkt', command=self.undo_last_point).grid(row=52,column=0,pady=4, sticky='ew')
        ttk.Button(self.controls, text='Cofnij ostatnią przewagę', command=self.undo_last_adv).grid(row=52,column=1,pady=4, sticky='ew')
        ttk.Button(self.controls, text='Cofnij ostatnią karę', command=self.undo_last_pen).grid(row=53,column=0,pady=4, sticky='ew')

        # Log
        self.log = tk.Text(self.content, height=6, state='disabled', bg='black', fg='white')
        self.log.grid(row=2,column=0, sticky='nsew', pady=(8,0))
        self.content.rowconfigure(2, weight=0)

        # Przycisk ustaw czas
        self.set_time_btn = ttk.Button(self, text='Ustaw czas', command=self.set_time_dialog)
        self.set_time_btn.place(relx=0.98, rely=0.02, anchor='ne')

        self.update_ui()

    # ---------- helpery ----------
    def format_time(self, secs):
        m = secs // 60
        s = secs % 60
        return f"{int(m):02d}:{int(s):02d}"

    def log_action(self, text):
        self.log['state'] = 'normal'
        ts = time.strftime('%H:%M:%S')
        self.log.insert('end', f"[{ts}] {text}\n")
        self.log.see('end')
        self.log['state'] = 'disabled'

    def update_ui(self):
        self.blue_points_var.set(self.state.blue_points)
        self.white_points_var.set(self.state.white_points)
        self.blue_adv_var.set(self.state.blue_adv)
        self.white_adv_var.set(self.state.white_adv)
        self.blue_pen_var.set(self.state.blue_pen)
        self.white_pen_var.set(self.state.white_pen)
        self.time_var.set(self.format_time(self.state.remaining))

    # ---------- akcje punktacji ----------
    def add_points(self, who, kind):
        val = self.state.points_map.get(kind,0)
        if who=='blue':
            self.state.blue_points += val
        else:
            self.state.white_points += val
        self.state.record({'type':'points','who':who,'kind':kind,'value':val})
        self.log_action(f"{who.upper()} +{val} ({kind})")
        self.update_ui()

    def add_adv(self, who):
        if who=='blue':
            self.state.blue_adv +=1
        else:
            self.state.white_adv +=1
        self.state.record({'type':'adv','who':who,'value':1})
        self.log_action(f"{who.upper()} +Przewaga")
        self.update_ui()

    def add_pen(self, who):
        if who=='blue':
            self.state.blue_pen +=1
            pcount = self.state.blue_pen
            opponent = 'white'
        else:
            self.state.white_pen +=1
            pcount = self.state.white_pen
            opponent = 'blue'

        effect = None
        if pcount==1:
            effect=None
            self.log_action(f"{who.upper()} +1 Kara (bez efektu)")
        elif pcount==2:
            if opponent=='blue':
                self.state.blue_adv +=1
            else:
                self.state.white_adv +=1
            effect={'type':'adv','target':opponent,'value':1}
            self.log_action(f"{who.upper()} +2 Kara -> {opponent.upper()} +1 Przewaga")
        else:
            if opponent=='blue':
                self.state.blue_points +=2
            else:
                self.state.white_points +=2
            effect={'type':'points','target':opponent,'value':2}
            self.log_action(f"{who.upper()} +{pcount} Kara -> {opponent.upper()} +2 Punkty")

        action={'type':'pen','who':who,'value':1,'pcount':pcount,'effect':effect}
        self.state.record(action)
        self.update_ui()

    # ---------- cofnięcia ----------
    def undo_action(self):
        ok = self.state.undo()
        if not ok:
            messagebox.showinfo('Cofnij','Brak akcji do cofnięcia')
            return
        self.log_action('Cofnięto ostatnią akcję')
        self.update_ui()

    def undo_last_point(self):
        hist = self.state.history
        for i in range(len(hist)-1,-1,-1):
            act = hist[i]
            if act.get('type')=='points':
                who = act.get('who')
                val = act.get('value',0)
                hist.pop(i)
                if who=='blue':
                    self.state.blue_points -=val
                else:
                    self.state.white_points -=val
                self.log_action(f'Cofnięto ostatni punkt: {who.upper()} -{val}')
                self.update_ui()
                return
        messagebox.showinfo('Cofnij punkt','Brak punktów do cofnięcia')

    def undo_last_adv(self):
        hist = self.state.history
        for i in range(len(hist)-1,-1,-1):
            act = hist[i]
            if act.get('type')=='adv':
                who = act.get('who')
                val = act.get('value',1)
                hist.pop(i)
                if who=='blue':
                    self.state.blue_adv -=val
                else:
                    self.state.white_adv -=val
                self.log_action(f'Cofnięto ostatnią przewagę: {who.upper()} -{val}')
                self.update_ui()
                return
        messagebox.showinfo('Cofnij przewagę','Brak przewag do cofnięcia')

    def undo_last_pen(self):
        hist = self.state.history
        for i in range(len(hist)-1,-1,-1):
            act = hist[i]
            if act.get('type')=='pen':
                who = act.get('who')
                effect = act.get('effect')
                hist.pop(i)
                if who=='blue':
                    self.state.blue_pen -=1
                else:
                    self.state.white_pen -=1
                if effect:
                    etype = effect.get('type')
                    target = effect.get('target')
                    val = effect.get('value',0)
                    if etype=='adv':
                        if target=='blue':
                            self.state.blue_adv -=val
                        else:
                            self.state.white_adv -=val
                    elif etype=='points':
                        if target=='blue':
                            self.state.blue_points -=val
                        else:
                            self.state.white_points -=val
                self.log_action(f'Cofnięto ostatnią karę: {who.upper()}')
                self.update_ui()
                return
        messagebox.showinfo('Cofnij karę','Brak kar do cofnięcia')

    # ---------- Timer ----------
    def start_pause(self):
        if not self.state.running:
            self.state.running=True
            self.state.record({'type':'time','prev':self.state.remaining})
            self._tick()
        else:
            self.state.running=False

    def _tick(self):
        if not self.state.running:
            return
        if self.state.remaining>0:
            self.state.remaining-=1
            self.time_var.set(self.format_time(self.state.remaining))
            self.after(1000,self._tick)
        else:
            self.state.running=False
            self.log_action('Koniec czasu!')

    def reset_match(self):
        if not messagebox.askyesno('Reset','Czy na pewno zresetować walkę?'):
            return
        blue_name = self.blue_name_var.get()
        white_name = self.white_name_var.get()
        self.state.reset()
        self.state.blue_name = blue_name
        self.state.white_name = white_name
        self.update_ui()
        self.log['state']='normal'
        self.log.delete('1.0','end')
        self.log['state']='disabled'

    # ---------- fullscreen / centering ----------
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.attributes('-fullscreen',self.fullscreen)
        if self.fullscreen:
            try:
                self.content.grid_forget()
            except:
                pass
            self.content.place(relx=0.5, rely=0.5, anchor='center')
        else:
            try:
                self.content.place_forget()
            except:
                pass
            self.content.grid(row=0,column=0,sticky='nsew')

    # ---------- Ustawianie czasu ----------
    def set_time_dialog(self):
        s = simpledialog.askstring('Ustaw czas','Podaj czas w formacie MM:SS (np. 05:00):', parent=self)
        if not s:
            return
        try:
            m, sec = map(int, s.split(':'))
            newt = m*60 + sec
            if newt<=0:
                raise ValueError()
            prev = self.state.remaining
            self.state.match_length=newt
            self.state.remaining=newt
            self.state.record({'type':'time','prev':prev})
            self.update_ui()
            self.log_action(f'Ustawiono nowy czas: {m:02d}:{sec:02d}')
        except:
            messagebox.showerror('Błąd','Nieprawidłowy format. Użyj MM:SS.')

    # ---------- Export ----------
    def export_csv(self):
        fname = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV','*.csv')])
        if not fname:
            return
        rows = [
            ['Zawodnik Niebieski', self.blue_name_var.get()],
            ['Zawodnik Biały', self.white_name_var.get()],
            ['Punkty Niebieski', self.state.blue_points],
            ['Punkty Biały', self.state.white_points],
            ['Przewagi Niebieski', self.state.blue_adv],
            ['Przewagi Biały', self.state.white_adv],
            ['Kary Niebieski', self.state.blue_pen],
            ['Kary Biały', self.state.white_pen],
        ]
        try:
            with open(fname,'w',newline='',encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
            messagebox.showinfo('Eksport',f'Zapisano do pliku: {fname}')
        except Exception as e:
            messagebox.showerror('Błąd eksportu',str(e))

if __name__=='__main__':
    app = ScoreboardApp()
    app.mainloop()
