import os
from PIL import Image, ImageTk, ImageSequence
import tkinter as tk
from tkinter import ttk
import pyautogui
import pyperclip 
import keyboard
import threading
import time
import win32gui
import ttkbootstrap as ttk
from ttkbootstrap.style import Style
import tkinter.font as tkfont
pyautogui.FAILSAFE = False

# --- Categorized itemIDs ---
item_categories = {
    "Foods": {
        "Herbs": "18",
        "Ale": "28",
        "Fish": "30",
        "Honey": "141",
        "Meat": "147",
        "Berries": "171",
        "Bread": "172",
        "Eggs": "220",
        "Vegetables": "230",
        "Apples": "296",
        "Sausages": "320",
    },
    "Food materials & Crops": {
        "Grain": "1",
        "Flour": "5",
        "Malt": "29",
        "Salt": "145",
        "Barley": "165",
        "Wheat": "217",
        "Rye": "298",
        "Flax": "11",
    },
    "Animals": {
        "Chickens": "42",
        "Sheep": "72",
        "Horses": "98",
        "Goats": "222",
        "Lambs": "232",
        "Oxen": "234",
        "Mules": "306",
    },
    "Fuels": {
        "Charcoal": "13",
        "Firewood": "216",
    },
    "Clothes, textils": {
        "Hides": "3",
        "Leather": "4",
        "Cloaks": "8",
        "Shoes": "10",
        "Linen": "12",
        "Wool": "23",
        "Yarn": "148",
        "Clothes": "149",
    },
    "Materials, tools": {
        "Tools": "6",
        "Wooden Parts": "7",
        "Iron ore": "14",
        "Iron Slab": "35",
        "Wax": "142",
        "Clay": "146",
        "Iron Parts": "317",
        "Dyes": "302",
    },
    "Weapons, armors": {
        "Spears": "133",
        "Sidearms": "177",
        "Polearms": "178",
        "Warbows": "205",
        "Crossbows": "206",
        "Small Shields": "270",
        "Large Shields": "271",
        "Gambesons": "163",
        "Mail Armor": "164",
        "Helmets": "273",
        "Plate Armor": "293",
    },
    "Building materials": {
        "Stone": "15",
        "Timber": "16",
        "Planks": "17",
        "Rooftiles": "269",
    }
}


# --- Globals ---
last_command_time = 0
command_cooldown = 0.2
trainer_clipboard_content = ""
floating_button = None
delay = 0.2
clipboard_command = ""
image_cache = {}
button_refs = {}
selected_button_name = None
selected_button = {"btn": None}
pxx = 24 #icon buttons x-y in pixel
amount_options = [1, 5, 10, 20, 50, 200, 500, 1000, 1500, 2500]

DEFAULT_BUTTON_BG = None

def set_clipboard_from_trainer(text):
    global trainer_clipboard_content
    pyperclip.copy(text)
    trainer_clipboard_content = text 

def get_default_button_bg(master=None):
    global DEFAULT_BUTTON_BG
    if DEFAULT_BUTTON_BG is None:
        sample = tk.Button(master)
        DEFAULT_BUTTON_BG = sample.cget("background")
        sample.destroy()
    return DEFAULT_BUTTON_BG

def is_image_button(btn):
    return str(btn.cget("image")) != ""

def highlight_button(btn, is_image=False):
    config = {}
    if is_image:
        config["relief"] = tk.FLAT
        config["bg"] = "#ffffff"
    else:
        config["relief"] = tk.SUNKEN
        config["fg"] = "#bb3335"  # finomabb piros
        config["bg"] = "#ffffff"
    btn.config(**config)

def unhighlight_button(btn, is_image=False):
    config = {}
    if is_image:
        config["relief"] = tk.FLAT
        config["bg"] = get_default_button_bg(btn)
    else:
        config["relief"] = tk.RAISED
        config["fg"] = "white"
        config["bg"] = get_default_button_bg(btn)
    btn.config(**config)

def reset_selected_button():
    if selected_button["btn"]:
        btn = selected_button["btn"]
        is_image = is_image_button(btn)
        unhighlight_button(btn, is_image)
        selected_button["btn"] = None

def select_button(btn):
    reset_selected_button()
    highlight_button(btn, is_image=is_image_button(btn))
    selected_button["btn"] = btn

# --- Tooltip class ---
class ToolTipManager:
    _instance = None

    def __init__(self):
        self.tip_window = None
        self.label = None

    def show(self, widget, text):
        self.hide()
        if not text:
            return
        x = widget.winfo_rootx() + 20
        y = widget.winfo_rooty() + 20
        self.tip_window = tw = tk.Toplevel(widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tw.attributes("-topmost", True)

        self.label = ttk.Label(
            tw,
            text=text,
            style="Tooltip.TLabel"
        )
        self.label.pack(ipadx=2)

    def hide(self):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None
tooltip_manager = ToolTipManager()


# --- Focus check ---
def get_foreground_window_title():
    window = win32gui.GetForegroundWindow()
    return win32gui.GetWindowText(window)

def is_manor_lords_focused():
    return get_foreground_window_title().strip() == "Manor Lords"

# --- Hotkey command paste ---
def paste_build_command(cmd):
    global last_command_time
    if not is_manor_lords_focused():
        print("Ignored hotkey: Manor Lords not focused.")
        return

    now = time.time()
    if now - last_command_time < command_cooldown:
        print("Command ignored: cooldown active")
        return
    last_command_time = now

    def worker():
        lines = cmd.strip().splitlines()
        for line in lines:
            if not line.strip():
                continue  # üres sorokat átugrunk
            time.sleep(delay)
            if not is_manor_lords_focused():
                print("Focus changed, aborting command.")
                return
            pyautogui.keyDown('f10')
            time.sleep(delay)
            pyautogui.keyUp('f10')
            time.sleep(delay)
            set_clipboard_from_trainer(line.strip())
            time.sleep(delay)
            pyautogui.keyDown('ctrl')
            time.sleep(delay)
            pyautogui.press('v')
            time.sleep(delay)
            pyautogui.keyUp('ctrl')
            time.sleep(delay)
            pyautogui.press('enter')

    threading.Thread(target=worker).start()


# --- Utilities ---

def reset_if_empty(var, default_value):
    if var.get().strip() == "":
        var.set(default_value)

def safe_int(var):
    try:
        val = var.get() if hasattr(var, "get") else var
        return int(val)
    except (ValueError, TypeError, tk.TclError):
        return None
    
def toggle_window_visibility(root):
    global floating_button
    if root.state() == 'normal':
        root.withdraw()
        # "Show Trainer" ablak létrehozása
        floating_button = tk.Toplevel()
        floating_button.overrideredirect(True)
        floating_button.geometry("+10+10")
        floating_button.attributes("-topmost", True)

        # látványos, nagyobb gomb ttk-vel
        show_btn = ttk.Button(
            floating_button,
            text="⏪ Show Trainer",
            command=lambda: restore_main_window(root),
            bootstyle="primary"  # vagy: "success", "info", stb.
        )
        show_btn.configure(style="Big.TButton")
        show_btn.pack(ipadx=10, ipady=5, padx=10, pady=10)


def restore_main_window(root):
    global floating_button
    if floating_button:
        floating_button.destroy()
        floating_button = None
    root.deiconify()
    root.lift()


def register_hotkeys(root=None):
    keyboard.add_hotkey('b', lambda: paste_build_command('k.buildInstantly'))
    keyboard.add_hotkey('u', lambda: paste_build_command('k.spawnConstructionResourcesToRegionBuildings'))
    keyboard.add_hotkey('k', lambda: paste_build_command('k.demolishSelectedBuildings'))
    keyboard.add_hotkey('num enter', lambda: paste_build_command(pyperclip.paste()))
    if root:
        keyboard.add_hotkey('n', lambda: toggle_window_visibility(root))  # csak elrejt, nem váltogat

        
def attach_tooltip(widget, text): 
    widget.bindtags((widget, *widget.bindtags())) # biztosítjuk, hogy a widget saját eseményt kapjon, ne csak a ttk belső réteg

    widget.bind("<Enter>", lambda e: tooltip_manager.show(widget, text))
    widget.bind("<Leave>", lambda e: tooltip_manager.hide())


# --- Command wrappers ---
def run_game_command(command: str):
    if not is_manor_lords_focused():
        print("Ignored command: Manor Lords not focused.")
        return

    def worker():
        time.sleep(delay)
        if not is_manor_lords_focused():
            print("Focus changed, aborting command.")
            return
        pyautogui.keyDown('f10')
        time.sleep(delay)
        pyautogui.keyUp('f10')
        time.sleep(delay)
        set_clipboard_from_trainer(command)
        pyautogui.keyDown('ctrl')
        time.sleep(delay)
        pyautogui.press('v')
        time.sleep(delay)
        pyautogui.keyUp('ctrl')
        time.sleep(delay)
        pyautogui.press('enter')

    threading.Thread(target=worker).start()

def run_paste_command_sequence():
    if not is_manor_lords_focused():
        print("Ignored paste: Manor Lords not focused.")
        return

    threading.Thread(target=paste_command_sequence).start()

def paste_command_sequence():
    time.sleep(delay)
    pyautogui.keyDown('f10')
    time.sleep(delay)
    pyautogui.keyUp('f10')
    time.sleep(delay)
    pyautogui.keyDown('ctrl')
    time.sleep(delay)
    pyautogui.press('v')
    time.sleep(delay)
    pyautogui.keyUp('ctrl')
    time.sleep(delay)
    pyautogui.press('enter')
    print("Command pasted from clipboard:", pyperclip.paste())

# --- UI helpers ---
def copy_command(item_id, amount, name=None):
    cmd = f"k.addResourceToSelectedBuildings {item_id} {amount}"
    set_clipboard_from_trainer(cmd)

def update_selected_item_clipboard(amount_getter):
    if selected_button["btn"]:
        for name, btn in button_refs.items():
            if btn == selected_button["btn"]:
                item_id = None
                for items in item_categories.values():
                    if name in items:
                        item_id = items[name]
                        break
                if item_id:
                    try:
                        amount = int(amount_getter())
                        copy_command(item_id, amount, name)
                    except ValueError:
                        pass  # Ignore if not a number

def set_selected_by_text(frame, text):
    def recursive_find_button(widget):
        for child in widget.winfo_children():
            if isinstance(child, tk.Button) and child.cget("text") == text:
                return child
            result = recursive_find_button(child)
            if result:
                return result
        return None

    reset_selected_button()  # <<< fontos sor

    btn = recursive_find_button(frame)
    if btn:
        is_image = is_image_button(btn)
        selected_button["btn"] = btn
        highlight_button(btn, is_image=is_image)

def add_buttons_grid(frame, buttons, columns=3, width=11):
    """
    buttons: list of (text, command[, tooltip])
    """
    for idx, btn_data in enumerate(buttons):
        if len(btn_data) == 3:
            text, command, tooltip_text = btn_data
        else:
            text, command = btn_data
            tooltip_text = None

        btn = tk.Button(frame, text=text, width=width, command=lambda c=command, t=text: [c(), set_selected_by_text(frame, t)])
        row = idx // columns
        col = idx % columns
        btn.grid(row=row, column=col, padx=2, pady=2, sticky="ew")

        if tooltip_text:
            attach_tooltip(btn, tooltip_text)


def create_combo_row(parent, label_text, variable, values, command_fn, button_text, width=6, readonly=True):
    row = tk.Frame(parent)
    row.pack(anchor='w', pady=1)

    tk.Label(row, text=f"{label_text}:").pack(side='left', padx=(0, 2))

    combo_state = "readonly" if readonly else "normal"
    combo = ttk.Combobox(row, textvariable=variable, values=values, state=combo_state, width=width)
    combo.pack(side='left', padx=(0, 5))

    btn = tk.Button(row, text=button_text, width=10)
    btn.pack(side='left')

    def on_click():
        command_fn()
        set_selected_by_text(row, button_text)

    btn.config(command=on_click)
    combo.bind("<<ComboboxSelected>>", lambda e: on_click())

    return combo, btn

def activate_and_run(frame, label, func):
    for child in frame.winfo_children():
        if isinstance(child, tk.Button) and child.cget("text") == label:
            if selected_button["btn"]:
                selected_button["btn"].config(relief=tk.RAISED)
            selected_button["btn"] = child
            child.config(relief=tk.SUNKEN)
            break
    func()

def load_image(name, master=None):
    if name in image_cache:
        return image_cache[name]
    try:
        path = os.path.join("images", f"{name}.png")
        image = Image.open(path).resize((pxx, pxx), resample=Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image, master=master)  # <<< FONTOS
        image_cache[name] = photo
        return photo
    except Exception as e:
        print(f"Failed to load image {name}: {e}")
        return tk.PhotoImage(width=pxx, height=pxx, master=master)  # <<< ez is


# --- UI Segment Functions ---
def create_add_resource_panel(parent):
    frame = tk.Frame(parent)
    frame.pack(anchor='nw')

    info_label = tk.Label(
        frame,
        text="Select quantity and resource, select\nbuilding in-game, hit Numpad Enter.",
        justify='left'
    )
    info_label.pack(anchor='w', padx=2, pady=(0, 10))

    # Quantity input (Entry)
    quantity_frame = tk.Frame(frame)
    quantity_frame.pack(anchor='w', pady=2)
    tk.Label(quantity_frame, text="Quantity (1–2500):").pack(side=tk.LEFT)

    default_amount = "1"
    max_amount = 2500
    amount_var = tk.StringVar(value=default_amount)

    def validate_amount(value):
        if value == "":
            return True
        if value.isdigit():
            num = int(value)
            return 1 <= num <= max_amount
        return False

    vcmd = frame.register(validate_amount)

    entry = tk.Entry(quantity_frame, textvariable=amount_var, width=6,
                     validate="key", validatecommand=(vcmd, "%P"))
    entry.pack(side=tk.LEFT, padx=2)

    def update_resource_clipboard(*args):
        if selected_button["btn"]:
            for name, btn in button_refs.items():
                if btn == selected_button["btn"]:
                    for items in item_categories.values():
                        if name in items:
                            item_id = items[name]
                            break
                    else:
                        return
                    try:
                        amt = int(amount_var.get())
                        if 1 <= amt <= max_amount:
                            cmd = f'k.addResourceToSelectedBuildings {item_id} {amt}'
                            set_clipboard_from_trainer(cmd)

                    except ValueError:
                        pass

    # Reset only when focus is lost
    entry.bind("<FocusOut>", lambda e: reset_if_empty(amount_var, default_amount))
    amount_var.trace_add("write", update_resource_clipboard)

    # --- Button categories ---
    joint_frame = None
    bg_initialized = False  # csak egyszer állítsuk be a default háttérszínt

    for category, items in item_categories.items():
        if category == "Fuels":
            if joint_frame is None:
                joint_frame = tk.Frame(parent)
                joint_frame.pack(padx=2, pady=2, fill='x')
            cat_frame = tk.LabelFrame(joint_frame, text=category)
            cat_frame.pack(side='right', expand=True, fill='x')
        elif category == "Building materials":
            if joint_frame is None:
                joint_frame = tk.Frame(parent)
                joint_frame.pack(padx=2, pady=2, fill='x')
            cat_frame = tk.LabelFrame(joint_frame, text=category)
            cat_frame.pack(side='left', expand=True, fill='x')
        else:
            cat_frame = tk.LabelFrame(parent, text=category)
            cat_frame.pack(padx=2, pady=2, fill='x')

        if category == "Animals":
            attach_tooltip(cat_frame, "(resources in building storage!)\nDon't mix this with spawn animals")

        row = 0
        col = 0
        for item_name, item_id in items.items():
            img = load_image(item_name, master=cat_frame)
            btn = tk.Button(cat_frame, image=img, width=pxx, height=pxx, relief=tk.RAISED, bd=1)

            # csak az első gombnál kérdezzük le a témából a default bg-t
            if not bg_initialized:
                get_default_button_bg(btn)
                bg_initialized = True

            def make_callback(iid=item_id, name=item_name, btn_ref=None):
                def callback():
                    amt = safe_int(amount_var)
                    if amt is None or not (1 <= amt <= max_amount):
                        return
                    cmd = f'k.addResourceToSelectedBuildings {iid} {amt}'
                    set_clipboard_from_trainer(cmd)
                    reset_selected_button()
                    highlight_button(btn_ref, is_image=is_image_button(btn_ref))
                    selected_button["btn"] = btn_ref
                return callback

            btn.config(command=make_callback(item_id, item_name, btn))
            btn.image = img
            btn.grid(row=row, column=col, padx=1, pady=1)

            button_refs[item_name] = btn
            attach_tooltip(btn, item_name)

            col += 1
            if col >= 8:
                col = 0
                row += 1



#
def create_hotkeys_panel(parent):
    for key, desc in [
        ("b", "Instant build: select building, move it with mouse, hit b key."),
        ("u", "Fill all resources to under-construction buildings."),
        ("k", "Demolish selected building.")
    ]:
        f = tk.LabelFrame(parent, text=f"{key} key")
        f.pack(anchor='w', fill='x', padx=2, pady=2)
        tk.Label(f, text=desc, justify='left').pack(anchor='w', padx=2, pady=2)
#
def create_deposit_panel(parent):
    frame = tk.LabelFrame(parent, text="Deposits")
    frame.pack(anchor='w', fill='x', padx=2, pady=2)

    deposit_types = ["Iron", "Clay", "Salt"]
    deposit_type_var = tk.StringVar(value="Iron")

    # Új: validált beviteli mező deposit amount-ra
    max_deposit_amount = 9999
    default_deposit_amount = "500"
    deposit_amount_var = tk.StringVar(value=default_deposit_amount)


    def validate_deposit_amount(value):
        if value == "":
            return True
        if value.isdigit():
            num = int(value)
            return 1 <= num <= max_deposit_amount
        return False

    vcmd = frame.register(validate_deposit_amount)

    combo_frame = ttk.Frame(frame)
    combo_frame.grid(row=0, column=0, columnspan=4, sticky='w', pady=5)

    ttk.Label(combo_frame, text="Type:").grid(row=0, column=0, padx=(2, 2), sticky='w')
    ttk.Combobox(combo_frame, textvariable=deposit_type_var, values=deposit_types, state="readonly", width=10).grid(row=0, column=1, padx=2)

    ttk.Label(combo_frame, text="Amount:").grid(row=0, column=2, padx=(2, 2), sticky='w')
    entry = tk.Entry(combo_frame, textvariable=deposit_amount_var, width=8,
                     validate="key", validatecommand=(vcmd, "%P"))
    entry.grid(row=0, column=3, padx=2)
    entry.bind("<FocusOut>", lambda e: reset_if_empty(deposit_amount_var, default_deposit_amount))

    button_frame = ttk.Frame(frame)
    button_frame.grid(row=1, column=0, columnspan=4, sticky='w', pady=(2, 2))

    def spawn():
        amount = safe_int(deposit_amount_var)
        if amount is not None:
            cmd = f'k.spawnDepositAtCursor {deposit_type_var.get().lower()} {amount}'
            set_clipboard_from_trainer(cmd)
            set_selected_by_text(button_frame, "Spawn")

    def remove():
        cmd = f'k.removeDepositAtCursor {deposit_type_var.get().lower()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(button_frame, "Remove")

    def rich():
        cmd = f'k.markRichDepositAtCursor {deposit_type_var.get().lower()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(button_frame, "Make Rich")

    def addto():
        amount = safe_int(deposit_amount_var)
        if amount is not None:
            cmd = f'k.addDepositAtCursor {deposit_type_var.get().lower()} {amount}'
            set_clipboard_from_trainer(cmd)
            set_selected_by_text(button_frame, "Add to")


    # Gombok
    spawn_btn = tk.Button(button_frame, text="Spawn", width=10, command=spawn)
    spawn_btn.grid(row=0, column=0, padx=2, pady=2)
    attach_tooltip(spawn_btn, "Spawn selected kind of deposit under cursor position")

    remove_btn = tk.Button(button_frame, text="Remove", width=10, command=remove)
    remove_btn.grid(row=0, column=1, padx=2, pady=2)
    attach_tooltip(remove_btn, "Remove selected kind of deposit under cursor position")

    rich_btn = tk.Button(button_frame, text="Make Rich", width=10, command=rich)
    rich_btn.grid(row=0, column=2, padx=2, pady=2)
    attach_tooltip(rich_btn, "Mark deposit infinite usage")

    addto_btn = tk.Button(button_frame, text="Add to", width=10, command=addto)
    addto_btn.grid(row=0, column=3, padx=2, pady=2)
    attach_tooltip(addto_btn, "Add amount to selected deposit")

    def update_type_clipboard(*args):
        if selected_button["btn"]:
            label = selected_button["btn"].cget("text")
            if label == "Spawn":
                spawn()
            elif label == "Remove":
                remove()
            elif label == "Make Rich":
                rich()
            elif label == "Add to":
                addto()

    def update_amount_clipboard(*args):
        if selected_button["btn"]:
            label = selected_button["btn"].cget("text")
            if label == "Spawn":
                spawn()
            elif label == "Add to":
                addto()

    deposit_type_var.trace_add("write", update_type_clipboard)
    deposit_amount_var.trace_add("write", update_amount_clipboard)

def create_wild_animals_panel(parent):
    frame = tk.LabelFrame(parent, text="Wild Animals")
    frame.pack(anchor='w', fill='x', padx=2, pady=2)

    spawn_quantity_var = tk.StringVar(value="40")
    add_amount_var = tk.StringVar(value="20")

    combo_frame = tk.Frame(frame)
    combo_frame.grid(row=0, column=0, columnspan=3, sticky='w', pady=(0, 5))

    tk.Label(combo_frame, text="Spawn:").grid(row=0, column=0, padx=(2, 2), sticky='w')
    spawn_combo = ttk.Combobox(combo_frame, textvariable=spawn_quantity_var, values=["40", "80", "120"], width=4, state="readonly")
    spawn_combo.grid(row=0, column=1, padx=(0, 10))

    tk.Label(combo_frame, text="Add Deer:").grid(row=0, column=2, padx=(2, 2), sticky='w')
    add_combo = ttk.Combobox(combo_frame, textvariable=add_amount_var, values=["20", "40", "60"], width=4, state="readonly")
    add_combo.grid(row=0, column=3)

    def spawn_animals():
        amt = spawn_quantity_var.get()
        cmd = f'k.spawnWildAnimalsAtCursor {amt}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(buttons_frame, "Spawn")

    def remove_animals():
        cmd = 'k.removeWildAnimalsAtCursor'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(buttons_frame, "Remove")

    def add_deer():
        amt = add_amount_var.get()
        cmd = f'k.spawnDeerToWildAnimalsAtCursor {amt}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(buttons_frame, "Add to")


    buttons_frame = tk.Frame(frame)
    buttons_frame.grid(row=1, column=0, columnspan=3, sticky='w')

    spawn_btn = tk.Button(buttons_frame, text="Spawn", width=11, command=spawn_animals)
    spawn_btn.grid(row=0, column=0, padx=2, pady=2)
    attach_tooltip(spawn_btn, "Spawn wild animals under cursor")

    remove_btn = tk.Button(buttons_frame, text="Remove", width=11, command=remove_animals)
    remove_btn.grid(row=0, column=1, padx=2, pady=2)
    attach_tooltip(remove_btn, "Remove wild animals under cursor")

    add_btn = tk.Button(buttons_frame, text="Add to", width=11, command=add_deer)
    add_btn.grid(row=0, column=2, padx=2, pady=2)
    attach_tooltip(add_btn, "Add more deer to existing group under cursor")

    # Combobox váltás → megfelelő gomb aktiválása és vágólap frissítés
    def on_spawn_combo_change(*args):
        spawn_animals()

    def on_add_combo_change(*args):
        add_deer()

    spawn_quantity_var.trace_add("write", on_spawn_combo_change)
    add_amount_var.trace_add("write", on_add_combo_change)
#
def create_berries_stones_panel(parent):
    frame = tk.LabelFrame(parent, text="Berries / Stones")
    frame.pack(anchor='w', fill='x', padx=2, pady=2)

    resource_options = ["Berries", "Stone"]
    resource_var = tk.StringVar(value="Berries")

    top_row = tk.Frame(frame)
    top_row.pack(anchor='w', pady=2)
    tk.Label(top_row, text="Type:").pack(side='left', padx=(2, 2))
    ttk.Combobox(top_row, textvariable=resource_var, values=resource_options, state="readonly", width=8).pack(side='left', padx=2)

    def spawn():
        cmd = f'k.spawnResourceAtCursor {resource_var.get().lower()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(button_frame, "Spawn")

    def remove():
        cmd = f'k.removeResourceAtCursor {resource_var.get().lower()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(button_frame, "Remove 1")

    def remove_clump():
        cmd = f'k.removeResourceClumpAtCursor {resource_var.get().lower()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(button_frame, "RemoveClump")

    def mark_rich():
        cmd = f'k.markRichResourceClumpAtCursor {resource_var.get().lower()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(button_frame, "Mark Rich")

    def refill():
        cmd = 'k.refillRegionResource berries'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(button_frame, "Refill Berries")
        
    button_frame = tk.Frame(frame)
    button_frame.pack(anchor='w')

    spawn_btn = tk.Button(button_frame, text="Spawn", width=12, command=spawn)
    spawn_btn.grid(row=0, column=0, padx=2, pady=2)
    attach_tooltip(spawn_btn, "Spawn single resource into a clump\nor make a new clump at cursor position")

    remove_btn = tk.Button(button_frame, text="Remove 1", width=12, command=remove)
    remove_btn.grid(row=0, column=1, padx=2, pady=2)
    attach_tooltip(remove_btn, "Remove one resource")

    remove_clump_btn = tk.Button(button_frame, text="RemoveClump", width=12, command=remove_clump)
    remove_clump_btn.grid(row=0, column=2, padx=2, pady=2)
    attach_tooltip(remove_clump_btn, "Remove resource clump")

    rich_btn = tk.Button(button_frame, text="Mark Rich", width=12, command=mark_rich)
    rich_btn.grid(row=1, column=0, padx=2, pady=2)
    attach_tooltip(rich_btn, "Mark clump as rich (doubles quantity)")

    refill_btn = tk.Button(button_frame, text="Refill Berries", width=12, command=refill)
    refill_btn.grid(row=1, column=1, padx=2, pady=2)
    attach_tooltip(refill_btn, "Refill only berries in the region")

    def update_clipboard(*args):
        if selected_button["btn"]:
            text = selected_button["btn"].cget("text")
            if text == "Spawn":
                spawn()
            elif text == "Remove 1":
                remove()
            elif text == "RemoveClump":
                remove_clump()
            elif text == "Mark Rich":
                mark_rich()
            # Refill Berries nem frissül resource alapján, mert csak berries esetén működik

    resource_var.trace_add("write", update_clipboard)

#
def create_fishing_panel(parent): 
    frame = tk.LabelFrame(parent, text="Fishing Pond")
    frame.pack(anchor='w', fill='x', padx=2, pady=2)

    def make_cmd_setter(cmd):
        def inner():
            set_clipboard_from_trainer(cmd)
        return inner

    add_buttons_grid(frame, [
        ("Place", make_cmd_setter("k.placeFishingPond"), "Place the pond, need big flat place, works with b key (build Instantly)"),
        ("Spawn Fish", make_cmd_setter("k.spawnShoalOfFishToFishingPondAtCursor"), "Spawn fish into the pond"),
        ("Remove", make_cmd_setter("k.removeFishingPondAtCursor"), "Remove the pond"),
        ("Make Rich", make_cmd_setter("k.makeRichFishingPondAtCursor"), "Mark the fish as rich resource (doubles quantity)"),
        ("Refill Fish", make_cmd_setter("k.refillRegionResource fish"), "Refill only fish in the region")
    ])


def create_visibility_toggle_panel(parent, root):
    frame = tk.Frame(parent)
    frame.pack(anchor='w', fill='x', padx=5, pady=5)

    btn = ttk.Button(
        frame,
        text="Hide trainer window (n)",
        width=25,
        command=lambda: toggle_window_visibility(root),
        bootstyle="info-outline"  # vagy: "secondary", "success", "danger", "primary-outline" stb.
    )
    btn.pack(anchor='w')
    attach_tooltip(btn, "Press n key to hide this trainer window\na clickable (Show Trainer) button will stay top left")
    
def create_spawn_animals_panel(parent):
    frame = tk.LabelFrame(parent, text="Spawn animals")
    frame.pack(anchor='w', fill='x', padx=2, pady=2)

    tk.Label(frame, text="Amount (1–99):").pack(anchor='w', padx=2)
    animal_amount_var = tk.StringVar(value="1")

    def validate_animal_amount(value):
        if value == "":
            return True
        if value.isdigit():
            num = int(value)
            return 1 <= num <= 99
        return False

    vcmd = frame.register(validate_animal_amount)

    entry = tk.Entry(frame, textvariable=animal_amount_var, width=5,
                 validate="key", validatecommand=(vcmd, "%P"))
    entry.pack(anchor='w', padx=2, pady=(0, 5))
    entry.bind("<FocusOut>", lambda e: reset_if_empty(animal_amount_var, "1"))

    animal_ids = {
        "sheep": "sheep",
        "lambs": "lamb",
        "oxen": "oxen",
        "horses": "horse",
        "mules": "mule"
    }

    animal_buttons_frame = tk.Frame(frame)
    animal_buttons_frame.pack(anchor='w', padx=2, pady=2)

    row = col = 0
    max_cols = 5

    def spawn_animal_cmd(animal_id, amount):
        cmd = f'k.spawnAnimalAtCursor {animal_id} {amount}'
        set_clipboard_from_trainer(cmd)


    def update_animal_clipboard(*args):
        if selected_button["btn"]:
            for name, btn in button_refs.items():
                if btn == selected_button["btn"]:
                    amt = safe_int(animal_amount_var)
                    if amt is not None and 1 <= amt <= 99:
                        spawn_animal_cmd(animal_ids[name], amt)

    animal_amount_var.trace_add("write", update_animal_clipboard)

    for animal_name, animal_id in animal_ids.items():
        img = load_image(animal_name, master=animal_buttons_frame)
        
        btn = tk.Button(animal_buttons_frame,
                        image=img,
                        width=pxx,
                        height=pxx,
                        relief=tk.RAISED,
                        bd=1)
        
        def make_callback(aid=animal_id, name=animal_name, btn_ref=btn):
            def callback():
                amt = safe_int(animal_amount_var)
                if amt is None or not (1 <= amt <= 99):
                    return
                cmd = f'k.spawnAnimalAtCursor {aid} {amt}'
                set_clipboard_from_trainer(cmd)
                reset_selected_button()
                highlight_button(btn_ref, is_image=is_image_button(btn_ref))
                selected_button["btn"] = btn_ref
            return callback


        btn.config(command=make_callback())
        btn.image = img
        btn.grid(row=row, column=col, padx=1, pady=1)

        button_refs[animal_name] = btn
        attach_tooltip(btn, animal_name.capitalize())

        col += 1
        if col >= max_cols:
            col = 0
            row += 1


def create_army_panel(parent):
    frame = tk.LabelFrame(parent, text="Army / Mercenaries")
    frame.pack(anchor='w', fill='x', padx=2, pady=(2, 2))

    def heal_units():
        cmd = "k.healArmyUnits"
        set_clipboard_from_trainer(cmd)

    def teleport_units():
        cmd = "k.teleportSelectedSquadsToCursor"
        set_clipboard_from_trainer(cmd)

    def set_merc_upkeep():
        set_selected_by_text(frame, "Merc Upkeep")
        cmd = (
            "k.setMercenaryForHireCost 0 1\n"
            "k.setMercenaryForHireCost 1 1\n"
            "k.setMercenaryForHireCost 2 1"
        )
        set_clipboard_from_trainer(cmd)

    def reroll_mercs():
        cmd = "k.rerollHireMercenaries"
        set_clipboard_from_trainer(cmd)

    def unlock_merc_pool():
        cmd = "k.releaseLockedMercenaryPool"
        set_clipboard_from_trainer(cmd)


    add_buttons_grid(frame, [
        ("Heal", heal_units, "Heals all army units and give max morale"),
        ("Teleport", teleport_units, "Teleport SELECTED squads to cursor position"),
        ("Merc Upkeep", set_merc_upkeep, "set all 3 Mercenary group monthly cost to 1\n(will send 3 commands to console)"),
        ("Reroll Mercs", reroll_mercs, "3 new mercenaries to choose from"),
        ("Unlock Mercs", unlock_merc_pool, "Unlock the 'already hired' mercenary slot(s)")
    ], columns=2)

def create_economy_panel(parent):
    frame = tk.LabelFrame(parent, text="Economy")
    frame.pack(anchor='w', fill='x', padx=2, pady=(2, 2))

    # Maximális értékek
    max_influence = 9999
    max_treasury = 9999
    max_wealth = 99999
    max_devpoints = 10

    # StringVar-ok
    influence_var = tk.StringVar(value="1000")
    treasury_var = tk.StringVar(value="1000")
    wealth_var = tk.StringVar(value="500")
    devpoints_var = tk.StringVar(value="1")

    # Validációs függvények
    def make_validator(max_value):
        def validate(value):
            if value == "":
                return True
            if value.isdigit():
                return 1 <= int(value) <= max_value
            return False
        return validate

    vcmd_infl = frame.register(make_validator(max_influence))
    vcmd_tres = frame.register(make_validator(max_treasury))
    vcmd_wealth = frame.register(make_validator(max_wealth))
    vcmd_dev = frame.register(make_validator(max_devpoints))

    def add_influence():
        cmd = f'k.addInfluence {influence_var.get()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(frame, "Influence")

    def add_treasury():
        cmd = f'k.addTreasury {treasury_var.get()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(frame, "Treasury")

    def add_wealth():
        cmd = f'k.addRegionalWealth {wealth_var.get()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(frame, "Wealth")

    def add_devpoints():
        cmd = f'k.addDevelopmentPoint {devpoints_var.get()}'
        set_clipboard_from_trainer(cmd)
        set_selected_by_text(frame, "Dev Points")

    def create_entry_row(label_text, var, vcmd, command, button_text, max_value):
        row = ttk.Frame(frame)
        row.pack(anchor='w', pady=2)

        ttk.Label(row, text=f"Add (1–{max_value}):").pack(side='left', padx=(2, 0))
        entry = tk.Entry(row, textvariable=var, width=6,
                 validate="key", validatecommand=(vcmd, "%P"))
        entry.pack(side='left', padx=2)
        entry.bind("<FocusOut>", lambda e, v=var, d=var.get(): reset_if_empty(v, d))

        btn = tk.Button(row, text=button_text, width=10, command=command)
        btn.pack(side='left', padx=5)
        attach_tooltip(btn, f"Add {label_text.lower()} to player")
        return btn

    # --- Entry sorok létrehozása + gombmentés ---
    infl_btn = create_entry_row("Influence", influence_var, vcmd_infl, add_influence, "Influence", max_influence)
    tres_btn = create_entry_row("Treasury", treasury_var, vcmd_tres, add_treasury, "Treasury", max_treasury)
    wealth_btn = create_entry_row("Regional Wealth", wealth_var, vcmd_wealth, add_wealth, "Wealth", max_wealth)
    dev_btn = create_entry_row("Dev Points", devpoints_var, vcmd_dev, add_devpoints, "Dev Points", max_devpoints)

    # --- Trace események: kiemelés + vágólap frissítés ---
    def update_influence(*args):
        reset_selected_button()
        highlight_button(infl_btn)
        selected_button["btn"] = infl_btn
        add_influence()

    def update_treasury(*args):
        reset_selected_button()
        highlight_button(tres_btn)
        selected_button["btn"] = tres_btn
        add_treasury()

    def update_wealth(*args):
        reset_selected_button()
        highlight_button(wealth_btn)
        selected_button["btn"] = wealth_btn
        add_wealth()

    def update_devpoints(*args):
        reset_selected_button()
        highlight_button(dev_btn)
        selected_button["btn"] = dev_btn
        add_devpoints()

    influence_var.trace_add("write", update_influence)
    treasury_var.trace_add("write", update_treasury)
    wealth_var.trace_add("write", update_wealth)
    devpoints_var.trace_add("write", update_devpoints)

def create_population_panel(parent):
    frame = tk.LabelFrame(parent, text="Population")
    frame.pack(anchor='w', fill='x', padx=2, pady=(2, 2))

    def place_tent():
        set_clipboard_from_trainer("k.placeHomelessTent")

    def clean_region():
        set_clipboard_from_trainer(
            "k.skipMourningForRegionBuildings\n"
            "k.putOutFireForRegionBuildings\n"
            "k.healDiseaseForRegionResidents"
        )
        set_selected_by_text(frame, "Clean Region")

    tk.Button(
        frame,
        text="Place Tent",
        width=10,
        command=lambda: [place_tent(), set_selected_by_text(frame, "Place Tent")]
    ).grid(row=0, column=0, padx=2, pady=2)

    # --- Validált Entry + funkciók ---
    newfam_var = tk.StringVar(value="1")
    newmem_var = tk.StringVar(value="1")

    def validate_family_count(value):
        if value == "":
            return True
        if value.isdigit():
            return 1 <= int(value) <= 50
        return False

    def validate_member_count(value):
        if value == "":
            return True
        if value.isdigit():
            return 1 <= int(value) <= 100
        return False

    vcmd_fam = frame.register(validate_family_count)
    vcmd_mem = frame.register(validate_member_count)

    def spawn_family():
        amt = safe_int(newfam_var)
        if amt is not None:
            set_clipboard_from_trainer(f'k.spawnNewFamily {amt}')

    def spawn_member():
        amt = safe_int(newmem_var)
        if amt is not None:
            set_clipboard_from_trainer(f'k.spawnNewFamilyMember {amt}')

    # --- UI elemek ---
    tk.Label(frame, text="New Families:").grid(row=1, column=0, padx=2, sticky='w')
    entry_fam = tk.Entry(frame, textvariable=newfam_var, width=5,
                     validate="key", validatecommand=(vcmd_fam, "%P"))
    entry_fam.grid(row=1, column=1)
    entry_fam.bind("<FocusOut>", lambda e: reset_if_empty(newfam_var, "1"))

    fam_btn = tk.Button(frame, text="Spawn", width=10,
        command=lambda: [spawn_family(), set_selected_by_text(frame, "Spawn")])
    fam_btn.grid(row=1, column=2)
    attach_tooltip(fam_btn, "Spawn new families in region")

    tk.Label(frame, text="Family Members:").grid(row=2, column=0, padx=2, sticky='w')
    entry_mem = tk.Entry(frame, textvariable=newmem_var, width=5,
                     validate="key", validatecommand=(vcmd_mem, "%P"))
    entry_mem.grid(row=2, column=1)
    entry_mem.bind("<FocusOut>", lambda e: reset_if_empty(newmem_var, "1"))

    mem_btn = tk.Button(frame, text="Add", width=10,
        command=lambda: [spawn_member(), set_selected_by_text(frame, "Add")])
    mem_btn.grid(row=2, column=2)
    attach_tooltip(mem_btn, "Add family members to existing families")

    def update_family_entry(*args):
        reset_selected_button()
        highlight_button(fam_btn)
        selected_button["btn"] = fam_btn
        spawn_family()

    def update_member_entry(*args):
        reset_selected_button()
        highlight_button(mem_btn)
        selected_button["btn"] = mem_btn
        spawn_member()

    newfam_var.trace_add("write", update_family_entry)
    newmem_var.trace_add("write", update_member_entry)

    # --- Clean Region gomb ---
    clean_btn = tk.Button(
        frame,
        text="Clean Region",
        width=10,
        command=clean_region
    )
    clean_btn.grid(row=3, column=0, columnspan=3, pady=(5, 2))

    attach_tooltip(clean_btn, "Remove fire, mourning and disease from region buildings\n(will send 3 commands to console)")


def create_misc_panel(parent):
    misc_frame = tk.LabelFrame(parent, text="Miscellaneous")
    misc_frame.pack(anchor='w', fill='x', padx=2, pady=2)

    create_army_panel(misc_frame)
    create_economy_panel(misc_frame)
    create_population_panel(misc_frame)

def clipboard_monitor(root): 
    status_frame = tk.Frame(root)
    status_frame.place(relx=1.0, rely=1.0, anchor="se", x=-5, y=-5)  # jobb alsó sarok, kis margóval

    label_prefix = tk.Label(
        status_frame,
        text="Clipboard: ",
        font=("Consolas", 8),
        fg="#fff",
        bg="#111"
    )
    label_prefix.pack(side="left")

    label_content = tk.Label(
        status_frame,
        text="",
        font=("Consolas", 8),
        fg="#ff4444",
        bg="#111"
    )
    label_content.pack(side="left")

    def update_clipboard_label():
        global trainer_clipboard_content
        try:
            content = pyperclip.paste()

            # Ha a tartalom változott, de nem a trainer írta, akkor 
            if content != trainer_clipboard_content:
                # Ekkor nem a trainer írta
                label_content.config(text="Clipboard data overwritten outside of trainer")
            else:
                shown = content if len(content) <= 100 else content[:100] + "..."
                label_content.config(text=shown)

            tooltip_text = content if content == trainer_clipboard_content else ""
            for lbl in (label_prefix, label_content):
                lbl.unbind("<Enter>")
                lbl.unbind("<Leave>")
                lbl.bind("<Enter>", lambda e, txt=tooltip_text: tooltip_manager.show(lbl, txt) if txt else None)
                lbl.bind("<Leave>", lambda e: tooltip_manager.hide())

        except Exception:
            label_content.config(text="<error>")

        root.after(500, update_clipboard_label)

    update_clipboard_label()

def set_gif_background(root, gif_path):
    canvas = tk.Canvas(root, highlightthickness=0, bd=0)
    canvas.place(x=0, y=0, relwidth=1, relheight=1)

    root.update()  # Frissíti az ablak méretét

    canvas_width = root.winfo_width()
    canvas_height = root.winfo_height()

    gif = Image.open(gif_path)
    original_width, original_height = gif.size
    new_size = (int(original_width * 1), int(original_height * 1.06))

    frames = []
    for frame in ImageSequence.Iterator(gif):
        resized_frame = frame.copy().convert("RGBA").resize(new_size, Image.LANCZOS)
        frames.append(ImageTk.PhotoImage(resized_frame))

    frame_count = len(frames)

    x = canvas_width // 2
    y = canvas_height // 2
    bg_id = canvas.create_image(x, y, anchor='center', image=frames[0])

    def animate(index):
        canvas.itemconfig(bg_id, image=frames[index])
        root.after(100, animate, (index + 1) % frame_count)

    animate(0)
    return canvas


# --- Main UI Build ---
def build_ui():
    pyperclip.copy("")  # törli a vágólap tartalmát
    root = ttk.Window(themename="vapor")
    root.resizable(False, False)
    
    root.geometry("950x570")  # ha nem volt eddig megadva méret
    root.title("Manor Lords Trainer - for Console Command mods")
    root.attributes('-topmost', True)

    # --- HÁTTÉR GIF betöltés ---
    set_gif_background(root, "images/ML.gif")
    
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=9, weight="bold")
    style = ttk.Style()
    #tooltip style
    style.configure("Tooltip.TLabel",
        background="#1e1e1e",
        foreground="#ffd75f",  # sárgás-narancsos
        font=("tahoma", 8, "bold"),
        padding=3,
        relief="solid",
        borderwidth=1)
    # --- Stílusok ---
    default_font = tkfont.nametofont("TkDefaultFont")
    default_font.configure(size=9, weight="bold")
    style = ttk.Style()
    style.configure("Tooltip.TLabel",
        background="#1e1e1e",
        foreground="#ffd75f",
        font=("tahoma", 8, "bold"),
        padding=3,
        relief="solid",
        borderwidth=1)
    style.configure("Big.TButton",
        font=("Segoe UI", 14, "bold"),
        padding=10)

    # --- Hotkeyek ---
    register_hotkeys(root)

    # --- Fő keret,  ---
    main_frame = tk.Frame(root, bg="#111", bd=0)
    main_frame.pack(padx=2, pady=2)

    # Bal oldal (Add resources)
    left_frame = tk.LabelFrame(main_frame, text="Add Resources", bg="#111", fg="white")
    left_frame.grid(row=0, column=0, sticky="nw")
    create_add_resource_panel(left_frame)

    # Jobb oldal – 2 oszlop
    right_frame = tk.Frame(main_frame, bg="#111")
    right_frame.grid(row=0, column=1, sticky="nw", padx=2)

    col1 = tk.Frame(right_frame, bg="#111")
    col1.grid(row=0, column=0, sticky="nw")

    col2 = tk.Frame(right_frame, bg="#111")
    col2.grid(row=0, column=1, sticky="nw", padx=(2, 2))

    # Jobb oldal bal oszlop
    create_hotkeys_panel(col1)
    create_deposit_panel(col1)
    create_wild_animals_panel(col1)
    create_berries_stones_panel(col1)
    create_fishing_panel(col1)
    create_visibility_toggle_panel(col1, root)

    # Jobb oldal jobb oszlop
    create_spawn_animals_panel(col2)
    create_misc_panel(col2)

    # --- Clipboard monitor ---
    clipboard_monitor(root)

    root.mainloop()

if __name__ == "__main__":
    register_hotkeys()
    build_ui()  
