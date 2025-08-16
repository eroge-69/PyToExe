#!/usr/bin/env python3
"""
Sleek ttkbootstrap UI for a Texting Story Builder
- Badge-free (styled Labels as badges)
- Modern gradient header + subtitle
- Split view (editor | live preview)
- Strict mode + comment rows
- Logging with RotatingFileHandler
- Shortcuts: Ctrl+S, Ctrl+B, F5 (refresh), F11 (fullscreen)
- Light/Dark theme toggle, Focus mode, Compact mode
"""

import os
import json
import zipfile
import logging
from logging.handlers import RotatingFileHandler

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
from tkinter import filedialog, messagebox, colorchooser
from tkinter.scrolledtext import ScrolledText

# -------------------------- Core builder logic --------------------------

def hex_to_rgb_floats(h: str):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join([c * 2 for c in h])
    if len(h) != 6:
        h = "555555"
    r = int(h[0:2], 16)
    g = int(h[2:4], 16)
    b = int(h[4:6], 16)
    return {"r": float(r), "g": float(g), "b": float(b)}


def parse_spec(text: str):
    meta = {"title": "Untitled", "aspect": "vertical", "theme": "dark", "background": None}
    characters, messages = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("#title:"):
            meta["title"] = line.split(":", 1)[1].strip()
        elif low.startswith("#aspect:"):
            v = line.split(":", 1)[1].strip().lower()
            meta["aspect"] = v if v in ("vertical", "horizontal") else "vertical"
        elif low.startswith("#theme:"):
            v = line.split(":", 1)[1].strip().lower()
            meta["theme"] = v if v in ("dark", "light") else "dark"
        elif low.startswith("#background:"):
            meta["background"] = line.split(":", 1)[1].strip()
        elif low.startswith("#character:"):
            payload = line.split(":", 1)[1].strip()
            parts = [p.strip() for p in payload.split("|")]
            if not parts:
                continue
            name = parts[0]
            side = (parts[1].lower() if len(parts) > 1 else "left")
            bubble = parts[2] if len(parts) > 2 else "#E9E9EB"
            fontc = parts[3] if len(parts) > 3 else "#000000"
            avatar = parts[4] if len(parts) > 4 else f"{name.lower()}.jpg"
            characters.append(
                {
                    "name": name,
                    "side": side if side in ("left", "right") else "left",
                    "bubble_hex": bubble,
                    "font_hex": fontc,
                    "avatar": avatar,
                }
            )
        else:
            if ":" in line:
                speaker, msg = line.split(":", 1)
                messages.append({"name": speaker.strip(), "text": msg.strip()})
    return meta, characters, messages


def build_config_app_schema(meta, characters, messages, add_comment_rows=False):
    char_entries, name_to_id = [], {}
    left_id = right_id = None

    for idx, ch in enumerate(characters, start=1):
        cid = idx
        name_to_id[ch["name"]] = cid
        char_entries.append(
            {
                "characterID": cid,
                "name": ch["name"],
                "avatarImageFile": ch["avatar"],
                "color": hex_to_rgb_floats(ch["bubble_hex"]),
                "fontColor": hex_to_rgb_floats(ch["font_hex"]),
                "sound": 0,
            }
        )
        if ch["side"] == "left" and left_id is None:
            left_id = cid
        if ch["side"] == "right" and right_id is None:
            right_id = cid

    if left_id is None and char_entries:
        left_id = char_entries[0]["characterID"]
    if right_id is None and len(char_entries) > 1:
        right_id = char_entries[1]["characterID"]

    messages_out = []
    for m in messages:
        speaker = m["name"]
        text = m["text"]
        cid = name_to_id.get(speaker)
        if not cid:
            cid = len(char_entries) + 1
            name_to_id[speaker] = cid
            char_entries.append(
                {
                    "characterID": cid,
                    "name": speaker,
                    "avatarImageFile": f"{speaker.lower()}.jpg",
                    "color": hex_to_rgb_floats("#E9E9EB"),
                    "fontColor": hex_to_rgb_floats("#000000"),
                    "sound": 0,
                }
            )
        side = "left" if cid == left_id else ("right" if cid == right_id else "left")

        if add_comment_rows:
            if side == "left":
                messages_out.append({"comment": 1, "leftCharacter": cid, "leftMessage": speaker})
            else:
                messages_out.append({"comment": 1, "rightCharacter": cid, "rightMessage": speaker})

        if side == "left":
            messages_out.append({"comment": 0, "leftCharacter": cid, "leftMessage": text})
        else:
            messages_out.append({"comment": 0, "rightCharacter": cid, "rightMessage": text})

    return {
        "name": meta["title"],
        "aspectRatio": meta["aspect"],
        "quality": -1,
        "backgroundImageFile": meta["background"] or "background.jpg",
        "insertVideoTitle": 0,
        "videoTitle": meta["title"],
        "hideCorrections": 0,
        "showTyping": "showTypingNone",
        "speed": -1,
        "typingSound": "typingSoundOff",
        "colorTheme": meta["theme"],
        "leftCharacter": left_id,
        "rightCharacter": right_id,
        "characters": char_entries,
        "messages": messages_out,
    }


def build_story_zip(config, assets_dir, out_path, strict=False, log_fn=lambda s: None):
    files_to_add, missing = [], []

    # Background: treat bg_* as built-in (no file required in strict)
    bg_file = config.get("backgroundImageFile")
    if bg_file:
        bg_path = os.path.join(assets_dir, bg_file)
        is_builtin_bg = isinstance(bg_file, str) and bg_file.startswith("bg_")
        if os.path.isfile(bg_path):
            files_to_add.append((bg_path, bg_file))
        else:
            if strict and not is_builtin_bg:
                missing.append(f"Missing background: {bg_path}")
            elif not is_builtin_bg:
                log_fn(f"[warn] Missing background: {bg_path}")

    # Avatars
    seen = set()
    for ch in config.get("characters", []):
        av = ch.get("avatarImageFile")
        if not av or av in seen:
            continue
        seen.add(av)
        av_path = os.path.join(assets_dir, av)
        if os.path.isfile(av_path):
            files_to_add.append((av_path, av))
        else:
            if strict:
                missing.append(f"Missing avatar: {av_path}")
            else:
                log_fn(f"[warn] Missing avatar: {av_path}")

    if strict and missing:
        raise FileNotFoundError("\n".join(missing))

    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("config.json", json.dumps(config, indent=2))
        for src, arc in files_to_add:
            zf.write(src, arcname=arc)


# -------------------------- UX: modern GUI --------------------------

TEMPLATE_TEXT = """#title: My First Story
#aspect: vertical      # vertical or horizontal
#theme: dark           # dark or light
#background: bg_2023-08-18-02-25-31   # app built-in, or use my_bg.jpg (in assets)

#character: Alice | left  | #E9E9EB | #000000 | alice.jpg
#character: Bob   | right | #1F8AF7 | #FFFFFF | bob.jpg

Alice: Hey Bob, how’s it going?
Bob: Pretty good! Just trying out this story builder.
Alice: Nice, looks like it works!
"""

LOG_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), "log.txt")


class ModernApp(tb.Window):
    def __init__(self):
        super().__init__(themename="superhero")  # default dark; runtime toggleable
        self.title("Texting Story Builder")
        self.geometry("1240x820")
        self.minsize(1024, 700)

        # style handle for theme/compact tweaks
        self.style: tb.Style = tb.Style()

        # state
        self.input_path = tb.StringVar()
        self.assets_dir = tb.StringVar()
        self.output_path = tb.StringVar()
        self.strict_var = tb.BooleanVar(value=False)
        self.comments_var = tb.BooleanVar(value=False)
        self.light_theme_var = tb.BooleanVar(value=False)
        self.focus_var = tb.BooleanVar(value=False)
        self.compact_var = tb.BooleanVar(value=False)
        self._focus_on = False

        # build UI
        self._build_header()
        self._build_body()
        self._build_logbar()
        self._init_logger()

        # preload
        self.editor.insert("1.0", TEMPLATE_TEXT)
        self.after(120, self.update_preview)

        # shortcuts
        self.bind_all("<Control-s>", lambda e: self.save_spec_as())
        self.bind_all("<Control-b>", lambda e: self.build_story())
        self.bind_all("<F5>", lambda e: self.update_preview())
        self.bind_all("<F11>", lambda e: self.toggle_fullscreen())

    # ---------- header (gradient) ----------
    def _build_header(self):
        header = tb.Frame(self, padding=(0, 0))
        header.pack(fill=X)

        canvas = tb.Canvas(header, height=92, highlightthickness=0, bd=0)
        canvas.pack(fill=X)

        def redraw(*_):
            canvas.delete("all")
            w = canvas.winfo_width() or 1240
            h = 92
            c1, c2 = (58, 130, 247), (70, 46, 128)  # blue -> indigo
            for i in range(w):
                r = int(c1[0] + (c2[0] - c1[0]) * i / w)
                g = int(c1[1] + (c2[1] - c1[1]) * i / w)
                b = int(c1[2] + (c2[2] - c1[2]) * i / w)
                canvas.create_line(i, 0, i, h, fill=f"#{r:02x}{g:02x}{b:02x}")
            canvas.create_text(
                24,
                h // 2 - 10,
                anchor="w",
                text="Texting Story Builder",
                font=("Segoe UI", 22, "bold"),
                fill="#ffffff",
            )
            canvas.create_text(
                24,
                h // 2 + 16,
                anchor="w",
                text="Build beautiful .story files",
                font=("Segoe UI", 11),
                fill="#e6ecff",
            )

        canvas.bind("<Configure>", redraw)
        self.after(10, redraw)

    # ---------- main body ----------
    def _build_body(self):
        rootpad = tb.Frame(self, padding=(16, 12, 16, 6))
        rootpad.pack(fill=BOTH, expand=True)

        # top controls row (card)
        top = tb.Labelframe(rootpad, text=" Project ", bootstyle=INFO, padding=12)
        top.pack(fill=X, pady=(0, 10))
        self.top_card = top

        # Inputs grid
        tb.Label(top, text="Input spec").grid(row=0, column=0, sticky="w")
        ipt = tb.Entry(top, textvariable=self.input_path)
        ipt.grid(row=0, column=1, sticky="we", padx=8)
        tb.Button(top, text="Open", command=self.open_spec, bootstyle=(SECONDARY, "outline")).grid(
            row=0, column=2, padx=4
        )
        tb.Button(top, text="Save As", command=self.save_spec_as, bootstyle=(SECONDARY, "outline")).grid(
            row=0, column=3, padx=4
        )
        tb.Button(top, text="Template", command=self.load_template, bootstyle=(SECONDARY, "outline")).grid(
            row=0, column=4, padx=4
        )

        tb.Label(top, text="Assets").grid(row=1, column=0, sticky="w", pady=(6, 0))
        tb.Entry(top, textvariable=self.assets_dir).grid(row=1, column=1, sticky="we", padx=8, pady=(6, 0))
        tb.Button(top, text="Browse", command=self.choose_assets, bootstyle=(SECONDARY, "outline")).grid(
            row=1, column=2, padx=4, pady=(6, 0)
        )

        tb.Label(top, text="Output").grid(row=2, column=0, sticky="w", pady=(6, 0))
        tb.Entry(top, textvariable=self.output_path).grid(row=2, column=1, sticky="we", padx=8, pady=(6, 0))
        tb.Button(top, text="Browse", command=self.choose_output, bootstyle=(SECONDARY, "outline")).grid(
            row=2, column=2, padx=4, pady=(6, 0)
        )

        # toggles + CTA (left)
        toggles = tb.Frame(top)
        toggles.grid(row=3, column=1, columnspan=2, sticky="w", pady=(10, 0))
        tb.Checkbutton(toggles, text="Strict", variable=self.strict_var, bootstyle="round-toggle").pack(
            side=LEFT, padx=(0, 12)
        )
        tb.Checkbutton(toggles, text="Comment rows", variable=self.comments_var, bootstyle="round-toggle").pack(
            side=LEFT
        )
        build_btn = tb.Button(top, text="Build .story  ▶", command=self.build_story, bootstyle=PRIMARY)
        build_btn.grid(row=3, column=4, sticky="e")
        ToolTip(build_btn, text="Ctrl+B to build")
        ToolTip(ipt, text="Path to your .txt spec file")

        # View controls on the far right
        view = tb.Frame(top)
        view.grid(row=0, column=5, rowspan=4, sticky="e", padx=(12, 0))
        tb.Checkbutton(
            view,
            text="Light theme",
            variable=self.light_theme_var,
            command=self.toggle_theme,
            bootstyle="round-toggle",
        ).pack(side=TOP, anchor="e")
        self.focus_btn = tb.Button(view, text="Focus mode", command=self.toggle_focus, bootstyle=(SECONDARY, "outline"))
        self.focus_btn.pack(side=TOP, pady=(6, 0), anchor="e")
        ToolTip(self.focus_btn, text="Hide sidebar & logs")
        self.compact_btn = tb.Button(view, text="Compact mode", command=self.toggle_compact, bootstyle=(SECONDARY, "outline"))
        self.compact_btn.pack(side=TOP, pady=(6, 0), anchor="e")
        ToolTip(self.compact_btn, text="Reduce paddings & fonts")

        top.grid_columnconfigure(1, weight=1)

        # Split view: editor | preview (cards)
        split = tb.PanedWindow(rootpad, orient=HORIZONTAL)
        split.pack(fill=BOTH, expand=True)
        self.split = split

        # Editor card
        left_card = tb.Labelframe(split, text=" Editor ", bootstyle=SECONDARY, padding=8)
        self.editor = ScrolledText(left_card, wrap="word", undo=True, maxundo=-1, height=22)
        self.editor.configure(
            font=("Cascadia Code", 11),
            background="#1b1f2a",
            foreground="#e9edf5",
            insertbackground="#e9edf5",
            relief="flat",
            borderwidth=0,
        )
        self.editor.pack(fill=BOTH, expand=True)
        self.editor.bind("<<Modified>>", self._on_text_modified)
        split.add(left_card, weight=3)

        # Right column container
        right_container = tb.Frame(split)
        split.add(right_container, weight=2)
        self.right_container = right_container

        # preview cards
        self.card_summary = tb.Labelframe(right_container, text=" Story Summary ", bootstyle=INFO, padding=10)
        self.card_summary.pack(fill=X)
        self.lbl_title = tb.Label(self.card_summary, text="Title: —", font=("Segoe UI", 11, "bold"))
        self.lbl_title.pack(anchor="w")
        self.lbl_counts = tb.Label(self.card_summary, text="Characters: 0   Messages: 0")
        self.lbl_counts.pack(anchor="w", pady=(4, 0))
        self.badges = tb.Frame(self.card_summary)
        self.badges.pack(fill=X, pady=(8, 0))
        # Badge look via Labels (inverse bootstyle for pill/filled look)
        self.badge_aspect = tb.Label(self.badges, text="vertical", bootstyle=(INFO, "inverse"), padding=(8, 2))
        self.badge_theme = tb.Label(self.badges, text="dark", bootstyle=(SECONDARY, "inverse"), padding=(8, 2))
        self.badge_bg = tb.Label(self.badges, text="bg: —", bootstyle=(SECONDARY, "inverse"), padding=(8, 2))
        for w in (self.badge_aspect, self.badge_theme, self.badge_bg):
            w.pack(side=LEFT, padx=(0, 6))

        self.card_chars = tb.Labelframe(right_container, text=" Characters ", bootstyle=SECONDARY, padding=10)
        self.card_chars.pack(fill=BOTH, expand=True, pady=(10, 0))
        self.char_list = tb.Frame(self.card_chars)
        self.char_list.pack(fill=BOTH, expand=True)

        self.card_actions = tb.Labelframe(right_container, text=" Quick Actions ", bootstyle=SECONDARY, padding=10)
        self.card_actions.pack(fill=X, pady=(10, 0))
        tb.Button(self.card_actions, text="Pick bubble color", bootstyle=INFO, command=self.pick_color).pack(
            side=LEFT, padx=(0, 8)
        )
        tb.Button(self.card_actions, text="Validate spec", bootstyle=(SECONDARY, "outline"), command=self.validate_spec).pack(
            side=LEFT
        )

        # log panel
        self.card_log = tb.Labelframe(rootpad, text=" Log ", bootstyle=SECONDARY, padding=8)
        self.card_log.pack(fill=BOTH, expand=True, pady=(10, 0))
        self.log_box = ScrolledText(self.card_log, wrap="word", height=8, state="disabled")
        self.log_box.configure(
            font=("Cascadia Code", 10),
            background="#141824",
            foreground="#cfd2dc",
            insertbackground="#cfd2dc",
            relief="flat",
            borderwidth=0,
        )
        self.log_box.pack(fill=BOTH, expand=True)

        # preload template loader after UI exists
        self.load_template = self._load_template_impl

    # ---------- status/log bar ----------
    def _build_logbar(self):
        bar = tb.Frame(self, padding=(16, 6, 16, 12))
        bar.pack(fill=X)
        self.status = tb.Label(bar, text="Ready", bootstyle=INVERSE)
        self.status.pack(side=RIGHT)

    def _init_logger(self):
        self.logger = logging.getLogger("story_builder")
        self.logger.setLevel(logging.INFO)
        self.logger.handlers.clear()
        fh = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(fh)

    # ---------- events/helpers ----------
    def log(self, msg: str, level=logging.INFO):
        self.logger.log(level, msg)
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def _on_text_modified(self, *_):
        self.editor.edit_modified(False)
        if hasattr(self, "_debounce"):
            try:
                self.after_cancel(self._debounce)
            except Exception:
                pass
        self._debounce = self.after(220, self.update_preview)

    def _load_template_impl(self):
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", TEMPLATE_TEXT)
        self.log("Template loaded into editor.")
        self.update_preview()

    def update_preview(self):
        text = self.editor.get("1.0", "end-1c")
        meta, chars, msgs = parse_spec(text)

        self.lbl_title.config(text=f"Title: {meta['title'] or 'Untitled'}")
        self.lbl_counts.config(text=f"Characters: {len(chars)}   Messages: {len(msgs)}")

        # badge-like labels
        aspect_style = (INFO, "inverse") if meta["aspect"] == "vertical" else (SUCCESS, "inverse")
        theme_style = (SECONDARY, "inverse") if meta["theme"] == "dark" else (WARNING, "inverse")
        self.badge_aspect.configure(text=meta["aspect"], bootstyle=aspect_style)
        self.badge_theme.configure(text=meta["theme"], bootstyle=theme_style)

        bg_text = meta["background"] or "—"
        self.badge_bg.configure(
            text=("bg: built-in" if isinstance(bg_text, str) and bg_text.startswith("bg_") else f"bg: {bg_text}")
        )

        # rebuild character list with color chips
        for w in self.char_list.winfo_children():
            w.destroy()
        if not chars:
            tb.Label(self.char_list, text="(No characters yet)").pack(anchor="w")
        else:
            for ch in chars:
                row = tb.Frame(self.char_list)
                row.pack(fill=X, pady=4)

                def chip(color_hex):
                    frm = tb.Frame(row, width=20, height=20)
                    frm.pack_propagate(False)
                    c = tb.Canvas(frm, width=20, height=20, highlightthickness=0, bd=0, bg=color_hex)
                    c.pack(fill=BOTH, expand=True)
                    return frm

                chip(ch["bubble_hex"]).pack(side=LEFT)
                tb.Label(row, text=" ").pack(side=LEFT)  # spacer
                chip(ch["font_hex"]).pack(side=LEFT)
                tb.Label(
                    row,
                    text=f"  {ch['name']}  ·  {ch['side']}  ·  {ch['avatar']}",
                    font=("Segoe UI", 10),
                ).pack(side=LEFT, padx=8)

        self.status.config(text=f"{len(chars)} chars · {len(msgs)} msgs · log: {os.path.basename(LOG_PATH)}")

    # ---------- UX extras ----------
    def toggle_theme(self):
        light = self.light_theme_var.get()
        theme = "flatly" if light else "superhero"
        try:
            self.style.theme_use(theme)
        except Exception:
            self.style.theme_use("flatly" if light else "darkly")
        # adjust editor/log colors to match theme
        if light:
            self.editor.configure(background="#ffffff", foreground="#1a1a1a", insertbackground="#1a1a1a")
            self.log_box.configure(background="#f6f7f9", foreground="#2c2f36", insertbackground="#2c2f36")
        else:
            self.editor.configure(background="#1b1f2a", foreground="#e9edf5", insertbackground="#e9edf5")
            self.log_box.configure(background="#141824", foreground="#cfd2dc", insertbackground="#cfd2dc")

    def toggle_focus(self):
        if not self._focus_on:
            # hide sidebar, top, logs
            try:
                self.split.forget(self.right_container)
            except Exception:
                pass
            try:
                self.top_card.pack_forget()
            except Exception:
                pass
            try:
                self.card_log.pack_forget()
            except Exception:
                pass
            self.focus_btn.configure(text="Exit focus", bootstyle=WARNING)
            self._focus_on = True
            self.status.config(text="Focus mode on")
        else:
            try:
                self.split.add(self.right_container, weight=2)
            except Exception:
                pass
            try:
                self.top_card.pack(fill=X, pady=(0, 10))
            except Exception:
                pass
            try:
                self.card_log.pack(fill=BOTH, expand=True, pady=(10, 0))
            except Exception:
                pass
            self.focus_btn.configure(text="Focus mode", bootstyle=(SECONDARY, "outline"))
            self._focus_on = False
            self.status.config(text="Focus mode off")

    def toggle_compact(self):
        compact = not self.compact_var.get()
        self.compact_var.set(compact)
        # fonts
        editor_font = ("Cascadia Code", 10 if compact else 11)
        log_font = ("Cascadia Code", 9 if compact else 10)
        self.editor.configure(font=editor_font)
        self.log_box.configure(font=log_font)
        # paddings / card density (best-effort)
        pad = 6 if compact else 10
        try:
            for lf in (self.card_summary, self.card_chars, self.card_actions, self.card_log, self.top_card):
                lf.configure(padding=pad)
        except Exception:
            pass
        # status
        self.status.config(text=("Compact mode on" if compact else "Compact mode off"))
        self.compact_btn.configure(text=("Exit compact" if compact else "Compact mode"))

    def toggle_fullscreen(self):
        cur = bool(self.attributes("-fullscreen"))
        self.attributes("-fullscreen", not cur)

    # ---------- file operations ----------
    def open_spec(self):
        path = filedialog.askopenfilename(
            title="Open story spec", filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not path:
            return
        self.input_path.set(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.delete("1.0", "end")
            self.editor.insert("1.0", content)
            if not self.assets_dir.get():
                self.assets_dir.set(os.path.dirname(path))
            self.log(f"Loaded spec: {path}")
            self.update_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")

    def save_spec_as(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save spec as",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.editor.get("1.0", "end-1c"))
            self.input_path.set(path)
            if not self.assets_dir.get():
                self.assets_dir.set(os.path.dirname(path))
            self.log(f"Saved spec: {path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def choose_assets(self):
        d = filedialog.askdirectory(title="Choose assets folder")
        if d:
            self.assets_dir.set(d)
            self.log(f"Assets folder: {d}")

    def choose_output(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".story",
            filetypes=[("Texting Story package", "*.story"), ("All files", "*.*")],
            title="Save .story as",
        )
        if path:
            self.output_path.set(path)

    def validate_spec(self):
        text = self.editor.get("1.0", "end-1c")
        meta, chars, msgs = parse_spec(text)
        issues = []
        if not meta["title"]:
            issues.append("Missing #title")
        if meta["aspect"] not in ("vertical", "horizontal"):
            issues.append("Invalid #aspect")
        if meta["theme"] not in ("dark", "light"):
            issues.append("Invalid #theme")
        if not chars:
            issues.append("No characters defined")
        if not msgs:
            issues.append("No messages")
        if issues:
            messagebox.showwarning("Validation", "Please fix:\n- " + "\n- ".join(issues))
        else:
            messagebox.showinfo("Validation", "Looks good!")

    def pick_color(self):
        color = colorchooser.askcolor(title="Pick a color")
        if color and color[1]:
            self.editor.insert("insert", color[1])

    def build_story(self):
        text = self.editor.get("1.0", "end-1c").strip()
        if not text:
            messagebox.showwarning("Empty spec", "Please enter or open a story spec.")
            return
        assets = self.assets_dir.get().strip() or "."
        outp = self.output_path.get().strip()
        if not outp:
            messagebox.showwarning("No output", "Please choose an output .story file.")
            return

        strict = self.strict_var.get()
        add_comments = self.comments_var.get()

        try:
            meta, chars, msgs = parse_spec(text)
            cfg = build_config_app_schema(meta, chars, msgs, add_comment_rows=add_comments)
            os.makedirs(os.path.dirname(os.path.abspath(outp)) or ".", exist_ok=True)
            self.log(f"Building: {outp}")
            self.log(f"Assets dir: {assets}")
            build_story_zip(cfg, assets, outp, strict=strict, log_fn=lambda s: self.log(s))
            self.log("Done.")
            messagebox.showinfo("Success", f"Built {os.path.basename(outp)}")
            self.status.config(text="Build complete ✓")
        except FileNotFoundError as e:
            self.log(str(e))
            messagebox.showerror("Missing files (strict)", str(e))
            self.status.config(text="Build failed ✗ (missing files)")
        except Exception as e:
            self.log(f"Error: {e}")
            messagebox.showerror("Error", f"Build failed:\n{e}")
            self.status.config(text="Build failed ✗")


# -------------------------- Entry point --------------------------

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
