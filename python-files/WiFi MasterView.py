import sys
import subprocess
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from collections import Counter
import csv
import webbrowser
import json
import os
import winreg

# === Program Name (change here to rename everywhere) ===
PROGRAM_NAME = 'WiFi MasterView'

# Language dictionary for UI text
LANGS = {
    'en': {
        'title': PROGRAM_NAME,
        'subtitle': 'Best AP channel',
        'scan': 'Scan Networks',
        'export': 'Export Results',
        'auto_on': 'Auto Refresh: On',
        'auto_off': 'Auto Refresh: Off',
        'interval': 'Interval (s):',
        'filter_title': 'Network Filter',
        'filter_label': 'Search (SSID, BSSID, Auth):',
        'signal_label': 'Min Signal %:',
        'apply_filter': 'Apply Filter',
        'no_results': 'No matching results.',
        'no_networks': 'No networks found.',
        'scan_failed': 'Scan failed.',
        'export_success': 'Results exported successfully.',
        'export_fail': 'Export failed:',
        'no_export': 'No results to export.',
        'plot': 'Show Chart',
        'plot_title': 'Channel Distribution (Filtered)',
        'plot_note': 'Please scan or filter networks first.',
        'error': 'Error',
        'info': 'Info',
        'ok': 'OK',
        'status_ready': 'Ready.',
        'status_showing': 'Showing {n} networks.',
        'status_scanning': 'Scanning...',
        'status_none': 'No networks found.',
        'status_no_match': 'No matching results.',
        'status_failed': 'Scan failed.',
        'export_csv': 'CSV Files',
        'export_txt': 'Text Files',
        'export_title': 'Export Results',
        'apply': 'Apply',
        'lang': 'Language',
        'columns': ["SSID", "Auth", "Channel", "Signal", "BSSID"],
        'channel': 'Channel',
        'networks': 'Networks',
        'signal': 'Signal',
        'help': 'Help',
    },
    'ar': {
        'title': 'واي فاي ماستر فيو',
        'subtitle': 'أفضل قناة',
        'scan': 'فحص الشبكات',
        'export': 'تصدير النتائج',
        'auto_on': 'تحديث تلقائي: تشغيل',
        'auto_off': 'تحديث تلقائي: إيقاف',
        'interval': 'الفاصل (ث):',
        'filter_title': 'فلترة الشبكات',
        'filter_label': 'بحث (SSID أو BSSID أو Auth):',
        'signal_label': 'الحد الأدنى للإشارة %:',
        'apply_filter': 'تطبيق الفلترة',
        'no_results': 'لا توجد نتائج مطابقة.',
        'no_networks': 'لم يتم العثور على شبكات.',
        'scan_failed': 'فشل الفحص.',
        'export_success': 'تم تصدير النتائج بنجاح.',
        'export_fail': 'خطأ في التصدير:',
        'no_export': 'لا توجد نتائج لتصديرها.',
        'plot': 'عرض الرسم البياني',
        'plot_title': 'توزيع الشبكات على القنوات (بعد الفلترة)',
        'plot_note': 'يرجى فحص الشبكات أو تطبيق الفلترة أولاً.',
        'error': 'خطأ',
        'info': 'ملاحظة',
        'ok': 'موافق',
        'status_ready': 'جاهز.',
        'status_showing': 'تم عرض {n} شبكة.',
        'status_scanning': 'جاري الفحص ...',
        'status_none': 'لم يتم العثور على شبكات.',
        'status_no_match': 'لا توجد نتائج مطابقة.',
        'status_failed': 'فشل الفحص.',
        'export_csv': 'ملفات CSV',
        'export_txt': 'ملفات نصية',
        'export_title': 'تصدير النتائج',
        'apply': 'تطبيق',
        'lang': 'اللغة',
        'columns': ["SSID", "Auth", "Channel", "Signal", "BSSID"],
        'channel': 'القناة',
        'networks': 'الشبكات',
        'signal': 'الإشارة',
        'help': 'المساعدة',
    }
}

SETTINGS_FILE = 'settings.json'

def detect_windows_theme():
    # Try to detect Windows dark mode (returns 'dark', 'light', or None)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize')
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        return 'light' if value == 1 else 'dark'
    except Exception:
        return None

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f)
    except Exception:
        pass

# WiFi scan using netsh (Windows only)
def scan_wifi():
    try:
        output = subprocess.check_output(
            ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
            encoding='utf-8', errors='ignore'
        )
    except Exception as e:
        return [], str(e)
    networks = []
    ssid = None
    channel = None
    bssid = None
    signal = None
    auth = None
    for line in output.splitlines():
        ssid_match = re.match(r'\s*SSID\s+\d+\s*:\s*(.*)', line)
        if ssid_match:
            ssid = ssid_match.group(1).strip()
        ch_match = re.match(r'\s*Channel\s*:\s*(\d+)', line)
        if ch_match:
            channel = int(ch_match.group(1))
        bssid_match = re.match(r'\s*BSSID\s+\d+\s*:\s*(.*)', line)
        if bssid_match:
            bssid = bssid_match.group(1).strip()
        sig_match = re.match(r'\s*Signal\s*:\s*(\d+)%', line)
        if sig_match:
            signal = int(sig_match.group(1))
        auth_match = re.match(r'\s*Authentication\s*:\s*(.*)', line)
        if auth_match:
            auth = auth_match.group(1).strip()
        if ssid and channel and bssid and signal is not None and auth:
            networks.append({
                'ssid': ssid,
                'channel': channel,
                'signal': signal,
                'bssid': bssid,
                'auth': auth
            })
            bssid = None
            signal = None
            auth = None
    return networks, None

# Recommend the best channel (least crowded)
def recommend_channel(networks):
    if not networks:
        return None
    channels = [n['channel'] for n in networks]
    usage = Counter(channels)
    best = min(usage, key=lambda ch: usage[ch])
    return best

def channel_overlap_weighted(channels, networks, band):
    overlap = {}
    for ch in sorted(set(channels)):
        if band == "2.4GHz":
            overlap_nets = [n for n in networks if abs(n['channel'] - ch) <= 2]
        elif band == "5GHz":
            overlap_nets = [n for n in networks if abs(n['channel'] - ch) <= 4]
        else:
            overlap_nets = [n for n in networks if n['channel'] == ch]
        # Weighted: higher signal = more impact
        weighted = sum(n['signal']/100 for n in overlap_nets)
        overlap[ch] = {'count': len(overlap_nets), 'weighted': weighted}
    return overlap

def best_channel_advanced(channels, networks, band):
    overlap = channel_overlap_weighted(channels, networks, band)
    if not overlap:
        return None, overlap
    best = min(overlap, key=lambda ch: (overlap[ch]['weighted'], overlap[ch]['count']))
    return best, overlap

HELP_TEXT = {
    'en': (
        "How to use WiFi Analyzer and Scanner:\n"
        "1. Click 'Scan Networks' to list nearby Wi-Fi networks.\n"
        "2. Use the Band selector to view 2.4GHz, 5GHz, or all networks.\n"
        "3. Filter networks by name, BSSID, Auth, or minimum signal.\n"
        "4. The chart shows channel congestion. Pink bars = less crowded, red = most crowded.\n"
        "5. 'Best AP channel' recommends the optimal channel for your router.\n"
        "6. Use 'Open Router Settings' to change your router's channel manually.\n"
        "7. Use 'Show Signal Strength Graph' to compare signal quality.\n"
        "Tips for better Wi-Fi:\n"
        "- Choose a channel with the least overlap and lowest weighted value.\n"
        "- Place your router in a central, open location.\n"
        "- Avoid overlapping channels with strong signals from neighbors.\n"
        "- For 2.4GHz, channels 1, 6, or 11 are usually best.\n"
        "- For 5GHz, use the least crowded channel.\n"
    ),
    'ar': (
        "كيفية استخدام محلل و ماسح الواي فاي:\n"
        "1. اضغط على 'فحص الشبكات' لعرض الشبكات القريبة.\n"
        "2. استخدم اختيار النطاق لعرض شبكات 2.4GHz أو 5GHz أو الكل.\n"
        "3. فلتر النتائج حسب الاسم أو BSSID أو نوع التوثيق أو الإشارة.\n"
        "4. الرسم البياني يوضح ازدحام القنوات. الأعمدة الوردية الأقل ازدحامًا، الحمراء الأكثر ازدحامًا.\n"
        "5. 'أفضل قناة' تعرض القناة المثالية لجهازك.\n"
        "6. استخدم 'فتح إعدادات الراوتر' لتغيير القناة يدويًا.\n"
        "7. استخدم 'رسم قوة الإشارة' لمقارنة جودة الشبكات.\n"
        "نصائح لتحسين الواي فاي:\n"
        "- اختر قناة بها أقل تداخل وأقل وزن.\n"
        "- ضع الراوتر في مكان مركزي ومفتوح.\n"
        "- تجنب القنوات التي عليها إشارات قوية من الجيران.\n"
        "- في 2.4GHz القنوات 1 أو 6 أو 11 غالبًا الأفضل.\n"
        "- في 5GHz اختر الأقل ازدحامًا.\n"
    )
}

class WifiAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.lang = self.settings.get('lang', 'en')
        self.theme = self.settings.get('theme', 'auto')
        self.title(PROGRAM_NAME)
        self.geometry("1200x700")
        self.configure(bg="#000000")
        self.networks = []
        self.filtered_networks = []
        self.after_id = None
        self.auto_refresh = False
        self.refresh_interval = tk.IntVar(value=self.settings.get('refresh_interval', 30))
        self.best_channel = "-"
        self.band_var = tk.StringVar(value=self.settings.get('band', "2.4GHz"))
        self.tooltip = None
        self.theme_colors = self.get_theme_colors(self.theme)
        self.create_widgets()
        self.filter_var.set(self.settings.get('filter', ''))
        self.signal_var.set(self.settings.get('min_signal', 0))
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def t(self, key):
        return LANGS[self.lang][key]

    def get_theme_colors(self, theme):
        # Returns a dict of color values for the theme
        if theme == 'auto':
            detected = detect_windows_theme()
            theme = detected if detected else 'dark'
        if theme == 'light':
            return {
                'bg': '#f5f6fa',
                'sidebar': '#e0e6ed',
                'text': '#232a36',
                'accent': '#e94e77',
                'button': '#e94e77',
                'button_fg': '#fff',
                'entry_bg': '#fff',
                'entry_fg': '#232a36',
                'tree_bg': '#fff',
                'tree_fg': '#232a36',
                'tree_alt': '#f9c6dc',
                'tree_sel': '#e94e77',
                'plot_bg': '#fff',
                'plot_bar': '#e94e77',
                'plot_bar_light': '#f9c6dc',
                'plot_bar_red': '#ffb3b3',
            }
        else:
            return {
                'bg': '#000000',
                'sidebar': '#111111',
                'text': '#fff',
                'accent': '#e94e77',
                'button': '#e94e77',
                'button_fg': '#fff',
                'entry_bg': '#232a36',
                'entry_fg': '#fff',
                'tree_bg': '#000000',
                'tree_fg': '#fff',
                'tree_alt': '#181818',
                'tree_sel': '#e94e77',
                'plot_bg': '#000000',
                'plot_bar': '#e94e77',
                'plot_bar_light': '#f9c6dc',
                'plot_bar_red': '#ffb3b3',
            }

    def set_theme(self, theme):
        self.theme = theme
        self.theme_colors = self.get_theme_colors(theme)
        self.save_user_settings()
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
        self.apply_filter()

    def create_widgets(self):
        c = self.theme_colors
        topbar = tk.Frame(self, bg=c['accent'], height=70)
        topbar.pack(side=tk.TOP, fill=tk.X)
        title = tk.Label(topbar, text=PROGRAM_NAME, font=("Segoe UI", 18, "bold"), bg=c['accent'], fg=c['button_fg'])
        title.place(x=20, y=10)
        subtitle = tk.Label(topbar, text=self.t('subtitle'), font=("Segoe UI", 16, "bold"), bg=c['accent'], fg=c['button_fg'])
        subtitle.place(x=20, y=38)

        main_frame = tk.Frame(self, bg=c['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        plot_frame = tk.Frame(main_frame, bg=c['bg'], width=600, height=500)
        plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20,10), pady=20)
        self.plot_frame = plot_frame
        self.plot_canvas = None

        self.best_channel_box = tk.Frame(plot_frame, bg=c['accent'], width=540, height=38, highlightbackground=c['button_fg'], highlightthickness=0, bd=0)
        self.best_channel_box.pack(side=tk.BOTTOM, pady=(10, 0))
        self.best_channel_box.pack_propagate(False)
        self.best_channel_label = tk.Label(
            self.best_channel_box,
            text="",
            font=("Segoe UI", 16, "bold"),
            bg=c['accent'],
            fg=c['button_fg'],
            padx=10,
            pady=2
        )
        self.best_channel_label.pack(expand=True, fill=tk.BOTH)
        self.update_best_channel(self.best_channel)
        # Hint below best channel
        self.best_channel_hint = tk.Label(
            plot_frame,
            text="Use this channel in your router settings for best performance.",
            font=("Segoe UI", 10, "italic"),
            bg=c['bg'],
            fg=c['accent']
        )
        self.best_channel_hint.pack(side=tk.BOTTOM, pady=(2, 0))

        # --- Buttons for API, Router Settings, and Signal Graph side by side ---
        btns_frame = tk.Frame(plot_frame, bg=c['bg'])
        btns_frame.pack(side=tk.BOTTOM, pady=(8, 0))
        self.api_btn = tk.Button(
            btns_frame,
            text="Advanced: Change Channel via API",
            font=("Segoe UI", 10, "bold"),
            bg=c['button'],
            fg=c['button_fg'],
            activebackground=c['accent'],
            activeforeground=c['button_fg'],
            relief="flat",
            bd=0,
            padx=8,
            pady=2,
            width=28,
            command=self.open_api_dialog
        )
        self.api_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.api_btn.bind('<Enter>', lambda e: self.show_tooltip(self.api_btn.winfo_rootx(), self.api_btn.winfo_rooty()+30, "For advanced users and supported routers only."))
        self.api_btn.bind('<Leave>', self.hide_tooltip)
        self.router_btn = tk.Button(
            btns_frame,
            text="Open Router Settings",
            font=("Segoe UI", 12, "bold"),
            bg=c['button'],
            fg=c['button_fg'],
            activebackground=c['accent'],
            activeforeground=c['button_fg'],
            relief="flat",
            bd=0,
            padx=12,
            pady=4,
            width=22,
            command=self.open_router_settings
        )
        self.router_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.signal_btn = tk.Button(
            btns_frame,
            text="Show Signal Strength Graph",
            font=("Segoe UI", 11, "bold"),
            bg=c['button'],
            fg=c['button_fg'],
            activebackground=c['accent'],
            activeforeground=c['button_fg'],
            relief="flat",
            bd=0,
            padx=10,
            pady=2,
            width=22,
            command=self.show_signal_graph
        )
        self.signal_btn.pack(side=tk.LEFT)

        sidebar = tk.Frame(main_frame, bg=c['sidebar'], width=420)
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10,20), pady=20)
        btn_frame = tk.Frame(sidebar, bg=c['sidebar'])
        btn_frame.pack(pady=(0,10), fill=tk.X)
        self.scan_btn = tk.Button(btn_frame, text=self.t('scan'), command=self.scan_networks, font=("Segoe UI", 11, "bold"), bg=c['button'], fg=c['button_fg'], activebackground=c['accent'], activeforeground=c['button_fg'], relief="flat", bd=0, padx=10, pady=4)
        self.scan_btn.pack(side=tk.LEFT, padx=6)
        self.export_btn = tk.Button(btn_frame, text=self.t('export'), command=self.export_results, font=("Segoe UI", 11, "bold"), bg=c['button'], fg=c['button_fg'], activebackground=c['accent'], activeforeground=c['button_fg'], relief="flat", bd=0, padx=10, pady=4)
        self.export_btn.pack(side=tk.LEFT, padx=6)
        self.auto_btn = tk.Button(btn_frame, text=self.t('auto_off'), command=self.toggle_auto_refresh, font=("Segoe UI", 11, "bold"), bg=c['entry_bg'], fg=c['button_fg'], activebackground=c['accent'], activeforeground=c['button_fg'], relief="flat", bd=0, padx=10, pady=4)
        self.auto_btn.pack(side=tk.LEFT, padx=6)
        tk.Label(btn_frame, text=self.t('interval'), bg=c['sidebar'], fg=c['text'], font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(12,2))
        interval_spin = tk.Spinbox(btn_frame, from_=10, to=120, increment=10, textvariable=self.refresh_interval, width=4, font=("Segoe UI", 10), bg=c['entry_bg'], fg=c['entry_fg'], insertbackground=c['entry_fg'], relief="solid", borderwidth=1)
        interval_spin.pack(side=tk.LEFT)

        band_frame = tk.LabelFrame(sidebar, text="Band", bg=c['sidebar'], fg=c['accent'], font=("Segoe UI", 12, "bold"), bd=2, relief="groove", labelanchor="n")
        band_frame.pack(pady=8, fill=tk.X)
        tk.Radiobutton(band_frame, text="2.4 GHz", variable=self.band_var, value="2.4GHz", bg=c['sidebar'], fg=c['text'], selectcolor=c['entry_bg'], font=("Segoe UI", 11), command=self.apply_filter).pack(anchor="w", padx=8, pady=2)
        tk.Radiobutton(band_frame, text="5 GHz", variable=self.band_var, value="5GHz", bg=c['sidebar'], fg=c['text'], selectcolor=c['entry_bg'], font=("Segoe UI", 11), command=self.apply_filter).pack(anchor="w", padx=8, pady=2)
        tk.Radiobutton(band_frame, text="All", variable=self.band_var, value="All", bg=c['sidebar'], fg=c['text'], selectcolor=c['entry_bg'], font=("Segoe UI", 11), command=self.apply_filter).pack(anchor="w", padx=8, pady=2)

        filter_frame = tk.LabelFrame(sidebar, text=self.t('filter_title'), bg=c['sidebar'], fg=c['accent'], font=("Segoe UI", 12, "bold"), bd=2, relief="groove", labelanchor="n")
        filter_frame.pack(pady=8, fill=tk.X)
        tk.Label(filter_frame, text=self.t('filter_label'), bg=c['sidebar'], fg=c['text'], font=("Segoe UI", 11)).pack(anchor="w", padx=8, pady=(6,0))
        self.filter_var = tk.StringVar()
        filter_entry = tk.Entry(filter_frame, textvariable=self.filter_var, width=18, font=("Segoe UI", 11), bg=c['entry_bg'], fg=c['entry_fg'], insertbackground=c['entry_fg'], relief="solid", borderwidth=1)
        filter_entry.pack(anchor="w", padx=8, pady=2)
        filter_entry.bind("<KeyRelease>", lambda e: self.apply_filter())
        tk.Label(filter_frame, text=self.t('signal_label'), bg=c['sidebar'], fg=c['text'], font=("Segoe UI", 11)).pack(anchor="w", padx=8, pady=(6,0))
        self.signal_var = tk.IntVar(value=0)
        signal_spin = tk.Spinbox(filter_frame, from_=0, to=100, textvariable=self.signal_var, width=8, font=("Segoe UI", 11), bg=c['entry_bg'], fg=c['entry_fg'], insertbackground=c['entry_fg'], relief="solid", borderwidth=1)
        signal_spin.pack(anchor="w", padx=8, pady=2)
        signal_spin.bind("<KeyRelease>", lambda e: self.apply_filter())
        tk.Button(filter_frame, text=self.t('apply_filter'), command=self.apply_filter, font=("Segoe UI", 11, "bold"), bg=c['entry_bg'], fg=c['button_fg'], activebackground=c['accent'], activeforeground=c['button_fg'], relief="flat", bd=0, padx=8, pady=2).pack(anchor="w", padx=8, pady=8, fill=tk.X)

        # Help button with info icon
        self.help_btn = tk.Button(
            sidebar,
            text="ℹ️ " + (self.t('help') if 'help' in LANGS[self.lang] else 'Help'),
            font=("Segoe UI", 11, "bold"),
            bg=c['button'],
            fg=c['button_fg'],
            activebackground=c['accent'],
            activeforeground=c['button_fg'],
            relief="flat",
            bd=0,
            padx=10,
            pady=4,
            command=self.show_help
        )
        self.help_btn.pack(pady=(8, 0), fill=tk.X)

        # Theme selector
        theme_frame = tk.Frame(sidebar, bg=c['sidebar'])
        theme_frame.pack(pady=(10, 0), fill=tk.X)
        tk.Label(theme_frame, text='Appearance:', bg=c['sidebar'], fg=c['accent'], font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=(8, 2))
        self.theme_var = tk.StringVar(value=self.theme)
        theme_menu = tk.OptionMenu(theme_frame, self.theme_var, 'auto', 'dark', 'light', command=self.set_theme)
        theme_menu.config(font=("Segoe UI", 11), bg=c['entry_bg'], fg=c['entry_fg'], activebackground=c['accent'], activeforeground=c['button_fg'], relief="flat")
        theme_menu.pack(side=tk.LEFT, padx=4)

        columns = self.t('columns')
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=c['tree_bg'], foreground=c['tree_fg'], fieldbackground=c['tree_bg'], rowheight=28, font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background=c['entry_bg'], foreground=c['accent'], font=("Segoe UI", 12, "bold"))
        style.map("Treeview", background=[('selected', c['tree_sel'])], foreground=[('selected', c['button_fg'])])
        self.tree = ttk.Treeview(sidebar, columns=columns, show="headings", height=16, style="Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "SSID":
                self.tree.column(col, width=140, anchor=tk.W)
            elif col == "Auth":
                self.tree.column(col, width=100, anchor=tk.CENTER)
            elif col == "Channel":
                self.tree.column(col, width=70, anchor=tk.CENTER)
            elif col == "Signal":
                self.tree.column(col, width=70, anchor=tk.CENTER)
            elif col == "BSSID":
                self.tree.column(col, width=180, anchor=tk.CENTER)
            else:
                self.tree.column(col, width=120, anchor=tk.CENTER)
        self.tree.pack(padx=0, pady=8, fill=tk.BOTH, expand=True)
        self.tree.bind('<Double-1>', self.copy_row_to_clipboard)
        self.tree.tag_configure('oddrow', background=c['tree_alt'])
        self.tree.tag_configure('evenrow', background=c['tree_bg'])

        self.status_var = tk.StringVar(value=self.t('status_ready'))
        self.status_bar = tk.Label(self, textvariable=self.status_var, anchor="w", bg=c['entry_bg'], fg=c['entry_fg'], font=("Segoe UI", 11))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Language switcher at bottom left, slightly up from the bottom, with globe icon
        self.lang_btn = tk.Menubutton(self, text="🌐 " + self.t('lang'), font=("Segoe UI", 12, "bold"), bg=c['button'], fg=c['button_fg'], relief="flat", activebackground=c['accent'], activeforeground=c['button_fg'], padx=18, pady=4)
        lang_menu = tk.Menu(self.lang_btn, tearoff=0)
        lang_menu.add_command(label="English", command=lambda: self.set_lang('en'))
        lang_menu.add_command(label="العربية", command=lambda: self.set_lang('ar'))
        self.lang_btn.config(menu=lang_menu)
        self.lang_btn.place(x=10, rely=0.94, anchor="sw")

    def set_lang(self, lang):
        self.lang = lang
        self.save_user_settings()
        self.title(PROGRAM_NAME)
        for widget in self.winfo_children():
            widget.destroy()
        self.create_widgets()
        self.apply_filter()

    def scan_networks(self):
        self.status_var.set(self.t('status_scanning'))
        self.update()
        self.tree.delete(*self.tree.get_children())
        self.networks, error = scan_wifi()
        if error:
            messagebox.showerror(self.t('error'), f"{self.t('scan_failed')}\n{error}")
            self.status_var.set(self.t('status_failed'))
            self.filtered_networks = []
            self.update_best_channel("-")
            self.clear_plot()
            return
        if not self.networks:
            self.status_var.set(self.t('status_none'))
            self.filtered_networks = []
            self.update_best_channel("-")
            self.clear_plot()
            return
        self.apply_filter()
        if self.auto_refresh:
            self.after_id = self.after(self.refresh_interval.get() * 1000, self.scan_networks)

    def apply_filter(self):
        query = self.filter_var.get().strip().lower()
        min_signal = self.signal_var.get()
        selected_band = self.band_var.get()
        filtered = []
        for net in self.networks:
            band = self.get_band(net['channel'])
            if selected_band != "All" and band != selected_band:
                continue
            if (
                query in net['ssid'].lower() or
                query in net['bssid'].lower() or
                query in net['auth'].lower()
            ) and net['signal'] >= min_signal:
                filtered.append(net)
        self.filtered_networks = filtered
        self.tree.delete(*self.tree.get_children())
        for idx, net in enumerate(filtered):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=(net['ssid'], net['auth'], net['channel'], f"{net['signal']}%", net['bssid']), tags=(tag,))
        if not filtered:
            self.status_var.set(self.t('status_no_match'))
            self.update_best_channel("-")
            self.clear_plot()
            return
        # Advanced best channel logic
        channels = [n['channel'] for n in filtered]
        band = selected_band if selected_band != "All" else self.get_band(channels[0]) if channels else "2.4GHz"
        best, overlap = best_channel_advanced(channels, filtered, band)
        if best:
            overlap_info = overlap[best]
            txt = f"{best}  |  Overlap: {overlap_info['count']}  Weighted: {overlap_info['weighted']:.2f}"
            self.update_best_channel(txt)
        else:
            self.update_best_channel("-")
        self.status_var.set(self.t('status_showing').format(n=len(filtered)))
        self.draw_plot(overlap if filtered else None)
        self.save_user_settings()

    def get_band(self, channel):
        if 1 <= channel <= 14:
            return "2.4GHz"
        elif (36 <= channel <= 64) or (100 <= channel <= 144) or (149 <= channel <= 165):
            return "5GHz"
        else:
            return "Other"

    def recommend_band_channel(self, networks, band):
        band_channels = [n['channel'] for n in networks if self.get_band(n['channel']) == band or band == "All"]
        if not band_channels:
            return None
        usage = Counter(band_channels)
        best = min(usage, key=lambda ch: usage[ch])
        return best

    def update_best_channel(self, value):
        if value == "-":
            txt = f"{self.t('subtitle')}: -"
        else:
            txt = value.replace(f"{self.t('subtitle')}: ", "")
            txt = f"{self.t('subtitle')}: {txt}"
        self.best_channel_label.config(text=txt)

    def export_results(self):
        if not self.filtered_networks:
            messagebox.showinfo(self.t('info'), self.t('no_export'))
            return
        filetypes = [(self.t('export_csv'), "*.csv"), (self.t('export_txt'), "*.txt")]
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=filetypes, title=self.t('export_title'))
        if not file:
            return
        try:
            if file.endswith(".csv"):
                with open(file, "w", newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.t('columns'))
                    for net in self.filtered_networks:
                        writer.writerow([
                            net['ssid'], net['auth'], net['channel'], f"{net['signal']}%", net['bssid']
                        ])
            else:
                with open(file, "w", encoding='utf-8') as f:
                    f.write("\t".join(self.t('columns')) + "\n")
                    for net in self.filtered_networks:
                        f.write(f"{net['ssid']}\t{net['auth']}\t{net['channel']}\t{net['signal']}%\t{net['bssid']}\n")
            messagebox.showinfo(self.t('export_title'), self.t('export_success'))
        except Exception as e:
            messagebox.showerror(self.t('export_title'), f"{self.t('export_fail')} {e}")

    def draw_plot(self, overlap=None):
        if not self.filtered_networks:
            self.clear_plot()
            return
        selected_band = self.band_var.get()
        channels = [n['channel'] for n in self.filtered_networks if selected_band == "All" or self.get_band(n['channel']) == selected_band]
        if not channels:
            self.clear_plot()
            return
        usage = Counter(channels)
        chs = sorted(usage.keys())
        counts = [usage[ch] for ch in chs]
        self.clear_plot()
        width, height = 540, 320
        margin = 40
        bar_width = max(18, (width - 2*margin) // max(1, len(chs)))
        max_count = max(counts)
        max_val = max(counts)
        # For advanced: get max weighted overlap
        max_weighted = 0
        if overlap:
            max_weighted = max(overlap[ch]['weighted'] for ch in chs)
        canvas = tk.Canvas(self.plot_frame, width=width, height=height, bg=self.theme_colors['plot_bg'], highlightthickness=0)
        canvas.create_line(margin, height-margin, width-margin, height-margin, fill="#fff", width=2)
        canvas.create_line(margin, margin, margin, height-margin, fill="#fff", width=2)
        self.bar_rects = []
        for i, ch in enumerate(chs):
            x0 = margin + i*bar_width + 8
            x1 = x0 + bar_width - 12
            y0 = height - margin
            y1 = y0 - (counts[i]/max_count)*(height-2*margin-20)
            # Advanced: use weighted overlap for color
            if overlap:
                w = overlap[ch]['weighted']
                if w == max_weighted and max_weighted > 0.5:
                    bar_color = self.theme_colors['plot_bar_red']  # semi-transparent red
                    outline_color = self.theme_colors['accent']
                else:
                    bar_color = self.theme_colors['plot_bar_light']  # more transparent pink
                    outline_color = self.theme_colors['accent']
            else:
                if counts[i] == max_val and max_val > 1:
                    bar_color = self.theme_colors['plot_bar_red']
                    outline_color = self.theme_colors['accent']
                else:
                    bar_color = self.theme_colors['plot_bar_light']
                    outline_color = self.theme_colors['accent']
            rect = canvas.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline=outline_color, width=2)
            canvas.create_text((x0+x1)//2, height-margin+15, text=str(ch), fill="#fff", font=("Segoe UI", 11, "bold"))
            canvas.create_text((x0+x1)//2, y1-12, text=str(counts[i]), fill="#fff", font=("Segoe UI", 10))
            self.bar_rects.append((rect, ch, counts[i]))
        canvas.create_text(width//2, height-8, text=self.t('channel'), fill="#fff", font=("Segoe UI", 12, "bold"))
        canvas.create_text(18, height//2, text=self.t('networks'), fill="#fff", font=("Segoe UI", 12, "bold"), angle=90)
        canvas.create_text(width//2, 18, text=self.t('plot_title'), fill="#fff", font=("Segoe UI", 13, "bold"))
        canvas.pack(fill=tk.BOTH, expand=True)
        self.plot_canvas = canvas
        canvas.bind('<Motion>', self.on_bar_hover)
        canvas.bind('<Leave>', self.hide_tooltip)

    def on_bar_hover(self, event):
        if not hasattr(self, 'bar_rects') or not self.bar_rects:
            return
        found = False
        for rect, ch, count in self.bar_rects:
            coords = self.plot_canvas.coords(rect)
            if coords and coords[0] <= event.x <= coords[2] and coords[3] <= event.y <= coords[1]:
                self.show_tooltip(event.x_root, event.y_root, f"{self.t('channel')}: {ch}\n{self.t('networks')}: {count}")
                found = True
                break
        if not found:
            self.hide_tooltip(None)

    def show_tooltip(self, x, y, text):
        if self.tooltip:
            self.tooltip.destroy()
        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+10}+{y+10}")
        label = tk.Label(self.tooltip, text=text, bg=self.theme_colors['bg'], fg="#fff", font=("Segoe UI", 10), padx=8, pady=4, relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

    def clear_plot(self):
        if self.plot_canvas:
            self.plot_canvas.destroy()
            self.plot_canvas = None
        self.bar_rects = []
        self.hide_tooltip(None)

    def copy_row_to_clipboard(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            vals = self.tree.item(item)['values']
            self.clipboard_clear()
            self.clipboard_append('\t'.join(str(v) for v in vals))
            self.status_var.set(self.t('info') + ': Copied to clipboard.')

    def toggle_auto_refresh(self):
        self.auto_refresh = not self.auto_refresh
        self.save_user_settings()
        if self.auto_refresh:
            self.auto_btn.config(text=self.t('auto_on'), bg=self.theme_colors['button'])
            self.scan_networks()
        else:
            self.auto_btn.config(text=self.t('auto_off'), bg=self.theme_colors['entry_bg'])
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None

    def open_router_settings(self):
        # Try 192.168.1.1, fallback to 192.168.0.1
        try:
            webbrowser.open('http://192.168.1.1')
        except Exception:
            webbrowser.open('http://192.168.0.1')
        # Show instructions
        best_channel_text = self.best_channel_label.cget('text')
        msg = (
            f"{best_channel_text}\n\n"
            "To change your Wi-Fi channel:\n"
            "1. Log in to your router settings in your browser.\n"
            "2. Find the Wi-Fi/WLAN settings.\n"
            "3. Change the channel to the recommended one above.\n"
            "4. Save and reboot if needed.\n"
            "(If you don't know the login, check your router label or manual.)"
        )
        messagebox.showinfo("Router Channel Change", msg)

    def open_api_dialog(self):
        # نافذة أكبر وتوسيط المحتوى
        win = tk.Toplevel(self)
        win.title("Advanced: Change Channel via API")
        win.geometry("420x340")
        win.configure(bg=self.theme_colors['bg'])
        # إطار مركزي
        center = tk.Frame(win, bg=self.theme_colors['bg'])
        center.pack(expand=True, fill=tk.BOTH)
        # الحقول
        def add_row(label, var, show=None):
            row = tk.Frame(center, bg=self.theme_colors['bg'])
            row.pack(pady=7, padx=10, fill=tk.X)
            tk.Label(row, text=label, bg=self.theme_colors['bg'], fg="#fff", font=("Segoe UI", 12)).pack(side=tk.LEFT, padx=(0,8))
            entry = tk.Entry(row, textvariable=var, font=("Segoe UI", 12), bg="#fff", show=show)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            return entry
        ip_var = tk.StringVar(value="192.168.1.1")
        user_var = tk.StringVar(value="admin")
        pass_var = tk.StringVar()
        ch_var = tk.StringVar()
        add_row("Router IP:", ip_var)
        add_row("Username:", user_var)
        add_row("Password:", pass_var, show="*")
        add_row("Channel:", ch_var)
        # زر التغيير
        def not_implemented():
            messagebox.showinfo("Not Implemented", "This feature is only available for supported routers with API access.\nPlease refer to your router documentation or contact support.")
        btn_frame = tk.Frame(center, bg=self.theme_colors['bg'])
        btn_frame.pack(pady=18)
        tk.Button(
            btn_frame, text="Change Channel", command=not_implemented,
            font=("Segoe UI", 13, "bold"), bg=self.theme_colors['button'], fg="#fff",
            relief="flat", width=22, height=2
        ).pack()

    def show_help(self):
        win = tk.Toplevel(self)
        win.title(PROGRAM_NAME + ' - ' + (self.t('help') if 'help' in LANGS[self.lang] else 'Help'))
        win.geometry('540x480')
        win.configure(bg=self.theme_colors['bg'])
        text = HELP_TEXT.get(self.lang, HELP_TEXT['en'])
        label = tk.Label(win, text=text, bg=self.theme_colors['bg'], fg="#fff", font=("Segoe UI", 12), justify="left", wraplength=500, anchor="nw")
        label.pack(padx=18, pady=18, fill=tk.BOTH, expand=True)
        tk.Button(win, text=self.t('ok') if 'ok' in LANGS[self.lang] else 'OK', command=win.destroy, font=("Segoe UI", 11, "bold"), bg=self.theme_colors['button'], fg="#fff", relief="flat").pack(pady=10)

    def save_user_settings(self):
        settings = {
            'lang': self.lang,
            'band': self.band_var.get(),
            'filter': self.filter_var.get(),
            'min_signal': self.signal_var.get(),
            'refresh_interval': self.refresh_interval.get(),
            'theme': self.theme
        }
        save_settings(settings)

    def on_close(self):
        self.save_user_settings()
        self.destroy()

    def show_signal_graph(self):
        if not self.filtered_networks:
            messagebox.showinfo(self.t('info'), 'No networks to show.')
            return
        win = tk.Toplevel(self)
        win.title('Signal Strength Graph')
        width, height = 900, 420
        margin = 60
        bar_width = max(36, (width-2*margin)//max(1,len(self.filtered_networks)))
        networks = self.filtered_networks
        n = len(networks)
        canvas = tk.Canvas(win, width=width, height=height, bg=self.theme_colors['bg'], highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        # X-axis and Y-axis
        canvas.create_line(margin, height-margin, width-margin, height-margin, fill="#fff", width=2)
        canvas.create_line(margin, margin, margin, height-margin, fill="#fff", width=2)
        # Bars
        max_signal = max(nw['signal'] for nw in networks)
        for i, net in enumerate(networks):
            x0 = margin + i*bar_width + 12
            x1 = x0 + bar_width - 16
            y0 = height - margin
            y1 = y0 - (net['signal']/100)*(height-2*margin-20)
            # Strongest signal: saturated pink, others lighter
            if net['signal'] == max_signal:
                bar_color = self.theme_colors['plot_bar']
            elif net['signal'] > 60:
                bar_color = self.theme_colors['plot_bar_light']
            else:
                bar_color = self.theme_colors['plot_bar_light']
            outline_color = self.theme_colors['plot_bar']
            rect = canvas.create_rectangle(x0, y0, x1, y1, fill=bar_color, outline=outline_color, width=3)
            label = net['ssid'] if net['ssid'] else net['bssid']
            # اسم الشبكة بزاوية 30 درجة
            canvas.create_text((x0+x1)//2, height-margin+28, text=label[:14], fill="#fff", font=("Segoe UI", 12, "bold"), angle=30)
            # نسبة الإشارة فوق العمود
            canvas.create_text((x0+x1)//2, y1-16, text=f"{net['signal']}%", fill="#fff", font=("Segoe UI", 12, "bold"))
            # Tooltip
            def make_on_hover(lbl, sig):
                return lambda e, l=lbl, s=sig: self.show_tooltip(e.x_root, e.y_root, f"{l}\nSignal: {s}%")
            canvas.tag_bind(rect, '<Enter>', make_on_hover(label, net['signal']))
            canvas.tag_bind(rect, '<Leave>', self.hide_tooltip)
        # Axis labels
        canvas.create_text(width//2, height-18, text='Network', fill="#fff", font=("Segoe UI", 15, "bold"))
        canvas.create_text(28, height//2, text='Signal %', fill="#fff", font=("Segoe UI", 15, "bold"), angle=90)
        canvas.create_text(width//2, 32, text='Signal Strength of Networks', fill="#fff", font=("Segoe UI", 20, "bold"))

if __name__ == "__main__":
    app = WifiAnalyzerApp()
    app.mainloop() 