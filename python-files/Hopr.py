import customtkinter as ctk
import tkinter as tk
from tkinter import colorchooser
import requests
import threading
import webbrowser
import asyncio
import platform
import os
import json
import uuid
import base64
import re
import psutil
import subprocess
try:
    import win32crypt
except Exception:
    win32crypt = None
from pathlib import Path
import copy
from PIL import Image, ImageTk, ImageDraw
from io import BytesIO

# -----------------------------
# Smooth scroll container (patched)
# -----------------------------
class SmoothScrollableFrame(ctk.CTkFrame):
    def __init__(self, master, fg_color="transparent", corner_radius=12, **kwargs):
        super().__init__(master, fg_color=fg_color, **kwargs)
        self._corner_radius = corner_radius

        # Canvas + scrollbar
        self._canvas = tk.Canvas(self, bd=0, highlightthickness=0, relief="flat",
                                 bg=self._tk_color(fg_color))
        # Route scrollbar through handler to avoid fighting smooth scroller
        self._vbar = ctk.CTkScrollbar(self, orientation="vertical",
                                      command=self._on_scrollbar_command)
        self._canvas.configure(yscrollcommand=self._vbar.set)

        self._canvas.pack(side="left", fill="both", expand=True)
        self._vbar.pack(side="right", fill="y")

        # The internal viewport where children live
        self.viewport = ctk.CTkFrame(self._canvas, fg_color=fg_color, corner_radius=corner_radius)
        self._win = self._canvas.create_window((0, 0), window=self.viewport, anchor="nw")

        # Smooth-wheel state
        self._target = 0.0      # yview fraction target
        self._anim_running = False
        self._wheel_active = False   # flag while wheel animation runs

        # keep scrollregion synced to content
        self.viewport.bind("<Configure>", self._on_viewport_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind mouse wheel (Windows / Mac / X11)
        self._bind_mousewheel()

        # Avoid artifacts on very fast drags
        self._canvas.configure(yscrollincrement=1)

        # When user grabs the scrollbar, stop any smooth animation
        try:
            self._vbar.bind("<ButtonPress-1>", lambda e: self._cancel_smooth())
            self._vbar.bind("<ButtonRelease-1>", lambda e: self._flush_canvas())
        except Exception:
            pass

        # Optional: external resize callback (the parent can set this)
        self.on_canvas_resize = None

    # -------- public helpers (compat shims) --------
    def grid_columnconfigure(self, index, weight=0, **kwargs):
        self.viewport.grid_columnconfigure(index, weight=weight, **kwargs)

    def winfo_children(self):
        return self.viewport.winfo_children()

    def configure(self, **kwargs):
        if "fg_color" in kwargs:
            fg = kwargs["fg_color"]
            try:
                self.viewport.configure(fg_color=fg)
            except Exception:
                pass
            try:
                self._canvas.configure(bg=self._tk_color(fg))
            except Exception:
                pass
            kwargs.pop("fg_color", None)
        return super().configure(**kwargs)

    # -------- internals --------
    def _on_viewport_configure(self, _evt=None):
        bbox = self._canvas.bbox(self._win)
        if bbox:
            self._canvas.configure(scrollregion=bbox)
        # Make inner frame match canvas width
        self._canvas.itemconfig(self._win, width=self._canvas.winfo_width())

    def _on_canvas_configure(self, _evt=None):
        # Keep viewport width equal to canvas width
        self._canvas.itemconfig(self._win, width=self._canvas.winfo_width())
        # Let parent know so it can recompute its grid columns
        if callable(self.on_canvas_resize):
            try:
                self.on_canvas_resize()
            except Exception:
                pass

    def _bind_mousewheel(self):
        for target in (self._canvas, self.viewport):
            try:
                target.bind('<Enter>', lambda e, t=self._canvas: t.focus_set())
                target.bind('<MouseWheel>', self._on_mousewheel)  # Windows/macOS
                target.bind('<Button-4>', self._on_mousewheel)    # X11 up
                target.bind('<Button-5>', self._on_mousewheel)    # X11 down
            except Exception:
                pass

    # Route CTkScrollbar commands through here
    def _on_scrollbar_command(self, *args):
        """
        CTkScrollbar passes ('moveto', fraction) during drag and ('scroll', n, 'units'/'pages').
        We cancel any smooth animation and directly move the canvas.
        """
        self._cancel_smooth()
        try:
            if not args:
                return
            if args[0] == 'moveto':
                frac = float(args[1])
                self._canvas.yview_moveto(self._clamp(frac, 0.0, 1.0))
            elif args[0] == 'scroll':
                amount = int(args[1])
                what = args[2]
                self._canvas.yview_scroll(amount, what)
        finally:
            self._flush_canvas()

    def _on_mousewheel(self, event):
        # Normalize delta to small increments; negative is down
        if getattr(event, "num", None) == 4:   # X11 up
            delta = +120
        elif getattr(event, "num", None) == 5: # X11 down
            delta = -120
        else:                # Windows / macOS
            delta = getattr(event, "delta", 0)

        step = -delta / 1800.0  # 2x scroll distance (smaller divisor -> bigger step)
        cur1, cur2 = self._canvas.yview()
        self._target = self._clamp(cur1 + step, 0.0, 1.0)

        if not self._anim_running:
            self._anim_running = True
            self._wheel_active = True
            self.after(10, self._animate_scroll)

    def _animate_scroll(self):
        cur1, _ = self._canvas.yview()
        diff = self._target - cur1
        if abs(diff) < 0.001:
            self._canvas.yview_moveto(self._target)
            self._anim_running = False
            self._wheel_active = False
            self._flush_canvas()
            return
        self._canvas.yview_moveto(self._clamp(cur1 + diff * 0.20, 0.0, 1.0))
        self._flush_canvas()
        self.after(10, self._animate_scroll)

    def _cancel_smooth(self):
        # Stop any ongoing wheel animation so it doesn't fight with drag
        self._anim_running = False
        self._wheel_active = False

    def _flush_canvas(self):
        # Ensures the canvas redraws immediately, avoids "smear"/duplicate artifacts
        try:
            self._canvas.update_idletasks()
        except Exception:
            pass

    @staticmethod
    def _clamp(x, a, b):
        return max(a, min(b, x))

    @staticmethod
    def _tk_color(ctk_color):
        # CTk accepts hex; Canvas needs a tk-compatible color string
        return ctk_color if isinstance(ctk_color, str) else "#000000"


# =============================
# mitmproxy (lazy import gates)
# =============================
try:
    from mitmproxy import http
    from mitmproxy.options import Options
    from mitmproxy.tools.dump import DumpMaster
    MITM_AVAILABLE = True
except Exception:
    MITM_AVAILABLE = False

# -----------------------------
# Proxy-related constants
# -----------------------------
PROXY_HOST = "127.0.0.1"
PROXY_PORT = 51823
proxy_settings = {
    "DFStringHttpCurlProxyHostAndPort": f"{PROXY_HOST}:{PROXY_PORT}",
    "DFStringDebugPlayerHttpProxyUrl": f"http://{PROXY_HOST}:{PROXY_PORT}",
    "DFFlagDebugEnableHttpProxy": "True",
    "DFStringHttpCurlProxyHostAndPortForExternalUrl": f"{PROXY_HOST}:{PROXY_PORT}",
}

# -----------------------------
# Paths & settings persistence
# -----------------------------
apps = {
    "Roblox": Path.home() / "AppData/Local/Roblox",
    "Bloxstrap": Path.home() / "AppData/Local/Bloxstrap",
    "Fishstrap": Path.home() / "AppData/Local/Fishstrap",
}
SETTINGS_PATH = Path.home() / "AppData/Local/SubplaceJoiner/settings.json"
original_settings = {}

def load_settings():
    try:
        return json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_settings(data):
    try:
        SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        SETTINGS_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except Exception:
        pass

# -----------------------------
# mitmproxy interceptor
# -----------------------------
class Interceptor:
    WANTED = (
        "/v1/join-game",
        "/v1/join-game-instance",
        "/v1/join-play-together-game",
        "/v1/join-play-together-game-instance",
    )

    def request(self, flow: 'http.HTTPFlow') -> None:
        url = flow.request.pretty_url
        if any(p in url for p in self.WANTED):
            content_type = flow.request.headers.get("Content-Type", "")
            if "application/json" in content_type.lower():
                try:
                    body_json = flow.request.json()
                except json.JSONDecodeError:
                    return
                if "isTeleport" not in body_json:
                    body_json["isTeleport"] = True
                body_json.setdefault("gameJoinAttemptId", str(uuid.uuid4()))
                flow.request.set_text(json.dumps(body_json))

    def response(self, flow: 'http.HTTPFlow') -> None:
        pass

# -----------------------------
# Async proxy lifecycle
# -----------------------------
async def start_proxy(self):
    if not MITM_AVAILABLE:
        self.error_label.configure(text="⚠️ mitmproxy not installed. Proxy features disabled.")
        self.after(0, self.enable_join_buttons)
        return

    options = Options(listen_host=PROXY_HOST, listen_port=PROXY_PORT)
    master = DumpMaster(options, with_termlog=False, with_dumper=False)
    master.addons.add(Interceptor())
    asyncio.create_task(master.run())

    # Wait for mitmproxy CA to exist
    self.set_status("Preparing proxy…")
    ca_path = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem"
    for _ in range(200):
        if ca_path.exists():
            break
        await asyncio.sleep(0.05)

    # Inject cacert + temporary ClientSettings for all supported launchers
    for app_name, path in apps.items():
        versions_path = path / "Versions"
        if not versions_path.exists():
            continue
        for version_folder in versions_path.iterdir():
            if not version_folder.is_dir():
                continue
            exe_files = list(version_folder.glob("*PlayerBeta.exe"))
            if not exe_files:
                continue

            # Ensure libcurl bundle includes mitm CA
            ssl_folder = version_folder / "ssl"
            ssl_folder.mkdir(exist_ok=True)
            ca_file = ssl_folder / "cacert.pem"
            try:
                mitm_ca_content = ca_path.read_text(encoding="utf-8")
                if ca_file.exists():
                    existing_content = ca_file.read_text(encoding="utf-8")
                    if mitm_ca_content not in existing_content:
                        with open(ca_file, "a", encoding="utf-8") as f:
                            f.write("\n" + mitm_ca_content)
                else:
                    with open(ca_file, "w", encoding="utf-8") as f:
                        f.write(mitm_ca_content)
            except Exception as e:
                print("[proxy] CA write failed:", e)

            # ClientSettings override
            target_folder = version_folder if app_name.lower() == "roblox" else (Path(path) / "Modifications")
            client_settings_folder = target_folder / "ClientSettings"
            client_settings_folder.mkdir(exist_ok=True)
            settings_file = client_settings_folder / "ClientAppSettings.json"

            try:
                existing = {}
                if settings_file.exists():
                    with open(settings_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)
                original_settings[str(settings_file)] = existing
                updated = dict(existing)
                updated.update(proxy_settings)
                with open(settings_file, "w", encoding="utf-8") as f:
                    json.dump(updated, f, indent=4)
            except Exception as e:
                print("[proxy] settings write failed:", e)

    # Wait for Roblox to start
    self.set_status("Waiting for Roblox to start…")
    count = 0
    while True:
        if any((p.info.get('name') or '').lower() == "robloxplayerbeta.exe" for p in psutil.process_iter(['name'])):
            break
        else:
            count +=1
            if count >= 100:
                for file_path, content in original_settings.items():
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(content, f, indent=4)
                    except Exception as e:
                        print(f"[proxy] restore failed {file_path}: {e}")
                try:
                    await master.shutdown()
                except Exception:
                    pass
                self.after(0, self.enable_join_buttons)
                self.set_status("Proxy stopped. Roblox did not open.")
                return
        await asyncio.sleep(0.1)

    count = 0
    while True:
        if any((p.info.get('name') or '').lower() == "robloxcrashhandler.exe" for p in psutil.process_iter(['name'])):
            break
        if not any((p.info.get('name') or '').lower() == "robloxplayerbeta.exe" for p in psutil.process_iter(['name'])):
            count += 1
            if count >= 50:
                for file_path, content in original_settings.items():
                    try:
                        with open(file_path, "w", encoding="utf-8") as f:
                            json.dump(content, f, indent=4)
                    except Exception as e:
                        print(f"[proxy] restore failed {file_path}: {e}")
                try:
                    await master.shutdown()
                except Exception:
                    pass
                self.after(0, self.enable_join_buttons)
                self.set_status("Proxy stopped. Roblox closed unexpectedly.")
                return
        else:
            count = 0
        await asyncio.sleep(0.1)

    self.set_status("Roblox started")

    # Restore original ClientSettings after the Player has started reading them
    for file_path, content in original_settings.items():
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(content, f, indent=4)
        except Exception as e:
            print(f"[proxy] restore failed {file_path}: {e}")

    # Wait until Roblox exits, then shutdown proxy
    while True:
        if not any((p.info.get('name') or '').lower() == "robloxplayerbeta.exe" for p in psutil.process_iter(['name'])):
            try:
                await master.shutdown()
            except Exception:
                pass
            self.after(0, self.enable_join_buttons)
            self.set_status("Proxy stopped. Ready.")
            break
        await asyncio.sleep(0.5)

# -----------------------------
# UI App
# -----------------------------
class RobloxSubplaceExplorer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Roblox Subplace Explorer")
        self.geometry("1000x700")

        # Layout/state
        self.search_history = []              # recent ids
        self.favorites = set()                # favorite ids (persisted)
        self._proxy_thread = None
        self.current_accent = "Blue"
        self.cookie_visible = False
        self.last_places = []
        self.custom_text_color = ""           # hex like #00ffaa
        self.card_size = "Medium"             # Small / Medium / Large
        self.save_enabled = True
        self._settings = load_settings()

        # Perf helpers
        self.thumb_cache = {}        # {place_id: PIL.Image} (original 512x512)
        self._rendering = False
        self._resize_after = None

        # Theme presets (base)
        self.theme_presets = {
            "Blue": {"primary": "#2563EB", "success": "#10B981", "error": "#EF4444",
                      "text_primary": "#E5E7EB", "text_secondary": "#9CA3AF", "border": "#334155"},
            "Purple": {"primary": "#7C3AED", "success": "#10B981", "error": "#EF4444",
                        "text_primary": "#E5E7EB", "text_secondary": "#9CA3AF", "border": "#334155"},
            "Emerald": {"primary": "#059669", "success": "#22C55E", "error": "#EF4444",
                         "text_primary": "#E5E7EB", "text_secondary": "#9CA3AF", "border": "#334155"},
        }

        # ---------- Restore persisted settings (guarded) ----------
        try:
            appearance = self._settings.get("appearance_mode")
            if appearance:
                ctk.set_appearance_mode(appearance)

            saved_preset = self._settings.get("accent_preset", self.current_accent)
            custom_theme = self._settings.get("custom_theme")

            if custom_theme:
                self.theme_presets["Custom"] = custom_theme
                self.current_accent = "Custom"
            else:
                self.current_accent = saved_preset if saved_preset in self.theme_presets else "Blue"

            self.custom_text_color = self._settings.get("custom_text_color", self.custom_text_color)
            self.card_size = self._settings.get("card_size", self.card_size)
            self.save_enabled = self._settings.get("save_enabled", True)

            # NEW: restore history & favorites
            self.search_history = self._settings.get("recent_ids", []) or []
            favs = self._settings.get("favorites", [])
            if isinstance(favs, list):
                self.favorites = set(x for x in favs if str(x).isdigit())
        except Exception:
            self.current_accent = "Blue"
            self.save_enabled = True

        base_preset = self.current_accent if self.current_accent in self.theme_presets else "Blue"
        self.colors = copy.deepcopy(self.theme_presets[base_preset])

        # UI
        self.create_ui()
        self.bind_events()
        self.refresh_styles(rebuild=False)

        # Render restored history & favorites
        self.render_history()
        self.render_favorites()

        # Restore splitter position after layout exists
        try:
            y = self._settings.get("splitter_y")
            if isinstance(y, int):
                self.after(60, lambda: self.splitter.sash_place(0, 0, max(72, y)))
        except Exception:
            pass

    # -------------------------
    # Helpers
    # -------------------------
    def app_bg(self):
        return "#0f1115" if ctk.get_appearance_mode() == "Dark" else "#F3F4F6"

    def section_bg(self):
        return "#141A22" if ctk.get_appearance_mode() == "Dark" else "#E7EBF2"

    # Size profiles control BOTH dimensions & image size
    def size_profile(self):
        return {
            # card_w is the fixed card width; thumb_ratio is % of card_w
            "Small":  {"card_w": 200, "thumb_ratio": 0.56, "title_size": 11, "meta_size": 9,  "corner": 12, "btn_h": 28, "pill_w": 72},
            "Medium": {"card_w": 260, "thumb_ratio": 0.64, "title_size": 13, "meta_size": 10, "corner": 14, "btn_h": 32, "pill_w": 80},
            "Large":  {"card_w": 320, "thumb_ratio": 0.70, "title_size": 15, "meta_size": 11, "corner": 16, "btn_h": 36, "pill_w": 86},
        }[self.card_size]

    # -------------------------
    # UI Composition
    # -------------------------
    def create_ui(self):
        # Top bar
        self.topbar = ctk.CTkFrame(self, fg_color="transparent")
        self.topbar.pack(fill="x", padx=12, pady=(10, 6))

        self.title_label = ctk.CTkLabel(self.topbar, text="Subplace Joiner", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left")

        # Appearance
        self.appearance_menu = ctk.CTkOptionMenu(self.topbar, values=["System", "Light", "Dark"],
                                                 command=self.on_appearance_change)
        self.appearance_menu.set(ctk.get_appearance_mode())
        self.appearance_menu.pack(side="right", padx=(6, 0))

        # Save settings
        self.save_chk = ctk.CTkCheckBox(self.topbar, text="Save settings", command=lambda: self.persist_settings())
        self.save_chk.select() if self.save_enabled else self.save_chk.deselect()
        self.save_chk.pack(side="right", padx=(10, 8))

        # Card size selector
        self.size_menu = ctk.CTkOptionMenu(self.topbar, values=["Small", "Medium", "Large"],
                                           command=self.on_card_size_change)
        self.size_menu.set(self.card_size)
        self.size_menu.pack(side="right", padx=(6, 6))

        # Accent preset menu
        accent_values = list(self.theme_presets.keys())
        self.accent_menu = ctk.CTkOptionMenu(self.topbar, values=accent_values,
                                             command=self.on_accent_change)
        if self.current_accent not in self.theme_presets:
            self.current_accent = "Blue"
        self.accent_menu.set(self.current_accent)
        self.accent_menu.pack(side="right", padx=(6, 6))

        # Accent color wheel
        self.accent_pick_btn = ctk.CTkButton(self.topbar, text="🎨 Accent", width=100, command=self.pick_accent)
        self.accent_pick_btn._role = "primary"
        self.accent_pick_btn.pack(side="right", padx=(6, 0))

        # Text color controls
        self.textcolor_entry = ctk.CTkEntry(self.topbar, width=130, placeholder_text="# Text color")
        if self.custom_text_color:
            self.textcolor_entry.insert(0, self.custom_text_color)
        self.textcolor_entry.pack(side="right", padx=(6, 0))
        self.textcolor_btn = ctk.CTkButton(self.topbar, text="Pick Color", width=100, command=self.pick_text_color)
        self.textcolor_btn.pack(side="right", padx=(6, 0))
        self.textcolor_btn._role = "primary"

        # Main area
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Search row
        search_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        search_row.pack(fill="x")

        self.search_entry = ctk.CTkEntry(search_row, placeholder_text="Enter Place ID", height=40,
                                         font=ctk.CTkFont(size=14))
        self.search_entry.pack(side="left", fill="x", expand=True)

        # Buttons same height as entry (40)
        self.search_button = ctk.CTkButton(search_row, text="Search", width=120, height=40, command=self.search_places)
        self.search_button.pack(side="left", padx=(8, 0))
        self.search_button._role = "primary"

        self.heart_button = ctk.CTkButton(search_row, text="★ Fav", width=80, height=40, command=self.toggle_favorite)
        self.heart_button.pack(side="left", padx=(8, 0))
        self.heart_button._role = "success"

        # Error label
        self.error_label = ctk.CTkLabel(self.main_container, text="", text_color=self.colors["error"])
        self.error_label.pack(anchor="w", pady=(6, 6))

        # Cookie input row
        cookie_row = ctk.CTkFrame(self.main_container, fg_color="transparent")
        cookie_row.pack(fill="x", pady=(0, 6))
        self.cookie_entry = ctk.CTkEntry(cookie_row, placeholder_text=".ROBLOSECURITY cookie (optional)", height=36, show="*")
        self.cookie_entry.pack(side="left", fill="x", expand=True)
        self.toggle_cookie_btn = ctk.CTkButton(cookie_row, text="Show", width=80, height=36, command=self.toggle_cookie_visibility)
        self.toggle_cookie_btn.pack(side="left", padx=(8, 0))
        self.toggle_cookie_btn._role = "primary"

        # --- Splitter for history/results (manual resize) ---
        self.splitter = tk.PanedWindow(self.main_container, orient="vertical",
                                       sashwidth=6, bg=self.app_bg(), bd=0, relief="flat")
        self.splitter.pack(fill="both", expand=True)

        # TOP pane with visible gap + rounded panel
        top_container = tk.Frame(self.splitter, bg=self.app_bg(), bd=0, highlightthickness=0)
        self.splitter.add(top_container, minsize=72)
        self.top_wrapper = ctk.CTkFrame(top_container, fg_color=self.section_bg(), corner_radius=14)
        self.top_wrapper.pack(fill="both", expand=True, padx=10, pady=8)
        top_inner = ctk.CTkFrame(self.top_wrapper, fg_color="transparent")
        top_inner.pack(fill="both", expand=True, padx=8, pady=8)

        self.history_header = ctk.CTkLabel(top_inner, text="Recent Place IDs",
                                           font=ctk.CTkFont(size=12, weight="bold"))
        self.history_header.pack(anchor="w", padx=6, pady=(2, 6))

        # Recent pills
        self.history_frame = ctk.CTkFrame(top_inner, fg_color="transparent")
        self.history_frame.pack(fill="x", expand=False)

        # Favorites header + pills
        self.fav_header = ctk.CTkLabel(top_inner, text="Favorites",
                                       font=ctk.CTkFont(size=12, weight="bold"))
        self.fav_header.pack(anchor="w", padx=6, pady=(10, 6))
        self.fav_frame = ctk.CTkFrame(top_inner, fg_color="transparent")
        self.fav_frame.pack(fill="x", expand=False)

        # BOTTOM pane with visible gap + rounded panel
        bottom_container = tk.Frame(self.splitter, bg=self.app_bg(), bd=0, highlightthickness=0)
        self.splitter.add(bottom_container)
        self.bottom_wrapper = ctk.CTkFrame(bottom_container, fg_color=self.section_bg(), corner_radius=14)
        self.bottom_wrapper.pack(fill="both", expand=True, padx=10, pady=10)
        bottom_inner = ctk.CTkFrame(self.bottom_wrapper, fg_color="transparent")
        bottom_inner.pack(fill="both", expand=True, padx=8, pady=10)

        self.results_header = ctk.CTkLabel(bottom_inner, text="Results",
                                           font=ctk.CTkFont(size=12, weight="bold"))
        self.results_header.pack(anchor="w", padx=6, pady=(0, 8))

        self.results_frame = SmoothScrollableFrame(bottom_inner, fg_color=self.section_bg(), corner_radius=12)
        self.results_frame.pack(fill="both", expand=True, padx=2, pady=(0, 4))

        # NEW: tell the scroll container to ping us when its canvas resizes
        self.results_frame.on_canvas_resize = self.update_grid_columns
        # (extra safety) also bind the canvas's Configure to recompute grid
        try:
            self.results_frame._canvas.bind("<Configure>", lambda e: self.update_grid_columns())
        except Exception:
            pass

        # Status bar
        self.status_bar = ctk.CTkLabel(self, text="Ready.")
        self.status_bar.pack(fill="x", side="bottom")

        # Hold references
        self.place_cards = []
        self.history_buttons = []
        self.fav_buttons = []

        # Recompute layout (debounced) whenever top-level resizes
        self.results_frame.bind("<Configure>", lambda e: self.update_grid_columns())
        self.update_grid_columns()

    def bind_events(self):
        self.bind("<Configure>", self.on_resize)
        self.history_frame.bind("<Configure>", lambda e: self.wrap_history_buttons())
        self.fav_frame.bind("<Configure>", lambda e: self.wrap_fav_buttons())
        self.search_entry.bind("<Return>", lambda e: self.search_places())
        self.bind("<Control-f>", lambda e: self.search_entry.focus_set())
        self.bind("<Escape>", lambda e: self.clear_results())
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # -------------------------
    # Theme & color pickers
    # -------------------------
    def on_appearance_change(self, mode):
        ctk.set_appearance_mode(mode)
        try:
            self.splitter.configure(bg=self.app_bg())
            self.top_wrapper.configure(fg_color=self.section_bg())
            self.bottom_wrapper.configure(fg_color=self.section_bg())
            self.results_frame.configure(fg_color=self.section_bg())
        except Exception:
            pass
        self.refresh_styles(rebuild=True)
        self.persist_settings()

    def on_accent_change(self, name):
        if name not in self.theme_presets:
            name = "Blue"
        self.current_accent = name
        self.colors = copy.deepcopy(self.theme_presets[name])
        self.refresh_styles(rebuild=True)
        self.persist_settings()

    def on_card_size_change(self, value):
        self.card_size = value
        self.update_grid_columns()
        if self.last_places:
            self.display_results(self.last_places)
            self.update_idletasks()
            self.update_grid_columns()
        self.persist_settings()

    def pick_text_color(self):
        hexval = self.textcolor_entry.get().strip()
        if not (len(hexval) in (4, 7) and hexval.startswith('#')):
            color = colorchooser.askcolor(title="Choose text color")[1]
        else:
            color = hexval
        if color:
            self.custom_text_color = color
            self.textcolor_entry.delete(0, tk.END)
            self.textcolor_entry.insert(0, color)
            self.refresh_styles(rebuild=True)
            self.persist_settings()

    def pick_accent(self):
        color = colorchooser.askcolor(title="Choose accent color")[1]
        if not color:
            return
        base = self.theme_presets.get(self.current_accent, self.theme_presets["Blue"])
        custom = {
            "primary": color,
            "success": base["success"],
            "error": base["error"],
            "text_primary": self.colors.get("text_primary", "#E5E7EB"),
            "text_secondary": base["text_secondary"],
            "border": base["border"],
        }
        self.theme_presets["Custom"] = custom
        self.current_accent = "Custom"
        try:
            self.accent_menu.configure(values=list(self.theme_presets.keys()))
            self.accent_menu.set("Custom")
        except Exception:
            pass
        self.colors = copy.deepcopy(custom)
        self.refresh_styles(rebuild=True)
        self.persist_settings()

    def refresh_styles(self, rebuild=False):
        primary = self.colors["primary"]
        success = self.colors["success"]
        error = self.colors["error"]

        def apply_roles(widget, text_color):
            for child in widget.winfo_children():
                apply_roles(child, text_color)
                role = getattr(child, "_role", None)
                if isinstance(child, ctk.CTkButton) and role is None:
                    role = "primary"
                    child._role = "primary"
                if role and isinstance(child, ctk.CTkButton):
                    if role == "primary":
                        child.configure(fg_color=primary, text_color=text_color)
                    elif role == "success":
                        child.configure(fg_color=success, text_color=text_color)
                    elif role == "danger":
                        child.configure(fg_color=error, text_color=text_color)
                elif isinstance(child, ctk.CTkLabel):
                    try:
                        child.configure(text_color=text_color)
                    except Exception:
                        pass
                if isinstance(child, ctk.CTkOptionMenu):
                    try:
                        child.configure(fg_color=primary, button_color=primary, text_color=text_color,
                                        button_hover_color=primary)
                    except Exception:
                        pass

        text_color = (self.custom_text_color or self.textcolor_entry.get().strip() or self.colors["text_primary"]) or "#E5E7EB"
        self.colors["text_primary"] = text_color

        for btn in (self.search_button, self.heart_button, self.toggle_cookie_btn,
                    self.textcolor_btn, self.accent_pick_btn):
            if btn is not None and not getattr(btn, "_role", None):
                btn._role = "primary"
        self.heart_button._role = "success"

        apply_roles(self, text_color)

        try:
            self.history_header.configure(text_color=self.colors["text_secondary"])
            self.fav_header.configure(text_color=self.colors["text_secondary"])
            self.results_header.configure(text_color=self.colors["text_secondary"])
            self.results_frame.configure(fg_color=self.section_bg())
        except Exception:
            pass

        if rebuild and self.last_places:
            self.display_results(self.last_places)

        self.error_label.configure(text_color=error)
        self.status_bar.configure(text_color=self.colors["text_secondary"])

    # -------------------------
    # Layout / wrapping
    # -------------------------
    def update_grid_columns(self):
        """Compute columns using the actual canvas width. Make columns non-stretching."""
        prof = self.size_profile()
        target = prof["card_w"]
        try:
            width = max(int(self.results_frame._canvas.winfo_width()), 400)
        except Exception:
            width = max(self.results_frame.viewport.winfo_width(), 400)
        padding = 16
        cols = max(1, width // (target + padding))
        self.cols = cols

        # Columns must NOT stretch
        for i in range(24):
            self.results_frame.viewport.grid_columnconfigure(i, weight=0)
        for i in range(cols):
            self.results_frame.viewport.grid_columnconfigure(i, weight=0)

        self.wrap_history_buttons()
        self.wrap_fav_buttons()
        self.reflow_cards()

    def on_resize(self, event):
        if event.widget != self:
            return
        if self._resize_after is not None:
            try:
                self.after_cancel(self._resize_after)
            except Exception:
                pass
        self._resize_after = self.after(60, self.update_grid_columns)

    def wrap_history_buttons(self):
        for w in getattr(self, "history_buttons", []):
            try:
                w.grid_forget()
            except Exception:
                pass
        if not self.search_history:
            return
        frame_width = max(self.history_frame.winfo_width(), 320)
        pill_w = self.size_profile()["pill_w"] + 12
        per_row = max(1, frame_width // pill_w)
        self.history_buttons = []
        for idx, pid in enumerate(self.search_history[:200]):
            btn = ctk.CTkButton(self.history_frame, text=str(pid), width=self.size_profile()["pill_w"],
                                command=lambda p=pid: self.quick_search(p))
            btn._role = "primary"
            r = idx // per_row
            c = idx % per_row
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="w")
            self.history_buttons.append(btn)

    def wrap_fav_buttons(self):
        for w in getattr(self, "fav_buttons", []):
            try:
                w.grid_forget()
            except Exception:
                pass
        fav_list = sorted(self.favorites, key=lambda x: int(x))
        if not fav_list:
            return
        frame_width = max(self.fav_frame.winfo_width(), 320)
        pill_w = self.size_profile()["pill_w"] + 12
        per_row = max(1, frame_width // pill_w)
        self.fav_buttons = []
        for idx, pid in enumerate(fav_list):
            btn = ctk.CTkButton(self.fav_frame, text=str(pid), width=self.size_profile()["pill_w"],
                                command=lambda p=pid: self.quick_search(p))
            btn._role = "success"
            r = idx // per_row
            c = idx % per_row
            btn.grid(row=r, column=c, padx=6, pady=6, sticky="w")
            self.fav_buttons.append(btn)

    def render_history(self):
        self.wrap_history_buttons()

    def render_favorites(self):
        self.wrap_fav_buttons()

    def _bind_scroll_on(self, widget):
        try:
            widget.bind("<MouseWheel>", lambda e: self.results_frame._on_mousewheel(e))
            widget.bind("<Button-4>", lambda e: self.results_frame._on_mousewheel(e))
            widget.bind("<Button-5>", lambda e: self.results_frame._on_mousewheel(e))
        except Exception:
            pass
        try:
            for child in widget.winfo_children():
                self._bind_scroll_on(child)
        except Exception:
            pass

    def reflow_cards(self):
        for idx, card in enumerate(self.place_cards):
            try:
                self._bind_scroll_on(card)
            except Exception:
                pass
            col = idx % getattr(self, "cols", 1)
            row = idx // getattr(self, "cols", 1)
            card.grid(row=row, column=col, padx=8, pady=8, sticky="w")

    # -------------------------
    # Search / Results
    # -------------------------
    def search_places(self):
        place_id = self.search_entry.get().strip()
        if not place_id.isdigit():
            self.error_label.configure(text="⚠️ Place ID must be a number")
            return
        self.error_label.configure(text="")
        self.clear_results()
        self.search_button.configure(state="disabled", text="Searching…")

        # update history & UI
        if place_id in self.search_history:
            self.search_history.remove(place_id)
        self.search_history.insert(0, place_id)
        self.render_history()
        self.update_fav_button_state(place_id)
        self.persist_settings()  # save recent ids immediately

        threading.Thread(target=self._search_worker, args=(place_id,), daemon=True).start()

    def quick_search(self, pid):
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, str(pid))
        self.search_places()

    def _search_worker(self, place_id):
        try:
            universe_response = requests.get(
                f"https://apis.roblox.com/universes/v1/places/{place_id}/universe",
                timeout=10
            )
            universe_response.raise_for_status()
            universe_data = universe_response.json()
            universe_id = universe_data.get("universeId")

            self.root_place_id = int(place_id)
            cursor = None
            all_places = []
            while True:
                url = f"https://develop.roblox.com/v1/universes/{universe_id}/places?limit=100"
                if cursor:
                    url += f"&cursor={cursor}"
                places_response = requests.get(url, timeout=10)
                places_response.raise_for_status()
                places_data = places_response.json()
                all_places.extend(places_data.get("data", []))
                cursor = places_data.get("nextPageCursor")
                if not cursor:
                    break
            self.after(0, lambda: self.display_results(all_places))
        except Exception as e:
            self.after(0, lambda: self.error_label.configure(text=f"⚠️ {str(e)}"))
        finally:
            self.after(0, lambda: self.search_button.configure(state="normal", text="Search"))

    def clear_results(self):
        for w in self.results_frame.viewport.winfo_children():
            w.destroy()
        self.place_cards = []
        self.status_bar.configure(text="Ready.")

    # ---------- Async thumbnail loading ----------
    def _load_thumb_async(self, place_id, size, label):
        def worker():
            try:
                pil = self._get_pil_thumb(place_id)
                img = self._pil_to_tk(pil, size)
            except Exception:
                img = None
            def apply():
                try:
                    if img:
                        label.configure(image=img, text="")
                        label.image = img
                    else:
                        label.configure(text="(no image)")
                except Exception:
                    pass
            self.after(0, apply)
        threading.Thread(target=worker, daemon=True).start()

    # ---------- Thumbnails (cached) ----------
    def _get_pil_thumb(self, place_id):
        if place_id in self.thumb_cache:
            return self.thumb_cache[place_id]
        thumb_url = f"https://thumbnails.roblox.com/v1/places/gameicons?placeIds={place_id}&size=512x512&format=Png"
        try:
            meta = requests.get(thumb_url, timeout=10)
            meta.raise_for_status()
            data = meta.json()
            img_url = data.get("data", [{}])[0].get("imageUrl")
            if not img_url:
                return None
            img_response = requests.get(img_url, timeout=10)
            img_response.raise_for_status()
            pil = Image.open(BytesIO(img_response.content)).convert("RGBA")
            self.thumb_cache[place_id] = pil
            return pil
        except Exception:
            return None

    def _pil_to_tk(self, pil_img, size):
        if pil_img is None:
            return None
        img = pil_img.resize((size, size), Image.Resampling.LANCZOS).copy()
        mask = Image.new("L", (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, size, size), radius=size//6, fill=255)
        img.putalpha(mask)
        return ImageTk.PhotoImage(img)

    def fetch_thumb(self, place_id, size):
        pil = self._get_pil_thumb(place_id)
        return self._pil_to_tk(pil, size)

    def display_results(self, places):
        if self._rendering:
            return
        self._rendering = True
        try:
            self.clear_results()
            self.last_places = places

            prof = self.size_profile()
            card_width = prof["card_w"]
            thumb_size = max(56, int(card_width * prof["thumb_ratio"]))

            for idx, place in enumerate(places):
                col = idx % getattr(self, "cols", 1)
                row = idx // getattr(self, "cols", 1)

                card = ctk.CTkFrame(self.results_frame.viewport, corner_radius=prof["corner"], width=card_width)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="w")
                card.grid_propagate(False)
                self.place_cards.append(card)

                # Placeholder while image loads
                lbl = ctk.CTkLabel(card, text='Loading...', width=thumb_size, height=thumb_size)
                lbl.pack(padx=10, pady=(10, 10))
                self._load_thumb_async(place.get('id'), thumb_size, lbl)

                # title
                label_text = f"{place.get('name', 'Unknown')} (ID: {place.get('id')})"
                if place.get('id') == getattr(self, "root_place_id", None):
                    label_text += "  ⭐ ROOT"
                title_lbl = ctk.CTkLabel(
                    card,
                    text=label_text,
                    anchor="center",
                    text_color=self.colors["text_primary"],
                    wraplength=card_width-20,
                    font=ctk.CTkFont(size=prof["title_size"], weight="bold")
                )
                title_lbl.pack(padx=8, pady=(0, 6))

                # meta
                meta_lbl = ctk.CTkLabel(
                    card,
                    text=f"Created: {place.get('created', '—')}\nUpdated: {place.get('updated', '—')}",
                    text_color=self.colors["text_secondary"],
                    font=ctk.CTkFont(size=prof["meta_size"])
                )
                meta_lbl.pack(padx=8, pady=(0, 6))

                # buttons
                buttons = ctk.CTkFrame(card, fg_color="transparent")
                buttons.pack(pady=(0, 10))

                join_button = ctk.CTkButton(buttons, text="Join",
                                            height=prof["btn_h"],
                                            width=card_width//2 - 16,
                                            command=lambda pid=place.get("id"): self.join_flow(pid))
                join_button._role = "primary"
                join_button.grid(row=0, column=0, padx=(8, 6))

                open_button = ctk.CTkButton(buttons, text="Open 🌐",
                                            height=prof["btn_h"],
                                            width=card_width//2 - 16,
                                            command=lambda pid=place.get("id"): self.open_in_browser(pid))
                open_button._role = "primary"
                open_button.grid(row=0, column=1, padx=(6, 8))

            self.reflow_cards()
            self.set_status(f"Found {len(places)} places")
        finally:
            self._rendering = False

    # -------------------------
    # Favorites
    # -------------------------
    def update_fav_button_state(self, pid_text=None):
        """Adjust ★ button text to reflect current ID's favorite state."""
        pid = (pid_text or self.search_entry.get().strip())
        if pid and pid.isdigit() and pid in self.favorites:
            self.heart_button.configure(text="★ Faved")
        else:
            self.heart_button.configure(text="★ Fav")

    def toggle_favorite(self):
        pid = self.search_entry.get().strip()
        if not pid.isdigit():
            return
        if pid in self.favorites:
            self.favorites.remove(pid)
            self.set_status(f"Removed {pid} from favorites")
        else:
            self.favorites.add(pid)
            self.set_status(f"Added {pid} to favorites")
        self.update_fav_button_state(pid)
        self.render_favorites()
        self.persist_settings()  # save favorites immediately

    # -------------------------
    # Join flow (with proxy & optional cookie)
    # -------------------------
    def join_flow(self, place_id):
        cookie = (self.cookie_entry.get().strip() if hasattr(self, "cookie_entry") else "") or (self.get_roblosecurity() or "")
        try:
            if cookie:
                ok = self.try_gamejoin(place_id, cookie)
                if not ok:
                    self.error_label.configure(text="⚠️ GameJoin not ready; launching anyway…")

            self.set_status("Launching Roblox…")
            self.launch_roblox(place_id)
            self.start_proxy_thread()
        except Exception as e:
            self.error_label.configure(text=f"⚠️ {e}")
            self.set_status("Failed to launch Roblox")

    def try_gamejoin(self, place_id, cookie):
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Roblox/WinInet",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": "https://www.roblox.com/",
            "Origin": "https://www.roblox.com",
            "Cookie": f".ROBLOSECURITY={cookie};"
        })
        token = self.get_xsrf_token(sess)
        if token:
            sess.headers["X-CSRF-TOKEN"] = token

        payload = {
            "placeId": int(getattr(self, "root_place_id", place_id) or place_id),
            "isTeleport": True,
            "isImmersiveAdsTeleport": False,
            "gameJoinAttemptId": str(uuid.uuid4()),
        }
        try:
            r = sess.post("https://gamejoin.roblox.com/v1/join-game", json=payload, timeout=15)
            data = {}
            try:
                data = r.json()
            except Exception:
                pass
            return (r.status_code == 200 and data.get("status") == 2)
        except Exception as e:
            print("[join] error:", e)
            return False

    def get_xsrf_token(self, sess: requests.Session):
        try:
            r = sess.post("https://auth.roblox.com/v2/logout", timeout=10)
            token = r.headers.get("x-csrf-token") or r.headers.get("X-CSRF-TOKEN")
            if token:
                return token
        except Exception as e:
            print("[xsrf] error:", e)
        return None

    def start_proxy_thread(self):
        if getattr(self, "_proxy_thread", None) and self._proxy_thread.is_alive():
            return
        def runner():
            asyncio.run(start_proxy(self))
        self._proxy_thread = threading.Thread(target=runner, daemon=True)
        self._proxy_thread.start()
        self.set_status("Proxy running…")
        # disable Join buttons while proxy is running
        for card in self.place_cards:
            for widget in card.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, ctk.CTkButton) and "Join" in btn.cget("text"):
                            btn.configure(state="disabled")

    def enable_join_buttons(self):
        for card in self.place_cards:
            for widget in card.winfo_children():
                if isinstance(widget, ctk.CTkFrame):
                    for btn in widget.winfo_children():
                        if isinstance(btn, ctk.CTkButton) and "Join" in btn.cget("text"):
                            btn.configure(state="normal")

    # -------------------------
    # Deep link launcher
    # -------------------------
    def launch_roblox(self, place_id):
        roblox_url = f"roblox://experiences/start?placeId={place_id}"
        system = platform.system()
        if system == "Windows":
            os.startfile(roblox_url)
        elif system == "Darwin":
            subprocess.run(["open", roblox_url], check=False)
        elif system == "Linux":
            subprocess.run(["xdg-open", roblox_url], check=False)
        else:
            webbrowser.open(roblox_url)

    # -------------------------
    # Browser helpers & misc
    # -------------------------
    def get_roblosecurity(self):
        r"""Auto-reads %LocalAppData%\Roblox\LocalStorage\RobloxCookies.dat and decrypts .ROBLOSECURITY via DPAPI. Returns token or None."""
        path = os.path.expandvars(r"%LocalAppData%\Roblox\LocalStorage\RobloxCookies.dat")
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r") as f:
                data = json.load(f)
            cookies_data = data.get("CookiesData")
            if not cookies_data:
                return None
            enc = base64.b64decode(cookies_data)
            if not win32crypt:
                return None
            dec = win32crypt.CryptUnprotectData(enc, None, None, None, 0)[1]
            s = dec.decode(errors="ignore")
            m = re.search(r"\.ROBLOSECURITY\s+([^\s;]+)", s)
            return m.group(1) if m else None
        except Exception:
            return None

    def open_in_browser(self, place_id):
        webbrowser.open(f"https://www.roblox.com/games/{place_id}")

    def toggle_cookie_visibility(self):
        self.cookie_visible = not self.cookie_visible
        try:
            self.cookie_entry.configure(show="" if self.cookie_visible else "*")
            self.toggle_cookie_btn.configure(text="Hide" if self.cookie_visible else "Show")
        except Exception:
            pass

    def set_status(self, text):
        try:
            self.status_bar.configure(text=text)
        except Exception:
            pass

    # -------------------------
    # Persistence
    # -------------------------
    def persist_settings(self):
        self.save_enabled = bool(self.save_chk.get())
        if not self.save_enabled:
            return
        custom_theme = self.theme_presets.get("Custom")
        data = {
            "appearance_mode": ctk.get_appearance_mode(),
            "accent_preset": self.current_accent,
            "custom_theme": custom_theme,
            "custom_text_color": self.custom_text_color,
            "card_size": self.card_size,
            "save_enabled": self.save_enabled,
            # NEW: persist history & favorites
            "recent_ids": self.search_history[:200],
            "favorites": sorted(self.favorites, key=lambda x: int(x)),
        }
        try:
            y = self.splitter.sash_coord(0)[1]
            data["splitter_y"] = int(y)
        except Exception:
            pass
        save_settings(data)

    def on_close(self):
        self.persist_settings()
        try:
            self.destroy()
        except Exception:
            pass


if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    app = RobloxSubplaceExplorer()
    app.mainloop()
