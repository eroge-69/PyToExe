import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import serial
import serial.tools.list_ports
import threading
import time
import re
import datetime
from tkinter import simpledialog
import queue
class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry("400x250+{}+{}".format(
            int(self.winfo_screenwidth()/2-200),
            int(self.winfo_screenheight()/2-125)))
        self.configure(bg='#4a7a8c')
        label = tk.Label(self, text="4G IoT\n載入中...", font=("Microsoft JhengHei", 18, "bold"), fg="white", bg="#4a7a8c")
        label.pack(expand=True)
        self.update()

class IoTDeviceConfigTool:
    def __init__(self, root):
        self.serial_queue = queue.Queue()
        self.root = root
        self.root.title("4G IoT")
        self.root.geometry("1080x700")
        self.root.minsize(900, 600)
        
        # 設置現代化主題
        self.style = ttk.Style()
        self.style.theme_use('clam')  # 必须使用 'clam' 主题才能自定义样式
        self.style.configure("CellBorders.Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white",
            font=('Microsoft JhengHei', 9),
            bordercolor="#cccccc",
            borderwidth=1,
            relief="solid")

        # 每一列加框（自訂 layout）
        self.style.layout("CellBorders.Treeview.Item", [
            ('Treeitem.padding', {'sticky': 'nswe', 'children': [
                ('Treeitem.indicator', {'side': 'left', 'sticky': ''}),
                ('Treeitem.image', {'side': 'left', 'sticky': ''}),
                ('Treeitem.text', {'side': 'left', 'sticky': ''})
            ]})
        ])
        # 储存格边框样式
        self.style.element_create("Treeitem.border", "from", "clam")
        self.style.layout("CellBorders.Treeview.Item", [
            ('Treeitem.border', {'sticky': 'nswe', 'children': [
                ('Treeitem.padding', {'sticky': 'nswe', 'children': [
                    ('Treeitem.image', {'side': 'right', 'sticky': ''}),
                    ('Treeitem.text', {'sticky': 'we'})
                ]})
            ]})
        ])
        
        # 表头样式
        self.style.configure("CellBorders.Treeview.Heading",
            background="#f8f8f8",
            foreground="black",
            padding=(5, 5),
            font=('Microsoft JhengHei', 10, 'bold'),
            bordercolor="#a5a5a5",
            borderwidth=1,
            relief="solid")
        
        # 选中行样式
        self.style.map("CellBorders.Treeview",
            background=[("selected", "#e2f0ff")],
            foreground=[("selected", "black")])

        
        # 自定義樣式
        self.style.configure('Bordered.TLabelframe', borderwidth=2, relief='groove')
        self.style.configure('Bordered.Treeview', borderwidth=1, relief='solid')

        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Microsoft JhengHei', 10))
        self.style.configure('TButton', font=('Microsoft JhengHei', 10), padding=5)
        self.style.configure('TEntry', padding=5)
        self.style.configure('TCombobox', padding=5)
        self.style.configure('Treeview', font=('Microsoft JhengHei', 9))
        self.style.configure('Treeview.Heading', font=('Microsoft JhengHei', 10, 'bold'))
        self.style.map('TButton', 
                      foreground=[('active', 'black'), ('!active', 'black')],
                      background=[('active', '#e6e6e6'), ('!active', '#f0f0f0')])
        
        # 主色調
        self.primary_color = '#4a7a8c'
        self.secondary_color = '#6c9eb8'
        self.accent_color = "#416ad9"

        # 端口相關變量
        self.ser = None
        self.serial_thread = None
        self.stop_event = threading.Event()
        self.current_section = None
        
        # 換行符選項
        self.use_nl = tk.BooleanVar(value=True)  # \n 換行符
        self.use_cr = tk.BooleanVar(value=False)  # \r 換行符
        
        # 創建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 創建左側導航框架
        self.left_frame = ttk.LabelFrame(self.main_frame, text="功能選單", width=180, style='Bordered.TLabelframe')
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # 創建右側內容框架
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 創建端口設置框架
        self.serial_frame = ttk.LabelFrame(self.right_frame, text="端口設置", style='Bordered.TLabelframe')
        self.serial_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 創建動態內容框架
        self.content_frame = ttk.Frame(self.right_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 創建接收區域框架
        self.receive_frame = ttk.LabelFrame(self.right_frame, text="數據通信", style='Bordered.TLabelframe')

        self.receive_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # 創建狀態欄
        self.status_bar = ttk.Label(self.root, text="就緒", relief=tk.SUNKEN, anchor=tk.W, padding=(5, 2))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 初始化UI
        self.init_serial_frame()
        self.init_navigation()
        self.init_receive_frame()
        
        # 初始顯示SIM卡設置
        self.current_section = "SIM卡設定"
        self.show_sim_settings()
        self.setup_treeview_style()


    def setup_treeview_style(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("CellBorders.Treeview",
            background="white",
            foreground="black",
            rowheight=25,
            fieldbackground="white",
            bordercolor="#cccccc",
            borderwidth=1,
            relief="solid")
        style.configure("CellBorders.Treeview.Heading",
            font=("Microsoft JhengHei", 10, "bold"),
            relief="solid",
            borderwidth=1)
        style.map("CellBorders.Treeview",
            background=[("selected", "#cce5ff")])
        

    def init_serial_frame(self):
        """初始化端口设置界面（顶部水平排列）"""
        # 创建顶部容器（放在root下，main_frame上方）
        self.top_frame = ttk.Frame(self.root)
        self.top_frame.pack(fill=tk.X, pady=(5,0), padx=10, before=self.main_frame)
        
        # 端口设置标签框架
        self.serial_frame = ttk.LabelFrame(self.top_frame, text="端口设置",style='Bordered.TLabelframe')
        self.serial_frame.pack(fill=tk.X, padx=0, pady=0)
        
        # 主水平布局容器
        serial_container = ttk.Frame(self.serial_frame)
        serial_container.pack(fill=tk.X, padx=5, pady=3)
        
        # 端口选择
        ttk.Label(serial_container, text="端口:").pack(side=tk.LEFT, padx=(0,5))
        self.port_combo = ttk.Combobox(serial_container, values=self.get_serial_ports(), width=14)
        self.port_combo.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        ttk.Button(serial_container, text="↻", width=3, 
                command=self.refresh_serial_ports).pack(side=tk.LEFT, padx=5)
        
        # 波特率
        ttk.Label(serial_container, text="波特率:").pack(side=tk.LEFT, padx=(10,5))
        self.baudrate_combo = ttk.Combobox(serial_container, values=["9600", "19200", "38400", "57600", "115200"], width=8)
        self.baudrate_combo.set("115200")
        self.baudrate_combo.pack(side=tk.LEFT, padx=5)
        
        # 数据位
        ttk.Label(serial_container, text="數據位:").pack(side=tk.LEFT, padx=(10,5))
        self.data_var = tk.StringVar(value="8")
        self.data_combobox = ttk.Combobox(serial_container, textvariable=self.data_var, 
                                        values=["5", "6", "7", "8"], width=4)
        self.data_combobox.pack(side=tk.LEFT, padx=5)
        
        # 停止位
        ttk.Label(serial_container, text="停止位:").pack(side=tk.LEFT, padx=(10,5))
        self.stop_var = tk.StringVar(value="1")
        self.stop_combobox = ttk.Combobox(serial_container, textvariable=self.stop_var, 
                                        values=["1", "1.5", "2"], width=4)
        self.stop_combobox.pack(side=tk.LEFT, padx=5)
        
        # 校验位
        ttk.Label(serial_container, text="奇偶校驗:").pack(side=tk.LEFT, padx=(10,5))
        self.parity_var = tk.StringVar(value="None")
        self.parity_combobox = ttk.Combobox(serial_container, textvariable=self.parity_var,
                                        values=["None", "Even", "Odd", "Mark", "Space"],
                                        width=8)
        self.parity_combobox.pack(side=tk.LEFT, padx=5)
        
        # 換行符设置
        ttk.Label(serial_container, text="換行符:").pack(side=tk.LEFT, padx=(10,5))
        self.use_nl = tk.BooleanVar(value=True)
        self.use_cr = tk.BooleanVar(value=False)
        ttk.Checkbutton(serial_container, text="\\n", variable=self.use_nl).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(serial_container, text="\\r", variable=self.use_cr).pack(side=tk.LEFT, padx=2)
        
        # 連接按钮（右侧对齐）
        self.connect_button = ttk.Button(serial_container, text="連接", width=8,
                                    command=self.toggle_connection, style='Accent.TButton')
        self.connect_button.pack(side=tk.RIGHT, padx=(10,0))
        
        # 确保刷新端口列表
        self.refresh_serial_ports()
    
    def init_navigation(self):
        """初始化導航按鈕"""
        # 建立樣式
        self.style.configure('Nav.TButton', font=('Microsoft JhengHei', 10), width=18)
        self.style.configure('SelectedNav.TButton', background=self.primary_color, foreground='white', 
                           font=('Microsoft JhengHei', 10, 'bold'), width=18)

        nav_items = [
            ("SIM卡設定", self.show_sim_settings),
            ("伺服器設定", self.show_server_settings),
            ("主要設定", self.show_main_settings),
            ("AI通訊設定", self.show_ai_settings),
            ("RS485設定", self.show_rs485_settings),
            ("區域網路設定", self.show_network_settings),
            ("WIFI設定", self.show_wifi_settings),
            ("其他設定", self.show_other_settings)
        ]

        self.nav_buttons = {}  # 儲存按鈕參考
        self.selected_nav_btn = None  # 當前選中的按鈕

        for text, command in nav_items:
            btn = ttk.Button(self.left_frame, text=text,
                            command=lambda cmd=command, txt=text: self.navigate_to(cmd, txt),
                            style='Nav.TButton')
            btn.pack(pady=3, padx=5, fill=tk.X)
            self.nav_buttons[text] = btn  # 儲存按鈕物件
    
    def navigate_to(self, command, text):
        """切換頁面並高亮選中的導航按鈕"""
        # 重設所有按鈕樣式
        for btn in self.nav_buttons.values():
            btn.configure(style='Nav.TButton')

        # 設定選中的按鈕樣式
        selected_btn = self.nav_buttons.get(text)
        if selected_btn:
            selected_btn.configure(style='SelectedNav.TButton')
            self.selected_nav_btn = selected_btn

        # 呼叫對應頁面顯示函式
        command()
    
    def init_receive_frame(self):
        """初始化接收区域"""
        # 控制栏
        control_frame = ttk.Frame(self.receive_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=(5, 0))
        
        # 自动滚动复选框
        self.auto_scroll = tk.BooleanVar(value=True)
        self.auto_scroll_check = tk.Checkbutton(
            control_frame, 
            text="自動滾到底部",
            variable=self.auto_scroll,
            indicatoron=True,
            onvalue=True,
            offvalue=False,
            selectcolor='white',
            bg='#f0f0f0',
            activebackground='#f0f0f0',
            font=('Microsoft JhengHei', 10)
        )
        self.auto_scroll_check.pack(side=tk.LEFT, padx=5)
        
        # 清空按钮
        ttk.Button(control_frame, text="清空", command=self.clear_receive_text).pack(side=tk.RIGHT)
        
        # 接收文本框容器（新增容器框架）
        text_container = ttk.Frame(self.receive_frame)
        text_container.pack(fill=tk.BOTH, expand=True)
        
        # 接收文本框
        self.receive_text = scrolledtext.ScrolledText(
            text_container, 
            wrap=tk.WORD, 
            state=tk.DISABLED,
            font=('Consolas', 10),
            bg='#ffffff',
            fg='#333333',
            insertbackground='#333333',
            selectbackground=self.secondary_color,
            height=15  # 固定顯示15行文字
        )
        self.receive_text.pack(fill=tk.BOTH, expand=True)
        
        # 強制設定接收區最小高度
        self.receive_frame.pack_propagate(False)
        self.receive_frame.configure(height=400)
    
    def get_serial_ports(self):
        """獲取可用端口列表"""
        ports = []
        try:
            for port in serial.tools.list_ports.comports():
                ports.append(port.device)
        except Exception as e:
            self.append_receive_text(f"獲取端口列表失敗: {e}\n")
        return ports
    
    def refresh_serial_ports(self):
        """刷新端口列表"""
        ports = self.get_serial_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
            self.append_receive_text(f"檢測到可用端口: {', '.join(ports)}\n")
        else:
            self.append_receive_text("未檢測到可用端口，請檢查連接\n")
    
    def toggle_connection(self):
        """切換端口連接狀態"""
        if self.ser and self.ser.is_open:
            self.disconnect_serial()
        else:
            self.connect_serial()
    
    def connect_serial(self):
        """連接端口"""
        def worker():
            port = self.port_combo.get()
            baudrate = int(self.baudrate_combo.get())
            
            # 獲取端口參數
            bytesize_map = {"5": serial.FIVEBITS, "6": serial.SIXBITS, 
                            "7": serial.SEVENBITS, "8": serial.EIGHTBITS}
            bytesize = bytesize_map[self.data_var.get()]
            
            stopbits_map = {"1": serial.STOPBITS_ONE, "1.5": serial.STOPBITS_ONE_POINT_FIVE, 
                        "2": serial.STOPBITS_TWO}
            stopbits = stopbits_map[self.stop_var.get()]
            
            parity_map = {"None": serial.PARITY_NONE, "Even": serial.PARITY_EVEN, 
                        "Odd": serial.PARITY_ODD, "Mark": serial.PARITY_MARK, 
                        "Space": serial.PARITY_SPACE}
            parity = parity_map[self.parity_var.get()]
            
            
            if not port:
                messagebox.showwarning("警告", "請選擇端口")
                return
                
            try:
                bytesize = bytesize_map[self.data_var.get()]
                stopbits = stopbits_map[self.stop_var.get()]
                parity = parity_map[self.parity_var.get()]
                self.ser = serial.Serial(
                    port=port,
                    baudrate=baudrate,
                    bytesize=bytesize,
                    stopbits=stopbits,
                    parity=parity,
                    timeout=1
                )
                self.clear_serial_buffer()
                self.connect_button.config(text="斷開", style='Danger.TButton')
                self.append_receive_text(f"已連接到 {port}，波特率 {baudrate}，數據位 {bytesize}，停止位 {stopbits}，奇偶校驗 {parity}\n")
                
                # 連接成功後禁用端口設定控件
                self.enable_serial_settings(False)
                
                # 啟動端口讀取線程
                self.stop_event.clear()
                self.serial_thread = threading.Thread(target=self.read_serial_data)
                self.serial_thread.daemon = True
                self.serial_thread.start()
                
                # 發送初始化指令（非阻塞）
                self.send_at_command("+++")
                time.sleep(0.1)  # 等待設備進入命令模式
                self.send_at_command("AT+VERS")
                time.sleep(0.1)
                self.send_at_command("AT+ID")
                
            except Exception as e:
                messagebox.showerror("錯誤", f"連接端口失敗: {e}")
        self.enable_serial_settings(False)
        threading.Thread(target=worker, daemon=True).start()

        # 定期檢查隊列（主線程）
        self.root.after(100, self.process_serial_queue)
    def disconnect_serial(self):
        """斷開端口連接"""
        if self.ser and self.ser.is_open:
            try:
                self.stop_event.set()
                if self.serial_thread and self.serial_thread.is_alive():
                    self.serial_thread.join(1.0)
                
                self.ser.close()
                self.append_receive_text("已斷開端口連接\n")
                self.connect_button.config(text="連接", style='Accent.TButton')
                
                # 斷開後恢復端口設定控件
                self.enable_serial_settings(True)
                
            except Exception as e:
                messagebox.showerror("錯誤", f"關閉端口失敗: {e}")
        else:
            self.append_receive_text("端口未連接\n")

    def enable_serial_settings(self, enable):
        """啟用或禁用端口設定控件"""
        state = 'normal' if enable else 'disabled'
        
        # 端口相關控件
        self.port_combo['state'] = state
        self.baudrate_combo['state'] = state
        self.data_combobox['state'] = state
        self.stop_combobox['state'] = state
        self.parity_combobox['state'] = state
        
        # 換行符設定
        for cb in [self.auto_scroll_check]:
            if enable:
                cb['state'] = 'normal'
            else:
                cb['state'] = 'disabled'
        
        # 刷新按鈕
        refresh_button = [child for child in self.serial_frame.winfo_children() 
                        if isinstance(child, ttk.Button) and child['text'] == '↻']
        if refresh_button:
            refresh_button[0]['state'] = state
        
        # 設置控件灰色外觀
        bg_color = '#f0f0f0' if not enable else 'white'
        fg_color = '#a0a0a0' if not enable else 'black'
        
        for widget in [self.port_combo, self.baudrate_combo, 
                    self.data_combobox, self.stop_combobox, 
                    self.parity_combobox]:
            widget['background'] = bg_color
            widget['foreground'] = fg_color
    
    def read_serial_data(self):
        """讀取端口數據"""
        buffer = ""
        while not self.stop_event.is_set():
            if self.ser and self.ser.is_open:
                try:
                    # 讀取所有可用數據
                    while self.ser.in_waiting:
                        data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='replace')
                        buffer += data
                        
                        # 檢查是否收到完整的一行（以換行符結尾）
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            if line:  # 忽略空行
                                self.root.after(0, self.append_receive_text, f"{line}\n")
                                self.root.after(0, self.parse_response, line)
                    
                    time.sleep(0.1)  # 避免過度占用CPU
                    
                except Exception as e:
                    self.root.after(0, self.append_receive_text, f"讀取錯誤: {e}\n")
                    break
    
    def append_receive_text(self, text):
        """安全地向接收文本框添加文本"""
        if hasattr(self, 'receive_text') and self.receive_text:
            self.receive_text.config(state=tk.NORMAL)
            self.receive_text.insert(tk.END, text)
            if self.auto_scroll.get():
                self.receive_text.see(tk.END)
            self.receive_text.config(state=tk.DISABLED)
        else:
            print(f"接收文本未初始化: {text}")  # 调试用
    
    def clear_receive_text(self):
        """清空接收文本区域"""
        if hasattr(self, 'receive_text') and self.receive_text:
            self.receive_text.config(state=tk.NORMAL)
            self.receive_text.delete(1.0, tk.END)
            self.receive_text.config(state=tk.DISABLED)
    
    def clear_content_frame(self):
        """清除內容框架中的所有控件"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def parse_response(self, response):
        """解析設備返回的數據"""
        # 处理SIM卡设置响应
        if response.startswith("+CAPN:"):
            try:
                # 解析格式: +CAPN: <apn> -u<username> -p<password> -a<auth>
                parts = response.split()
                if len(parts) > 1:
                    apn = parts[1]
                    self.apn_var.set(apn)
                    
                    # 重置其他参数
                    self.username_var.set("")
                    self.password_var.set("")
                    self.auth_var.set("1:PAP")
                    
                    # 解析其他参数
                    for part in parts[2:]:
                        if part.startswith("-u"):
                            self.username_var.set(part[2:])
                        elif part.startswith("-p"):
                            self.password_var.set(part[2:])
                        elif part.startswith("-a"):
                            auth_map = {"PAP": "1:PAP", "CHAP": "2:CHAP"}
                            self.auth_var.set(auth_map.get(part[2:], "1:PAP"))
                
                self.update_settings_display()
            except Exception as e:
                self.append_receive_text(f"解析APN設定失敗: {e}\n")
        
        # 處理網路設備IP設置響應
        elif response.startswith("+NETDEVIP:"):
            try:
                # 清除表格現有數據
                for item in self.netdevip_tree.get_children():
                    self.netdevip_tree.delete(item)
                
                # 解析回應格式：0:192.168.168.254,255.255.255.0,fa:5a:bd:e6:dc:e2
                entries = response[len("+NETDEVIP:"):].strip().split('\n')
                
                for entry in entries:
                    if not entry.strip():
                        continue
                    
                    # 分割索引和數據
                    index_data = entry.split(':', 1)
                    if len(index_data) == 2:
                        index = index_data[0].strip()
                        data_parts = index_data[1].split(',')
                        
                        if len(data_parts) >= 3:
                            ip = data_parts[0].strip()
                            netmask = data_parts[1].strip()
                            mac = data_parts[2].strip() if len(data_parts) > 2 else ""
                            
                            # 添加到表格
                            self.netdevip_tree.insert("", tk.END, values=(index, ip, netmask, mac))
            except Exception as e:
                self.append_receive_text(f"解析網路設備IP設定失敗: {e}\n")
        
        # 處理AI信號設置響應
        elif response.startswith("+RTUPINCNF:"):
            try:
                # 格式: +RTUPINCNF:1,0,1,0,0 (5個通道的設置)
                values = response[len("+RTUPINCNF:"):].strip().split(',')
                
                if hasattr(self, 'ai_signal_tree'):
                    for i in range(min(len(values), 5)):  # 最多5個通道
                        channel_type = ""
                        if values[i] == "0":
                            channel_type = "0:不使用"
                        elif values[i] == "1":
                            channel_type = "1:電壓"
                        elif values[i] == "3":
                            channel_type = "3:電流"
                        elif values[i] == "5":
                            channel_type = "5:IO輸入"
                        elif values[i] == "6":
                            channel_type = "6:IO輸出"
                        elif values[i] == "7":
                            channel_type = "7:計數"
                        elif values[i] == "8":
                            channel_type = "8:計速"
                        self.ai_signal_tree.item(f"channel{i+1}", values=(f"通道{i+1}", channel_type))
            except Exception as e:
                self.append_receive_text(f"解析AI信號設定失敗: {e}\n")
        
        # 處理AI線性設置響應
        elif response.startswith("+RTUCALAD:"):
            try:
                # 格式: +RTUCALAD:-s500000 -o0 -r250
                parts = response[len("+RTUCALAD:"):].strip().split()
                
                if hasattr(self, 'ai_linear_tree'):
                    # 解析參數
                    slope = "500000"  # 預設值
                    offset = "0"      # 預設值
                    resistance = "250" # 預設值
                    
                    for part in parts:
                        if part.startswith("-s"):
                            slope = part[2:]
                        elif part.startswith("-o"):
                            offset = part[2:]
                        elif part.startswith("-r"):
                            resistance = part[2:]
                    
                    # 更新所有通道的值
                    for i in range(1, 6):
                        self.ai_linear_tree.item(f"linear{i}", 
                                            values=(f"通道{i}", slope, offset, resistance))
            except Exception as e:
                self.append_receive_text(f"解析AI線性設定失敗: {e}\n")

    
    def send_at_command(self, command, timeout=2):
        if self.ser and self.ser.is_open:
            try:
                final_command = command
                if command.strip() != "+++":
                    if self.use_nl.get():
                        final_command += '\n'
                    if self.use_cr.get():
                        final_command += '\r'
                
                self.ser.write(final_command.encode('utf-8'))
                self.append_receive_text(f"發送指令: {final_command.strip()}")
                
                # 等待回應
                start_time = time.time()
                response = ""
                while time.time() - start_time < timeout:
                    if self.ser.in_waiting:
                        data = self.ser.read(self.ser.in_waiting).decode('utf-8', errors='replace')
                        response += data
                        if "OK" in response or "ERROR" in response:  # 常見的AT指令回應
                            break
                
                if response:
                    self.append_receive_text(f"收到回應: {response}\n")
                    return response
                else:
                    self.append_receive_text("未收到回應\n")
                    return None
                    
            except Exception as e:
                self.append_receive_text(f"發送指令失敗: {e}\n")
                return None
        else:
            messagebox.showwarning("警告", "端口未連接")
            return None

    def wait_for_ok_and_send_next(self, next_command, delay):
        """
        非同步等待接收到 OK 回應後，再執行下一條指令
        """
        def check_response():
            # Get the last few lines from the receive text widget
            self.receive_text.config(state=tk.NORMAL)
            text_content = self.receive_text.get("1.0", tk.END)
            self.receive_text.config(state=tk.DISABLED)
            
            if "OK" in text_content.splitlines()[-5:]:  # Check last 5 lines for "OK"
                self.append_receive_text("收到 OK 回應，繼續執行下一步\n")
                if next_command:
                    self.root.after(delay, lambda: self.send_at_command(next_command))
            else:
                # 每 100ms 檢查一次，最多等 5 秒 (可自行調整)
                nonlocal retries
                retries -= 1
                if retries > 0:
                    self.root.after(100, check_response)
                else:
                    self.append_receive_text("未收到 OK 回應，放棄後續指令\n")

        retries = 50  # 最多重試 50 次（5 秒）
        check_response()

    def clear_serial_buffer(self):
        """清空端口緩衝區"""
        if self.ser and self.ser.is_open:
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()
    
    def show_sim_settings(self):
        """显示SIM卡设置"""
        self.clear_content_frame()

        # 创建SIM卡设置框架
        self.sim_frame = ttk.LabelFrame(self.content_frame, text="1. SIM卡設定",style='Bordered.TLabelframe')
        self.sim_frame.pack(fill=tk.X, pady=5, padx=5)
        self.sim_frame.columnconfigure(1, weight=1)

        # 使用 StringVar 綁定變數
        self.apn_var = tk.StringVar(value="internet")
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.auth_var = tk.StringVar(value="1:PAP")

        # 設定變數變動時回調
        self.apn_var.trace_add("write", self.update_settings_display)
        self.username_var.trace_add("write", self.update_settings_display)
        self.password_var.trace_add("write", self.update_settings_display)
        self.auth_var.trace_add("write", self.update_settings_display)

        # APN 設定
        ttk.Label(self.sim_frame, text="APN:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.apn_entry = ttk.Entry(self.sim_frame, textvariable=self.apn_var)
        self.apn_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Username 設定
        ttk.Label(self.sim_frame, text="Username:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.sim_frame, textvariable=self.username_var)
        self.username_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Password 設定
        ttk.Label(self.sim_frame, text="Password:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.sim_frame, textvariable=self.password_var, show="*")
        self.password_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Authentication 設定
        ttk.Label(self.sim_frame, text="Authentication:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.auth_combo = ttk.Combobox(
            self.sim_frame,
            textvariable=self.auth_var,
            values=["1:PAP", "2:CHAP"],
            state="readonly"
        )
        self.auth_combo.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # 顯示當前設定的 Label
        self.settings_display = ttk.Label(
            self.sim_frame,
            text="當前設定: APN=internet",
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(5, 2),
            style='Status.TLabel'
        )
        self.settings_display.grid(row=4, column=0, columnspan=2, sticky="ew", pady=5)

        # 按鈕區塊
        button_frame = ttk.Frame(self.sim_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="讀取", command=self.read_sim_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="送出", command=self.send_sim_settings, style='Primary.TButton').pack(side=tk.LEFT, padx=5)

        # =================================================================
        # 新增分隔線
        separator = ttk.Separator(self.content_frame, orient='horizontal')
        separator.pack(fill=tk.X, pady=10, padx=5)

        # 新增 RUT 配置框架（間距更緊湊）
        self.rut_frame = ttk.LabelFrame(self.content_frame, text="2.RUT配置", style='Bordered.TLabelframe')
        self.rut_frame.pack(fill=tk.X, pady=(0, 5), padx=5)  # 上方間距設為0
        self.rut_frame.columnconfigure(1, weight=1)

        # === RUT 定時重啟設定 ===
        self.reboot_var = tk.StringVar(value="0")  # 預設為 0 分鐘
        ttk.Label(self.rut_frame, text="設備定時重啟:").grid(row=0, column=0, sticky=tk.E, padx=(5,2), pady=(5,2))
        ttk.Entry(self.rut_frame, textvariable=self.reboot_var, width=8).grid(row=0, column=1, sticky=tk.W, padx=(0,2), pady=(5,2))
        ttk.Label(self.rut_frame, text="分鐘(設為0不啟用)").grid(row=0, column=2, sticky=tk.W, padx=(0,2), pady=(5,2))
        ttk.Button(self.rut_frame, text="▲", width=2, command=lambda: self.increment_value(self.reboot_var)).grid(row=0, column=3, sticky=tk.W, padx=(0,2), pady=(5,2))
        ttk.Button(self.rut_frame, text="▼", width=2, command=lambda: self.decrement_value(self.reboot_var)).grid(row=0, column=4, sticky=tk.W, padx=(0,2), pady=(5,2))
        ttk.Button(self.rut_frame, text="清除", command=lambda: self.reboot_var.set("0"), style='Danger.TButton').grid(row=0, column=5, sticky=tk.W, padx=(0,2), pady=(5,2))


        # 主被動模式設定（同一行緊湊排列）
        self.mode_var = tk.StringVar(value="10:主動")  # 預設值為主動
        ttk.Label(self.rut_frame, text="主被動模式:").grid(row=1, column=0, sticky=tk.E, padx=(5,2), pady=(2,5))
        mode_combobox = ttk.Combobox(
            self.rut_frame,
            textvariable=self.mode_var,
            values=["10:主動", "0:被動"],
            state="readonly",
            width=8
        )
        mode_combobox.grid(row=1, column=1, sticky=tk.W, padx=(0,2), pady=(2,5))
        ttk.Label(self.rut_frame, text="注意!設備必須設為被動模式", foreground="red").grid(row=1, column=2, sticky=tk.W, padx=(0,2), pady=(2,5))

        # RUT 配置按鈕區塊
        rut_button_frame = ttk.Frame(self.rut_frame)
        rut_button_frame.grid(row=1, column=0, columnspan=8, sticky="e", pady=(5,5), padx=(0,5))

        ttk.Button(rut_button_frame, text="讀取時間", command=self.read_ruttime_settings).grid(row=0, column=0, padx=3)
        ttk.Button(rut_button_frame, text="送出時間", command=self.send_ruttime_settings, style='Primary.TButton').grid(row=0, column=1, padx=3)
        ttk.Separator(rut_button_frame, orient="vertical").grid(row=0, column=2, sticky="ns", padx=5)  # 可選分隔線
        ttk.Button(rut_button_frame, text="讀取模式", command=self.read_rut_settings).grid(row=0, column=3, padx=3)
        ttk.Button(rut_button_frame, text="送出模式", command=self.send_rut_settings, style='Primary.TButton').grid(row=0, column=4, padx=3)


        # 初始化顯示
        self.update_settings_display()

    def read_ruttime_settings(self):
        """讀取設備定時重啟時間（從設備讀取 RBTYPE=1 設定）"""
        def worker():
            response = self.send_at_command("AT+RBTYPE")
            for line in response.splitlines():
                if line.startswith("+RBTYPE:"):
                    try:
                        parts = line.split(":")[1].strip().split()
                        if parts[0] == "1":  # RBTYPE=1 是時間設定
                            self.reboot_var.set(parts[1])  # 設定分鐘數
                            break
                    except Exception as e:
                        messagebox.showerror("錯誤", f"資料解析失敗：{e}")
        threading.Thread(target=worker).start()
       
    def send_ruttime_settings(self):
        """送出設備定時重啟時間（不包含模式）"""
        minutes = self.reboot_var.get()
        try:
            minutes_int = int(minutes)
            if minutes_int < 0:
                messagebox.showerror("錯誤", "請輸入非負整數")
                return
            command = f"AT+RBTYPE=1 {minutes_int}"
        except ValueError:
            messagebox.showerror("錯誤", "請輸入有效的數字")
            return

        def worker():
            self.send_at_command(command)
            self.receive_text.insert(tk.END, f"已送出: {command}\n")
            messagebox.showinfo("成功", "定時重啟時間已更新")

        threading.Thread(target=worker).start()



    def read_rut_settings(self):
        """讀取RUT配置設定"""
        def worker():
            response = self.send_at_command("AT+RBTYPE")

            # 假設設備回應格式為：+RBTYPE: 0 10
            for line in response.splitlines():
                if line.startswith("+RBTYPE:"):
                    try:
                        parts = line.split(":")[1].strip().split()
                        reboot_time = parts[0]
                        mode_val = parts[1]

                        self.reboot_var.set(reboot_time)
                        if mode_val == "0":
                            self.mode_var.set("10:主動")
                        elif mode_val == "10":
                            self.mode_var.set("0:被動")
                    except Exception as e:
                        messagebox.showerror("解析錯誤", f"資料格式錯誤: {e}")
                    break

        threading.Thread(target=worker).start()

    def send_rut_settings(self):
        """送出 RTU 模式設定（主動/被動）"""
        mode = self.mode_var.get()

        if mode == "10:主動":
            command = "AT+RBTYPE=2 10"
        elif mode == "0:被動":
            command = "AT+RBTYPE=2 0"
        else:
            messagebox.showerror("錯誤", "請選擇有效的模式")
            return

        def worker():
            self.send_at_command(command)
            self.receive_text.insert(tk.END, f"已送出: {command}\n")
            messagebox.showinfo("成功", "RTU 模式已更新")

        threading.Thread(target=worker).start()

    def update_settings_display(self, *args):
        """更新實時設置顯示"""
        apn = self.apn_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        auth = self.auth_var.get().split(":")[1]  # 获取认证类型文字部分
        
        parts = []
        if apn:
            parts.append(f"APN={apn}")
        if username:
            parts.append(f"使用者={username}")
        if password:
            parts.append(f"密碼={'*'*len(password)}")
        if auth != "NONE":
            parts.append(f"認證={auth}")
        
        display_text = "當前設定: " + " | ".join(parts) if parts else "當前設定: 未設定"
        
        # 更新显示
        if hasattr(self, 'settings_display'):
            self.settings_display.config(text=display_text)
        
        # 同时更新状态栏（如果有）
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=display_text)

    def update_sim_settings(self, *args):
        """实时更新SIM卡设置显示"""
        apn = self.apn_var.get()
        username = self.username_var.get()
        password = self.password_var.get()
        auth = self.auth_var.get().split(":")[1]  # 获取认证类型文字部分
        
        settings = []
        if apn:
            settings.append(f"APN={apn}")
        if username:
            settings.append(f"Username={username}")
        if password:
            settings.append(f"Password={'*'*len(password)}")
        if auth != "NONE":
            settings.append(f"Auth={auth}")
        
        if settings:
            self.sim_settings_label.config(text="當前設定: " + ", ".join(settings))
        else:
            self.sim_settings_label.config(text="當前設定: 未設定")
        
        # 同时实时更新要发送的指令预览
        self.update_command_preview()

    def update_command_preview(self):
        """更新要发送的指令预览"""
        apn = self.apn_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        auth = self.auth_var.get().split(":")[1]  # 获取认证类型文字部分
        
        # 构建AT指令预览
        command = f"AT+CAPN={apn}" if apn else "AT+CAPN"
        
        if username:
            command += f" -u{username}"
        if password:
            command += f" -p{password}"
        if auth != "NONE":
            command += f" -a{auth}"
        
        # 更新状态栏或特定Label显示指令
        if hasattr(self, 'command_preview_label'):
            self.command_preview_label.config(text=f"将发送: {command}")

    
        # 初始化更新
        self.update_sim_settings()
    
    def show_server_settings(self):
        """顯示伺服器設置"""
        self.clear_content_frame()

        # === 伺服器配置區塊 ===
        frame1 = ttk.LabelFrame(self.content_frame, text="3. 伺服器配置", style='Bordered.TLabelframe')
        frame1.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(frame1, text="伺服器位址:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.server_ip_entry = ttk.Entry(frame1, width=30)
        self.server_ip_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.server_ip_entry.insert(0, "leede.myds.me")

        ttk.Label(frame1, text="伺服器端口:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.server_port_entry = ttk.Entry(frame1, width=10)
        self.server_port_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.server_port_entry.insert(0, "5555")

        ttk.Label(frame1, text="協議:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.server_proto_combo = ttk.Combobox(frame1, values=["TCP", "UDP"], state="readonly", width=10)
        self.server_proto_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.server_proto_combo.set("TCP")

        ttk.Button(frame1, text="讀取", command=self.read_server).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame1, text="送出", command=self.send_server, style='Primary.TButton').grid(row=0, column=4, padx=5, pady=5)

        # === 網路設備IP設定區塊 ===
        frame2 = ttk.LabelFrame(self.content_frame, text="4. 網路設備IP設定", style='Bordered.TLabelframe')
        frame2.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        columns = ("索引", "IP位址", "子網掩碼", "MAC位址")
        self.netdevip_tree = ttk.Treeview(frame2, columns=columns, show="headings", height=5, style='CellBorders.Treeview')

        for col in columns:
            self.netdevip_tree.heading(col, text=col)
            self.netdevip_tree.column(col, width=140, anchor=tk.CENTER)

        self.netdevip_tree.grid(row=0, column=0, columnspan=3, sticky="nsew")

        scrollbar_x = ttk.Scrollbar(frame2, orient="horizontal", command=self.netdevip_tree.xview)
        self.netdevip_tree.configure(xscrollcommand=scrollbar_x.set)
        scrollbar_x.grid(row=1, column=0, columnspan=3, sticky="ew")

        # 讀取與送出按鈕
        ttk.Button(frame2, text="讀取", command=self.read_netdevip).grid(row=2, column=1, pady=5)
        ttk.Button(frame2, text="送出", command=self.send_netdevip, style='Primary.TButton').grid(row=2, column=2, pady=5)

        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)

        self.netdevip_tree.bind("<Double-1>", self.on_treeview_double_click)

        # 交錯底色樣式
        self.netdevip_tree.tag_configure('oddrow', background='#f9f9f9')
        self.netdevip_tree.tag_configure('evenrow', background="#dbdbdb")

        # 預設插入 5 筆空白資料，交錯底色
        for i in range(5):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.netdevip_tree.insert('', tk.END, values=("", "", "", ""), tags=(tag,))




    
    def on_treeview_double_click(self, event):
        """雙擊 Treeview 儲存格啟用編輯"""
        region = self.netdevip_tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        # 找到哪一格
        row_id = self.netdevip_tree.identify_row(event.y)
        column = self.netdevip_tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1  # 轉成 0-based index

        if row_id == "" or col_index < 0:
            return

        # 儲存目前值
        item = self.netdevip_tree.item(row_id)
        old_value = item["values"][col_index]

        # 取得儲存格的位置
        x, y, width, height = self.netdevip_tree.bbox(row_id, column)

        # 建立可編輯 Entry
        self.edit_box = tk.Entry(self.netdevip_tree)
        self.edit_box.place(x=x, y=y, width=width, height=height)
        self.edit_box.insert(0, old_value)
        self.edit_box.focus()

        # 設定事件
        def save_edit(event=None):
            new_value = self.edit_box.get()
            values = list(item["values"])
            values[col_index] = new_value
            self.netdevip_tree.item(row_id, values=values)
            self.edit_box.destroy()

        self.edit_box.bind("<Return>", save_edit)
        self.edit_box.bind("<FocusOut>", lambda e: self.edit_box.destroy())

    def show_main_settings(self):
        """顯示主要設置"""
        self.clear_content_frame()

        # === 5. 上傳設定 ===
        frame1 = ttk.LabelFrame(self.content_frame, text="5. 上傳設定",style='Bordered.TLabelframe')
        frame1.pack(fill=tk.X, pady=5, padx=5)

        # 讀取與送出按鈕（右上角）
        btn_frame1 = ttk.Frame(frame1)
        btn_frame1.grid(row=0, column=3, columnspan=2, sticky=tk.E, padx=5, pady=5)
        ttk.Button(btn_frame1, text="讀取", command=self.read_upload_settings).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame1, text="送出", command=self.send_upload_settings, style='Primary.TButton').pack(side=tk.LEFT, padx=2)

        # 採樣時間間隔
        ttk.Label(frame1, text="採樣時間間隔:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        sample_frame = ttk.Frame(frame1)
        sample_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W)
        self.sample_interval_entry = ttk.Entry(sample_frame, width=10)
        self.sample_interval_entry.pack(side=tk.LEFT)
        ttk.Label(sample_frame, text="秒").pack(side=tk.LEFT, padx=(5, 0))
        self.sample_interval_entry.insert(0, "60")

        # 上傳時間間隔
        ttk.Label(frame1, text="上傳時間間隔:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        upload_frame = ttk.Frame(frame1)
        upload_frame.grid(row=3, column=1, columnspan=2, sticky=tk.W)
        self.upload_interval_entry = ttk.Entry(upload_frame, width=10)
        self.upload_interval_entry.pack(side=tk.LEFT)
        ttk.Label(upload_frame, text="秒").pack(side=tk.LEFT, padx=(5, 0))
        self.upload_interval_entry.insert(0, "600")

        # 儲存時間間隔
        ttk.Label(frame1, text="儲存時間間隔:").grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        save_frame = ttk.Frame(frame1)
        save_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W)
        self.save_interval_entry = ttk.Entry(save_frame, width=10)
        self.save_interval_entry.pack(side=tk.LEFT)
        ttk.Label(save_frame, text="秒").pack(side=tk.LEFT, padx=(5, 0))
        self.save_interval_entry.insert(0, "60")

        # 供電模式
        ttk.Label(frame1, text="供電模式:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.power_mode_combo = ttk.Combobox(
            frame1,
            values=["0:電源模式(不休眠)", "3:電池模式(定時休眠)"],
            state="readonly",
            width=20
        )
        self.power_mode_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.power_mode_combo.set("0:電源模式(不休眠)")

        # === 6. 上傳格式設定 ===
        frame2 = ttk.LabelFrame(self.content_frame, text="6. 上傳格式設定",  style='Bordered.TLabelframe')
        frame2.pack(fill=tk.X, pady=5, padx=5)

        # 讀取與送出按鈕（右上角）
        btn_frame2 = ttk.Frame(frame2)
        btn_frame2.grid(row=0, column=3, columnspan=2, sticky=tk.E, padx=5, pady=5)
        ttk.Button(btn_frame2, text="讀取", command=self.read_upload_format).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame2, text="送出", command=self.send_upload_format, style='Primary.TButton').pack(side=tk.LEFT, padx=2)

        # 上傳數據格式
        ttk.Label(frame2, text="上傳數據格式:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.upload_format_combo = ttk.Combobox(
            frame2,
            values=["1:RTU MODBUS", "3:ID+字串", "4:JSON格式"],
            state="readonly",
            width=15
        )
        self.upload_format_combo.grid(row=0, column=1, columnspan=2, sticky=tk.W, padx=5, pady=5)
        self.upload_format_combo.set("1:RTU MODBUS")

        # RTU Modbus 站號
        ttk.Label(frame2, text="RTU Modbus站號:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.rtu_station_entry = ttk.Entry(frame2, width=10)
        self.rtu_station_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.rtu_station_entry.insert(0, "1")

        # RTU Modbus port
        ttk.Label(frame2, text="RTU Modbus port:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.rtu_port_entry = ttk.Entry(frame2, width=10)
        self.rtu_port_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.rtu_port_entry.insert(0, "502")

    def edit_setting_value(self, widget):

        """雙擊編輯設定值"""
        # 創建編輯窗口
        edit_win = tk.Toplevel(self.root)
        edit_win.title("編輯設定值")
        edit_win.geometry("300x150")
        
        # 獲取當前值
        current_value = widget.get()
        
        # 創建標籤
        label_text = "採樣時間間隔" if widget == self.sample_interval_entry else \
                    "上傳時間間隔" if widget == self.upload_interval_entry else \
                    "儲存時間間隔" if widget == self.save_interval_entry else \
                    "RTU Modbus站號" if widget == self.rtu_station_entry else \
                    "RTU Modbus port"
        ttk.Label(edit_win, text=f"{label_text}:").pack(pady=5)  
        # 創建輸入框
        entry_var = tk.StringVar(value=current_value)
        entry = ttk.Entry(edit_win, textvariable=entry_var)
        entry.pack(pady=5)
        entry.focus()
        
    # 保存按鈕
        def save_value():
            new_value = entry_var.get()
            widget.delete(0, tk.END)
            widget.insert(0, new_value)
            edit_win.destroy()
        
        ttk.Button(edit_win, text="保存", command=save_value, style='Primary.TButton').pack(pady=10)

    def show_ai_settings(self):
        """顯示AI通訊設定"""
        self.clear_content_frame()

        # === 7. AI訊號設定區塊 ===
        frame1 = ttk.LabelFrame(self.content_frame, text="7. AI訊號設定", style='Bordered.TLabelframe')
        frame1.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        columns = ("通道", "信號類型")
        self.ai_signal_tree = ttk.Treeview(frame1, columns=columns, show="headings", height=4)
        
        # 設定交錯底色樣式
        self.ai_signal_tree.tag_configure('oddrow', background='#f9f9f9')
        self.ai_signal_tree.tag_configure('evenrow', background='#ebebeb')

        # 設定欄位
        self.ai_signal_tree.heading("通道", text="通道")
        self.ai_signal_tree.column("通道", width=38, anchor=tk.CENTER)
        self.ai_signal_tree.heading("信號類型", text="信號類型")
        self.ai_signal_tree.column("信號類型", width=100, anchor=tk.CENTER)

        # 插入空資料（含交錯底色）
        for i in range(20):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.ai_signal_tree.insert("", tk.END, iid=f"channel{i}", values=(f"通道{i}", ""), tags=(tag,))

        # 捲軸
        scrollbar = ttk.Scrollbar(frame1, orient=tk.VERTICAL, command=self.ai_signal_tree.yview)
        self.ai_signal_tree.configure(yscrollcommand=scrollbar.set)

        self.ai_signal_tree.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)

        # 按鈕區塊
        button_frame = ttk.Frame(frame1)
        button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(button_frame, text="讀取", command=self.read_ai_signal_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="送出", command=self.send_ai_signal_settings, style='Primary.TButton').pack(side=tk.LEFT, padx=5)

        # 調整 frame 大小
        frame1.grid_rowconfigure(0, weight=1)
        frame1.grid_columnconfigure(0, weight=1)

        self.ai_signal_tree.bind("<Double-1>", self.on_ai_signal_double_click)

        # === 8. AI線性設定區塊 ===
        frame2 = ttk.LabelFrame(self.content_frame, text="8. AI訊號線性設定", style='Bordered.TLabelframe')
        frame2.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        linear_columns = ("通道", "斜率", "偏移量", "電阻值")
        self.ai_linear_tree = ttk.Treeview(frame2, columns=linear_columns, show="headings", height=4)

        self.ai_linear_tree.tag_configure('oddrow', background='#f9f9f9')
        self.ai_linear_tree.tag_configure('evenrow', background='#ebebeb')

        for col in linear_columns:
            self.ai_linear_tree.heading(col, text=col)
            self.ai_linear_tree.column(col, width=100, anchor=tk.CENTER)

        for i in range(20):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.ai_linear_tree.insert("", tk.END, iid=f"linear{i}", values=(f"通道{i}", "", "", ""), tags=(tag,))

        linear_scrollbar = ttk.Scrollbar(frame2, orient=tk.VERTICAL, command=self.ai_linear_tree.yview)
        self.ai_linear_tree.configure(yscrollcommand=linear_scrollbar.set)

        self.ai_linear_tree.grid(row=0, column=0, sticky=tk.NSEW)
        linear_scrollbar.grid(row=0, column=1, sticky=tk.NS)

        linear_button_frame = ttk.Frame(frame2)
        linear_button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        ttk.Button(linear_button_frame, text="讀取", command=self.read_ai_linear_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(linear_button_frame, text="送出", command=self.send_ai_linear_settings, style='Primary.TButton').pack(side=tk.LEFT, padx=5)

        frame2.grid_rowconfigure(0, weight=1)
        frame2.grid_columnconfigure(0, weight=1)

        self.ai_linear_tree.bind("<Double-1>", self.on_ai_linear_double_click)



    def on_ai_signal_double_click(self, event):
        """雙擊AI訊號設定表格編輯"""
        row_id = self.ai_signal_tree.focus()
        column = self.ai_signal_tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        
        # 只允許編輯信號類型列
        if not row_id or col_index != 1:
            return
        
        # 獲取當前值
        current_values = list(self.ai_signal_tree.item(row_id, 'values'))
        current_value = current_values[1]
        
        # 創建編輯窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("編輯信號類型")
        edit_window.geometry("300x120")
        
        # 信號類型選項
        ttk.Label(edit_window, text="選擇信號類型:").pack(pady=5)
        signal_combo = ttk.Combobox(edit_window, values=["0:不使用", "1:電壓", "3:電流", "5:IO輸入", "6:IO輸出", "7:計數", "8:計速"], state="readonly")
        signal_combo.pack(pady=5)
        
        # 如果有當前值，設置為選中
        if current_value:
            signal_combo.set(current_value)
        else:
            signal_combo.set("0:不使用")
        
        # 保存按鈕
        def save_edit():
            new_value = signal_combo.get()
            current_values[1] = new_value
            self.ai_signal_tree.item(row_id, values=current_values)
            edit_window.destroy()
        
        ttk.Button(edit_window, text="保存", command=save_edit, style='Primary.TButton').pack(pady=5)

    def on_ai_linear_double_click(self, event):
        """雙擊AI線性設定表格編輯"""
        row_id = self.ai_linear_tree.focus()
        column = self.ai_linear_tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        
        # 不允許編輯通道列
        if not row_id or col_index == 0:
            return
        
        # 獲取當前值
        current_values = list(self.ai_linear_tree.item(row_id, 'values'))
        current_value = current_values[col_index]
        
        # 創建編輯窗口
        edit_window = tk.Toplevel(self.root)
        edit_window.title("編輯參數")
        edit_window.geometry("300x120")
        
        # 根據列類型創建不同的標籤
        if col_index == 1:  # 斜率
            ttk.Label(edit_window, text="輸入斜率:").pack(pady=5)
        elif col_index == 2:  # 偏移量
            ttk.Label(edit_window, text="輸入偏移量:").pack(pady=5)
        else:  # 電阻值
            ttk.Label(edit_window, text="輸入電阻值:").pack(pady=5)
        
        # 輸入框
        edit_entry = ttk.Entry(edit_window)
        edit_entry.pack(pady=5)
        
        # 如果有當前值，設置為預設值
        if current_value:
            edit_entry.insert(0, current_value)
        
        # 保存按鈕
        def save_edit():
            new_value = edit_entry.get()
            current_values[col_index] = new_value
            self.ai_linear_tree.item(row_id, values=current_values)
            edit_window.destroy()
        
        ttk.Button(edit_window, text="保存", command=save_edit, style='Primary.TButton').pack(pady=5)

    def edit_table_cell(self, event):
        """通用表格單元格編輯函數"""
        # 獲取點擊的表格控件
        tree = event.widget
        # 獲取點擊的行和列
        row_id = tree.focus()
        column = tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        
        if not row_id:
            return
        
        # 獲取當前值
        item = tree.item(row_id)
        values = list(item['values'])
        current_value = values[col_index]
        
        # 創建編輯窗口
        edit_win = tk.Toplevel(self.root)
        edit_win.title("編輯數值")
        edit_win.geometry("300x150")
        
        # 根據列類型決定編輯控件
        if "功能碼" in tree.heading(column)['text'] or "協議" in tree.heading(column)['text']:
            # 下拉框編輯
            ttk.Label(edit_win, text=f"編輯 {tree.heading(column)['text']}:").pack(pady=5)
            combo = ttk.Combobox(edit_win, state="readonly")
            
            # 設置下拉選項
            if "功能碼" in tree.heading(column)['text']:
                combo['values'] = ["00:無", "03:只讀(4XXXX)", "04:只讀(3XXXX)", "06:單個寫入"]
            elif "協議" in tree.heading(column)['text']:
                combo['values'] = ["0:TCP", "1:UDP"]
                
            combo.set(current_value)
            combo.pack(pady=5)
            
            def save_edit():
                values[col_index] = combo.get()
                tree.item(row_id, values=values)
                edit_win.destroy()
                
        else:
            # 普通文本編輯
            ttk.Label(edit_win, text=f"編輯 {tree.heading(column)['text']}:").pack(pady=5)
            entry = ttk.Entry(edit_win)
            entry.insert(0, current_value)
            entry.pack(pady=5)
            
            def save_edit():
                values[col_index] = entry.get()
                tree.item(row_id, values=values)
                edit_win.destroy()
        
        # 保存按鈕
        ttk.Button(edit_win, text="保存", command=save_edit, style='Primary.TButton').pack(pady=10)
        
        # 點擊Enter鍵也保存
        edit_win.bind("<Return>", lambda e: save_edit())

    def show_network_settings(self):
        """显示区域网络设置"""
        self.clear_content_frame()
        
        # 创建Notebook来切换两个子页面
        self.network_notebook = ttk.Notebook(self.content_frame)
        self.network_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 31. PORT转发
        self.port_forward_frame = ttk.Frame(self.network_notebook)
        self.network_notebook.add(self.port_forward_frame, text="31. PORT轉發")
        self.init_port_forward_settings()
        
        # 32. 区域网络设置
        self.lan_settings_frame = ttk.Frame(self.network_notebook)
        self.network_notebook.add(self.lan_settings_frame, text="32. 區域網路設定")
        self.init_lan_settings()

    def init_port_forward_settings(self):
        """初始化PORT转發设置 - 表格模式"""
        frame = ttk.LabelFrame(self.port_forward_frame, text="31. PORT轉發設定（0-15）",  style='Bordered.TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格框架
        table_frame = ttk.Frame(frame)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建水平和垂直滚动条
        x_scrollbar = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL)
        y_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL)
        
        # 定义表格列
        columns = ("索引", "通訊協議 0:TCP/1:UDP", "外部埠", "設備IP:埠")
        self.port_forward_tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            height=10,  # 只顯示10行
            xscrollcommand=x_scrollbar.set,
            yscrollcommand=y_scrollbar.set,
            style='Bordered.Treeview'
        )
        
        # 設定交錯底色樣式
        self.port_forward_tree.tag_configure('oddrow', background='#f9f9f9')
        self.port_forward_tree.tag_configure('evenrow', background='#e6e6e6')
        
        # 配置列标题和宽度
        col_widths = [60, 100, 80, 150]
        for idx, col in enumerate(columns):
            self.port_forward_tree.heading(col, text=col)
            self.port_forward_tree.column(col, width=col_widths[idx], anchor=tk.CENTER)
        
        # 添加0-15行数据，並套用交錯行顏色
        for i in range(16):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.port_forward_tree.insert(
                "", 
                tk.END, 
                values=(str(i), "0:TCP", "502", "192.168.1.1:502"),
                tags=(tag,)
            )
        
        # 双击编辑功能
        self.port_forward_tree.bind("<Double-1>", self.on_port_entry_double_click)
        
        # 布局
        self.port_forward_tree.grid(row=0, column=0, sticky=tk.NSEW)
        y_scrollbar.grid(row=0, column=1, sticky=tk.NS)
        x_scrollbar.grid(row=1, column=0, sticky=tk.EW)
        
        # 配置滚动条
        x_scrollbar.config(command=self.port_forward_tree.xview)
        y_scrollbar.config(command=self.port_forward_tree.yview)
        
        # 按钮区域
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        # 操作按钮
        ttk.Button(button_frame, text="讀取配置", command=self.read_port_forward_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="保存修改", command=self.save_port_forward_settings, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="發送到設備", command=self.send_port_forward_settings, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        
        # 编辑窗口（隐藏状态）
        self.port_edit_window = None
        
        # 配置网格权重
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)


    def on_port_entry_double_click(self, event):
        """双击表格单元格编辑"""
        # 获取选中的行和列
        row_id = self.port_forward_tree.focus()
        column = self.port_forward_tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        
        # 只允许编辑后三列（跳过索引列）
        if not row_id or col_index < 1 or col_index > 3:
            return
        
        # 获取当前值
        current_values = list(self.port_forward_tree.item(row_id, 'values'))
        current_value = current_values[col_index]
        
        # 创建编辑窗口
        self.port_edit_window = tk.Toplevel(self.root)
        self.port_edit_window.title("編輯設定")
        self.port_edit_window.geometry("300x120")
        
        # 根据列类型创建不同的编辑控件
        if col_index == 1:  # 通讯协议
            ttk.Label(self.port_edit_window, text="選擇協議:").pack(pady=5)
            edit_combo = ttk.Combobox(self.port_edit_window, values=["0:TCP", "1:UDP"], state="readonly")
            edit_combo.set(current_value)
            edit_combo.pack(pady=5)
        else:  # 外部埠或设备IP:埠
            ttk.Label(self.port_edit_window, text="输入新值:").pack(pady=5)
            edit_entry = ttk.Entry(self.port_edit_window)
            edit_entry.insert(0, current_value)
            edit_entry.pack(pady=5)
        
        # 保存按钮
        def save_edit():
            if col_index == 1:
                new_value = edit_combo.get()
            else:
                new_value = edit_entry.get()
            
            current_values[col_index] = new_value
            self.port_forward_tree.item(row_id, values=current_values)
            self.port_edit_window.destroy()
        
        ttk.Button(self.port_edit_window, text="保存", command=save_edit, style='Primary.TButton').pack(pady=5)

    def save_port_forward_settings(self):
        """保存所有修改（内存中）"""
        messagebox.showinfo("保存", "所有修改已保存（內存中）", parent=self.root)
        
    def read_port_forward_settings(self):
        """讀取PORT轉發設定 (AT+DNATCNF) 並更新表格"""
        response = self.send_at_command("AT+DNATCNF")
        self.append_receive_text(f"收到回應:\n{response}\n")

        try:
            # 創建一個字典來存儲解析後的設定，索引為鍵
            port_settings = {}
            
            # 解析每一行回應
            for line in response.splitlines():
                if line.startswith("+DNATCNF="):
                    # 移除命令前綴
                    data = line[len("+DNATCNF="):].strip()
                    
                    # 分割成索引和設定
                    parts = data.split(':', 1)
                    if len(parts) != 2:
                        continue
                    
                    index = int(parts[0].strip())
                    settings = [s.strip() for s in parts[1].split(',')]
                    
                    if len(settings) != 3:
                        continue
                    
                    # 儲存設定到字典
                    port_settings[index] = {
                        'protocol': settings[0],
                        'ext_port': settings[1],
                        'dev_ip_port': settings[2]
                    }
            
            # 更新表格中的每一行
            for item in self.port_forward_tree.get_children():
                index = int(self.port_forward_tree.item(item, 'values')[0])
                
                if index in port_settings:
                    # 如果有從設備讀取的設定，使用這些值
                    settings = port_settings[index]
                    proto_text = f"{settings['protocol']}:UDP" if settings['protocol'] == "1" else f"{settings['protocol']}:TCP"
                    self.port_forward_tree.item(item, values=(
                        str(index),
                        proto_text,
                        settings['ext_port'],
                        settings['dev_ip_port']
                    ))
                else:
                    # 如果沒有從設備讀取的設定，保持原樣或清空
                    current_values = list(self.port_forward_tree.item(item, 'values'))
                    self.port_forward_tree.item(item, values=(
                        current_values[0],  # 索引
                        current_values[1],   # 協議 (保持不變)
                        "",                 # 外部埠 (清空)
                        ""                 # 設備IP:埠 (清空)
                    ))
                    
        except Exception as e:
            self.append_receive_text(f"解析PORT轉發設定失敗: {e}\n")

    def send_port_forward_settings(self):
        """整批發送所有PORT轉發設定 (使用 AT+DNATCNF 格式)"""
        try:
            for item in self.port_forward_tree.get_children():
                index, proto, ext_port, dev_ip_port = self.port_forward_tree.item(item, 'values')
                proto_code = proto.split(":")[0]  # "0" for TCP, "1" for UDP

                command = f"AT+DNATCNF={index} -u{proto_code} -s{ext_port} -d{dev_ip_port}"
                response = self.send_at_command(command)
                self.append_receive_text(f"{command}\n{response.strip()}\n")

        except Exception as e:
            self.append_receive_text(f"整批發送PORT轉發設定失敗: {e}\n")

    def send_all_port_forward_settings(self):
            """發送PORT轉發設置"""
            index = self.port_index_combo.get()
            proto = self.port_proto_combo.get().split(":")[0]
            external_port = self.port_external_entry.get()
            device_ip_port = self.port_device_entry.get()
            
            # 更新表格中的數據
            for item in self.port_forward_tree.get_children():
                if self.port_forward_tree.item(item, 'values')[0] == index:
                    self.port_forward_tree.item(item, values=(
                        index, 
                        f"{proto}:{'TCP' if proto == '0' else 'UDP'}",
                        external_port,
                        device_ip_port
                    ))
                    break
            
            self.send_at_command(f"AT+DNATCNF={index},{proto},{external_port},{device_ip_port}")


    def read_lan_settings(self):
        """讀取區域網路設置並更新UI"""
        response = self.send_at_command("AT+LANCNF?")
        self.append_receive_text(f"收到回應:\n{response}\n")

        try:
            if "+LANCNF=" in response:
                # 解析回應格式: +LANCNF=-i192.168.168.254 -m255.255.255.0 -a16:f0:37:09:a5:71 -d168.95.1.1
                settings = {}
                parts = response.split("+LANCNF=")[1].split()
                
                for part in parts:
                    if part.startswith("-i"):
                        settings['ip'] = part[2:]
                    elif part.startswith("-m"):
                        settings['netmask'] = part[2:]
                    elif part.startswith("-a"):
                        settings['mac'] = part[2:]
                    elif part.startswith("-d"):
                        settings['dns'] = part[2:]

                # 更新UI中的輸入框
                self.lan_ip_entry.delete(0, tk.END)
                self.lan_ip_entry.insert(0, settings.get('ip', '192.168.1.100'))
                
                self.lan_netmask_entry.delete(0, tk.END)
                self.lan_netmask_entry.insert(0, settings.get('netmask', '255.255.255.0'))
                
                self.lan_mac_entry.delete(0, tk.END)
                self.lan_mac_entry.insert(0, settings.get('mac', '00:11:22:33:44:55'))
                
                self.lan_dns_entry.delete(0, tk.END)
                self.lan_dns_entry.insert(0, settings.get('dns', '8.8.8.8'))
                
        except Exception as e:
            self.append_receive_text(f"解析區域網路設定失敗: {e}\n")
            messagebox.showerror("錯誤", f"讀取區域網路設定失敗: {e}", parent=self.root)

    def send_lan_settings(self):
        """發送區域網路設置"""
        try:
            ip = self.lan_ip_entry.get()
            netmask = self.lan_netmask_entry.get()
            mac = self.lan_mac_entry.get()
            dns = self.lan_dns_entry.get()
            
            # 驗證輸入
            if not all([ip, netmask, mac, dns]):
                messagebox.showwarning("警告", "所有欄位必須填寫", parent=self.root)
                return
                
            # 發送命令
            command = f"AT+LANCNF=-i{ip} -m{netmask} -a{mac} -d{dns}"
            response = self.send_at_command(command)
            self.append_receive_text(f"{command}\n{response}\n")
            
            if "OK" in response:
                messagebox.showinfo("成功", "區域網路設定已發送", parent=self.root)
            else:
                messagebox.showerror("錯誤", "發送區域網路設定失敗", parent=self.root)
                
        except Exception as e:
            self.append_receive_text(f"發送區域網路設定失敗: {e}\n")
            messagebox.showerror("錯誤", f"發送區域網路設定失敗: {e}", parent=self.root)


    def init_lan_settings(self):
        """初始化區域網路設定"""
        frame = ttk.LabelFrame(self.lan_settings_frame, text="32. 區域網路設定",  style='Bordered.TLabelframe')
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # IP
        ttk.Label(frame, text="IP:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.lan_ip_entry = ttk.Entry(frame, width=15)
        self.lan_ip_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.lan_ip_entry.insert(0, "192.168.1.100")
        
        # 子網路遮罩
        ttk.Label(frame, text="子網路遮罩:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.lan_netmask_entry = ttk.Entry(frame, width=15)
        self.lan_netmask_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.lan_netmask_entry.insert(0, "255.255.255.0")
        
        # MAC
        ttk.Label(frame, text="MAC:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.lan_mac_entry = ttk.Entry(frame, width=17)
        self.lan_mac_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.lan_mac_entry.insert(0, "00:11:22:33:44:55")
        
        # DNS伺服器
        ttk.Label(frame, text="DNS伺服器:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.lan_dns_entry = ttk.Entry(frame, width=15)
        self.lan_dns_entry.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.lan_dns_entry.insert(0, "8.8.8.8")
        
        # 讀取和發送按鈕
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(button_frame, text="讀取", command=self.read_lan_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="送出", command=self.send_lan_settings, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
    
    def show_rs485_settings(self):
        """顯示RS485設定（優化排版）"""
        self.clear_content_frame()
        main_frame = ttk.Frame(self.content_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # ========== RS485基本設定 ==========
        rs485_frame = ttk.LabelFrame(main_frame, text="9. RS485設定",  style='Bordered.TLabelframe')
        rs485_frame.pack(fill=tk.X, pady=(0, 10))
        for i in range(4):
            rs485_frame.grid_rowconfigure(i, pad=4)
        for i in range(6):
            rs485_frame.grid_columnconfigure(i, weight=1)

        # 通訊組
        ttk.Label(rs485_frame, text="通訊組:").grid(row=0, column=0, sticky=tk.E, padx=(8,2))
        self.rs485_group_combo = ttk.Combobox(rs485_frame, values=["0", "1", "2", "3", "4"], state="readonly", width=4)
        self.rs485_group_combo.grid(row=0, column=1, sticky=tk.W)
        self.rs485_group_combo.set("0")
        # 設備位置
        ttk.Label(rs485_frame, text="設備位置:").grid(row=0, column=2, sticky=tk.E, padx=(10,2))
        self.rs485_addr_entry = ttk.Entry(rs485_frame, width=6, validate='key', validatecommand=(self.root.register(self.validate_max2_digit), '%P'))
        self.rs485_addr_entry.grid(row=0, column=3, sticky=tk.W)
        self.rs485_addr_entry.insert(0, "00")
        # 起始位址
        ttk.Label(rs485_frame, text="起始位址:").grid(row=1, column=0, sticky=tk.E, padx=(8,2))
        self.rs485_start_entry = ttk.Entry(rs485_frame, width=6, validate='key', validatecommand=(self.root.register(self.validate_max4_digit), '%P'))
        self.rs485_start_entry.grid(row=1, column=1, sticky=tk.W)
        self.rs485_start_entry.insert(0, "0000")
        # 功能碼
        ttk.Label(rs485_frame, text="功能碼:").grid(row=1, column=2, sticky=tk.E, padx=(10,2))
        self.rs485_func_combo = ttk.Combobox(rs485_frame, values=["00:無", "03:只讀(4XXXX)", "04:只讀(3XXXX)", "06:單個寫入"], state="readonly", width=15)
        self.rs485_func_combo.grid(row=1, column=3, sticky=tk.W)
        self.rs485_func_combo.set("00:無")
        # 數據長度
        ttk.Label(rs485_frame, text="數據長度:").grid(row=2, column=0, sticky=tk.E, padx=(8,2))
        self.rs485_length_entry = ttk.Entry(rs485_frame, width=6, validate='key', validatecommand=(self.root.register(self.validate_max4_digit), '%P'))
        self.rs485_length_entry.grid(row=2, column=1, sticky=tk.W)
        self.rs485_length_entry.insert(0, "0001")

        # 按鈕區域
        button_frame = ttk.Frame(rs485_frame)
        button_frame.grid(row=3, column=0, columnspan=6, pady=10)
        ttk.Button(button_frame, text="讀取", command=self.read_rs485_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="生成指令", command=self.generate_rs485_command, style='Primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="送出", command=self.send_rs485_settings).pack(side=tk.LEFT, padx=5)

        # ========== MODBUS指令表格 ==========
        table_frame = ttk.LabelFrame(main_frame, text="MODBUS指令設定",  style='Bordered.TLabelframe')
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.rs485_table = ttk.Treeview(
            table_frame,
            columns=("通訊組", "MODBUS指令"),
            show="headings",
            style='Bordered.Treeview'
        )

        self.rs485_table.heading("通訊組", text="通訊組")
        self.rs485_table.heading("MODBUS指令", text="MODBUS指令")
        self.rs485_table.column("通訊組", width=80, anchor=tk.CENTER)
        self.rs485_table.column("MODBUS指令", width=150, anchor=tk.CENTER)

        # ✨ 加入交錯底色樣式
        self.rs485_table.tag_configure('oddrow', background='#f9f9f9')
        self.rs485_table.tag_configure('evenrow', background='#e6e6e6')

        # ✨ 插入交錯資料
        for i in range(20):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.rs485_table.insert("", tk.END, values=(str(i), "00000000000"), tags=(tag,))

        # 滾動條
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.rs485_table.yview)
        self.rs485_table.configure(yscrollcommand=scrollbar.set)

        self.rs485_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.rs485_table.bind("<Double-1>", self.edit_rs485_table_item)


    def validate_max4_digit(self, value: str) -> bool:
        """限制最多4位且為16進位格式"""
        if len(value) > 4:
            return False
        return all(c in '0123456789ABCDEFabcdef' for c in value)

    def validate_max2_digit(self, value: str) -> bool:
        """限制最多2位且為16進位格式"""
        if len(value) > 2:
            return False
        return all(c in '0123456789ABCDEFabcdef' for c in value)


    def validate_hex(self, value):
        """驗證輸入是否為有效的十六進制數字"""
        try:
            int(value, 16)
            return True
        except ValueError:
            return False

    def edit_rs485_table_item(self, event):
        """編輯表格中的MODBUS指令"""
        item = self.rs485_table.selection()
        if not item:
            return
            
        column = self.rs485_table.identify_column(event.x)
        if column == "#2":  # 只允許編輯MODBUS指令列
            current_value = self.rs485_table.item(item, 'values')[1]
            
            # 創建編輯窗口
            edit_win = tk.Toplevel(self.root)
            edit_win.title("編輯MODBUS指令")
            edit_win.geometry("300x120")
            
            ttk.Label(edit_win, text="輸入MODBUS指令 (10位十六進制):").pack(pady=5)
            entry = ttk.Entry(edit_win, validate='key', 
                            validatecommand=(self.root.register(self.validate_hex_length), '%P'))
            entry.pack(pady=5)
            entry.insert(0, current_value)
            
            def save_edit():
                new_value = entry.get().zfill(10)  # 不足10位補零
                values = list(self.rs485_table.item(item, 'values'))
                values[1] = new_value
                self.rs485_table.item(item, values=values)
                edit_win.destroy()
            
            ttk.Button(edit_win, text="保存", command=save_edit, 
                    style='Primary.TButton').pack(pady=5)

    def validate_hex_length(self, value):
        """驗證MODBUS指令長度不超過10位十六進制"""
        if len(value) > 10:
            return False
        return self.validate_hex(value)

    def generate_rs485_command(self):
        """生成RS485指令並更新指定通訊組欄位"""
        try:
            group = self.rs485_group_combo.get()
            addr = self.rs485_addr_entry.get().zfill(2)
            func = self.rs485_func_combo.get().split(":")[0].zfill(2)
            start = self.rs485_start_entry.get().zfill(4)
            length = self.rs485_length_entry.get().zfill(4)
            modbus_cmd = f"{addr}{func}{start}{length}"

            for item in self.rs485_table.get_children():
                if self.rs485_table.item(item, 'values')[0] == group:
                    self.rs485_table.item(item, values=(group, modbus_cmd))
                    break

            self.append_receive_text(f"已生成MODBUS指令: {modbus_cmd}\n")
        except Exception as e:
            messagebox.showerror("錯誤", f"生成指令失敗: {str(e)}")


    def read_rs485_settings(self):
        """讀取RS485設定並更新表格"""
        response = self.send_at_command("AT+RTUEXTMB")
        #self.append_receive_text("正在讀取RS485設定...\n")

        if response:
            try:
                for item in self.rs485_table.get_children():
                    self.rs485_table.item(item, values=(self.rs485_table.item(item, 'values')[0], ""))

                lines = response.splitlines()  # 分行解析
                for line in lines:
                    if ":" in line:
                        index_str, cmd = line.split(":", 1)
                        index = index_str.strip()
                        cmd = cmd.strip().replace(" ", "")
                        for item in self.rs485_table.get_children():
                            if self.rs485_table.item(item, 'values')[0] == index:
                                self.rs485_table.item(item, values=(index, cmd))
                                break
            except Exception as e:
                self.append_receive_text(f"解析 RS485 設定失敗: {e}\n")



    def send_rs485_settings(self):
        """發送全部 RS485 設定"""
        try:
            for item in self.rs485_table.get_children():
                group, modbus_cmd = self.rs485_table.item(item, 'values')
                if not modbus_cmd:
                    continue
                command = f"AT+RTUEXTMB={group} {modbus_cmd}" 
                response = self.send_at_command(command)  # 傳送指令
                self.append_receive_text(f"{command}\n{response.strip()}\n") 
        except Exception as e:
            messagebox.showerror("錯誤", f"發送 RS485 設定失敗: {str(e)}")


    def show_other_settings(self):
        """顯示其他設置"""
        self.clear_content_frame()
        
        # 測試上傳數據格式框架
        frame1 = ttk.LabelFrame(self.content_frame, text="15. 測試上傳數據格式",  style='Bordered.TLabelframe')
        frame1.pack(fill=tk.X, pady=5, padx=5)
        
        # 顯示資料與格式按鈕
        ttk.Button(frame1, text="顯示資料與格式", command=self.show_data_format).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 封包測試輸入框
        ttk.Label(frame1, text="封包測試:").pack(side=tk.LEFT, padx=5, pady=5)
        self.packet_test_entry = ttk.Entry(frame1, width=15)
        self.packet_test_entry.pack
        # 封包測試輸入框
        ttk.Label(frame1, text="封包測試:").pack(side=tk.LEFT, padx=5, pady=5)
        self.packet_test_entry = ttk.Entry(frame1, width=15)
        self.packet_test_entry.pack(side=tk.LEFT, padx=5, pady=5)
        
        # PIN值按鈕
        ttk.Button(frame1, text="PIN值", command=self.show_pin_value).pack(side=tk.LEFT, padx=5, pady=5)
        
        #清空RTU紀錄數據
        frame2 = ttk.LabelFrame(self.content_frame, text="16. 清空RTU紀錄數據",  style='Bordered.TLabelframe')
        frame2.pack(fill=tk.X, pady=5, padx=5)
        # 讓第一欄自動延展
        frame2.columnconfigure(0, weight=1)
        # 建立按鈕，放在欄 1，靠右
        ttk.Button(frame2, text="清空", command=lambda: self.send_at_command("AT+RTUCNFSV"), style='Danger.TButton').grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        
        # 指令模式框架
        frame3 = ttk.LabelFrame(self.content_frame, text="18. 指令模式",  style='Bordered.TLabelframe')
        frame3.pack(fill=tk.X, pady=5, padx=5)
        
        # 指令輸入框
        self.command_entry = ttk.Entry(frame3)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        
        # 發送按鈕
        ttk.Button(frame3, text="送出", command=self.send_manual_command, style='Primary.TButton').pack(side=tk.LEFT, padx=5, pady=5)
        
        # 時間校正框架
        frame4 = ttk.LabelFrame(self.content_frame, text="20. 時間校正",  style='Bordered.TLabelframe')
        frame4.pack(fill=tk.X, pady=5, padx=5)
        
        # 傳訊器時間
        ttk.Label(frame4, text="傳訊器時間:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.device_time_entry = ttk.Entry(frame4, width=20)
        self.device_time_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 讀取和校正按鈕
        ttk.Button(frame4, text="讀取", command=self.read_device_time).grid(row=0, column=2, padx=5, pady=5)
        ttk.Button(frame4, text="校正同步本地時間", command=self.sync_local_time, style='Primary.TButton').grid(row=0, column=3, padx=5, pady=5)
    
    def show_wifi_settings(self):
        """顯示WIFI設定，整頁灰色背景，內容滾動"""

        self.clear_content_frame()

        style = ttk.Style()
        style.configure("Gray.TFrame", background="#f0f0f0")
        style.configure("Gray.TLabelframe", background="#f0f0f0")
        style.configure("Gray.TLabelframe.Label", background="#f0f0f0")

        # 創建滾動畫布，背景灰色
        canvas = tk.Canvas(self.content_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=canvas.yview)

        # scrollable_frame 也設定灰底 style
        scrollable_frame = ttk.Frame(canvas, style="Gray.TFrame")

        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        scrollable_frame.bind("<Configure>", on_configure)

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 綁定滑鼠滾輪事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # === 41. WIFI啟用設定 ===
        frame1 = ttk.LabelFrame(scrollable_frame, text="41. WIFI啟用設定", style='Gray.TLabelframe')
        frame1.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(frame1, text="是否關閉:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_enable_combo = ttk.Combobox(frame1, values=["未設定", "0:關閉", "1:打開"], state="readonly", width=10)
        self.wifi_enable_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_enable_combo.set("未設定")

        ttk.Label(frame1, text="通道:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_channel_combo = ttk.Combobox(frame1,
                                            values=[str(i) for i in range(12)] + ["AUTO"],
                                            state="readonly", width=10)
        self.wifi_channel_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_channel_combo.set("0")

        ttk.Button(frame1, text="讀取", command=self.read_wifi_device).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame1, text="送出", command=self.send_wifi_device, style='Primary.TButton').grid(row=0, column=4, padx=5, pady=5)

        # === 42. WIFI熱點參數 ===
        frame2 = ttk.LabelFrame(scrollable_frame, text="42. WIFI熱點參數", style='Gray.TLabelframe')
        frame2.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(frame2, text="SSID:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_ssid_entry = ttk.Entry(frame2, width=30)
        self.wifi_ssid_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame2, text="加密方式:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_encrypt_combo = ttk.Combobox(frame2, values=["PSK2:PSK2加密", "NONE:不加密"], state="readonly", width=15)
        self.wifi_encrypt_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_encrypt_combo.set("PSK2:PSK2加密")

        ttk.Label(frame2, text="密碼:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_password_entry = ttk.Entry(frame2, width=30, show='*')
        self.wifi_password_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Button(frame2, text="讀取", command=self.read_wifi_hotspot).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame2, text="送出", command=self.send_wifi_hotspot, style='Primary.TButton').grid(row=0, column=4, padx=5, pady=5)

        # === 43. WIFI熱點DHCP服務開關 ===
        frame3 = ttk.LabelFrame(scrollable_frame, text="43. WIFI熱點DHCP服務開關", style='Gray.TLabelframe')
        frame3.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(frame3, text="DHCP開關:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_dhcp_combo = ttk.Combobox(frame3, values=["未設定", "0:關閉DHCP服務", "1:打開DHCP服務"], state="readonly", width=20)
        self.wifi_dhcp_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_dhcp_combo.set("未設定")

        ttk.Button(frame3, text="讀取", command=self.read_wifi_dhcp).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame3, text="送出", command=self.send_wifi_dhcp, style='Primary.TButton').grid(row=0, column=4, padx=5, pady=5)

        # === 44. DHCP服務配置 ===
        frame4 = ttk.LabelFrame(scrollable_frame, text="44. DHCP服務配置", style='Gray.TLabelframe')
        frame4.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(frame4, text="起始偏移數:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.dhcp_start_frame = ttk.Frame(frame4, style="Gray.TFrame")
        self.dhcp_start_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        self.dhcp_start_entry = ttk.Entry(self.dhcp_start_frame, width=10)
        self.dhcp_start_entry.pack(side=tk.LEFT)
        self.dhcp_start_entry.insert(0, "0")

        ttk.Button(self.dhcp_start_frame, text="▲", width=2, command=lambda: self.increment_value(self.dhcp_start_entry)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.dhcp_start_frame, text="▼", width=2, command=lambda: self.decrement_value(self.dhcp_start_entry)).pack(side=tk.LEFT, padx=2)

        ttk.Label(frame4, text="總個數:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.dhcp_limit_frame = ttk.Frame(frame4, style="Gray.TFrame")
        self.dhcp_limit_frame.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        self.dhcp_limit_entry = ttk.Entry(self.dhcp_limit_frame, width=10)
        self.dhcp_limit_entry.pack(side=tk.LEFT)
        self.dhcp_limit_entry.insert(0, "150")

        ttk.Button(self.dhcp_limit_frame, text="▲", width=2, command=lambda: self.increment_value(self.dhcp_limit_entry)).pack(side=tk.LEFT, padx=2)
        ttk.Button(self.dhcp_limit_frame, text="▼", width=2, command=lambda: self.decrement_value(self.dhcp_limit_entry)).pack(side=tk.LEFT, padx=2)

        ttk.Button(frame4, text="讀取", command=self.read_dhcp_config).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame4, text="送出", command=self.send_dhcp_config, style='Primary.TButton').grid(row=0, column=4, padx=5, pady=5)

        # === 45. WIFI終端配置 ===
        frame5 = ttk.LabelFrame(scrollable_frame, text="45. WIFI終端配置", style='Gray.TLabelframe')
        frame5.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(frame5, text="WIFI終端開關:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_combo = ttk.Combobox(frame5, values=["未設定", "0:關閉DHCP服務", "1:打開DHCP服務"], state="readonly", width=20)
        self.wifi_client_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_client_combo.set("未設定")

        ttk.Label(frame5, text="SSID:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_ssid_entry = ttk.Entry(frame5, width=30)
        self.wifi_client_ssid_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame5, text="認證模式:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_auth_combo = ttk.Combobox(frame5, values=["NONE", "WPA2PSK"], state="readonly", width=15)
        self.wifi_client_auth_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_client_auth_combo.set("WPA2PSK")

        ttk.Label(frame5, text="加密模式:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_encrypt_combo = ttk.Combobox(frame5, values=["AES", "TKIPAES"], state="readonly", width=15)
        self.wifi_client_encrypt_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_client_encrypt_combo.set("AES")

        ttk.Label(frame5, text="密碼:").grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_password_entry = ttk.Entry(frame5, width=30, show='*')
        self.wifi_client_password_entry.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Button(frame5, text="讀取", command=self.read_wifi_client).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame5, text="送出", command=self.send_wifi_client, style='Primary.TButton').grid(row=0, column=4, padx=5, pady=5)

        # === 46. WIFI終端IP配置 ===
        frame6 = ttk.LabelFrame(scrollable_frame, text="46. WIFI終端IP配置", style='Gray.TLabelframe')
        frame6.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(frame6, text="IP模式:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_ip_combo = ttk.Combobox(frame6, values=["未設定", "DHCP:動態獲取", "STATIC:靜態設定"], state="readonly", width=20)
        self.wifi_client_ip_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.wifi_client_ip_combo.set("未設定")

        ttk.Label(frame6, text="靜態IP地址:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_ip_entry = ttk.Entry(frame6, width=20)
        self.wifi_client_ip_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(frame6, text="子網路遮罩:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.wifi_client_netmask_entry = ttk.Entry(frame6, width=20)
        self.wifi_client_netmask_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Button(frame6, text="讀取", command=self.read_wifi_client_ip).grid(row=0, column=3, padx=5, pady=5)
        ttk.Button(frame6, text="送出", command=self.send_wifi_client_ip, style='Primary.TButton').grid(row=0, column=4, padx=5, pady=5)

        # === 47. WIFI配置立即生效 ===
        frame7 = ttk.LabelFrame(scrollable_frame, text="47. WIFI配置立即生效", style='Gray.TLabelframe')
        frame7.pack(fill=tk.X, pady=5, padx=5)

        ttk.Button(frame7, text="立即生效", command=lambda: self.send_at_command("AT+WIFIRELOAD"), style='Primary.TButton').pack(padx=5, pady=5)

        # === 48. 列出WIFI熱點 ===
        frame8 = ttk.LabelFrame(scrollable_frame, text="48. 列出WIFI熱點", style='Gray.TLabelframe')
        frame8.pack(fill=tk.X, pady=5, padx=5)

        ttk.Button(frame8, text="列出熱點", command=lambda: self.send_at_command("AT+WIFILIST"), style='Primary.TButton').pack(padx=5, pady=5)

    
    def increment_value(self, var, step=1):
        try:
            val = int(var.get())
            var.set(str(val + step))
        except ValueError:
            var.set("1")

    def decrement_value(self, var, step=1):
        try:
            val = int(var.get())
            if val - step >= 0:
                var.set(str(val - step))
        except ValueError:
            var.set("0")

    
    def show_data_format(self):
        """顯示資料與格式"""
        self.send_at_command("AT+RTURECORD")
        messagebox.showinfo("資料格式", "當前上傳數據格式: " + self.upload_format_combo.get())
        
    
    def show_pin_value(self):
        """顯示PIN值"""
        pin = simpledialog.askstring("PIN值", "請輸入PIN值:")
        if pin:
            self.append_receive_text(f"PIN值設置為: {pin}\n")
    
    def send_manual_command(self):
        """發送手動指令"""
        command = self.command_entry.get().strip()
        if command:
            self.send_at_command(command)
    
    def read_device_time(self):
        """讀取設備時間"""
        self.send_at_command("AT+RTUTIME")
    
    def sync_local_time(self):
        """同步本地時間"""
        now = datetime.datetime.now()
        time_str = now.strftime("%Y%m%d%H%M%S")
        self.send_at_command(f"AT+RTUTIME={time_str}")
    
    def read_sim_settings(self):
        """讀取SIM卡設置"""
        self.send_at_command("AT+CAPN")
    
    def send_sim_settings(self):
        """發送SIM卡設置"""
        apn = self.apn_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        auth = self.auth_combo.get().split(":")[1]  # 获取认证类型文字部分
        self.send_at_command(f"AT+CAPN={apn} -u{username} -p{password} -a{auth}")
    
    def read_reboot(self):
        """讀取重啟設置"""
        self.send_at_command("AT+RBTYPE")
    
    def send_reboot(self):
        """發送重啟設置"""
        reboot_time = self.reboot_entry.get()
        self.send_at_command(f"AT+RBTYPE={reboot_time}")
    
    def read_mode(self):
        """讀取模式設置"""
        self.send_at_command("AT+RBTYPE")
    
    def send_mode(self):
        """發送模式設置"""
        mode = "0" if self.mode_combo.get() == "主動" else "1"
        self.send_at_command(f"AT+RBTYPE={mode}")
    
    def read_server(self):
        """讀取伺服器設置"""
        self.send_at_command("AT+SERVER")
    
    def send_server(self):
        """發送伺服器設置"""
        ip = self.server_ip_entry.get()
        port = self.server_port_entry.get()
        proto = "0" if self.server_proto_combo.get() == "TCP" else "1"
        self.send_at_command(f"AT+SERVER={ip} {port} {proto}")
    
    def read_netdevip(self):
        """讀取網路設備IP設定，顯示於表格"""
        def worker():
            response = self.send_at_command("AT+NETDEVIP")  # 實際AT指令

            print("設備回應：\n", response)  # debug用

            if not response:
                self.append_receive_text("未收到回應\n")
                print(response)  # debug用
                return

            try:
                # 清除現有表格
                for item in self.netdevip_tree.get_children():
                    self.netdevip_tree.delete(item)

                row_index = 0  # 加入 row 計數器

                for line in response.splitlines():
                    line = line.strip()
                    if not line or ':' not in line:
                        continue

                    # 拆成：index 與 剩下的 IP資訊
                    index_part, data_part = line.split(":", 1)
                    index = index_part.strip()
                    parts = [p.strip() for p in data_part.split(",")]

                    if len(parts) == 3:
                        ip, netmask, mac = parts
                        print(f"插入表格: {index}, {ip}, {netmask}, {mac}")  # debug

                        tag = 'evenrow' if row_index % 2 == 0 else 'oddrow'  # 加上交錯顏色
                        self.netdevip_tree.insert("", tk.END, values=(index, ip, netmask, mac), tags=(tag,))
                        row_index += 1

            except Exception as e:
                self.append_receive_text(f"解析錯誤: {e}\n")

        threading.Thread(target=worker).start()


    def send_netdevip(self):
        """一次發送表格中所有網絡設備IP設置"""
        all_items = self.netdevip_tree.get_children()
        if not all_items:
            messagebox.showwarning("提示", "表格中沒有任何資料")
            return

        for item in all_items:
            values = self.netdevip_tree.item(item, "values")
            if len(values) < 4:
                messagebox.showerror("錯誤", f"第 {item} 列資料不足，跳過該列")
                continue
            ip = values[1]       # IP位址
            mask = values[2]     # 子網掩碼
            gateway = ""         # 依需求修改，若有欄位可改為 values[x]
            dns = ""
            self.send_at_command(f"AT+NETDEVIP={ip} {mask} {gateway} {dns}")
            # 可視需求增加延遲，避免指令發送太快
            time.sleep(0.1)

    
    def read_upload_settings(self):
        """讀取上傳設置"""
        self.send_at_command("AT+RTUCONF")
    
    def send_upload_settings(self):
        """發送上傳設置"""
        sample = self.sample_interval_entry.get()
        upload = self.upload_interval_entry.get()
        save = self.save_interval_entry.get()
        power = self.power_mode_combo.get().split(":")[0]
        self.send_at_command(f"AT+RTUCONF=-s{sample} -u{upload} -r{save} -h{power}")
    
    def read_upload_format(self):
        """讀取上傳格式"""
        self.send_at_command("AT+ENHP")
    
    def send_upload_format(self):
        """發送上傳格式"""
        format_val = self.upload_format_combo.get().split(":")[0]
        station = self.rtu_station_entry.get()
        port = self.rtu_port_entry.get()
        self.send_at_command(f"AT+ENHP={format_val} {station} {port}")
    
    def read_ai_signal_settings(self):
        def worker():
            response = self.send_at_command("AT+RTUPINCNF")
            self.append_receive_text(f"收到回應:{response}\n")
            self.root.after(0, lambda: self.parse_ai_signal_response(response))
            if not response:
                self.append_receive_text("未收到 AI 訊號設定回應\n")
                return
            try:
                # 尋找 +RTUPINCNF: 開頭的行並解析
                for line in response.splitlines():
                    if line.startswith("+RTUPINCNF:"):
                        values = line[len("+RTUPINCNF:"):].strip().split(',')
                        for i in range(min(len(values), 5)):
                            val = values[i]
                            if val == "0":
                                channel_type = "0:不使用"
                            elif val == "1":
                                channel_type = "1:電壓"
                            elif val == "3":
                                channel_type = "3:電流"
                            elif val == "5":
                                channel_type = "5:IO輸入"
                            elif val == "6":
                                channel_type = "6:IO輸出"
                            elif val == "7":
                                channel_type = "7:計數"
                            elif val == "8":
                                channel_type = "8:計速"
                            else:
                                channel_type = val
                            self.ai_signal_tree.item(f"channel{i+1}", values=(f"通道{i+1}", channel_type))
            except Exception as e:
                self.append_receive_text(f"解析AI訊號設定失敗: {e}\n")
        threading.Thread(target=worker, daemon=True).start()

    def parse_ai_signal_response(self, response):
        try:
            if not hasattr(self, 'ai_signal_tree'):
                return
            for line in response.splitlines():
                if ':' in line:
                    parts = line.split(':', 1)
                    index = int(parts[0].strip())
                    values = parts[1].strip().split(',')
                    if len(values) >= 1:
                        ai_type = values[0].strip()
                        if ai_type == "0":
                            text = "0:不使用"
                        elif ai_type == "1":
                            text = "1:電壓"
                        elif ai_type == "3":
                            text = "3:電流"
                        elif ai_type == "5":
                            text = "5:IO輸入"
                        elif ai_type == "6":
                            text = "6:IO輸出"
                        elif ai_type == "7":
                            text = "7:計數"
                        elif ai_type == "8":
                            text = "8:計速"
                        else:
                            text = f"{ai_type}:未知"
                        iid = f"channel{index}"
                        if iid in self.ai_signal_tree.get_children():
                            self.ai_signal_tree.item(iid, values=(f"通道{index+1}", text))
        except Exception as e:
            self.append_receive_text(f"解析AI訊號設定失敗: {e}\n")

   


    def send_ai_signal_settings(self):
        """依照每個通道逐條發送 AI 訊號設定指令"""
        try:
            for i in range(20):  # 共 20 通道
                iid = f"channel{i}"
                if iid not in self.ai_signal_tree.get_children():
                    continue

                item = self.ai_signal_tree.item(iid)
                value = item['values'][1] if item['values'] else "0:不使用"
                ai_type = value.split(":")[0].strip()

                if ai_type not in ['0', '1', '3', '5', '6', '7', '8']:
                    ai_type = '0'  # 防呆處理

                # 預設警報為 0
                command = f"AT+RTUPINCNF={i} -t{ai_type} -a0"

                # 根據類型補參數
                if ai_type == '5':  # IO輸入
                    command += " -r1"
                elif ai_type == '6':  # IO輸出
                    command += " -i0"

                # 發送指令（單通道）
                response = self.send_at_command(command)
                self.append_receive_text(f"{command}\n{response.strip()}\n")

        except Exception as e:
            self.append_receive_text(f"送出 AI 設定失敗: {e}\n")


    
    def read_ai_linear_settings(self):
        def worker():
            response = self.send_at_command("AT+RTUCALI")
            self.append_receive_text(f"收到回應:\n{response}\n")
            self.root.after(0, lambda: self.parse_ai_linear_response(response))
            # 檢查是否有回應
            if not response:
                self.append_receive_text("未收到 AI 線性設定回應\n")
                return
            try:
                for line in response.splitlines():
                    if line.startswith("+RTUCALAD:"):
                        parts = line[len("+RTUCALAD:"):].strip().split()
                        slope = "500000"
                        offset = "0"
                        resistance = "250"
                        for part in parts:
                            if part.startswith("-s"):
                                slope = part[2:]
                            elif part.startswith("-o"):
                                offset = part[2:]
                            elif part.startswith("-r"):
                                resistance = part[2:]
                        for i in range(1, 6):
                            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                            self.ai_linear_tree.item(f"linear{i}", values=(f"通道{i}", slope, offset, resistance), tags=(tag,))
            except Exception as e:
                self.append_receive_text(f"解析AI線性設定失敗: {e}\n")
        threading.Thread(target=worker, daemon=True).start()

    def parse_ai_linear_response(self, response):
        try:
            if not hasattr(self, 'ai_linear_tree'):
                return
            for line in response.splitlines():
                if ':' in line:
                    parts = line.split(':', 1)
                    index = int(parts[0].strip())
                    values = parts[1].strip().split(',')
                    if len(values) >= 3:
                        slope = values[0].strip()
                        offset = values[1].strip()
                        resistance = values[2].strip()
                        iid = f"linear{index}"
                        if iid in self.ai_linear_tree.get_children():
                            self.ai_linear_tree.item(iid, values=(f"通道{index+1}", slope, offset, resistance))
        except Exception as e:
            self.append_receive_text(f"解析AI線性設定失敗: {e}\n")



    def send_ai_linear_settings(self):
        """逐通道送出 AI 線性設定（0~7通道）"""
        try:
            for i in range(8):  # 送出前 8 通道 (linear0 ~ linear7)
                item = self.ai_linear_tree.item(f"linear{i}")
                values = item.get('values', [])

                slope = values[1] if len(values) > 1 and values[1] else "500000"
                offset = values[2] if len(values) > 2 and values[2] else "0"
                resistance = values[3] if len(values) > 3 and values[3] else "250"

                command = f"AT+RTUCALI={i} -s{slope} -o{offset} -r{resistance}"
                response = self.send_at_command(command)
                self.append_receive_text(f"{command}\n{response.strip()}\n")

        except Exception as e:
            self.append_receive_text(f"送出 AI 線性設定失敗: {e}\n")


    
    def read_port_forward_settings(self):
        """讀取PORT轉發設置"""
        self.send_at_command("AT+DNATCNF")
    
    def read_wifi_device(self):
        """讀取WIFI設備設置"""
        self.send_at_command("AT+WIFIDEV")
    
    def send_wifi_device(self):
        """發送WIFI設備設置"""
        enable = "0" if "關閉" in self.wifi_enable_combo.get() else "1"
        channel = self.wifi_channel_combo.get()
        if channel == "AUTO":
            channel = "255"
        self.send_at_command(f"AT+WIFIDEV={enable} {channel}")
    
    def read_wifi_hotspot(self):
        """讀取WIFI熱點設置"""
        response = self.send_at_command("AT+WIFISAP")
        self.append_receive_text(f"WIFI熱點回應:\n{response}\n")

        # 處理回應格式: +WIFISAP=ssid password encrypt
        try:
            for line in response.splitlines():
                if line.startswith("+WIFISAP="):
                    parts = line[len("+WIFISAP="):].strip().split()
                    if len(parts) == 3:
                        ssid, password, encrypt = parts

                        # 更新欄位
                        self.wifi_ssid_entry.delete(0, tk.END)
                        self.wifi_ssid_entry.insert(0, ssid)

                        self.wifi_password_entry.delete(0, tk.END)
                        self.wifi_password_entry.insert(0, password)

                        if encrypt == "1":
                            self.wifi_encrypt_combo.set("PSK2:PSK2加密")
                        else:
                            self.wifi_encrypt_combo.set("NONE:不加密")
                    break
        except Exception as e:
            self.append_receive_text(f"解析WIFI熱點設定失敗: {e}\n")

    
    def send_wifi_hotspot(self):
        """發送WIFI熱點設置"""
        ssid = self.wifi_ssid_entry.get()
        password = self.wifi_password_entry.get()
        encrypt = "psk2" if self.wifi_encrypt_combo.get().startswith("none") else "0"
        self.send_at_command(f"AT+WIFISAP=ssid {ssid} encryption {encrypt} key {password}")
    
    def read_wifi_dhcp(self):
        """讀取WIFI DHCP設置"""
        self.send_at_command("AT+WIFIDHCP")
    
    def send_wifi_dhcp(self):
        """發送WIFI DHCP設置"""
        dhcp = "0" if "關閉" in self.wifi_dhcp_combo.get() else "1"
        self.send_at_command(f"AT+WIFIDHCP=maindhcp {dhcp}")
    
    def read_dhcp_config(self):
        """讀取DHCP配置"""
        self.send_at_command("AT+WIFIDHCPCF")
    
    def send_dhcp_config(self):
        """發送DHCP配置"""
        start = self.dhcp_start_entry.get()
        limit = self.dhcp_limit_entry.get()
        self.send_at_command(f"AT+WIFIDHCPCF={start},{limit}")
    
    def read_wifi_client(self):
        """讀取WIFI終端設置"""
        self.send_at_command("AT+WIFICLI")
    
    def send_wifi_client(self):
        """發送WIFI終端設置"""
        enable = "1" if "打開" in self.wifi_client_combo.get() else "0"
        ssid = self.wifi_client_ssid_entry.get()
        auth = self.wifi_client_auth_combo.get()
        encrypt = self.wifi_client_encrypt_combo.get()
        password = self.wifi_client_password_entry.get()
        self.send_at_command(f"AT+WIFICLI={enable},{ssid},{auth},{encrypt},{password}")
    
    def read_wifi_client_ip(self):
        """讀取WIFI終端IP設置"""
        self.send_at_command("AT+WIFICLIIP")
    
    def send_wifi_client_ip(self):
        """發送WIFI終端IP設置"""
        mode = "DHCP" if "DHCP" in self.wifi_client_ip_combo.get() else "STATIC"
        ip = self.wifi_client_ip_entry.get()
        netmask = self.wifi_client_netmask_entry.get()
        self.send_at_command(f"AT+WIFICLIIP={mode},{ip},{netmask}")

if __name__ == "__main__":
    root = tk.Tk()
    splash = SplashScreen(root)
    root.withdraw()
    def start_main():
        splash.destroy()
        root.deiconify()
        IoTDeviceConfigTool(root)
    root.after(500, start_main)  # 過場動畫顯示0.5秒
    root.mainloop()
