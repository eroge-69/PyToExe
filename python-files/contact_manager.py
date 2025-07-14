import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import re
import os

class ContactManager:
    def __init__(self, root):
        self.root = root
        self.root.title("联系人管理系统")
        self.root.geometry("900x700")
        
        # 设置窗口图标和样式
        self.root.configure(bg='#f0f0f0')
        
        # 初始化数据库
        self.init_database()
        
        # 创建界面
        self.create_widgets()
        
        # 加载所有联系人
        self.load_contacts()
    
    def init_database(self):
        """初始化SQLite数据库"""
        # 获取程序所在目录
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包后的exe文件
            db_path = os.path.join(os.path.dirname(sys.executable), 'contacts.db')
        else:
            # 如果是普通python文件
            db_path = 'contacts.db'
        
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        
        # 创建联系人表
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                add_date TEXT NOT NULL,
                UNIQUE(name, phone)
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 主框架
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 标题
        title_label = tk.Label(main_frame, text="联系人管理系统", 
                              font=('微软雅黑', 16, 'bold'), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # 添加联系人区域
        add_frame = ttk.LabelFrame(main_frame, text="添加新联系人", padding="15")
        add_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # 姓名输入
        ttk.Label(add_frame, text="姓名:", font=('微软雅黑', 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.name_entry = ttk.Entry(add_frame, width=25, font=('微软雅黑', 10))
        self.name_entry.grid(row=0, column=1, padx=(0, 15))
        
        # 电话输入
        ttk.Label(add_frame, text="电话:", font=('微软雅黑', 10)).grid(row=0, column=2, sticky=tk.W, padx=(0, 8))
        self.phone_entry = ttk.Entry(add_frame, width=25, font=('微软雅黑', 10))
        self.phone_entry.grid(row=0, column=3, padx=(0, 15))
        
        # 添加按钮
        self.add_button = ttk.Button(add_frame, text="添加联系人", command=self.add_contact)
        self.add_button.grid(row=0, column=4, padx=(15, 0))
        
        # 搜索区域
        search_frame = ttk.LabelFrame(main_frame, text="搜索联系人", padding="15")
        search_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(search_frame, text="搜索:", font=('微软雅黑', 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))
        self.search_entry = ttk.Entry(search_frame, width=40, font=('微软雅黑', 10))
        self.search_entry.grid(row=0, column=1, padx=(0, 15))
        self.search_entry.bind('<KeyRelease>', self.search_contacts)
        
        # 清空搜索按钮
        ttk.Button(search_frame, text="清空搜索", command=self.clear_search).grid(row=0, column=2, padx=(15, 0))
        
        # 联系人列表
        list_frame = ttk.LabelFrame(main_frame, text="联系人列表", padding="15")
        list_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 创建Treeview
        columns = ('ID', '姓名', '电话', '添加日期')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18)
        
        # 定义列标题和宽度
        self.tree.heading('ID', text='编号')
        self.tree.heading('姓名', text='姓名')
        self.tree.heading('电话', text='电话')
        self.tree.heading('添加日期', text='添加日期')
        
        self.tree.column('ID', width=60, anchor='center')
        self.tree.column('姓名', width=200, anchor='center')
        self.tree.column('电话', width=200, anchor='center')
        self.tree.column('添加日期', width=300, anchor='center')
        
        # 设置字体
        style.configure("Treeview", font=('微软雅黑', 9))
        style.configure("Treeview.Heading", font=('微软雅黑', 10, 'bold'))
        
        # 滚动条
        scrollbar_v = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_h = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        # 布局
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar_v.grid(row=0, column=1, sticky=(tk.N, tk.S))
        scrollbar_h.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 操作按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(15, 0))
        
        ttk.Button(button_frame, text="删除选中联系人", command=self.delete_contact).pack(side=tk.LEFT, padx=(0, 15))
        
        # 统计信息
        self.stats_label = tk.Label(button_frame, text="总联系人数: 0", 
                                   font=('微软雅黑', 10), bg='#f0f0f0', fg='#34495e')
        self.stats_label.pack(side=tk.LEFT)
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # 绑定键盘事件
        self.name_entry.bind('<Return>', lambda e: self.phone_entry.focus())
        self.phone_entry.bind('<Return>', lambda e: self.add_contact())
        
        # 双击删除功能
        self.tree.bind('<Double-1>', self.on_double_click)
    
    def validate_phone(self, phone):
        """验证电话号码格式"""
        # 移除所有非数字字符
        phone = re.sub(r'[^\d]', '', phone)
        
        # 检查是否为有效的手机号码
        if len(phone) == 11 and phone.startswith(('13', '14', '15', '16', '17', '18', '19')):
            return phone
        # 检查固定电话
        elif len(phone) >= 7 and len(phone) <= 12:
            return phone
        else:
            return None
    
    def add_contact(self):
        """添加新联系人"""
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        if not name:
            messagebox.showerror("错误", "请输入姓名！")
            self.name_entry.focus()
            return
        
        if not phone:
            messagebox.showerror("错误", "请输入电话号码！")
            self.phone_entry.focus()
            return
        
        # 验证电话号码
        validated_phone = self.validate_phone(phone)
        if not validated_phone:
            messagebox.showerror("错误", "电话号码格式不正确！\n请输入11位手机号或7-12位固定电话")
            self.phone_entry.focus()
            return
        
        # 检查是否已存在
        if self.is_duplicate(name, validated_phone):
            messagebox.showwarning("重复提醒", f"联系人已存在！\n姓名: {name}\n电话: {validated_phone}")
            return
        
        # 添加到数据库
        try:
            add_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO contacts (name, phone, add_date) VALUES (?, ?, ?)",
                (name, validated_phone, add_date)
            )
            self.conn.commit()
            
            # 清空输入框
            self.name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            
            # 刷新列表
            self.load_contacts()
            
            messagebox.showinfo("成功", f"联系人添加成功！\n姓名: {name}\n电话: {validated_phone}")
            
            # 焦点回到姓名输入框
            self.name_entry.focus()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "添加联系人失败，数据库错误！")
    
    def is_duplicate(self, name, phone):
        """检查是否为重复联系人"""
        self.cursor.execute(
            "SELECT COUNT(*) FROM contacts WHERE name = ? OR phone = ?",
            (name, phone)
        )
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def load_contacts(self):
        """加载所有联系人到列表"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 从数据库加载
        self.cursor.execute("SELECT id, name, phone, add_date FROM contacts ORDER BY add_date DESC")
        contacts = self.cursor.fetchall()
        
        for contact in contacts:
            self.tree.insert('', 'end', values=contact)
        
        # 更新统计信息
        self.update_stats()
    
    def search_contacts(self, event=None):
        """搜索联系人"""
        search_term = self.search_entry.get().strip()
        
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not search_term:
            # 如果搜索框为空，显示所有联系人
            self.load_contacts()
            return
        
        # 搜索匹配的联系人
        self.cursor.execute(
            "SELECT id, name, phone, add_date FROM contacts WHERE name LIKE ? OR phone LIKE ? ORDER BY add_date DESC",
            (f'%{search_term}%', f'%{search_term}%')
        )
        contacts = self.cursor.fetchall()
        
        for contact in contacts:
            self.tree.insert('', 'end', values=contact)
        
        # 更新统计信息
        self.update_stats()
    
    def clear_search(self):
        """清空搜索"""
        self.search_entry.delete(0, tk.END)
        self.load_contacts()
    
    def delete_contact(self):
        """删除选中的联系人"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("提醒", "请先选择要删除的联系人！")
            return
        
        # 获取选中的联系人信息
        contact_data = self.tree.item(selected_item[0])['values']
        contact_id = contact_data[0]
        contact_name = contact_data[1]
        contact_phone = contact_data[2]
        
        # 确认删除
        if messagebox.askyesno("确认删除", f"确定要删除以下联系人吗？\n\n姓名: {contact_name}\n电话: {contact_phone}"):
            try:
                self.cursor.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
                self.conn.commit()
                
                # 刷新列表
                self.load_contacts()
                
                messagebox.showinfo("成功", f"联系人 {contact_name} 已删除！")
                
            except sqlite3.Error as e:
                messagebox.showerror("错误", f"删除失败：{str(e)}")
    
    def on_double_click(self, event):
        """双击事件处理"""
        selected_item = self.tree.selection()
        if selected_item:
            contact_data = self.tree.item(selected_item[0])['values']
            contact_name = contact_data[1]
            contact_phone = contact_data[2]
            contact_date = contact_data[3]
            
            messagebox.showinfo("联系人详情", 
                              f"姓名: {contact_name}\n电话: {contact_phone}\n添加时间: {contact_date}")
    
    def update_stats(self):
        """更新统计信息"""
        total_contacts = len(self.tree.get_children())
        self.stats_label.config(text=f"总联系人数: {total_contacts}")
    
    def __del__(self):
        """关闭数据库连接"""
        if hasattr(self, 'conn'):
            self.conn.close()

def main():
    root = tk.Tk()
    app = ContactManager(root)
    
    # 处理窗口关闭事件
    def on_closing():
        if hasattr(app, 'conn'):
            app.conn.close()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 让窗口居中显示
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":
    import sys
    main()