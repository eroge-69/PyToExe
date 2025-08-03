# file: image_sorter_app.py

import os
import json
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

PRESET_FILE = "presets.json"
IMAGE_EXT = (".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff")


def load_presets():
    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_presets(presets):
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(presets, f, indent=2, ensure_ascii=False)


class ImageSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("画像分類アプリ")

        self.presets = load_presets()
        self.selected_files = []
        self.preset_vars = {}
        self.current_edit = None
        self.global_output = ""
        self.use_global_output = tk.BooleanVar(value=False)

        self.build_ui()

    def build_ui(self):
        edit_frame = ttk.LabelFrame(self.root, text="プリセット（作品）管理")
        edit_frame.pack(fill="x", padx=10, pady=5)

        top_row = ttk.Frame(edit_frame)
        top_row.pack(fill="x", pady=2)

        self.preset_combo = ttk.Combobox(top_row, state="readonly", values=list(self.presets.keys()))
        self.preset_combo.pack(side="left", padx=5, fill="x", expand=True)
        self.preset_combo.bind("<<ComboboxSelected>>", self.select_edit_preset)

        ttk.Button(top_row, text="＋作成", command=self.add_preset).pack(side="left", padx=2)
        ttk.Button(top_row, text="名前変更", command=self.rename_preset).pack(side="left", padx=2)
        ttk.Button(top_row, text="🗑削除", command=self.delete_preset).pack(side="left", padx=2)

        self.tag_listbox = tk.Listbox(edit_frame, height=5)
        self.tag_listbox.pack(fill="x", padx=5, pady=3)

        tag_entry_row = ttk.Frame(edit_frame)
        tag_entry_row.pack()
        self.tag_entry = ttk.Entry(tag_entry_row, width=30)
        self.tag_entry.pack(side="left", padx=5)
        ttk.Button(tag_entry_row, text="＋追加", command=self.add_tag).pack(side="left")
        ttk.Button(tag_entry_row, text="削除", command=self.remove_tag).pack(side="left")

        output_row = ttk.Frame(edit_frame)
        output_row.pack(pady=4)
        self.output_label = ttk.Label(output_row, text="出力先: 未設定")
        self.output_label.pack(side="left", padx=5)
        ttk.Button(output_row, text="出力先変更", command=self.set_output_folder).pack(side="left")

        # 使用プリセット欄
        use_frame = ttk.LabelFrame(self.root, text="使用するプリセット（複数選択）")
        use_frame.pack(fill="x", padx=10, pady=5)

        self.preset_check_frame = ttk.Frame(use_frame)
        self.preset_check_frame.pack(fill="x", padx=5)
        self.update_preset_checkboxes()

        # 統一出力先欄
        global_frame = ttk.LabelFrame(self.root, text="出力先の統一設定")
        global_frame.pack(fill="x", padx=10, pady=5)

        check_row = ttk.Frame(global_frame)
        check_row.pack(anchor="w", padx=5, pady=3)
        ttk.Checkbutton(check_row, text="統一出力先を使う", variable=self.use_global_output).pack(side="left")

        path_row = ttk.Frame(global_frame)
        path_row.pack(fill="x", padx=5)
        self.global_output_label = ttk.Label(path_row, text="統一出力先: 未設定")
        self.global_output_label.pack(side="left", fill="x", expand=True)
        ttk.Button(path_row, text="出力先選択", command=self.set_global_output).pack(side="right")

        # 分類操作
        file_frame = ttk.LabelFrame(self.root, text="画像分類")
        file_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(file_frame, text="📂 画像を選択", command=self.select_images).pack(side="left", padx=5)
        ttk.Button(file_frame, text="▶ 分類実行", command=self.classify_images).pack(side="left", padx=5)

        self.image_listbox = tk.Listbox(self.root, height=6)
        self.image_listbox.pack(fill="x", padx=10, pady=5)

    def update_preset_checkboxes(self):
        for widget in self.preset_check_frame.winfo_children():
            widget.destroy()
        self.preset_vars.clear()
        for name in self.presets:
            var = tk.BooleanVar()
            cb = ttk.Checkbutton(self.preset_check_frame, text=name, variable=var)
            cb.pack(anchor="w")
            self.preset_vars[name] = var

    def select_edit_preset(self, event=None):
        name = self.preset_combo.get()
        if name and name in self.presets:
            self.current_edit = name
            self.refresh_tag_list()
            self.output_label.config(text=f"出力先: {self.presets[name]['output'] or '未設定'}")

    def add_preset(self):
        name = simpledialog.askstring("新しいプリセット名", "作品名:")
        if not name or name in self.presets:
            return
        self.presets[name] = {"tags": [], "output": ""}
        save_presets(self.presets)
        self.preset_combo["values"] = list(self.presets.keys())
        self.update_preset_checkboxes()

    def rename_preset(self):
        if not self.current_edit:
            return
        new_name = simpledialog.askstring("名前変更", "新しい名前:", initialvalue=self.current_edit)
        if not new_name or new_name in self.presets:
            return
        self.presets[new_name] = self.presets.pop(self.current_edit)
        save_presets(self.presets)
        self.preset_combo["values"] = list(self.presets.keys())
        self.preset_combo.set(new_name)
        self.current_edit = new_name
        self.update_preset_checkboxes()

    def delete_preset(self):
        name = self.preset_combo.get()
        if not name:
            return
        if messagebox.askyesno("削除確認", f"{name} を削除しますか？"):
            self.presets.pop(name)
            save_presets(self.presets)
            self.current_edit = None
            self.preset_combo["values"] = list(self.presets.keys())
            self.preset_combo.set("")
            self.refresh_tag_list()
            self.output_label.config(text="出力先: 未設定")
            self.update_preset_checkboxes()

    def refresh_tag_list(self):
        self.tag_listbox.delete(0, "end")
        if self.current_edit:
            for tag in self.presets[self.current_edit]["tags"]:
                self.tag_listbox.insert("end", tag)

    def add_tag(self):
        if not self.current_edit:
            return
        tag = self.tag_entry.get().strip()
        if not tag:
            return
        tags = self.presets[self.current_edit]["tags"]
        if tag not in tags:
            tags.append(tag)
            save_presets(self.presets)
            self.refresh_tag_list()
        self.tag_entry.delete(0, "end")

    def remove_tag(self):
        if not self.current_edit:
            return
        selection = self.tag_listbox.curselection()
        if not selection:
            return
        tag = self.tag_listbox.get(selection[0])
        self.presets[self.current_edit]["tags"].remove(tag)
        save_presets(self.presets)
        self.refresh_tag_list()

    def set_output_folder(self):
        if not self.current_edit:
            return
        path = filedialog.askdirectory()
        if path:
            self.presets[self.current_edit]["output"] = path
            save_presets(self.presets)
            self.output_label.config(text=f"出力先: {path}")

    def set_global_output(self):
        path = filedialog.askdirectory()
        if path:
            self.global_output = path
            self.global_output_label.config(text=f"統一出力先: {path}")

    def select_images(self):
        files = filedialog.askopenfilenames(filetypes=[("画像ファイル", "*.jpg *.jpeg *.png *.gif *.bmp *.webp *.tiff")])
        if files:
            self.selected_files = files
            self.image_listbox.delete(0, "end")
            for f in files:
                self.image_listbox.insert("end", os.path.basename(f))

    def classify_images(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "画像を選択してください。")
            return

        selected_presets = [name for name, var in self.preset_vars.items() if var.get()]
        if not selected_presets:
            messagebox.showwarning("警告", "使用するプリセットにチェックを入れてください。")
            return

        moved = 0
        for file_path in self.selected_files:
            fname = os.path.basename(file_path)
            for preset_name in selected_presets:
                preset = self.presets[preset_name]
                tags = preset.get("tags", [])
                output = self.global_output if self.use_global_output.get() else preset.get("output", "")
                if not tags or not output:
                    continue
                for tag in tags:
                    if tag.lower() in fname.lower():
                        if self.use_global_output.get():
                            target_dir = os.path.join(output, preset_name, tag)
                        else:
                            target_dir = os.path.join(output, tag)
                        try:
                            os.makedirs(target_dir, exist_ok=True)
                            shutil.copy(file_path, os.path.join(target_dir, fname))
                            moved += 1
                        except Exception as e:
                            print(f"❌ コピー失敗: {fname} → {target_dir} : {e}")
                        break

        messagebox.showinfo("分類完了", f"{moved} 枚の画像を分類しました。")


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSorterApp(root)
    root.mainloop()