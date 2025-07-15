import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import platform
from PIL import Image, ImageTk
import ctypes
import sys

# 确保中文显示正常
try:
    if platform.system() == "Windows":
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
except:
    pass

class EuropeHangAssistant:
    def __init__(self, root):
        self.root = root
        self.root.title("欧洲挂简易使用助手")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置中文字体
        self.font = ('Microsoft YaHei UI', 10)
        
        # 数据存储
        self.config_file = "europe_hang_config.json"
        self.config = self.load_config()
        
        # 创建主框架
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        self.tab_control = ttk.Notebook(self.main_frame)
        
        # 欢迎页
        self.welcome_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.welcome_tab, text="欢迎使用")
        
        # 按键说明页
        self.keys_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.keys_tab, text="常用按键")
        
        # 设置页
        self.setup_tabs = {}
        steps = ["队长设置", "队友设置", "打怪范围", "捡物设置", "启动设置"]
        for step in steps:
            tab = ttk.Frame(self.tab_control)
            self.tab_control.add(tab, text=step)
            self.setup_tabs[step] = tab
        
        # 保存/加载页
        self.save_tab = ttk.Frame(self.tab_control)
        self.tab_control.add(self.save_tab, text="保存/加载")
        
        # 放置标签页
        self.tab_control.pack(expand=1, fill="both")
        
        # 创建各个页面的内容
        self.create_welcome_page()
        self.create_keys_page()
        self.create_setup_pages()
        self.create_save_page()
        
        # 底部状态栏
        self.status_bar = ttk.Label(root, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定事件
        self.root.bind("<F1>", self.show_help)
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败: {str(e)}")
        return {}
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("成功", "配置已保存")
            self.status_bar.config(text="配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置失败: {str(e)}")
    
    def create_welcome_page(self):
        """创建欢迎页面"""
        # 标题
        ttk.Label(self.welcome_tab, text="欧洲挂简易使用助手", font=('Microsoft YaHei UI', 16, 'bold')).pack(pady=20)
        
        # 简介
        intro = """
        欢迎使用欧洲挂简易使用助手！本工具将帮助您快速上手欧洲挂，
        按照以下步骤设置，您将能够轻松使用挂机功能。
        
        主要功能：
        1. 提供详细的设置向导
        2. 保存和加载您的个性化配置
        3. 显示常用按键和操作指南
        4. 提供简单的使用帮助
        
        使用方法：
        1. 依次在各个标签页中完成设置
        2. 每完成一个步骤后建议保存配置
        3. 所有设置完成后，点击"启动"按钮开始挂机
        
        注意：每次更新设置后，请记得保存配置！
        """
        ttk.Label(self.welcome_tab, text=intro, font=self.font, justify=tk.LEFT).pack(padx=20, pady=10)
        
        # 图片或图标
        try:
            # 如果有图标可以显示在这里
            # img = Image.open("logo.png")
            # img = img.resize((200, 200), Image.LANCZOS)
            # photo = ImageTk.PhotoImage(img)
            # ttk.Label(self.welcome_tab, image=photo).pack(pady=20)
            # self.logo = photo  # 保持引用
            pass
        except:
            pass
        
        # 快速开始按钮
        ttk.Button(self.welcome_tab, text="开始设置", command=lambda: self.tab_control.select(2)).pack(pady=20)
    
    def create_keys_page(self):
        """创建常用按键页面"""
        ttk.Label(self.keys_page, text="欧洲挂常用按键", font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=10)
        
        keys_info = [
            ("Home", "呼出菜单（和行者一样）"),
            ("End", "启动/停止当前窗口（鼠标停留在哪个号就是哪个窗口）"),
            ("Ins", "启动/停止所有窗口（所有的多开号）"),
            ("Page Up", "上一个配置文件"),
            ("Page Down", "下一个配置文件"),
            ("Delete", "删除当前配置"),
            ("F1", "显示帮助信息")
        ]
        
        # 创建表格
        tree = ttk.Treeview(self.keys_page, columns=("key", "description"), show="headings", height=10)
        tree.heading("key", text="按键")
        tree.heading("description", text="功能描述")
        tree.column("key", width=100, anchor=tk.CENTER)
        tree.column("description", width=500)
        
        for key, desc in keys_info:
            tree.insert("", tk.END, values=(key, desc))
        
        tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 提示信息
        ttk.Label(self.keys_page, text="每个步骤完成后请保存配置，下次可直接读取使用。", 
                 font=self.font, foreground="red").pack(pady=10)
    
    def create_setup_pages(self):
        """创建设置页面"""
        # 队长设置
        self.create_captain_setup()
        
        # 队友设置
        self.create_teammate_setup()
        
        # 打怪范围设置
        self.create_monster_setup()
        
        # 捡物设置
        self.create_pickup_setup()
        
        # 启动设置
        self.create_start_setup()
    
    def create_captain_setup(self):
        """创建队长设置页面"""
        frame = self.setup_tabs["队长设置"]
        
        ttk.Label(frame, text="队长设置 - 自动邀请队友组队", font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=10)
        
        # 队友列表
        ttk.Label(frame, text="队友名称（用英文分号;分隔，最后一名队友后不要加符号）", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        teammates_var = tk.StringVar(value=self.config.get("teammates", ""))
        teammates_entry = ttk.Entry(frame, textvariable=teammates_var, width=60)
        teammates_entry.pack(fill=tk.X, padx=20, pady=5)
        
        # 其他设置
        ttk.Label(frame, text="其他队长设置", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        # 创建一个框架来容纳复选框
        check_frame = ttk.Frame(frame)
        check_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 复选框
        invite_auto_var = tk.BooleanVar(value=self.config.get("invite_auto", True))
        ttk.Checkbutton(check_frame, text="自动邀请", variable=invite_auto_var).pack(side=tk.LEFT, padx=10)
        
        accept_return_var = tk.BooleanVar(value=self.config.get("accept_return", True))
        ttk.Checkbutton(check_frame, text="接受回归", variable=accept_return_var).pack(side=tk.LEFT, padx=10)
        
        # 保存按钮
        def save_captain_settings():
            self.config["teammates"] = teammates_var.get()
            self.config["invite_auto"] = invite_auto_var.get()
            self.config["accept_return"] = accept_return_var.get()
            self.save_config()
        
        ttk.Button(frame, text="保存设置", command=save_captain_settings).pack(pady=20)
        
        # 提示信息
        ttk.Label(frame, text="设置完成后，请切换到下一个标签页继续设置队友。", 
                 font=self.font, foreground="blue").pack(pady=10)
    
    def create_teammate_setup(self):
        """创建队友设置页面"""
        frame = self.setup_tabs["队友设置"]
        
        ttk.Label(frame, text="队友设置 - 自动同意组队和战斗设置", font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=10)
        
        # 角色类型选择
        ttk.Label(frame, text="选择角色类型", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        role_var = tk.StringVar(value=self.config.get("role_type", "战士"))
        roles = ["战士", "法师", "奶妈"]
        
        role_frame = ttk.Frame(frame)
        role_frame.pack(fill=tk.X, padx=20, pady=5)
        
        for role in roles:
            ttk.Radiobutton(role_frame, text=role, variable=role_var, value=role).pack(side=tk.LEFT, padx=10)
        
        # 自动同意组队
        ttk.Label(frame, text="组队设置", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        accept_team_var = tk.BooleanVar(value=self.config.get("accept_team", True))
        ttk.Checkbutton(frame, text="自动同意组队", variable=accept_team_var).pack(padx=30, pady=5, anchor=tk.W)
        
        # 战斗设置
        ttk.Label(frame, text="战斗设置", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        follow_attack_var = tk.BooleanVar(value=self.config.get("follow_attack", True))
        ttk.Checkbutton(frame, text="跟随攻击", variable=follow_attack_var).pack(padx=30, pady=5, anchor=tk.W)
        
        # 奶妈特殊设置
        healer_frame = ttk.LabelFrame(frame, text="奶妈特殊设置", padding="10")
        healer_frame.pack(fill=tk.X, padx=20, pady=5)
        
        heal_skill_var = tk.StringVar(value=self.config.get("heal_skill", ""))
        ttk.Label(healer_frame, text="加血技能:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(healer_frame, textvariable=heal_skill_var, width=20).pack(side=tk.LEFT, padx=5)
        
        interval_var = tk.BooleanVar(value=self.config.get("heal_interval", False))
        ttk.Checkbutton(healer_frame, text="加血技能间隔时间", variable=interval_var).pack(side=tk.LEFT, padx=5)
        
        # 自我保护设置
        ttk.Label(frame, text="自我保护设置", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        self_heal_var = tk.BooleanVar(value=self.config.get("self_heal", True))
        ttk.Checkbutton(frame, text="自动给自己加血", variable=self_heal_var).pack(padx=30, pady=5, anchor=tk.W)
        
        low_hp_var = tk.IntVar(value=self.config.get("low_hp", 30))
        ttk.Label(frame, text="低血量百分比:").pack(padx=30, pady=5, anchor=tk.W)
        ttk.Scale(frame, from_=0, to=100, variable=low_hp_var, orient=tk.HORIZONTAL, length=300).pack(padx=30, pady=5)
        ttk.Label(frame, textvariable=low_hp_var).pack(padx=30, pady=0, anchor=tk.W)
        
        # 保存按钮
        def save_teammate_settings():
            self.config["role_type"] = role_var.get()
            self.config["accept_team"] = accept_team_var.get()
            self.config["follow_attack"] = follow_attack_var.get()
            self.config["heal_skill"] = heal_skill_var.get()
            self.config["heal_interval"] = interval_var.get()
            self.config["self_heal"] = self_heal_var.get()
            self.config["low_hp"] = low_hp_var.get()
            self.save_config()
        
        ttk.Button(frame, text="保存设置", command=save_teammate_settings).pack(pady=20)
        
        # 提示信息
        ttk.Label(frame, text="设置完成后，请切换到下一个标签页设置打怪范围。", 
                 font=self.font, foreground="blue").pack(pady=10)
    
    def create_monster_setup(self):
        """创建打怪范围设置页面"""
        frame = self.setup_tabs["打怪范围"]
        
        ttk.Label(frame, text="打怪范围设置", font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=10)
        
        # 地图选择
        ttk.Label(frame, text="选择地图", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        map_var = tk.StringVar(value=self.config.get("map", "新手村"))
        maps = ["新手村", "兽人部落", "精灵森林", "矮人矿洞", "龙穴"]
        
        map_combo = ttk.Combobox(frame, textvariable=map_var, values=maps, state="readonly")
        map_combo.pack(fill=tk.X, padx=20, pady=5)
        
        # 范围设置
        ttk.Label(frame, text="打怪范围设置", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        # 创建一个框架来容纳坐标设置
        coord_frame = ttk.Frame(frame)
        coord_frame.pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Label(coord_frame, text="左上角 X:").grid(row=0, column=0, padx=5, pady=5)
        left_x_var = tk.IntVar(value=self.config.get("left_x", 100))
        ttk.Entry(coord_frame, textvariable=left_x_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="左上角 Y:").grid(row=0, column=2, padx=5, pady=5)
        left_y_var = tk.IntVar(value=self.config.get("left_y", 100))
        ttk.Entry(coord_frame, textvariable=left_y_var, width=10).grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="右下角 X:").grid(row=1, column=0, padx=5, pady=5)
        right_x_var = tk.IntVar(value=self.config.get("right_x", 500))
        ttk.Entry(coord_frame, textvariable=right_x_var, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(coord_frame, text="右下角 Y:").grid(row=1, column=2, padx=5, pady=5)
        right_y_var = tk.IntVar(value=self.config.get("right_y", 500))
        ttk.Entry(coord_frame, textvariable=right_y_var, width=10).grid(row=1, column=3, padx=5, pady=5)
        
        # 避开障碍物
        avoid_obstacles_var = tk.BooleanVar(value=self.config.get("avoid_obstacles", True))
        ttk.Checkbutton(frame, text="避开障碍物", variable=avoid_obstacles_var).pack(padx=30, pady=5, anchor=tk.W)
        
        # 不打首领
        avoid_boss_var = tk.BooleanVar(value=self.config.get("avoid_boss", True))
        ttk.Checkbutton(frame, text="不打首领", variable=avoid_boss_var).pack(padx=30, pady=5, anchor=tk.W)
        
        # 不打宝箱
        avoid_chest_var = tk.BooleanVar(value=self.config.get("avoid_chest", True))
        ttk.Checkbutton(frame, text="不打宝箱", variable=avoid_chest_var).pack(padx=30, pady=5, anchor=tk.W)
        
        # 保存按钮
        def save_monster_settings():
            self.config["map"] = map_var.get()
            self.config["left_x"] = left_x_var.get()
            self.config["left_y"] = left_y_var.get()
            self.config["right_x"] = right_x_var.get()
            self.config["right_y"] = right_y_var.get()
            self.config["avoid_obstacles"] = avoid_obstacles_var.get()
            self.config["avoid_boss"] = avoid_boss_var.get()
            self.config["avoid_chest"] = avoid_chest_var.get()
            self.save_config()
        
        ttk.Button(frame, text="保存设置", command=save_monster_settings).pack(pady=20)
        
        # 提示信息
        ttk.Label(frame, text="设置完成后，请切换到下一个标签页设置捡物选项。", 
                 font=self.font, foreground="blue").pack(pady=10)
    
    def create_pickup_setup(self):
        """创建捡物设置页面"""
        frame = self.setup_tabs["捡物设置"]
        
        ttk.Label(frame, text="捡物设置", font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=10)
        
        # 角色类型选择（影响捡物）
        ttk.Label(frame, text="选择角色类型（影响捡物）", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        role_pickup_var = tk.StringVar(value=self.config.get("role_pickup", "战士"))
        roles = ["战士", "法师", "奶妈"]
        
        role_frame = ttk.Frame(frame)
        role_frame.pack(fill=tk.X, padx=20, pady=5)
        
        for role in roles:
            ttk.Radiobutton(role_frame, text=role, variable=role_pickup_var, value=role).pack(side=tk.LEFT, padx=10)
        
        # 捡物设置
        ttk.Label(frame, text="捡物选项", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        # 创建一个框架来容纳捡物选项
        pickup_frame = ttk.Frame(frame)
        pickup_frame.pack(fill=tk.X, padx=20, pady=5)
        
        # 药品
        pickup_health_var = tk.BooleanVar(value=self.config.get("pickup_health", True))
        ttk.Checkbutton(pickup_frame, text="生命药水", variable=pickup_health_var).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        pickup_mana_var = tk.BooleanVar(value=self.config.get("pickup_mana", True))
        ttk.Checkbutton(pickup_frame, text="魔法药水", variable=pickup_mana_var).grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 装备
        pickup_equipment_var = tk.BooleanVar(value=self.config.get("pickup_equipment", True))
        ttk.Checkbutton(pickup_frame, text="装备", variable=pickup_equipment_var).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 金币
        pickup_gold_var = tk.BooleanVar(value=self.config.get("pickup_gold", True))
        ttk.Checkbutton(pickup_frame, text="金币", variable=pickup_gold_var).grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 特殊物品
        pickup_special_var = tk.BooleanVar(value=self.config.get("pickup_special", True))
        ttk.Checkbutton(pickup_frame, text="特殊物品", variable=pickup_special_var).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # 自定义物品
        ttk.Label(frame, text="自定义捡取物品（用英文分号;分隔）", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        custom_items_var = tk.StringVar(value=self.config.get("custom_items", ""))
        ttk.Entry(frame, textvariable=custom_items_var, width=60).pack(fill=tk.X, padx=20, pady=5)
        
        # 保存按钮
        def save_pickup_settings():
            self.config["role_pickup"] = role_pickup_var.get()
            self.config["pickup_health"] = pickup_health_var.get()
            self.config["pickup_mana"] = pickup_mana_var.get()
            self.config["pickup_equipment"] = pickup_equipment_var.get()
            self.config["pickup_gold"] = pickup_gold_var.get()
            self.config["pickup_special"] = pickup_special_var.get()
            self.config["custom_items"] = custom_items_var.get()
            self.save_config()
        
        ttk.Button(frame, text="保存设置", command=save_pickup_settings).pack(pady=20)
        
        # 提示信息
        ttk.Label(frame, text="设置完成后，请切换到下一个标签页设置启动选项。", 
                 font=self.font, foreground="blue").pack(pady=10)
    
    def create_start_setup(self):
        """创建启动设置页面"""
        frame = self.setup_tabs["启动设置"]
        
        ttk.Label(frame, text="启动设置", font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=10)
        
        # 启动前确认
        ttk.Label(frame, text="请确认您已完成所有设置并保存", font=self.font, foreground="red").pack(padx=20, pady=10, anchor=tk.W)
        
        # 显示当前配置摘要
        ttk.Label(frame, text="当前配置摘要", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        # 创建一个文本框显示配置摘要
        config_text = tk.Text(frame, height=10, width=70, wrap=tk.WORD)
        config_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # 填充配置摘要
        def update_config_summary():
            config_text.delete(1.0, tk.END)
            if not self.config:
                config_text.insert(tk.END, "未找到配置，请先完成设置并保存。")
                return
                
            summary = "配置摘要:\n\n"
            summary += f"队长设置: {self.config.get('teammates', '未设置')}\n"
            summary += f"角色类型: {self.config.get('role_type', '未设置')}\n"
            summary += f"地图选择: {self.config.get('map', '未设置')}\n"
            summary += f"打怪范围: ({self.config.get('left_x', 0)}, {self.config.get('left_y', 0)}) - ({self.config.get('right_x', 0)}, {self.config.get('right_y', 0)})\n"
            summary += f"捡物设置: 生命药水({self.config.get('pickup_health', False)}), 魔法药水({self.config.get('pickup_mana', False)})\n"
            
            config_text.insert(tk.END, summary)
        
        # 刷新摘要按钮
        ttk.Button(frame, text="刷新配置摘要", command=update_config_summary).pack(pady=10)
        
        # 启动按钮
        def start_hang():
            update_config_summary()
            if not self.config:
                messagebox.showerror("错误", "请先完成设置并保存配置！")
                return
                
            # 这里应该启动欧洲挂程序
            # 由于不知道具体路径，我们模拟启动
            messagebox.showinfo("启动", "欧洲挂已启动！\n\n请使用以下快捷键控制：\n- Home: 呼出菜单\n- End: 启动/停止当前窗口\n- Ins: 启动/停止所有窗口")
            
            # 模拟启动命令
            try:
                # 实际应用中，替换为真实的启动命令
                if platform.system() == "Windows":
                    # subprocess.Popen(["path/to/europe_hang.exe"])
                    pass
                elif platform.system() == "Linux":
                    # subprocess.Popen(["path/to/europe_hang"])
                    pass
                elif platform.system() == "Darwin":
                    # subprocess.Popen(["open", "path/to/europe_hang.app"])
                    pass
            except Exception as e:
                messagebox.showerror("启动失败", f"无法启动欧洲挂: {str(e)}\n\n请确保程序已正确安装。")
        
        ttk.Button(frame, text="启动欧洲挂", command=start_hang, style='Accent.TButton').pack(pady=20)
        
        # 提示信息
        ttk.Label(frame, text="启动后，请使用Home键呼出菜单，Ins键启动所有窗口。", 
                 font=self.font, foreground="blue").pack(pady=10)
    
    def create_save_page(self):
        """创建保存/加载页面"""
        frame = self.save_tab
        
        ttk.Label(frame, text="保存/加载配置", font=('Microsoft YaHei UI', 14, 'bold')).pack(pady=10)
        
        # 配置文件列表
        ttk.Label(frame, text="配置文件", font=self.font).pack(padx=20, pady=5, anchor=tk.W)
        
        # 创建一个框架来容纳文件列表和按钮
        file_frame = ttk.Frame(frame)
        file_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # 左侧列表框显示配置文件
        config_files = self.get_config_files()
        config_listbox = tk.Listbox(file_frame, width=40, height=10)
        config_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # 填充列表
        for file in config_files:
            config_listbox.insert(tk.END, file)
        
        # 右侧按钮
        button_frame = ttk.Frame(file_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 刷新按钮
        def refresh_files():
            config_listbox.delete(0, tk.END)
            for file in self.get_config_files():
                config_listbox.insert(tk.END, file)
        
        ttk.Button(button_frame, text="刷新", command=refresh_files).pack(fill=tk.X, pady=5)
        
        # 保存配置按钮
        save_name_var = tk.StringVar(value="我的配置")
        ttk.Label(button_frame, text="配置名称:").pack(pady=5, anchor=tk.W)
        ttk.Entry(button_frame, textvariable=save_name_var).pack(fill=tk.X, pady=5)
        
        def save_current_config():
            config_name = save_name_var.get()
            if not config_name:
                messagebox.showerror("错误", "请输入配置名称！")
                return
                
            config_file = f"{config_name}.json"
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("成功", f"配置已保存为: {config_file}")
                refresh_files()
            except Exception as e:
                messagebox.showerror("错误", f"保存配置失败: {str(e)}")
        
        ttk.Button(button_frame, text="保存当前配置", command=save_current_config).pack(fill=tk.X, pady=5)
        
        # 加载配置按钮
        def load_selected_config():
            selected_index = config_listbox.curselection()
            if not selected_index:
                messagebox.showerror("错误", "请先选择一个配置文件！")
                return
                
            config_file = config_listbox.get(selected_index)
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                messagebox.showinfo("成功", f"已加载配置: {config_file}")
                self.status_bar.config(text=f"已加载配置: {config_file}")
            except Exception as e:
                messagebox.showerror("错误", f"加载配置失败: {str(e)}")
        
        ttk.Button(button_frame, text="加载选中配置", command=load_selected_config).pack(fill=tk.X, pady=5)
        
        # 删除配置按钮
        def delete_selected_config():
            selected_index = config_listbox.curselection()
            if not selected_index:
                messagebox.showerror("错误", "请先选择一个配置文件！")
                return
                
            config_file = config_listbox.get(selected_index)
            if messagebox.askyesno("确认", f"确定要删除配置文件 '{config_file}' 吗？"):
                try:
                    os.remove(config_file)
                    messagebox.showinfo("成功", f"已删除配置: {config_file}")
                    refresh_files()
                except Exception as e:
                    messagebox.showerror("错误", f"删除配置失败: {str(e)}")
        
        ttk.Button(button_frame, text="删除选中配置", command=delete_selected_config).pack(fill=tk.X, pady=5)
        
        # 提示信息
        ttk.Label(frame, text="配置文件将保存在程序运行目录下，扩展名为.json", 
                 font=self.font, foreground="blue").pack(pady=10)
    
    def get_config_files(self):
        """获取所有配置文件"""
        try:
            return [f for f in os.listdir('.') if f.endswith('.json') and f != self.config_file]
        except:
            return []
    
    def show_help(self, event=None):
        """显示帮助信息"""
        help_text = """
        欧洲挂简易使用助手帮助
        
        一、基本操作
        1. Home键 - 呼出/隐藏欧洲挂菜单
        2. End键 - 启动/停止当前鼠标所在窗口
        3. Ins键 - 启动/停止所有窗口
        4. Page Up/Down - 切换配置文件
        
        二、使用流程
        1. 在队长设置中输入队友名称并设置自动邀请
        2. 在队友设置中选择角色类型并设置自动同意组队
        3. 在打怪范围设置中选择地图并划定打怪区域
        4. 在捡物设置中选择需要拾取的物品
        5. 保存所有设置后，点击启动按钮开始挂机
        
        三、常见问题
        1. 无法启动：请确保欧洲挂已正确安装并能独立运行
        2. 无法组队：检查队长和队友的设置是否匹配
        3. 角色不行动：确认已按Ins键启动所有窗口
        
        四、注意事项
        - 每次修改设置后请务必保存
        - 建议定期备份重要配置
        - 本工具仅为辅助，不替代欧洲挂本身功能
        """
        messagebox.showinfo("帮助", help_text)

def main():
    # 创建应用程序
    root = tk.Tk()
    
    # 设置主题
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    
    # 自定义样式
    style.configure('Accent.TButton', font=('Microsoft YaHei UI', 12, 'bold'))
    
    # 创建助手实例
    app = EuropeHangAssistant(root)
    
    # 运行应用程序
    root.mainloop()

if __name__ == "__main__":
    main()    
