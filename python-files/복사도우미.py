import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os
import sys

def remove_path_limit():
    # Windows 10 이상에서 경로 제한 해제
    try:
        if sys.platform == 'win32':
            import winreg
            key = r'SYSTEM\\CurrentControlSet\\Control\\FileSystem'
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0, winreg.KEY_SET_VALUE) as reg:
                winreg.SetValueEx(reg, 'LongPathsEnabled', 0, winreg.REG_DWORD, 1)
    except Exception:
        pass  # 권한 없으면 무시

def run_robocopy(src, dst):
    cmd = [
        'robocopy',
        src,
        dst,
        '/E',  # 하위폴더 포함, 빈 폴더도
        '/NFL', '/NDL', '/NJH', '/NJS', '/NC', '/NS', '/NP',  # 로그 최소화
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode

def main():
    remove_path_limit()
    root = tk.Tk()
    root.title('복사도우미')
    root.geometry('400x200')

    src_folder = tk.StringVar()
    dst_folder = tk.StringVar()

    def select_src():
        folder = filedialog.askdirectory(title='원본폴더를 선택해주세요')
        if folder:
            src_folder.set(folder)

    def select_dst():
        folder = filedialog.askdirectory(title='대상폴더를 선택해주세요')
        if folder:
            dst_folder.set(folder)

    def do_copy():
        src = src_folder.get()
        dst = dst_folder.get()
        if not src or not dst:
            messagebox.showerror('오류', '폴더를 모두 선택해주세요.')
            return
        ret = run_robocopy(src, dst)
        if ret <= 7:
            messagebox.showinfo('성공', '복사 완료!')
        else:
            messagebox.showerror('실패', f'복사 실패! (코드: {ret})')

    def cancel():
        root.destroy()

    tk.Button(root, text='원본폴더를 선택해주세요', command=select_src).pack(pady=10)
    tk.Label(root, textvariable=src_folder).pack()
    tk.Button(root, text='대상폴더를 선택해주세요', command=select_dst).pack(pady=10)
    tk.Label(root, textvariable=dst_folder).pack()
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)
    tk.Button(btn_frame, text='확인', command=do_copy, width=10).pack(side='left', padx=10)
    tk.Button(btn_frame, text='취소', command=cancel, width=10).pack(side='right', padx=10)
    root.mainloop()

if __name__ == '__main__':
    main()
