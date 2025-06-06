
import tkinter as tk

def count_non_whitespace(text):
    return len(''.join(text.split()))

root = tk.Tk()
root.title("기원 글자수 카운터")
root.geometry("500x300")

text_input = tk.Text(root, wrap=tk.WORD, font=("맑은 고딕", 12))
text_input.pack(expand=True, fill='both')

count_label = tk.Label(root, text="공백 제외 글자 수: 0", font=("맑은 고딕", 11))
count_label.pack(pady=5)

def update_count(event=None):
    content = text_input.get("1.0", tk.END)
    count = count_non_whitespace(content)
    count_label.config(text=f"공백 제외 글자 수: {count}")

text_input.bind("<KeyRelease>", update_count)

root.mainloop()
