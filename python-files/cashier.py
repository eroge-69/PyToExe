# main.py
import os
import re
import sys
import ctypes
import atexit
import shutil
import unicodedata
import msvcrt  # arrow keys

# ================== CONSOLE / THEME ==================
RESET = "\033[0m"

def rgb(r, g, b):        return f"\033[38;2;{r};{g};{b}m"
def bg(r, g, b):         return f"\033[48;2;{r};{g};{b}m"
def bold(s: str) -> str: return f"\033[1m{s}\033[22m"

COLORS = {
    "default": rgb(230, 230, 230),
    "title":   rgb(255, 0, 128),      # bright pink (borders / accent)
    "highlight_bg": bg(200, 0, 100),  # darker pink bg for "Price" label
    "divider": rgb(0, 200, 200),      # cyan (main boxes)
    "label":   rgb(150, 200, 255),
    "ok":      rgb(0, 210, 120),
    "warn":    rgb(240, 200, 0),
    "err":     rgb(235, 80, 80),      # red (Delete)
    "muted":   rgb(160, 160, 160),
    "profit":  rgb(0, 220, 120),
    "loss":    rgb(255, 90, 90),
    "number":  rgb(255, 200, 120),    # the yellow/orange number color
    "border":  rgb(0, 200, 200),
    "net_label_bg": bg(0, 200, 200),  # cyan fill behind "Net profit:"
}
C = COLORS
D = C["default"]

HL_BG  = bg(0, 200, 200)
HL_TXT = rgb(10, 10, 10)

# safe selector arrow
SELECT_ARROW = C["title"] + ">" + RESET + D
NO_ARROW     = "  "

BOX_STYLE = "rounded"

def box_chars(style=BOX_STYLE):
    if style == "rounded": return ("╭","╮","╰","╯","─","│")
    if style == "double":  return ("╔","╗","╚","╝","═","║")
    if style == "heavy":   return ("┏","┓","┗","┛","━","┃")
    return ("┌","┐","└","┘","─","│")

def enable_vt_mode():
    """Enable UTF-8 + VT sequences on Windows."""
    if not sys.platform.startswith("win"): return
    k32 = ctypes.windll.kernel32
    try:
        k32.SetConsoleOutputCP(65001)
        k32.SetConsoleCP(65001)
    except Exception:
        pass
    for handle_id in (-11, -12):  # stdout, stderr
        try:
            handle = k32.GetStdHandle(handle_id)
            mode = ctypes.c_uint()
            if k32.GetConsoleMode(handle, ctypes.byref(mode)):
                k32.SetConsoleMode(handle, ctypes.c_uint(mode.value | 0x0004))
        except Exception:
            pass

def apply_default_foreground():
    enable_vt_mode()
    sys.stdout.write(D)
    sys.stdout.flush()

def reset_theme():
    try:
        sys.stdout.write(RESET)
        sys.stdout.flush()
    except Exception:
        pass

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")
    apply_default_foreground()

apply_default_foreground()
atexit.register(reset_theme)

def console_supports_unicode() -> bool:
    if not sys.platform.startswith("win"): return True
    try:
        return ctypes.windll.kernel32.GetConsoleOutputCP() == 65001
    except Exception:
        return False

EMOJI_OK = console_supports_unicode()
MONEY_S = "💵" if EMOJI_OK else "$"
MONEY_N = "💰" if EMOJI_OK else "NET$"
FACE    = "😤" if EMOJI_OK else "(cons)"
BOX_E   = "📦" if EMOJI_OK else "[sold]"

# ================== WIDTH / ANSI HELPERS ==================
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def split_ansi(s: str):
    idx = 0
    for m in ANSI_RE.finditer(s):
        if m.start() > idx: yield ("text", s[idx:m.start()])
        yield ("ansi", m.group()); idx = m.end()
    if idx < len(s): yield ("text", s[idx:])

def char_cell_width(ch: str) -> int:
    if unicodedata.category(ch).startswith("M") or ch in ("\u200d","\u200c","\ufe0f","\ufe0e"):
        return 0
    eaw = unicodedata.east_asian_width(ch)
    return 2 if eaw in ("W","F") else 1

def visible_width(s: str) -> int:
    w = 0
    for kind, tok in split_ansi(s):
        if kind == "text":
            for ch in tok:
                w += char_cell_width(ch)
    return w

def clip_visible(s: str, maxw: int) -> str:
    out, w = [], 0
    for kind, tok in split_ansi(s):
        if kind == "ansi":
            out.append(tok); continue
        for ch in tok:
            cw = char_cell_width(ch)
            if w + cw > maxw:
                out.append("…"); return "".join(out)
            out.append(ch); w += cw
    return "".join(out)

# ================== PRINT BOX ==================
TL, TR, BL, BR, H, V = box_chars()
UI_SIDE_PAD = 1

ACCENT_ON   = True
ACCENT_GAP  = 1
ACCENT_CHAR = "┃"
ACCENT_COLOR = C["title"]

ACCENT_CAP_STYLE = "heavy"
def accent_caps(style: str):
    if style == "rounded": return "╮", "╯"
    if style == "block":   return "▜", "▟"
    return "┓", "┛"
ACCENT_TOP_CHAR, ACCENT_BOTTOM_CHAR = accent_caps(ACCENT_CAP_STYLE)

def cha(col: int) -> str:
    return f"\x1b[{max(1,col)}G"

def print_box(lines, *, width=None, border_color=None, style=None, accent=ACCENT_ON, center_mask=None):
    """Draw a cyan rounded box with optional pink accent rail on the right."""
    global TL, TR, BL, BR, H, V
    if style is not None:
        TL, TR, BL, BR, H, V = box_chars(style)
    if border_color is None:
        border_color = C["border"]

    content_w = max((visible_width(s) for s in lines), default=0)
    inner_w = max(10, width if width is not None else content_w + 2*UI_SIDE_PAD)

    cols = shutil.get_terminal_size(fallback=(100, 30)).columns
    extra = (ACCENT_GAP + 1) if accent else 0
    inner_w = min(inner_w, max(10, cols - (4 + extra)))

    left_pad_col      = 1 + 1 + UI_SIDE_PAD
    right_border_col  = 1 + 1 + inner_w
    accent_col        = right_border_col + 1 + ACCENT_GAP
    allowed = inner_w - 2*UI_SIDE_PAD

    sys.stdout.write("\x1b[?7l"); sys.stdout.flush()  # nowrap

    # top
    sys.stdout.write(border_color + TL + (H * inner_w) + TR + RESET + D)
    if accent:
        sys.stdout.write("\r" + cha(accent_col) + ACCENT_COLOR + ACCENT_TOP_CHAR + RESET + D)
    sys.stdout.write("\n")

    # content
    for i, s in enumerate(lines):
        s2 = clip_visible(s, allowed)
        sys.stdout.write(border_color + V + RESET + D + (" " * inner_w) + border_color + V + RESET + D)
        start_col = left_pad_col
        if center_mask and i < len(center_mask) and center_mask[i]:
            pad = max(0, (allowed - visible_width(s2)) // 2)
            start_col += pad
        sys.stdout.write("\r" + cha(start_col) + s2 + RESET + D)
        if accent:
            sys.stdout.write("\r" + cha(accent_col) + ACCENT_COLOR + ACCENT_CHAR + RESET + D)
        sys.stdout.write("\r" + cha(right_border_col) + border_color + V + RESET + D + "\n")

    # bottom
    sys.stdout.write(border_color + BL + (H * inner_w) + BR + RESET + D)
    if accent:
        sys.stdout.write("\r" + cha(accent_col) + ACCENT_COLOR + ACCENT_BOTTOM_CHAR + RESET + D)
    sys.stdout.write("\n")

    sys.stdout.write("\x1b[?7h"); sys.stdout.flush()  # re-enable wrap

def required_rows_for_box(num_content_lines: int) -> int:
    return 2 + num_content_lines

# ================== MINI SUB-BOX & LAYOUT HELPERS ==================
def sub_box(lines, border_color):
    """A stable mini box that keeps sides connected by measuring visible width precisely."""
    content_w = max(visible_width(l) for l in lines) if lines else 0
    inner = content_w + 2  # one space pad on each side
    top    = border_color + "╭" + "─" * inner + "╮" + RESET + D
    middle = []
    for l in lines:
        pad = content_w - visible_width(l)
        middle.append(border_color + "│ " + RESET + D + l + (" " * pad) + border_color + " │" + RESET + D)
    bottom = border_color + "╰" + "─" * inner + "╯" + RESET + D
    return [top] + middle + [bottom]

def box_visible_width(lines) -> int:
    return max(visible_width(l) for l in lines) if lines else 0

def hstack(boxes, gap=4):
    """Horizontally stack multiple boxes (each is a list of lines)."""
    widths = [box_visible_width(b) for b in boxes]
    heights = [len(b) for b in boxes]
    H = max(heights) if heights else 0
    out = []
    for i in range(H):
        parts = []
        for b, w in zip(boxes, widths):
            if i < len(b):
                parts.append(b[i])
            else:
                parts.append(" " * w)
        out.append((" " * gap).join(parts))
    return out

def indent_lines(lines, n_spaces=2):
    pad = " " * n_spaces
    return [pad + l for l in lines]

# ================== TITLE ==================
def bracket_title_lines(text: str, color, style="rounded", padding=1):
    # Keep ASCII only (no fullwidth) so it always renders; compact capsule.
    if style == "double":
        tl, tr, bl, br, hch = "╔","╗","╚","╝","═"
    elif style == "heavy":
        tl, tr, bl, br, hch = "┏","┓","┗","┛","━"
    else:
        tl, tr, bl, br, hch = "╭","╮","╰","╯","─"
    inner = " " * padding + text + " " * padding
    top    = color + (tl + (hch * visible_width(inner)) + tr) + RESET + D
    middle = color + inner + RESET + D
    bottom = color + (bl + (hch * visible_width(inner)) + br) + RESET + D
    return [top, middle, bottom]

# ================== DATA / REGEX ==================
TRANSCRIPTS_DIR = "transcripts"
RE_CONSUMED = re.compile(r"^(Consumed)\s*[:\-]\s*([+-]?\d+(?:\.\d+)?)\s*$", re.IGNORECASE)
RE_SOLD     = re.compile(r"^(Sold)\s*[:\-]\s*([+-]?\d+(?:\.\d+)?)\s*$", re.IGNORECASE)
RE_VOLUME   = re.compile(r"(\d+(?:\.\d+)?)\s*ml", re.IGNORECASE)
RE_UNIT     = re.compile(r"^(Unit)\s*[:\-]\s*([+-]?\d+(?:\.\d+)?)\s*$", re.IGNORECASE)
RE_SIGNED   = re.compile(r"[+-]?\d+(?:\.\d+)?")
RE_WHOLE_SIGNED = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*$")

def first_signed_float(text: str):
    m = RE_SIGNED.search(text); return float(m.group()) if m else None
def volume_float(text: str):
    m = RE_VOLUME.search(text); return float(m.group(1)) if m else None
def parse_whole_signed_or_none(text: str):
    m = RE_WHOLE_SIGNED.match(text); return float(m.group(1)) if m else None

def read_lines(p):
    with open(p,"r",encoding="utf-8") as f:
        return [l.rstrip("\n") for l in f.readlines()]

def write_lines(p, lines):
    with open(p,"w",encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

# ================== PRICE ROOF ==================
def price_roof_box(price_value: float):
    label = C["highlight_bg"] + " Price " + RESET + D
    value = C["number"] + f"{price_value:.2f}" + RESET + D
    line  = label + " " * (30 - visible_width(label) - visible_width(value)) + value
    box_color = C["title"]
    top    = " " + box_color + "┌" + "─" * (visible_width(line)+2) + "┐" + RESET + D
    middle = box_color + "│" + RESET + D + line + " " + box_color + "  │" + RESET + D
    bottom = " " + box_color + "└" + "─" * (visible_width(line)+2) + "┘" + RESET + D
    return [top, middle, bottom]

# ===== NEW: single box for Volume / Remaining ml / Missing ml =====
def _aligned_three_volume_lines(volume_val: float, remaining_val: float) -> list[str]:
    """
    One compact box: Volume, Remaining ml, Missing ml (all right-aligned),
    so there is a single border around all of them.
    """
    # remaining_val here can be negative if oversold/overconsumed — keep the sign for display style
    missing_val = max(0.0, volume_val - remaining_val)  # consumed + sold (never negative)

    r1 = C["number"] + f"{volume_val:.1f}ml" + RESET + D
    r2 = C["number"] + f"_-{remaining_val:.1f}ml-_" + RESET + D
    r3 = C["number"] + f"_-{missing_val:.1f}ml-_" + RESET + D

    rmax = max(visible_width(r1), visible_width(r2), visible_width(r3))
    l1 = "Volume:".ljust(10)    + " " + " "*(rmax - visible_width(r1)) + r1
    l2 = "Remaining:".ljust(10) + " " + " "*(rmax - visible_width(r2)) + r2
    l3 = "Missing:".ljust(10)   + " " + " "*(rmax - visible_width(r3)) + r3
    return [l1, l2, l3]

# ================== PANEL (compose + layout) ==================
def label(text): return C["label"] + text + RESET + D

def compose_panel_thc_lines(content: str):
    rows = [ln.rstrip() for ln in content.splitlines() if ln.strip()]
    price=None; volume_str=""; volume_val=0.0; consumed=0.0; sold=0.0; unit=None; txns=[]; reading=False
    for ln in rows:
        low = ln.strip().lower()
        if ln.lower().startswith("unit"):
            m = RE_UNIT.match(ln.strip())
            if m: unit = float(m.group(2))
            continue
        if price is None:
            v = first_signed_float(ln)
            if v is not None: price=v; continue
        if ("ml" in low) and not volume_str:
            volume_str = ln.strip(); v = volume_float(ln); volume_val = v or volume_val; continue
        m = RE_CONSUMED.match(ln.strip())
        if m: consumed = max(0.0, float(m.group(2))); continue
        m = RE_SOLD.match(ln.strip())
        if m: sold = max(0.0, float(m.group(2))); continue
        if low == "transactions:": reading=True; continue
        if reading:
            v = parse_whole_signed_or_none(ln) or first_signed_float(ln)
            if v is not None: txns.append(v)
            else: reading=False

    remaining_ml = volume_val - (consumed + sold)             # can be negative (we keep the sign for the styled display)
    gross_sales = sum(txns) if txns else 0.0
    net_profit  = gross_sales - (price or 0.0)
    profit_color = C["profit"] if gross_sales >= 0 else C["loss"]
    net_color    = C["profit"] if net_profit >= 0 else C["loss"]

    # ----- rate mapping: 0.5 ml -> 250.0, so 1.0 ml -> 500.0
    RATE_PER_HALF = 250.0
    RATE_PER_ML   = RATE_PER_HALF * 2.0

    remaining_value = max(0.0, remaining_ml) * RATE_PER_ML
    missing_value   = max(0.0, volume_val - remaining_ml) * RATE_PER_ML  # (consumed + sold) * 500

    unit_val = unit if unit is not None else 0.0            # price per 0.5 ml (user-set)
    unit_per_ml = unit_val * 2.0
    potential   = unit_val * (volume_val * 2.0)             # total potential value if all volume sold at unit price
    est_current = unit_per_ml * sold                        # current estimated profit from sold ml
    # estimated unit price that matches actual gross (per 0.5 & per ml)
    if sold > 0:
        est_unit_per_ml  = gross_sales / sold
        est_unit_per_half = est_unit_per_ml * 0.5
    else:
        est_unit_per_ml = est_unit_per_half = 0.0
    consumed_value = consumed * unit_per_ml                 # newly requested line

    # ========== Header (title + price tag) ==========
    title_lines = bracket_title_lines("THC", C["title"], style="rounded", padding=1)
    center_mask = [True, True, True]

    price_box = price_roof_box(price if price is not None else 0.0)

    # ========== TOP ROW: left value box + right unit box ==========
    value_lines = [
        "Remaining value:",
        C["number"] + f"{remaining_value:.2f}" + RESET + D,
        "",
        "Missing value:",
        C["number"] + f"{missing_value:.2f}" + RESET + D
    ]
    value_box = sub_box(value_lines, C["divider"])

    unit_lines = [
        "Unit (0.5ml): " + C["number"] + f"{unit_val:.2f}" + RESET + D,
        "Potential: "   + C["number"] + f"{potential:.2f}" + RESET + D,
        "Est/unit: "    + C["number"] + f"{est_unit_per_half:.2f}/0.5" + RESET + D +
                         "  (" + C["number"] + f"{est_unit_per_ml:.2f}/ml" + RESET + D + ")",
        "Est curr: "    + C["number"] + f"{est_current:.2f}" + RESET + D,
    ]
    unit_box = sub_box(unit_lines, C["title"])

    top_row = hstack([value_box, unit_box], gap=6)

    # ========== SECOND ROW: left ml box (Volume/Remaining/Missing ml) + right stats ==========
    ml_box = sub_box(_aligned_three_volume_lines(volume_val, remaining_ml), C["divider"])

    stats_lines = [
        "▣ " + label("Consumed:") + f"{consumed:.1f}ml" + "   " +
        "▣ " + label("Sold:") + f"{sold:.1f}ml",
        "Consumed value: " + C["number"] + f"{consumed_value:.2f}" + RESET + D,
        "",
        "Profit: " + profit_color + f"{MONEY_S} {gross_sales:.2f}" + RESET + D,
    ]
    # Net profit label (yellow text on cyan bg)
    net_label = C["net_label_bg"] + C["number"] + " Net profit: " + RESET + D
    net_line = net_label + " " + net_color + f"{MONEY_N} {net_profit:.2f}" + RESET + D
    net_inner = sub_box([net_line], C["border"])
    stats_box = sub_box(stats_lines + [""] + indent_lines(net_inner, 1), C["divider"])

    mid_row = hstack([ml_box, stats_box], gap=6)

    # ======== Build the outer panel content lines ========
    content_lines = []
    content_lines += title_lines
    content_lines += [""]
    content_lines += price_box
    content_lines += [""]
    content_lines += top_row
    content_lines += [""]
    content_lines += mid_row

    lines = content_lines
    center_mask += [False] * (len(lines) - len(center_mask))
    return lines, center_mask

def draw_panel_thc(content: str, inner_width: int | None = None):
    lines, center_mask = compose_panel_thc_lines(content)
    print_box(lines, style=BOX_STYLE, accent=True, center_mask=center_mask, width=inner_width)

# ================== KEY INPUT (arrows) ==================
def read_key():
    """Return 'up','down','enter','esc' for arrow navigation."""
    while True:
        ch = msvcrt.getwch()
        if ch == '\r':
            return "enter"
        if ch == '\x1b':
            if msvcrt.kbhit():
                msvcrt.getwch()
            return "esc"
        if ch in ('\x00', '\xe0'):
            ch2 = msvcrt.getwch()
            if ch2 == 'H': return "up"
            if ch2 == 'P': return "down"

# ================== GENERIC SELECT LIST ==================
def set_window_exact(cols: int, lines: int):
    cols = max(30, cols)
    lines = max(10, lines)
    try:
        os.system(f"mode con: cols={cols} lines={lines}")
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            GWL_STYLE = -16
            WS_SIZEBOX = 0x00040000
            WS_MAXIMIZEBOX = 0x00010000
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
            style &= ~WS_SIZEBOX
            style &= ~WS_MAXIMIZEBOX
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
    except Exception:
        pass

def select_from_list(title: str, items: list[str], hint: str = "↑/↓ move  •  Enter select  •  Esc cancel", start_index=0) -> int | None:
    idx = max(0, min(start_index, len(items)-1)) if items else 0
    while True:
        clear_screen()
        lines = [C["title"] + title + RESET + D, ""]
        for i, text in enumerate(items):
            prefix = (SELECT_ARROW + " ") if i == idx else NO_ARROW
            if i == idx:
                pretty = HL_BG + HL_TXT + " " + text + " " + RESET + D
                lines.append(prefix + pretty)
            else:
                lines.append(prefix + text)
        lines += ["", C["muted"] + hint + RESET + D]

        content_w = max(visible_width(s) for s in lines) if lines else 10
        inner_w = max(10, content_w + 2*UI_SIDE_PAD)
        cols_needed = 2 + inner_w + 2
        rows_needed = 2 + len(lines)
        set_window_exact(cols_needed, rows_needed)

        print_box(lines, accent=True, width=inner_w)

        key = read_key()
        if key == "up":
            idx = (idx - 1) % len(items) if items else 0
        elif key == "down":
            idx = (idx + 1) % len(items) if items else 0
        elif key == "enter":
            return idx if items else None
        elif key == "esc":
            return None

# ================== STYLED INPUT HELPERS ==================
PROMPT_ARROW = C["divider"] + "➤ " + RESET + D
def safe_input(prompt: str) -> str:
    try:
        return input(C["muted"] + prompt + RESET + D + "\n" + PROMPT_ARROW)
    except (EOFError, KeyboardInterrupt):
        return ""

def form_prompt(title: str, fields: list[str]) -> list[str]:
    clear_screen()
    lines = [C["title"] + bold(title) + RESET + D, ""]
    lines += [f"- {f}" for f in fields]
    content_w = max(visible_width(s) for s in lines) if lines else 30
    inner_w = max(30, content_w + 2*UI_SIDE_PAD)
    set_window_exact(2 + inner_w + 2, 2 + len(lines))
    print_box(lines, accent=True, width=inner_w)

    answers = []
    for f in fields:
        ans = safe_input(f"{f}:")
        answers.append(ans)
        clear_screen()
        print_box(lines, accent=True, width=inner_w)
    return answers

def float_or_zero(s: str) -> float:
    try:
        return float(first_signed_float(s) if first_signed_float(s) is not None else 0.0)
    except Exception:
        return 0.0

# ================== ACTIONS ==================
def _get_field_index(lines, regex):
    for i, raw in enumerate(lines):
        if regex.match(raw.strip()): return i
    return None

def apply_record(filepath: str):
    header = [
        C["title"] + bold("Edit Entry") + RESET + D,
        "",
        "Enter a volume delta (positive or negative).",
        "Then choose Consumed or Sold.",
        "If you leave Amount blank and a Unit price exists, we'll auto-compute **only for Sold**.",
    ]
    cw = max(visible_width(s) for s in header)
    iw = max(40, cw + 2*UI_SIDE_PAD)
    set_window_exact(2 + iw + 2, 2 + len(header))
    print_box(header, accent=True, width=iw)

    lines = read_lines(filepath)
    RE_CONSUMED_L = re.compile(r"^(Consumed)\s*[:\-]\s*([+-]?\d+(?:\.\d+)?)\s*$", re.IGNORECASE)
    RE_SOLD_L     = re.compile(r"^(Sold)\s*[:\-]\s*([+-]?\d+(?:\.\d+)?)\s*$", re.IGNORECASE)
    RE_UNIT_L     = re.compile(r"^(Unit)\s*[:\-]\s*([+-]?\d+(?:\.\d+)?)\s*$", re.IGNORECASE)

    def get_idx(regex):
        for i, raw in enumerate(lines):
            if regex.match(raw.strip()): return i
        return None

    consumed_idx = get_idx(RE_CONSUMED_L)
    sold_idx     = get_idx(RE_SOLD_L)
    unit_idx     = get_idx(RE_UNIT_L)
    tx_idx = None
    for i, raw in enumerate(lines):
        if raw.strip().lower() == "transactions:":
            tx_idx = i; break

    def get_val(idx, regex):
        if idx is None: return 0.0
        m = regex.match(lines[idx].strip())
        return float(m.group(2)) if m else 0.0

    cur_consumed = max(0.0, get_val(consumed_idx, RE_CONSUMED_L))
    cur_sold     = max(0.0, get_val(sold_idx, RE_SOLD_L))
    unit_price   = get_val(unit_idx, RE_UNIT_L) if unit_idx is not None else None

    vol_in = safe_input("Enter volume sold/consumed or 0 to access transactions").strip()
    clear_screen()
    try: vol_delta = float(vol_in)
    except ValueError:
        print_box([C["err"] + "Invalid volume." + RESET + D], accent=True, width=40); return

    bucket = ""
    if vol_in != "0":
        bucket = safe_input("Apply this to (c)onsumed or (s)old? Press Enter to skip [s]").strip().lower()
        clear_screen()
    if bucket not in ("c","s",""):
        print_box([C["err"] + "Invalid choice." + RESET + D], accent=True, width=40); return

    if bucket == "c":
        new_consumed = max(0.0, cur_consumed + vol_delta)
        if consumed_idx is None: lines.append(f"Consumed-{new_consumed}")
        else: lines[consumed_idx] = f"Consumed-{new_consumed}"
    elif bucket == "s":
        new_sold = max(0.0, cur_sold + vol_delta)
        if sold_idx is None: lines.append(f"Sold-{new_sold}")
        else: lines[sold_idx] = f"Sold-{new_sold}"

    amt_in = safe_input("Enter amount for this action (blank = auto for Sold if Unit price set, negative allowed)").strip()
    clear_screen()
    amount = None
    if amt_in != "":
        try:
            amount = float(amt_in)
        except ValueError:
            print_box([C["err"] + "Invalid amount. Skipped." + RESET + D], accent=True, width=40)
            amount = None
    else:
        # only auto-add amount for Sold entries
        if bucket == "s" and unit_price is not None and vol_in != "0":
            try:
                amount = float(vol_delta) * float(unit_price) * 2.0  # unit_price is per 0.5ml -> per ml * vol
            except Exception:
                amount = None

    if amount is not None:
        if tx_idx is None:
            lines.append("transactions:"); tx_idx = len(lines)-1
        insert_at = tx_idx+1
        while insert_at < len(lines):
            ln = lines[insert_at]
            if parse_whole_signed_or_none(ln) is None and first_signed_float(ln) is None: break
            insert_at += 1
        lines.insert(insert_at, f"{amount:.2f}")

    write_lines(filepath, lines)
    print_box([C["ok"] + "Entry recorded. File updated!" + RESET + D], accent=True, width=40)
    safe_input("Press Enter to continue...")

# ================== AUTO-FIT WINDOW FOR PANEL + ACTIONS ==================
def required_width_and_height_for_boxes(boxes: list[list[str]]) -> tuple[int, int]:
    inner_ws = []
    rows = 0
    for lines in boxes:
        content_w = max(visible_width(s) for s in lines) if lines else 10
        inner_w = max(10, content_w + 2*UI_SIDE_PAD)
        inner_ws.append(inner_w)
        rows += required_rows_for_box(len(lines))
    cols_needed = max(2 + w + 2 for w in inner_ws) if inner_ws else 40
    return cols_needed, rows

def compose_actions_lines(actions, idx):
    lines = [C["title"] + "Actions" + RESET + D, ""]
    for i, text in enumerate(actions):
        is_delete = ("Delete transcript" in text)
        label_t = (C["err"] + text + RESET + D) if is_delete else text
        prefix = (SELECT_ARROW + " ") if i == idx else NO_ARROW
        if i == idx:
            pretty = HL_BG + HL_TXT + " " + label_t + " " + RESET + D
            lines.append(prefix + pretty)
        else:
            lines.append(prefix + label_t)
    lines += ["", C["muted"] + "↑/↓ move  •  Enter select  •  Esc close" + RESET + D]
    return lines

def viewer_main_inline(path: str):
    actions = ["Edit transcript", "Set unit price", "Delete transcript", "Pop out", "Close window"]
    idx = 0
    while True:
        content = "\n".join(read_lines(path))
        panel_lines, center_mask = compose_panel_thc_lines(content)
        actions_lines = compose_actions_lines(actions, idx)

        cols_needed, rows_needed = required_width_and_height_for_boxes([panel_lines, actions_lines])
        # Add a couple of rows for breathing room
        set_window_exact(cols_needed, rows_needed + 1)

        clear_screen()

        def inner_w_for(lines):
            cw = max(visible_width(s) for s in lines)
            return max(10, cw + 2*UI_SIDE_PAD)

        print_box(panel_lines, style=BOX_STYLE, accent=True,
                  center_mask=center_mask, width=inner_w_for(panel_lines))
        print_box(actions_lines, accent=True, width=inner_w_for(actions_lines))

        key = read_key()
        if key == "up":
            idx = (idx - 1) % len(actions)
        elif key == "down":
            idx = (idx + 1) % len(actions)
        elif key == "enter":
            choice = actions[idx]
            if choice == "Close window":
                return
            elif choice == "Edit transcript":
                apply_record(path)
            elif choice == "Delete transcript":
                clear_screen()
                confirm_lines = [
                    C["err"] + bold("DELETE transcript?") + RESET + D,
                    "",
                    f"This will permanently remove:",
                    os.path.basename(path),
                    "",
                    "Press Enter to confirm, Esc to cancel."
                ]
                cw = max(visible_width(s) for s in confirm_lines)
                iw = max(10, cw + 2*UI_SIDE_PAD)
                set_window_exact(2 + iw + 2, 2 + len(confirm_lines))
                print_box(confirm_lines, accent=True, width=iw)
                while True:
                    k = read_key()
                    if k == "enter":
                        try:
                            os.remove(path)
                            print_box([C["ok"] + "Deleted." + RESET + D], accent=True, width=30)
                        except Exception as e:
                            print_box([C["err"] + f"Failed to delete: {e}" + RESET + D], accent=True, width=40)
                        safe_input("Press Enter...")
                        return
                    if k == "esc":
                        break
            elif choice == "Pop out":
                launch_viewer_window(path)
            elif choice == "Set unit price":
                val = safe_input("Enter new unit price (per 0.5ml): ").strip()
                try:
                    v = float(val)
                except Exception:
                    print_box([C["err"] + "Invalid value." + RESET + D], accent=True, width=36)
                    safe_input("Press Enter...")
                else:
                    lines = read_lines(path)
                    unit_idx = _get_field_index(lines, RE_UNIT)
                    if unit_idx is None:
                        insert_at = 1 if len(lines) > 1 else len(lines)
                        lines.insert(insert_at, f"Unit-{v}")
                    else:
                        lines[unit_idx] = f"Unit-{v}"
                    write_lines(path, lines)
        elif key == "esc":
            return

# ================== POP-OUT VIEWER WINDOW ==================
def launch_viewer_window(path: str):
    py = sys.executable
    script = os.path.abspath(sys.argv[0])
    cmd = f'cmd /c start "" "{py}" "{script}" --view "{path}"'
    os.system(cmd)

def viewer_main_popup(path: str):
    viewer_main_inline(path)

# ================== LIST & CREATE ==================
def list_and_view(folder=TRANSCRIPTS_DIR):
    if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)
    while True:
        files = [f for f in os.listdir(folder) if f.lower().endswith(".txt")]
        files.sort()
        items = [f for f in files] + ["Back"]
        sel = select_from_list("Available TXT Files", items)
        if sel is None or items[sel] == "Back":
            return
        path = os.path.join(folder, items[sel])
        viewer_main_inline(path)

def create_new(folder=TRANSCRIPTS_DIR):
    if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)

    fields = [
        "Price (number only)",
        "Volume (ml, e.g., 10)",
        "Consumed (ml, e.g., 0.5)",
        "Sold (ml, e.g., 1)",
        "Unit price (per 0.5ml, optional)",
        "Transactions (comma separated, optional)"
    ]
    answers = form_prompt("Create New Transcript", fields)
    price_s, volume_s, consumed_s, sold_s, unit_s, tx_input = answers

    def fz(x):
        try:
            v = first_signed_float(x)
            return 0.0 if v is None else float(v)
        except Exception:
            return 0.0

    price    = fz(price_s)
    volume   = fz(volume_s)
    consumed = max(0.0, fz(consumed_s))
    sold     = max(0.0, fz(sold_s))
    unit_val = None if unit_s.strip() == "" else fz(unit_s)

    existing = [f for f in os.listdir(folder) if f.lower().startswith("transcript") and f.lower().endswith(".txt")]
    nums = [int(re.search(r"(\d+)", f).group(1)) for f in existing if re.search(r"(\d+)", f)]
    next_num = max(nums)+1 if nums else 1
    name = f"transcript{next_num}.txt"
    path = os.path.join(folder, name)

    tx_lines = [x.strip() for x in (tx_input or "").split(",") if x.strip()]

    out = [
        "Thc",
        f"{price}",
        f"_-{volume}ml-_",
        f"Consumed-{consumed}",
        f"Sold-{sold}",
    ]
    if unit_val is not None:
        out.insert(2, f"Unit-{unit_val}")  # keep it near top
    if tx_lines:
        out += ["transactions:"] + [str(fz(t)) for t in tx_lines]

    write_lines(path, out)

    done_lines = [C["ok"] + f"{name} created!" + RESET + D]
    cw = max(visible_width(s) for s in done_lines)
    iw = max(40, cw + 2*UI_SIDE_PAD)
    set_window_exact(2 + iw + 2, 2 + len(done_lines))
    print_box(done_lines, accent=True, width=iw)
    safe_input("Press Enter...")

# ================== MAIN MENU ==================
def main_menu():
    items = ["View TXT files", "Create new transcript", "Exit"]
    while True:
        sel = select_from_list("Menu", items)
        if sel is None:
            return
        choice = items[sel]
        if choice == "View TXT files":
            list_and_view()
        elif choice == "Create new transcript":
            create_new()
        elif choice == "Exit":
            return

# ================== ENTRY POINT ==================
def main():
    try:
        if len(sys.argv) >= 3 and sys.argv[1] == "--view":
            viewer_main_popup(sys.argv[2])
            return
        main_menu()
    finally:
        reset_theme()

if __name__ == "__main__":
    main()
