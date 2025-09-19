
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tire Pallet Layout GUI – Pro v4.3
- Minták: Square, Hex, Quad‑4, Diag‑2, Dice‑5
- AUTO módok: 5→4→2 szabály, illetve max darabszám
- Tengely-tiltás (kapcsoló), középső engedélyezés, színezett ráhagyás, export (CSV/PNG/PDF)
- Fejráhagyás számítás
- ÚJ: Dice‑5 minta „szoros” pakkal a középső kör körül (c = cmin) → ha fér, a 4 sarokgumi **hozzáilleszkedik** a középsőhöz (tangens)
"""

import re, math, csv, tkinter as tk
from tkinter import ttk, messagebox, filedialog

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Circle
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# ---------- utils ----------
def parse_size(s: str):
    m = re.match(r"\s*(\d{3})/(\d{2})\s*[Z]?[Rr]\s*(\d{2})", s)
    if not m: raise ValueError("Helyes formátum: pl. 185/50R15")
    return float(m.group(1)), float(m.group(2)), float(m.group(3))

def tire_od_mm(size_str: str) -> float:
    w, ar, rim = parse_size(size_str)
    return 2*w*(ar/100.0) + rim*25.4

def layer_mm(size_str: str, comp_pct: float) -> float:
    w, _, _ = parse_size(size_str)
    return w*(1-comp_pct/100.0)

def centered_1d_positions(L: float, D: float):
    r = D/2.0; half=L/2.0
    kmax = int((half - r) // D)
    return [i*D for i in range(-kmax, kmax+1)] if kmax >= 0 else []

# ---------- rácsok ----------
def square_centered(L: float, D: float):
    xs = centered_1d_positions(L, D); ys = centered_1d_positions(L, D)
    return [(x,y) for x in xs for y in ys]

def hex_rows(L: float, D: float):
    r = D/2.0; v=D*math.sqrt(3)/2.0; half=L/2.0
    rows=[(0,0.0)]; j=1
    while j*v <= half - r + 1e-9:
        rows += [( j, j*v), (-j, -j*v)]
        j+=1
    rows.sort(key=lambda t: t[1])
    return rows, v

def hex_centered_parity(L: float, D: float, even_offset_zero: bool):
    rows,v = hex_rows(L, D)
    r=D/2.0; half=L/2.0; max_abs = half - r + 1e-9
    pts=[]
    for j,y in rows:
        j_even = (j % 2 == 0)
        offset = 0.0 if (j_even == even_offset_zero) else (D/2.0)
        xs=[0.0]; k=1
        while True:
            x=k*D
            if x <= max_abs + r: xs += [ x, -x ]; k+=1
            else: break
        for xb in xs:
            x = xb + offset
            if abs(x) <= max_abs: pts.append((x,y))
    return pts

# ---------- minták ----------
def pattern_quadrant4(L: float, D: float, axis_keep: float):
    r=D/2.0; half=L/2.0
    cmin = max(r, r + axis_keep)
    cmax = half - r
    if cmin > cmax: return []
    c = cmin  # szorosan a tengelyhez közelít (de nem ér hozzá, ha axis_keep>0)
    return [( c, c), (-c, c), ( c,-c), (-c,-c)]

def pattern_diagonal2(L: float, D: float, axis_keep: float):
    r=D/2.0; half=L/2.0
    cmin = max(r/math.sqrt(2.0), r + axis_keep)
    cmax = half - r
    if cmin > cmax: return []
    c = cmin  # szoros az átló mentén
    return [( c,-c), (-c, c)]

def pattern_dice5(L: float, D: float, allow_center: bool, axis_keep: float):
    if not allow_center: return []
    r=D/2.0; half=L/2.0
    # cmin feltétel: ne metssze a tengelyt (r+axis), és a középsővel legyen legalább érintő (sqrt(2)*c >= 2r → c >= sqrt(2) r)
    cmin = max(r + axis_keep, math.sqrt(2.0)*r)
    cmax = half - r
    if cmin > cmax: return [(0.0,0.0)]  # ha csak a középső fér el
    c = cmin  # <<< TIGHT PACK: érintő a középsővel, ha axis_keep=0
    return [(0.0,0.0), ( c, c), (-c, c), ( c,-c), (-c,-c)]

# ---------- szűrők ----------
def keepout_filter(pts, L, D, keepout):
    if keepout <= 0: return pts
    r=D/2.0
    return [(x,y) for (x,y) in pts if (x*x + y*y) >= (keepout + r)**2]

def axis_keepout_filter(pts, D, axis_keep, enabled: bool):
    if not enabled: return pts
    r=D/2.0; thr = r + max(0.0, axis_keep) - 1e-9
    return [(x,y) for (x,y) in pts if (abs(x) >= thr and abs(y) >= thr)]

def efficiency(L, D, n):
    return 100.0 * (n*math.pi*(D/2.0)**2) / (L*L)

def edge_clearances(pts, L, D):
    r=D/2.0; half=L/2.0
    if not pts: 
        return [], dict(left=None,right=None,bottom=None,top=None,global_min=None)
    per=[]; left=right=bottom=top=float('inf')
    for (x,y) in pts:
        cl = (x - (-half)) - r
        cr = (half - x) - r
        cb = (y - (-half)) - r
        ct = (half - y) - r
        cmin=min(cl,cr,cb,ct)
        per.append((x,y,cl,cr,cb,ct,cmin))
        left=min(left,cl); right=min(right,cr); bottom=min(bottom,cb); top=min(top,ct)
    gmin=min(left,right,bottom,top)
    return per, dict(left=left,right=right,bottom=bottom,top=top,global_min=gmin)

# ---------- GUI ----------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Tire Pallet Layout – Pro v4.3 (tight Dice‑5)")
        self.geometry("1360x860")

        frm = ttk.Frame(self, padding=10); frm.pack(fill="both", expand=True)
        ip = ttk.LabelFrame(frm, text="Beállítások", padding=10); ip.grid(row=0, column=0, sticky="nsw")

        # inputs
        self.var_size = tk.StringVar(value="285/45R21")
        self.var_side = tk.StringVar(value="1600")
        self.var_margin = tk.StringVar(value="0")
        self.var_keep = tk.StringVar(value="0")
        self.var_axis_on = tk.BooleanVar(value=False)
        self.var_axis_mm = tk.StringVar(value="0")
        self.var_allow_center = tk.BooleanVar(value=True)
        self.var_comp = tk.StringVar(value="0")
        self.var_maxh = tk.StringVar(value="1600")
        self.var_mode = tk.StringVar(value="auto_rules")  # auto_rules/auto_max/square/hex/quad4/diag2/dice5

        r=0
        def row(lbl, widget):
            nonlocal r
            ttk.Label(ip, text=lbl).grid(row=r, column=0, sticky="w"); widget.grid(row=r, column=1, sticky="w", padx=5, pady=2); r+=1

        row("Gumiméret:", ttk.Entry(ip, textvariable=self.var_size, width=16))
        row("Paletta oldal (mm):", ttk.Entry(ip, textvariable=self.var_side, width=12))
        row("Perem ráhagyás (mm):", ttk.Entry(ip, textvariable=self.var_margin, width=12))
        row("Középső tiltott kör (mm):", ttk.Entry(ip, textvariable=self.var_keep, width=12))

        axfrm = ttk.Frame(ip)
        ttk.Checkbutton(axfrm, text="Tengely tiltás", variable=self.var_axis_on).pack(side="left")
        ttk.Entry(axfrm, textvariable=self.var_axis_mm, width=6).pack(side="left", padx=(6,0))
        tk.Label(axfrm, text="mm").pack(side="left")
        row(" ", axfrm)

        row("Kompresszió (%):", ttk.Entry(ip, textvariable=self.var_comp, width=12))
        row("Max. magasság (mm):", ttk.Entry(ip, textvariable=self.var_maxh, width=12))
        row("Középső engedélyezett:", ttk.Checkbutton(ip, variable=self.var_allow_center))

        ttk.Label(ip, text="Mód:").grid(row=r, column=0, sticky="w")
        modes = ttk.Frame(ip); modes.grid(row=r, column=1, sticky="w"); r+=1
        for txt,val in [("AUTO (5→4→2)","auto_rules"),("AUTO (max)","auto_max"),
                        ("Square","square"),("Hex","hex"),("Quad‑4","quad4"),("Diag‑2","diag2"),("Dice‑5","dice5")]:
            ttk.Radiobutton(modes, text=txt, variable=self.var_mode, value=val).pack(side="left")

        ttk.Button(ip, text="Rajzol", command=self.draw).grid(row=r, column=0, pady=6, sticky="ew")
        ttk.Button(ip, text="PNG mentés", command=self.save_png).grid(row=r, column=1, pady=6, sticky="ew"); r+=1
        ttk.Button(ip, text="Export CSV", command=self.export_csv).grid(row=r, column=0, pady=6, sticky="ew")
        ttk.Button(ip, text="Export PDF", command=self.export_pdf).grid(row=r, column=1, pady=6, sticky="ew"); r+=1

        self.info = tk.Text(ip, width=48, height=20, wrap="word"); self.info.grid(row=r, column=0, columnspan=2, pady=6)

        fig = Figure(figsize=(9.2,8.0), dpi=100); self.ax = fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(fig, master=frm); self.canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=(10,0))
        frm.columnconfigure(1, weight=1); frm.rowconfigure(0, weight=1)
        self.draw()

    def _read(self):
        s=self.var_size.get().strip(); L=float(self.var_side.get()); mg=float(self.var_margin.get())
        ko=float(self.var_keep.get()); axis_on=self.var_axis_on.get(); ak=float(self.var_axis_mm.get())
        allow_center=self.var_allow_center.get(); cp=float(self.var_comp.get()); mh=float(self.var_maxh.get())
        mode=self.var_mode.get()
        return s,L,mg,ko,axis_on,ak,allow_center,cp,mh,mode

    def build_layouts(self, L, D, keep, axis_on, axis_mm, allow_center):
        sq = square_centered(L, D)
        hxA = hex_centered_parity(L, D, True)
        hxB = hex_centered_parity(L, D, False)
        hx  = hxA if len(hxA)>=len(hxB) else hxB
        q4  = pattern_quadrant4(L, D, axis_mm if axis_on else 0.0)
        d2  = pattern_diagonal2(L, D, axis_mm if axis_on else 0.0)
        d5  = pattern_dice5(L, D, allow_center, axis_mm if axis_on else 0.0)

        def filt(pts):
            pts = keepout_filter(pts, L, D, keep)
            pts = axis_keepout_filter(pts, D, axis_mm, axis_on)
            return pts

        return dict(square=filt(sq), hex=filt(hx), quad4=filt(q4), diag2=filt(d2), dice5=filt(d5))

    def choose_auto_rules(self, dct):
        if len(dct["dice5"]) >= 5: return "dice5"
        if len(dct["quad4"]) >= 4: return "quad4"
        if len(dct["diag2"]) >= 2: return "diag2"
        return "hex" if len(dct["hex"]) >= len(dct["square"]) else "square"

    def choose_auto_max(self, dct):
        order = ["hex","square","quad4","diag2","dice5"]
        return max(order, key=lambda k: (len(dct[k]), -order.index(k)))

    def draw(self):
        try:
            size,L,mg,ko,axis_on,ak,allow_center,cp,mh,mode = self._read()
            D=tire_od_mm(size); usable=max(0.0, L - 2*mg)
            if usable < D: raise ValueError("A hasznos paletta oldal kisebb, mint a gumi átmérője.")
            layouts = self.build_layouts(usable, D, ko, axis_on, ak, allow_center)
            choice = {"auto_rules": self.choose_auto_rules(layouts), "auto_max": self.choose_auto_max(layouts)}.get(mode, mode)
            pts = layouts.get(choice, [])
            per,sides = edge_clearances(pts, usable, D)

            layer_h = layer_mm(size, cp)
            layers  = int(mh // max(1e-9, layer_h))
            stack_h = layers * layer_h
            headroom = max(0.0, mh - stack_h)
            total   = layers*len(pts)

            # draw
            self.ax.clear(); half=usable/2.0; r=D/2.0
            self.ax.plot([-half,half,half,-half,-half],[-half,-half,half,half,-half],'k-')
            self.ax.axhline(0,lw=0.9,ls='--',color='k'); self.ax.axvline(0,lw=0.9,ls='--',color='k')
            if ko>0: self.ax.add_patch(Circle((0,0), ko, fill=False, color='red', lw=1.0))
            if axis_on and ak>0:
                self.ax.fill_betweenx([-half,half], -(r+ak), (r+ak), color='red', alpha=0.05)
                self.ax.fill_between([-half,half], -(r+ak), (r+ak), color='red', alpha=0.05)
            if per:
                mins=[p[6] for p in per]; mn,mx=min(mins),max(mins)
                norm=mcolors.Normalize(vmin=mn, vmax=mx if mx>mn else mn+1); cmap=cm.get_cmap('viridis')
                for (x,y,cl,cr,cb,ct,cmin) in per:
                    self.ax.add_patch(Circle((x,y), r, fill=False, lw=1.4, edgecolor=cmap(norm(cmin))))
                annot=f"Oldalsó min. ráhagyás (globális): {sides['global_min']:.1f} mm | Fejráhagyás: {headroom:.1f} mm"
            else:
                annot=f"Nincs kör. Fejráhagyás: {headroom:.1f} mm"
            title_map = {"auto_rules":"AUTO (5→4→2)","auto_max":"AUTO (max)","square":"SQUARE","hex":"HEX","quad4":"QUAD‑4","diag2":"DIAG‑2","dice5":"DICE‑5"}
            self.ax.set_title(f"{title_map.get(choice, choice)} | rétegenként: {len(pts)} | rétegek: {layers} | összes: {total}\n{annot}")
            self.ax.set_aspect('equal', adjustable='box'); self.ax.set_xlim(-half,half); self.ax.set_ylim(-half,half)
            self.ax.set_xlabel("X (mm) – középponttól"); self.ax.set_ylabel("Y (mm) – középponttól"); self.ax.grid(True, ls=':', lw=0.5)
            self.canvas.draw()

            # info
            effs = {k: efficiency(usable, D, len(v)) for k,v in layouts.items()}
            self.info.delete("1.0","end")
            self.info.insert("end", f"Méret: {size} | OD: {D:.1f} mm | Hasznos oldal: {usable:.1f} mm\n")
            self.info.insert("end", f"Axis-tiltás: {'ON' if axis_on else 'OFF'} ({ak:.1f} mm) | Keepout: {ko:.1f} mm | Középső eng.: {allow_center}\n\n")
            for k in ["square","hex","quad4","diag2","dice5"]:
                self.info.insert("end", f"{k:>7}: {len(layouts[k])} db/réteg, eff {effs[k]:.1f}%\n")
            self.info.insert("end", f"\nVálasztott: {title_map.get(choice, choice)} | Rétegvast.: {layer_h:.1f} mm | Rétegek: {layers} | Halom mag.: {stack_h:.1f} mm\n")
            self.info.insert("end", f"**Fejráhagyás**: {headroom:.1f} mm a {mh:.0f} mm-es maximumból | Összdarab: {total}\n")

            self._last=dict(pts=pts,D=D,usable=usable,choice=choice,per=per, layers=layers, total=total,
                            layer_h=layer_h, stack_h=stack_h, headroom=headroom, maxh=mh)

        except Exception as e:
            messagebox.showerror("Hiba", str(e))

    def save_png(self):
        fn = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG","*.png")])
        if not fn: return
        self.canvas.figure.savefig(fn, dpi=150); messagebox.showinfo("Mentve", fn)

    def export_pdf(self):
        fn = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")])
        if not fn: return
        self.canvas.figure.savefig(fn); messagebox.showinfo("Mentve", fn)

    def export_csv(self):
        last = getattr(self, "_last", None)
        if not last or not last["per"]:
            messagebox.showwarning("Figyelem", "Nincs exportálható adat."); return
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
        if not fn: return
        with open(fn,"w",newline="",encoding="utf-8") as f:
            w=csv.writer(f); w.writerow(["idx","x_mm","y_mm","clear_left","clear_right","clear_bottom","clear_top","clear_min"])
            for i,(x,y,cl,cr,cb,ct,cmin) in enumerate(last["per"], start=1):
                w.writerow([i,f"{x:.1f}",f"{y:.1f}",f"{cl:.1f}",f"{cr:.1f}",f"{cb:.1f}",f"{ct:.1f}",f"{cmin:.1f}"])

if __name__=="__main__":
    App().mainloop()
