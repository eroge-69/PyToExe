import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import threading


class ProgramRunnerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("自動化程式執行器")
        self.root.geometry("600x450")

        # 設置樣式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, font=('Microsoft YaHei', 10))
        self.style.configure("TLabel", font=('Microsoft YaHei', 10))

        # 主框架
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # 標題
        ttk.Label(self.main_frame, text="自動化程式執行器",
                  font=('Microsoft YaHei', 14, 'bold')).pack(pady=10)

        # 程式清單
        self.programs = [
            {
                "name": "CSV 轉 XLSX",
                "path": r"C:\Users\靚仔\Desktop\Coding\Python Coding\csv檔轉換成xlsx檔.py",
                "executable": sys.executable,
                "encoding": "utf-8"
            },
            {
                "name": "R 分析程式",
                "path": r"C:\Users\靚仔\Desktop\Coding\R\Ho Heng Iao.R",
                "executable": r"C:\Program Files\R\R-4.5.0\bin\Rscript.exe",
                "encoding": "utf-8"
            },
            {
                "name": "XLSX 合併 PDF",
                "path": r"C:\Users\靚仔\Desktop\Coding\Python Coding\xlsx檔合併為pdf檔.py",
                "executable": sys.executable,
                "encoding": "utf-8"
            }
        ]

        # 創建程式框架
        self.program_frames = []
        self.status_labels = []
        self.run_buttons = []

        for i, program in enumerate(self.programs):
            frame = ttk.Frame(self.main_frame)
            frame.pack(fill=tk.X, pady=5)
            self.program_frames.append(frame)

            # 程式名稱和狀態
            ttk.Label(frame, text=program["name"], width=15).pack(side=tk.LEFT)
            status_label = ttk.Label(frame, text="等待執行", foreground="gray")
            status_label.pack(side=tk.LEFT, padx=10)
            self.status_labels.append(status_label)

            # 單獨運行按鈕
            run_btn = ttk.Button(
                frame,
                text="運行",
                command=lambda idx=i: self.run_program(idx),
                width=5
            )
            run_btn.pack(side=tk.RIGHT)
            self.run_buttons.append(run_btn)

        # 主控制按鈕
        btn_frame = ttk.Frame(self.main_frame)
        btn_frame.pack(pady=15)

        self.run_all_btn = ttk.Button(
            btn_frame,
            text="運行所有程式",
            command=self.run_all_programs,
            style="Accent.TButton"
        )
        self.run_all_btn.pack(side=tk.LEFT, padx=5)

        self.clear_btn = ttk.Button(
            btn_frame,
            text="清空日誌",
            command=self.clear_log
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)

        # 日誌區域
        self.log_text = tk.Text(self.main_frame, height=12, state="disabled")
        self.scrollbar = ttk.Scrollbar(self.main_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 設置按鈕樣式
        self.style.map("Accent.TButton",
                       foreground=[('pressed', 'white'), ('active', 'white')],
                       background=[('pressed', '#0066cc'), ('active', '#0066cc')])
        self.style.configure("Accent.TButton", foreground="white", background="#0078d7")

    def log_message(self, message):
        """添加消息到日誌"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")

    def clear_log(self):
        """清空日誌"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")

    def run_program(self, index):
        """運行單個程式"""
        program = self.programs[index]
        self.status_labels[index].config(text="執行中...", foreground="blue")
        self.log_message(f"開始執行: {program['name']}")
        self.root.update()

        try:
            # 檢查程式檔是否存在
            if not os.path.exists(program["path"]):
                raise FileNotFoundError(f"找不到檔: {program['path']}")

            # 檢查執行檔是否存在(對於完整路徑)
            if os.path.isabs(program["executable"]) and not os.path.exists(program["executable"]):
                raise FileNotFoundError(f"找不到執行檔: {program['executable']}")

            # 準備命令
            cmd = [program["executable"], program["path"]]
            self.log_message(f"執行命令: {' '.join(cmd)}")

            # 解決編碼問題
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'

            # 運行進程(解決編碼問題)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                env=env,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

            # 捕獲輸出(使用執行緒避免阻塞)
            def read_output(pipe, pipe_name):
                for line in iter(pipe.readline, ''):
                    self.log_message(f"{program['name']} {pipe_name}: {line.strip()}")
                pipe.close()

            stdout_thread = threading.Thread(
                target=read_output,
                args=(process.stdout, "輸出")
            )
            stderr_thread = threading.Thread(
                target=read_output,
                args=(process.stderr, "錯誤")
            )

            stdout_thread.daemon = True
            stderr_thread.daemon = True

            stdout_thread.start()
            stderr_thread.start()

            # 等待進程完成
            return_code = process.wait()

            stdout_thread.join(timeout=0.1)
            stderr_thread.join(timeout=0.1)

            if return_code == 0:
                self.status_labels[index].config(text="執行成功", foreground="green")
                self.log_message(f"{program['name']} 執行成功")
            else:
                raise Exception(f"返回代碼: {return_code}")

        except Exception as e:
            self.status_labels[index].config(text="執行失敗", foreground="red")
            self.log_message(f"{program['name']} 錯誤: {str(e)}")
            if "Rscript" in str(e):
                self.log_message("提示: 請確認R語言已安裝且路徑正確")
                self.log_message(f"當前Rscript路徑: {program['executable']}")

    def run_all_programs(self):
        """運行所有程式"""
        self.run_all_btn.config(state="disabled")
        for btn in self.run_buttons:
            btn.config(state="disabled")

        self.log_message("\n=== 開始執行所有程式 ===")

        for i in range(len(self.programs)):
            self.run_program(i)
            self.root.update()

        self.log_message("=== 所有程式執行完畢 ===")
        self.run_all_btn.config(state="normal")
        for btn in self.run_buttons:
            btn.config(state="normal")

        messagebox.showinfo("完成", "所有程式已執行完畢!")


if __name__ == "__main__":
    # 設置系統編碼為UTF-8
    import io
    import locale

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

    root = tk.Tk()

    # 嘗試設置視窗圖示
    try:
        root.iconbitmap("icon.ico")
    except:
        pass

    app = ProgramRunnerApp(root)
    root.mainloop()

