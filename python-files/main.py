#!/usr/bin/env python3
\"\"\"EduLauncher - original launcher (improved)

Features:
- Light theme default, dark theme option via settings.
- Tabs with shortcuts. Add via dialog; drop support if TkinterDnD2 is installed.
- Global hotkey (pynput GlobalHotKeys) configurable.
- Optional open on middle-click (requires pynput mouse listener).
- Context menu for each shortcut: Open, Open folder, Edit, Remove.
- Export/Import tabs as JSON.
- Auto-start on Windows (uses registry when available).
- build_exe.bat provided to build with PyInstaller on Windows.

Dependencies:
pip install pynput pillow TkinterDnD2  # TkinterDnD2 optional for drag-drop

Run:
python main.py
\"\"\"

import os, sys, json, webbrowser, threading, subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

CONFIG_FILE = Path(__file__).parent / "config.json"
DEFAULT_CONFIG = {
    "app_name": "EduLauncher",
    "theme": "light",  # light or dark
    "window": {"width":420,"height":240},
    "auto_hide_ms": 5000,
    "use_middle_click": True,
    "global_hotkey": "<ctrl>+<alt>+m",  # pynput format for GlobalHotKeys
    "tabs":[{"name":"Favorites","items":[]}]
}

def load_config():
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # ensure defaults for missing keys
        for k,v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
        return cfg
    except Exception as e:
        print("Failed to load config:", e)
        return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print("Failed to save config:", e)

class EduLauncher(tk.Tk):
    def __init__(self, cfg):
        super().__init__()
        self.cfg = cfg
        self.title(cfg.get("app_name","EduLauncher"))
        self.withdraw()
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self.hide)
        self.style = ttk.Style(self)
        self.apply_theme(cfg.get("theme","light"))
        self.geometry(f\"{cfg['window']['width']}x{cfg['window']['height']}\")
        self.create_widgets()
        self.hotkey_listener = None
        self.mouse_listener = None
        self.setup_listeners()

    def apply_theme(self, theme):
        if theme == "dark":
            # minimal dark styling using ttk themes if available
            try:
                self.style.theme_use('clam')
            except:
                pass
        else:
            try:
                self.style.theme_use('default')
            except:
                pass

    def create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="both", expand=True, padx=6, pady=6)
        self.notebook = ttk.Notebook(top)
        self.notebook.pack(fill="both", expand=True)
        self.tab_frames = []
        for tab in self.cfg.get("tabs",[]):
            f = ttk.Frame(self.notebook)
            self.notebook.add(f, text=tab.get("name","Tab"))
            self.tab_frames.append(f)
            self.populate_tab(f, tab)
        ctrl = ttk.Frame(self)
        ctrl.pack(fill="x", padx=6, pady=(0,6))
        ttk.Button(ctrl, text="Add", command=self.add_shortcut).pack(side="left")
        ttk.Button(ctrl, text="Edit Tabs", command=self.edit_tabs).pack(side="left", padx=4)
        ttk.Button(ctrl, text="Settings", command=self.open_settings).pack(side="right")

    def populate_tab(self, frame, tab):
        for w in frame.winfo_children():
            w.destroy()
        items = tab.get("items",[])
        cols = 4
        for idx, it in enumerate(items):
            r = idx // cols
            c = idx % cols
            btn = ttk.Button(frame, text=it.get("label", Path(it.get("path","")).name), width=18)
            btn.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            btn._item = it
            btn.bind("<Button-1>", lambda e, p=it: self.launch_item(p))
            btn.bind("<Button-3>", lambda e, b=btn: self.show_context(e, b))

    def show_context(self, event, btn):
        menu = tk.Menu(self, tearoff=0)
        item = btn._item
        menu.add_command(label="Open", command=lambda i=item: self.launch_item(i))
        menu.add_command(label="Open folder", command=lambda i=item: self.open_folder(i))
        menu.add_command(label="Edit", command=lambda b=btn: self.edit_item(b))
        menu.add_command(label="Remove", command=lambda b=btn: self.remove_item(b))
        menu.tk_popup(event.x_root, event.y_root)

    def launch_item(self, item):
        p = item.get("path")
        t = item.get("type","file")
        if not p:
            return
        try:
            if t == "url":
                webbrowser.open(p)
            else:
                if sys.platform.startswith("win"):
                    os.startfile(p)
                else:
                    subprocess.Popen(["xdg-open", p])
        except Exception as e:
            messagebox.showerror("Launch failed", str(e))

    def open_folder(self, item):
        p = item.get("path")
        if not p:
            return
        folder = str(Path(p).parent)
        try:
            if sys.platform.startswith("win"):
                os.startfile(folder)
            else:
                subprocess.Popen(["xdg-open", folder])
        except Exception as e:
            messagebox.showerror("Open folder failed", str(e))

    def edit_item(self, btn):
        item = btn._item
        new_label = simpledialog.askstring("Edit label", "Label:", initialvalue=item.get("label",""))
        if new_label is None:
            return
        item['label'] = new_label
        save_config(self.cfg)
        # refresh tab
        idx = self.notebook.index(self.notebook.select())
        self.populate_tab(self.tab_frames[idx], self.cfg['tabs'][idx])

    def remove_item(self, btn):
        idx = self.notebook.index(self.notebook.select())
        items = self.cfg['tabs'][idx].get('items',[])
        try:
            items.remove(btn._item)
            save_config(self.cfg)
            self.populate_tab(self.tab_frames[idx], self.cfg['tabs'][idx])
        except Exception as e:
            print("Remove failed", e)

    def add_shortcut(self):
        idx = self.notebook.index(self.notebook.select())
        path = filedialog.askopenfilename(title="Choose file or cancel to add URL")
        if path:
            item = {"type":"file","path":path,"label":Path(path).name}
        else:
            url = simpledialog.askstring("URL","Enter URL to add:")
            if not url:
                return
            item = {"type":"url","path":url,"label":url}
        self.cfg['tabs'][idx].setdefault('items',[]).append(item)
        save_config(self.cfg)
        self.populate_tab(self.tab_frames[idx], self.cfg['tabs'][idx])

    def edit_tabs(self):
        dlg = TabsEditor(self, self.cfg)
        self.wait_window(dlg)
        # reload tabs
        for f in self.tab_frames:
            f.destroy()
        self.tab_frames = []
        self.notebook.forget(0, 'end')
        for tab in self.cfg.get("tabs",[]):
            f = ttk.Frame(self.notebook)
            self.notebook.add(f, text=tab.get("name","Tab"))
            self.tab_frames.append(f)
            self.populate_tab(f, tab)
        save_config(self.cfg)

    def open_settings(self):
        dlg = SettingsDialog(self, self.cfg, callback=self.on_settings_saved)
        self.wait_window(dlg)

    def on_settings_saved(self, new_cfg):
        self.cfg = new_cfg
        save_config(self.cfg)
        self.apply_theme(self.cfg.get("theme","light"))
        # restart listeners to pick up hotkey/middle-click changes
        self.setup_listeners()

    def show_at_mouse(self, x=None, y=None):
        if x is None or y is None:
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
        self.update_idletasks()
        w = self.winfo_width() or self.cfg['window']['width']
        h = self.winfo_height() or self.cfg['window']['height']
        screen_w = self.winfo_screenwidth(); screen_h = self.winfo_screenheight()
        nx = min(max(0, x), screen_w - w); ny = min(max(0, y), screen_h - h)
        self.geometry(f\"+{nx}+{ny}\")
        self.deiconify(); self.lift()
        # auto-hide
        ah = self.cfg.get('auto_hide_ms',5000)
        if ah>0:
            self.after(ah, self.hide)

    def hide(self):
        self.withdraw()

    def setup_listeners(self):
        # stop old listeners if running
        try:
            if self.hotkey_listener:
                self.hotkey_listener.stop()
        except:
            pass
        try:
            if self.mouse_listener:
                self.mouse_listener.stop()
        except:
            pass

        # setup mouse middle-click listener if enabled
        if self.cfg.get("use_middle_click", True):
            try:
                from pynput import mouse
                def on_click(x,y,button,pressed):
                    try:
                        if pressed and button == mouse.Button.middle:
                            self.after(0, lambda: self.show_at_mouse(x,y))
                    except Exception as e:
                        print('mouse listener error', e)
                self.mouse_listener = mouse.Listener(on_click=on_click)
                self.mouse_listener.daemon = True
                self.mouse_listener.start()
            except Exception as e:
                print("Mouse listener not available:", e)

        # setup global hotkey using pynput GlobalHotKeys
        gh = self.cfg.get("global_hotkey","<ctrl>+<alt>+m")
        try:
            from pynput.keyboard import GlobalHotKeys
            def on_activate():
                self.after(0, self.show_at_mouse)
            # pynput expects mapping like {'<ctrl>+<alt>+m': on_activate}
            self.hotkey_listener = GlobalHotKeys({gh: on_activate})
            self.hotkey_listener.daemon = True
            self.hotkey_listener.start()
        except Exception as e:
            print("Hotkey listener not available:", e)

class TabsEditor(tk.Toplevel):
    def __init__(self, parent, cfg):
        super().__init__(parent)
        self.cfg = cfg
        self.title("Edit Tabs")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self); frm.pack(padx=8,pady=8)
        ttk.Label(frm, text="Tabs (one per line)").pack(anchor="w")
        self.text = tk.Text(frm, height=8, width=40)
        self.text.pack()
        tabs = "\\n".join(t.get('name','Tab') for t in self.cfg.get('tabs',[]))
        self.text.insert('1.0', tabs)
        ttk.Button(frm, text="Save", command=self.on_save).pack(pady=6)

    def on_save(self):
        lines = [l.strip() for l in self.text.get('1.0','end').splitlines() if l.strip()]
        self.cfg['tabs'] = [{'name':n,'items':[]} for n in lines] if lines else self.cfg.get('tabs',[])
        self.destroy()

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, cfg, callback):
        super().__init__(parent)
        self.cfg = cfg.copy()
        self.callback = callback
        self.title("Settings")
        self.create_widgets()

    def create_widgets(self):
        nb = ttk.Notebook(self); nb.pack(fill="both", expand=True, padx=8, pady=8)
        # Appearance tab
        a = ttk.Frame(nb); nb.add(a, text="Appearance")
        ttk.Label(a, text="Theme:").grid(row=0,column=0,sticky="w", pady=4)
        self.theme_var = tk.StringVar(value=self.cfg.get("theme","light"))
        ttk.Radiobutton(a, text="Light", variable=self.theme_var, value="light").grid(row=0,column=1,sticky="w")
        ttk.Radiobutton(a, text="Dark", variable=self.theme_var, value="dark").grid(row=0,column=2,sticky="w")
        ttk.Label(a, text="Icon size:").grid(row=1,column=0,sticky="w", pady=4)
        self.icon_size = tk.IntVar(value=48)
        ttk.Scale(a, from_=24, to=96, variable=self.icon_size, orient="horizontal").grid(row=1,column=1,columnspan=2, sticky="we")

        ttk.Label(a, text="Auto-hide (seconds, 0 = never):").grid(row=2,column=0,sticky="w", pady=4)
        self.auto_hide = tk.IntVar(value=self.cfg.get("auto_hide_ms",5000)//1000)
        ttk.Spinbox(a, from_=0, to=60, textvariable=self.auto_hide).grid(row=2,column=1, sticky="w")

        # Shortcuts tab
        s = ttk.Frame(nb); nb.add(s, text="Shortcuts")
        ttk.Label(s, text="Global hotkey (pynput format):").grid(row=0,column=0, sticky="w", pady=4)
        self.hotkey_entry = ttk.Entry(s); self.hotkey_entry.grid(row=0,column=1, sticky="we")
        self.hotkey_entry.insert(0, self.cfg.get("global_hotkey","<ctrl>+<alt>+m"))
        self.use_middle = tk.BooleanVar(value=self.cfg.get("use_middle_click", True))
        ttk.Checkbutton(s, text="Open with middle mouse click", variable=self.use_middle).grid(row=1,column=0, columnspan=2, sticky="w")

        # System tab
        y = ttk.Frame(nb); nb.add(y, text="System")
        self.autostart = tk.BooleanVar(value=False)
        ttk.Checkbutton(y, text="Run on Windows startup", variable=self.autostart).grid(row=0, column=0, sticky="w")
        ttk.Button(y, text="Export tabs (JSON)", command=self.export_tabs).grid(row=1,column=0, sticky="w", pady=4)
        ttk.Button(y, text="Import tabs (JSON)", command=self.import_tabs).grid(row=2,column=0, sticky="w", pady=4)
        ttk.Button(y, text="Reset config to defaults", command=self.reset_config).grid(row=3,column=0, sticky="w", pady=8)

        btns = ttk.Frame(self); btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="Save", command=self.on_save).pack(side="right", padx=6)
        ttk.Button(btns, text="Cancel", command=self.destroy).pack(side="right")

    def export_tabs(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files","*.json")])
        if not path: return
        data = {"tabs": self.cfg.get("tabs",[])}
        try:
            with open(path,"w",encoding="utf-8") as f:
                json.dump(data,f,indent=2,ensure_ascii=False)
            messagebox.showinfo("Export","Exported successfully.")
        except Exception as e:
            messagebox.showerror("Export failed", str(e))

    def import_tabs(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files","*.json")])
        if not path: return
        try:
            with open(path,"r",encoding="utf-8") as f:
                data = json.load(f)
            if "tabs" in data:
                self.cfg['tabs'] = data['tabs']
                messagebox.showinfo("Import","Imported tabs. Click Save to apply.")
            else:
                messagebox.showerror("Import failed", "No 'tabs' key found.")
        except Exception as e:
            messagebox.showerror("Import failed", str(e))

    def reset_config(self):
        if messagebox.askyesno("Reset","Reset to defaults?"):
            self.cfg = DEFAULT_CONFIG.copy()
            messagebox.showinfo("Reset","Configuration reset. Click Save to apply.")

    def on_save(self):
        self.cfg['theme'] = self.theme_var.get()
        self.cfg['auto_hide_ms'] = max(0, int(self.auto_hide.get())*1000)
        self.cfg['global_hotkey'] = self.hotkey_entry.get().strip()
        self.cfg['use_middle_click'] = bool(self.use_middle.get())
        # autostart handling
        if self.autostart.get():
            try:
                enable_autostart()
            except Exception as e:
                messagebox.showwarning("Autostart","Could not enable autostart: "+str(e))
        else:
            try:
                disable_autostart()
            except:
                pass
        self.callback(self.cfg)
        self.destroy()

def enable_autostart():
    if sys.platform.startswith("win"):
        try:
            import winreg
            exe = str(Path(sys.executable).resolve())
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, DEFAULT_CONFIG['app_name'], 0, winreg.REG_SZ, exe + " " + str(Path(__file__).name))
            winreg.CloseKey(key)
        except Exception as e:
            raise e
    else:
        raise NotImplementedError("Autostart only implemented for Windows in this script.")

def disable_autostart():
    if sys.platform.startswith("win"):
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
            winreg.DeleteValue(key, DEFAULT_CONFIG['app_name'])
            winreg.CloseKey(key)
        except Exception as e:
            pass

def main():
    cfg = load_config()
    app = EduLauncher(cfg)
    try:
        app.mainloop()
    finally:
        save_config(app.cfg)

if __name__ == "__main__":
    main()
