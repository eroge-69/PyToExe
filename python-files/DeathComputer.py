import tkinter as tk
import ctypes
import random
import time
import sys

# ------------------- Скрытие консоли -------------------
ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# ------------------- Основное окно -------------------
root = tk.Tk()
root.attributes('-fullscreen', True)
root.attributes('-topmost', True)
root.overrideredirect(True)
root.attributes('-transparentcolor', 'black')

canvas = tk.Canvas(root, width=root.winfo_screenwidth(),
                   height=root.winfo_screenheight(),
                   highlightthickness=0, bg='black')
canvas.pack()

# ------------------- Глобальные переменные -------------------
crosses = []
lines = []
colors = ["red", "green", "blue", "yellow", "cyan", "magenta", "white"]
phase_flags = {"started": False, "phase": 0}
start_time = None

# ------------------- Отмена скрипта -------------------
def cancel_script():
    cancel_win = tk.Toplevel()
    cancel_win.overrideredirect(True)
    cancel_win.attributes('-topmost', True)
    cancel_win.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
    cancel_canvas = tk.Canvas(cancel_win, width=root.winfo_screenwidth(),
                              height=root.winfo_screenheight(),
                              bg='black', highlightthickness=0)
    cancel_canvas.pack()
    cancel_canvas.create_text(root.winfo_screenwidth()//2, root.winfo_screenheight()//2,
                              text="KID GO CRY", fill="red", font=("Arial", 72))
    cancel_win.update()
    cancel_win.after(1000, lambda: sys.exit())
    cancel_win.mainloop()

# ------------------- Предупреждения -------------------
def show_warning(text, callback_yes, callback_no):
    fw = tk.Toplevel()
    fw.overrideredirect(True)
    fw.attributes('-topmost', True)
    fw.geometry(f"500x200+{root.winfo_screenwidth()//2 - 250}+{root.winfo_screenheight()//2 - 100}")
    fw.configure(bg='black')
    tk.Label(fw, text=text, fg="white", bg="black", font=("Arial", 18), wraplength=480).pack(pady=20)
    btn_frame = tk.Frame(fw, bg='black')
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="YES", command=lambda: [fw.destroy(), callback_yes()],
              bg="green", fg="white", font=("Arial", 16), width=12, height=2).pack(side="left", padx=20)
    tk.Button(btn_frame, text="NO", command=lambda: [fw.destroy(), callback_no()],
              bg="red", fg="white", font=("Arial", 16), width=12, height=2).pack(side="right", padx=20)

# ------------------- Анимации -------------------
def spawn_crosses(n=5):
    for _ in range(n):
        x = random.randint(0, root.winfo_screenwidth())
        y = random.randint(0, root.winfo_screenheight())
        color = random.choice(colors)
        crosses.append(canvas.create_text(x, y, text="X", fill=color, font=("Arial", 16)))

def spawn_lines(n=5):
    for _ in range(n):
        x1 = random.randint(0, root.winfo_screenwidth())
        y1 = random.randint(0, root.winfo_screenheight())
        x2 = random.randint(0, root.winfo_screenwidth())
        y2 = random.randint(0, root.winfo_screenheight())
        color = random.choice(colors)
        lines.append(canvas.create_line(x1, y1, x2, y2, fill=color, width=2))

def clear_canvas():
    for c in crosses + lines:
        canvas.delete(c)
    crosses.clear()
    lines.clear()

def jitter_elements():
    for c in crosses:
        canvas.move(c, random.randint(-5,5), random.randint(-5,5))
    for l in lines:
        canvas.move(l, random.randint(-3,3), random.randint(-3,3))

# ------------------- Фазы -------------------
def phase1():
    spawn_crosses(3)
    root.after(200, phase1)

def phase2():
    spawn_lines(3)
    root.after(300, phase2)

def phase3():
    spawn_crosses(5)
    root.after(50, phase3)

def phase4():
    spawn_lines(10)
    root.after(100, phase4)

def phase5():
    spawn_lines(1)
    jitter_elements()
    root.after(50, phase5)

def phase6():
    spawn_crosses(3)
    spawn_lines(3)
    jitter_elements()
    root.after(50, phase6)

def phase7():
    spawn_crosses(5)
    jitter_elements()
    root.after(70, phase7)

def phase8():
    spawn_lines(5)
    jitter_elements()
    root.after(70, phase8)

def phase9():
    spawn_crosses(5)
    spawn_lines(5)
    jitter_elements()
    root.after(100, phase9)

def phase10():
    # смешение всех эффектов
    spawn_crosses(7)
    spawn_lines(7)
    jitter_elements()
    root.after(50, phase10)

def phase11():
    # финальный хаос
    spawn_crosses(10)
    spawn_lines(10)
    jitter_elements()
    root.after(30, phase11)

# ------------------- Фазовый контроллер -------------------
def run_phases():
    global start_time
    if not phase_flags["started"]:
        return
    elapsed = time.time() - start_time

    if elapsed < 5:
        phase1()
    elif elapsed < 10:
        phase2()
    elif elapsed < 20:
        phase3()
    elif elapsed < 30:
        phase4()
    elif elapsed < 40:
        phase5()
    elif elapsed < 50:
        phase6()
    elif elapsed < 60:
        phase7()
    elif elapsed < 70:
        phase8()
    elif elapsed < 80:
        phase9()
    elif elapsed < 100:
        phase10()
    else:
        phase11()
    
    root.after(50, run_phases)

# ------------------- Запуск -------------------
def start_second_warning():
    show_warning(
        "Last warning: DONT LAUNCH IT",
        callback_yes=start_animation,
        callback_no=cancel_script
    )

def start_animation():
    global start_time
    phase_flags["started"] = True
    start_time = time.time()
    run_phases()

# Первое предупреждение
show_warning(
    "You sure you wanna launch that? It can launch CPU 0-15",
    callback_yes=start_second_warning,
    callback_no=cancel_script
)

root.mainloop()
