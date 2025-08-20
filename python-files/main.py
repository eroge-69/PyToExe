import tkinter as tk
from tkinter import filedialog, messagebox

def generate_vcf():
    names = text_names.get("1.0", tk.END).strip().split("\n")
    numbers = text_numbers.get("1.0", tk.END).strip().split("\n")

    if len(names) != len(numbers):
        messagebox.showerror("错误", "姓名和号码数量不一致，请检查！")
        return

    vcf_content = ""
    for name, number in zip(names, numbers):
        vcf_content += f"BEGIN:VCARD\n"
        vcf_content += f"VERSION:3.0\n"
        vcf_content += f"FN:{name.strip()}\n"
        vcf_content += f"TEL;TYPE=CELL:{number.strip()}\n"
        vcf_content += f"END:VCARD\n"

    save_path = filedialog.asksaveasfilename(
        title="保存联系人文件",
        defaultextension=".vcf",
        filetypes=[("vCard 文件", "*.vcf")]
    )
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(vcf_content)
        messagebox.showinfo("完成", f"联系人已保存到：\n{save_path}")

# GUI 界面
root = tk.Tk()
root.title("妙瓦底打包人")
root.geometry("600x400")

frame = tk.Frame(root)
frame.pack(fill="both", expand=True, padx=10, pady=10)

# 姓名输入框
label_names = tk.Label(frame, text="放入姓名（一行一个）")
label_names.grid(row=0, column=0, padx=5, pady=5)
text_names = tk.Text(frame, width=30)
text_names.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

# 号码输入框
label_numbers = tk.Label(frame, text="放入号码（一行一个）")
label_numbers.grid(row=0, column=1, padx=5, pady=5)
text_numbers = tk.Text(frame, width=30)
text_numbers.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

# 生成按钮
btn_generate = tk.Button(root, text="生成联系人 VCF 文件", command=generate_vcf)
btn_generate.pack(pady=10)

root.mainloop()
