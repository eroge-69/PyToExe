import datetime as dt
import json
import pathlib
import queue
import threading
import time
import tkinter as tk
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk

import matplotlib
from gigachat import GigaChat
from markdown import markdown
from tkcalendar import DateEntry
from tkhtmlview import HTMLScrolledText

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

CONFIG_PATH = pathlib.Path("habit_config.json")
DEFAULT_CONFIG = {
    "giga_credentials": "",
    "verify_ssl_certs": True,
    "scope": "GIGACHAT_API_PERS",
}


def load_cfg():
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    CONFIG_PATH.write_text(
        json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return DEFAULT_CONFIG.copy()


def save_cfg(cfg):
    CONFIG_PATH.write_text(
        json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8"
    )


CFG = load_cfg()


class PlaceholderEntry(ttk.Entry):
    def __init__(self, master, placeholder: str, textvariable=None, **kw):
        super().__init__(master, textvariable=textvariable, **kw)
        self.placeholder = placeholder
        self._var = textvariable or tk.StringVar()
        self.config(textvariable=self._var)
        self._show()
        self.bind("<FocusIn>", self._clear)
        self.bind("<FocusOut>", self._show)

    def _clear(self, *_):
        if self._var.get() == self.placeholder:
            self._var.set("")
            self.configure(style="TEntry")

    def _show(self, *_):
        if not self._var.get():
            self._var.set(self.placeholder)
            self.configure(style="placeholder.TEntry")

    def real_value(self):
        val = self._var.get().strip()
        return "" if val == self.placeholder else val


def fetch_gigachat(prompt, q: queue.Queue):
    try:
        with GigaChat(
            credentials=CFG["giga_credentials"],
            verify_ssl_certs=CFG["verify_ssl_certs"],
            scope=CFG["scope"],
        ) as giga:
            token = giga.get_token()
            ttl_sec = (token.expires_at / 1000) - time.time()
            resp = giga.chat(prompt)
            text = resp.choices[0].message.content.strip()
        q.put((True, text, ttl_sec))
    except Exception as e:
        q.put((False, str(e), 0))


class HabitApp(tk.Tk):
    DESC_PLACEHOLDER = "Напр.: Кофе на вынос"

    def __init__(self):
        super().__init__()
        self.title("Сколько стоит привычка?")
        self.resizable(False, False)
        ttk.Style(self).configure("placeholder.TEntry", foreground="#808080")

        ttk.Label(self, text="Цена одной покупки (₽):").grid(
            row=0, column=0, sticky="w"
        )
        self.price_var = tk.StringVar()
        PlaceholderEntry(self, "напр., 150", self.price_var, width=12).grid(
            row=0, column=1, padx=5, pady=2
        )

        ttk.Label(self, text="Сколько раз покупка совершается:").grid(
            row=1, column=0, sticky="w"
        )
        self.freq_var = tk.StringVar()
        PlaceholderEntry(self, "напр., 3", self.freq_var, width=12).grid(
            row=1, column=1, padx=5, pady=2
        )

        ttk.Label(self, text="Как часто происходит покупка?").grid(
            row=2, column=0, sticky="w", pady=(6, 0)
        )
        self.period_var = tk.StringVar(value="week")
        f_period = ttk.Frame(self)
        f_period.grid(row=2, column=1, columnspan=3, sticky="w")
        for v, t in [("day", "в день"), ("week", "в неделю"), ("month", "в месяц")]:
            ttk.Radiobutton(f_period, text=t, value=v, variable=self.period_var).pack(
                side="left", padx=6
            )

        ttk.Label(self, text="Описание привычки:").grid(row=3, column=0, sticky="w")
        self.desc_entry = PlaceholderEntry(self, self.DESC_PLACEHOLDER, width=25)
        self.desc_entry.grid(row=3, column=1, columnspan=3, sticky="we", padx=5, pady=2)

        self.use_date_var = tk.BooleanVar(master=self, value=False)
        ttk.Checkbutton(
            self,
            text="Учитывать дату",
            variable=self.use_date_var,
            command=self._toggle_date,
        ).grid(row=4, column=0, sticky="w")
        self.until_var = tk.StringVar()
        self.date_entry = DateEntry(
            self,
            textvariable=self.until_var,
            date_pattern="yyyy-mm-dd",
            mindate=dt.date.today(),
            state="disabled",
        )
        self.date_entry.grid(row=4, column=1, padx=5, pady=2, sticky="w")

        ttk.Button(self, text="Рассчитать", command=self.calculate).grid(
            row=5, column=0, padx=5, pady=6
        )
        ttk.Button(self, text="Копировать результат", command=self.copy_result).grid(
            row=5, column=1, pady=6
        )

        self.result_lbl = ttk.Label(self, text="", justify="left")
        self.result_lbl.grid(row=6, column=0, columnspan=4, sticky="w", padx=5)

        fig = Figure(figsize=(4, 2.7), dpi=100)
        self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=self)
        self.canvas.get_tk_widget().grid(row=7, column=0, columnspan=4, padx=5, pady=5)

        self.status = ttk.Label(self, text="Токен не получен", anchor="w")
        self.status.grid(row=8, column=0, columnspan=4, sticky="we")

        m = tk.Menu(self)
        s = tk.Menu(m, tearoff=0)
        s.add_command(label="Данные GigaChat…", command=self.open_settings)
        m.add_cascade(label="Настройки", menu=s)
        self.config(menu=m)

        self._queue = queue.Queue()
        self.after(200, self._check_queue)
        self.last_analysis = ""

    def _toggle_date(self):
        if self.use_date_var.get():
            self.date_entry.config(state="readonly")
        else:
            self.date_entry.config(state="disabled")
            self.until_var.set("")

    def _rus_period(self):
        return {"day": "в день", "week": "в неделю", "month": "в месяц"}[
            self.period_var.get()
        ]

    def calculate(self):
        try:
            price = Decimal(self.price_var.get().replace(",", "."))
            freq = Decimal(self.freq_var.get().replace(",", "."))
            if price <= 0 or freq <= 0:
                raise InvalidOperation
        except InvalidOperation:
            messagebox.showerror("Ошибка", "Введите корректную цену и частоту.")
            return
        if self.period_var.get() == "":
            messagebox.showerror("Ошибка", "Выберите период.")
            return

        if self.use_date_var.get() and self.until_var.get():
            until = dt.datetime.strptime(self.until_var.get(), "%Y-%m-%d").date()
            delta = (until - dt.date.today()).days
            if delta <= 0:
                messagebox.showerror("Дата", "Дата должна быть в будущем.")
                return
            per_map = {"day": 1, "week": 7, "month": 30}
            purchases = (delta / per_map[self.period_var.get()]) * freq
            cost1, cost5 = price * purchases, None
            label1 = f"До {until.isoformat()}"
        else:
            per_y = {"day": 365, "week": 52, "month": 12}[self.period_var.get()]
            cost1 = price * freq * per_y
            cost5 = cost1 * 5
            label1 = "1 год"

        if cost5:
            self.result_lbl.config(
                text=f"Вы тратите {cost1:,.2f} ₽ в год\nи {cost5:,.2f} ₽ за 5 лет.".replace(
                    ",", " "
                )
            )
            self._draw_pair(cost1, cost5, (label1, "5 лет"))
        else:
            self.result_lbl.config(text=f"{label1}: {cost1:,.2f} ₽".replace(",", " "))
            self._draw_single(cost1, label1)

        desc = self.desc_entry.real_value()
        if CFG["giga_credentials"] and desc:
            prompt = (
                f"Привычка: {desc}. Цена {price} ₽, {freq} раз {self._rus_period()}. "
                f"Суммарный расход: {cost1:,.0f} ₽ "
                f"{('(до '+label1+')') if cost5 is None else 'в год'}. "
                "Верни ровно 3 плюса, 3 минуса и 3 альтернативы "
                "строго по шаблону Markdown."
            )
            self._wait_win = self._show_wait()
            threading.Thread(
                target=fetch_gigachat, args=(prompt, self._queue), daemon=True
            ).start()

    def _draw_pair(self, y1, y2, labels):
        self.ax.clear()
        bars = self.ax.bar(labels, [y1, y2], color="#0077cc")
        self.ax.set_ylabel("Расход, ₽")
        self.ax.set_title("Стоимость привычки")
        for b, v in zip(bars, [y1, y2]):
            self.ax.annotate(
                f"{v:,.0f}".replace(",", " "),
                xy=(b.get_x() + b.get_width() / 2, v),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
            )
        self.canvas.draw_idle()

    def _draw_single(self, val, label):
        self.ax.clear()
        bar = self.ax.bar([label], [val], color="#0077cc")[0]
        self.ax.set_ylabel("Расход, ₽")
        self.ax.set_title("Стоимость привычки")
        self.ax.annotate(
            f"{val:,.0f}".replace(",", " "),
            xy=(bar.get_x() + bar.get_width() / 2, val),
            xytext=(0, 3),
            textcoords="offset points",
            ha="center",
            va="bottom",
        )
        self.canvas.draw_idle()

    def copy_result(self):
        combined = self.result_lbl.cget("text")
        if self.last_analysis:
            combined += "\n\n" + self.last_analysis

        self.clipboard_clear()
        self.clipboard_append(combined)
        messagebox.showinfo("Скопировано", "Результат и анализ в буфере обмена.")

    def _show_answer(self, md_text: str):
        self.last_analysis = md_text

        win = tk.Toplevel(self)
        win.title("Анализ")
        win.resizable(True, True)

        html = markdown(md_text, extensions=["extra", "sane_lists"])

        viewer = HTMLScrolledText(
            win, html=html, width=70, height=30, background="white"
        )
        viewer.pack(expand=True, fill="both", padx=8, pady=8)

        win.update_idletasks()
        win.geometry(
            f"+{self.winfo_rootx() - win.winfo_width() - 20}"
            f"+{self.winfo_rooty() + 60}"
        )

    def _show_wait(self):
        w = tk.Toplevel(self)
        w.title("GigaChat")
        w.grab_set()
        ttk.Label(w, text="Пожалуйста, подождите…").pack(padx=10, pady=5)
        pb = ttk.Progressbar(w, mode="indeterminate", length=200)
        pb.pack(pady=5)
        pb.start(10)
        w.update_idletasks()
        w.geometry(f"+{self.winfo_rootx()-w.winfo_width()-20}+{self.winfo_rooty()+20}")
        return w

    def _check_queue(self):
        try:
            ok, data, ttl = self._queue.get_nowait()
            if hasattr(self, "_wait_win") and self._wait_win.winfo_exists():
                self._wait_win.destroy()
            if ok:
                self._show_answer(data)
                self.status.config(text=f"Токен жив ещё: {int(ttl//60)} мин")
            else:
                messagebox.showerror("GigaChat", data)
        except queue.Empty:
            pass
        self.after(200, self._check_queue)

    def open_settings(self):
        win = tk.Toplevel(self)
        win.title("Настройки GigaChat")
        win.resizable(False, False)
        pad = {"padx": 5, "pady": 5}
        cred = tk.StringVar(value=CFG["giga_credentials"])
        ttk.Label(win, text="Authorization-Key:").grid(
            row=0, column=0, sticky="w", **pad
        )
        ent = ttk.Entry(win, textvariable=cred, show="*", width=42)
        ent.grid(row=0, column=1, **pad)
        ttk.Button(
            win,
            text="👁",
            width=3,
            command=lambda: ent.config(show="" if ent.cget("show") else "*"),
        ).grid(row=0, column=2, **pad)
        sslv = tk.BooleanVar(value=CFG["verify_ssl_certs"])
        ttk.Checkbutton(win, text="Проверять TLS-сертификаты", variable=sslv).grid(
            row=1, column=0, columnspan=3, sticky="w", **pad
        )
        scopev = tk.StringVar(value=CFG["scope"])
        ttk.Label(win, text="Scope API:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Combobox(
            win,
            textvariable=scopev,
            values=["GIGACHAT_API_PERS", "GIGACHAT_API_B2B", "GIGACHAT_API_CORP"],
            state="readonly",
        ).grid(row=2, column=1, sticky="w", **pad)
        ttk.Button(
            win,
            text="Сохранить",
            command=lambda: (
                CFG.update(
                    {
                        "giga_credentials": cred.get().strip(),
                        "verify_ssl_certs": bool(sslv.get()),
                        "scope": scopev.get(),
                    }
                ),
                save_cfg(CFG),
                messagebox.showinfo("OK", "Сохранено."),
                win.destroy(),
            ),
        ).grid(row=3, column=0, columnspan=3, pady=5)

    def _is_number(self, s: str) -> bool:
        return s == "" or s.replace(",", ".", 1).replace(".", "", 1).isdigit()


if __name__ == "__main__":
    HabitApp().mainloop()
