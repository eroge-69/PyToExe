#!/usr/bin/env python3
"""
SWF Encryptor - 图形化 Windows 可执行工具（Python + Tkinter）

功能：
- 选择单个或多个 SWF 文件，或选择包含 SWF 的文件夹（递归）
- 使用密码通过 PBKDF2(SHA256) 派生 AES-256-GCM 密钥并加密/解密文件
- 输出格式（自定义）：MAGIC(6) + ver(1) + iterations(4 big-endian) + salt(16) + iv(12) + ciphertext
- 可打包为单文件 EXE： pyinstaller --onefile --windowed swf_encryptor_gui.py

依赖：
- Python 3.8+
- cryptography

安装：
    pip install cryptography

打包（生成 swf_encryptor.exe）：
    pip install pyinstaller
    pyinstaller --onefile --windowed --add-data "path/to/your/icon.ico;." swf_encryptor_gui.py

注意：生成的 exe 将包含运行所需的 Python 运行时和依赖，用户无需额外安装 Python。

"""
import os
import sys
import struct
import threading
import secrets
import queue
from tkinter import Tk, Button, Listbox, Label, Entry, Scrollbar, Text, END, filedialog, SINGLE, MULTIPLE, VERTICAL, RIGHT, Y, LEFT, BOTH, Frame, ttk, BooleanVar, Checkbutton
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

MAGIC = b"SWFENC"  # 6 bytes
VERSION = 1

# header layout: MAGIC(6) + ver(1) + iterations(4 big-endian) + salt(16) + iv(12) + ciphertext


def derive_key(password: bytes, salt: bytes, iterations: int) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password)


class Worker(threading.Thread):
    def __init__(self, tasks, qlog):
        super().__init__()
        self.tasks = tasks
        self.qlog = qlog
        self.daemon = True

    def log(self, *args):
        self.qlog.put(' '.join(map(str, args)))

    def encrypt_file(self, path, password, iterations):
        try:
            self.log(f"开始加密: {path}")
            with open(path, 'rb') as f:
                data = f.read()
            salt = secrets.token_bytes(16)
            iv = secrets.token_bytes(12)
            key = derive_key(password.encode('utf-8'), salt, iterations)
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(iv, data, None)
            out = MAGIC + struct.pack('>B', VERSION) + struct.pack('>I', iterations) + salt + iv + ciphertext
            out_path = path + '.enc'
            with open(out_path, 'wb') as f:
                f.write(out)
            self.log(f"已生成: {out_path}")
        except Exception as e:
            self.log(f"加密失败 {path}: {e}")

    def decrypt_file(self, path, password):
        try:
            self.log(f"开始解密: {path}")
            with open(path, 'rb') as f:
                data = f.read()
            if not data.startswith(MAGIC):
                self.log(f"文件格式错误（MAGIC 不匹配）: {path}")
                return
            off = len(MAGIC)
            ver = data[off]
            off += 1
            if ver != VERSION:
                self.log(f"不支持的版本 {ver}：{path}")
                return
            iterations = struct.unpack('>I', data[off:off+4])[0]
            off += 4
            salt = data[off:off+16]
            off += 16
            iv = data[off:off+12]
            off += 12
            ciphertext = data[off:]
            key = derive_key(password.encode('utf-8'), salt, iterations)
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(iv, ciphertext, None)
            # 原始名
            if path.endswith('.enc'):
                out_path = path[:-4]
            else:
                out_path = path + '.dec'
            with open(out_path, 'wb') as f:
                f.write(plaintext)
            self.log(f"已生成: {out_path}")
        except Exception as e:
            self.log(f"解密失败 {path}: {e}")

    def run(self):
        for task in self.tasks:
            mode = task['mode']
            if mode == 'enc':
                self.encrypt_file(task['path'], task['password'], task['iterations'])
            else:
                self.decrypt_file(task['path'], task['password'])
        self.log('任务完成')


class App:
    def __init__(self, root):
        self.root = root
        root.title('SWF Encryptor - 图形化')
        root.geometry('820x520')

        top = Frame(root)
        top.pack(fill=BOTH, padx=10, pady=8)

        left = Frame(top)
        left.pack(side=LEFT, fill=BOTH, expand=True)

        Label(left, text='文件列表（选择后可移除）').pack(anchor='w')
        self.listbox = Listbox(left, selectmode=MULTIPLE)
        self.listbox.pack(fill=BOTH, expand=True, side=LEFT)
        sb = Scrollbar(left, orient=VERTICAL, command=self.listbox.yview)
        sb.pack(side=RIGHT, fill=Y)
        self.listbox.config(yscrollcommand=sb.set)

        btns = Frame(root)
        btns.pack(fill='x', padx=10)

        Button(btns, text='添加文件', command=self.add_files).pack(side='left')
        Button(btns, text='添加文件夹（递归）', command=self.add_folder).pack(side='left')
        Button(btns, text='移除选中', command=self.remove_selected).pack(side='left')
        Button(btns, text='清空列表', command=self.clear_list).pack(side='left')

        right = Frame(top)
        right.pack(side=LEFT, fill='y', padx=12)

        Label(right, text='密码:').pack(anchor='w')
        self.pwd_entry = Entry(right, width=30, show='*')
        self.pwd_entry.pack(anchor='w')

        Label(right, text='PBKDF2 迭代次数:').pack(anchor='w', pady=(8,0))
        self.iter_entry = Entry(right, width=12)
        self.iter_entry.insert(0, '200000')
        self.iter_entry.pack(anchor='w')

        self.recursive_var = BooleanVar(value=True)
        Checkbutton(right, text='添加文件夹时递归子目录', variable=self.recursive_var).pack(anchor='w', pady=(6,0))

        Button(right, text='加密选中', command=self.encrypt_selected, width=20).pack(pady=(12,4))
        Button(right, text='解密选中', command=self.decrypt_selected, width=20).pack()

        Label(root, text='日志').pack(anchor='w', padx=12, pady=(10,0))
        self.logbox = Text(root, height=10)
        self.logbox.pack(fill=BOTH, padx=12, pady=(0,12), expand=False)

        self.qlog = queue.Queue()
        self.root.after(200, self.poll_log)

    def add_files(self):
        paths = filedialog.askopenfilenames(title='选择文件', filetypes=[('SWF files','*.swf'), ('All files','*.*')])
        for p in paths:
            self.listbox.insert(END, p)

    def add_folder(self):
        folder = filedialog.askdirectory(title='选择文件夹')
        if not folder:
            return
        # 扫描 .swf 文件
        if self.recursive_var.get():
            for root_dir, dirs, files in os.walk(folder):
                for f in files:
                    if f.lower().endswith('.swf') or f.lower().endswith('.swf.enc'):
                        self.listbox.insert(END, os.path.join(root_dir, f))
        else:
            for f in os.listdir(folder):
                if f.lower().endswith('.swf') or f.lower().endswith('.swf.enc'):
                    self.listbox.insert(END, os.path.join(folder, f))

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        for i in reversed(sel):
            self.listbox.delete(i)

    def clear_list(self):
        self.listbox.delete(0, END)

    def poll_log(self):
        while not self.qlog.empty():
            msg = self.qlog.get()
            self.logbox.insert(END, msg + '\n')
            self.logbox.see(END)
        self.root.after(200, self.poll_log)

    def encrypt_selected(self):
        items = [self.listbox.get(i) for i in range(self.listbox.size()) if i in self.listbox.curselection()]
        if not items:
            self.qlog.put('请先选择要加密的文件')
            return
        pwd = self.pwd_entry.get()
        if not pwd:
            self.qlog.put('请输入密码')
            return
        try:
            iterations = int(self.iter_entry.get())
        except Exception:
            self.qlog.put('迭代次数必须为整数')
            return
        tasks = [{'mode':'enc','path':p,'password':pwd,'iterations':iterations} for p in items]
        worker = Worker(tasks, self.qlog)
        worker.start()

    def decrypt_selected(self):
        items = [self.listbox.get(i) for i in range(self.listbox.size()) if i in self.listbox.curselection()]
        if not items:
            self.qlog.put('请先选择要解密的文件')
            return
        pwd = self.pwd_entry.get()
        if not pwd:
            self.qlog.put('请输入密码')
            return
        tasks = [{'mode':'dec','path':p,'password':pwd} for p in items]
        worker = Worker(tasks, self.qlog)
        worker.start()


def main():
    root = Tk()
    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
