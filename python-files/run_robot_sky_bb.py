import subprocess
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk
import os
import datetime
import sys

sys.setrecursionlimit(10000)

ROBOT_CONFIGS = [
    {
        "name": "SKY_BB_01",
        "excel_path": r"D:\Robot\Robot_SKY_BB\Files\NEW.xlsx",
        "default_log_dir": r"D:\Robot\Robot_SKY_BB\Log",
        "robot_file": r"Script_New_Registration_1st.robot",
        "working_dir": r"D:\Robot\Robot_SKY_BB\Testsuites\NEW",
    },
    {
        "name": "SKY_BB_02",
        "excel_path": r"D:\Robot\Run\SKY_BB_02\Files\NEW.xlsx",
        "default_log_dir": r"D:/Robot/Run/Log",
        "robot_file": r"Script_New_Registration_1st.robot",
        "working_dir": r"D:\Robot\Run\SKY_BB_02\Testsuites\NEW",
    },
    {
        "name": "SKY_BB_03",
        "excel_path": r"D:\Robot\Run\SKY_BB_03\Files\NEW.xlsx",
        "default_log_dir": r"D:/Robot/Run/Log",
        "robot_file": r"Script_New_Registration_1st.robot",
        "working_dir": r"D:\Robot\Run\SKY_BB_03\Testsuites\NEW",
    },
]

# Elegant compact color scheme
COLORS = {
    'primary': '#6366f1',           # Indigo
    'primary_light': '#8b5cf6',     # Purple
    'success': '#10b981',           # Emerald
    'warning': '#f59e0b',           # Amber
    'danger': '#ef4444',            # Red
    'secondary': '#06b6d4',         # Cyan
    'background': '#f8fafc',        # Light gray
    'card_bg': '#ffffff',           # White
    'border': '#e2e8f0',            # Light border
    'text_dark': '#1e293b',         # Dark text
    'text_light': '#64748b',        # Light text
    'text_white': '#ffffff',        # White text
    'shadow': 'rgba(0, 0, 0, 0.1)', # Shadow
}

def is_excel_open(excel_path):
    try:
        temp_name = excel_path + ".locktest"
        os.rename(excel_path, temp_name)
        os.rename(temp_name, excel_path)
        return False
    except PermissionError:
        return True
    except Exception:
        return False

def open_excel(excel_path):
    try:
        os.startfile(excel_path)
    except Exception as e:
        messagebox.showerror("Error", f"Cannot open Excel file:\n{e}")

def run_robot(config, log_dir_var, status_indicator=None):
    if is_excel_open(config["excel_path"]):
        messagebox.showwarning("คำเตือน", "กรุณาปิดไฟล์ Excel (NEW.xlsx) ก่อนรัน Robot Framework")
        return

    log_dir = log_dir_var.get()
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    if status_indicator:
        status_indicator.config(fg=COLORS['danger'])  # 🔴

    now = datetime.datetime.now()
    date = now.strftime("%m_%d_%Y")
    time = now.strftime("%H%M%S")
    datetime_str = f"{date}_{time}"

    output_dir = os.path.join(log_dir, datetime_str)
    os.makedirs(output_dir, exist_ok=True)

    output_xml = os.path.join(output_dir, f"output_{datetime_str}.xml")
    log_html = os.path.join(output_dir, f"log_{datetime_str}.html")
    report_html = os.path.join(output_dir, f"report_{datetime_str}.html")

    robot_cmd = (
        f'robot -d "{output_dir}" '
        f'--output "{output_xml}" '
        f'--log "{log_html}" '
        f'--report "{report_html}" '
        f'{config["robot_file"]}'
    )
    
    terminal_cmd = f'start cmd /K "title {config["name"]} && cd /d {config["working_dir"]} && {robot_cmd}"'
    os.system(terminal_cmd)

    if status_indicator:
        status_indicator.config(fg=COLORS['success'])  # ✅


def browse_log_dir(default_dir, log_dir_var):
    folder = filedialog.askdirectory(initialdir=default_dir)
    if folder:
        log_dir_var.set(folder)

def create_modern_button(parent, text, command, bg_color, icon="", width=8):
    """Create modern flat button with hover effects"""
    
    btn = tk.Button(parent,
                   text=f"{icon} {text}",
                   command=command,
                   bg=bg_color,
                   fg=COLORS['text_white'],
                   font=('Segoe UI', 9, 'bold'),
                   relief='flat',
                   borderwidth=0,
                   padx=8,
                   pady=6,
                   width=width,
                   cursor='hand2')
    
    # Calculate darker color for hover
    def darken_color(color):
        # Simple color darkening
        if color == COLORS['primary']:
            return '#4f46e5'
        elif color == COLORS['success']:
            return '#059669'
        elif color == COLORS['secondary']:
            return '#0891b2'
        elif color == COLORS['warning']:
            return '#d97706'
        return color
    
    hover_color = darken_color(bg_color)
    
    def on_enter(e):
        btn.config(bg=hover_color)
    
    def on_leave(e):
        btn.config(bg=bg_color)
    
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    
    return btn

def create_compact_card(parent, config, idx):
    """Create compact card design"""
    
    # Main card frame
    card = tk.Frame(parent, bg=COLORS['card_bg'], relief='solid', borderwidth=1, padx=12, pady=10)
    card.pack(fill='x', padx=8, pady=4)
    
    # Header row
    header_frame = tk.Frame(card, bg=COLORS['card_bg'])
    header_frame.pack(fill='x', pady=(0, 8))
    
    # Robot name and number
    name_label = tk.Label(header_frame,
                         text=f"🤖 {config['name']}",
                         font=('Segoe UI', 11, 'bold'),
                         bg=COLORS['card_bg'],
                         fg=COLORS['primary'])
    name_label.pack(side='left')
    
    # Status indicator
    status_indicator = tk.Label(header_frame,
                              text="●",
                              font=('Arial', 12),
                              bg=COLORS['card_bg'],
                              fg=COLORS['success'])
    status_indicator.pack(side='right')
    
    # Log directory row
    log_frame = tk.Frame(card, bg=COLORS['card_bg'])
    log_frame.pack(fill='x', pady=(0, 8))
    
    log_label = tk.Label(log_frame,
                        text="Log:",
                        font=('Segoe UI', 9),
                        bg=COLORS['card_bg'],
                        fg=COLORS['text_light'])
    log_label.pack(side='left')
    
    log_dir_var = tk.StringVar(value=config["default_log_dir"])
    
    log_entry = tk.Entry(log_frame,
                        textvariable=log_dir_var,
                        font=('Segoe UI', 8),
                        relief='solid',
                        borderwidth=1,
                        bg='#f8fafc',
                        width=35)
    log_entry.pack(side='left', padx=(5, 5), fill='x', expand=True)
    
    # Browse button - compact
    browse_btn = tk.Button(log_frame,
                          text="📂",
                          command=lambda: browse_log_dir(config["default_log_dir"], log_dir_var),
                          bg=COLORS['secondary'],
                          fg=COLORS['text_white'],
                          font=('Segoe UI', 8),
                          relief='flat',
                          padx=6,
                          pady=4,
                          cursor='hand2')
    browse_btn.pack(side='right')
    
    # Action buttons row
    action_frame = tk.Frame(card, bg=COLORS['card_bg'])
    action_frame.pack(fill='x')
    
    # Excel button
    excel_btn = create_modern_button(action_frame,
                                   "Excel",
                                   lambda: open_excel(config["excel_path"]),
                                   COLORS['success'],
                                   "📊",
                                   width=6)
    excel_btn.pack(side='left', padx=(0, 4))
    
    # Run button - prominent
    run_btn = create_modern_button(action_frame,
                                "RUN",
                                lambda: run_robot(config, log_dir_var, status_indicator),
                                COLORS['primary'],
                                "▶️",
                                width=8)
    run_btn.pack(side='right')
    
    return log_dir_var

# Create compact main window
root = tk.Tk()
root.title("🤖 Robot Manager")
root.geometry("560x500")
root.configure(bg=COLORS['background'])
root.resizable(False, False)  # Fixed size for compact design

# Compact header
header = tk.Frame(root, bg=COLORS['primary'], height=60)
header.pack(fill='x')
header.pack_propagate(False)

title_label = tk.Label(header,
                      text="🤖 Robot Framework Manager",
                      font=('Segoe UI', 14, 'bold'),
                      bg=COLORS['primary'],
                      fg=COLORS['text_white'])
title_label.pack(pady=18)

# Status bar
# status_frame = tk.Frame(root, bg='#f0f9ff', height=32)
# status_frame.pack(fill='x', padx=8, pady=(8, 0))
# status_frame.pack_propagate(False)

# status_label = tk.Label(status_frame,
#                        text="✨ พร้อมใช้งาน",
#                        font=('Segoe UI', 9),
#                        bg='#f0f9ff',
#                        fg=COLORS['primary'])
# status_label.pack(pady=6)

# Main content area
main_frame = tk.Frame(root, bg=COLORS['background'])
main_frame.pack(fill='both', expand=True, padx=8, pady=8)

# Create compact robot cards
log_dir_vars = []
for idx, config in enumerate(ROBOT_CONFIGS):
    log_dir_var = create_compact_card(main_frame, config, idx)
    log_dir_vars.append(log_dir_var)

# Compact footer
footer = tk.Frame(root, bg=COLORS['text_dark'], height=28)
footer.pack(fill='x', side='bottom')
footer.pack_propagate(False)

footer_label = tk.Label(footer,
                       text="© 2024 Robot Manager Pro",
                       font=('Segoe UI', 8),
                       bg=COLORS['text_dark'],
                       fg='#94a3b8')
footer_label.pack(pady=6)

# Simple title animation
def animate_title():
    current = title_label.cget('text')
    if '🤖' in current:
        title_label.config(text="🚀 Robot Framework Manager")
    else:
        title_label.config(text="🤖 Robot Framework Manager")
    root.after(5000, animate_title)

# Add subtle hover effects to cards
def add_card_hover(card):
    original_bg = card.cget('bg')
    
    def on_enter(e):
        card.config(bg='#f8fafc')
    
    def on_leave(e):
        card.config(bg=original_bg)
    
    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)
    
    # Apply to all child widgets
    for child in card.winfo_children():
        child.bind("<Enter>", on_enter)
        child.bind("<Leave>", on_leave)

# Apply hover effects to all cards
for widget in main_frame.winfo_children():
    if isinstance(widget, tk.Frame):
        add_card_hover(widget)

# Start animations
root.after(3000, animate_title)

# Center window
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

# Prevent window from being resized to maintain compact design
root.minsize(520, 500)
root.maxsize(520, 500)

root.mainloop()