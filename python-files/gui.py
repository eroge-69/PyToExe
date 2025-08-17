# -*- coding: utf-8 -*-
import os
import sys
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

APP_TITLE = "Roblox Coins v1.17"
LOGO_DEFAULT_PATH = "roblox_logo.png"  # ضع الصورة بجانب الملف إن رغبت

class RobloxDemoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("560x420")
        self.minsize(520, 380)
        self.configure(bg="#0b0f16")
        self.iconbitmap(False, self._maybe_get_iconbitmap()) if hasattr(self, 'iconbitmap') else None

        # تهيئة نمط ttk (Dark Style)
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass
        self._setup_dark_theme()

        self.logo_img = None
        self._build_ui()
        self._attempt_load_default_logo()

    def _maybe_get_iconbitmap(self):
        # في بعض الأنظمة، يمكن ضبط أيقونة النافذة إذا كانت متاحة
        return ""

    def _setup_dark_theme(self):
        fg = "#e6eaf2"
        bg = "#0b0f16"
        card = "#121826"
        accent = "#7aa2ff"
        accent2 = "#3ddc97"
        danger = "#ff4d4f"

        self.style.configure("TFrame", background=card)
        self.style.configure("Card.TFrame", background=card)
        self.style.configure("TLabel", background=card, foreground=fg, font=("Segoe UI", 11))
        self.style.configure("Title.TLabel", font=("Segoe UI Semibold", 16))
        self.style.configure("Sub.TLabel", font=("Segoe UI", 10), foreground="#b8c0cc")
        self.style.configure("TButton", font=("Segoe UI Semibold", 11), padding=8)
        self.style.map("TButton",
                       background=[("active", accent)],
                       foreground=[("disabled", "#777"), ("!disabled", fg)])
        self.style.configure("Accent.TButton", background=accent)
        self.style.configure("Ok.TButton", background=accent2)
        self.style.configure("Danger.TButton", background=danger)
        self.style.configure("TEntry", fieldbackground="#0a0e15", foreground=fg)
        self.style.configure("TProgressbar", troughcolor="#0a0e15", background=accent)

        # إطار الحاوية الأساسي
        self.root_frame = ttk.Frame(self, style="Card.TFrame", padding=16)
        self.root_frame.pack(fill="both", expand=True)

    def _build_ui(self):
        # رأس التطبيق
        header = ttk.Frame(self.root_frame, padding=(12, 12, 12, 6))
        header.pack(fill="x")

        self.logo_label = ttk.Label(header)
        self.logo_label.pack(side="left", padx=(0, 12))

        title_box = ttk.Frame(header)
        title_box.pack(side="left", fill="x", expand=True)
        ttk.Label(title_box, text="Roblox Coins", style="Title.TLabel").pack(anchor="w")
        ttk.Label(title_box, text="", style="Sub.TLabel").pack(anchor="w", pady=(2,0))

        choose_logo_btn = ttk.Button(header, text="اختر شعار", command=self._choose_logo)
        choose_logo_btn.pack(side="right")

        # بطاقة الإدخال
        card = ttk.Frame(self.root_frame, padding=16, style="Card.TFrame")
        card.pack(fill="x", pady=(8, 12))

        ttk.Label(card, text="كمية العملات المطلوبة للحقن").grid(row=0, column=0, sticky="w")
        self.amount_var = tk.StringVar(value="1000")
        vcmd = (self.register(self._validate_digits), "%P")
        self.amount_entry = ttk.Entry(card, textvariable=self.amount_var, validate="key", validatecommand=vcmd, width=22)
        self.amount_entry.grid(row=1, column=0, sticky="w")

        self.note_label = ttk.Label(card, text="أدخل قيمة رقمية فقط.", style="Sub.TLabel")
        self.note_label.grid(row=2, column=0, sticky="w", pady=(6, 0))

        # أزرار التحكم
        buttons = ttk.Frame(self.root_frame, padding=8)
        buttons.pack(fill="x")

        self.inject_btn = ttk.Button(buttons, text="🚀 Inject", style="Accent.TButton", command=self._simulate_inject)
        self.inject_btn.pack(side="left")

        self.reset_btn = ttk.Button(buttons, text="إعادة تعيين", style="TButton", command=self._reset_ui)
        self.reset_btn.pack(side="left", padx=(8, 0))

        self.exit_btn = ttk.Button(buttons, text="خروج", style="Danger.TButton", command=self.destroy)
        self.exit_btn.pack(side="right")

        # الشريط السفلي + التقدم
        footer = ttk.Frame(self.root_frame, padding=(8, 12))
        footer.pack(fill="x", side="bottom")

        self.progress = ttk.Progressbar(footer, mode="determinate", maximum=100)
        self.progress.pack(fill="x")

        self.status_var = tk.StringVar(value="جاهز")
        self.status_label = ttk.Label(footer, textvariable=self.status_var, style="Sub.TLabel")
        self.status_label.pack(anchor="w", pady=(6, 0))

    def _validate_digits(self, proposed: str) -> bool:
        if proposed == "":
            return True
        return proposed.isdigit()

    def _attempt_load_default_logo(self):
        if os.path.exists(LOGO_DEFAULT_PATH):
            self._set_logo(LOGO_DEFAULT_PATH)
        else:
            # شعار نصي بسيط إن لم تتوفر صورة
            self.logo_label.configure(text="▢", font=("Segoe UI", 32))

    def _choose_logo(self):
        filetypes = [
            ("صور", "*.png *.jpg *.jpeg *.webp *.gif"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg;*.jpeg"),
            ("WEBP", "*.webp"),
            ("GIF", "*.gif"),
            ("كل الملفات", "*.*"),
        ]
        path = filedialog.askopenfilename(title="اختر صورة الشعار", filetypes=filetypes)
        if path:
            self._set_logo(path)

    def _set_logo(self, path: str):
        try:
            if PIL_AVAILABLE:
                img = Image.open(path)
                # تصغير الشعار بشكل متناسب
                img.thumbnail((64, 64), Image.LANCZOS)
                self.logo_img = ImageTk.PhotoImage(img)
            else:
                # في حال عدم توفر PIL، نحاول مع PhotoImage (يدعم PNG/GIF في الغالب)
                self.logo_img = tk.PhotoImage(file=path)
            self.logo_label.configure(image=self.logo_img, text="")
        except Exception as e:
            self.logo_img = None
            self.logo_label.configure(text="▢", font=("Segoe UI", 32))
            messagebox.showwarning("تعذر تحميل الشعار", f"تعذر قراءة الصورة:\n{e}")

    def _simulate_inject(self):
        amount_text = self.amount_var.get().strip()
        if not amount_text or not amount_text.isdigit():
            messagebox.showerror("قيمة غير صالحة", "من فضلك أدخل رقماً صحيحاً.")
            return

        amount = int(amount_text)
        if amount <= 0:
            messagebox.showerror("قيمة غير صالحة", "القيمة يجب أن تكون أكبر من صفر.")
            return
        if amount > 10_000_000:
            if not messagebox.askyesno(
                "قيمة كبيرة",
                "أدخلت قيمة كبيرة جداً.",
            ):
                return

        self._lock_controls(True)
        self.status_var.set("(لا يوجد اتصال بأي لعبة)")
        self.progress['value'] = 0

        # تقدم تدريجي لطيف
        steps = [5, 12, 18, 28, 39, 52, 68, 81, 92, 100]
        delay_ms = 160

        def step_update(i=0):
            if i < len(steps):
                self.progress['value'] = steps[i]
                self.after(delay_ms, step_update, i+1)
            else:
                self.status_var.set("تمت بنجاح ✅ .")
                messagebox.showinfo(
                    "نجاح ",
                    f""
                )
                self._lock_controls(False)
        step_update(0)

    def _reset_ui(self):
        self.amount_var.set("1000")
        self.progress['value'] = 0
        self.status_var.set("جاهز")

    def _lock_controls(self, locked: bool):
        state = tk.DISABLED if locked else tk.NORMAL
        for w in (self.inject_btn, self.reset_btn):
            w.configure(state=state)
        self.amount_entry.configure(state=state)


def main():
    app = RobloxDemoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
