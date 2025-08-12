
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

APP_TITLE = "CPK Analysis — Premium (±Tol)"
VERSION = "1.1"

def parse_values(text: str):
    if not text:
        return []
    for ch in [",", ";", "\n", "\t"]:
        text = text.replace(ch, " ")
    vals = []
    for t in text.split():
        try:
            vals.append(float(t))
        except ValueError:
            pass
    return vals

def compute_cp_cpk(values, lsl, usl):
    a = np.asarray(values, dtype=float)
    if a.size < 2:
        raise ValueError("Need at least 2 measurements.")
    if lsl is None or usl is None:
        raise ValueError("Limits are not defined.")
    if lsl >= usl:
        raise ValueError("USL must be greater than LSL.")
    mean = float(np.mean(a))
    std = float(np.std(a, ddof=1))
    if std <= 0:
        raise ValueError("Standard deviation is zero; cannot compute Cp/Cpk.")
    cp = (usl - lsl) / (6.0 * std)
    cpu = (usl - mean) / (3.0 * std)
    cpl = (mean - lsl) / (3.0 * std)
    cpk = min(cpu, cpl)
    oos = np.sum((a < lsl) | (a > usl))
    pct_oos = 100.0 * oos / a.size
    return {
        "n": int(a.size),
        "mean": mean,
        "std": std,
        "cp": cp,
        "cpk": cpk,
        "cpu": cpu,
        "cpl": cpl,
        "oos": int(oos),
        "pct_oos": pct_oos,
    }

def plot_chart(fig, values, lsl, usl, nominal, stats, dark=False):
    fig.clf()
    ax = fig.add_subplot(111)

    a = np.asarray(values, dtype=float)
    bins = max(5, min(30, a.size // 3))
    ax.hist(a, bins=bins, alpha=0.75, edgecolor="#222222" if not dark else "#DDDDDD")

    ax.grid(True, linestyle=":", linewidth=0.7, alpha=0.6)
    ax.set_xlabel("Measured Values")
    ax.set_ylabel("Frequency")
    ax.set_title("CPK Analysis", pad=10, fontsize=12, weight="bold")

    ymin, ymax = ax.get_ylim()
    def vline(x, ls, label):
        ax.vlines(x, ymin, ymax, linestyles=ls, linewidth=2, label=label)

    vline(lsl, "dashed", f"LSL ({lsl:g})")
    vline(usl, "dashed", f"USL ({usl:g})")
    vline(nominal, "dashdot", f"Nominal ({nominal:g})")
    vline(stats["mean"], "solid", f"Mean ({stats['mean']:.4g})")

    x = np.linspace(min(a.min(), lsl) - 3*stats["std"], max(a.max(), usl) + 3*stats["std"], 400)
    pdf = (1.0/(stats["std"]*np.sqrt(2*np.pi))) * np.exp(-0.5*((x-stats["mean"])/stats["std"])**2)
    scale = 0.9 * ymax / np.max(pdf) if np.max(pdf) > 0 else 1.0
    ax.plot(x, pdf*scale, linewidth=2, label="Normal fit")

    xx = np.linspace(x.min(), x.max(), 600)
    yy = (1.0/(stats["std"]*np.sqrt(2*np.pi))) * np.exp(-0.5*((xx-stats["mean"])/stats["std"])**2) * scale
    ax.fill_between(xx, 0, yy, where=(xx < lsl), alpha=0.25, color="#E57373", label="Below LSL")
    ax.fill_between(xx, 0, yy, where=(xx > usl), alpha=0.25, color="#64B5F6", label="Above USL")

    ax.legend(loc="upper left", fontsize=9, ncol=2)

    box_text = (
        f"n: {stats['n']}\n"
        f"Mean: {stats['mean']:.5g}\n"
        f"Std Dev: {stats['std']:.5g}\n"
        f"Cp: {stats['cp']:.5g}\n"
        f"Cpk: {stats['cpk']:.5g}\n"
        f"OOS: {stats['oos']}  ({stats['pct_oos']:.3g}%)"
    )
    ax.text(
        0.995, 0.98, box_text,
        ha="right", va="top",
        transform=ax.transAxes,
        fontsize=10,
        bbox=dict(
            boxstyle="round,pad=0.4",
            facecolor=("#ffffff" if not dark else "#1e1e1e"),
            edgecolor=("#888888" if not dark else "#BBBBBB"),
            alpha=0.85,
        ),
    )

    if dark:
        ax.set_facecolor("#111111")
        fig.patch.set_facecolor("#0b0b0b")
        ax.tick_params(colors="#DDDDDD")
        for spine in ax.spines.values():
            spine.set_color("#AAAAAA")
        leg = ax.get_legend()
        if leg:
            for txt in leg.get_texts():
                txt.set_color("#DDDDDD")

    fig.tight_layout()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE}")
        self.geometry("1120x760")
        try:
            self.tk.call("tk", "scaling", 1.25)
        except Exception:
            pass

        # state
        self.dark = False

        # Tk variables for live updates
        self.var_nom = tk.StringVar(value="0")
        self.var_ptol = tk.StringVar(value="0")
        self.var_ntol = tk.StringVar(value="0")
        self.var_lsl = tk.StringVar(value="")
        self.var_usl = tk.StringVar(value="")

        self._build_style()
        self._build_ui()
        self._bind_live_updates()
        self._recalc_limits()  # initialize computed LSL/USL

    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass
        pad = 6
        style.configure("TLabel", padding=pad)
        style.configure("TButton", padding=pad)
        style.configure("TEntry", padding=pad)
        style.configure("TLabelframe", padding=pad)
        style.configure("TLabelframe.Label", font=("Segoe UI", 12, "bold"))
        style.configure("Treeview", rowheight=24)

    def _build_ui(self):
        # Top bar
        top = ttk.Frame(self); top.pack(side=tk.TOP, fill=tk.X, padx=12, pady=8)
        ttk.Label(top, text=APP_TITLE, font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT)
        ttk.Label(top, text=f"v{VERSION}", foreground="#666").pack(side=tk.LEFT, padx=(8,0))
        self.dark_var = tk.BooleanVar(value=self.dark)
        ttk.Checkbutton(top, text="Dark Mode", variable=self.dark_var, command=self.toggle_theme).pack(side=tk.RIGHT)

        # Body split
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)

        # Left... inputs
        left = ttk.Labelframe(paned, text="Inputs")
        paned.add(left, weight=1)

        frm = ttk.Frame(left); frm.pack(fill=tk.X, padx=8, pady=8)
        # nominal, +tol, -tol
        ttk.Label(frm, text="Nominal").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        ttk.Label(frm, text="+Tol").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        ttk.Label(frm, text="-Tol").grid(row=2, column=0, sticky="w", padx=4, pady=4)

        self.e_nom = ttk.Entry(frm, width=18, textvariable=self.var_nom); self.e_nom.grid(row=0, column=1, sticky="we", padx=4, pady=4)
        self.e_ptol = ttk.Entry(frm, width=18, textvariable=self.var_ptol); self.e_ptol.grid(row=1, column=1, sticky="we", padx=4, pady=4)
        self.e_ntol = ttk.Entry(frm, width=18, textvariable=self.var_ntol); self.e_ntol.grid(row=2, column=1, sticky="we", padx=4, pady=4)

        # read-only computed LSL/USL
        ttk.Label(frm, text="LSL (calc)").grid(row=0, column=2, sticky="w", padx=10, pady=4)
        ttk.Label(frm, text="USL (calc)").grid(row=1, column=2, sticky="w", padx=10, pady=4)
        self.e_lsl = ttk.Entry(frm, width=16, textvariable=self.var_lsl, state="readonly"); self.e_lsl.grid(row=0, column=3, sticky="we", padx=4, pady=4)
        self.e_usl = ttk.Entry(frm, width=16, textvariable=self.var_usl, state="readonly"); self.e_usl.grid(row=1, column=3, sticky="we", padx=4, pady=4)

        frm.columnconfigure(1, weight=1)
        frm.columnconfigure(3, weight=1)

        # values
        ttk.Label(left, text="Measurements (paste... commas/spaces/newlines ok)").pack(anchor="w", padx=10, pady=(8,2))
        self.t_values = tk.Text(left, height=12, wrap="word", relief="solid", borderwidth=1)
        self.t_values.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0,8))

        # action buttons
        btns = ttk.Frame(left); btns.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(btns, text="Compute + Render", command=self.compute_render).pack(side=tk.LEFT)
        ttk.Button(btns, text="Export PNG", command=self.export_png).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Export PDF", command=self.export_pdf).pack(side=tk.LEFT, padx=6)

        # Right... chart
        right = ttk.Labelframe(paned, text="Chart")
        paned.add(right, weight=2)

        self.fig = plt.Figure(figsize=(6.8, 4.8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        tb = ttk.Frame(right); tb.pack(fill=tk.X, padx=8, pady=(0,8))
        self.nav = NavigationToolbar2Tk(self.canvas, tb); self.nav.update()

        # Results area
        res = ttk.Labelframe(self, text="Results")
        res.pack(fill=tk.X, padx=12, pady=(0,12))
        self.result_var = tk.StringVar(value="—")
        ttk.Label(res, textvariable=self.result_var, font=("Consolas", 11)).pack(anchor="w", padx=10, pady=6)

    def _bind_live_updates(self):
        # Update LSL/USL whenever nominal or tolerances change
        for var in (self.var_nom, self.var_ptol, self.var_ntol):
            var.trace_add("write", lambda *args: self._recalc_limits())

    def _recalc_limits(self):
        def _to_float(s):
            try:
                return float(s)
            except Exception:
                return None
        nom = _to_float(self.var_nom.get())
        ptol = _to_float(self.var_ptol.get())
        ntol = _to_float(self.var_ntol.get())

        if nom is None or (ptol is None and ntol is None):
            self._set_readonly(self.e_lsl, self.var_lsl, "")
            self._set_readonly(self.e_usl, self.var_usl, "")
            return

        usl = None if ptol is None else nom + ptol
        lsl = None if ntol is None else nom - ntol

        self._set_readonly(self.e_lsl, self.var_lsl, "" if lsl is None else f"{lsl:.6g}")
        self._set_readonly(self.e_usl, self.var_usl, "" if usl is None else f"{usl:.6g}")

    def _set_readonly(self, entry, var, text):
        # helper to update textvariable on a readonly entry
        state = entry.cget("state")
        entry.config(state="normal")
        var.set(text)
        entry.config(state="readonly")

    def toggle_theme(self):
        self.dark = bool(getattr(self, "dark_var", tk.BooleanVar(value=False)).get())
        try:
            self.compute_render(update_only=True)
        except Exception:
            pass

    def compute_render(self, update_only=False):
        try:
            vals = parse_values(self.t_values.get("1.0", tk.END))
            nom = float(self.var_nom.get())
            ptol = float(self.var_ptol.get())
            ntol = float(self.var_ntol.get())
            lsl = nom - ntol
            usl = nom + ptol
            stats = compute_cp_cpk(vals, lsl, usl)
        except Exception as e:
            if not update_only:
                messagebox.showerror("Input Error", str(e))
            return

        self.result_var.set(
            f"n={stats['n']}  mean={stats['mean']:.6g}  std={stats['std']:.6g}  "
            f"Cp={stats['cp']:.5g}  Cpk={stats['cpk']:.5g}  OOS={stats['oos']} ({stats['pct_oos']:.3g}%)"
        )

        plot_chart(self.fig, vals, lsl, usl, nom, stats, dark=self.dark)
        self.canvas.draw()

    def export_png(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")])
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=200, bbox_inches="tight")
            messagebox.showinfo("Saved", f"PNG saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_pdf(self):
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not path:
            return
        try:
            self.fig.savefig(path, dpi=300, bbox_inches="tight")
            messagebox.showinfo("Saved", f"PDF saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()
