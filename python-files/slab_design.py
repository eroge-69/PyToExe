import tkinter as tk 
import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import is456_coeffs as is456
import math
from tabulate import tabulate
app = tk.Tk()
# app.geometry("400x520+950+5")
app.geometry("1180x475+175+0")
app.minsize(width=1180, height=475)
app.maxsize(width=1180, height=475)
# app.state("zoomed")
app.title("Two way slab design")

# Fonts
f1 = ctk.CTkFont(family="Century Gothic", size=16)
f2 = ctk.CTkFont(family="Century Gothic", size=16, weight="bold")
f3 = ctk.CTkFont(family="Times New Roman", size=20, weight="bold")

frame_01 = tk.Frame(app)
frame_01.pack(expand=True, fill="both")

given_data = tk.LabelFrame(frame_01, text="INPUTS", width=380, height=470)
given_data.place(x=10, y=0)

f_01 = tk.LabelFrame(given_data, text="SIZING", width=350, height=265)
f_01.place(x=10, y=0)

tk.Label(f_01, text="Short side\t\t\t  mm", font=f1).place(x=10, y=0)
tk.Label(f_01, text="Long side\t\t\t  mm", font=f1).place(x=10, y=30)
tk.Label(f_01, text="Trial depth\t\t\t  mm", font=f1).place(x=10, y=60)
tk.Label(f_01, text="Support width\t\t\t  mm", font=f1).place(x=10, y=90)
tk.Label(f_01, text="Panel type", font=f1).place(x=10, y=120)
tk.Label(f_01, text="Bar dia", font=f1).place(x=10, y=180)
tk.Label(f_01, text="Clear cover\t\t\t  mm", font=f1).place(x=10, y=210)

f_02 = tk.LabelFrame(given_data, text="LOADING", width=350, height=80)
f_02.place(x=10, y=270)

tk.Label(f_02, text="Live load\t\t\t\tkN/m²", font=f1).place(x=10, y=0)
tk.Label(f_02, text="Floor finish\t\t\tkN/m²", font=f1).place(x=10, y=30)

f_03 = tk.LabelFrame(given_data, text="MATERIAL GRADES", width=350, height=80)
f_03.place(x=10, y=355)

tk.Label(f_03, text="Grade of Concrete", font=f1).place(x=10, y=0)
tk.Label(f_03, text="Grade of Steel", font=f1).place(x=10, y=30)

# Inputs 

lx = ctk.CTkEntry(f_01, width=120, font=f2, justify="center", text_color="red")
lx.place(x=180, y=0)
lx.insert(0, "5000")

ly = ctk.CTkEntry(f_01, width=120, font=f2,  justify="center", text_color="red")
ly.place(x=180, y=30)
ly.insert(0, "7000")

trial_depth = ctk.CTkEntry(f_01, width=120, font=f2,  justify="center", text_color="red")
trial_depth.place(x=180, y=60)
trial_depth.insert(0, "150")

support_width = ctk.CTkEntry(f_01, width=120, font=f2,  justify="center", text_color="red")
support_width.place(x=180, y=90)
support_width.insert(0, "230")

panel_var = tk.StringVar(value=list(is456._PANEL_DATA.keys())[0])
panel_box = ctk.CTkComboBox(f_01, variable=panel_var, state="readonly",
                         values=list(is456._PANEL_DATA.keys()), width=330, font=f2, text_color='red')
panel_box.place(x=10, y=150)

bar_dia = ctk.CTkComboBox(f_01, width=115, font=f2,  justify="center", text_color="red", values=["8", "10", "12"])
bar_dia.place(x=180, y=180)

clear_cover = ctk.CTkEntry(f_01, width=115, font=f2,  justify="center", text_color="red")
clear_cover.place(x=180, y=210)
clear_cover.insert(0, "25")

live_load = ctk.CTkEntry(f_02, width=115, font=f2,  justify="center", text_color="red")
live_load.place(x=180, y=0)
live_load.insert(0, "3")
floor_finish = ctk.CTkEntry(f_02, width=115, font=f2,  justify="center", text_color="red")
floor_finish.place(x=180, y=30)
floor_finish.insert(0, "1.5")

fy_entry = ctk.CTkComboBox(f_03, values=["250", "415", "500"], width=115, font=f2, text_color="red", justify="center")
fy_entry.place(x=180, y=30)
fy_entry.set('415')

fck_entry = ctk.CTkComboBox(f_03, values=["20", "25", "30"], width=115, font=f2, text_color="red", justify="center")
fck_entry.place(x=180, y=0)
fck_entry.set('25')

# Logic
def round_up_to_10(x):
    return int(math.ceil(x / 10.0)) * 10

def round_down_to_10(x):
    return int(math.floor(x / 10.0)) * 10

def choose_standard_spacing(calculated_spacing):
    # available standard spacings (edit as you prefer)
    standard_spacings = [125, 135, 150, 180, 200]
    standard_spacings.sort(reverse=True)
    for s in standard_spacings:
        if s <= calculated_spacing:
            return s
    return standard_spacings[-1]

# calculate effective span
from oop import calculate_effective_span
def function_02():
    global beta, lx_eff, ly_eff, dx_efft, dy_efft
    a = calculate_effective_span(float(lx.get()), float(ly.get()), float(trial_depth.get()),
                                 float(clear_cover.get()), float(bar_dia.get()), float(support_width.get()))
    beta, lx_eff, ly_eff = a.beta, a.lx_eff, a.ly_eff
    dx_efft, dy_efft = a.dx_efft, a.dy_efft

    data = [
        ["Lx eff",        f"= {a.lx_eff:.0f} mm"],
        ["Ly eff",        f"= {a.ly_eff:.0f} mm"],
        ["β = Ly/Lx",     f"= {a.beta:.3f}"],
        ["d provided",   f"= {dx_efft:.0f} mm"]
    ]
    print(tabulate(data, tablefmt="rounded_grid"))


# BM coefficients 
def calculate():
    global beta  # <-- fetch from global memory
    try:
        panel = panel_var.get()
        ax_neg, ax_pos, ay_neg, ay_pos = is456.get_alpha_values(beta, panel)

        # Store for further use if needed
        global alpha_x_neg, alpha_x_pos, alpha_y_neg, alpha_y_pos
        alpha_x_neg = ax_neg
        alpha_x_pos = ax_pos
        alpha_y_neg = ay_neg
        alpha_y_pos = ay_pos

        data = [
            ["Panel type", f"{panel}"],
            ["β", f"{beta:.3f}"],
            ["α x⁻ (support)", f"{ax_neg:.4f}"],
            ["α x⁺ (mid‑span)", f"{ax_pos:.4f}"],
            ["α y⁻ (support)", f"{ay_neg:.4f}"],
            ["α y⁺ (mid‑span)", f"{ay_pos:.4f}"]
        ]
        # for row in data:
        #     print(f"{row[0]:<25} {row[1]:<100}")
        # print("-" * 40)
        print(tabulate(data, tablefmt="rounded_grid"))
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Load calculations
from oop import calculate_load
def function_03():
    global total_load, dead_load
    a = calculate_load(float(trial_depth.get()),float(floor_finish.get()),float(live_load.get()))
    dead_load = a.dead_load
    total_load = a.total_load
    data = [
        ["Wu", f"{a.total_load} KN"]
    ]
    # print(f"Wu = {a.total_load} KN")
    print(tabulate(data, tablefmt="rounded_grid"))

# Moment calculations
from oop import calculate_moment
def function_04():
    global Mu_x, Mu_y
    a = calculate_moment(lx_eff, total_load, alpha_x_pos, alpha_y_pos)
    Mu_x = a.Mu_x
    Mu_y = a.Mu_y 
    print(F"Mu_x = {a.Mu_x:.4f} kN.m")
    print(f"Mu_y = {a.Mu_y:.4f} kN.m")
    
# Depth check
from oop import calculate_depth_check
def function_01():
    global D_req, d_req, D_collapse, d_collapse
    a = calculate_depth_check(float(fy_entry.get()), float(fck_entry.get()),
                              float(bar_dia.get()), float(clear_cover.get()),
                              float(trial_depth.get()), Mu_x, lx_eff)
    print("/" * 5, "\033[91mFor Limit State of Collapse\033[0m", "/" * 5)
    data_01 = [
        ["D required", f"= {a.D_ultimate} mm"],
        ["d requried", f"= {a.d_ultimate} mm"],
    ]
    for row in data_01:
        print(f"{row[0]:<15} {row[1]:<10}")

    print("/" * 5, "For Limite State of Serviceability", "/" * 5)
    data_02 = [
        ["D required", f"= {a.D_serviceability} mm"],
        ["d required", f"= {a.d_serviceability} mm"]
    ]
    for row in data_02:
        print(f"{row[0]:<15} {row[1]:<10}")
        # for row in data:
        #     print(f"{row[0]:<25} {row[1]:<100}")
        # print("-" * 40)
    a.check()
    D_collapse = a.D_ultimate
    d_collapse = a.d_ultimate

    D_req = a.D_serviceability
    d_req = a.d_serviceability

# Area of steel calculations
from oop import calculate_area_of_steel
def function_05():
    global Ast_min, Astx, Asty
    a = calculate_area_of_steel(float(trial_depth.get()),dx_efft,dy_efft,float(fck_entry.get()),float(fy_entry.get()),Mu_x,Mu_y)

    Ast_min = a.Ast_min
    Astx = a.Astx 
    Asty = a.Asty

    a.result()

def calculate_spacing():
    global s_for_min_ast, s_x, s_y
    bar = float(bar_dia.get())
    a_st = (math.pi/4.0) * bar * bar    # area of ONE bar, sq.mm

    # required Ast per meter in each direction
    req_x = max(Ast_min, Astx)
    req_y = max(Ast_min, Asty)

    # trial spacing from area balance: a_st / s * 1000 = Ast_req  =>  s = a_st/Ast_req * 1000
    s_min_ast = (a_st / Ast_min) * 1000.0
    s_calc_x = (a_st / req_x) * 1000.0
    s_calc_y = (a_st / req_y) * 1000.0

    # round down to 10s, then snap to standard list
    def snap(s):
        from math import floor
        s10 = int(math.floor(s / 10.0)) * 10
        return choose_standard_spacing(s10)

    s_for_min_ast = snap(s_min_ast)
    s_x = snap(s_calc_x)
    s_y = snap(s_calc_y)

    # IS 456 max spacing limits for main bars: ≤ min(3d, 300 mm)
    d_eff = dx_efft  # = dy_efft
    s_max_main = min(3 * d_eff, 300.0)
    s_x = min(s_x, s_max_main)
    s_y = min(s_y, s_max_main)

    data = [
        ["Spacing for Ast.min", f"{s_for_min_ast:.0f} mm"],
        ["Sx (provide)",        f"{s_x:.0f} mm"],
        ["Sy (provide)",        f"{s_y:.0f} mm"]
    ]
    print(tabulate(data, tablefmt="rounded_grid"))

# output / results

output_frame = tk.LabelFrame(frame_01, text="OUTPUT", width=380, height=420)
output_frame.place(x=400, y=0)

general_result_frame = tk.LabelFrame(output_frame, text="GENERAL", width=350, height=120)
general_result_frame.place(x=10, y=0)

tk.Label(general_result_frame, text="Provide", font=f2, fg="#000000").place(x=10, y=0)
result_01 = tk.Label(general_result_frame,font=f1,  text="# __ - ___ mm c-c along x-direction")
result_01.place(x=10, y=30)
result_02 = tk.Label(general_result_frame,font=f1,  text="# __ - ___ mm c-c along y-direction")
result_02.place(x=10, y=60)

def general_result():
    a = int(bar_dia.get())
    tk.Label(general_result_frame, font=f2, text=f"{a} - {s_x}", fg="#002fff").place(x=25, y=30)
    tk.Label(general_result_frame, font=f2, text=f"{a} - {s_y}", fg="#002fff").place(x=25, y=60)
    # result_01.config(text=f"# {a} - {s_x} mm c-c along x-direction", font=f2)
    # result_02.config(text=f"# {a} - {s_y} mm c-c along y-direction", font=f2)

checks_frame = tk.LabelFrame(output_frame, text="CHECK", width=350, height=120)
checks_frame.place(x=10, y=130)

# check for deflection
tk.Label(checks_frame, font=f1, text="1] Check for deflection").place(x=10, y=0)
tk.Label(checks_frame, font=f1, text="2] Check for crack control").place(x=10, y=30)
tk.Label(checks_frame, font=f1, text="3] Check for development length").place(x=10, y=60)

def depth_check():
    a = calculate_depth_check(float(fy_entry.get()), float(fck_entry.get()),
                              float(bar_dia.get()), float(clear_cover.get()),
                              float(trial_depth.get()), Mu_x, lx_eff)
    if a.trial_depth >= a.D_serviceability:
        tk.Label(checks_frame, text="✅", fg="Green", font=f2).place(x=300, y=0)
    else:
        tk.Label(checks_frame, text="❌", fg="Red", font=f2).place(x=300, y=0)

# check for crack control
def crack_control():
    bar = float(bar_dia.get())
    overall_depth = float(trial_depth.get())

    if bar <= overall_depth / 8:
        tk.Label(checks_frame, text="✅", fg="Green", font=f2).place(x=300, y=30)
    else:
        tk.Label(checks_frame, text="❌", fg="Red", font=f2).place(x=300, y=30)
       
# check for development length
def check_development_length():
    global Ld_pro, Ld_req
    M_1 = Mu_x / 2
    V = 0.4 * total_load

    bar = float(bar_dia.get())
    overall_depth = float(trial_depth.get())  

    l_0 = max((12 * bar),overall_depth)
    Ld_pro = 1.3 * (M_1/V) + l_0
    tau_bd = float()
    fck = float(fck_entry.get())

    if fck == 20:
        tau_bd = 1.2
    elif fck == 25:
        tau_bd = 1.4
    elif fck == 30:
        tau_bd = 1.5
    Ld_req = (0.87 * fck * bar)/(4*tau_bd)

    if Ld_pro > Ld_req:
        tk.Label(checks_frame, text="✅", fg="Green", font=f2).place(x=300, y=60)
    else:
        tk.Label(checks_frame, text="❌", fg="Red", font=f2).place(x=300, y=60)

# Report / detailed calculations
report_frame = tk.LabelFrame(frame_01, text="REPORT", width=380, height=470)
report_frame.place(x=790, y=0)

f4 = ctk.CTkFont(family="Consolas", size=16)
def detailed_report():
    a = ctk.CTkTextbox(report_frame, width=355, height=430, fg_color="#000000", text_color="#FFFB00", font=f4, scrollbar_button_color="red", scrollbar_button_hover_color="#00fff2")
    
    a.insert("1.0", f"Effective short span = {lx_eff} mm\n")
    a.insert("2.0", f"Effective long span = {ly_eff} mm\n")
    a.insert("3.0", f"\nAspect ratio (β) = {beta:.3f}\n\talpha-x = {alpha_x_pos:.4f}\n\talpha-y = {alpha_y_pos:.4f}\n")
    a.insert("8.0", f"\nLoads :-\n\tD.L. of slab\t=\t{dead_load:.2f} kN/sqm\n\tFloor finish\t=\t{float(floor_finish.get()):.2f} kN/sqm\n\tL.L on slab\t =\t{float(live_load.get()):.2f} kN/sqm\n")
    a.insert("12.0", "\t---------------------------")
    a.insert("13.0", f"\nTotal ultimate load\t= {total_load:.3f} kN/sqm\n")
    a.insert("14.0", f"\nBending moment :-\n")
    a.insert("16.0", f"\tMdu(x)\t= {Mu_x:.2f} kNm\n\tMdu(y)\t= {Mu_y:.2f} kNm\n")
    a.insert("18.0", f"\nDepth :-\n    for LSM collapse,\n\tD = {D_collapse} mm\n\td = {d_collapse} mm")
    a.insert("23.0", f"\n    for LSM serviceability,\n\tD = {D_req} mm\n\td = {d_req} mm\n")
    a.insert("26.0", f"\nArea of steel :-\n\tAst(min) = {Ast_min:.2f} sq.mm\n\tAst(x) = {Astx:.2f} sq.mm\n\tAst(y) = {Asty:.2f} sq.mm\n")
    a.insert("31.0", f"\nSpacing of steel :-\n\tS(min) = {s_for_min_ast:.2f} sq.mm\n\tS(x) = {s_x:.2f} sq.mm\n\tS(y) = {s_y:.2f} sq.mm\n")
    a.insert("37.0", f"\nChecks :-\n  1] Check for deflection\n\tD(req.) = {D_req} mm\n\tD(pro.) = {float(trial_depth.get())} mm")

    if float(trial_depth.get()) >= D_req:
        a.insert("41.0", f"\n    [D(pro.) > D(req.)]Satisfied\n")
    else:
        a.insert("41.0", f"\n    [D(pro.) < D(req.)]Not satisfied\n")

    a.insert("45.0", f"\n  2] Check for crack control\n\tDia. of bar = {int(bar_dia.get())} mm\n\tD / 8 = {(float(trial_depth.get())/8):.2f} mm")

    if float(bar_dia.get()) < float(trial_depth.get()) / 8:
        a.insert("48.0", "\n    [Bar dia. < D / 8]Satisfied\n")
    else:
        a.insert("48.0", "\n    [Bar dia. > D / 8]Not satisfied\n")

    a.insert("49.0", f"\n  3] Check for development length\n\tLd(red.) = {Ld_req:.2f} mm\n\tLd(pro.) = {Ld_pro:.2f} mm")

    if Ld_pro >= Ld_req:
        a.insert("52.0", "\n    [Ld(pro.) > Ld(req.)]Satisfied")
    else:
        a.insert("52.0", "\n    [Ld(pro.) < Ld(req.)]Not satisfied")

    a.place(x=10, y=10)
    a.configure(state="disabled")

# Button
def cal_all():
    function_02()
    calculate()
    function_03()
    function_04()
    function_01()
    function_05()
    calculate_spacing()
    general_result()
    depth_check()
    crack_control()
    check_development_length()
    detailed_report()
    
# calculate button
button = tk.Button(frame_01, text='DESIGN', font=f2, fg="#8c00ff", overrelief="ridge",width=12, command=cal_all)
button.place(x=405, y=430)

button_01 = tk.Button(frame_01, text='REPORT', font=f2, fg="#03b0c7", overrelief="ridge",width=12, command=detailed_report)
button_01.place(x=530, y=430)

button_02 = tk.Button(frame_01, text='CLOSE', font=f2, fg="#ff5e00", overrelief="ridge",width=12, command=app.destroy)
button_02.place(x=655, y=430)

app.bind("<Return>", lambda event: cal_all())

app.mainloop()