# -*- coding: utf-8 -*-
"""
FPC Antenna Designer — Enhanced Desktop App
Features added in v2:
- Gerber (RS-274X) export (basic GTL & GKO)
- S11/Q approximate simulation and plot (matplotlib)
- PDF report generation (optional, using reportlab if installed)
- Improved automatic layer/turns heuristic considering trace width/thickness/ferrite
- Saves SVG/DXF/Gerber/HTML/PDF
Notes:
- This tool is for preliminary design and prototyping. Final tuning requires VNA and LCR measurements.
- For PDF export install reportlab: pip install reportlab
- Required (recommended): numpy, matplotlib
"""
import math, os, io, sys, datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk  # pillow is optional for preview thumbnails
try:
    import numpy as np
    import matplotlib.pyplot as plt
    HAS_NUMPY = True
except Exception:
    HAS_NUMPY = False

# Try optional PDF library
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas as pdfcanvas
    HAS_REPORTLAB = True
except Exception:
    HAS_REPORTLAB = False

MU0 = 4*math.pi*1e-7
K1, K2 = 2.34, 2.75

# --- utility electromagnetic functions ---
def calc_L_from_C_f(C_pF, f_MHz):
    C = C_pF*1e-12
    f = f_MHz*1e6
    if C<=0 or f<=0: return float('nan')
    return 1/((2*math.pi*f)**2 * C) * 1e6  # µH

def calc_C_from_L_f(L_uH, f_MHz):
    L = L_uH*1e-6
    f = f_MHz*1e6
    if L<=0 or f<=0: return float('nan')
    return 1/((2*math.pi*f)**2 * L) * 1e12  # pF

def skin_depth_cu(freq):
    rho = 1.68e-8; mu = 4*math.pi*1e-7
    return math.sqrt(2*rho/(2*math.pi*freq*mu))

def estimate_L_loop(n, d_avg_mm, rho, traceW_mm):
    # heuristic coil inductance proportional to n^2 * mean_diameter
    widthFactor = 1 - min(0.35, max(0.0,(traceW_mm - 0.2)/1.5))
    d_avg_m = d_avg_mm/1000.0
    L = MU0 * (n**2) * d_avg_m * K1 / (1 + K2 * rho)
    return L*1e6*widthFactor

# reuse geometry and estimation functions (similar to earlier version)
def estimate_L_rect(n, W, H, traceW, space):
    p = traceW + space
    d_out = (W + H)/2.0
    d_in = d_out - 2*n*p
    d_avg = (d_out + d_in)/2.0
    rho = (d_out - d_in)/max(d_out + d_in, 1e-9)
    L_uH = estimate_L_loop(n, d_avg, rho, traceW)
    return L_uH, d_in, d_avg, rho

def estimate_L_circle(n, D, traceW, space):
    p = traceW + space
    d_out = D
    d_in = d_out - 2*n*p
    d_avg = (d_out + d_in)/2.0
    rho = (d_out - d_in)/max(d_out + d_in, 1e-9)
    L_uH = estimate_L_loop(n, d_avg, rho, traceW)
    return L_uH, d_in, d_avg, rho

def coords_spiral_rect(W,H,margin,p,nTurns):
    left, top, right, bottom = margin, margin, W-margin, H-margin
    pts = [(left,top)]
    for _ in range(nTurns):
        pts += [(right,top),(right,bottom),(left,bottom)]
        left += p; top += p; right -= p; bottom -= p
        if left>=right or top>=bottom: break
        pts += [(left,top)]
    return pts

def coords_spiral_circle(D,margin,p,nTurns):
    R_out = (D/2.0)-margin
    Rin = max(0.0, R_out - nTurns*p)
    segsPerTurn = 96
    turns = max(1, nTurns)
    a = Rin; b = p/(2*math.pi)
    thetaMax = 2*math.pi*turns
    pts = []
    for i in range(turns*segsPerTurn+1):
        th = i*(thetaMax/(turns*segsPerTurn))
        r = a + b*th
        x = (D/2.0) + r*math.cos(th)
        y = (D/2.0) + r*math.sin(th)
        pts.append((x,y))
    return pts

def estimate_length_path(pts):
    L=0.0
    for i in range(1,len(pts)):
        dx = pts[i][0]-pts[i-1][0]; dy = pts[i][1]-pts[i-1][1]
        L += math.hypot(dx,dy)
    return L/1000.0  # meters

def estimate_R_ac(freq, length_m, width_mm, thickness_mm):
    rho=1.68e-8
    delta=skin_depth_cu(freq)
    t_eff = min(thickness_mm/1000.0, 2*delta)
    A = (width_mm/1000.0)*t_eff
    if A<=0: return 1e6
    return rho*length_m/A

def estimate_Q(freq, L_uH, R_ohm):
    w=2*math.pi*freq; L=L_uH*1e-6
    if R_ohm<=0: return 0.0
    return w*L/R_ohm

def s11_approx(f_array, f0, Q):
    # approximate S11 magnitude (dB) of an RLC resonator near resonance (simple model)
    # assume reflection coefficient magnitude ~ |(jQ*(f/f0 - f0/f)) / (1 + jQ*(f/f0 - f0/f))|
    out = []
    for f in f_array:
        x = Q*(f/f0 - f0/f)
        mag = abs(x / complex(1, x))
        # convert to dB reflection (approximated)
        reldB = 20*math.log10(mag+1e-9)
        out.append(reldB)
    return np.array(out) if HAS_NUMPY else [20*math.log10(abs(1e-9)) for _ in f_array]

# --- Gerber generator (rudimentary) ---
def gen_gerber_gtraces_from_pts(pts, trace_mm, filename_gtl):
    # Create a simplistic Gerber: using stroke as series of draw flashes with aperture circular (not truly RS274X precise)
    # We'll output basic Gerber primitives: G01 linear moves with D01 (draw) and D02 (move). This is approximate and may need post-processing.
    lines = []
    lines.append('%FSLAX24Y24*%')  # format
    lines.append('%MOMM*%')  # units mm
    lines.append('G90*')  # absolute
    lines.append('G21*')  # mm
    lines.append('G54D10*')  # select aperture 10 (not defined here; simple)
    # Convert points to gerber coordinates with 4 integer 4 decimal (not strict)
    def fmt(x): return f"{x:.4f}"
    if not pts: pts = []
    if pts:
        x0,y0 = pts[0]
        lines.append(f'X{fmt(x0)}Y{fmt(y0)}D02*')  # move
        for x,y in pts[1:]:
            lines.append(f'X{fmt(x)}Y{fmt(y)}D01*')  # draw
    lines.append('M02*')
    with open(filename_gtl, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

def gen_gko_outline(W,H,filename_gko):
    lines = ['%FSLAX24Y24*%','%MOMM*%','G90*','G21*']
    def fmt(x): return f"{x:.4f}"
    lines.append(f'X{fmt(0)}Y{fmt(0)}D02*')
    lines.append(f'X{fmt(W)}Y{fmt(0)}D01*')
    lines.append(f'X{fmt(W)}Y{fmt(H)}D01*')
    lines.append(f'X{fmt(0)}Y{fmt(H)}D01*')
    lines.append('M02*')
    with open(filename_gko,'w',encoding='utf-8') as f:
        f.write('\n'.join(lines))

# --- GUI application ---
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FPC Antenna Designer — v2")
        self.geometry("980x680")
        self.minsize(900,620)
        frm = ttk.Frame(self, padding=8); frm.pack(fill="both", expand=True)

        # left inputs
        left = ttk.Frame(frm); left.pack(side="left", fill="y", padx=(0,8))
        self.shape = tk.StringVar(value='rect')
        ttk.Label(left, text='شكل الهوائي').grid(row=0,column=0,sticky='w')
        ttk.Combobox(left, textvariable=self.shape, values=['rect','circle'], width=12).grid(row=0,column=1)
        self.freq = tk.DoubleVar(value=13.56); ttk.Label(left,text='التردد MHz').grid(row=1,column=0); ttk.Entry(left,textvariable=self.freq,width=12).grid(row=1,column=1)
        self.Cchip = tk.DoubleVar(value=25.0); ttk.Label(left,text='C_chip pF').grid(row=2,column=0); ttk.Entry(left,textvariable=self.Cchip,width=12).grid(row=2,column=1)
        self.W = tk.DoubleVar(value=13.0); ttk.Label(left,text='W mm').grid(row=3,column=0); ttk.Entry(left,textvariable=self.W,width=12).grid(row=3,column=1)
        self.H = tk.DoubleVar(value=7.0); ttk.Label(left,text='H mm').grid(row=4,column=0); ttk.Entry(left,textvariable=self.H,width=12).grid(row=4,column=1)
        self.D = tk.DoubleVar(value=12.0); ttk.Label(left,text='D mm').grid(row=5,column=0); ttk.Entry(left,textvariable=self.D,width=12).grid(row=5,column=1)
        self.margin = tk.DoubleVar(value=0.5); ttk.Label(left,text='Margin mm').grid(row=6,column=0); ttk.Entry(left,textvariable=self.margin,width=12).grid(row=6,column=1)
        self.trace = tk.DoubleVar(value=0.2); ttk.Label(left,text='Trace mm').grid(row=7,column=0); ttk.Entry(left,textvariable=self.trace,width=12).grid(row=7,column=1)
        self.space = tk.DoubleVar(value=0.2); ttk.Label(left,text='Spacing mm').grid(row=8,column=0); ttk.Entry(left,textvariable=self.space,width=12).grid(row=8,column=1)
        self.thickness = tk.DoubleVar(value=0.018); ttk.Label(left,text='Copper thickness mm').grid(row=9,column=0); ttk.Entry(left,textvariable=self.thickness,width=12).grid(row=9,column=1)
        self.ferrite = tk.DoubleVar(value=1.0); ttk.Label(left,text='Ferrite factor').grid(row=10,column=0); ttk.Entry(left,textvariable=self.ferrite,width=12).grid(row=10,column=1)
        self.use_pads = tk.BooleanVar(value=False); ttk.Checkbutton(left,text='Add pads',variable=self.use_pads).grid(row=11,column=0,columnspan=2,sticky='w')
        ttk.Label(left,text='Pad gap mm').grid(row=12,column=0); self.padgap = tk.DoubleVar(value=11.0); ttk.Entry(left,textvariable=self.padgap,width=12).grid(row=12,column=1)
        ttk.Button(left,text='احسب/حدّث',command=self.compute).grid(row=13,column=0,columnspan=2,pady=6)
        ttk.Button(left,text='حفظ SVG',command=self.save_svg).grid(row=14,column=0,padx=2,pady=2)
        ttk.Button(left,text='حفظ DXF',command=self.save_dxf).grid(row=14,column=1,padx=2,pady=2)
        ttk.Button(left,text='حفظ Gerber',command=self.save_gerber).grid(row=15,column=0,padx=2,pady=2)
        ttk.Button(left,text='حفظ تقرير (PDF/HTML)',command=self.save_report).grid(row=15,column=1,padx=2,pady=2)

        # right area: preview + charts
        right = ttk.Frame(frm); right.pack(side='right',fill='both',expand=True)
        self.summary = tk.StringVar(value='—'); ttk.Label(right,textvariable=self.summary).pack(anchor='w')
        self.canvas = tk.Canvas(right,bg='white',width=620,height=520); self.canvas.pack(fill='both',expand=True)
        # small image holder for S11 plot
        self.s11_img = None

        self.design = None; self.stats = None
        self.compute()

    def compute(self):
        shape = self.shape.get(); fMHz = float(self.freq.get()); freq = fMHz*1e6
        Cchip = float(self.Cchip.get()); W = float(self.W.get()); H = float(self.H.get()); D = float(self.D.get())
        margin = float(self.margin.get()); trace = float(self.trace.get()); space = float(self.space.get())
        thickness = float(self.thickness.get()); ferrite = float(self.ferrite.get())
        p = trace + space
        if shape=='rect':
            minDim = min(W,H)
            maxTurns = max(1, int((minDim-2*margin)/(2*p)))
        else:
            maxTurns = max(1, int(((D-2*margin)/2)/p))

        targetL = calc_L_from_C_f(Cchip,fMHz) if Cchip>0 else None
        best=None
        for n in range(1, maxTurns+1):
            L_uH, d_in, d_avg, rho = (estimate_L_rect(n,W,H,trace,space) if shape=='rect' else estimate_L_circle(n,D,trace,space))
            L_eff = L_uH * (ferrite**1.0) * (1.0)  # layer effect later
            # choose by closeness to targetL or maximize L if no C provided
            score = abs(L_eff - targetL) if targetL else -L_eff
            if best is None or score < best['score']:
                best = {'n':n,'L_uH':L_eff,'d_avg':d_avg,'rho':rho,'score':score}

        # auto layers: try to reach target L if possible by stacking up to 3 layers (simple heuristic)
        layers = 1
        if targetL and best['L_uH'] < targetL:
            for ly in (2,3):
                if best['L_uH'] * (ly**0.9) >= targetL:
                    layers = ly; break
            else:
                layers = 3

        n = best['n']; L_uH = best['L_uH'] * (layers**0.9)
        pts = (coords_spiral_rect(W,H,margin,p,n) if shape=='rect' else coords_spiral_circle(D,margin,p,n))
        length_m = estimate_length_path(pts); R = estimate_R_ac(freq,length_m,trace,thickness); Q = estimate_Q(freq,L_uH,R)
        area_m2 = (W/1000.0)*(H/1000.0) if shape=='rect' else math.pi*(D/2000.0)**2
        rng = estimate_range_cm(area_m2,Q,ferrite)
        pads = []
        if self.use_pads.get():
            gap = float(self.padgap.get()); pw=1.2; ph=1.6
            cx = (W/2.0) if shape=='rect' else (D/2.0); y = (H - ph/2.0 - 0.5) if shape=='rect' else (D - ph/2.0 - 0.5)
            x1 = cx - gap/2.0; x2 = cx + gap/2.0
            pads = [(x1,y,pw,ph),(x2,y,pw,ph)]

        self.design = {'shape':shape,'W':W,'H':H,'D':D,'margin':margin,'trace':trace,'space':space,
                       'thickness':thickness,'ferrite':ferrite,'n':n,'layers':layers,'L_uH':L_uH,'pts':pts,'pads':pads,
                       'vbW':W if shape=='rect' else D,'vbH':H if shape=='rect' else D}
        self.stats = {'freq':freq,'Cchip_pF':Cchip,'R_ohm':R,'Q':Q,'length_m':length_m,'range_cm':rng}

        self.summary.set(f"n={n}, layers={layers}, L≈{L_uH:.4f} µH, R≈{R:.2f} Ω, Q≈{Q:.1f}, range≈{rng:.1f} cm")
        self.draw_preview()
        self.plot_s11()

    def draw_preview(self):
        self.canvas.delete('all')
        if not self.design: return
        d = self.design; vbW,vbH = d['vbW'], d['vbH']; pts = d['pts']; trace = d['trace']
        Wc = int(self.canvas.winfo_width() or self.canvas['width']); Hc = int(self.canvas.winfo_height() or self.canvas['height'])
        sx = (Wc-40)/vbW if vbW>0 else 1; sy = (Hc-40)/vbH if vbH>0 else 1; s=min(sx,sy); ox=20; oy=20
        self.canvas.create_rectangle(ox,oy,ox+vbW*s,oy+vbH*s,outline='#333')
        last=None
        for x,y in pts:
            X=ox+x*s; Y=oy+y*s
            if last: self.canvas.create_line(last[0],last[1],X,Y,fill='#0a84ff',width=max(1,int(trace*s)))
            last=(X,Y)
        for px,py,pw,ph in d['pads']:
            x1 = ox+(px-pw/2.0)*s; y1=oy+(py-ph/2.0)*s; x2=ox+(px+pw/2.0)*s; y2=oy+(py+ph/2.0)*s
            self.canvas.create_rectangle(x1,y1,x2,y2,fill='#999',outline='#000')

    def plot_s11(self):
        if not HAS_NUMPY:
            return
        # build approximate S11 around resonance
        f0 = 13.56e6
        freqs = np.linspace(f0*0.6, f0*1.4, 400)
        Q = max(1.0, self.stats.get('Q',5))
        s11 = s11_approx(freqs, f0, Q)
        # plot and save to temporary PNG
        plt.figure(figsize=(4.5,2.2), dpi=120)
        plt.plot((freqs/1e6)-13.56, s11)  # x-axis in MHz offset
        plt.xlabel('ΔMHz from 13.56')
        plt.ylabel('Reflection (approx dB)')
        plt.title(f'Approx S11 — Q={Q:.1f}')
        plt.grid(True, linestyle=':', alpha=0.6)
        tmpfile = os.path.join(os.path.expanduser('~'), '.fpc_s11_preview.png')
        plt.tight_layout()
        plt.savefig(tmpfile)
        plt.close()
        try:
            img = Image.open(tmpfile)
            img.thumbnail((360,160))
            self.s11_img = ImageTk.PhotoImage(img)
            # display on canvas top-right corner
            self.canvas.create_image( self.canvas.winfo_width()-10-180, 10+80, image=self.s11_img, anchor='ne' )
        except Exception:
            pass

    def _svg_str(self):
        d = self.design; pts = d['pts']; trace = d['trace']; pads = d['pads']
        vbW, vbH = d['vbW'], d['vbH']
        s = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{vbW}mm' height='{vbH}mm' viewBox='0 0 {vbW} {vbH}'>",
             f"<rect x='0' y='0' width='{vbW}' height='{vbH}' fill='#fff' stroke='#000'/>"]
        if len(pts)>1:
            path = 'M ' + ' L '.join(f"{x} {y}" for x,y in pts)
            s.append(f"<path d='{path}' stroke='#0a84ff' stroke-width='{trace}' fill='none' stroke-linecap='round'/>")
        for px,py,pw,ph in pads:
            s.append(f"<rect x='{px-pw/2.0}' y='{py-ph/2.0}' width='{pw}' height='{ph}' fill='#999' stroke='#000'/>")
        s.append('</svg>')
        return '\n'.join(s)

    def _dxf_str(self):
        d = self.design; pts = d['pts']; trace = d['trace']; pads = d['pads']
        layer = 'ANTENNA'
        def sec(name): return f"0\nSECTION\n2\n{name}\n"
        header = sec('HEADER') + "9\n$INSUNITS\n70\n4\n0\nENDSEC\n"
        tables = "0\nSECTION\n2\nTABLES\n0\nTABLE\n2\nLAYER\n70\n1\n0\nLAYER\n2\n"+layer+"\n70\n0\n62\n7\n6\nCONTINUOUS\n0\nENDTAB\n0\nENDSEC\n"
        blocks = "0\nSECTION\n2\nBLOCKS\n0\nENDSEC\n"
        ent = sec('ENTITIES')
        ent += f"0\nLWPOLYLINE\n8\n{layer}\n90\n{len(pts)}\n70\n0\n43\n{trace}\n"
        for x,y in pts:
            ent += f"10\n{x}\n20\n{y}\n"
        # pads as simple LWPOLYLINE rectangles
        for px,py,pw,ph in pads:
            x1,y1 = px-pw/2.0, py-ph/2.0; x2,y2 = px+pw/2.0, py+ph/2.0
            ent += "0\nLWPOLYLINE\n8\nPADS\n90\n5\n70\n1\n"
            ent += f"10\n{x1}\n20\n{y1}\n10\n{x2}\n20\n{y1}\n10\n{x2}\n20\n{y2}\n10\n{x1}\n20\n{y2}\n10\n{x1}\n20\n{y1}\n"
        ent += "0\nENDSEC\n"
        eof = "0\nEOF\n"
        return "0\nSECTION\n2\nACAD\n0\nENDSEC\n"+header+tables+blocks+ent+eof

    def _gerber_files(self, folder):
        # creates GTL and GKO (outline) in folder
        pts = self.design['pts']; trace = self.design['trace']; vbW = self.design['vbW']; vbH = self.design['vbH']
        gtl = os.path.join(folder, 'GTL.gbr'); gko = os.path.join(folder, 'GKO.gbr')
        gen_gerber_gtraces_from_pts(pts, trace, gtl)
        gen_gko_outline(vbW, vbH, gko)
        return [gtl, gko]

    def _report_html(self):
        d = self.design; s = self.stats
        dims = f"W={d['W']}mm, H={d['H']}mm" if d['shape']=='rect' else f"D={d['D']}mm"
        html = f"""<!DOCTYPE html><html lang='ar' dir='rtl'><meta charset='utf-8'><title>تقرير تصميم هوائي FPC</title>
        <style>body{{font-family:Arial;padding:20px}} table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:6px}}</style>
        <h1>تقرير تصميم هوائي FPC</h1>
        <p>الشكل: {'مستطيل' if d['shape']=='rect' else 'دائري'} | الأبعاد: {dims}</p>
        <table>
        <tr><th>التردد</th><td>{s['freq']/1e6:.3f} MHz</td></tr>
        <tr><th>C_chip</th><td>{s['Cchip_pF']:.2f} pF</td></tr>
        <tr><th>عدد اللفات</th><td>{d['n']}</td></tr>
        <tr><th>الطبقات (مقترح)</th><td>{d['layers']}</td></tr>
        <tr><th>L (µH)</th><td>{d['L_uH']:.4f}</td></tr>
        <tr><th>R (Ω)</th><td>{s['R_ohm']:.3f}</td></tr>
        <tr><th>Q</th><td>{s['Q']:.2f}</td></tr>
        <tr><th>المدى التقديري</th><td>{s['range_cm']:.1f} سم</td></tr>
        <tr><th>Trace/Spacing</th><td>{d['trace']} / {d['space']} mm</td></tr>
        <tr><th>الهامش</th><td>{d['margin']} mm</td></tr>
        <tr><th>سمك النحاس</th><td>{d['thickness']} mm</td></tr>
        </table>
        <p>ملاحظة: هذه نتائج تقريبية. لاستخدام عملي دقّق بالقياسات باستخدام LCR meter وVNA.</p>
        </html>"""
        return html

    def save_svg(self):
        path = filedialog.asksaveasfilename(defaultextension='.svg', filetypes=[('SVG','*.svg')])
        if not path: return
        with open(path,'w',encoding='utf-8') as f: f.write(self._svg_str())
        messagebox.showinfo('تم','تم حفظ SVG.')

    def save_dxf(self):
        path = filedialog.asksaveasfilename(defaultextension='.dxf', filetypes=[('DXF','*.dxf')])
        if not path: return
        with open(path,'w',encoding='utf-8') as f: f.write(self._dxf_str())
        messagebox.showinfo('تم','تم حفظ DXF.')

    def save_gerber(self):
        folder = filedialog.askdirectory(title='اختر مجلد لحفظ ملفات Gerber (GTL,GKO)')
        if not folder: return
        files = self._gerber_files(folder)
        messagebox.showinfo('تم', f'تم حفظ Gerber:\n' + '\n'.join(files))

    def save_report(self):
        # prefer PDF if reportlab available
        html = self._report_html()
        if HAS_REPORTLAB:
            path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF','*.pdf')])
            if not path: return
            # generate simple PDF with reportlab and include S11 image if exists
            c = pdfcanvas.Canvas(path, pagesize=(595,842))  # A4 approx in points
            text = c.beginText(40, 800); text.setFont('Helvetica',10)
            lines = html.splitlines()
            for ln in lines[:40]:
                text.textLine(ln.strip())
            c.drawText(text)
            # try include S11 preview if created
            tmpimg = os.path.join(os.path.expanduser('~'), '.fpc_s11_preview.png')
            if os.path.exists(tmpimg):
                try:
                    c.drawImage(tmpimg, 40, 520, width=500, height=200)
                except Exception:
                    pass
            c.save()
            messagebox.showinfo('تم','تم حفظ تقرير PDF.')
        else:
            path = filedialog.asksaveasfilename(defaultextension='.html', filetypes=[('HTML','*.html')])
            if not path: return
            with open(path,'w',encoding='utf-8') as f: f.write(html)
            messagebox.showinfo('تم','تم حفظ تقرير HTML.')

if __name__ == "__main__":
    app = App(); app.mainloop()
