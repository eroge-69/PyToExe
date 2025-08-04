
import tkinter as tk
from tkinter import filedialog, messagebox

# 替换规则
replacements = [
    ("<h2", '<h2 class="mbr-section-title mbr-fonts-style mb-3" data-app-selector=".mbr-section-title" mbr-theme-style="display-2" mbr-if="showTitle"'),
    ("<p>", '<p class="mbr-text mbr-fonts-style" mbr-theme-style="display-7" mbr-if="showText" data-app-selector=".mbr-text, .mbr-section-btn">'),
    ("<ul>", '<ul class="list mbr-fonts-style" mbr-theme-style="display-7" data-app-selector=".list" data-multiline mbr-article>')
]

def replace_text():
    input_text = input_box.get("1.0", tk.END)
    for target, replacement in replacements:
        input_text = input_text.replace(target, replacement)
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, input_text)

def save_result():
    result_text = output_box.get("1.0", tk.END)
    file_path = filedialog.asksaveasfilename(defaultextension=".html",
                                             filetypes=[("HTML Files", "*.html"), ("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(result_text)
        messagebox.showinfo("保存成功", f"文件已保存到：\n{file_path}")

window = tk.Tk()
window.title("批量查找替换工具")
window.geometry("900x600")

tk.Label(window, text="原始内容：").pack()
input_box = tk.Text(window, height=15)
input_box.pack(fill=tk.X, padx=10)

tk.Button(window, text="一键替换", command=replace_text).pack(pady=10)

tk.Label(window, text="替换后内容：").pack()
output_box = tk.Text(window, height=15)
output_box.pack(fill=tk.X, padx=10)

tk.Button(window, text="另存为文件", command=save_result).pack(pady=10)

window.mainloop()
