#!/usr/bin/env python3
import rumps
import threading
import hid
import subprocess
import tkinter as tk
from tkinter import colorchooser, messagebox
from functools import partial
import json
import logging
import os
import time

# ===========================
# Config
# ===========================
VENDOR_ID = 0x1234  # Replace with your macro pad VID
PRODUCT_ID = 0x5678  # Replace with your macro pad PID
REPORT_SIZE = 8
CONFIG_FILE = "macropad_config.json"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

# ===========================
# Utilities
# ===========================
def key_detector(callback):
    root = tk.Tk()
    root.title("Press any key")
    tk.Label(root, text="Press a key now", font=("Helvetica", 14)).pack(padx=20, pady=20)
    def on_key(event):
        callback(event.keysym)
        root.destroy()
    root.bind("<Key>", on_key)
    root.mainloop()

def open_color_picker(callback):
    color = colorchooser.askcolor(title="Select RGB Color")[1]
    if color:
        callback(color)

def fade_rgb(app, start_color, end_color, steps=10, delay=0.05):
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2],16) for i in (0,2,4))
    sr, sg, sb = hex_to_rgb(start_color)
    er, eg, eb = hex_to_rgb(end_color)
    for step in range(1, steps+1):
        r = int(sr + (er - sr)*step/steps)
        g = int(sg + (eg - sg)*step/steps)
        b = int(sb + (eb - sb)*step/steps)
        app.send_rgb_to_device(f"#{r:02X}{g:02X}{b:02X}")
        time.sleep(delay)

# ===========================
# Action Registry
# ===========================
class ActionRegistry:
    def __init__(self, app):
        self.app = app
    def execute(self, action):
        if callable(action):
            action()
        elif isinstance(action, str):
            if action.startswith("shell:"):
                subprocess.run(action[6:], shell=True)
            elif action in dir(self):
                getattr(self, action)()
            else:
                logging.warning(f"Unknown action: {action}")
    # Built-in actions
    def play_pause(self):
        subprocess.run(["osascript", "-e", 'tell application "Music" to playpause()'])
    def next_track(self):
        subprocess.run(["osascript", "-e", 'tell application "Music" to next track'])
    def previous_track(self):
        subprocess.run(["osascript", "-e", 'tell application "Music" to previous track'])
    def increase_volume(self):
        subprocess.run(["osascript", "-e", 'set volume output volume ((output volume of (get volume settings)) + 5)'])
    def decrease_volume(self):
        subprocess.run(["osascript", "-e", 'set volume output volume ((output volume of (get volume settings)) - 5)'])

# ===========================
# Main App
# ===========================
class MacropadMenu(rumps.App):
    def __init__(self):
        super().__init__("Macropad")
        self.actions = ActionRegistry(self)
        self.keys = [self.actions.play_pause, self.actions.next_track, self.actions.previous_track]
        self.knob = {"cw": self.actions.increase_volume,
                     "ccw": self.actions.decrease_volume,
                     "click": self.actions.play_pause}
        self.rgb = "#FFFFFF"
        self.device = None
        self.stop_flag = threading.Event()
        self.config = {}
        self.load_config()

        # Menu setup
        self.menu = [
            rumps.MenuItem("Keys", [
                rumps.MenuItem(f"Key 1: {self.get_action_name(self.keys[0])}", callback=partial(self.customize_key,0)),
                rumps.MenuItem(f"Key 2: {self.get_action_name(self.keys[1])}", callback=partial(self.customize_key,1)),
                rumps.MenuItem(f"Key 3: {self.get_action_name(self.keys[2])}", callback=partial(self.customize_key,2))
            ]),
            rumps.MenuItem("Knob", [
                rumps.MenuItem(f"Clockwise: {self.get_action_name(self.knob['cw'])}", callback=partial(self.customize_knob,"cw")),
                rumps.MenuItem(f"Counterclockwise: {self.get_action_name(self.knob['ccw'])}", callback=partial(self.customize_knob,"ccw")),
                rumps.MenuItem(f"Click: {self.get_action_name(self.knob['click'])}", callback=partial(self.customize_knob,"click"))
            ]),
            rumps.MenuItem("RGB", [
                rumps.MenuItem(f"Current Color: {self.rgb}"),
                rumps.MenuItem("Pick Color", callback=self.customize_rgb)
            ]),
            rumps.MenuItem("Advanced Settings", [
                rumps.MenuItem("HID Mapping Mode", callback=self.hid_mapping_mode),
                rumps.MenuItem("Debug Mode", callback=self.toggle_debug)
            ]),
            "Start",
            "Stop",
            "Quit"
        ]
        self.debug = False

    def get_action_name(self, action):
        return getattr(action,'__name__',str(action))

    # ===========================
    # Customization
    # ===========================
    def customize_key(self, idx, _):
        self.open_customize_window(f"Key {idx+1}", lambda action: self.assign_key(idx, action))

    def customize_knob(self, part, _):
        self.open_customize_window(f"Knob {part.capitalize()}", lambda action: self.assign_knob(part, action))

    def customize_rgb(self, _):
        threading.Thread(target=open_color_picker, args=(self.assign_rgb,), daemon=True).start()

    def open_customize_window(self, title, assign_callback):
        win = tk.Tk()
        win.title(f"Customize {title}")
        tk.Label(win, text=f"Set action for {title}").pack(padx=10, pady=10)
        options = ["Play/Pause","Next Track","Previous Track","Increase Volume","Decrease Volume"]
        var = tk.StringVar(win)
        var.set(options[0])
        tk.OptionMenu(win,var,*options).pack(padx=10,pady=5)
        entry = tk.Entry(win,width=30)
        entry.pack(padx=10,pady=5)
        entry.insert(0,"shell:")
        tk.Button(win,text="Key Detector",command=lambda:[key_detector(assign_callback),win.destroy()]).pack(padx=10,pady=5)
        def save_action():
            action = entry.get() if entry.get()!="shell:" else var.get().replace(" ","_").lower()
            builtin_map = {
                "play_pause": self.actions.play_pause,
                "next_track": self.actions.next_track,
                "previous_track": self.actions.previous_track,
                "increase_volume": self.actions.increase_volume,
                "decrease_volume": self.actions.decrease_volume
            }
            assign_callback(builtin_map.get(action,action))
            self.save_config()
            win.destroy()
        tk.Button(win,text="Save",command=save_action).pack(padx=10,pady=5)
        win.mainloop()

    def assign_key(self, idx, action):
        self.keys[idx] = action
        self.menu["Keys"][f"Key {idx+1}: {self.get_action_name(action)}"].title = f"Key {idx+1}: {self.get_action_name(action)}"

    def assign_knob(self, part, action):
        self.knob[part] = action
        self.menu["Knob"][f"{part.capitalize()}: {self.get_action_name(action)}"].title = f"{part.capitalize()}: {self.get_action_name(action)}"

    def assign_rgb(self, color):
        prev_color = self.rgb
        self.rgb = color
        self.menu["RGB"][f"Current Color: {prev_color}"].title = f"Current Color: {color}"
        threading.Thread(target=fade_rgb,args=(self,prev_color,color),daemon=True).start()
        self.save_config()

    # ===========================
    # Advanced
    # ===========================
    def hid_mapping_mode(self,_):
        messagebox.showinfo("HID Mapping","HID Mapping Mode Enabled: logs raw bytes for each press")
        self.debug = True

    def toggle_debug(self,_):
        self.debug = not self.debug
        messagebox.showinfo("Debug Mode",f"Debug Mode {'Enabled' if self.debug else 'Disabled'}")

    # ===========================
    # HID Integration
    # ===========================
    @rumps.clicked("Start")
    def start(self,_):
        if self.device:
            return
        self.stop_flag.clear()
        threading.Thread(target=self.reader_thread,daemon=True).start()

    @rumps.clicked("Stop")
    def stop(self,_):
        self.stop_flag.set()
        if self.device:
            self.device.close()
            self.device=None

    @rumps.clicked("Quit")
    def quit_app(self,_):
        self.stop_flag.set()
        if self.device:
            self.device.close()
        rumps.quit_application()

    def reader_thread(self):
        try:
            self.device = hid.Device(VENDOR_ID,PRODUCT_ID)
        except Exception as e:
            logging.error(f"Cannot open device: {e}")
            return
        logging.info("HID device opened")
        while not self.stop_flag.is_set():
            try:
                data = self.device.read(REPORT_SIZE,timeout_ms=250)
            except Exception as e:
                logging.error(f"HID read error: {e}")
                break
            if data:
                if self.debug:
                    logging.info(f"HID report: {data}")
                self.handle_input(data)

    def handle_input(self,data):
        if self.debug:
            logging.info(f"Raw HID data: {data}")
        if data[0]: self.actions.execute(self.keys[0])
        if data[1]: self.actions.execute(self.keys[1])
        if data[2]: self.actions.execute(self.keys[2])
        if data[3]: self.actions.execute(self.knob["cw"])
        if data[4]: self.actions.execute(self.knob["ccw"])
        if data[5]: self.actions.execute(self.knob["click"])

    # ===========================
    # RGB Output
    # ===========================
    def send_rgb_to_device(self,color):
        if not self.device:
            return
        r = int(color[1:3],16)
        g = int(color[3:5],16)
        b = int(color[5:7],16)
        # Replace below with actual device write
        # self.device.write([0x00,r,g,b])
        logging.info(f"RGB sent to device: ({r},{g},{b})")

    # ===========================
    # Config
    # ===========================
    def save_config(self):
        cfg = {
            "keys": [getattr(k,'__name__',k) for k in self.keys],
            "knob": {k:getattr(v,'__name__',v) for k,v in self.knob.items()},
            "rgb": self.rgb
        }
        with open(CONFIG_FILE,"w") as f:
            json.dump(cfg,f)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE,"r") as f:
                cfg = json.load(f)
                self.config = cfg
                builtin_map = {
                    "play_pause": self.actions.play_pause,
                    "next_track": self.actions.next_track,
                    "previous_track": self.actions.previous_track,
                    "increase_volume": self.actions.increase_volume,
                    "decrease_volume": self.actions.decrease_volume
                }
                if "keys" in cfg:
                    self.keys = [builtin_map.get(k,k) for k in cfg["keys"]]
                if "knob" in cfg:
                    self.knob = {k:builtin_map.get(v,v) for k,v in cfg["knob"].items()}
                if "rgb" in cfg:
                    self.rgb = cfg["rgb"]

# ===========================
# Main
# ===========================
def main():
    MacropadMenu().run()

if __name__=="__main__":
    main()