import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class LuaMaster:
    def __init__(self, root):
        self.root = root
        self.root.title("LuaMaster")
        self.root.geometry("600x400")
        
        # Tạo frame chính chia làm 2 phần
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Phần 1: Tách Lua
        self.frame1 = tk.LabelFrame(self.main_frame, text="Tách File Lua", padx=10, pady=10)
        self.frame1.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=5)
        
        # Phần 2: Tạo Folder
        self.frame2 = tk.LabelFrame(self.main_frame, text="Tạo Folder theo File Lua", padx=10, pady=10)
        self.frame2.pack(fill=tk.BOTH, expand=True, side=tk.RIGHT, padx=5)
        
        # Khởi tạo giao diện cho phần 1
        self.init_part1()
        # Khởi tạo giao diện cho phần 2
        self.init_part2()
        
    def init_part1(self):
        # Input folder
        tk.Label(self.frame1, text="Thư mục Input:").pack(anchor=tk.W)
        self.input_entry1 = tk.Entry(self.frame1, width=30)
        self.input_entry1.pack(fill=tk.X, pady=(0,5))
        tk.Button(self.frame1, text="Chọn...", command=self.select_input1).pack(anchor=tk.E)
        
        # Output folder
        tk.Label(self.frame1, text="Thư mục Output:").pack(anchor=tk.W, pady=(10,0))
        self.output_entry = tk.Entry(self.frame1, width=30)
        self.output_entry.pack(fill=tk.X, pady=(0,5))
        tk.Button(self.frame1, text="Chọn...", command=self.select_output).pack(anchor=tk.E)
        
        # Nút tách Lua
        tk.Button(self.frame1, text="Tách Lua", command=self.extract_lua, bg="#4CAF50", fg="white").pack(pady=(15,5), fill=tk.X)
        
        # Thanh trạng thái
        self.status1 = tk.StringVar()
        self.status1.set("Sẵn sàng")
        tk.Label(self.frame1, textvariable=self.status1, fg="gray", anchor=tk.W).pack(fill=tk.X)
        
    def init_part2(self):
        # Input folder
        tk.Label(self.frame2, text="Thư mục Input:").pack(anchor=tk.W)
        self.input_entry2 = tk.Entry(self.frame2, width=30)
        self.input_entry2.pack(fill=tk.X, pady=(0,5))
        tk.Button(self.frame2, text="Chọn...", command=self.select_input2).pack(anchor=tk.E)
        
        # Nút tạo folder
        tk.Button(self.frame2, text="Tạo Folder", command=self.create_folders, bg="#2196F3", fg="white").pack(pady=(15,5), fill=tk.X)
        
        # Thanh trạng thái
        self.status2 = tk.StringVar()
        self.status2.set("Sẵn sàng")
        tk.Label(self.frame2, textvariable=self.status2, fg="gray", anchor=tk.W).pack(fill=tk.X)
        
    def select_input1(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_entry1.delete(0, tk.END)
            self.input_entry1.insert(0, folder)
            
    def select_input2(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_entry2.delete(0, tk.END)
            self.input_entry2.insert(0, folder)
            
    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)
            
    def extract_lua(self):
        input_dir = self.input_entry1.get()
        output_dir = self.output_entry.get()
        
        if not input_dir or not output_dir:
            messagebox.showerror("Lỗi", "Vui lòng chọn cả thư mục Input và Output")
            return
            
        self.status1.set("Đang tìm kiếm file .lua...")
        self.root.update()
        
        lua_files = []
        for root, dirs, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.lua'):
                    lua_files.append(os.path.join(root, file))
        
        if not lua_files:
            self.status1.set("Không tìm thấy file .lua nào")
            messagebox.showinfo("Thông báo", "Không có file .lua nào trong thư mục Input")
            return
            
        self.status1.set(f"Đang sao chép {len(lua_files)} file .lua...")
        self.root.update()
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            for lua_file in lua_files:
                shutil.copy2(lua_file, output_dir)
                
            self.status1.set(f"Hoàn thành! Đã sao chép {len(lua_files)} file .lua")
            messagebox.showinfo("Thông báo", f"Đã sao chép thành công {len(lua_files)} file .lua vào thư mục Output")
        except Exception as e:
            self.status1.set("Lỗi khi sao chép file")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")
            
    def create_folders(self):
        input_dir = self.input_entry2.get()
        
        if not input_dir:
            messagebox.showerror("Lỗi", "Vui lòng chọn thư mục Input")
            return
            
        self.status2.set("Đang tìm kiếm file .lua...")
        self.root.update()
        
        lua_files = []
        for file in os.listdir(input_dir):
            if file.lower().endswith('.lua'):
                lua_files.append(file)
        
        if not lua_files:
            self.status2.set("Không tìm thấy file .lua nào")
            messagebox.showinfo("Thông báo", "Không có file .lua nào trong thư mục Input")
            return
            
        self.status2.set(f"Đang tạo folder cho {len(lua_files)} file .lua...")
        self.root.update()
        
        try:
            created_count = 0
            for lua_file in lua_files:
                folder_name = os.path.splitext(lua_file)[0]
                folder_path = os.path.join(input_dir, folder_name)
                
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    created_count += 1
                    
            self.status2.set(f"Hoàn thành! Đã tạo {created_count} folder")
            messagebox.showinfo("Thông báo", f"Đã tạo thành công {created_count} folder")
        except Exception as e:
            self.status2.set("Lỗi khi tạo folder")
            messagebox.showerror("Lỗi", f"Có lỗi xảy ra: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = LuaMaster(root)
    root.mainloop()