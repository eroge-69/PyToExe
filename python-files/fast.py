import ctypes
import ctypes.wintypes as wintypes
import psutil
import os
import tkinter as tk
from tkinter import ttk

PROCESS_ALL_ACCESS = 0x1F0FFF
LIST_MODULES_ALL = 0x03
k32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi

def get_python27_base_address(h_process):
    h_modules = (wintypes.HMODULE * 1024)()
    needed = wintypes.DWORD()
    if not psapi.EnumProcessModulesEx(h_process, h_modules, ctypes.sizeof(h_modules), ctypes.byref(needed), LIST_MODULES_ALL):
        return None
    count = int(needed.value / ctypes.sizeof(wintypes.HMODULE))
    for i in range(count):
        module_name = ctypes.create_string_buffer(255)
        psapi.GetModuleBaseNameA(h_process, h_modules[i], module_name, ctypes.sizeof(module_name))
        if b"python27.dll" in module_name.value.lower():
            return h_modules[i]
    return None

def inject_script(pid, script_path):
    script_abs = os.path.abspath(script_path).replace("\\", "\\\\")
    full_command = f"exec(open(r'{script_abs}').read())"
    h_process = k32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        return f"[-] PID {pid}: erişilemedi."

    base = get_python27_base_address(h_process)
    if not base:
        return f"[-] PID {pid}: python27.dll yok."

    try:
        # Python DLL dosyasını direkt olarak belirttiğiniz yoldan alıyoruz
        dll_path = r"C:\mt2eng\metin2\en-GB\python27.dll"
        local_py = ctypes.windll.LoadLibrary(dll_path)
    except Exception as e:
        return f"[-] PID {pid}: DLL yüklenemedi: {e}"

    offset = ctypes.cast(local_py.PyRun_SimpleString, ctypes.c_void_p).value - local_py._handle
    remote_func = base + offset

    remote_str = k32.VirtualAllocEx(h_process, 0, len(full_command)+1, 0x1000, 0x40)
    k32.WriteProcessMemory(h_process, remote_str, full_command.encode('ascii'), len(full_command)+1, None)
    thread = k32.CreateRemoteThread(h_process, None, 0, remote_func, remote_str, 0, None)
    if not thread:
        return f"[-] PID {pid}: Thread başlatılamadı."

    return f"[✓] PID {pid}: {os.path.basename(script_path)} inject edildi."

# GUI uygulaması
class InjectorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Injector")
        self.geometry("600x380")
        self.resizable(False, False)

        self.process_list = tk.Listbox(self, selectmode=tk.SINGLE, exportselection=False, width=40)
        self.script_list = tk.Listbox(self, selectmode=tk.EXTENDED, exportselection=False, width=30)

        self.process_list.grid(row=0, column=0, padx=10, pady=10, rowspan=4)
        self.script_list.grid(row=0, column=1, padx=10, pady=10, rowspan=4)

        self.inject_btn = ttk.Button(self, text="Inject", command=self.inject_selected)
        self.inject_all_btn = ttk.Button(self, text="Inject All", command=self.inject_all)
        self.refresh_btn = ttk.Button(self, text="Refresh", command=self.refresh_lists)

        self.inject_btn.grid(row=4, column=0, padx=10, pady=5)
        self.inject_all_btn.grid(row=4, column=1, padx=10, pady=5)
        self.refresh_btn.grid(row=5, column=0, columnspan=2, pady=5)

        self.refresh_lists()

    def refresh_lists(self):
        self.processes = {
            proc.info['pid']: proc.info['name']
            for proc in psutil.process_iter(['pid', 'name'])
            if proc.info['name'] and proc.info['name'].lower().startswith("metin2client")
        }
        self.process_list.delete(0, tk.END)
        for pid, name in self.processes.items():
            self.process_list.insert(tk.END, f"{pid} - {name}")

        # Klasör yolunu burada belirtiyoruz
        script_folder = r"C:\Users\Cano\Desktop\script"
        self.scripts = [f for f in os.listdir(script_folder) if f.endswith(".py")]

        self.script_list.delete(0, tk.END)
        for s in self.scripts:
            self.script_list.insert(tk.END, s)

    def inject_selected(self):
        selection = self.process_list.curselection()
        script_sel = self.script_list.curselection()

        if not selection or not script_sel:
            print("[-] Lütfen bir client ve bir script seçin.")
            return

        pid_text = self.process_list.get(selection[0])
        pid = int(pid_text.split(" - ")[0])
        script = self.script_list.get(script_sel[0])

        # Script tam yolunu alıyoruz
        script_folder = r"C:\Users\Cano\Desktop\script"
        script_path = os.path.join(script_folder, script)

        result = inject_script(pid, script_path)
        print(result)

    def inject_all(self):
        if not self.processes:
            print("[-] Hiçbir client yok.")
            return
        selected_scripts = [self.script_list.get(i) for i in self.script_list.curselection()]
        if not selected_scripts:
            print("[-] Script seçilmedi.")
            return

        script_folder = r"C:\Users\Cano\Desktop\script"
        for pid in self.processes:
            for script in selected_scripts:
                script_path = os.path.join(script_folder, script)
                result = inject_script(pid, script_path)
                print(result)

if __name__ == "__main__":
    InjectorApp().mainloop()
