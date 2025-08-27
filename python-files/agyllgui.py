import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

# 기본 설정
PROFILE_NAME = "PrinterProfile"
PATCH_COUNT = "300"

def run_targen():
    cmd = ["targen", "-v", "-d2", f"-f{PATCH_COUNT}", PROFILE_NAME]
    subprocess.run(cmd)
    messagebox.showinfo("완료", "테스트 차트 생성 완료!")

def run_printtarg():
    cmd = ["printtarg", "-v", "-iCM", "-h", f"-T{PATCH_COUNT}", PROFILE_NAME]
    subprocess.run(cmd)
    messagebox.showinfo("완료", "차트 출력용 파일 생성 완료!")

def select_scan_file():
    filepath = filedialog.askopenfilename(filetypes=[("TIFF files", "*.tif")])
    scan_entry.delete(0, tk.END)
    scan_entry.insert(0, filepath)

def run_scanin():
    scan_file = scan_entry.get()
    if not os.path.exists(scan_file):
        messagebox.showerror("오류", "스캔 파일을 찾을 수 없습니다.")
        return
    cmd = ["scanin", "-v", "-dipn", scan_file, f"{PROFILE_NAME}.cht", f"{PROFILE_NAME}.cie"]
    subprocess.run(cmd)
    messagebox.showinfo("완료", "스캔 데이터 추출 완료!")

def run_colprof():
    cmd = ["colprof", "-v", f"-D{PROFILE_NAME} Profile", "-qm", "-kp", "-i", "D50", "-o", "iso12647-2", PROFILE_NAME]
    subprocess.run(cmd)
    messagebox.showinfo("완료", f"프린터 프로파일 생성 완료!\n{PROFILE_NAME}.icc")

# GUI 구성
root = tk.Tk()
root.title("ArgyllCMS 프린터 프로파일링 도구")
root.geometry("400x300")

tk.Label(root, text="스캔된 TIFF 파일 선택:").pack(pady=5)
scan_entry = tk.Entry(root, width=40)
scan_entry.pack()
tk.Button(root, text="파일 선택", command=select_scan_file).pack(pady=5)

tk.Button(root, text="① 테스트 차트 생성 (targen)", command=run_targen).pack(pady=5)
tk.Button(root, text="② 차트 출력용 파일 생성 (printtarg)", command=run_printtarg).pack(pady=5)
tk.Button(root, text="③ 스캔 데이터 추출 (scanin)", command=run_scanin).pack(pady=5)
tk.Button(root, text="④ 프린터 프로파일 생성 (colprof)", command=run_colprof).pack(pady=5)

root.mainloop()