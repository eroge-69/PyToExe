# -*- coding: utf-8 -*-
# UNN (Universal 1..32) -> FDI Zahnschema Visualizer (Tkinter)
# Entertaste löst Übersetzung aus, leert die Textbox
# UNN->FDI Mapping in Textbox
# Zahnschema mittig im Fenster

import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext

# Mapping Universal (1..32) -> FDI (bleibende Zähne)
UNN_TO_FDI = {
    "1": 18, "2": 17, "3": 16, "4": 15, "5": 14, "6": 13, "7": 12, "8": 11,
    "9": 21, "10": 22, "11": 23, "12": 24, "13": 25, "14": 26, "15": 27, "16": 28,
    "17": 38, "18": 37, "19": 36, "20": 35, "21": 34, "22": 33, "23": 32, "24": 31,
    "25": 41, "26": 42, "27": 43, "28": 44, "29": 45, "30": 46, "31": 47, "32": 48,
}

# Zeichen-Reihenfolge (oben 1|2, unten 4|3)
FDI_LAYOUT_TOP    = [18,17,16,15,14,13,12,11, 21,22,23,24,25,26,27,28]
FDI_LAYOUT_BOTTOM = [48,47,46,45,44,43,42,41, 31,32,33,34,35,36,37,38]

class ZahnschemaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UNN → FDI")
        self.geometry("1000x620")
        self.minsize(900, 560)

        self._build_ui()
        self.bind("<Configure>", self._on_resize)
        self._draw_schema()

    # ---------- UI ----------
    def _build_ui(self):
        container = ttk.Frame(self, padding=12)
        container.pack(fill="both", expand=True)

        ttk.Label(container, text="UNN-Eingabe:").pack(anchor="w")
        self.var_input = tk.StringVar()
        entry = ttk.Entry(container, textvariable=self.var_input)
        entry.pack(fill="x", pady=(4, 8))
        entry.focus_set()
        entry.bind("<Return>", self._on_enter)

        row = ttk.Frame(container)
        row.pack(fill="x", pady=(0, 8))
        ttk.Button(row, text="Übersetzen & anzeigen", command=self.on_translate).pack(side="left")
        ttk.Button(row, text="Zurücksetzen", command=self.on_reset).pack(side="left", padx=(8, 0))

        ttk.Label(container, text="Zuordnung UNN → FDI:").pack(anchor="w")
        self.txt_output = scrolledtext.ScrolledText(
            container,
            height=8,
            wrap="none",
            font=("Courier New", 10)
        )
        self.txt_output.pack(fill="x", pady=(2, 10))
        self._set_output_text("", readonly=True)

        canvas_frame = ttk.Frame(container)
        canvas_frame.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(fill="both", expand=True)

        self.tooth_items = {}
        self.selected_fdi = []

        # Basismaße
        self.base_tooth_w = 42
        self.base_tooth_h = 58
        self.base_cell_pad = 8
        self.base_mid_gap = 18
        self.base_top_margin = 28
        self.base_bottom_extra = 30
        self.base_title_y = 14

    # ---------- Parsing ----------
    @staticmethod
    def _normalize_token(tok):
        t = tok.strip()
        if not t:
            return None
        if t.isdigit():
            return str(int(t))
        return t

    @staticmethod
    def _parse_unn_list(s):
        tokens = re.split(r"[,\s;]+", s.strip())
        out, seen = [], set()
        for t in tokens:
            nt = ZahnschemaApp._normalize_token(t)
            if nt and nt not in seen:
                seen.add(nt)
                out.append(nt)
        return out

    # ---------- Zeichnen ----------
    def _compute_layout(self):
        cw = max(600, self.canvas.winfo_width())
        ref_w = 1000
        scale = max(0.7, min(1.6, cw / ref_w))

        TOOTH_W = int(self.base_tooth_w * scale)
        TOOTH_H = int(self.base_tooth_h * scale)
        CELL_PAD = int(self.base_cell_pad * scale)
        MID_GAP = int(self.base_mid_gap * scale)
        TOP_MARGIN = int(self.base_top_margin * scale)
        BOTTOM_EXTRA = int(self.base_bottom_extra * scale)
        TITLE_Y = int(self.base_title_y * scale)
        return TOOTH_W, TOOTH_H, CELL_PAD, MID_GAP, TOP_MARGIN, BOTTOM_EXTRA, TITLE_Y

    def _calc_total_width(self, n_teeth, tooth_w, cell_pad, mid_gap):
        """Gesamtbreite berechnen (inkl. Mittellücke)."""
        # 16 Zähne pro Reihe, nach 8 eine Mittellücke
        return n_teeth * (tooth_w + cell_pad) + mid_gap - cell_pad

    def _draw_schema(self):
        self.canvas.delete("all")
        self.tooth_items.clear()

        TOOTH_W, TOOTH_H, CELL_PAD, MID_GAP, TOP_MARGIN, BOTTOM_EXTRA, TITLE_Y = self._compute_layout()

        c_w = self.canvas.winfo_width()
        self.canvas.create_text(c_w/2, TITLE_Y, text="FDI-Zahnschema", font=("Arial", 12, "bold"))

        y_top = TOP_MARGIN + TITLE_Y
        y_bottom = y_top + TOOTH_H + CELL_PAD + BOTTOM_EXTRA

        # Gesamtbreite der Zähne berechnen
        total_w = self._calc_total_width(len(FDI_LAYOUT_TOP), TOOTH_W, CELL_PAD, MID_GAP)
        start_x_centered = (c_w - total_w) / 2

        def draw_row(fdi_row, y):
            x = start_x_centered
            for idx, fdi in enumerate(fdi_row):
                if idx == 8:
                    x += MID_GAP
                rect = self.canvas.create_rectangle(x, y, x+TOOTH_W, y+TOOTH_H,
                                                    outline="#888", width=1, fill="#f5f5f5")
                text = self.canvas.create_text(x+TOOTH_W/2, y+TOOTH_H/2, text=str(fdi),
                                               font=("Arial", max(9, int(11*TOOTH_W/42)), "bold"), fill="#333")
                self.tooth_items[str(fdi)] = (rect, text)
                x += TOOTH_W + CELL_PAD

        draw_row(FDI_LAYOUT_TOP, y_top)
        draw_row(FDI_LAYOUT_BOTTOM, y_bottom)

        self.canvas.create_text(c_w/2, y_bottom + TOOTH_H + CELL_PAD,
                                text="Grün = Ausgewählt (Eingabe)",
                                anchor="center", font=("Arial", 9))
        self._highlight_fdi(self.selected_fdi)

    def _highlight_fdi(self, fdi_list):
        for fdi_key, (rect_id, _text_id) in self.tooth_items.items():
            self.canvas.itemconfig(rect_id, fill="#f5f5f5", outline="#888", width=1)
        for fdi in fdi_list:
            key = str(fdi)
            if key in self.tooth_items:
                rect_id, _ = self.tooth_items[key]
                self.canvas.itemconfig(rect_id, fill="#a6e3a1", outline="#4caf50", width=2)

    # ---------- Output-Textbox ----------
    def _set_output_text(self, text, readonly=True):
        self.txt_output.configure(state="normal")
        self.txt_output.delete("1.0", "end")
        if text:
            self.txt_output.insert("1.0", text)
        if readonly:
            self.txt_output.configure(state="disabled")

    def _build_mapping_text(self, mapping_pairs, invalid_list):
        lines = []
        if mapping_pairs:
            lines.append("UNN  ->  FDI")
            lines.append("----------------")
            for unn_val, fdi_val in mapping_pairs:
                lines.append(f"{str(unn_val):>3}  ->  {str(fdi_val):<3}")
        else:
            lines.append("Keine gültigen UNN-Werte erkannt.")
        if invalid_list:
            lines.append("")
            lines.append("Ungültig: " + ", ".join(invalid_list))
        return "\n".join(lines)

    # ---------- Events ----------
    def _on_resize(self, _event):
        self._draw_schema()

    def _on_enter(self, event):
        self.on_translate()
        self.var_input.set("")   # Eingabefeld leeren

    def on_translate(self):
        raw = self.var_input.get()
        if not raw.strip():
            messagebox.showinfo("Hinweis", "Bitte UNN-Werte eingeben")
            return

        unn_tokens = self._parse_unn_list(raw)
        valid_unn, invalid = [], []
        for t in unn_tokens:
            if t in UNN_TO_FDI:
                valid_unn.append(t)
            else:
                invalid.append(t)

        mapping_pairs = [(u, UNN_TO_FDI[u]) for u in valid_unn]
        self.selected_fdi = [fd for (_, fd) in mapping_pairs]

        mapping_text = self._build_mapping_text(mapping_pairs, invalid)
        self._set_output_text(mapping_text, readonly=True)

        self._highlight_fdi(self.selected_fdi)

    def on_reset(self):
        self.var_input.set("")
        self.selected_fdi = []
        self._highlight_fdi([])
        self._set_output_text("", readonly=True)

if __name__ == "__main__":
    app = ZahnschemaApp()
    app.mainloop()
