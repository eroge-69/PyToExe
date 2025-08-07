import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import requests
import threading
from datetime import datetime

# 调试信息：打印当前目录和文件列表
print("当前目录：", os.getcwd())
print("目录下文件：", os.listdir('.'))

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
print("脚本所在目录：", script_dir)

# 自动检测QUERY_NAME文件
def safe_read_query_names():
    # 优先在脚本所在目录查找，其次在当前工作目录查找
    search_dirs = [script_dir, os.getcwd()]
    for search_dir in search_dirs:
        for fname in ["QUERY_NAME.xlsx", "QUERY_NAME.xls"]:
            file_path = os.path.join(search_dir, fname)
            if os.path.exists(file_path):
                print(f"找到文件：{file_path}")
                return read_query_names(file_path)
    messagebox.showerror("文件错误", f"未找到 QUERY_NAME.xlsx 或 QUERY_NAME.xls\n搜索目录：{search_dirs}")
    exit(1)

def read_query_names(xls_path):
    df = pd.read_excel(xls_path)
    # 自动适配字段名
    col = 'QUERY_NAME' if 'QUERY_NAME' in df.columns else 'name'
    # 按T子类分组
    grouped_data = {}
    for _, row in df.iterrows():
        t_subclass = row['T子类']
        if t_subclass not in grouped_data:
            grouped_data[t_subclass] = []
        grouped_data[t_subclass].append({
            'i_project': row['I项目'],
            'query_name': row[col]
        })
    return grouped_data

def read_fields(xlsx_path):
    # 优先在脚本所在目录查找，其次在当前工作目录查找
    search_dirs = [script_dir, os.getcwd()]
    for search_dir in search_dirs:
        file_path = os.path.join(search_dir, xlsx_path)
        if os.path.exists(file_path):
            print(f"找到保留字段文件：{file_path}")
            df = pd.read_excel(file_path)
            # 读取A列的所有非空值作为字段名
            fields = []
            for value in df.iloc[:, 0]:  # 读取第一列（A列）
                if pd.notna(value) and str(value).strip():  # 检查非空且非空字符串
                    fields.append(str(value).strip())
            print(f"读取到的字段：{fields}")
            return fields
    messagebox.showerror("文件错误", f"未找到 {xlsx_path}\n搜索目录：{search_dirs}")
    exit(1)

def read_login_info():
    """读取登录信息.xlsx文件"""
    try:
        # 优先在脚本所在目录查找，其次在当前工作目录查找
        search_dirs = [script_dir, os.getcwd()]
        for search_dir in search_dirs:
            file_path = os.path.join(search_dir, "登录信息.xlsx")
            if os.path.exists(file_path):
                print(f"找到登录信息文件：{file_path}")
                df = pd.read_excel(file_path)
                
                # 将数据转换为字典格式
                login_info = {}
                for _, row in df.iterrows():
                    field = row['字段']
                    value = row['值']
                    if pd.notna(field) and pd.notna(value):
                        login_info[str(field).strip()] = str(value).strip()
                
                print(f"读取到的登录信息：{login_info}")
                return login_info
        
        print("找不到登录信息.xlsx文件，将使用默认值")
        return {}
    except Exception as e:
        print(f"读取登录信息.xlsx文件失败: {str(e)}")
        return {}

# 获取单个QUERY_NAME数据
def fetch_data(query_name, system, system_pwd, user, note, method, page_size=1000):
    url = "http://172.16.5.152:33000/cmdb-web/cm-api/v1/common-api"
    all_data = []
    page = 1
    while True:
        req = {
            "SYSTEM": system,
            "SYSTEM_PWD": system_pwd,
            "USER": user,
            "NOTE": note,
            "METHOD": method,
            "TIMEOUT": 100,
            "DATA": {
                "CI_CONDITION": {
                    "QUERY_NAME": query_name.split('-')[-2] + "-RedisCache" if "-RedisCache" in query_name else query_name,
                    "page": page,
                    "pageNum": page_size,
                    "CUSTOM_QUERY_LIST": {}
                }
            }
        }
        try:
            resp = requests.post(url, json=req, timeout=100)
            if resp.status_code == 200:
                result = resp.json()
                if result.get("RETURN_CODE") == "00":
                    data = result.get("RETURN_DATA", [])
                    if not data:
                        break
                    all_data.extend(data)
                    if len(data) < page_size:
                        break
                    page += 1
                else:
                    break
            else:
                break
        except Exception as e:
            break
    return all_data

def get_i_project_by_query_name(query_name, grouped_data):
    """根据QUERY_NAME获取对应的I项目"""
    for t_subclass, items in grouped_data.items():
        for item in items:
            if item['query_name'] == query_name:
                return item['i_project']
    return None

def get_prefixed_fields(fields, i_project):
    """为字段名添加I项目前缀"""
    prefixed_fields = []
    for field in fields:
        prefixed_field = f"{i_project}_{field}"
        prefixed_fields.append(prefixed_field)
    return prefixed_fields

def remove_i_project_prefix(field_name, i_project):
    """去除字段名中的I项目前缀"""
    prefix = f"{i_project}_"
    if field_name.startswith(prefix):
        return field_name[len(prefix):]
    return field_name

def get_all_fields_from_data(data, i_project):
    """从数据中获取所有字段名（去除前缀）"""
    if not data:
        return []
    
    # 获取第一条数据的所有字段名
    all_fields = list(data[0].keys())
    
    # 去除I项目前缀
    cleaned_fields = []
    for field in all_fields:
        cleaned_field = remove_i_project_prefix(field, i_project)
        cleaned_fields.append(cleaned_field)
    
    return cleaned_fields

def get_all_fields_with_special_fields(data, i_project):
    """从数据中获取所有字段名（去除前缀），并添加T子类和I项目字段"""
    if not data:
        return []
    
    # 获取第一条数据的所有字段名
    all_fields = list(data[0].keys())
    
    # 去除I项目前缀
    cleaned_fields = []
    for field in all_fields:
        cleaned_field = remove_i_project_prefix(field, i_project)
        cleaned_fields.append(cleaned_field)
    
    # 添加T子类和I项目字段（如果不存在）
    if "T子类" not in cleaned_fields:
        cleaned_fields.append("T子类")
    if "I项目" not in cleaned_fields:
        cleaned_fields.append("I项目")
    
    return cleaned_fields

class CMDBApp:
    def __init__(self, root):
        self.root = root
        import tkinter as tk
        self.system_var = tk.StringVar()
        self.system_pwd_var = tk.StringVar()
        self.user_var = tk.StringVar()
        self.note_var = tk.StringVar()
        self.output_mode = tk.StringVar(value="sheet")
        self.main_log_text = None
        self.popup_log_text = None
        self.log_window = None
        self.grouped_query_names = safe_read_query_names()
        self.fields = read_fields("保留字段.xlsx")
        # 自动填充登录信息
        login_info = read_login_info()
        if login_info:
            self.system_var.set(login_info.get('system', ''))
            self.system_pwd_var.set(login_info.get('system_PWD', ''))
            self.user_var.set(login_info.get('user', ''))
            self.note_var.set(login_info.get('note', ''))
        self.create_widgets()

    def create_widgets(self):
        # 全局样式
        main_bg = "#f4f6fa"
        card_bg = "#ffffff"
        accent = "#2563eb"
        border = "#e0e7ef"
        title_font = ("微软雅黑", 20, "bold")
        subtitle_font = ("微软雅黑", 12, "bold")
        default_font = ("微软雅黑", 10)
        self.root.option_add("*Font", default_font)
        style = ttk.Style()
        style.configure("TFrame", background=main_bg)
        style.configure("TLabel", background=main_bg, font=default_font)
        style.configure("TButton", font=default_font, padding=6)
        style.configure("TLabelframe", background=card_bg, font=subtitle_font, borderwidth=0)
        style.configure("TLabelframe.Label", background=card_bg, font=subtitle_font)
        style.configure("Treeview", font=default_font, rowheight=24)
        style.configure("Treeview.Heading", font=subtitle_font)
        style.configure("TProgressbar", thickness=12)
        style.map("TButton", foreground=[('active', accent)], background=[('active', '#e6f0fa')])
        self.root.title("CMDB数据获取工具 v2.0")
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)
        self.root.configure(bg=main_bg)
        # 顶部横幅
        top_frame = ttk.Frame(self.root, style="TFrame")
        top_frame.pack(fill="x", pady=(0, 8))
        banner = ttk.Frame(top_frame, style="TFrame")
        banner.pack(fill="x", padx=0, pady=0)
        icon_label = ttk.Label(banner, text="🛡️", font=("微软雅黑", 22), background=main_bg)
        icon_label.pack(side="left", padx=(16, 8), pady=4)
        title_label = ttk.Label(banner, text="CMDB数据获取工具", font=title_font, background=main_bg, foreground=accent)
        title_label.pack(side="left", pady=4)
        subtitle_label = ttk.Label(banner, text="高效、智能、专业的CMDB批量数据导出助手", font=("微软雅黑", 10), background=main_bg, foreground="#64748b")
        subtitle_label.pack(side="left", padx=(12, 0), pady=4)
        version_label = ttk.Label(banner, text="v2.0", font=("微软雅黑", 9), background=main_bg, foreground="#94a3b8")
        version_label.pack(side="right", padx=(0, 16), pady=4)
        # 主内容区（左右三卡片）
        main_content = ttk.Frame(self.root, style="TFrame")
        main_content.pack(fill="both", expand=True, padx=12, pady=0)
        main_content.columnconfigure(0, weight=1)
        main_content.columnconfigure(1, weight=2)
        main_content.columnconfigure(2, weight=1)
        main_content.rowconfigure(0, weight=1)
        # 左：接口信息卡片
        api_card = ttk.Labelframe(main_content, text="接口用户信息", padding=12, style="TLabelframe")
        api_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)
        api_card.grid_columnconfigure(1, weight=1)
        ttk.Label(api_card, text="调用系统:", background=card_bg).grid(row=0, column=0, sticky="w", pady=2)
        system_entry = ttk.Entry(api_card, textvariable=self.system_var, width=12)
        system_entry.grid(row=0, column=1, sticky="ew", pady=2, padx=(4, 0))
        ttk.Label(api_card, text="密码:", background=card_bg).grid(row=1, column=0, sticky="w", pady=2)
        system_pwd_entry = ttk.Entry(api_card, textvariable=self.system_pwd_var, width=12, show="*")
        system_pwd_entry.grid(row=1, column=1, sticky="ew", pady=2, padx=(4, 0))
        ttk.Label(api_card, text="用户:", background=card_bg).grid(row=2, column=0, sticky="w", pady=2)
        user_entry = ttk.Entry(api_card, textvariable=self.user_var, width=12)
        user_entry.grid(row=2, column=1, sticky="ew", pady=2, padx=(4, 0))
        ttk.Label(api_card, text="调用原因:", background=card_bg).grid(row=3, column=0, sticky="w", pady=2)
        note_entry = ttk.Entry(api_card, textvariable=self.note_var, width=16)
        note_entry.grid(row=3, column=1, sticky="ew", pady=2, padx=(4, 0))
        api_help = ttk.Label(api_card, text="所有字段必填，自动读取登录信息.xlsx", background=card_bg, foreground="#22c55e", font=("微软雅黑", 9))
        api_help.grid(row=4, column=0, columnspan=2, sticky="w", pady=(6, 0))
        if self.system_var.get() and self.system_pwd_var.get() and self.user_var.get() and self.note_var.get():
            auto_fill_label = ttk.Label(api_card, text="已自动填充登录信息", background=card_bg, foreground=accent, font=("微软雅黑", 9))
            auto_fill_label.grid(row=5, column=0, columnspan=2, sticky="w", pady=(2, 0))
        # 中：QUERY_NAME卡片
        query_card = ttk.Labelframe(main_content, text="选择项目 (QUERY_NAME)", padding=12, style="TLabelframe")
        query_card.grid(row=0, column=1, sticky="nsew", padx=(0, 8), pady=0)
        query_card.grid_rowconfigure(2, weight=1)
        query_card.grid_columnconfigure(0, weight=1)
        search_frame = ttk.Frame(query_card, style="TFrame")
        search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        search_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(search_frame, text="搜索:", background=card_bg).grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_query_names)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        btn_frame = ttk.Frame(query_card, style="TFrame")
        btn_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        for i in range(4):
            btn_frame.grid_columnconfigure(i, weight=1)
        ttk.Button(btn_frame, text="全选", command=self.select_all_query_names).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(btn_frame, text="全不选", command=self.deselect_all_query_names).grid(row=0, column=1, padx=(0, 2))
        ttk.Button(btn_frame, text="选T子类", command=self.select_current_t_subclass).grid(row=0, column=2, padx=(0, 2))
        ttk.Button(btn_frame, text="选I项目", command=self.select_current_i_project).grid(row=0, column=3)
        tree_frame = ttk.Frame(query_card, style="TFrame")
        tree_frame.grid(row=2, column=0, sticky="nsew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.query_tree = ttk.Treeview(tree_frame, show="tree", selectmode="extended", height=10)
        self.query_tree.grid(row=0, column=0, sticky="nsew")
        query_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.query_tree.yview)
        query_scrollbar.grid(row=0, column=1, sticky="ns")
        self.query_tree.configure(yscrollcommand=query_scrollbar.set)
        self.populate_query_tree()
        # 右：字段选择卡片
        field_card = ttk.Labelframe(main_content, text="选择保留字段", padding=12, style="TLabelframe")
        field_card.grid(row=0, column=2, sticky="nsew", padx=(0, 0), pady=0)
        field_card.grid_rowconfigure(3, weight=1)
        field_card.grid_columnconfigure(0, weight=1)
        field_search_frame = ttk.Frame(field_card, style="TFrame")
        field_search_frame.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        field_search_frame.grid_columnconfigure(1, weight=1)
        ttk.Label(field_search_frame, text="搜索:", background=card_bg).grid(row=0, column=0, sticky="w")
        self.field_search_var = tk.StringVar()
        self.field_search_var.trace('w', self.filter_fields)
        field_search_entry = ttk.Entry(field_search_frame, textvariable=self.field_search_var)
        field_search_entry.grid(row=0, column=1, sticky="ew", padx=(4, 0))
        field_btn_frame = ttk.Frame(field_card, style="TFrame")
        field_btn_frame.grid(row=1, column=0, sticky="ew", pady=(0, 4))
        field_btn_frame.grid_columnconfigure(0, weight=1)
        field_btn_frame.grid_columnconfigure(1, weight=1)
        ttk.Button(field_btn_frame, text="全选", command=self.select_all_fields).grid(row=0, column=0, padx=(0, 2))
        ttk.Button(field_btn_frame, text="全不选", command=self.deselect_all_fields).grid(row=0, column=1)
        list_frame = ttk.Frame(field_card, style="TFrame")
        list_frame.grid(row=3, column=0, sticky="nsew")
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)
        self.field_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, height=10, font=default_font)
        self.field_listbox.grid(row=0, column=0, sticky="nsew")
        field_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.field_listbox.yview)
        field_scrollbar.grid(row=0, column=1, sticky="ns")
        self.field_listbox.configure(yscrollcommand=field_scrollbar.set)
        self.populate_field_list()
        # 底部横栏
        bottom_frame = ttk.Frame(self.root, style="TFrame")
        bottom_frame.pack(fill="x", padx=12, pady=(8, 4))
        output_card = ttk.Labelframe(bottom_frame, text="输出方式", padding=8, style="TLabelframe")
        output_card.pack(fill="x", pady=(0, 4))
        ttk.Radiobutton(output_card, text="每I项目单独sheet", variable=self.output_mode, value="sheet").pack(side="left", padx=6)
        ttk.Radiobutton(output_card, text="全部合并到一个sheet", variable=self.output_mode, value="merge").pack(side="left", padx=6)
        output_help = ttk.Label(output_card, text="未选择保留字段时，合并模式下会智能去重字段名后保存", foreground="#22c55e", font=("微软雅黑", 9), background=card_bg)
        output_help.pack(side="left", padx=10)
        control_frame = ttk.Frame(bottom_frame, style="TFrame")
        control_frame.pack(fill="x", pady=(0, 2))
        btn_frame = ttk.Frame(control_frame, style="TFrame")
        btn_frame.pack(pady=2)
        self.start_btn = ttk.Button(btn_frame, text="开始获取数据", command=self.start_fetch)
        self.start_btn.pack(side="left", padx=(0, 6))
        help_btn = ttk.Button(btn_frame, text="详细帮助", command=self.show_help)
        help_btn.pack(side="left", padx=(0, 6))
        about_btn = ttk.Button(btn_frame, text="关于", command=self.show_about)
        about_btn.pack(side="left")
        progress_frame = ttk.Frame(control_frame, style="TFrame")
        progress_frame.pack(fill="x", pady=(0, 1))
        self.progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate", length=350)
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(side="right")
        # 主界面实时日志区（卡片式，底部，始终可见）
        main_log_card = ttk.Labelframe(self.root, text="实时日志", padding=6, style="TLabelframe")
        main_log_card.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.main_log_text = scrolledtext.ScrolledText(main_log_card, height=6, wrap=tk.WORD, font=("Consolas", 9))
        self.main_log_text.pack(fill="both", expand=True)
        log_btn_frame = ttk.Frame(main_log_card, style="TFrame")
        log_btn_frame.pack(fill="x", pady=(2, 0))
        clear_log_btn = ttk.Button(log_btn_frame, text="清空日志", command=self.clear_log)
        clear_log_btn.pack(side="left", padx=(0, 6))
        copy_log_btn = ttk.Button(log_btn_frame, text="复制日志", command=self.copy_log)
        copy_log_btn.pack(side="left")
        # 日志区弹窗（可折叠/弹窗）
        # self.log_window = None # This line is moved up

    def log_message(self, message):
        """添加日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        if self.main_log_text:
            self.main_log_text.insert("end", log_entry)
            self.main_log_text.see("end")
        if self.popup_log_text:
            self.popup_log_text.insert("end", log_entry)
            self.popup_log_text.see("end")
        self.root.update_idletasks()

    def on_tree_click(self, event):
        """处理树形控件的点击事件"""
        region = self.query_tree.identify_region(event.x, event.y)
        if region == "cell":
            item = self.query_tree.identify_row(event.y)
            if item:
                # 检查是否是I项目节点（有父节点）
                if self.query_tree.parent(item) != "":
                    # 切换选中状态
                    if item in self.query_tree.selection():
                        self.query_tree.selection_remove(item)
                    else:
                        self.query_tree.selection_add(item)
                    return "break"
                # 点击T子类节点时，切换其下所有I项目的选中状态
                else:
                    children = self.query_tree.get_children(item)
                    if children:
                        # 检查是否所有子节点都被选中
                        all_selected = all(child in self.query_tree.selection() for child in children)
                        if all_selected:
                            # 如果全部选中，则全部取消
                            for child in children:
                                self.query_tree.selection_remove(child)
                        else:
                            # 否则全部选中
                            for child in children:
                                self.query_tree.selection_add(child)
                    return "break"
        return None

    def populate_query_tree(self):
        """填充QUERY_NAME树形结构"""
        self.query_tree.delete(*self.query_tree.get_children())
        for t_subclass, items in self.grouped_query_names.items():
            # 插入T子类节点
            t_subclass_id = self.query_tree.insert("", "end", text=t_subclass, tags=("t_subclass",))
            # 插入I项目节点（只显示I项目名称，QUERY_NAME存储在values中）
            for item in items:
                self.query_tree.insert(t_subclass_id, "end", text=item['i_project'], 
                                     values=(item['query_name'],), tags=("i_project",))

    def populate_field_list(self):
        """填充字段列表"""
        self.field_listbox.delete(0, tk.END)
        for field in self.fields:
            self.field_listbox.insert(tk.END, field)

    def filter_query_names(self, *args):
        """根据搜索条件过滤QUERY_NAME"""
        search_text = self.search_var.get().lower()
        self.query_tree.delete(*self.query_tree.get_children())
        
        for t_subclass, items in self.grouped_query_names.items():
            # 检查T子类是否匹配
            if search_text in t_subclass.lower():
                t_subclass_id = self.query_tree.insert("", "end", text=t_subclass, tags=("t_subclass",))
                for item in items:
                    self.query_tree.insert(t_subclass_id, "end", text=item['i_project'], 
                                         values=(item['query_name'],), tags=("i_project",))
            else:
                # 检查I项目是否匹配（只搜索I项目名称，不搜索QUERY_NAME）
                matching_items = [item for item in items if search_text in item['i_project'].lower()]
                if matching_items:
                    t_subclass_id = self.query_tree.insert("", "end", text=t_subclass, tags=("t_subclass",))
                    for item in matching_items:
                        self.query_tree.insert(t_subclass_id, "end", text=item['i_project'], 
                                             values=(item['query_name'],), tags=("i_project",))

    def filter_fields(self, *args):
        """根据搜索条件过滤字段"""
        search_text = self.field_search_var.get().lower()
        self.field_listbox.delete(0, tk.END)
        for field in self.fields:
            if search_text in field.lower():
                self.field_listbox.insert(tk.END, field)

    def select_all_query_names(self):
        """选择所有QUERY_NAME"""
        for item in self.query_tree.get_children():
            for child in self.query_tree.get_children(item):
                self.query_tree.selection_add(child)

    def deselect_all_query_names(self):
        """取消选择所有QUERY_NAME"""
        self.query_tree.selection_remove(self.query_tree.selection())

    def select_current_t_subclass(self):
        """选择当前T子类的所有I项目"""
        selected = self.query_tree.selection()
        for item in selected:
            if self.query_tree.parent(item) == "":  # T子类节点
                for child in self.query_tree.get_children(item):
                    self.query_tree.selection_add(child)

    def select_current_i_project(self):
        """选择当前I项目"""
        selected = self.query_tree.selection()
        for item in selected:
            if self.query_tree.parent(item) != "":  # I项目节点
                self.query_tree.selection_add(item)

    def select_all_fields(self):
        """选择所有字段"""
        self.field_listbox.selection_set(0, tk.END)

    def deselect_all_fields(self):
        """取消选择所有字段"""
        self.field_listbox.selection_clear(0, tk.END)

    def show_help(self):
        """显示详细帮助信息"""
        help_text = """
📋 CMDB数据获取工具使用说明

🔹 基本操作流程：
1. 确认接口用户信息（程序启动时自动填充）
2. 选择需要获取的QUERY_NAME（可多选）
3. 选择要保留的字段（可选，不选择则使用所有字段）
4. 选择输出方式（分sheet或合并）
5. 点击"开始获取数据"

🔹 QUERY_NAME选择：
• 点击I项目名称：选中对应的QUERY_NAME（无需显示QUERY_NAME名称）
• 点击T子类：全选/取消其下所有I项目
• 使用搜索框快速查找I项目
• 支持批量操作按钮

🔹 保留字段选择：
• 不选择字段：自动使用所有接口返回字段
• 选择字段：只保留指定的字段
• 自动去除I项目前缀（如：PC服务器_配置项ID → 配置项ID）
• 始终包含T子类和I项目字段

🔹 输出方式：
• 每I项目单独sheet：每个I项目创建一个工作表
• 全部合并到一个sheet：所有数据合并到一个工作表
• 合并模式智能去重：多次出现的字段去除前缀，单次出现的保留完整名称

🔹 字段排序：
• 优先按照"保留字段"列表的顺序排列
• 未在列表中的字段按字母顺序排列

🔹 接口用户信息：
• 调用系统：接口调用的系统名称
• 密码：接口访问密码
• 用户：调用接口的用户名
• 调用原因：接口调用的用途说明
• 所有字段都必须填写才能调用接口
• 程序启动时会自动读取"登录信息.xlsx"文件并填充默认值

🔹 注意事项：
• 确保网络连接正常
• 确保QUERY_NAME.xlsx和保留字段.xlsx文件存在
• 大量数据获取可能需要较长时间
• 建议先选择少量数据测试

🔹 日志信息：
• 实时显示处理进度
• 显示字段映射和去重信息
• 显示数据获取统计
        """
        messagebox.showinfo("详细帮助", help_text)

    def clear_log(self):
        """清空日志"""
        if self.main_log_text:
            self.main_log_text.delete("1.0", "end")
        if self.popup_log_text:
            self.popup_log_text.delete("1.0", "end")
        self.log_message("🗑️ 日志已清空")

    def copy_log(self):
        """复制日志内容"""
        try:
            log_content = ""
            if self.popup_log_text:
                log_content = self.popup_log_text.get("1.0", "end")
            elif self.main_log_text:
                log_content = self.main_log_text.get("1.0", "end")
            self.root.clipboard_clear()
            self.root.clipboard_append(log_content)
            from tkinter import messagebox
            messagebox.showinfo("复制成功", "日志内容已复制到剪贴板")
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("复制失败", f"复制日志内容时出错：{str(e)}")

    def show_about(self):
        """显示关于信息"""
        about_text = """
🔧 CMDB数据获取工具 v2.0

📋 功能特性：
• 支持多QUERY_NAME数据获取
• 智能字段去重和前缀处理
• 灵活的字段选择机制
• 多种输出格式支持
• 实时处理日志显示

🛠️ 技术特点：
• 基于Python tkinter开发
• 支持Excel文件输出
• 智能字段映射处理
• 友好的用户界面

📞 使用说明：
点击"详细帮助"按钮查看完整使用说明

🎯 适用场景：
• CMDB数据批量获取
• 配置项信息导出
• 数据分析和报表生成
        """
        messagebox.showinfo("关于", about_text)

    def refresh_query_tree(self):
        """刷新QUERY_NAME树"""
        try:
            self.grouped_query_names = safe_read_query_names()
            self.populate_query_tree()
            self.log_message("🔄 QUERY_NAME列表已刷新")
        except Exception as e:
            self.log_message(f"❌ 刷新QUERY_NAME列表失败: {str(e)}")
            messagebox.showerror("刷新失败", f"刷新QUERY_NAME列表时出错：{str(e)}")

    def get_selected_query_names(self):
        """获取选中的QUERY_NAME列表"""
        selected_query_names = []
        for item in self.query_tree.selection():
            if self.query_tree.parent(item) != "":  # I项目节点
                values = self.query_tree.item(item, "values")
                if values:
                    selected_query_names.append(values[0])
        return selected_query_names

    def start_fetch(self):
        # 验证接口用户信息
        system = self.system_var.get().strip()
        system_pwd = self.system_pwd_var.get().strip()
        user = self.user_var.get().strip()
        note = self.note_var.get().strip()
        
        if not system or not system_pwd or not user or not note:
            messagebox.showwarning("提示", "请填写完整的接口用户信息：\n• 调用系统\n• 密码\n• 用户\n• 调用原因")
            return
        
        self.selected_query_names = self.get_selected_query_names()
        self.selected_fields = [self.fields[i] for i in self.field_listbox.curselection()]
        
        if not self.selected_query_names:
            messagebox.showwarning("提示", "请至少选择一个QUERY_NAME")
            return
            
        # 如果未选择保留字段，则使用所有字段（需要去除前缀）
        if not self.selected_fields:
            self.log_message("未选择保留字段，将使用所有接口返回字段（去除I项目前缀）")
            self.selected_fields = []  # 空列表表示使用所有字段
            
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel文件", "*.xlsx")])
        if not save_path:
            return
            
        # 清空日志
        if self.main_log_text:
            self.main_log_text.delete("1.0", "end")
        if self.popup_log_text:
            self.popup_log_text.delete("1.0", "end")
        self.log_message("🚀 开始数据获取任务...")
        self.log_message(f"🔐 接口用户信息: {user}@{system}")
        self.log_message(f"📋 选择的QUERY_NAME数量: {len(self.selected_query_names)}")
        if self.selected_fields:
            self.log_message(f"🔧 选择的保留字段数量: {len(self.selected_fields)}")
        else:
            self.log_message("🔧 选择的保留字段: 无（将使用所有接口返回字段，自动去除I项目前缀）")
        self.log_message(f"📊 输出方式: {'每I项目单独sheet' if self.output_mode.get() == 'sheet' else '全部合并到一个sheet'}")
        self.log_message(f"💾 保存路径: {save_path}")
        self.log_message("=" * 60)
            
        self.start_btn.config(state="disabled")
        # 传递接口用户信息给fetch_and_save方法
        threading.Thread(target=self.fetch_and_save, args=(save_path, system, system_pwd, user, note)).start()

    def fetch_and_save(self, save_path, system, system_pwd, user, note):
        method = "configClassAction_customQuery-PC-RedisCache"
        # 重置进度条
        self.progress["value"] = 0
        self.progress["maximum"] = 100
        self.progress_label.config(text="0%")
        
        self.log_message("开始连接CMDB接口...")
        
        # 先获取所有数据的基本信息
        for idx, query_name in enumerate(self.selected_query_names):
            self.log_message(f"正在获取第 {idx+1}/{len(self.selected_query_names)} 个QUERY_NAME: {query_name}")
            data = fetch_data(query_name, system, system_pwd, user, note, method)
            self.log_message(f"  → 获取到 {len(data)} 条数据")
            
            if data:
                # 显示第一条数据的字段名，用于调试
                first_item = data[0]
                self.log_message(f"  → 接口返回的字段名示例: {list(first_item.keys())[:10]}...")
            
            # 获取对应的I项目
            i_project = get_i_project_by_query_name(query_name, self.grouped_query_names)
            if i_project:
                self.log_message(f"  → 对应I项目: {i_project}")
            else:
                self.log_message(f"  → 警告: 未找到QUERY_NAME对应的I项目")
            
            # 更新进度条和百分比
            progress_value = (idx + 1) / len(self.selected_query_names) * 100
            self.progress["value"] = progress_value
            self.progress_label.config(text=f"{progress_value:.1f}%")
            self.root.update_idletasks()
            
        self.log_message("数据获取完成，开始处理数据...")
        self.log_message("开始保存Excel文件...")
        
        if self.output_mode.get() == "sheet":
            # 按I项目分sheet
            writer = pd.ExcelWriter(save_path, engine="openpyxl")
            sheet_count = 0
            
            # 按I项目分组数据
            i_project_data = {}
            for query_name in self.selected_query_names:
                i_project = get_i_project_by_query_name(query_name, self.grouped_query_names)
                if i_project:
                    if i_project not in i_project_data:
                        i_project_data[i_project] = []
                    
                    # 获取该QUERY_NAME对应的数据
                    data = fetch_data(query_name, system, system_pwd, user, note, method)
                    if data:
                        # 确定要处理的字段
                        if self.selected_fields:
                            # 使用用户选择的字段
                            fields_to_process = self.selected_fields
                        else:
                            # 使用所有字段（去除前缀），并添加T子类和I项目字段
                            all_fields = get_all_fields_with_special_fields(data, i_project)
                            # 按照预定义字段的顺序排序
                            if self.fields:
                                ordered_fields = []
                                # 先添加预定义字段中存在的字段
                                for field in self.fields:
                                    if field in all_fields:
                                        ordered_fields.append(field)
                                # 再添加其他字段
                                for field in all_fields:
                                    if field not in ordered_fields:
                                        ordered_fields.append(field)
                                fields_to_process = ordered_fields
                            else:
                                fields_to_process = all_fields
                            self.log_message(f"  → 使用所有字段: {len(fields_to_process)} 个")
                        
                        # 处理数据
                        processed_data = []
                        for d in data:
                            processed_item = {}
                            for field in fields_to_process:
                                # 特殊处理T子类和I项目字段
                                if field == "T子类":
                                    # 从grouped_data中获取对应的T子类
                                    t_subclass = None
                                    for t_sub, items in self.grouped_query_names.items():
                                        for item in items:
                                            if item['query_name'] == query_name:
                                                t_subclass = t_sub
                                                break
                                        if t_subclass:
                                            break
                                    processed_item[field] = t_subclass if t_subclass else ""
                                elif field == "I项目":
                                    # 直接使用当前I项目
                                    processed_item[field] = i_project
                                else:
                                    # 其他字段正常处理
                                    prefixed_field = f"{i_project}_{field}"
                                    if prefixed_field in d:
                                        processed_item[field] = d[prefixed_field]
                                    else:
                                        processed_item[field] = ""
                            processed_data.append(processed_item)
                        
                        i_project_data[i_project].extend(processed_data)
                        self.log_message(f"  → {i_project}: 添加 {len(processed_data)} 条数据")
            
            # 为每个I项目创建sheet
            for i_project, sheet_data in i_project_data.items():
                if sheet_data:
                    sheet_name = str(i_project)[:31]  # Excel sheet名称限制31字符
                    sheet_df = pd.DataFrame(sheet_data)
                    sheet_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    sheet_count += 1
                    self.log_message(f"  → 创建sheet: {sheet_name} ({len(sheet_data)} 条数据)")
            
            writer.close()
            self.log_message(f"Excel文件保存完成，共创建 {sheet_count} 个sheet")
        else:
            # 合并模式：需要处理字段去重
            if not self.selected_fields:
                # 未选择字段时，需要收集所有字段并去重
                self.log_message("合并模式：收集所有字段并智能去重...")
                
                # 收集所有字段及其出现次数
                field_count = {}
                field_mapping = {}  # 存储字段名到最终字段名的映射
                
                # 第一遍：收集所有字段及其出现次数
                for query_name in self.selected_query_names:
                    i_project = get_i_project_by_query_name(query_name, self.grouped_query_names)
                    if i_project:
                        data = fetch_data(query_name, system, system_pwd, user, note, method)
                        if data:
                            # 获取原始字段名和去除前缀后的字段名
                            original_fields = list(data[0].keys())
                            for original_field in original_fields:
                                cleaned_field = remove_i_project_prefix(original_field, i_project)
                                
                                # 统计出现次数
                                if cleaned_field in field_count:
                                    field_count[cleaned_field] += 1
                                    # 如果出现多次，使用去除前缀的字段名
                                    field_mapping[cleaned_field] = cleaned_field
                                else:
                                    field_count[cleaned_field] = 1
                                    # 如果只出现一次，保留原始字段名
                                    field_mapping[cleaned_field] = original_field
                            
                            self.log_message(f"  → {i_project}: 收集到 {len(original_fields)} 个字段")
                
                # 添加T子类和I项目字段
                if "T子类" not in field_mapping:
                    field_mapping["T子类"] = "T子类"
                if "I项目" not in field_mapping:
                    field_mapping["I项目"] = "I项目"
                
                # 转换为有序列表，优先按照选择保留字段的顺序排序
                if self.fields:  # 如果有预定义的字段列表
                    # 按照预定义字段的顺序排序
                    ordered_fields = []
                    # 先添加预定义字段中存在的字段
                    for field in self.fields:
                        if field in field_mapping:
                            ordered_fields.append(field)
                    # 再添加其他字段
                    for field in sorted(field_mapping.keys()):
                        if field not in ordered_fields:
                            ordered_fields.append(field)
                    all_fields_list = ordered_fields
                else:
                    all_fields_list = sorted(list(field_mapping.keys()))
                self.log_message(f"合并模式：智能去重后共有 {len(all_fields_list)} 个字段")
                
                # 显示字段映射信息
                for field in all_fields_list:
                    final_name = field_mapping[field]
                    count = field_count.get(field, 1)
                    if count == 1:
                        self.log_message(f"    → {field} (出现1次): 保留完整名称 '{final_name}'")
                    else:
                        self.log_message(f"    → {field} (出现{count}次): 使用简化名称 '{final_name}'")
                
                # 保存字段映射供后续使用
                self.field_mapping = field_mapping
            
            # 处理数据
            merged_data = []
            for query_name in self.selected_query_names:
                i_project = get_i_project_by_query_name(query_name, self.grouped_query_names)
                if i_project:
                    # 重新获取数据
                    data = fetch_data(query_name, system, system_pwd, user, note, method)
                    if data:
                        # 确定要处理的字段
                        if self.selected_fields:
                            # 使用用户选择的字段
                            fields_to_process = self.selected_fields
                        else:
                            # 使用去重后的所有字段
                            fields_to_process = all_fields_list
                        
                        # 处理数据
                        processed_data = []
                        for d in data:
                            processed_item = {}
                            for field in fields_to_process:
                                # 特殊处理T子类和I项目字段
                                if field == "T子类":
                                    # 从grouped_data中获取对应的T子类
                                    t_subclass = None
                                    for t_sub, items in self.grouped_query_names.items():
                                        for item in items:
                                            if item['query_name'] == query_name:
                                                t_subclass = t_sub
                                                break
                                        if t_subclass:
                                            break
                                    processed_item[field] = t_subclass if t_subclass else ""
                                elif field == "I项目":
                                    # 直接使用当前I项目
                                    processed_item[field] = i_project
                                else:
                                    # 其他字段处理
                                    if self.selected_fields:
                                        # 用户选择字段模式：使用前缀查找
                                        prefixed_field = f"{i_project}_{field}"
                                        if prefixed_field in d:
                                            processed_item[field] = d[prefixed_field]
                                        else:
                                            processed_item[field] = ""
                                    else:
                                        # 智能去重模式：使用字段映射
                                        final_field_name = self.field_mapping[field]
                                        if final_field_name == field:
                                            # 简化名称：需要添加前缀查找
                                            prefixed_field = f"{i_project}_{field}"
                                            if prefixed_field in d:
                                                processed_item[final_field_name] = d[prefixed_field]
                                            else:
                                                processed_item[final_field_name] = ""
                                        else:
                                            # 完整名称：直接查找
                                            if final_field_name in d:
                                                processed_item[final_field_name] = d[final_field_name]
                                            else:
                                                processed_item[final_field_name] = ""
                            processed_data.append(processed_item)
                        
                        merged_data.extend(processed_data)
                        self.log_message(f"  → {i_project}: 添加 {len(processed_data)} 条数据")
            
            if merged_data:
                df = pd.DataFrame(merged_data)
                df.to_excel(save_path, index=False)
                self.log_message(f"Excel文件保存完成，共 {len(df)} 条数据")
            else:
                self.log_message("警告: 没有数据可保存！")
            
        self.log_message("✅ 任务完成！")
        self.log_message("🎉 数据获取和处理已成功完成！")
        self.start_btn.config(state="normal")
        messagebox.showinfo("🎉 完成", f"数据已成功保存到：\n{save_path}\n\n请检查输出文件确认数据完整性。")

if __name__ == "__main__":
    root = tk.Tk()
    app = CMDBApp(root)
    root.mainloop()