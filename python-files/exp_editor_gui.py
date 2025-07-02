import yaml
import os
import sys
import logging
from tkinter import ttk, messagebox, Tk, Frame, Listbox, Scrollbar, Label, Entry, Button, Radiobutton, StringVar, Menu, filedialog, END, SINGLE, Toplevel
import numpy as np
import hashlib

# --- Setup Logging ---
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'editor_log.txt')
logging.basicConfig(filename=log_file, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

USERNAME_HASH = "b23fcb8820e567d1143f4a15cfeaf04ba660bafd89eeb496e99ffd8bd1079f71"  # hash ของ 'testuser'
PASSWORD_HASH = "13d249f2cb4127b40cfa757866850278793f814ded3c587fe5889e889a7a9f6c"  # hash ของ 'testpass'

def check_login_hash(input_user, input_password):
    user_hash = hashlib.sha256(input_user.encode()).hexdigest()
    pass_hash = hashlib.sha256(input_password.encode()).hexdigest()
    return user_hash == USERNAME_HASH and pass_hash == PASSWORD_HASH

def show_login_dialog():
    login_ok = False
    login = Tk()
    login.title("LogOn")
    login.geometry("260x120")
    login.resizable(False, False)
    login.configure(bg="#232323")

    frame = Frame(login, bg="#232323")
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Label ID
    id_label = Label(frame, text="ID", font=("Segoe UI", 10, "bold"), fg="#e0e0e0", bg="#232323")
    id_label.grid(row=0, column=0, sticky="e", pady=(2, 2), padx=(0, 6))
    user_entry = Entry(frame, font=("Segoe UI", 10), relief="flat", bg="#333333", fg="#e0e0e0", insertbackground="#e0e0e0", highlightthickness=1, highlightbackground="#444444", highlightcolor="#888888")
    user_entry.grid(row=0, column=1, pady=(2, 2), ipadx=18, ipady=2)
    user_entry.focus()

    # Label Password
    pass_label = Label(frame, text="Password", font=("Segoe UI", 10, "bold"), fg="#e0e0e0", bg="#232323")
    pass_label.grid(row=1, column=0, sticky="e", pady=(2, 2), padx=(0, 6))
    pass_entry = Entry(frame, show="*", font=("Segoe UI", 10), relief="flat", bg="#333333", fg="#e0e0e0", insertbackground="#e0e0e0", highlightthickness=1, highlightbackground="#444444", highlightcolor="#888888")
    pass_entry.grid(row=1, column=1, pady=(2, 2), ipadx=18, ipady=2)

    def check_and_login():
        nonlocal login_ok
        user = user_entry.get()
        pw = pass_entry.get()
        if check_login_hash(user, pw):
            login_ok = True
            login.destroy()
        else:
            messagebox.showerror("Login Failed", "ID หรือ Password ไม่ถูกต้อง")

    # ปุ่ม login อยู่ล่างสุด (ใช้ tk.Button แทน ttk.Button)
    login_btn = Button(
        frame, text="login",
        font=("Segoe UI", 10),
        bg="#333333", fg="#ffffff",
        activebackground="#444444", activeforeground="#ffffff",
        relief="flat", borderwidth=0, highlightthickness=0,
        command=check_and_login
    )
    login_btn.grid(row=2, column=0, columnspan=2, pady=(10, 2), ipadx=10, ipady=2)

    login.bind('<Return>', lambda e: check_and_login())
    login.protocol("WM_DELETE_WINDOW", login.destroy)
    login.mainloop()
    return login_ok

class Tooltip:
    def __init__(self, widget):
        self.widget = widget
        self.tip_window = None
        logging.info("Tooltip helper initialized.")

    def showtip(self, text):
        self.text = text
        if self.tip_window or not self.text:
            return
        try:
            x, y, _, _ = self.widget.bbox("insert")
            x = x + self.widget.winfo_rootx() + 25
            y = y + self.widget.winfo_rooty() + 20
            self.tip_window = tw = Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry(f" +{x}+{y}")
            label = Label(tw, text=self.text, justify='left',
                          background="#ffffe0", relief='solid', borderwidth=1,
                          font=("Segoe UI", "10", "normal"))
            label.pack(ipadx=1)
        except Exception as e:
            logging.error(f"Failed to display tooltip: {e}", exc_info=True)

    def hidetip(self):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

def create_tooltip(widget, text_generator):
    tooltip = Tooltip(widget)
    last_index = -1

    def enter(event):
        nonlocal last_index
        try:
            index = widget.nearest(event.y)
            if index != last_index:
                last_index = index
                text = text_generator(index)
                if text:
                    tooltip.showtip(text)
                else:
                    tooltip.hidetip()
        except Exception as e:
            logging.error(f"Error in tooltip enter event: {e}", exc_info=True)

    def leave(event):
        nonlocal last_index
        last_index = -1
        tooltip.hidetip()

    widget.bind('<Motion>', enter)
    widget.bind('<Leave>', leave)

class ExpEditorApp:
    def __init__(self, root):
        logging.info("--- Initializing ExpEditorApp ---")
        self.root = root
        self.root.geometry("850x650")
        self.current_file = os.path.join(os.getcwd(), 'job_exp.yml')
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'editor_config.yml')
        logging.info(f"Set current file to: {self.current_file}")
        logging.info(f"Set config file to: {self.config_file}")
        
        self.data = None
        self.unsaved_changes = False
        self.selected_group_index = None
        self.selected_exp_type = StringVar(value="BaseExp")
        self.is_dark_mode = True

        self.style = ttk.Style(root)
        self.setup_themes()
        
        self.create_menu()

        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.left_frame = ttk.Frame(self.main_frame, width=280)
        self.left_frame.pack(side="left", fill="y", padx=(0, 10))
        self.left_frame.pack_propagate(False)

        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side="right", fill="both", expand=True)

        self.group_label = ttk.Label(self.left_frame, text="Job Groups", font=("Segoe UI", 12, "bold"))
        self.group_label.pack(pady=(0, 5))
        
        list_frame = ttk.Frame(self.left_frame)
        list_frame.pack(fill="both", expand=True)
        self.job_group_list = Listbox(list_frame, selectmode=SINGLE, exportselection=False, font=("Segoe UI", 10))
        self.job_group_list.pack(side="left", fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.job_group_list.yview)
        scrollbar.pack(side="right", fill="y")
        self.job_group_list.config(yscrollcommand=scrollbar.set)
        
        self.job_group_list.bind('<<ListboxSelect>>', self.on_group_select)
        create_tooltip(self.job_group_list, self.get_tooltip_text)

        controls_frame = ttk.Frame(self.right_frame)
        controls_frame.pack(fill="x", pady=(0, 10))

        self.exp_type_label = ttk.Label(controls_frame, text="EXP Type:", font=("Segoe UI", 10, "bold"))
        self.exp_type_label.pack(side="left", padx=(0, 10))
        self.base_exp_radio = ttk.Radiobutton(controls_frame, text="Base EXP", variable=self.selected_exp_type, value="BaseExp", command=self.on_exp_type_change)
        self.base_exp_radio.pack(side="left")
        self.job_exp_radio = ttk.Radiobutton(controls_frame, text="Job EXP", variable=self.selected_exp_type, value="JobExp", command=self.on_exp_type_change)
        self.job_exp_radio.pack(side="left")

        tree_frame = ttk.Frame(self.right_frame)
        tree_frame.pack(fill="both", expand=True)
        
        # Add Auto Calculate EXP and Jump to Level buttons above the table
        jump_frame = ttk.Frame(self.right_frame)
        jump_frame.pack(fill="x", pady=(0, 5))
        auto_calc_btn = ttk.Button(jump_frame, text="Auto Calculate EXP", command=self.auto_calculate_exp)
        auto_calc_btn.pack(side="right", padx=5)
        jump_btn = ttk.Button(jump_frame, text="Jump to Level", command=self.jump_to_level, style="Accent.TButton")
        jump_btn.pack(side="right", padx=5)

        # --- ย้าย bottom_frame มาอยู่ใน jump_frame เพื่อให้ปุ่มเรียงแถวเดียวกัน ---
        bottom_frame = ttk.Frame(jump_frame)
        bottom_frame.pack(side="left", padx=(0, 10), pady=2)

        self.add_remove_count_var = StringVar(value="1")
        count_entry = ttk.Entry(bottom_frame, width=4, textvariable=self.add_remove_count_var, justify='center')
        count_entry.pack(side="left", padx=(5, 2), pady=2)

        add_btn = ttk.Button(bottom_frame, text="+", width=3, command=self.add_exp_rows)
        add_btn.pack(side="left", padx=2, pady=2)

        remove_btn = ttk.Button(bottom_frame, text="-", width=3, command=self.remove_exp_rows)
        remove_btn.pack(side="left", padx=2, pady=2)

        maxexp_btn = ttk.Button(bottom_frame, text="Max EXP", width=10, command=self.set_max_exp_button)
        maxexp_btn.pack(side="left", padx=(20, 2), pady=2)

        # ใช้แค่ 2 คอลัมน์: Level | EXP
        self.tree = ttk.Treeview(tree_frame, columns=('Level', 'EXP'), show='headings')
        self.tree.heading('Level', text='Level', anchor='center')
        self.tree.heading('EXP', text='EXP', anchor='center')
        self.tree.column('Level', width=120, anchor='center', stretch=False, minwidth=80)
        self.tree.column('EXP', width=180, minwidth=80, anchor='w', stretch=True)
        self.tree.pack(side='left', fill='both', expand=True)

        # Add double-click event binding for editing
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Return>', self.on_double_click)  # Allow editing with Enter key too
        
        # Create an Entry widget for editing
        self.edit_entry = ttk.Entry(self.tree, justify='left')
        self.edit_entry.bind('<Return>', self.on_edit_complete)
        self.edit_entry.bind('<Escape>', lambda e: self.edit_entry.place_forget())
        self.edit_entry.bind('<FocusOut>', self.on_edit_complete)
        
        # Track the item being edited
        self.editing_item = None
        self.editing_column = None

        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        tree_scrollbar.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=tree_scrollbar.set)
        self.tree.bind('<<TreeviewSelect>>', self.on_level_select)

        self.load_config()

        self.load_exp_data(self.current_file)
        self.apply_theme()
        
        # Keyboard shortcuts
        self.root.bind('<Control-j>', lambda e: self.jump_to_level())
        self.root.bind('<Control-J>', lambda e: self.jump_to_level())
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        logging.info("--- App initialization complete ---")

    def get_tooltip_text(self, index):
        try:
            if self.data and 'Body' in self.data and 0 <= index < len(self.data['Body']):
                group = self.data['Body'][index]
                jobs = [job for job, enabled in group.get('Jobs', {}).items() if enabled]
                return "\n".join(jobs)
        except Exception as e:
            logging.error(f"Error generating tooltip text for index {index}: {e}", exc_info=True)
        return ""

    def setup_themes(self):
        self.light_theme = {
            "bg": "#F8F9FB",              # เบากว่าเดิม
            "fg": "#222222",              # ดำอ่อน อ่านง่าย
            "list_bg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "accent_bg": "#2196F3",       # ฟ้าเด่น
            "accent_fg": "#FFFFFF",
            "tree_bg": "#FAFAFA",         # ขาวอมเทา
            "tree_fg": "#222222",
            "tree_heading_bg": "#E3E6EA", # เทาอ่อน
            "tree_heading_fg": "#222222",
            "selected_bg": "#B3D7FF",     # ฟ้าอ่อน
            "grid_color": "#B0B0B0"        # เทาอ่อน
        }
        self.dark_theme = {
            "bg": "#2E2E2E", "fg": "#E0E0E0", "list_bg": "#3C3C3C", "entry_bg": "#3C3C3C",
            "accent_bg": "#5DB85D", "accent_fg": "#000000", "tree_bg": "#3C3C3C", "tree_fg": "#E0E0E0",
            "tree_heading_bg": "#4C4C4C", "tree_heading_fg": "#E0E0E0", "selected_bg": "#5C5C5C",
            "grid_color": "#555555"  # Color for grid lines
        }
        self.style.theme_use('clam')

    def apply_theme(self):
        theme = self.dark_theme if self.is_dark_mode else self.light_theme
        
        self.root.config(bg=theme["bg"])
        self.style.configure('TFrame', background=theme["bg"])
        self.style.configure('TLabel', background=theme["bg"], foreground=theme["fg"], font=("Segoe UI", 10))
        self.style.configure('TRadiobutton', background=theme["bg"], foreground=theme["fg"], font=("Segoe UI", 10))
        self.style.configure('TButton', font=("Segoe UI", 10))
        self.style.configure('Accent.TButton', foreground=theme["accent_fg"], background=theme["accent_bg"], font=("Segoe UI", 10, 'bold'))
        self.style.map('Accent.TButton', background=[('active', theme["accent_bg"])])

        self.group_label.config(background=theme["bg"], foreground=theme["fg"])
        self.job_group_list.config(bg=theme["list_bg"], fg=theme["fg"], selectbackground=theme["selected_bg"])
        
        # Treeview: ชัดเจนแบบตาราง
        self.style.configure('Treeview', 
                            background=theme["tree_bg"], 
                            foreground=theme["tree_fg"], 
                            fieldbackground=theme["tree_bg"],
                            bordercolor=theme["grid_color"],
                            borderwidth=1,
                            relief='solid',
                            rowheight=25,
                            font=("Segoe UI", 10),
                            padding=[6, 0])

        # Row striping
        self.tree.tag_configure('oddrow', background=theme["tree_bg"])
        self.tree.tag_configure('evenrow', background=self.adjust_color(theme["tree_bg"], 12))

        # Header
        self.style.configure('Treeview.Heading', 
                            background=theme["tree_heading_bg"], 
                            foreground=theme["tree_heading_fg"], 
                            font=("Segoe UI", 11, 'bold'),
                            borderwidth=2,
                            relief='raised',
                            padding=[0, 4])

        self.style.configure('TEntry', fieldbackground=theme["entry_bg"], foreground=theme["fg"], insertcolor=theme["fg"])

        # Custom Treeview style for vertical separator
        self.style.layout('Custom.Treeview', [
            ('Treeview.field', {'sticky': 'nswe', 'children': [
                ('Treeview.padding', {'sticky': 'nswe', 'children': [
                    ('Treeview.treearea', {'sticky': 'nswe'})
                ]})
            ]})
        ])
        self.style.configure('Custom.Treeview',
            background=theme["tree_bg"],
            foreground=theme["tree_fg"],
            fieldbackground=theme["tree_bg"],
            borderwidth=1,
            relief='solid',
            rowheight=25)
        # Do NOT use tag_configure with borderwidth, bordercolor, relief (unsupported)

    def toggle_dark_mode(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_data, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As...", command=self.save_file_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)
        menubar.add_cascade(label="File", menu=file_menu)

        # Switch-style toggle for light/dark mode (BooleanVar)
        view_menu = Menu(menubar, tearoff=0)
        from tkinter import BooleanVar
        self.is_dark_mode_var = BooleanVar(value=self.is_dark_mode)
        def on_toggle():
            self.is_dark_mode = self.is_dark_mode_var.get()
            self.apply_theme()
        view_menu.add_checkbutton(label="Toggle dark Mode", variable=self.is_dark_mode_var, command=on_toggle)
        menubar.add_cascade(label="View", menu=view_menu)

        # เพิ่มเมนู ? สำหรับข้อมูลผู้จัดทำและเวอร์ชัน
        def show_about():
            messagebox.showinfo(
                "เกี่ยวกับโปรแกรม",
                "EXP Editor\n\nผู้จัดทำ: ƒɾìҽɾҽղ\nเวอร์ชัน: 1.0.0\n\nโปรแกรมสำหรับแก้ไขและคำนวณ EXP progression ของ rAthena (YAML)\n\nติดต่อ Discord: @kreanlnwza"
            )
        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="เกี่ยวกับ...", command=show_about)
        menubar.add_cascade(label="?", menu=help_menu)

        self.root.bind("<Control-o>", lambda e: self.open_file())
        self.root.bind("<Control-s>", lambda e: self.save_data())
        self.root.bind("<Control-S>", lambda e: self.save_file_as())

    def update_title(self):
        filename = os.path.basename(self.current_file)
        self.root.title(f"EXP Editor - {filename}{' *' if self.unsaved_changes else ''}")

    def load_exp_data(self, filepath):
        logging.info(f"Attempting to load data from: {filepath}")
        if not os.path.exists(filepath):
            logging.warning(f"File not found: {filepath}")
            if messagebox.askyesno("File Not Found", f"File '{os.path.basename(filepath)}' not found.\nWould you like to create it?"):
                self.data = {'Header': {'Type': 'JOB_STATS', 'Version': 3}, 'Body': []}
                self.current_file = filepath
                self.populate_job_group_list()
                self.update_title()
            else:
                if self.data is None: self.root.destroy()
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = yaml.safe_load(f)
            logging.info("YAML file read and parsed successfully.")
            self.current_file = filepath
            self.populate_job_group_list()
            self.populate_exp_table()
            self.unsaved_changes = False
            self.update_title()
        except Exception as e:
            logging.error(f"Failed to read or parse YAML file: {e}", exc_info=True)
            messagebox.showerror("File Read Error", f"An error occurred while reading the YAML file:\n{e}")
            if self.data is None: self.root.destroy()

    def get_group_description(self, group):
        desc_parts = []

        if 'GroupName' in group:
            desc_parts.append(group['GroupName'])

        jobs = [job for job, enabled in group.get('Jobs', {}).items() if enabled]
        if jobs:
            jobs_str = ", ".join(jobs[:3])
            if len(jobs) > 3:
                jobs_str += f", (+{len(jobs) - 3})"
            desc_parts.append(f"({jobs_str})")
        elif not desc_parts: # If no GroupName and no jobs, then it's an unnamed group
            desc_parts.append("Unnamed Group")

        if 'BaseExp' in group:
            desc_parts.append("[EXP]")
        if 'JobExp' in group:
            desc_parts.append("[J.EXP]")

        return " ".join(desc_parts)

    def populate_job_group_list(self):
        logging.info("Populating job group list...")
        self.job_group_list.delete(0, END)
        if self.data and 'Body' in self.data:
            for group in self.data.get('Body', []):
                group_name = self.get_group_description(group)
                self.job_group_list.insert(END, group_name)
            logging.info(f"Populated list with {self.job_group_list.size()} items.")
        else:
            logging.warning("No data or body to populate job group list.")

    def on_group_select(self, event):
        if selection := event.widget.curselection():
            self.selected_group_index = selection[0]
            logging.info(f"Group selected: index {self.selected_group_index}")
            group = self.data['Body'][self.selected_group_index]
            logging.info(f"Selected group data: {group}")
            if 'BaseExp' in group:
                self.selected_exp_type.set("BaseExp")
            elif 'JobExp' in group:
                self.selected_exp_type.set("JobExp")
            logging.info(f"Selected EXP type after group selection: {self.selected_exp_type.get()}")
            self.populate_exp_table()

    def on_exp_type_change(self):
        logging.info(f"EXP type changed to: {self.selected_exp_type.get()}")
        self.populate_exp_table()

    def populate_exp_table(self, event=None):
        logging.info("Populating EXP table...")
        for item in self.tree.get_children():
            self.tree.delete(item)
        if self.selected_group_index is None or not self.data:
            logging.warning("No group selected or no data. Cannot populate EXP table.")
            return
        group = self.data['Body'][self.selected_group_index]
        exp_type = self.selected_exp_type.get()
        logging.info(f"Populating table for group: {group.get('GroupName', 'Unnamed')} and EXP type: {exp_type}")
        if exp_table := group.get(exp_type):
            for idx, item in enumerate(exp_table):
                values = (item['Level'], item['Exp'])
                item_id = self.tree.insert('', 'end', values=values)
                tags = []
                if idx % 2 == 0:
                    tags.append('evenrow')
                else:
                    tags.append('oddrow')
                self.tree.item(item_id, tags=tuple(tags))
        else:
            logging.warning(f"No {exp_type} data found for the selected group.")

    def on_level_select(self, event):
        # No more self.level_entry or self.exp_entry to update
        pass

    def update_exp_value(self, event=None):
        # This method is now obsolete since editing is in-place in the table
        pass

    def set_max_exp(self):
        if not self.tree.selection():
            messagebox.showwarning("No Selection", "Please select a level from the table to identify the table type.")
            return
            
        level_to_update_str = self.level_entry.get()
        if not level_to_update_str:
             messagebox.showwarning("No Selection", "Please select a level first.")
             return
        
        level_to_update = int(level_to_update_str)
        exp_type = self.selected_exp_type.get()
        
        # Get actual final level from data
        group = self.data['Body'][self.selected_group_index]
        final_level = self._get_final_level_for_type(group, exp_type)
            
        # Check if user is trying to set max EXP on final level
        if level_to_update == final_level:
            if not messagebox.askyesno("Final Level", 
                                     f"This is the final level ({final_level}) for {exp_type}.\n"
                                     f"It should always be 999999999.\n"
                                     f"Do you want to set it to the fixed final value?"):
                return
        
        max_exp_value = 999999999
        
        self.exp_entry.delete(0, END)
        self.exp_entry.insert(0, str(max_exp_value))
        self.update_exp_value()


    def _ensure_final_level_fixed(self, group, exp_type, final_level, final_exp):
        """Ensure the final level always has the fixed EXP value"""
        final_level_exists = False
        for item in group[exp_type]:
            if item['Level'] == final_level:
                if item['Exp'] != final_exp:
                    logging.warning(f"Final level {final_level} had EXP {item['Exp']}, fixing to {final_exp}")
                item['Exp'] = final_exp  # Force final level to fixed EXP
                final_level_exists = True
                break
        
        if not final_level_exists:
            # Add final level if it doesn't exist
            group[exp_type].append({'Level': final_level, 'Exp': final_exp})
            logging.info(f"Added missing final level {final_level} with fixed EXP {final_exp}")

    def _get_final_level_for_type(self, group, exp_type):
        """Get the actual final level from existing data"""
        if exp_type in group and group[exp_type]:
            return max(item['Level'] for item in group[exp_type])
        else:
            # Default values if no data exists
            return 99 if exp_type == 'JobExp' else 50

    def _validate_final_levels(self):
        """Validate that all final levels have the correct fixed EXP"""
        if not self.data or 'Body' not in self.data:
            return True
            
        validation_issues = []
        fixed_issues = []
        
        for group_index, group in enumerate(self.data['Body']):
            for exp_type in ['BaseExp', 'JobExp']:
                if exp_type in group and group[exp_type]:
                    final_level = self._get_final_level_for_type(group, exp_type)
                    final_exp = 999999999
                    
                    # Check if final level exists and has correct EXP
                    final_level_item = None
                    for item in group[exp_type]:
                        if item['Level'] == final_level:
                            final_level_item = item
                            break
                    
                    if final_level_item:
                        if final_level_item['Exp'] != final_exp:
                            validation_issues.append(f"Group {group_index + 1} {exp_type}: Level {final_level} has EXP {final_level_item['Exp']} (should be {final_exp})")
                            # Auto-fix the issue
                            final_level_item['Exp'] = final_exp
                            fixed_issues.append(f"Fixed Group {group_index + 1} {exp_type}: Level {final_level}")
                    else:
                        validation_issues.append(f"Group {group_index + 1} {exp_type}: Missing final level {final_level}")
                        # Auto-fix by adding final level
                        group[exp_type].append({'Level': final_level, 'Exp': final_exp})
                        group[exp_type].sort(key=lambda x: x['Level'])
                        fixed_issues.append(f"Added Group {group_index + 1} {exp_type}: Level {final_level}")
        
        if validation_issues:
            if fixed_issues:
                self.unsaved_changes = True
                self.update_title()
                messagebox.showinfo("Final Level Validation", 
                                   f"Found and fixed {len(fixed_issues)} final level issues:\n\n" + 
                                   "\n".join(fixed_issues[:5]) + 
                                   (f"\n... and {len(fixed_issues) - 5} more" if len(fixed_issues) > 5 else ""))
                self.populate_exp_table()  # Refresh display
        
        return len(validation_issues) == 0

    def jump_to_level(self):
        """Open dialog to jump to a specific level in the current EXP table"""
        if self.selected_group_index is None:
            messagebox.showwarning("No Group Selected", "Please select a job group first.")
            return
        
        group = self.data['Body'][self.selected_group_index]
        exp_type = self.selected_exp_type.get()
        
        if exp_type not in group or not group[exp_type]:
            messagebox.showwarning("No EXP Data", f"The selected group does not have {exp_type} data.")
            return
        
        # Get all available levels for this group and exp type
        available_levels = sorted([item['Level'] for item in group[exp_type]])
        
        if not available_levels:
            messagebox.showwarning("No Data", "No level data found for the selected group and EXP type.")
            return
        
        # Create dialog
        dialog = Toplevel(self.root)
        dialog.title("Jump to Level")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("260x140")
        dialog.resizable(False, False)
        
        # Center the dialog on parent window
        dialog.update_idletasks()
        x = (self.root.winfo_x() + (self.root.winfo_width() // 2)) - (dialog.winfo_width() // 2)
        y = (self.root.winfo_y() + (self.root.winfo_height() // 2)) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        frame = ttk.Frame(dialog, padding="15")
        frame.pack(fill="both", expand=True)
        
        # Level input
        ttk.Label(frame, text="Level to jump to:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        level_entry = ttk.Entry(frame, width=15)
        level_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        level_entry.focus()
        
        # Info label
        info_text = f"Available levels: {available_levels[0]} - {available_levels[-1]}"
        info_label = ttk.Label(frame, text=info_text, font=("Segoe UI", 8))
        info_label.grid(row=1, column=0, columnspan=2, pady=(0, 10), sticky="w")
        
        def on_jump():
            try:
                target_level = int(level_entry.get())
                
                if target_level not in available_levels:
                    messagebox.showerror("Level Not Found", 
                                       f"Level {target_level} is not available in the current data.\n"
                                       f"Available levels: {available_levels[0]} - {available_levels[-1]}")
                    return
                
                # Find the item in the treeview
                for item_id in self.tree.get_children():
                    item_values = self.tree.item(item_id, 'values')
                    if item_values and int(item_values[0]) == target_level:
                        # Select and scroll to the item
                        self.tree.selection_set(item_id)
                        self.tree.focus(item_id)
                        self.tree.see(item_id)
                        
                        # Update the selection in the listbox (if applicable)
                        for i, exp_item in enumerate(group[exp_type]):
                            if exp_item['Level'] == target_level:
                                self.exp_listbox.selection_clear(0, END)
                                self.exp_listbox.selection_set(i)
                                self.exp_listbox.see(i)
                                self.on_exp_select(None)
                                break
                        
                        dialog.destroy()
                        messagebox.showinfo("Success", f"Jumped to Level {target_level}")
                        return
                
                messagebox.showerror("Error", f"Could not find Level {target_level} in the display.")
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid level number.")
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Jump", command=on_jump).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side="left", padx=5)
        
        # Bind Enter key to jump
        def on_enter(event):
            on_jump()
        
        level_entry.bind('<Return>', on_enter)
        dialog.protocol("WM_DELETE_WINDOW", on_cancel)
        
        self.root.wait_window(dialog)

    def save_data_to_path(self, filepath):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(self.data, f, allow_unicode=True, sort_keys=False, indent=2)
            
            self.current_file = filepath
            self.unsaved_changes = False
            self.update_title()
            messagebox.showinfo("Success", f"Successfully saved changes to {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Save Error", f"An error occurred while saving the file:\n{e}")

    def save_data(self):
        self.save_data_to_path(self.current_file)

    def save_file_as(self):
        if filepath := filedialog.asksaveasfilename(defaultextension=".yml", filetypes=[("YAML Files", "*.yml"), ("All Files", "*.*")]):
            self.save_data_to_path(filepath)

    def open_file(self):
        if self.unsaved_changes:
            if not messagebox.askyesno("Unsaved Changes", "You have unsaved changes. Open a new file without saving?"):
                return
        
        if filepath := filedialog.askopenfilename(filetypes=[("YAML Files", "*.yml"), ("All Files", "*.*")]):
            self.load_exp_data(filepath)

    def on_closing(self):
        self.save_config()
        if self.unsaved_changes:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before quitting?")
            if response is True: # Yes
                self.save_data()
                self.root.destroy()
            elif response is False: # No
                self.root.destroy()
            else: # Cancel
                return
        else:
            self.root.destroy()

    def load_config(self):
        logging.info(f"Attempting to load config from: {self.config_file}")
        default_level_width = 120
        default_exp_width = 250

        config_loaded = False
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                if config and 'column_widths' in config:
                    widths = config['column_widths']
                    
                    level_width = widths.get('Level', default_level_width)
                    exp_width = widths.get('EXP', default_exp_width)

                    # Validate loaded widths - prevent extremely large values
                    if level_width <= 0 or level_width > 800: level_width = default_level_width
                    if exp_width <= 0 or exp_width > 1000: exp_width = default_exp_width

                    # Ensure loaded widths are at least the default/minwidth
                    if level_width < 80: level_width = default_level_width
                    if exp_width < 150: exp_width = default_exp_width

                    self.tree.column('Level', width=level_width, stretch=False)
                    self.tree.column('EXP', width=exp_width, stretch=True)
                    logging.info(f"Loaded column widths: Level={level_width}, EXP={exp_width}")
                    config_loaded = True
                    logging.info("Config loaded successfully.")
            except Exception as e:
                logging.error(f"Failed to load or parse config file: {e}. Deleting corrupted config file.", exc_info=True)
                # Delete corrupted config file to prevent future issues
                try:
                    os.remove(self.config_file)
                    logging.info(f"Deleted corrupted config file: {self.config_file}")
                except Exception as remove_e:
                    logging.error(f"Failed to delete corrupted config file: {remove_e}", exc_info=True)
        
        if not config_loaded:
            logging.info("Config file not found or invalid. Using default column widths.")
            self.tree.column('Level', width=default_level_width, stretch=False)
            self.tree.column('EXP', width=default_exp_width, stretch=True)
            logging.info(f"Using default column widths: Level={default_level_width}, EXP={default_exp_width}")
        
        self.tree.update_idletasks() # Force UI update

    def save_config(self):
        logging.info(f"Attempting to save config to: {self.config_file}")
        level_width = self.tree.column('Level', 'width')
        exp_width = self.tree.column('EXP', 'width')

        # Ensure widths are reasonable before saving
        if level_width < 80 or level_width > 800: level_width = 120 # Reasonable range
        if exp_width < 150 or exp_width > 1000: exp_width = 250 # Reasonable range

        config = {
            'column_widths': {
                'Level': level_width,
                'EXP': exp_width
            }
        }
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, sort_keys=False, indent=2)
            logging.info(f"Config saved successfully with Level={level_width}, EXP={exp_width}")
        except Exception as e:
            logging.error(f"Failed to save config file: {e}", exc_info=True)

    def adjust_color(self, color, amount):
        """Adjust color brightness by amount"""
        try:
            # Convert hex to RGB
            color = color.lstrip('#')
            rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            
            # Adjust each component
            new_rgb = tuple(min(255, max(0, c + amount)) for c in rgb)
            
            # Convert back to hex
            return f'#{new_rgb[0]:02x}{new_rgb[1]:02x}{new_rgb[2]:02x}'
        except:
            return color

    def on_double_click(self, event):
        """Handle double-click event on the treeview"""
        region = self.tree.identify_region(event.x, event.y)
        if region == 'cell':
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)
            # Only allow editing EXP column (now #2)
            if column == '#2' and item:  # #2 is the EXP column
                self.start_edit(item, column)

    def start_edit(self, item, column):
        """Start editing a cell"""
        if self.editing_item:
            self.on_edit_complete(None)
        # Get cell coordinates
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
        # Position entry widget on top of cell
        self.edit_entry.place(x=bbox[0], y=bbox[1],
                            width=bbox[2], height=bbox[3])
        # Get current value (EXP is now index 1)
        current_value = self.tree.item(item)['values'][1]
        self.edit_entry.delete(0, 'end')
        self.edit_entry.insert(0, current_value)
        self.edit_entry.selection_range(0, 'end')
        self.edit_entry.focus_set()
        self.editing_item = item
        self.editing_column = column

    def on_edit_complete(self, event):
        """Handle completion of cell editing"""
        if not self.editing_item:
            return
        try:
            new_value = int(self.edit_entry.get())
            item_values = list(self.tree.item(self.editing_item)['values'])
            level = item_values[0]
            # Update treeview (EXP is index 1)
            item_values[1] = new_value
            self.tree.item(self.editing_item, values=item_values)
            # Update data structure
            group = self.data['Body'][self.selected_group_index]
            exp_type = self.selected_exp_type.get()
            for item in group.get(exp_type, []):
                if item['Level'] == level:
                    item['Exp'] = new_value
                    break
            self.unsaved_changes = True
            self.update_title()
        except ValueError:
            messagebox.showerror("Invalid Input", "EXP value must be an integer.")
        finally:
            self.edit_entry.place_forget()
            self.editing_item = None
            self.editing_column = None
            self.tree.focus_set()

    def auto_calculate_exp(self):
        if self.selected_group_index is None:
            messagebox.showwarning("No Group Selected", "Please select a job group first.")
            return

        group = self.data['Body'][self.selected_group_index]
        exp_type = self.selected_exp_type.get()

        if exp_type not in group or not group[exp_type]:
            messagebox.showwarning("No EXP Data", f"The selected group does not have {exp_type} data to calculate.")
            return

        self.show_auto_calculate_dialog(group, exp_type)

    def show_auto_calculate_dialog(self, group, exp_type):
        dialog = Toplevel(self.root)
        dialog.title("Auto Calculate EXP Range")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("260x140")
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding="10")
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Start Level:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        start_level_entry = ttk.Entry(frame)
        start_level_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        if group[exp_type]:
            last_level = max(item['Level'] for item in group[exp_type])
            start_level_entry.insert(0, str(last_level))
        else:
            start_level_entry.insert(0, "1")

        ttk.Label(frame, text="End Level:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        end_level_entry = ttk.Entry(frame)
        end_level_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Determine max level for the selected exp_type
        max_level = 0
        if group[exp_type]:
            max_level = max(item['Level'] for item in group[exp_type])
        
        # Set default end level to a reasonable value, but allow user to go beyond max_level
        default_end_level = max(1, max_level - 1) if max_level > 1 else 1
        end_level_entry.insert(0, str(default_end_level))

        def on_confirm():
            try:
                start_level = int(start_level_entry.get())
                end_level = int(end_level_entry.get())
                
                if end_level < start_level:
                    end_level = start_level + 1
                    end_level_entry.delete(0, 'end')
                    end_level_entry.insert(0, str(end_level))
                
                # Basic validation
                if start_level < 1:
                    messagebox.showerror("Invalid Range", "Start level must be at least 1.")
                    return
                if end_level < start_level:
                    messagebox.showerror("Invalid Range", "End level must be greater than or equal to start level.")
                    return
                if end_level > 9999:  # Extended maximum limit for user flexibility
                    if not messagebox.askyesno("Very High Level Warning", 
                                             f"End level ({end_level}) is extremely high (over 9999).\n"
                                             f"This may take a long time to calculate and use a lot of memory.\n"
                                             f"Do you want to continue?"):
                        return
                
                # Warning if end_level exceeds existing data
                if end_level >= max_level and max_level > 0:
                    if not messagebox.askyesno("High Level Warning", 
                                             f"End level ({end_level}) is higher than existing max level ({max_level}).\n"
                                             f"The calculation will extend beyond existing data.\n"
                                             f"Do you want to continue?"):
                        return
                
                dialog.destroy()
                self._perform_auto_calculation(group, exp_type, start_level, end_level)
            except ValueError:
                messagebox.showerror("Invalid Input", "Levels must be integers.")

        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Calculate", command=on_confirm).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left", padx=5)

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        self.root.wait_window(dialog)

    def calculate_exp_progression_expo(self, start_level, start_exp, end_level, final_exp=999999999):
        # คำนวณ EXP progression แบบ exponential smooth
        result = {}
        n = end_level - start_level
        if n <= 0:
            return {}
        # คำนวณอัตราโต
        growth = (final_exp / start_exp) ** (1 / n)
        for lv in range(start_level, end_level+1):
            if lv == end_level:
                result[lv] = final_exp
            else:
                result[lv] = int(start_exp * (growth ** (lv - start_level)))
        return result

    def _perform_auto_calculation(self, group, exp_type, start_level, end_level):
        exp_data = sorted(group[exp_type], key=lambda x: x['Level'])
        # หาเลเวลก่อนสุดท้ายที่ EXP < 99999999
        prev_item = None
        for item in reversed(exp_data):
            if item['Level'] < start_level and item['Exp'] < 99999999:
                prev_item = item
                break
        if prev_item is None:
            messagebox.showerror("Data Error", "Cannot find valid EXP for calculation.")
            return
        start_exp = prev_item['Exp']
        # คำนวณ EXP progression แบบ exponential
        updated_exp_values = self.calculate_exp_progression_expo(prev_item['Level'], start_exp, end_level)
        # ลบเลเวลที่เกิน end_level ออก
        group[exp_type] = [item for item in group[exp_type] if item['Level'] <= prev_item['Level']]
        # เพิ่ม/อัปเดตค่าใหม่
        for lv in range(prev_item['Level']+1, end_level+1):
            group[exp_type].append({'Level': lv, 'Exp': updated_exp_values[lv]})
        group[exp_type].sort(key=lambda x: x['Level'])
        self.populate_exp_table()
        self.unsaved_changes = True
        self.update_title()
        messagebox.showinfo("Calculation Complete", f"Auto calculation for {exp_type} finished for levels {prev_item['Level']+1} to {end_level}.")

    def add_exp_rows(self):
        """เพิ่มแถว EXP ตามจำนวนที่ระบุ"""
        if self.selected_group_index is None or not self.data:
            messagebox.showwarning("No Group Selected", "กรุณาเลือกกลุ่มก่อน")
            return
        group = self.data['Body'][self.selected_group_index]
        exp_type = self.selected_exp_type.get()
        try:
            count = int(self.add_remove_count_var.get())
            if count < 1: count = 1
        except Exception:
            count = 1
        # หาเลเวลสุดท้าย
        last_level = 0
        if exp_type in group and group[exp_type]:
            last_level = max(item['Level'] for item in group[exp_type])
        for i in range(count):
            last_level += 1
            group.setdefault(exp_type, []).append({'Level': last_level, 'Exp': 0})
        group[exp_type].sort(key=lambda x: x['Level'])
        self.populate_exp_table()
        self.unsaved_changes = True
        self.update_title()

    def remove_exp_rows(self):
        """ลบแถว EXP จากท้าย ตามจำนวนที่ระบุ"""
        if self.selected_group_index is None or not self.data:
            messagebox.showwarning("No Group Selected", "กรุณาเลือกกลุ่มก่อน")
            return
        group = self.data['Body'][self.selected_group_index]
        exp_type = self.selected_exp_type.get()
        try:
            count = int(self.add_remove_count_var.get())
            if count < 1: count = 1
        except Exception:
            count = 1
        if exp_type in group and group[exp_type]:
            # ห้ามลบจนหมด (เหลืออย่างน้อย 1 แถว)
            remain = max(1, len(group[exp_type]) - count)
            group[exp_type] = group[exp_type][:remain]
            self.populate_exp_table()
            self.unsaved_changes = True
            self.update_title()

    def set_max_exp_button(self):
        """ตั้งค่า EXP ของเลเวลสุดท้ายเป็น 999999999 (หรือค่าที่ fix ตามประเภท)"""
        if self.selected_group_index is None or not self.data:
            messagebox.showwarning("No Group Selected", "กรุณาเลือกกลุ่มก่อน")
            return
        group = self.data['Body'][self.selected_group_index]
        exp_type = self.selected_exp_type.get()
        if exp_type in group and group[exp_type]:
            # base/job lv. อาจมี max ไม่เท่ากัน ให้ใช้เลเวลสุดท้ายของ exp_type นั้น
            final_level = max(item['Level'] for item in group[exp_type])
            for item in group[exp_type]:
                if item['Level'] == final_level:
                    item['Exp'] = 999999999
            self.populate_exp_table()
            self.unsaved_changes = True
            self.update_title()
            messagebox.showinfo("Max EXP", f"ตั้งค่า EXP ของเลเวลสุดท้าย ({final_level}) เป็น 999999999 เรียบร้อยแล้ว")
        else:
            messagebox.showwarning("No Data", "ไม่พบข้อมูล EXP ในกลุ่มนี้")

def check_pyyaml():
    try:
        import yaml
        logging.info("PyYAML dependency check passed.")
        return True
    except ImportError:
        logging.critical("PyYAML library is not installed.")
        root = Tk()
        root.withdraw()
        messagebox.showerror("Dependency Missing", "PyYAML library is not installed.\nPlease run 'pip install pyyaml' in your command prompt.")
        root.destroy()
        return False

if __name__ == "__main__":
    try:
        if check_pyyaml():
            if show_login_dialog():
                logging.info("Starting application...")
                root = Tk()
                app = ExpEditorApp(root)
                root.mainloop()
                logging.info("Application closed normally.")
            else:
                # ไม่ผ่าน login
                pass
    except Exception as e:
        logging.critical(f"An unhandled exception occurred: {e}", exc_info=True)
        messagebox.showerror("Fatal Error", f"A fatal error occurred. Please check the log file for details.\n\n{e}")