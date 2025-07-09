
import tkinter as tk
import pyperclip

def main():
    root = tk.Tk()
    root.title("Kopyacı")
    root.geometry("300x120")
    root.attributes("-topmost", True)

    label = tk.Label(root, text="Metni girin:")
    label.pack(pady=(10, 0))

    entry = tk.Entry(root, width=40)
    entry.pack(pady=5)

    def copy_text():
        text = entry.get()
        pyperclip.copy(text)

    copy_button = tk.Button(root, text="Kopyala", command=copy_text)
    copy_button.pack(pady=(5, 10))

    root.mainloop()

if __name__ == "__main__":
    main()
