#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generatore GUI di immagini a strisce nere e colorate.

Definizione angolo:
- angle_deg è l'orientamento delle STRISCE (non della normale), in gradi,
  misurato antiorario rispetto all'asse orizzontale.
  0° = strisce orizzontali, 90° = strisce verticali.

Dipendenze: numpy, Pillow (pip install numpy pillow)
"""

import os
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from datetime import datetime

import numpy as np
from PIL import Image, ImageTk


# ---------------------------- Logica immagine ---------------------------- #

def generate_stripes(width, height, black_w, color_w, rgb_color, angle_deg):
    """Ritorna un oggetto PIL.Image con pattern a strisce.
    width, height: dimensioni finali in px
    black_w, color_w: larghezze (px) di bande nere e colorate
    rgb_color: tuple (R,G,B) 0..255
    angle_deg: orientamento strisce (0°=orizzontali, 90°=verticali)
    """
    if width <= 0 or height <= 0:
        raise ValueError("Dimensioni immagine non valide.")
    if black_w <= 0 or color_w <= 0:
        raise ValueError("Le larghezze delle strisce devono essere > 0.")

    period = float(black_w + color_w)

    # Coordinate centrate
    x = np.arange(width) - (width - 1) / 2.0
    y = np.arange(height) - (height - 1) / 2.0
    X, Y = np.meshgrid(x, y)

    theta = math.radians(angle_deg)
    phi = theta + math.pi / 2.0  # angolo della normale alle strisce

    # Distanza lungo la normale (linee equispaziate)
    t = X * math.cos(phi) + Y * math.sin(phi)

    # Riduci a un periodo [0, period)
    s = np.mod(t, period)

    # Sotto black_w -> nero, altrimenti colore
    mask_color = s >= black_w

    img = np.zeros((height, width, 3), dtype=np.uint8)
    img[mask_color] = np.array(rgb_color, dtype=np.uint8)
    return Image.fromarray(img, mode="RGB")


# ---------------------------- Interfaccia Grafica ---------------------------- #

class StripesApp(tk.Tk):
    PREVIEW_MAX_W = 640
    PREVIEW_MAX_H = 480

    def __init__(self):
        super().__init__()
        self.title("Generatore Strisce - PNG/BMP")
        self.geometry("+120+80")
        self.minsize(900, 520)

        # Variabili Tk
        self.var_width   = tk.IntVar(value=1200)
        self.var_height  = tk.IntVar(value=800)
        self.var_bw      = tk.IntVar(value=20)   # black width
        self.var_cw      = tk.IntVar(value=20)   # color width
        self.var_r       = tk.IntVar(value=0)
        self.var_g       = tk.IntVar(value=120)
        self.var_b       = tk.IntVar(value=255)
        self.var_angle   = tk.DoubleVar(value=90.0)
        self.var_format  = tk.StringVar(value="png")  # 'png' o 'bmp'

        # Stato preview
        self.preview_image = None
        self.preview_photo = None

        # UI
        self._build_ui()

        # Prima anteprima
        self.update_preview()

    # --- UI layout ---
    def _build_ui(self):
        # Contenitori
        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        left = ttk.Frame(frm)
        left.pack(side="left", fill="y", padx=(0, 12))

        right = ttk.Frame(frm)
        right.pack(side="right", fill="both", expand=True)

        # --- Pannello parametri ---
        g_dims = ttk.Labelframe(left, text="Dimensioni immagine (px)")
        g_dims.pack(fill="x", pady=6)
        self._row(g_dims, "Larghezza", self.var_width, from_=1, to=20000, step=1)
        self._row(g_dims, "Altezza",   self.var_height, from_=1, to=20000, step=1)

        g_bands = ttk.Labelframe(left, text="Strisce (pixel)")
        g_bands.pack(fill="x", pady=6)
        self._row(g_bands, "Nere (larghezza)", self.var_bw, from_=1, to=2000, step=1)
        self._row(g_bands, "Colorate (larghezza)", self.var_cw, from_=1, to=2000, step=1)

        g_color = ttk.Labelframe(left, text="Colore strisce colorate (RGB 8 bit)")
        g_color.pack(fill="x", pady=6)
        self._rgb_row(g_color)
        ttk.Button(g_color, text="Scegli colore…", command=self.pick_color).pack(pady=(6,0), fill="x")

        g_angle = ttk.Labelframe(left, text="Orientamento strisce (gradi)")
        g_angle.pack(fill="x", pady=6)
        s = ttk.Scale(g_angle, from_=0.0, to=180.0, variable=self.var_angle, command=lambda _=None: self._debounced_preview())
        s.pack(fill="x", padx=4, pady=6)
        ttk.Label(g_angle, textvariable=self.var_angle, width=6).pack()

        g_fmt = ttk.Labelframe(left, text="Formato di salvataggio")
        g_fmt.pack(fill="x", pady=6)
        ttk.Radiobutton(g_fmt, text="PNG", variable=self.var_format, value="png").pack(anchor="w")
        ttk.Radiobutton(g_fmt, text="Bitmap (BMP)", variable=self.var_format, value="bmp").pack(anchor="w")

        # Pulsanti
        btns = ttk.Frame(left)
        btns.pack(fill="x", pady=10)
        ttk.Button(btns, text="Aggiorna anteprima", command=self.update_preview).pack(fill="x")
        ttk.Button(btns, text="Salva…", command=self.save_image).pack(fill="x", pady=(6,0))

        # --- Area anteprima ---
        right_top = ttk.Frame(right)
        right_top.pack(fill="both", expand=True)

        self.preview_label = ttk.Label(right_top, text="Anteprima")
        self.preview_label.pack(anchor="w")

        self.preview_panel = ttk.Label(right_top, relief="solid")
        self.preview_panel.pack(fill="both", expand=True, padx=4, pady=4)

        help_txt = (
            "Suggerimenti:\n"
            "• 0° = strisce orizzontali, 90° = verticali.\n"
            "• L’anteprima è ridimensionata per la finestra; il file salvato usa le dimensioni reali.\n"
            "• Usa ‘Salva…’ per scegliere la posizione e il formato (PNG/BMP)."
        )
        ttk.Label(right, text=help_txt, foreground="#555").pack(anchor="w", pady=(4,0))

        # Trigger anteprima quando cambiano i campi numerici
        for v in (self.var_width, self.var_height, self.var_bw, self.var_cw, self.var_r, self.var_g, self.var_b):
            v.trace_add("write", lambda *_: self._debounced_preview())

    def _row(self, parent, label, var, from_, to, step=1):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=4, pady=4)
        ttk.Label(row, text=label, width=20).pack(side="left")
        sp = ttk.Spinbox(row, from_=from_, to=to, textvariable=var, increment=step, width=10)
        sp.pack(side="left")

    def _rgb_row(self, parent):
        row = ttk.Frame(parent)
        row.pack(fill="x", padx=4, pady=4)
        ttk.Label(row, text="R", width=2).pack(side="left")
        ttk.Spinbox(row, from_=0, to=255, textvariable=self.var_r, width=5).pack(side="left", padx=(0,8))
        ttk.Label(row, text="G", width=2).pack(side="left")
        ttk.Spinbox(row, from_=0, to=255, textvariable=self.var_g, width=5).pack(side="left", padx=(0,8))
        ttk.Label(row, text="B", width=2).pack(side="left")
        ttk.Spinbox(row, from_=0, to=255, textvariable=self.var_b, width=5).pack(side="left")

    # --- Azioni ---
    def pick_color(self):
        initial = "#%02x%02x%02x" % (self.var_r.get(), self.var_g.get(), self.var_b.get())
        color = colorchooser.askcolor(initialcolor=initial, title="Scegli colore bande")
        if color and color[0]:
            r, g, b = map(int, color[0])
            self.var_r.set(r); self.var_g.set(g); self.var_b.set(b)

    def _get_params(self):
        try:
            W = int(self.var_width.get())
            H = int(self.var_height.get())
            bw = int(self.var_bw.get())
            cw = int(self.var_cw.get())
            rgb = (int(self.var_r.get()), int(self.var_g.get()), int(self.var_b.get()))
            angle = float(self.var_angle.get())
            fmt = self.var_format.get().lower()
            if fmt not in ("png", "bmp"):
                fmt = "png"
            # Validazioni rapide
            for v in rgb:
                if not (0 <= v <= 255):
                    raise ValueError("RGB fuori 0..255")
            return W, H, bw, cw, rgb, angle, fmt
        except Exception as e:
            raise ValueError(f"Parametri non validi: {e}")

    def update_preview(self):
        """Rigenera e mostra l'anteprima (ridotta)."""
        try:
            W, H, bw, cw, rgb, angle, _ = self._get_params()

            # Genera immagine alla risoluzione nativa poi riduci per anteprima
            img = generate_stripes(W, H, bw, cw, rgb, angle)

            # Ridimensiona per pannello anteprima
            panel_w = max(200, min(self.PREVIEW_MAX_W, self.preview_panel.winfo_width() or self.PREVIEW_MAX_W))
            panel_h = max(150, min(self.PREVIEW_MAX_H, self.preview_panel.winfo_height() or self.PREVIEW_MAX_H))
            preview = img.copy()
            preview.thumbnail((panel_w, panel_h), Image.LANCZOS)

            self.preview_image = preview
            self.preview_photo = ImageTk.PhotoImage(preview)
            self.preview_panel.configure(image=self.preview_photo)
            self.preview_label.configure(text=f"Anteprima ({preview.width}×{preview.height})")
        except Exception as e:
            self.preview_panel.configure(image="", text=f"Errore anteprima:\n{e}")

    def save_image(self):
        """Chiede dove salvare e scrive il file PNG/BMP completo."""
        try:
            W, H, bw, cw, rgb, angle, fmt = self._get_params()

            # Nome suggerito
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            base = f"stripes_{W}x{H}_bw{bw}_cw{cw}_rgb{rgb[0]}-{rgb[1]}-{rgb[2]}_ang{angle:.1f}_{ts}"
            defext = ".png" if fmt == "png" else ".bmp"

            filetypes = [("PNG", "*.png"), ("Bitmap", "*.bmp")]
            initialfile = base + defext
            path = filedialog.asksaveasfilename(
                title="Salva immagine",
                defaultextension=defext,
                filetypes=filetypes,
                initialfile=initialfile,
            )
            if not path:
                return

            # Rispetta l'estensione scelta manualmente
            ext = os.path.splitext(path)[1].lower()
            out_fmt = "PNG" if ext == ".png" else "BMP"

            img = generate_stripes(W, H, bw, cw, rgb, angle)

            if out_fmt == "PNG":
                img.save(path, format="PNG", compress_level=6)
            else:
                img.save(path, format="BMP")

            messagebox.showinfo("Salvato", f"Immagine salvata:\n{path}")
        except Exception as e:
            messagebox.showerror("Errore salvataggio", str(e))

    # Semplice debounce per non rigenerare ad ogni singolo tick
    def _debounced_preview(self):
        if hasattr(self, "_preview_after_id"):
            self.after_cancel(self._preview_after_id)
        self._preview_after_id = self.after(250, self.update_preview)


if __name__ == "__main__":
    app = StripesApp()
    app.mainloop()
