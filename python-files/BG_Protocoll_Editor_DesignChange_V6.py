import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import re

# ========= Constants for consistent padding =========
PAD_SM = 4
PAD_MD = 10
PAD_LG = 16

# =======================================================================
# ========= Modern Flat Design (Google Inspired) - Pastel Tones =========
# =======================================================================
def setup_modern_flat_style(root, base_size=10):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # --- 1. Define Color Palette ---
    BG_COLOR = "#f5f5f5"
    CARD_COLOR = "#ffffff"
    TEXT_COLOR = "#212121"
    SUBTLE_TEXT_COLOR = "#757575"
    BORDER_COLOR = "#e0e0e0"
    PRIMARY_BLUE = "#64b5f6"
    PRIMARY_BLUE_HOVER = "#42a5f5"
    SUCCESS_GREEN = "#81c784"
    SUCCESS_GREEN_HOVER = "#66bb6a"
    WARNING_ORANGE = "#ffb74d"
    WARNING_ORANGE_HOVER = "#ffa726"
    ACTIVE_GREEN_BG = "#e8f5e9" # Light pastel green for active rows
    
    # --- 2. Basic Elements & Font Sizes ---
    root.configure(bg=BG_COLOR)
    font_normal = ("Segoe UI", base_size)
    font_bold = ("Segoe UI", base_size, "bold")
    font_small_bold = ("Segoe UI", base_size - 1, "bold")
    font_header = ("Segoe UI", base_size + 2, "bold")
    font_card_header = ("Segoe UI", base_size + 1, "bold")

    style.configure("TFrame", background=BG_COLOR)
    style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=font_normal)
    style.configure("Card.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR, font=font_normal)
    style.configure("Header.TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=font_header)
    
    # --- 3. "Card" Style for Labelframes ---
    style.configure("Card.TLabelframe", background=CARD_COLOR, borderwidth=1, relief="solid", bordercolor=BORDER_COLOR)
    style.configure("Card.TLabelframe.Label", background=CARD_COLOR, foreground=TEXT_COLOR, font=font_card_header)

    # --- 4. Input Fields ---
    style.configure("TEntry", borderwidth=1, relief="flat", fieldbackground=CARD_COLOR, padding=6, font=font_normal)
    style.map("TEntry", bordercolor=[("focus", PRIMARY_BLUE), ("!focus", BORDER_COLOR)], relief=[("focus", "solid"), ("!focus", "solid")])
    style.configure("TCombobox", arrowsize=18, borderwidth=1, relief="flat", padding=4, font=font_normal)
    style.map("TCombobox", fieldbackground=[("readonly", CARD_COLOR)], bordercolor=[("focus", PRIMARY_BLUE), ("!focus", BORDER_COLOR)], relief=[("focus", "solid"), ("!focus", "solid")])

    # --- 5. Checkbuttons ---
    style.configure("TCheckbutton", background=CARD_COLOR, foreground=TEXT_COLOR, font=font_normal, padding=5)
    style.map("TCheckbutton",
        indicatorcolor=[
            ("active", "selected", PRIMARY_BLUE_HOVER),
            ("selected", PRIMARY_BLUE),
            ("active", "!selected", BORDER_COLOR),
        ]
    )

    # --- 6. Dropdown Menus (OptionMenu) ---
    style.configure("TMenubutton", background=CARD_COLOR, padding=(8, 6), borderwidth=1, relief="solid", bordercolor=BORDER_COLOR, arrowcolor=SUBTLE_TEXT_COLOR, font=font_normal)
    style.map("TMenubutton", bordercolor=[("active", PRIMARY_BLUE)], background=[("active", CARD_COLOR)])

    # --- 7. Buttons ---
    button_padding = (14, 8)
    
    style.configure("Primary.TButton", background=PRIMARY_BLUE, foreground="white", font=font_bold, padding=button_padding, borderwidth=0, relief="flat")
    style.map("Primary.TButton", background=[("pressed", PRIMARY_BLUE_HOVER), ("active", PRIMARY_BLUE_HOVER)])
    style.configure("Success.TButton", background=SUCCESS_GREEN, foreground="white", font=font_bold, padding=button_padding, borderwidth=0, relief="flat")
    style.map("Success.TButton", background=[("pressed", SUCCESS_GREEN_HOVER), ("active", SUCCESS_GREEN_HOVER)])
    style.configure("Warning.TButton", background=WARNING_ORANGE, foreground="white", font=font_bold, padding=button_padding, borderwidth=0, relief="flat")
    style.map("Warning.TButton", background=[("pressed", WARNING_ORANGE_HOVER), ("active", WARNING_ORANGE_HOVER)])
    style.configure("TButton", background="#e0e0e0", foreground=TEXT_COLOR, font=font_normal, padding=(10, 6), borderwidth=0, relief="flat")
    style.map("TButton", background=[("pressed", "#bdbdbd"), ("active", "#cfcfcf")])

    # --- 8. Scrollbar ---
    style.configure("Modern.Vertical.TScrollbar", troughcolor=BG_COLOR, background=BORDER_COLOR, borderwidth=0, relief="flat", arrowsize=14, arrowcolor=SUBTLE_TEXT_COLOR)
    style.map("Modern.Vertical.TScrollbar", background=[("active", SUBTLE_TEXT_COLOR)])

    # --- 9. Table Headers and Rows ---
    style.configure("TableHeader.TLabel", background="#eeeeee", foreground=SUBTLE_TEXT_COLOR, padding=5, relief="flat", anchor="center", font=font_small_bold)
    style.configure("EvenRow.TLabel", background=CARD_COLOR, foreground=TEXT_COLOR)
    style.configure("OddRow.TLabel", background=BG_COLOR, foreground=TEXT_COLOR)
    style.configure("ActiveRow.TLabel", background=ACTIVE_GREEN_BG, foreground=TEXT_COLOR) # Style for active rows
    
    # --- 10. Tabs (Notebook) ---
    style.configure("TNotebook", background=BG_COLOR, borderwidth=0)
    style.configure("TNotebook.Tab", padding=(12, 8), font=font_normal, borderwidth=0)
    style.map("TNotebook.Tab", background=[("selected", CARD_COLOR), ("!selected", BG_COLOR)], expand=[("selected", [1, 1, 1, 0])])

# =======================================================================
# ========= Global Constants ============================================
# =======================================================================
HEADER_LINES = [
    "*PLZ1*;16;4;15;4;17;4", "*PZ1*;16;8;15;8;17;8", "*V1*;13;4", "*T1*;21;4", "*PLZ2*;16;12;15;12;17;12",
    "*PZ2*;16;16;15;16;17;16", "*V2*;13;12", "*T2*;21;12", "*PLZ3*;16;20;15;20;17;20", "*PZ3*;16;24;15;24;17;24",
    "*V3*;13;20", "*T3*;21;20", "*PLZ4*;16;28;15;28;17;28", "*PZ4*;16;32;15;32;17;32", "*V4*;13;28",
    "*T4*;21;28", "*PLZ5*;16;36;15;36;17;36", "*PZ5*;16;40;15;40;17;40", "*V5*;13;36", "*T5*;21;36",
    "*PLZ6*;16;44;15;44;17;44", "*PZ6*;16;48;15;48;17;48", "*V6*;13;44", "*T6*;21;44", "*PLZ7*;16;52;15;52;17;52",
    "*PZ7*;16;56;15;56;17;56", "*V7*;13;52", "*T7*;21;52", "*PLZ8*;16;60;15;60;17;60", "*PZ8*;16;64;15;64;17;64",
    "*V8*;13;60", "*T8*;21;60"
]
LABEL_CHOICES = {
    0: "No Selection", 1: "JaClean", 2: "Crystal-Violete", 3: "Distilled Water", 4: "Lugol's", 5: "JetDecolorizer",
    6: "Safranin", 7: "Methylenblue", 8: "May-Gruenwald", 9: "JetBuffer", 10: "Giemsa", 11: "Buffer",
    12: "Wright-Giemsa", 13: "Wright"
}
METHOD_MAPPING = {
    "Gram": 1, "Löffler's Methylene Blue": 2, "Hematoxylin & Eosin": 3, "May-Grünwald-Giemsa": 4,
    "May-Grünwald": 5, "Wright-Giemsa": 6, "Giemsa": 7, "Wright": 8
}


class ProtocolEditor:
    
    def __init__(self, root):
        self.root = root
        self.root.title("Protocol Editor")

        self.base_font_size = 10
        self.cons_vars = [tk.IntVar(value=0) for _ in range(5)]
        self.rows_widgets = []
        self.step_label_vars = []
        self.step_name_vars = []
        self.percent_options = [str(x) for x in range(0, 101, 10)]
        self.label_options = list(LABEL_CHOICES.values())
        self.label_num_to_text = LABEL_CHOICES
        self.label_text_to_num = {v: k for k, v in LABEL_CHOICES.items()}
        self.method_options = list(METHOD_MAPPING.keys())
        self.selected_method = tk.StringVar(value=self.method_options[0])
        self.custom_filename = tk.StringVar(value="")
        
        self.build_gui()

    def build_gui(self):
        setup_modern_flat_style(self.root, self.base_font_size)
        self._create_file_toolbar()
        self._create_consumption_frame()
        self._create_tabbed_protocol_view()

    def _create_file_toolbar(self):
        frame_file = ttk.Frame(self.root)
        frame_file.pack(fill='x', padx=PAD_LG, pady=PAD_MD, anchor='n')

        ttk.Label(frame_file, text="Method:").pack(side='left')
        ttk.Combobox(frame_file, textvariable=self.selected_method, values=self.method_options, state='readonly', width=28).pack(side='left', padx=PAD_MD)
        ttk.Label(frame_file, text="Filename:").pack(side='left')
        ttk.Entry(frame_file, textvariable=self.custom_filename, width=30).pack(side='left', padx=PAD_MD)
        
        ttk.Button(frame_file, text="Open", style='Warning.TButton', command=self.open_file).pack(side='left', padx=PAD_SM)
        ttk.Button(frame_file, text="Save", style='Primary.TButton', takefocus=0, command=self.save_file).pack(side='left', padx=PAD_SM)
        ttk.Button(frame_file, text="New", style='Success.TButton', command=self.clear_all).pack(side='left', padx=PAD_SM)
    
    def _create_consumption_frame(self):
        frame_cons = ttk.Labelframe(self.root, text="Reagent Consumption [ml]", style="Card.TLabelframe")
        frame_cons.pack(fill='x', padx=PAD_LG, pady=(0, PAD_MD))
        for i in range(5):
            ttk.Label(frame_cons, text=f"Valve {i+1}:", style="Card.TLabel").pack(side='left', padx=6)
            ttk.Entry(frame_cons, textvariable=self.cons_vars[i], width=6).pack(side='left', padx=PAD_MD)
        
    def _create_tabbed_protocol_view(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=PAD_LG, pady=(0, PAD_LG))
        
        self.notebook = ttk.Notebook(main_frame, style="TNotebook")
        self.notebook.pack(fill="both", expand=True, pady=PAD_SM)
        
        vcmd = (self.root.register(self.validate_time_input), '%P')
        headers = ["#", "Active Valve", "Pre-fill", "Tray Func", "Heater", "Tray Out", "Fill", 
                   "Vacuum", "Duration", "Min T", "Max T", "Sensor", "Calib", "Waste", "Heater P", "Reagent"]
        
        for step_idx in range(8):
            tab_frame = ttk.Frame(self.notebook, padding=PAD_MD)
            self.notebook.add(tab_frame, text=f"Step {step_idx + 1}")
            self._create_step_content(tab_frame, step_idx, headers, vcmd)

    def _create_step_content(self, parent, step_idx, headers, vcmd):
        top_bar = ttk.Frame(parent)
        top_bar.pack(fill='x', pady=(0, PAD_MD))

        label_var = tk.StringVar(value="No Selection")
        self.step_label_vars.append(label_var)
        name_var = tk.StringVar(value=f"Staining Step {step_idx + 1}")
        self.step_name_vars.append(name_var)

        ttk.Label(top_bar, text="Step Name:").pack(side='left', padx=(0, PAD_SM))
        ttk.Entry(top_bar, textvariable=name_var, width=20).pack(side='left', padx=(0, PAD_MD))
        ttk.Label(top_bar, text="Reagent:").pack(side='left', padx=(PAD_MD, PAD_SM))
        ttk.Combobox(top_bar, textvariable=label_var, values=self.label_options, state='readonly', width=20).pack(side='left')

        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True)

        for col, h in enumerate(headers):
            ttk.Label(table_frame, text=h, style='TableHeader.TLabel').grid(row=0, column=col, sticky='nsew', padx=1, pady=1)

        for i in range(8):
            global_idx = step_idx * 8 + i
            row_widgets = {}
            
            row_num_label = ttk.Label(table_frame, text=str(global_idx + 1), width=4, anchor='center')
            row_num_label.grid(row=i + 1, column=0, padx=1, pady=1, sticky='nsew')
            row_widgets['row_num_label'] = row_num_label

            valve_options = ["None"] + [f"V{n}" for n in range(1, 8)]
            valve_var = tk.StringVar(value="None")
            row_widgets['active_valve'] = valve_var
            
            ttk.OptionMenu(table_frame, valve_var, valve_var.get(), *valve_options).grid(row=i + 1, column=1, padx=1, pady=1, sticky='ew')
            
            columns_order = ['pre_fill', 'tray_func', 'heater', 'tray_pos', 'fill_p', 'vacuum_p', 'dwell', 'min_t', 'max_t', 'bubble', 'calib', 'waste_p', 'heater_p', 'label']

            for col, field in enumerate(columns_order, start=2):
                if field == 'label':
                    reagent_label = ttk.Label(table_frame, textvariable=label_var, anchor='center')
                    reagent_label.grid(row=i + 1, column=col, padx=1, pady=1, sticky='nsew')
                    row_widgets['reagent_label'] = reagent_label
                    row_widgets[field] = label_var
                elif field in ['pre_fill', 'tray_func', 'heater', 'tray_pos', 'bubble', 'calib', 'waste_p']:
                    var = tk.IntVar(value=0)
                    row_widgets[field] = var
                    ttk.Checkbutton(table_frame, variable=var).grid(row=i + 1, column=col)
                elif field in ['fill_p', 'vacuum_p', 'heater_p']:
                    var = tk.StringVar(value=self.percent_options[0])
                    row_widgets[field] = var
                    ttk.Combobox(table_frame, textvariable=var, values=self.percent_options, width=5, state='readonly').grid(row=i + 1, column=col, padx=1, pady=1, sticky='ew')
                elif field in ['dwell', 'min_t', 'max_t']:
                    var = tk.DoubleVar(value=0.0)
                    row_widgets[field] = var
                    ttk.Entry(table_frame, textvariable=var, width=6, validate='key', validatecommand=vcmd).grid(row=i + 1, column=col, padx=1, pady=1, sticky='ew')
            
            self.rows_widgets.append(row_widgets)
            # Add trace for row highlighting AFTER all widgets for the row are created
            valve_var.trace_add("write", lambda *args, idx=global_idx, widgets=row_widgets: self._on_valve_change(idx, widgets))
            self._on_valve_change(global_idx, row_widgets) # Set initial style

    def _on_valve_change(self, row_index, widgets):
        # This check prevents the error by ensuring the reagent_label exists before trying to access it
        if 'reagent_label' not in widgets:
            return

        valve_value = widgets['active_valve'].get()
        if valve_value != "None":
            new_style = "ActiveRow.TLabel"
        else:
            new_style = "OddRow.TLabel" if (row_index % 2) != 0 else "EvenRow.TLabel"
        
        widgets['row_num_label'].configure(style=new_style)
        widgets['reagent_label'].configure(style=new_style)

    def validate_time_input(self, new_value):
        if not new_value: return True
        try: return 0.0 <= float(new_value) <= 90.0
        except ValueError: return False

    def clear_all(self):
        self.selected_method.set(self.method_options[0])
        self.custom_filename.set("")
        for var in self.cons_vars: var.set(0)
        for i in range(8):
            self.step_label_vars[i].set("No Selection")
            self.step_name_vars[i].set(f"Staining Step {i + 1}")
        for row in self.rows_widgets:
            row['active_valve'].set("None")
            for key, var in row.items():
                if key not in ['active_valve', 'label', 'row_num_label', 'reagent_label']:
                    if isinstance(var, tk.IntVar): var.set(0)
                    else: var.set(self.percent_options[0]) if isinstance(var, tk.StringVar) else var.set(0.0)

    def open_file(self): pass
    def save_file(self): pass


class ProtocolEditorEnhanced(ProtocolEditor):
    def __init__(self, root):
        super().__init__(root)
        self._init_enhancements()

    def _init_enhancements(self):
        notebook_parent = self.notebook.master
        
        ctrl_frame = ttk.Frame(notebook_parent)
        ctrl_frame.pack(side='bottom', fill='x', pady=(PAD_MD, 0))

        ttk.Label(ctrl_frame, text="Zoom:").pack(side='left', padx=(0, PAD_SM))
        ttk.Button(ctrl_frame, text="-", command=self._zoom_out, width=4).pack(side='left')
        ttk.Button(ctrl_frame, text="+", command=self._zoom_in, width=4).pack(side='left', padx=(PAD_SM, PAD_MD))
        
        ttk.Label(ctrl_frame, text="Reorder Tabs:").pack(side='left')
        ttk.Button(ctrl_frame, text="← Move Left", command=lambda: self._move_tab(-1)).pack(side='left', padx=PAD_SM)
        ttk.Button(ctrl_frame, text="Move Right →", command=lambda: self._move_tab(1)).pack(side='left', padx=PAD_MD)
        
        ttk.Button(ctrl_frame, text="Load Step Preset", command=self._load_step_preset).pack(side='right', padx=PAD_SM)
        ttk.Button(ctrl_frame, text="Save Step Preset", style="Primary.TButton", command=self._save_step_preset).pack(side='right', padx=PAD_SM)
        ttk.Button(ctrl_frame, text="Clear Current Step", style="Warning.TButton", command=self._clear_current_step).pack(side='right', padx=PAD_SM)

        for name_var in self.step_name_vars:
            name_var.trace_add("write", self._on_name_change)
        self._update_tab_titles()

    def _on_name_change(self, *args):
        self._update_tab_titles()

    def _update_tab_titles(self):
        for i in range(self.notebook.index("end")):
            name = self.step_name_vars[i].get().strip()
            tab_title = f"{i + 1}. {name or f'Staining Step {i + 1}'}"
            self.notebook.tab(i, text=tab_title)

    def _move_tab(self, direction):
        current_index = self.notebook.index(self.notebook.select())
        new_index = current_index + direction
        if not (0 <= new_index < self.notebook.index("end")): return

        self.step_name_vars.insert(new_index, self.step_name_vars.pop(current_index))
        self.step_label_vars.insert(new_index, self.step_label_vars.pop(current_index))
        
        start_index = current_index * 8
        row_segment = self.rows_widgets[start_index : start_index + 8]
        del self.rows_widgets[start_index : start_index + 8]
        self.rows_widgets[new_index*8:new_index*8] = row_segment

        tab_widget = self.notebook.nametowidget(self.notebook.tabs()[current_index])
        self.notebook.forget(current_index)
        self.notebook.insert(new_index, tab_widget, text="dummy")
        
        self.notebook.select(new_index)
        self._update_tab_titles()
        self._update_row_numbers()

    def _update_row_numbers(self):
        for i, row_widget_dict in enumerate(self.rows_widgets):
            row_widget_dict['row_num_label'].config(text=str(i + 1))
            self._on_valve_change(i, row_widget_dict)
            
    def _clear_current_step(self):
        step_idx = self.notebook.index(self.notebook.select())
        
        self.step_name_vars[step_idx].set(f"Staining Step {step_idx + 1}")
        self.step_label_vars[step_idx].set("No Selection")
        
        start_index = step_idx * 8
        for i in range(8):
            row = self.rows_widgets[start_index + i]
            row['active_valve'].set("None")
            for key, var in row.items():
                if key not in ['active_valve', 'label', 'row_num_label', 'reagent_label']:
                    if isinstance(var, tk.IntVar): var.set(0)
                    else: var.set("0") if isinstance(var, tk.StringVar) else var.set(0.0)

    def _zoom_in(self):
        self.base_font_size += 1
        setup_modern_flat_style(self.root, self.base_font_size)

    def _zoom_out(self):
        self.base_font_size = max(7, self.base_font_size - 1)
        setup_modern_flat_style(self.root, self.base_font_size)

    def _collect_step_data(self, step_idx):
        data = { 'name': self.step_name_vars[step_idx].get(), 'label_num': self.label_text_to_num.get(self.step_label_vars[step_idx].get(), 0), 'rows': [] }
        start_index = step_idx * 8
        for i in range(8):
            row = self.rows_widgets[start_index + i]
            row_data = {'active_valve': row['active_valve'].get()}
            for field in ['pre_fill','tray_func','heater','tray_pos','fill_p','vacuum_p','dwell','min_t','max_t','bubble','calib','waste_p','heater_p']:
                row_data[field] = row[field].get()
            data['rows'].append(row_data)
        return data

    def _apply_step_data(self, step_idx, data):
        self.step_name_vars[step_idx].set(data.get('name', f"Step {step_idx + 1}"))
        self.step_label_vars[step_idx].set(self.label_num_to_text.get(int(data.get('label_num', 0)), "No Selection"))
        start_index = step_idx * 8
        rows_data = data.get('rows', [])
        for i, rowd in enumerate(rows_data[:8]):
            row = self.rows_widgets[start_index + i]
            row['active_valve'].set(rowd.get('active_valve', "None"))
            for field in ['pre_fill','tray_func','heater','tray_pos','fill_p','vacuum_p','dwell','min_t','max_t','bubble','calib','waste_p','heater_p']:
                if field in rowd: row[field].set(rowd[field])

    def _save_step_preset(self):
        step_idx = self.notebook.index(self.notebook.select())
        step_name = self.step_name_vars[step_idx].get().strip()
        sanitized_name = re.sub(r'[<>:"/\\|?*]', '', step_name)
        sanitized_name = sanitized_name.strip('. ') 
        default_filename = f"{sanitized_name}.json" if sanitized_name else f"step_{step_idx+1}_preset.json"
        data = self._collect_step_data(step_idx)
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("Preset JSON", "*.json")], initialfile=default_filename)
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Preset Saved", "The step was successfully saved as a preset.")
        except Exception as e: messagebox.showerror("Error Saving", str(e))

    def _load_step_preset(self):
        step_idx = self.notebook.index(self.notebook.select())
        path = filedialog.askopenfilename(filetypes=[("Preset JSON", "*.json")])
        if not path: return
        try:
            with open(path, "r", encoding="utf-8") as f: data = json.load(f)
            self._apply_step_data(step_idx, data)
            messagebox.showinfo("Preset Loaded", "The preset was successfully loaded into the current step.")
        except Exception as e: messagebox.showerror("Error Loading", str(e))


if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.geometry("1024x768")
        app = ProtocolEditorEnhanced(root)
        root.mainloop()
    except Exception as e:
        import traceback
        messagebox.showerror("Startup Error", traceback.format_exc())