import tkinter as tk
import win32gui
import win32con

class MouseLockApp
    def __init__(self, root)
        self.root = root
        self.root.title(Mouse Lock Demo)
        self.root.geometry(400x200)

        label = tk.Label(root, text=Enter password to unlock mouse)
        label.pack(pady=10)

        self.entry = tk.Entry(root, show=)
        self.entry.pack(pady=10)
        self.entry.bind(Return, self.check_password)

        # Lock cursor when window is ready
        self.root.after(500, self.lock_mouse)

        # Make sure mouse is unlocked on close
        self.root.protocol(WM_DELETE_WINDOW, self.on_close)

    def lock_mouse(self)
        hwnd = win32gui.GetForegroundWindow()
        rect = win32gui.GetWindowRect(hwnd)
        win32gui.ClipCursor(rect)

    def unlock_mouse(self)
        win32gui.ClipCursor(None)

    def check_password(self, event)
        if self.entry.get() == 123
            self.unlock_mouse()
            tk.messagebox.showinfo(Success, Mouse unlocked!)
        else
            tk.messagebox.showerror(Error, Wrong password!)
            self.entry.delete(0, tk.END)

    def on_close(self)
        self.unlock_mouse()
        self.root.destroy()


if __name__ == __main__
    import tkinter.messagebox
    root = tk.Tk()
    app = MouseLockApp(root)
    root.mainloop()
