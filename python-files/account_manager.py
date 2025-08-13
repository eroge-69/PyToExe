import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import csv
import json
import re

class AccountManager:
    def __init__(self, root):
        self.root = root
        self.root.title("账号管理工具")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # 设置中文字体支持
        self.style = ttk.Style()
        self.style.configure("Treeview.Heading", font=("SimHei", 10, "bold"))
        self.style.configure("Treeview", font=("SimHei", 10), rowheight=25)
        
        # 数据存储
        self.accounts = []
        self.data_file = "accounts.json"
        
        # 加载已有数据
        self.load_data()
        
        # 创建界面
        self.create_widgets()
    
    def create_widgets(self):
        # 创建菜单栏
        self.create_menu()
        
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建表格
        columns = ("角色名", "等级", "账号", "密码", "邮箱", "邮箱密码")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        # 设置列宽
        column_widths = [150, 80, 180, 150, 200, 150]
        for col, width in zip(columns, column_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar_y = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 放置表格和滚动条
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 创建按钮框架
        button_frame = ttk.Frame(main_frame, padding="10")
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 按钮
        buttons = [
            ("添加账号", self.add_account),
            ("编辑账号", self.edit_account),
            ("删除账号", self.delete_account),
            ("导入TXT", self.import_from_txt),
            ("导出TXT", self.export_to_txt),
            ("清空数据", self.clear_all)
        ]
        
        for text, command in buttons:
            btn = ttk.Button(button_frame, text=text, command=command, width=12)
            btn.pack(fill=tk.X, pady=5)
        
        # 刷新表格数据
        self.refresh_table()
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="导入TXT", command=self.import_from_txt)
        file_menu.add_command(label="导出TXT", command=self.export_to_txt)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="关于", command=self.show_about)
        help_menu.add_command(label="使用说明", command=self.show_help)
        menubar.add_cascade(label="帮助", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def refresh_table(self):
        # 清空表格
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # 重新填充表格
        for account in self.accounts:
            self.tree.insert("", tk.END, values=(
                account["角色名"],
                account["等级"],
                account["账号"],
                account["密码"],
                account["邮箱"],
                account["邮箱密码"]
            ))
    
    def add_account(self):
        self.show_account_dialog("添加账号")
    
    def edit_account(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个账号")
            return
        
        index = self.tree.index(selected_item[0])
        self.show_account_dialog("编辑账号", index)
    
    def show_account_dialog(self, title, index=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 初始值
        initial_values = {
            "角色名": "",
            "等级": "",
            "账号": "",
            "密码": "",
            "邮箱": "",
            "邮箱密码": ""
        }
        
        if index is not None:
            initial_values = self.accounts[index]
        
        # 创建输入框
        entries = {}
        labels = ["角色名:", "等级:", "账号:", "密码:", "邮箱:", "邮箱密码:"]
        
        for i, label_text in enumerate(labels):
            frame = ttk.Frame(dialog, padding="5")
            frame.pack(fill=tk.X, padx=20)
            
            label = ttk.Label(frame, text=label_text, width=10)
            label.pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame)
            entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)
            entry.insert(0, initial_values[label_text[:-1]])
            
            entries[label_text[:-1]] = entry
        
        # 按钮框架
        btn_frame = ttk.Frame(dialog, padding="10")
        btn_frame.pack(fill=tk.X)
        
        def save_account():
            # 验证邮箱格式
            email = entries["邮箱"].get()
            if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("错误", "请输入有效的邮箱地址")
                return
            
            # 验证等级为数字
            level = entries["等级"].get()
            if level and not level.isdigit():
                messagebox.showerror("错误", "等级必须是数字")
                return
            
            # 保存数据
            account_data = {
                "角色名": entries["角色名"].get(),
                "等级": entries["等级"].get(),
                "账号": entries["账号"].get(),
                "密码": entries["密码"].get(),
                "邮箱": entries["邮箱"].get(),
                "邮箱密码": entries["邮箱密码"].get()
            }
            
            if index is None:
                self.accounts.append(account_data)
            else:
                self.accounts[index] = account_data
            
            self.save_data()
            self.refresh_table()
            dialog.destroy()
        
        # 按钮
        ttk.Button(btn_frame, text="保存", command=save_account).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.RIGHT, padx=10)
    
    def delete_account(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("警告", "请先选择一个账号")
            return
        
        if messagebox.askyesno("确认", "确定要删除选中的账号吗？"):
            index = self.tree.index(selected_item[0])
            del self.accounts[index]
            self.save_data()
            self.refresh_table()
    
    def import_from_txt(self):
        file_path = filedialog.askopenfilename(
            title="选择TXT文件",
            filetypes=[("TXT文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                # 读取文件内容
                lines = file.readlines()
                
                # 验证文件格式
                if not lines:
                    messagebox.showwarning("警告", "文件为空")
                    return
                
                # 检查标题行
                header = lines[0].strip().split(',')
                required_fields = ["角色名", "等级", "账号", "密码", "邮箱", "邮箱密码"]
                if header != required_fields:
                    messagebox.showerror("错误", "文件格式不正确，第一行应为：角色名,等级,账号,密码,邮箱,邮箱密码")
                    return
                
                # 导入数据
                new_accounts = []
                for i, line in enumerate(lines[1:], start=2):
                    line = line.strip()
                    if not line:
                        continue
                        
                    fields = line.split(',')
                    if len(fields) != 6:
                        messagebox.showerror("错误", f"第{i}行格式不正确，应包含6个字段")
                        return
                    
                    # 简单验证
                    if fields[4] and not re.match(r"[^@]+@[^@]+\.[^@]+", fields[4]):
                        if not messagebox.askyesno("警告", f"第{i}行邮箱格式不正确，是否继续导入？"):
                            return
                    
                    if fields[1] and not fields[1].isdigit():
                        if not messagebox.askyesno("警告", f"第{i}行等级不是数字，是否继续导入？"):
                            return
                    
                    new_accounts.append({
                        "角色名": fields[0],
                        "等级": fields[1],
                        "账号": fields[2],
                        "密码": fields[3],
                        "邮箱": fields[4],
                        "邮箱密码": fields[5]
                    })
                
                # 询问是否替换现有数据
                if self.accounts and not messagebox.askyesno("确认", "是否替换现有数据？选择否将追加数据"):
                    self.accounts.extend(new_accounts)
                else:
                    self.accounts = new_accounts
                
                self.save_data()
                self.refresh_table()
                messagebox.showinfo("成功", f"成功导入{len(new_accounts)}个账号")
                
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")
    
    def export_to_txt(self):
        if not self.accounts:
            messagebox.showwarning("警告", "没有数据可导出")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存TXT文件",
            defaultextension=".txt",
            filetypes=[("TXT文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                # 写入标题行
                header = ["角色名", "等级", "账号", "密码", "邮箱", "邮箱密码"]
                file.write(','.join(header) + '\n')
                
                # 写入数据
                for account in self.accounts:
                    line = [
                        account["角色名"],
                        account["等级"],
                        account["账号"],
                        account["密码"],
                        account["邮箱"],
                        account["邮箱密码"]
                    ]
                    file.write(','.join(line) + '\n')
            
            messagebox.showinfo("成功", f"成功导出{len(self.accounts)}个账号到 {file_path}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")
    
    def clear_all(self):
        if not self.accounts:
            messagebox.showinfo("提示", "数据已为空")
            return
        
        if messagebox.askyesno("确认", "确定要清空所有数据吗？此操作不可恢复！"):
            self.accounts = []
            self.save_data()
            self.refresh_table()
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as file:
                json.dump(self.accounts, file, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败：{str(e)}")
    
    def load_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as file:
                    self.accounts = json.load(file)
        except Exception as e:
            messagebox.showerror("错误", f"加载数据失败：{str(e)}")
            self.accounts = []
    
    def show_about(self):
        messagebox.showinfo("关于", "账号管理工具 v1.0\n\n用于管理各类账号信息，支持导入导出TXT文件。")
    
    def show_help(self):
        help_text = """使用说明：

1. 添加账号：点击"添加账号"按钮，填写信息后保存。
2. 编辑账号：选择一个账号，点击"编辑账号"按钮修改信息。
3. 删除账号：选择一个账号，点击"删除账号"按钮。
4. 导入TXT：
   - TXT文件格式要求：
     第一行为标题行：角色名,等级,账号,密码,邮箱,邮箱密码
     后续每行一个账号信息，用逗号分隔
   - 示例：
     角色名,等级,账号,密码,邮箱,邮箱密码
     战士,50,zhanshi123,abc123,zs@example.com,zs123
     法师,45,fashi456,def456,fs@example.com,fs456

5. 导出TXT：将当前所有账号信息导出为TXT文件。

数据会自动保存到程序目录下的accounts.json文件中。
"""
        messagebox.showinfo("使用说明", help_text)

if __name__ == "__main__":
    root = tk.Tk()
    app = AccountManager(root)
    root.mainloop()
