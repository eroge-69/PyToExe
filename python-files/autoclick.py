import os
import json
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import threading
import time
import random
import numpy as np
import pygetwindow as gw
import keyboard
import win32api
import win32con
# from noise import pnoise1
from pynput import keyboard as pynput_keyboard
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# === Création de la fenêtre ===
app = tb.Window(themename="darkly")
app.title("Sake & Theback Private Clicker")
app.geometry("800x450")
app.resizable(False, False)

# === Variables Tkinter ===
allow_in_menus         = tk.BooleanVar(value=False)
mode_var               = tk.StringVar(value="blatant")
blatant_cps            = tk.DoubleVar(value=12.0)
legit_min_cps          = tk.DoubleVar(value=8.0)
legit_max_cps          = tk.DoubleVar(value=14.0)
block_hit_enabled      = tk.BooleanVar(value=False)
block_hit_chance       = tk.DoubleVar(value=25.0)
profile_name_var       = tk.StringVar(value="default")
autoclicker_state_text = tk.StringVar(value="⛔ OFF")
"""" Add these with your existing variables"""""
spike_mode = tk.BooleanVar(value=False)
spike_duration = tk.DoubleVar(value=0.5) 
spike_multiplier = tk.DoubleVar(value=1.5)

# Type de toggle: Keyboard ou souris (Left, Right, Middle, X1, X2)
toggle_method_var      = tk.StringVar(value="X1")

# === Perlin noise parameters for "legit" mode ===
perlin_x       = 0.0
perlin_speed   = 0.05   # controls how fast the noise moves
perlin_octaves = 1      # number of Perlin octaves
perlin_seed    = 42     # seed for reproducibility

# === Sweep mode variables ===
sweep_values = []
sweep_index  = 0

# === États globaux ===
running    = False
click_down = False






# === Détection fenêtre jeu ===
ALLOWED_WINDOW_KEYWORDS  = ["Minecraft", "Lunar", "Badlion", "AZLauncher", "javaw"]
DISALLOWED_MENU_KEYWORDS = ["inventory", "chest", "anvil", "crafting", "furnace", "enchant"]
VK_MAP = {"Left":0x01, "Right":0x02, "Middle":0x04, "X1":0x05, "X2":0x06}

def window_is_game():
    """Retourne True si la fenêtre active est un client Minecraft autorisé."""
    try:
        win = gw.getActiveWindow()
        if not win:
            return False
        title = win.title.lower()
        if allow_in_menus.get():
            return any(k.lower() in title for k in ALLOWED_WINDOW_KEYWORDS)
        for m in DISALLOWED_MENU_KEYWORDS + ["inventaire", "coffre", "enclume"]:
            if m in title:
                return False
        return any(k.lower() in title for k in ALLOWED_WINDOW_KEYWORDS)
    except:
        return False






# === Simulation clic fiable ===
def simulate_left_down():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
def simulate_left_up():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
def simulate_right_click():
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
    time.sleep(0.02)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

# === Boucle d'autoclick ===
def autoclick_loop():
    global click_down, sweep_index, perlin_x, spike_start_time
    last_click_time = 0
    
    while True:
        if running and win32api.GetAsyncKeyState(0x01) < 0 and window_is_game():
            # Initialize spike timer on first click
            if not click_down:
                spike_start_time = time.time()
            
            # Get CPS using the helper function
            cps = calculate_cps(spike_start_time)
            
            # Execute click
            delay = 1 / max(cps, 1)
            now = time.time()
            if now - last_click_time >= delay:
                simulate_left_down()
                last_click_time = now
                click_down = True
                
                if block_hit_enabled.get() and random.random() <= block_hit_chance.get()/100:
                    simulate_right_click()
                    
        else:
            if click_down:
                simulate_left_up()
                click_down = False
            time.sleep(0.01)


        """"helper function"""


def calculate_cps(spike_start_time):
    global perlin_x, sweep_index  # Declare globals at the top of the function
    
    mode = mode_var.get()
    base_cps = 0
    
    if mode == "blatant":
        base_cps = blatant_cps.get()
    # elif mode == "legit":
        # Perlin noise calculation
       # n = pnoise1(perlin_x, octaves=3, persistence=0.5, lacunarity=2.0, base=perlin_seed)
       # mn = legit_min_cps.get()
        # mx = legit_max_cps.get()
       # mid = (mn + mx) / 2
       # amp = (mx - mn) / 2
       # base_cps = mid + n * amp
        # Update Perlin position
       # perlin_x += perlin_speed
    elif mode == "sweep":
        if sweep_values:
            base_cps = float(sweep_values[sweep_index])
            sweep_index = (sweep_index + 1) % len(sweep_values)
        else:
            base_cps = random.uniform(legit_min_cps.get(), legit_max_cps.get())
    else:  # Fallback mode
        mn = legit_min_cps.get()
        mx = legit_max_cps.get()
        base_cps = random.uniform(min(mn, mx), max(mn, mx))
    
    # Apply spike multiplier if active
    if (spike_mode.get() and 
        (time.time() - spike_start_time) < spike_duration.get()):
        return base_cps * spike_multiplier.get()
    
    return base_cps


threading.Thread(target=autoclick_loop, daemon=True).start()

# === Toggle & hotkey ===
active_key = None
def toggle_autoclick():
    global running, click_down, spike_start_time
    running = not running
    if running:
        spike_start_time = time.time()  # Reset spike timer on activation
    if not running and click_down:
        simulate_left_up()
        click_down = False
    toggle_button.configure(
        style="Clicker.On.TButton" if running else "Clicker.Off.TButton"
    )
    autoclicker_state_text.set("✅ ON" if running else "⛔ OFF")
    print(f"[Autoclicker] {'✅ Activé' if running else '⛔ Désactivé'}")

# === Récupération touche clavier ===
hotkey_entry_var = tk.StringVar(value="F6")
def on_key_detect(event):
    try: n = event.name
    except: n = str(event)
    hotkey_entry_var.set(n.upper()); keyboard.unhook_all()
def on_hotkey_entry_click(evt):
    hotkey_entry_var.set("..."); keyboard.hook(on_key_detect)
def valider_touche():
    global active_key
    name = hotkey_entry_var.get().lower()
    if not name or name == "...":
        print("[Hotkey] ❌ Aucune touche à valider."); return
    try: keyboard.remove_hotkey(active_key)
    except: pass
    def trigger(): app.after(0, toggle_autoclick)
    active_key = name; keyboard.add_hotkey(name, trigger)
    print(f"[Hotkey] ✅ Touche activée : {name.upper()}")

# F11 via pynput
def f11_listener():
    def on_press(key):
        if key == pynput_keyboard.Key.f11: toggle_autoclick()
    with pynput_keyboard.Listener(on_press=on_press, suppress=False) as l: l.join()
threading.Thread(target=f11_listener, daemon=True).start()
keyboard.add_hotkey("f6", toggle_autoclick)

# === Polling toggle souris ===
def poll_toggle_mouse():
    prev = False
    while True:
        method = toggle_method_var.get()
        code = VK_MAP.get(method)
        if code:
            pressed = (win32api.GetAsyncKeyState(code) & 0x8000) != 0
            if pressed and not prev: toggle_autoclick()
            prev = pressed
        else:
            prev = False
        time.sleep(0.01)
threading.Thread(target=poll_toggle_mouse, daemon=True).start()

# === On change mode: recalcul sweep ===
def on_mode_change(event=None):
    mode = mode_var.get()
    if mode == "blatant":
        blatant_frame.pack(pady=5)
        legit_min_frame.pack_forget()
        legit_max_frame.pack_forget()
    else:
        blatant_frame.pack_forget()
        legit_min_frame.pack(pady=5)
        legit_max_frame.pack(pady=5)
    if mode == "sweep":
        mn = legit_min_cps.get()
        mx = legit_max_cps.get()
        global sweep_index
        sweep_values[:] = np.linspace(mn, mx, num=100)
        sweep_index = 0

# === Profils ===
def ensure_profiles_dir(): os.makedirs("profiles", exist_ok=True)
def update_profile_list():
    ensure_profiles_dir()
    profile_dropdown['values'] = sorted(f[:-5] for f in os.listdir("profiles") if f.endswith(".json"))
def save_profile():
    ensure_profiles_dir()
    name = profile_name_var.get().strip()
    if not name:
        print("[Profil] ❌ Nom de profil vide."); return
    data = {
        # Existing settings...
        "mode": mode_var.get(),
        "blatant_cps": blatant_cps.get(),
        "legit_min_cps": legit_min_cps.get(),
        "legit_max_cps": legit_max_cps.get(),
        "block_hit": block_hit_enabled.get(),
        "block_hit_chance": block_hit_chance.get(),
        "allow_in_menus": allow_in_menus.get(),
        # New spike settings
        "spike_mode": spike_mode.get(),
        "spike_duration": spike_duration.get(),
        "spike_multiplier": spike_multiplier.get()
    }
    with open(f"profiles/{name}.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"[Profil] 💾 Sauvegardé : {name}")
    update_profile_list()






def load_profile():
    name = profile_name_var.get().strip()
    try:
        with open(f"profiles/{name}.json", "r") as f:
            data = json.load(f)
        # Existing settings...
        mode_var.set(data["mode"])
        blatant_cps.set(data["blatant_cps"])
        legit_min_cps.set(data["legit_min_cps"])
        legit_max_cps.set(data["legit_max_cps"])
        block_hit_enabled.set(data["block_hit"])
        block_hit_chance.set(data["block_hit_chance"])
        allow_in_menus.set(data["allow_in_menus"])
        # New spike settings
        spike_mode.set(data.get("spike_mode", False))
        spike_duration.set(data.get("spike_duration", 0.5))
        spike_multiplier.set(data.get("spike_multiplier", 1.5))
        # Update GUI
        spike_duration_slider.set(data.get("spike_duration", 0.5))
        spike_multiplier_slider.set(data.get("spike_multiplier", 1.5))
        on_mode_change()
        blatant_value_label.config(text=f"{blatant_cps.get():.1f} CPS")
        legit_min_value_label.config(text=f"{legit_min_cps.get():.1f} CPS")
        legit_max_value_label.config(text=f"{legit_max_cps.get():.1f} CPS")
        blockhit_value_label.config(text=f"{block_hit_chance.get():.0f}%")
        print(f"[Profil] ✅ Chargé : {name}")
    except FileNotFoundError:
        print(f"[Profil] ❌ Introuvable : {name}")

# === Layout GUI ===
style = tb.Style()
style.theme_use("darkly")
bg = style.lookup("TFrame", "background")
style.configure("Clicker.On.TButton",  background="#1f6aa5", borderwidth=1, relief="solid")
style.configure("Clicker.Off.TButton", background=bg,      borderwidth=1, relief="solid")

# Contrôles principaux
controls_frame = ttk.Frame(app)
controls_frame.pack(pady=15)

# choix toggle method
ttk.Label(controls_frame, text="Toggle via:").grid(row=0, column=0, padx=(0,5))
toggle_dropdown = ttk.Combobox(
    controls_frame,
    textvariable=toggle_method_var,
    values=["Keyboard","Left","Right","Middle","X1","X2"],
    state="readonly",
    width=8
)
toggle_dropdown.grid(row=0, column=1)

# bouton toggle
toggle_button = ttk.Button(
    controls_frame,
    textvariable=autoclicker_state_text,
    width=4,
    style="Clicker.Off.TButton",
    command=toggle_autoclick
)
toggle_button.grid(row=0, column=2, padx=10)

# entrée hotkey clavier
ttk.Label(controls_frame, text="Touche :").grid(row=0, column=3)
hotkey_entry = ttk.Entry(controls_frame, textvariable=hotkey_entry_var, width=12, state="readonly")
hotkey_entry.grid(row=0, column=4, padx=5)
hotkey_entry.bind("<Button-1>", on_hotkey_entry_click)
valider_btn = ttk.Button(controls_frame, text="Valider", command=valider_touche)
valider_btn.grid(row=0, column=5, padx=5)

# options menus
ttk.Checkbutton(app, text="Actif dans les menus", variable=allow_in_menus).pack(pady=5)

# Profils & modes
o_frame = ttk.Frame(app)
o_frame.pack(pady=8)
ttk.Label(o_frame, text="Profil :").grid(row=0, column=0, padx=(0,5))
profile_dropdown = ttk.Combobox(o_frame, textvariable=profile_name_var, values=[], width=15, state="readonly")
profile_dropdown.grid(row=0, column=1)
ttk.Button(o_frame, text="💾 Sauvegarder", command=save_profile).grid(row=0, column=2, padx=5)
ttk.Button(o_frame, text="📂 Charger", command=load_profile).grid(row=0, column=3, padx=5)

ttk.Label(app, text="Mode :").pack(pady=(10,2))
mode_dropdown = ttk.Combobox(app, textvariable=mode_var, values=["blatant","legit","sweep"], width=10, state="readonly")
mode_dropdown.pack(pady=2)
mode_dropdown.bind("<<ComboboxSelected>>", on_mode_change)



# Spike Mode Controls
spike_frame = ttk.Frame(app)
ttk.Checkbutton(spike_frame, text="Spike Mode", variable=spike_mode).pack(side=tk.LEFT)

# Duration Slider with Arrow Key Support
ttk.Label(spike_frame, text="Duration:").pack(side=tk.LEFT, padx=(10,0))
spike_duration_slider = ttk.Scale(
    spike_frame, 
    from_=0.1, 
    to=15.0, 
    variable=spike_duration, 
    orient="horizontal", 
    length=120
)
spike_duration_slider.pack(side=tk.LEFT, padx=5)
spike_duration_label = ttk.Label(spike_frame, text=f"{spike_duration.get():.1f}s")
spike_duration_label.pack(side=tk.LEFT)

# Multiplier Slider with Arrow Key Support
ttk.Label(spike_frame, text="Multiplier:").pack(side=tk.LEFT, padx=(10,0))
spike_multiplier_slider = ttk.Scale(
    spike_frame, 
    from_=1.0, 
    to=3.0, 
    variable=spike_multiplier, 
    orient="horizontal", 
    length=120
)
spike_multiplier_slider.pack(side=tk.LEFT, padx=5)
spike_multiplier_label = ttk.Label(spike_frame, text=f"{spike_multiplier.get():.1f}x")
spike_multiplier_label.pack(side=tk.LEFT)

# Add keyboard bindings for arrow key control
def on_arrow_key(event, slider, var, step):
    current = var.get()
    if event.keysym == 'Left':
        var.set(max(slider['from'], current - step))
    elif event.keysym == 'Right':
        var.set(min(slider['to'], current + step))

# Bind arrow keys to sliders
spike_duration_slider.bind('<Left>', lambda e: on_arrow_key(e, spike_duration_slider, spike_duration, 0.1))
spike_duration_slider.bind('<Right>', lambda e: on_arrow_key(e, spike_duration_slider, spike_duration, 0.1))
spike_multiplier_slider.bind('<Left>', lambda e: on_arrow_key(e, spike_multiplier_slider, spike_multiplier, 0.1))
spike_multiplier_slider.bind('<Right>', lambda e: on_arrow_key(e, spike_multiplier_slider, spike_multiplier, 0.1))

# Make sure sliders can receive keyboard focus
spike_duration_slider.bind('<1>', lambda e: spike_duration_slider.focus_set())
spike_multiplier_slider.bind('<1>', lambda e: spike_multiplier_slider.focus_set())

spike_frame.pack(pady=5)

# Update labels when values change
spike_duration.trace_add('write', lambda *_: spike_duration_label.config(text=f"{spike_duration.get():.1f}s"))
spike_multiplier.trace_add('write', lambda *_: spike_multiplier_label.config(text=f"{spike_multiplier.get():.1f}x"))







blatant_frame = ttk.Frame(app)
blatant_slider = ttk.Scale(blatant_frame, from_=1, to=30, variable=blatant_cps, orient="horizontal", length=350,
                           command=lambda v: blatant_value_label.config(text=f"{float(v):.1f} CPS"))
blatant_slider.pack(side=tk.LEFT)
blatant_value_label = ttk.Label(blatant_frame, text=f"{blatant_cps.get():.1f} CPS")
blatant_value_label.pack(side=tk.LEFT, padx=5)

legit_min_frame = ttk.Frame(app)
legit_min_slider = ttk.Scale(legit_min_frame, from_=5, to=25, variable=legit_min_cps, orient="horizontal", length=350,
                             command=lambda v: legit_min_value_label.config(text=f"{float(v):.1f} CPS"))
legit_min_slider.pack(side=tk.LEFT)
legit_min_value_label = ttk.Label(legit_min_frame, text=f"{legit_min_cps.get():.1f} CPS")
legit_min_value_label.pack(side=tk.LEFT, padx=5)

legit_max_frame = ttk.Frame(app)
legit_max_slider = ttk.Scale(legit_max_frame, from_=5, to=25, variable=legit_max_cps, orient="horizontal", length=350,
                             command=lambda v: legit_max_value_label.config(text=f"{float(v):.1f} CPS"))
legit_max_slider.pack(side=tk.LEFT)
legit_max_value_label = ttk.Label(legit_max_frame, text=f"{legit_max_cps.get():.1f} CPS")
legit_max_value_label.pack(side=tk.LEFT, padx=5)

block_frame = ttk.Frame(app)
ttk.Checkbutton(block_frame, text="BlockHit", variable=block_hit_enabled).pack(side=tk.LEFT)
ttk.Label(block_frame, text="Chance (%)").pack(side=tk.LEFT, padx=(10,0))
block_hit_scale = ttk.Scale(block_frame, from_=0, to=100, variable=block_hit_chance, orient="horizontal", length=200,
                            command=lambda v: blockhit_value_label.config(text=f"{float(v):.0f}%"))
block_hit_scale.pack(side=tk.LEFT, padx=5)
blockhit_value_label = ttk.Label(block_frame, text=f"{block_hit_chance.get():.0f}%")
blockhit_value_label.pack(side=tk.LEFT)
block_frame.pack(pady=10)

# Update labels when sliders move
spike_duration_slider.configure(command=lambda v: [
    spike_duration.set(round(float(v), 1)),
    spike_duration_label.config(text=f"{float(v):.1f}s")
])
spike_multiplier_slider.configure(command=lambda v: [
    spike_multiplier.set(round(float(v), 1)),
    spike_multiplier_label.config(text=f"{float(v):.1f}x")
])





update_profile_list()
on_mode_change()
app.mainloop()