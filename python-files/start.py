#!/usr/bin/env python3
# cal_csv_generator.py
# GUI Tkinter — maschere funzionanti per DD/MM/YYYY e HH:MM, esporta CSV compatibile Google Calendar (date ISO YYYY-MM-DD)

import csv
import os
import sys
from datetime import datetime, timedelta, date
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# -------------------- helper --------------------
def parse_date(s):
    """s deve essere 'DD/MM/YYYY' completo, altrimenti ritorna None"""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%d/%m/%Y").date()
    except Exception:
        return None

def parse_time(s):
    """s deve essere 'HH:MM' completo, altrimenti None"""
    if not s:
        return None
    try:
        return datetime.strptime(s.strip(), "%H:%M").time()
    except Exception:
        return None

def daterange(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)

# -------------------- generazione slot --------------------
def generate_slots(start_date, end_date,
                   morning_start, morning_end,
                   afternoon_start, afternoon_end,
                   duration_minutes,
                   weekdays_allowed=None,
                   exclude_start_times=None):
    """
    Restituisce lista di tuple (StartDateISO, StartTime, EndDateISO, EndTime)
    dove StartDateISO = 'YYYY-MM-DD' (compatibile CSV Google Calendar)
    """
    slots = []
    duration = timedelta(minutes=duration_minutes)
    if exclude_start_times is None:
        exclude_start_times = set()
    else:
        exclude_start_times = set(exclude_start_times)

    for single_date in daterange(start_date, end_date):
        if weekdays_allowed and single_date.weekday() not in weekdays_allowed:
            continue

        if morning_start and morning_end:
            cur_dt = datetime.combine(single_date, morning_start)
            end_boundary = datetime.combine(single_date, morning_end)
            while cur_dt + duration <= end_boundary:
                st = cur_dt.time().strftime("%H:%M")
                if st not in exclude_start_times:
                    slots.append((single_date.strftime("%Y-%m-%d"), st,
                                  (cur_dt + duration).date().strftime("%Y-%m-%d"),
                                  (cur_dt + duration).time().strftime("%H:%M")))
                cur_dt += duration

        if afternoon_start and afternoon_end:
            cur_dt = datetime.combine(single_date, afternoon_start)
            end_boundary = datetime.combine(single_date, afternoon_end)
            while cur_dt + duration <= end_boundary:
                st = cur_dt.time().strftime("%H:%M")
                if st not in exclude_start_times:
                    slots.append((single_date.strftime("%Y-%m-%d"), st,
                                  (cur_dt + duration).date().strftime("%Y-%m-%d"),
                                  (cur_dt + duration).time().strftime("%H:%M")))
                cur_dt += duration

    return slots

# -------------------- MaskedEntry (robusta) --------------------
class MaskedEntry(ttk.Entry):
    """
    Campo mascherato per:
      - mask='DD/MM/YYYY'  (visual length 10, max digits 8)
      - mask='HH:MM'       (visual length 5, max digits 4)
    Gestisce digitazione sequenziale, backspace/delete, incolla, click.
    Fornisce get_value() -> stringa formattata completa oppure '' se incompleta.
    """
    def __init__(self, master=None, mask='', width=12, **kwargs):
        super().__init__(master, **kwargs)
        self.mask = mask
        if mask == 'DD/MM/YYYY':
            self.visual_len = 10
            self.sep_positions = {2: '/', 5: '/'}
            self.digit_positions = [0,1,3,4,6,7,8,9]
            self.max_digits = 8
        elif mask == 'HH:MM':
            self.visual_len = 5
            self.sep_positions = {2: ':'}
            self.digit_positions = [0,1,3,4]
            self.max_digits = 4
        else:
            raise ValueError("Mask non supportata")

        self.placeholder = '_'
        self.digits = []  # lista di caratteri numerici
        self.var = tk.StringVar()
        self.configure(textvariable=self.var, width=width)
        self._updating = False

        # bind tastiera + click + incolla
        self.bind('<KeyPress>', self._on_keypress)
        self.bind('<Button-1>', self._on_click)
        self.bind('<FocusIn>', self._on_focus_in)
        self.bind('<Control-v>', self._on_paste)
        self.bind('<Control-V>', self._on_paste)

        # mostro la maschera iniziale
        self._rebuild_display()

    # --- utilità di mapping ---
    def _rebuild_display(self, set_cursor_pos=None):
        chars = [self.placeholder] * self.visual_len
        for pos, sep in self.sep_positions.items():
            chars[pos] = sep
        for i, d in enumerate(self.digits):
            pos = self.digit_positions[i]
            chars[pos] = d
        display = ''.join(chars)
        self._updating = True
        self.var.set(display)
        # se ci chiedono di settare il cursore lo facciamo, altrimenti lo lasciamo dove l'utente aveva
        if set_cursor_pos is not None:
            # clamp
            if set_cursor_pos < 0:
                set_cursor_pos = 0
            if set_cursor_pos > self.visual_len:
                set_cursor_pos = self.visual_len
            try:
                self.icursor(set_cursor_pos)
            except Exception:
                pass
        self._updating = False

    def _cursor_digit_index(self):
        """Ritorna l'indice (0..len(digits)) corrispondente alla posizione cursore"""
        pos = self.index(tk.INSERT)
        idx = 0
        for p in self.digit_positions:
            if p < pos:
                idx += 1
        return idx

    def _digit_index_to_visual_pos_after(self, digit_index):
        """
        Dato un indice di cifra (0..n), ritorna la posizione visiva dove porre il cursore
        dopo la cifra indicata (ossia subito dopo il carattere visuale).
        """
        if digit_index < len(self.digit_positions):
            return self.digit_positions[digit_index] + 1
        else:
            return self.visual_len

    # --- gestione tastiera ---
    def _on_keypress(self, event):
        if self._updating:
            return "break"
        keysym = event.keysym

        # navigazione consentita
        if keysym in ('Left', 'Right', 'Home', 'End', 'Tab', 'ISO_Left_Tab'):
            return None  # default

        # backspace: cancella cifra precedente
        if keysym == 'BackSpace':
            idx = self._cursor_digit_index()
            if idx > 0:
                del self.digits[idx - 1]
                new_pos = self._digit_index_to_visual_pos_after(idx - 1)
                self._rebuild_display(set_cursor_pos=new_pos)
            return "break"

        # delete: cancella cifra corrente
        if keysym == 'Delete':
            idx = self._cursor_digit_index()
            if idx < len(self.digits):
                del self.digits[idx]
                new_pos = self._digit_index_to_visual_pos_after(idx)
                self._rebuild_display(set_cursor_pos=new_pos)
            return "break"

        ch = event.char
        # inserimento cifra
        if ch and ch.isdigit():
            idx = self._cursor_digit_index()
            if len(self.digits) < self.max_digits:
                self.digits.insert(idx, ch)
                new_pos = self._digit_index_to_visual_pos_after(idx)
                self._rebuild_display(set_cursor_pos=new_pos)
            return "break"

        # ignora altri caratteri imprimibili
        return "break" if ch else None

    # incolla dal clipboard (gestito in modo pulito: prendo solo cifre)
    def _on_paste(self, event):
        try:
            txt = self.selection_get(selection='CLIPBOARD')
        except Exception:
            return "break"
        digits = ''.join(c for c in txt if c.isdigit())
        if not digits:
            return "break"
        idx = self._cursor_digit_index()
        space = self.max_digits - len(self.digits)
        to_insert = digits[:space]
        for i, ch in enumerate(to_insert):
            self.digits.insert(idx + i, ch)
        new_idx_after = idx + len(to_insert) - 1
        if new_idx_after < 0:
            new_pos = self._digit_index_to_visual_pos_after(idx)
        else:
            new_pos = self._digit_index_to_visual_pos_after(new_idx_after)
        self._rebuild_display(set_cursor_pos=new_pos)
        return "break"

    # click/focus: se l'utente clicca su separatore lo sposto al prossimo campo cifra
    def _on_click(self, event):
        # lascio il default click posizionare il cursore, poi correggo subito dopo
        self.after(1, self._fix_cursor_after_click)
        return None

    def _on_focus_in(self, event):
        self.after(1, self._fix_cursor_after_click)

    def _fix_cursor_after_click(self):
        pos = self.index(tk.INSERT)
        # se pos cade su una separazione (ad esempio 2 o 5) spostalo al prossimo digit pos
        if pos in self.sep_positions:
            for p in self.digit_positions:
                if p >= pos:
                    self.icursor(p)
                    return
            self.icursor(self.visual_len)
            return
        # clamp
        if pos > self.visual_len:
            self.icursor(self.visual_len)

    # valore da usare nel parsing: se incompleto restituisce '' (in modo che parse_date/time fallisca)
    def get_value(self):
        if len(self.digits) == self.max_digits:
            chars = [self.placeholder] * self.visual_len
            for pos, sep in self.sep_positions.items():
                chars[pos] = sep
            for i, d in enumerate(self.digits):
                chars[self.digit_positions[i]] = d
            return ''.join(chars)
        return ''

    # utilità per impostare un valore (es. caricamento)
    def set_value(self, s):
        digits = ''.join(c for c in s if c.isdigit())
        self.digits = list(digits[:self.max_digits])
        self._rebuild_display()

# -------------------- GUI principale --------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV Generator per Google Calendar")
        self.configure(padx=18, pady=18)
        self.geometry("")  # auto-size
        self.minsize(600, 420)
        self._build_ui()
        self.center_window()

    def center_window(self):
        self.update_idletasks()
        w = self.winfo_width(); h = self.winfo_height()
        sw = self.winfo_screenwidth(); sh = self.winfo_screenheight()
        x = (sw // 2) - (w // 2); y = (sh // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        pad = 10
        container = ttk.Frame(self, padding=pad)
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)

        # Date (maschera unica)
        date_frame = ttk.LabelFrame(container, text="Intervallo date (DD/MM/YYYY)", padding=8)
        date_frame.grid(column=0, row=0, sticky=tk.N, pady=(0,8))
        self.start_date = MaskedEntry(date_frame, mask='DD/MM/YYYY', width=12)
        self.start_date.grid(column=0, row=0, sticky=tk.W, padx=(6,6))
        self.end_date = MaskedEntry(date_frame, mask='DD/MM/YYYY', width=12)
        self.end_date.grid(column=1, row=0, sticky=tk.W, padx=(6,6))

        # Orari
        time_frame = ttk.LabelFrame(container, text="Orari (HH:MM)", padding=8)
        time_frame.grid(column=0, row=1, sticky=tk.N, pady=(0,8))
        ttk.Label(time_frame, text="Mattina inizio").grid(column=0, row=0, sticky=tk.W, padx=(4,8))
        self.morning_start = MaskedEntry(time_frame, mask='HH:MM', width=6)
        self.morning_start.grid(column=1, row=0, sticky=tk.W)
        ttk.Label(time_frame, text="Mattina fine").grid(column=2, row=0, sticky=tk.W, padx=(16,8))
        self.morning_end = MaskedEntry(time_frame, mask='HH:MM', width=6)
        self.morning_end.grid(column=3, row=0, sticky=tk.W)

        ttk.Label(time_frame, text="Pomeriggio inizio").grid(column=0, row=1, sticky=tk.W, padx=(4,8), pady=(6,0))
        self.afternoon_start = MaskedEntry(time_frame, mask='HH:MM', width=6)
        self.afternoon_start.grid(column=1, row=1, sticky=tk.W, pady=(6,0))
        ttk.Label(time_frame, text="Pomeriggio fine").grid(column=2, row=1, sticky=tk.W, padx=(16,8), pady=(6,0))
        self.afternoon_end = MaskedEntry(time_frame, mask='HH:MM', width=6)
        self.afternoon_end.grid(column=3, row=1, sticky=tk.W, pady=(6,0))

        # durata
        dur_frame = ttk.Frame(container, padding=(0,4))
        dur_frame.grid(column=0, row=2, sticky=tk.W, pady=(0,6))
        ttk.Label(dur_frame, text="Durata (minuti):").grid(column=0, row=0, sticky=tk.W)
        self.duration_spin = ttk.Spinbox(dur_frame, from_=5, to=480, increment=5, width=6)
        self.duration_spin.set(30)
        self.duration_spin.grid(column=1, row=0, sticky=tk.W, padx=(8,0))

        # giorni settimana
        dow_frame = ttk.LabelFrame(container, text="Giorni della settimana (includi)", padding=8)
        dow_frame.grid(column=0, row=3, sticky=tk.W, pady=(0,8))
        self.week_vars = []
        days = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
        for i, d in enumerate(days):
            var = tk.IntVar(value=1)
            cb = ttk.Checkbutton(dow_frame, text=d, variable=var)
            cb.grid(column=i, row=0, sticky=tk.W, padx=4)
            self.week_vars.append(var)

        # esclusione orari
        excl_frame = ttk.Frame(container, padding=(0,4))
        excl_frame.grid(column=0, row=4, sticky=tk.EW, pady=(0,6))
        ttk.Label(excl_frame, text="Escludi orari di inizio (HH:MM separati da , )").grid(column=0, row=0, sticky=tk.W)
        self.exclude_entry = ttk.Entry(excl_frame)
        self.exclude_entry.grid(column=1, row=0, sticky=tk.EW, padx=(8,0))
        excl_frame.columnconfigure(1, weight=1)

        # pulsanti
        btn_frame = ttk.Frame(container)
        btn_frame.grid(column=0, row=5, sticky=tk.EW, pady=(6,0))
        for i in range(3):
            btn_frame.columnconfigure(i, weight=1)
        self.preview_btn = ttk.Button(btn_frame, text="Anteprima (mostra primi 20)", command=self.on_preview)
        self.preview_btn.grid(column=0, row=0, sticky=tk.EW, padx=4)
        self.save_btn = ttk.Button(btn_frame, text="Salva CSV", command=self.on_save)
        self.save_btn.grid(column=1, row=0, sticky=tk.EW, padx=4)
        self.quit_btn = ttk.Button(btn_frame, text="Esci", command=self.destroy)
        self.quit_btn.grid(column=2, row=0, sticky=tk.EW, padx=4)

        # preview
        preview_frame = ttk.LabelFrame(container, text="Preview eventi", padding=8)
        preview_frame.grid(column=0, row=6, sticky=tk.NSEW, pady=(8,0))
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        self.preview_text = tk.Text(preview_frame, height=12, wrap=tk.NONE)
        self.preview_text.grid(column=0, row=0, sticky=tk.NSEW)
        vsb = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        vsb.grid(column=1, row=0, sticky=tk.NS)
        hsb = ttk.Scrollbar(preview_frame, orient=tk.HORIZONTAL, command=self.preview_text.xview)
        hsb.grid(column=0, row=1, sticky=tk.EW)
        self.preview_text.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # hint
        hint = ttk.Label(container, text="Input: digitare solo numeri. I separatori (/ e :) vengono inseriti automaticamente.", foreground="#555")
        hint.grid(column=0, row=7, sticky=tk.W, pady=(6,0))

    # raccolta input
    def _gather_inputs(self):
        sd = parse_date(self.start_date.get_value())
        ed = parse_date(self.end_date.get_value())
        ms = parse_time(self.morning_start.get_value())
        me = parse_time(self.morning_end.get_value())
        ps = parse_time(self.afternoon_start.get_value())
        pe = parse_time(self.afternoon_end.get_value())
        try:
            duration = int(self.duration_spin.get())
        except Exception:
            duration = None

        weekdays_allowed = [i for i, v in enumerate(self.week_vars) if v.get() == 1]
        if len(weekdays_allowed) == 7:
            weekdays_allowed = None

        excl_raw = self.exclude_entry.get().strip()
        exclude_list = []
        if excl_raw:
            for part in excl_raw.split(','):
                t = parse_time(part.strip())
                if t:
                    exclude_list.append(t.strftime('%H:%M'))

        return sd, ed, ms, me, ps, pe, duration, weekdays_allowed, exclude_list

    # validazione semplice
    def _validate(self, sd, ed, ms, me, ps, pe, duration):
        if not sd or not ed:
            messagebox.showerror("Errore", "Date non valide. Usa DD/MM/YYYY (campo completo).")
            return False
        if ed < sd:
            messagebox.showerror("Errore", "La data fine deve essere >= data inizio.")
            return False
        if duration is None or duration <= 0:
            messagebox.showerror("Errore", "Durata non valida.")
            return False
        if not any([ms and me, ps and pe]):
            messagebox.showerror("Errore", "Serve almeno un intervallo (mattina o pomeriggio) valido.")
            return False
        if ms and me and datetime.combine(date.today(), ms) >= datetime.combine(date.today(), me):
            messagebox.showerror("Errore", "Mattina: ora inizio deve essere < ora fine")
            return False
        if ps and pe and datetime.combine(date.today(), ps) >= datetime.combine(date.today(), pe):
            messagebox.showerror("Errore", "Pomeriggio: ora inizio deve essere < ora fine")
            return False
        return True

    # anteprima
    def on_preview(self):
        sd, ed, ms, me, ps, pe, duration, weekdays_allowed, exclude_list = self._gather_inputs()
        if not self._validate(sd, ed, ms, me, ps, pe, duration):
            return
        slots = generate_slots(sd, ed, ms, me, ps, pe, duration, weekdays_allowed, exclude_list)
        self.preview_text.delete('1.0', tk.END)
        if not slots:
            self.preview_text.insert(tk.END, "Nessun evento generato con i parametri forniti.\n")
            return
        self.preview_text.insert(tk.END, f"Totale eventi: {len(slots)}\n\n")
        for i, s in enumerate(slots[:200]):  # mostro fino a 200 se richiesto
            # s[0] è ISO YYYY-MM-DD, lo mostro in DD/MM/YYYY per coerenza con l'UI
            d_disp = datetime.strptime(s[0], "%Y-%m-%d").strftime("%d/%m/%Y")
            self.preview_text.insert(tk.END, f"{i+1:03d}. {d_disp} {s[1]} -> {s[3]}\n")

    # salva CSV (formato compatibile Google Calendar: Start Date in YYYY-MM-DD)
    def on_save(self):
        sd, ed, ms, me, ps, pe, duration, weekdays_allowed, exclude_list = self._gather_inputs()
        if not self._validate(sd, ed, ms, me, ps, pe, duration):
            return
        slots = generate_slots(sd, ed, ms, me, ps, pe, duration, weekdays_allowed, exclude_list)
        if not slots:
            messagebox.showinfo("Info", "Nessun evento da salvare.")
            return

        fpath = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV file', '*.csv')],
                                             title='Salva CSV come')
        if not fpath:
            return

        try:
            with open(fpath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Subject','Start Date','Start Time','End Date','End Time','Description','Location'])
                for s in slots:
                    writer.writerow(['', s[0], s[1], s[2], s[3], '', ''])
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile salvare il file: {e}")
            return

        messagebox.showinfo("Fatto", f"CSV salvato: {fpath}")
        if messagebox.askyesno("Apri cartella", "Vuoi aprire la cartella contenente il file?"):
            folder = os.path.dirname(fpath)
            if sys.platform.startswith('win'):
                os.startfile(folder)
            elif sys.platform.startswith('darwin'):
                os.system(f'open \"{folder}\"')
            else:
                os.system(f'xdg-open \"{folder}\"')

# --- entry point ---
if __name__ == '__main__':
    app = App()
    app.mainloop()
