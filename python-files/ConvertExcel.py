import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import logging

class ExcelCleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Excel Cleaner - ลบแถวที่มีคำที่ระบุ")
        self.root.geometry("500x350")
        # ตัวแปรเก็บค่า
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.keyword = tk.StringVar(value="bank")
        self.case_sensitive = tk.BooleanVar(value=False)
        self.sheet_name = tk.StringVar()
        # ตั้งค่า logging
        logging.basicConfig(filename='excel_cleaner.log', level=logging.ERROR, 
                          format='%(asctime)s - %(levelname)s - %(message)s')
        # สร้าง UI
        self.create_widgets()
        
    def create_widgets(self):
        # Frame หลัก
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ส่วนเลือกไฟล์
        file_frame = ttk.LabelFrame(main_frame, text="เลือกไฟล์ Excel", padding=10)
        file_frame.pack(fill=tk.X, pady=5)
        ttk.Label(file_frame, text="ไฟล์ต้นทาง:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.input_path, width=40).grid(row=0, column=1, padx=5)
        ttk.Button(file_frame, text="เลือกไฟล์...", command=self.browse_input_file).grid(row=0, column=2)
        ttk.Label(file_frame, text="ไฟล์ปลายทาง:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(file_frame, textvariable=self.output_path, width=40).grid(row=1, column=1, padx=5)
        ttk.Button(file_frame, text="เลือกที่เก็บ...", command=self.browse_output_file).grid(row=1, column=2)
        # ส่วนตั้งค่า
        settings_frame = ttk.LabelFrame(main_frame, text="ตั้งค่า", padding=10)
        settings_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(settings_frame, text="คำที่ต้องการลบ:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.keyword, width=20).grid(row=0, column=1, sticky=tk.W, padx=5)
        ttk.Checkbutton(settings_frame, text="คำนึงถึงตัวพิมพ์ใหญ่เล็ก", variable=self.case_sensitive).grid(row=1, column=0, columnspan=2, sticky=tk.W)
        
        ttk.Label(settings_frame, text="ชีตที่ต้องการ (เว้นว่างสำหรับทุกชีต):").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(settings_frame, textvariable=self.sheet_name, width=20).grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=5)
        
        # ปุ่มดำเนินการ
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        ttk.Button(action_frame, text="Star", command=self.clean_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="ออก", command=self.confirm_exit).pack(side=tk.RIGHT, padx=5)
    
    def browse_input_file(self):
        filetypes = (
            ('Excel files', '*.xlsx *.xls'),
            ('All files', '*.*')
        )
        filename = filedialog.askopenfilename(
            title="เลือกไฟล์ Excel ต้นทาง",
            filetypes=filetypes
        )
        if filename:
            self.input_path.set(filename)
            if not self.output_path.get():
                path = Path(filename)
                self.output_path.set(str(path.parent / f"{path.stem}_cleaned.xlsx"))
    
    def browse_output_file(self):
        filetypes = (
            ('Excel files', '*.xlsx'),
            ('All files', '*.*')
        )
        filename = filedialog.asksaveasfilename(
            title="เลือกที่เก็บไฟล์ผลลัพธ์",
            filetypes=filetypes,
            defaultextension=".xlsx"
        )
        if filename:
            self.output_path.set(filename)
    
    def confirm_exit(self):
        if messagebox.askokcancel("ออก", "คุณต้องการออกจากโปรแกรมหรือไม่?"):
            self.root.destroy()
    
    def clean_file(self):
        # ตรวจสอบ input
        if not self.input_path.get():
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกไฟล์ต้นทาง")
            return
        if not self.keyword.get().strip():
            messagebox.showerror("ข้อผิดพลาด", "กรุณาระบุคำที่ต้องการค้นหา")
            return
            
        # แสดง progress bar
        self.progress.start()
        self.root.config(cursor="wait")
        self.root.update()
        
        try:
            cleaned_file = self.clean_excel_file(
                input_path=self.input_path.get(),
                output_path=self.output_path.get(),
                keyword=self.keyword.get().strip(),
                sheet_name=self.sheet_name.get() if self.sheet_name.get() else None,
                case_sensitive=self.case_sensitive.get()
            )
            messagebox.showinfo(
                "สำเร็จ", 
                f"ทำความสะอาดไฟล์เรียบร้อยแล้ว!\nไฟล์ผลลัพธ์ถูกบันทึกที่:\n{cleaned_file}"
            )
        except ValueError as ve:
            messagebox.showerror("ข้อผิดพลาด", str(ve))
            logging.error(f"ValueError: {str(ve)}")
        except FileNotFoundError as fe:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่พบไฟล์: {str(fe)}")
            logging.error(f"FileNotFoundError: {str(fe)}")
        except PermissionError as pe:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถเขียนไฟล์ได้: {str(pe)}")
            logging.error(f"PermissionError: {str(pe)}")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")
            logging.error(f"Unexpected error: {str(e)}")
        finally:
            self.progress.stop()
            self.root.config(cursor="")
    
    def clean_excel_file(self, input_path, output_path=None, keyword='bank', sheet_name=None, case_sensitive=False):
        input_path = Path(input_path)
        if not input_path.exists():
            raise FileNotFoundError(f"ไม่พบไฟล์ {input_path}")
            
        if output_path is None:
            output_path = input_path.parent / f"{input_path.stem}_cleaned.xlsx"
        else:
            output_path = Path(output_path)

        # เลือก engine ตามนามสกุลไฟล์
        read_engine = 'xlrd' if input_path.suffix.lower() == '.xls' else 'openpyxl'
        write_engine = 'openpyxl'

        try:
            excel_file = pd.ExcelFile(input_path, engine=read_engine)
        except Exception as e:
            raise ValueError(f"ไม่สามารถเปิดไฟล์ Excel ได้: {str(e)}")

        if sheet_name and sheet_name not in excel_file.sheet_names:
            raise ValueError(f"ไม่พบชีต '{sheet_name}' ในไฟล์")

        with pd.ExcelWriter(output_path, engine=write_engine) as writer:
            sheets = [sheet_name] if sheet_name else excel_file.sheet_names

            for sheet in sheets:
                try:
                    df = pd.read_excel(input_path, sheet_name=sheet, engine=read_engine)
                    # จัดการ NaN และแปลงเป็น string อย่างปลอดภัย
                    mask = df.apply(lambda row: row.apply(lambda x: str(x) if pd.notnull(x) else '')
                                  .str.contains(keyword, case=case_sensitive, na=False)).any(axis=1)
                    cleaned_df = df[~mask]
                    cleaned_df.to_excel(writer, sheet_name=sheet, index=False)
                except Exception as e:
                    raise ValueError(f"ข้อผิดพลาดขณะประมวลผลชีต '{sheet}': {str(e)}")
        return str(output_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = ExcelCleanerApp(root)
    root.mainloop()