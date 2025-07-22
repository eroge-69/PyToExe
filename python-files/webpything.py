#!/usr/bin/env python3
import sys
import ctypes
from cefpython3 import cefpython as cef
import customtkinter as ctk

# ─── CEF + Tkinter Integration ──────────────────────────────────────────────
class ChromiumFrame(ctk.CTkFrame):
    def __init__(self, master, initial_url="about:blank", **kwargs):
        super().__init__(master, **kwargs)
        self.initial_url = initial_url
        self.browser = None

        # Delay embed until frame is fully created
        self.bind("<Map>", self.on_map)
        # Keep browser in sync with widget size
        self.bind("<Configure>", self.on_configure)

    def on_map(self, _):
        if not self.browser:
            self.embed_browser()

    def embed_browser(self):
        window_info = cef.WindowInfo()
        rect = [0, 0, self.winfo_width(), self.winfo_height()]
        # On Windows, you need to set this style flag to allow embedding
        if sys.platform.startswith("win"):
            ctypes.windll.user32.SetWindowLongW(
                self.winfo_id(), -16,
                ctypes.windll.user32.GetWindowLongW(self.winfo_id(), -16)
                | 0x40000000  # WS_CHILD
            )
        window_info.SetAsChild(self.winfo_id(), rect)
        self.browser = cef.CreateBrowserSync(window_info, url=self.initial_url)

        # Pump CEF message loop periodically
        self.after(10, self.message_loop)

    def message_loop(self):
        cef.MessageLoopWork()
        self.after(10, self.message_loop)

    def on_configure(self, event):
        if self.browser:
            self.browser.SetBounds(0, 0, event.width, event.height)

    def load_url(self, url):
        if self.browser:
            self.browser.LoadUrl(url)

# ─── Main App ────────────────────────────────────────────────────────────────
class WebEmulator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Chromium‑Powered Web Emulator")
        self.geometry("1200x800")

        # ─ Sidebar ────────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=180)
        sidebar.pack(side="left", fill="y", padx=5, pady=5)
        sidebar.pack_propagate(False)

        new_tab_btn = ctk.CTkButton(sidebar, text="+ New Tab", command=self.add_tab)
        new_tab_btn.pack(fill="x", pady=(10, 5), padx=10)

        self.tabs_frame = ctk.CTkFrame(sidebar)
        self.tabs_frame.pack(fill="both", expand=True, padx=5)

        # ─ Main Area ───────────────────────────────────────────────────────────
        main = ctk.CTkFrame(self)
        main.pack(side="right", fill="both", expand=True, padx=5, pady=5)

        # Toolbar
        toolbar = ctk.CTkFrame(main, height=40)
        toolbar.pack(fill="x", pady=(0,10), padx=10)
        toolbar.pack_propagate(False)

        self.back_btn  = ctk.CTkButton(toolbar, text="◀", width=30, command=self.go_back)
        self.back_btn.pack(side="left", padx=(0,5))
        self.forward_btn  = ctk.CTkButton(toolbar, text="▶", width=30, command=self.go_forward)
        self.forward_btn.pack(side="left", padx=5)
        self.refresh_btn = ctk.CTkButton(toolbar, text="⟳", width=30, command=self.refresh)
        self.refresh_btn.pack(side="left", padx=5)
        self.home_btn   = ctk.CTkButton(toolbar, text="🏠", width=30, command=self.go_home)
        self.home_btn.pack(side="left", padx=5)
        self.close_btn   = ctk.CTkButton(toolbar, text="✖", width=30, command=self.close_tab)
        self.close_btn.pack(side="left", padx=(5,20))

        self.url_entry = ctk.CTkEntry(toolbar, placeholder_text="https://example.com")
        self.url_entry.pack(side="left", fill="x", expand=True)
        ctk.CTkButton(toolbar, text="Go", width=60, command=self.on_go).pack(side="right", padx=(10,0))

        # Content holders
        self.content = ctk.CTkFrame(main)
        self.content.pack(fill="both", expand=True, padx=10, pady=(0,10))

        # Tab storage
        self.tabs = []
        self.current = None

        # Initialize CEF
        cef_settings = {"multi_threaded_message_loop": False}
        cef.Initialize(settings=cef_settings)

        # Create first tab
        self.add_tab()

        # On close, cleanup CEF
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_tab(self):
        frame = ChromiumFrame(self.content, initial_url="https://www.google.com")
        frame.pack(fill="both", expand=True)
        frame.pack_forget()

        tab = {"frame": frame, "history": [], "index": -1}
        idx = len(self.tabs)
        self.tabs.append(tab)

        btn = ctk.CTkButton(self.tabs_frame, text=f"Tab {idx+1}",
                            width=140, anchor="w",
                            command=lambda i=idx: self.switch(i))
        btn.pack(fill="x", pady=2)
        tab["button"] = btn

        self.switch(idx)

    def switch(self, idx):
        if self.current is not None:
            self.tabs[self.current]["frame"].pack_forget()
        self.current = idx
        tab = self.tabs[idx]
        tab["frame"].pack(fill="both", expand=True)
        # Update address bar
        if tab["index"] >= 0:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, tab["history"][tab["index"]])
        else:
            self.url_entry.delete(0, "end")

    def close_tab(self):
        if self.current is None: return
        tab = self.tabs.pop(self.current)
        tab["frame"].destroy()
        tab["button"].destroy()
        # re-number buttons
        for i, t in enumerate(self.tabs):
            t["button"].configure(text=f"Tab {i+1}", command=lambda j=i: self.switch(j))
        # pick new current
        if self.tabs:
            self.switch(min(self.current, len(self.tabs)-1))
        else:
            self.on_close()

    def navigate(self, url):
        if not url.startswith(("http://","https://")):
            url = "http://"+url
        tab = self.tabs[self.current]
        # trim forward history
        if tab["index"] < len(tab["history"])-1:
            tab["history"] = tab["history"][:tab["index"]+1]
        tab["history"].append(url)
        tab["index"] += 1
        tab["frame"].load_url(url)
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, url)

    def on_go(self):     self.navigate(self.url_entry.get().strip())
    def go_back(self):
        tab = self.tabs[self.current]
        if tab["index"] > 0:
            tab["index"] -= 1
            url = tab["history"][tab["index"]]
            tab["frame"].load_url(url)
            self.url_entry.delete(0, "end"); self.url_entry.insert(0, url)
    def go_forward(self):
        tab = self.tabs[self.current]
        if tab["index"] < len(tab["history"]) - 1:
            tab["index"] += 1
            url = tab["history"][tab["index"]]
            tab["frame"].load_url(url)
            self.url_entry.delete(0, "end"); self.url_entry.insert(0, url)
    def refresh(self):
        tab = self.tabs[self.current]
        if tab["index"] >= 0:
            tab["frame"].load_url(tab["history"][tab["index"]])
    def go_home(self):
        self.navigate("https://www.google.com")

    def on_close(self):
        cef.Shutdown()
        self.destroy()

if __name__ == "__main__":
    app = WebEmulator()
    app.mainloop()
