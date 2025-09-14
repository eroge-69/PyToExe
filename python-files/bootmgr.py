import tkinter as tk
import psutil
import platform

class FactoryBootMgr:
    def __init__(self, root):
        self.root = root
        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="#0000AA")
        self.root.title("FactoryOS Boot Manager")
        self.root.bind("<Escape>", lambda e: root.destroy())  # press Esc to exit

        self.font = ("Courier New", 11, "bold")

        self.lines = [
            "FactoryOS Boot Manager",
            "------------------------",
            f"CPU: {platform.processor()}",
            f"Architecture: {platform.architecture()[0]}",
            f"Machine: {platform.machine()}",
            f"RAM: {round(psutil.virtual_memory().total / (1024 ** 3), 2)} GB",
            f"Disk(s): {', '.join([disk.device for disk in psutil.disk_partitions()])}",
            f"System: {platform.system()} {platform.release()}",
            "",
            "Press [ESC] to exit..."
        ]

        for line in self.lines:
            tk.Label(root, text=line, font=self.font, fg="white", bg="#0000AA").pack(pady=2)

# Launch fullscreen boot manager
root = tk.Tk()
app = FactoryBootMgr(root)
root.mainloop()
