# -*- coding: utf-8 -*-
"""
Created on Sun Jun 22 14:02:59 2025

@author: asuta
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import json

PASSWORD = "user01"
DATA_FILE = "image_data.json"

class ImageLauncherApp:
    DEFAULT_DATA = [
        ["C:/Users/22341072/Downloads/Blue_Archive_JP_logo.png", ""],
        ["C:/Users/22341072/Downloads/logo_obt.png", ""],
        ["C:/Users/22341072/Downloads/logo_totk.png", ""]
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("画像ランチャー")
        self.root.configure(bg='white')

        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")

        self.image_data = self.load_data()
        self.index = 0

        self.load_images()
        self.create_widgets()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data == self.DEFAULT_DATA:
                        return self.DEFAULT_DATA
                    return data
            except Exception as e:
                messagebox.showerror("読み込みエラー", f"データファイルの読み込みに失敗しました：\n{e}")
                return self.DEFAULT_DATA
        else:
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.DEFAULT_DATA, f, indent=2, ensure_ascii=False)
            return self.DEFAULT_DATA

    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.image_data, f, indent=2, ensure_ascii=False)

    def load_images(self):
        self.images = []
        for path, _ in self.image_data:
            try:
                img = Image.open(path).resize((self.screen_width - 600, self.screen_height - 500))
                self.images.append(ImageTk.PhotoImage(img))
            except Exception as e:
                print(f"[画像読み込みエラー] {path} → {e}")
                self.images.append(None)

    def create_widgets(self):
        title_frame = tk.Frame(self.root, bg='white')
        title_frame.place(x=20, y=10)

        tk.Label(title_frame, text="ゲームセレクター", bg='white', fg='black',
                 font=("HGP創英角ﾎﾟｯﾌﾟ体", 60)).pack(anchor='w')
        tk.Label(title_frame, text="クリックでゲームを遊ぶ", bg='white', fg='gray',
                 font=("HGP創英角ﾎﾟｯﾌﾟ体", 30)).pack(anchor='w')

        self.left_btn = tk.Button(self.root, text="←", font=("Arial", 28), command=self.prev_image, bg='white')
        self.left_btn.pack(side='left', padx=30)

        if self.images[self.index]:
            self.img_btn = tk.Button(self.root, image=self.images[self.index], command=self.confirm_and_launch, bd=0, bg='white')
        else:
            self.img_btn = tk.Button(self.root, text="画像が読み込めません", font=("Arial", 20), command=self.confirm_and_launch, bg='white', width=40, height=10)
        self.img_btn.pack(side='left', expand=True)

        self.right_btn = tk.Button(self.root, text="→", font=("Arial", 28), command=self.next_image, bg='white')
        self.right_btn.pack(side='left', padx=30)

        self.edit_btn = tk.Button(self.root, text="⚙ 編集", font=("Arial", 12), bg='lightgray', command=self.request_password)
        self.edit_btn.place(relx=1.0, rely=0.0, anchor='ne', x=-20, y=20)

    def prev_image(self):
        self.index = (self.index - 1) % len(self.image_data)
        self.update_image()

    def next_image(self):
        self.index = (self.index + 1) % len(self.image_data)
        self.update_image()

    def update_image(self):
        if self.images[self.index]:
            self.img_btn.config(image=self.images[self.index], text="")
        else:
            self.img_btn.config(image="", text="画像が読み込めません")

    def confirm_and_launch(self):
        exec_path = self.image_data[self.index][1]
        if not exec_path or not os.path.isfile(exec_path):
            messagebox.showwarning("未設定", "この画像には実行ファイルが設定されていません。")
            return
        if messagebox.askyesno("ゲーム起動", "このゲームを始めますか？"):
            try:
                os.startfile(exec_path)
            except Exception as e:
                messagebox.showerror("実行失敗", f"実行できませんでした：\n{e}")

    def request_password(self):
        pw_win = tk.Toplevel(self.root)
        pw_win.title("パスワード認証")
        pw_win.geometry("300x120")
        pw_win.configure(bg='white')

        tk.Label(pw_win, text="パスワードを入力：", bg='white').pack(pady=10)
        pw_entry = tk.Entry(pw_win, show="●", width=20)
        pw_entry.pack()
        tk.Button(pw_win, text="OK", command=lambda: self.check_password(pw_entry.get(), pw_win)).pack(pady=10)

    def check_password(self, entry, win):
        if entry == PASSWORD:
            win.destroy()
            self.open_editor()
        else:
            messagebox.showerror("認証失敗", "パスワードが正しくありません。")

    def open_editor(self):
        editor = tk.Toplevel(self.root)
        editor.title("編集モード")
        editor.geometry("660x600")
        editor.configure(bg='white')

        temp_data = self.image_data.copy()

        def update_ui():
            for widget in editor.winfo_children():
                widget.destroy()

            for i, (img_path, exe_path) in enumerate(temp_data):
                frame = tk.Frame(editor, bg='white')
                frame.pack(fill='x', pady=5, padx=10)

                label = f"{i+1}: {os.path.basename(img_path)} | 実行: {os.path.basename(exe_path) if exe_path else '未設定'}"
                tk.Label(frame, text=label, bg='white').pack(side='left', padx=5)

                tk.Button(frame, text="画像変更", command=lambda i=i: self.replace_image(temp_data, i, update_ui, editor)).pack(side='left', padx=5)
                tk.Button(frame, text="実行ファイル", command=lambda i=i: self.set_exec(temp_data, i, update_ui, editor)).pack(side='left', padx=5)

                if i >= 3:
                    tk.Button(frame, text="削除", fg='red', command=lambda i=i: self.delete_entry(temp_data, i, update_ui)).pack(side='left', padx=5)

            tk.Button(editor, text="＋ 画像追加", command=lambda: self.add_entry(temp_data, update_ui, editor)).pack(pady=10)
            tk.Button(editor, text="💾 保存", font=("Arial", 12), bg='lightblue',
                      command=lambda: self.commit_changes(temp_data, editor)).pack(pady=15)

        update_ui()

    def replace_image(self, data, index, refresh, parent_win):
        path = filedialog.askopenfilename(parent=parent_win, filetypes=[("画像ファイル", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            data[index][0] = path
            refresh()

    def set_exec(self, data, index, refresh, parent_win):
        path = filedialog.askopenfilename(parent=parent_win, filetypes=[("実行ファイル", "*.exe")])
        if path:
            data[index][1] = path
            refresh()

    def delete_entry(self, data, index, refresh):
        if messagebox.askyesno("削除確認", "この画像を削除しますか？"):
            del data[index]
            refresh()

    def add_entry(self, data, refresh, parent_win):
        path = filedialog.askopenfilename(parent=parent_win, filetypes=[("画像ファイル", "*.png;*.jpg;*.jpeg;*.bmp")])
        if path:
            data.append([path, ""])
            refresh()

    def commit_changes(self, new_data, window):
        self.image_data = new_data
        self.index = min(self.index, len(self.image_data) - 1)
        self.save_data()
        self.load_images()
        self.update_image()
        window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLauncherApp(root)
    root.mainloop()
