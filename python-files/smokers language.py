import tkinter as tk
from tkinter import messagebox

# Character mappings
char_map = {}
rev_map = {}
all_chars = 'ابتثجحخدذرزسشصضطظعغفقكلمنهويءئةآأإىABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789؟.,! '

for i, char in enumerate(all_chars):
    code = str(i + 10)
    char_map[char] = code
    rev_map[code] = char

def encode(text):
    return '$'.join(char_map.get(c, '') for c in text if c in char_map)

def decode(code):
    return ''.join(rev_map.get(part, '') for part in code.split('$'))

def handle_encode():
    msg = entry_input.get("1.0", tk.END).strip()
    result = encode(msg)
    entry_output.delete("1.0", tk.END)
    entry_output.insert(tk.END, result)

def handle_decode():
    msg = entry_input.get("1.0", tk.END).strip()
    result = decode(msg)
    entry_output.delete("1.0", tk.END)
    entry_output.insert(tk.END, result)

def copy_to_clipboard():
    result = entry_output.get("1.0", tk.END).strip()
    if result:
        root.clipboard_clear()
        root.clipboard_append(result)
        root.update_idletasks()
        messagebox.showinfo("Copied", "Copied! You can now paste it anywhere.")
    else:
        messagebox.showwarning("Empty", "Nothing to copy!")

def show_help():
    help_text = (
        "🔐 How to Use | كيفية الاستخدام:\n\n"
        "1. Type a normal message (English or Arabic) in the top box.\n"
        "   ✍️ اكتب رسالة عادية في المربع العلوي.\n\n"
        "2. Click 'Encode' to convert it into a secret number code.\n"
        "   🔢 اضغط على 'Encode' لتحويلها إلى أرقام سرية.\n\n"
        "3. Click 'Copy to Clipboard' to copy it.\n"
        "   📋 اضغط على 'Copy to Clipboard' لنسخ الشيفرة.\n\n"
        "4. Send the code to your friend.\n"
        "   📤 أرسل الشيفرة إلى صديقك.\n\n"
        "5. Your friend pastes it, then clicks 'Decode'.\n"
        "   📥 صديقك يلصق الشيفرة ويضغط 'Decode'.\n\n"
        "⚠️ ملاحظة مهمة:\n"
        "لما تيجي تكتب بالعربي ولما صاحبك يبعث لك الرسالة المشفرة، لازم تتأكد إنك محول لغة الكيبورد للإنجليزية قبل ما تلصق الشيفرة.\n"
        "👈 شوف جنب الساعة، إذا مكتوب (ع) ما بزبط، لازم تحول لـ (ENG)."
    )
    messagebox.showinfo("How to Use / طريقة الاستخدام", help_text)

# GUI setup
root = tk.Tk()
root.title("Secret Code Messenger")

tk.Label(root, text="Enter message or code:").pack()
entry_input = tk.Text(root, height=4, width=50)
entry_input.pack()

tk.Button(root, text="Encode", command=handle_encode).pack(pady=3)
tk.Button(root, text="Decode", command=handle_decode).pack(pady=3)

tk.Label(root, text="Result:").pack()
entry_output = tk.Text(root, height=4, width=50)
entry_output.pack()

tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard).pack(pady=5)
tk.Button(root, text="Help / مساعدة", command=show_help).pack(pady=5)

root.mainloop()
