import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinterdnd2 import TkinterDnD, DND_FILES
from bs4 import BeautifulSoup
import re
from collections import defaultdict
import json
import os

# --- Language Configuration ---
LANGUAGES = {
    'zh': {
        "title": "自动算分器 by Murasame",
        "header": "自动算分器",
        "drop_files": "拖放 HTML 文件到这里",
        "loaded_files": "已加载文件",
        "all_names": "所有名字 (可删除)",
        "merging_rules": "合并规则 (x=y)",
        "delete_name": "删除选中名字",
        "add_rule": "添加规则",
        "save_rules": "保存规则",
        "load_rules": "加载规则",
        "process": "开始处理",
        "clear_all": "全部清空",
        "switch_lang": "English",
        "copyright": "版权所有 © 2025 Murasame. 保留所有权利.",
        "add_rule_prompt_title": "添加规则",
        "add_rule_prompt_text": "输入规则 (格式: '别名=主名'):",
        "results_title": "处理结果",
        "results_header": "--- 平均标准分数 ---\n\n",
        "copy_to_clipboard": "复制到剪贴板",
        "copied": "已复制",
        "results_copied": "结果已复制到剪贴板",
        "no_files_warning_title": "警告",
        "no_files_warning_text": "没有加载任何文件。",
        "rules_saved_title": "成功",
        "rules_saved_text": "规则已成功保存。",
        "rules_loaded_title": "成功",
        "rules_loaded_text": "规则已成功加载。",
        "file_dialog_title": "选择规则文件",
        "cleared_title": "已清空",
        "cleared_text": "所有文件、名字和规则已被清空。",
        "error_title": "错误",
        "error_processing_file": "处理文件 {file} 失败: {e}",
    },
    'en': {
        "title": "Score Processor by Murasame",
        "header": "Score Processor",
        "drop_files": "Drag & Drop HTML Files Here",
        "loaded_files": "Loaded Files",
        "all_names": "All Names (Can be deleted)",
        "merging_rules": "Merging Rules (x=y)",
        "delete_name": "Delete Selected Name",
        "add_rule": "Add Rule",
        "save_rules": "Save Rules",
        "load_rules": "Load Rules",
        "process": "Process",
        "clear_all": "Clear All",
        "switch_lang": "简体中文",
        "copyright": "Copyright © 2025 Murasame. All rights reserved.",
        "add_rule_prompt_title": "Add Rule",
        "add_rule_prompt_text": "Enter a rule in 'alias=main_name' format:",
        "results_title": "Processing Results",
        "results_header": "--- Average Standard Scores ---\n\n",
        "copy_to_clipboard": "Copy to Clipboard",
        "copied": "Copied",
        "results_copied": "Results copied to clipboard.",
        "no_files_warning_title": "Warning",
        "no_files_warning_text": "No files loaded.",
        "rules_saved_title": "Success",
        "rules_saved_text": "Rules have been saved successfully.",
        "rules_loaded_title": "Success",
        "rules_loaded_text": "Rules have been loaded successfully.",
        "file_dialog_title": "Select Rules File",
        "cleared_title": "Cleared",
        "cleared_text": "All files, names, and rules have been cleared.",
        "error_title": "Error",
        "error_processing_file": "Failed to process {file}: {e}",
    }
}

# --- Disjoint Set Union (DSU) ---
class DSU:
    def __init__(self):
        self.parent = {}
    def find(self, i):
        if self.parent.get(i) is None: self.parent[i] = i
        if self.parent[i] == i: return i
        self.parent[i] = self.find(self.parent[i])
        return self.parent[i]
    def union(self, i, j):
        root_i = self.find(i)
        root_j = self.find(j)
        if root_i != root_j: self.parent[root_j] = root_i

# --- Core Logic ---
def strip_name(s):
    s = s.strip().lower()
    pos = s.find('_')
    if pos != -1: s = s[pos + 1:]
    s = re.sub(r'cqyc|c[1-3]|g[1-3]|[0-9]|\.|\_|\!|\~|\?| |副本|子文件夹|没|（|）|似|寄|了|-', '', s)
    return s

def extract_table_content(html_file, lang_get):
    names, scores = [], []
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        soup = BeautifulSoup(content, 'lxml')
        table = soup.find('table', {'cellpadding': '1', 'style': 'border-style: solid;'})
        if table:
            for row in table.find_all('tr'):
                tds = row.find_all('td')
                if len(tds) >= 3 and tds[1].get('class') == ['td-0'] and tds[2].get('class') == ['td-2']:
                    name = strip_name(tds[1].get_text(strip=True))
                    score_text = tds[2].get_text(strip=True)
                    if 'std' not in name:
                        names.append(name)
                        scores.append(float(score_text))
    except Exception as e:
        messagebox.showerror(lang_get("error_title"), lang_get("error_processing_file").format(file=html_file, e=e))
    return names, scores

def process_data(file_list, dsu, excluded_names, lang_get):
    score_map = defaultdict(list)
    all_names = set()
    for html_file in file_list:
        names, _ = extract_table_content(html_file, lang_get)
        for name in names:
            if name not in excluded_names:
                all_names.add(name)
    
    for name in all_names: dsu.find(name)
    
    for html_file in file_list:
        names, scores = extract_table_content(html_file, lang_get)
        valid_scores = [score for name, score in zip(names, scores) if name not in excluded_names]
        max_score = max(valid_scores) if valid_scores else 0

        if max_score > 0:
            for name, score in zip(names, scores):
                if name not in excluded_names:
                    std_score = (score / max_score) * 100.0
                    root_name = dsu.find(name)
                    score_map[root_name].append(std_score)

    avg_scores = {name: sum(s) / len(s) for name, s in score_map.items()}
    return sorted(avg_scores.items(), key=lambda x: x[1], reverse=True)

# --- UI Application ---
class App(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.dsu = DSU()
        self.file_list = []
        self.all_names = set()
        self.excluded_names = set()
        self.rules = []
        self.current_lang = 'zh'
        
        # --- 现代化UI样式配置 ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam') # 'clam' 主题更易于定制

        # 全局背景和字体设置
        self.configure(bg='white')
        self.style.configure('.', background='white', foreground='black', font=("Helvetica", 10))

        # 框架和标签设置为白色背景
        self.style.configure("TFrame", background='white')
        self.style.configure("TLabel", background='white', foreground='black')
        self.style.configure("Header.TLabel", background='white', font=("Helvetica", 16, "bold"))
        self.style.configure("TLabelframe", background='white')
        self.style.configure("TLabelframe.Label", background='white', font=("Helvetica", 11, "bold"))
        
        # 现代化按钮样式
        self.style.configure("TButton", 
                             padding=6, 
                             relief="flat", 
                             font=("Helvetica", 10, "bold"),
                             background="#007AFF", 
                             foreground="white")
        self.style.map("TButton",
                       background=[('active', '#0056b3'), ('pressed', '#004494')])

        # 切换语言按钮的特殊样式 (稍暗)
        self.style.configure("Secondary.TButton", 
                             background="#dcdcdc", 
                             foreground="black")
        self.style.map("Secondary.TButton",
                       background=[('active', '#cccccc'), ('pressed', '#bcbcbc')])


        self.setup_ui()
        self.update_ui_text()

    def get_text(self, key):
        return LANGUAGES[self.current_lang].get(key, key)

    def setup_ui(self):
        # 使用白色背景的主框架
        self.main_frame = ttk.Frame(self, padding="10 10 10 0")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # --- 顶栏 (标题和语言切换按钮) ---
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        self.header_label = ttk.Label(top_frame, style="Header.TLabel")
        self.header_label.pack(side=tk.LEFT, pady=(0, 10))
        self.lang_button = ttk.Button(top_frame, command=self.toggle_language, style="Secondary.TButton")
        self.lang_button.pack(side=tk.RIGHT, pady=(0, 5))

        # --- 文件拖放区域 ---
        self.drop_label = tk.Label(self.main_frame, 
                                   relief=tk.SOLID, 
                                   borderwidth=1, 
                                   fg="#888888", 
                                   bg="#fafafa", # 使用淡灰色以示区分
                                   bd=1) 
        self.drop_label.pack(fill=tk.X, ipady=20, pady=5)
        self.drop_label.drop_target_register(DND_FILES)
        self.drop_label.dnd_bind('<<Drop>>', self.on_drop)

        # --- 管理区 (三列布局) ---
        management_frame = ttk.Frame(self.main_frame)
        management_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        management_frame.columnconfigure(0, weight=1)
        management_frame.columnconfigure(1, weight=1)
        management_frame.columnconfigure(2, weight=1)

        # 列 1: 已加载文件
        self.files_frame = ttk.Labelframe(management_frame, padding=5)
        self.files_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        self.file_listbox = tk.Listbox(self.files_frame, height=10, bg='white', relief='solid', bd=1, highlightthickness=0)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)

        # 列 2: 所有名字
        self.names_frame = ttk.Labelframe(management_frame, padding=5)
        self.names_frame.grid(row=0, column=1, sticky="nsew", padx=5)
        self.all_names_listbox = tk.Listbox(self.names_frame, selectmode=tk.EXTENDED, height=10, bg='white', relief='solid', bd=1, highlightthickness=0)
        self.all_names_listbox.pack(fill=tk.BOTH, expand=True)
        self.delete_name_button = ttk.Button(self.names_frame, command=self.delete_selected_names, style="Secondary.TButton")
        self.delete_name_button.pack(fill=tk.X, pady=(5, 0))

        # 列 3: 合并规则
        self.rules_frame = ttk.Labelframe(management_frame, padding=5)
        self.rules_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0))
        self.rule_listbox = tk.Listbox(self.rules_frame, height=10, bg='white', relief='solid', bd=1, highlightthickness=0)
        self.rule_listbox.pack(fill=tk.BOTH, expand=True)
        self.add_rule_button = ttk.Button(self.rules_frame, command=self.add_rule, style="Secondary.TButton")
        self.add_rule_button.pack(fill=tk.X, pady=(5,0))

        # --- 底部按钮区 ---
        bottom_button_frame = ttk.Frame(self.main_frame)
        bottom_button_frame.pack(fill=tk.X, pady=(10,0))
        self.save_rules_button = ttk.Button(bottom_button_frame, command=self.save_rules, style="Secondary.TButton")
        self.save_rules_button.pack(side=tk.LEFT, expand=True, padx=(0,5))
        self.load_rules_button = ttk.Button(bottom_button_frame, command=self.load_rules, style="Secondary.TButton")
        self.load_rules_button.pack(side=tk.LEFT, expand=True, padx=5)
        
        # "清空"和"处理"按钮，使用次要样式
        self.clear_button = ttk.Button(bottom_button_frame, command=self.clear_all, style="Secondary.TButton")
        self.clear_button.pack(side=tk.LEFT, expand=True, padx=5)
        self.process_button = ttk.Button(bottom_button_frame, command=self.run_processing)
        self.process_button.pack(side=tk.LEFT, expand=True, padx=(5,0))
        
        # --- 版权信息 ---
        self.copyright_label = ttk.Label(self.main_frame, anchor=tk.CENTER)
        self.copyright_label.pack(side=tk.BOTTOM, pady=(15, 5))
    def update_ui_text(self):
        self.title(self.get_text("title"))
        self.header_label.config(text=self.get_text("header"))
        self.lang_button.config(text=self.get_text("switch_lang"))
        self.drop_label.config(text=self.get_text("drop_files"))
        self.files_frame.config(text=self.get_text("loaded_files"))
        self.names_frame.config(text=self.get_text("all_names"))
        self.rules_frame.config(text=self.get_text("merging_rules"))
        self.delete_name_button.config(text=self.get_text("delete_name"))
        self.add_rule_button.config(text=self.get_text("add_rule"))
        self.save_rules_button.config(text=self.get_text("save_rules"))
        self.load_rules_button.config(text=self.get_text("load_rules"))
        self.process_button.config(text=self.get_text("process"))
        self.clear_button.config(text=self.get_text("clear_all"))
        self.copyright_label.config(text=self.get_text("copyright"))
    
    def toggle_language(self):
        self.current_lang = 'en' if self.current_lang == 'zh' else 'zh'
        self.update_ui_text()
        
    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        for f in files:
            if f.endswith(('.html', '.htm')) and f not in self.file_list:
                self.file_list.append(f)
                self.file_listbox.insert(tk.END, os.path.basename(f))
                names, _ = extract_table_content(f, self.get_text)
                new_names = set(names) - self.all_names
                for name in sorted(list(new_names)):
                    self.all_names_listbox.insert(tk.END, name)
                self.all_names.update(new_names)
    
    def delete_selected_names(self):
        selected_indices = self.all_names_listbox.curselection()
        for i in reversed(selected_indices):
            name_to_delete = self.all_names_listbox.get(i)
            self.excluded_names.add(name_to_delete)
            self.all_names_listbox.delete(i)

    def add_rule(self):
        rule = simpledialog.askstring(self.get_text("add_rule_prompt_title"), self.get_text("add_rule_prompt_text"))
        if rule and '=' in rule:
            alias, main_name = [x.strip() for x in rule.split('=')]
            if alias and main_name:
                self.rules.append((alias, main_name))
                self.rule_listbox.insert(tk.END, f"{alias} -> {main_name}")
                self.dsu.union(alias, main_name)

    def save_rules(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title=self.get_text("file_dialog_title"), initialfile="rules.json")
        if filepath:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.rules, f, indent=4)
            messagebox.showinfo(self.get_text("rules_saved_title"), self.get_text("rules_saved_text"))

    def load_rules(self):
        filepath = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], title=self.get_text("file_dialog_title"))
        if filepath:
            with open(filepath, 'r', encoding='utf-8') as f:
                loaded_rules = json.load(f)
            self.rules.clear()
            self.rule_listbox.delete(0, tk.END)
            self.dsu = DSU()
            for alias, main_name in loaded_rules:
                 self.rules.append((alias, main_name))
                 self.rule_listbox.insert(tk.END, f"{alias} -> {main_name}")
                 self.dsu.union(alias, main_name)
            messagebox.showinfo(self.get_text("rules_loaded_title"), self.get_text("rules_loaded_text"))

    def run_processing(self):
        if not self.file_list:
            messagebox.showwarning(self.get_text("no_files_warning_title"), self.get_text("no_files_warning_text"))
            return
        
        sorted_scores = process_data(self.file_list, self.dsu, self.excluded_names, self.get_text)
        self.show_results(sorted_scores)

    def show_results(self, sorted_scores):
        result_win = tk.Toplevel(self)
        result_win.title(self.get_text("results_title"))
        result_win.geometry("450x700") # Increased width for better display

        text_frame = ttk.Frame(result_win, padding=10)
        text_frame.pack(fill=tk.BOTH, expand=True)
        result_text = tk.Text(text_frame, wrap=tk.NONE, font=("Arial", 15)) # Use Courier New for consistent char width

        v_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=result_text.yview)
        h_scroll = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, command=result_text.xview)
        result_text['yscrollcommand'] = v_scroll.set
        result_text['xscrollcommand'] = h_scroll.set

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        result_text.pack(fill=tk.BOTH, expand=True)

        result_text.insert(tk.END, self.get_text("results_header"))

        # --- Helper function to calculate display width ---
        def get_display_length(text):
            length = 0
            for char in text:
                # Full-width characters (e.g., Chinese) occupy more space
                if '\u4e00' <= char <= '\u9fff':
                    length += 2
                else:
                    length += 1
            return length

        # --- Dynamic padding for alignment ---
        max_name_width = 0
        if sorted_scores:
            max_name_width = max(get_display_length(name) for name, _ in sorted_scores)
        for name, avg_score in sorted_scores:
            # Calculate padding needed to align all scores
            result_text.insert(tk.END, f"{name}\t\t{avg_score:>8.2f}\n")

        result_text.config(state=tk.DISABLED)

        def copy_to_clipboard():
            self.clipboard_clear()
            self.clipboard_append(result_text.get(1.0, tk.END))
            messagebox.showinfo(self.get_text("copied"), self.get_text("results_copied"))

        copy_button = ttk.Button(result_win, text=self.get_text("copy_to_clipboard"), command=copy_to_clipboard)
        copy_button.pack(pady=(0, 10))
        
    def clear_all(self):
        self.file_list.clear()
        self.all_names.clear()
        self.excluded_names.clear()
        self.rules.clear()
        self.file_listbox.delete(0, tk.END)
        self.all_names_listbox.delete(0, tk.END)
        self.rule_listbox.delete(0, tk.END)
        self.dsu = DSU()
        messagebox.showinfo(self.get_text("cleared_title"), self.get_text("cleared_text"))

if __name__ == '__main__':
    app = App()
    app.mainloop()
