import os
import sys
import ctypes
from ctypes import wintypes
import threading
import psutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
VIRTUAL_MEM = 0x3000
PAGE_READWRITE = 0x04
LPVOID = ctypes.c_void_p
SIZE_T = ctypes.c_size_t
DWORD = ctypes.c_uint32
HANDLE = ctypes.c_void_p

# Toolhelp constants
TH32CS_SNAPMODULE = 0x00000008
TH32CS_SNAPMODULE32 = 0x00000010
MAX_PATH = 260

# WinAPI prototypes used by injector and module enumeration/unload
kernel32.OpenProcess.argtypes = (DWORD, wintypes.BOOL, DWORD)
kernel32.OpenProcess.restype = HANDLE

kernel32.VirtualAllocEx.argtypes = (HANDLE, LPVOID, SIZE_T, DWORD, DWORD)
kernel32.VirtualAllocEx.restype = LPVOID

kernel32.WriteProcessMemory.argtypes = (HANDLE, LPVOID, ctypes.c_void_p, SIZE_T, ctypes.POINTER(SIZE_T))
kernel32.WriteProcessMemory.restype = wintypes.BOOL

kernel32.VirtualFreeEx.argtypes = (HANDLE, LPVOID, SIZE_T, DWORD)
kernel32.VirtualFreeEx.restype = wintypes.BOOL

kernel32.GetModuleHandleA.argtypes = (ctypes.c_char_p,)
kernel32.GetModuleHandleA.restype = HANDLE

kernel32.GetProcAddress.argtypes = (HANDLE, ctypes.c_char_p)
kernel32.GetProcAddress.restype = ctypes.c_void_p

kernel32.CreateRemoteThread.argtypes = (HANDLE, LPVOID, SIZE_T, LPVOID, LPVOID, DWORD, ctypes.POINTER(DWORD))
kernel32.CreateRemoteThread.restype = HANDLE

kernel32.WaitForSingleObject.argtypes = (HANDLE, DWORD)
kernel32.WaitForSingleObject.restype = DWORD

kernel32.CloseHandle.argtypes = (HANDLE,)
kernel32.CloseHandle.restype = wintypes.BOOL

kernel32.CreateToolhelp32Snapshot.argtypes = (DWORD, DWORD)
kernel32.CreateToolhelp32Snapshot.restype = HANDLE

# MODULEENTRY32W structure for wide-char module enumeration
class MODULEENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("th32ModuleID", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("GlblcntUsage", wintypes.DWORD),
        ("ProccntUsage", wintypes.DWORD),
        ("modBaseAddr", LPVOID),
        ("modBaseSize", wintypes.DWORD),
        ("hModule", HANDLE),
        ("szModule", wintypes.WCHAR * MAX_PATH),
        ("szExePath", wintypes.WCHAR * MAX_PATH),
    ]

kernel32.Module32FirstW = kernel32.Module32FirstW
kernel32.Module32FirstW.argtypes = (HANDLE, ctypes.POINTER(MODULEENTRY32W))
kernel32.Module32FirstW.restype = wintypes.BOOL

kernel32.Module32NextW = kernel32.Module32NextW
kernel32.Module32NextW.argtypes = (HANDLE, ctypes.POINTER(MODULEENTRY32W))
kernel32.Module32NextW.restype = wintypes.BOOL

def _winerr_str():
    err = ctypes.get_last_error()
    return f"[err {err}] {ctypes.FormatError(err)}"

def inject_dll(pid: int, dll_path: str, timeout_ms: int = 5000) -> str:
    if not os.path.isfile(dll_path):
        return "DLL file not found."

    h_process = None
    h_thread = None
    arg_addr = None

    try:
        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))
        if not h_process:
            return f"OpenProcess failed: {_winerr_str()} (run as admin?)"

        dll_bytes = dll_path.encode('utf-8') + b'\x00'
        size = len(dll_bytes)

        arg_addr = kernel32.VirtualAllocEx(h_process, None, size, VIRTUAL_MEM, PAGE_READWRITE)
        if not arg_addr:
            return f"VirtualAllocEx failed: {_winerr_str()}"

        written = SIZE_T(0)
        ok = kernel32.WriteProcessMemory(h_process, arg_addr, dll_bytes, size, ctypes.byref(written))
        if not ok or written.value != size:
            return f"WriteProcessMemory failed: {_winerr_str()} (written {written.value}/{size})"

        h_k32 = kernel32.GetModuleHandleA(b"kernel32.dll")
        if not h_k32:
            return f"GetModuleHandleA failed: {_winerr_str()}"

        loadlib_addr = kernel32.GetProcAddress(h_k32, b"LoadLibraryA")
        if not loadlib_addr:
            return f"GetProcAddress(LoadLibraryA) failed: {_winerr_str()}"

        thread_id = DWORD(0)
        h_thread = kernel32.CreateRemoteThread(h_process, None, 0, ctypes.c_void_p(loadlib_addr), arg_addr, 0, ctypes.byref(thread_id))
        if not h_thread:
            return f"CreateRemoteThread failed: {_winerr_str()}"

        kernel32.WaitForSingleObject(h_thread, DWORD(timeout_ms))

        # best-effort free of allocated memory
        try:
            kernel32.VirtualFreeEx(h_process, arg_addr, 0, 0x8000)  # MEM_RELEASE
            arg_addr = None
        except Exception:
            pass

        return "OK"
    except Exception as e:
        return f"Exception: {e}"
    finally:
        try:
            if h_thread:
                kernel32.CloseHandle(h_thread)
        except Exception:
            pass
        try:
            if h_process:
                kernel32.CloseHandle(h_process)
        except Exception:
            pass

def find_remote_module_base(pid: int, module_name: str):
    """Return module base (hModule) for a module name in remote process or None."""
    if not module_name:
        return None, "No module name provided."

    # normalize name for comparison
    mod_lower = module_name.lower()

    snap = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPMODULE | TH32CS_SNAPMODULE32, int(pid))
    if not snap or snap == HANDLE(-1).value:
        return None, f"CreateToolhelp32Snapshot failed: {_winerr_str()}"

    me32 = MODULEENTRY32W()
    me32.dwSize = ctypes.sizeof(MODULEENTRY32W)

    try:
        ok = kernel32.Module32FirstW(snap, ctypes.byref(me32))
        if not ok:
            return None, f"Module32FirstW failed: {_winerr_str()}"
        while ok:
            name = me32.szModule
            if name and name.lower() == mod_lower:
                # found
                base = me32.hModule  # this is the module handle (base address)
                return base, None
            ok = kernel32.Module32NextW(snap, ctypes.byref(me32))
        return None, "Module not found in target process."
    finally:
        try:
            kernel32.CloseHandle(snap)
        except Exception:
            pass

def unload_remote_library(pid: int, module_name: str, timeout_ms: int = 5000) -> str:
    """Attempt to FreeLibrary the remote module by name. Returns 'OK' or error string."""
    if not module_name:
        return "No module name provided."

    base_handle, err = find_remote_module_base(pid, module_name)
    if err:
        return f"Find module failed: {err}"

    h_process = None
    h_thread = None
    try:
        h_process = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, int(pid))
        if not h_process:
            return f"OpenProcess failed: {_winerr_str()} (run as admin?)"

        h_k32 = kernel32.GetModuleHandleA(b"kernel32.dll")
        if not h_k32:
            return f"GetModuleHandleA failed: {_winerr_str()}"

        freelib_addr = kernel32.GetProcAddress(h_k32, b"FreeLibrary")
        if not freelib_addr:
            return f"GetProcAddress(FreeLibrary) failed: {_winerr_str()}"

        thread_id = DWORD(0)
        # pass the module handle/base address as parameter to FreeLibrary
        h_thread = kernel32.CreateRemoteThread(h_process, None, 0, ctypes.c_void_p(freelib_addr), ctypes.c_void_p(ctypes.cast(base_handle, ctypes.c_void_p).value), 0, ctypes.byref(thread_id))
        if not h_thread:
            return f"CreateRemoteThread(FreeLibrary) failed: {_winerr_str()}"

        kernel32.WaitForSingleObject(h_thread, DWORD(timeout_ms))
        return "OK"
    except Exception as e:
        return f"Exception: {e}"
    finally:
        try:
            if h_thread:
                kernel32.CloseHandle(h_thread)
        except Exception:
            pass
        try:
            if h_process:
                kernel32.CloseHandle(h_process)
        except Exception:
            pass

# GUI
class InjectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DLL Injector - CFR")
        self.root.geometry("720x430")
        # make window not resizable (sizable: none)
        self.root.resizable(False, False)

        self.selected_pid = None
        self.dll_path = ""
        self.all_processes = []

        # Process list frame
        proc_frame = ttk.LabelFrame(root, text="Running processes")
        proc_frame.place(x=10, y=10, width=460, height=380)

        self.proc_tree = ttk.Treeview(proc_frame, columns=("pid","name","exe"), show="headings", selectmode="browse")
        self.proc_tree.heading("pid", text="PID")
        self.proc_tree.heading("name", text="Name")
        self.proc_tree.heading("exe", text="Path")
        self.proc_tree.column("pid", width=60, anchor="center")
        self.proc_tree.column("name", width=140, anchor="w")
        self.proc_tree.column("exe", width=240, anchor="w")
        self.proc_tree.pack(fill="both", expand=True)
        self.proc_tree.bind("<<TreeviewSelect>>", self.on_select_proc)

        # Search box
        search_frame = ttk.Frame(proc_frame)
        search_frame.pack(fill="x", pady=(4,2))
        ttk.Label(search_frame, text="Search:").pack(side="left", padx=(2,4))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        search_entry.bind("<KeyRelease>", self.on_search)

        # Buttons frame
        btn_frame = ttk.Frame(root)
        btn_frame.place(x=480, y=10, width=220, height=160)
        ttk.Button(btn_frame, text="Refresh list", command=self.refresh_process_list).pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Select by PID", command=self.select_by_pid).pack(fill="x", pady=6)
        ttk.Button(btn_frame, text="Kill selected process", command=self.kill_selected).pack(fill="x", pady=6)
        # DETACH / Unload button
        ttk.Button(btn_frame, text="Unload DLL (Detach)", command=self.detach_selected).pack(fill="x", pady=6)

        # DLL selection
        dll_frame = ttk.LabelFrame(root, text="DLL to inject")
        dll_frame.place(x=480, y=180, width=220, height=140)
        self.dll_label = ttk.Label(dll_frame, text="No DLL chosen", wraplength=200)
        self.dll_label.pack(pady=(8,4))
        ttk.Button(dll_frame, text="Browse DLL...", command=self.browse_dll).pack(fill="x", padx=8, pady=6)
        ttk.Button(dll_frame, text="Open folder", command=self.open_dll_folder).pack(fill="x", padx=8)

        # Inject / status
        inject_frame = ttk.Frame(root)
        inject_frame.place(x=480, y=330, width=220, height=90)
        ttk.Button(inject_frame, text="Inject DLL", command=self.inject_button, style="Accent.TButton").pack(fill="x", pady=(6,8))
        self.status_label = ttk.Label(inject_frame, text="Status: idle", wraplength=200)
        self.status_label.pack()

        # Footer tip
        tip = ("Tip: Run this as Administrator if access denied.\n"
               "DLL bitness must match target process bitness.")
        ttk.Label(root, text=tip, foreground="gray").place(x=10, y=395)

        self.refresh_process_list()

    def refresh_process_list(self):
        self.all_processes.clear()
        for i in self.proc_tree.get_children():
            self.proc_tree.delete(i)
        for p in psutil.process_iter(['pid','name','exe']):
            try:
                pid = p.info['pid']
                name = p.info['name'] or ""
                exe = p.info.get('exe') or ""
                self.all_processes.append((pid,name,exe))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        self.update_treeview()
        self.status_label.config(text="Status: process list refreshed")

    def update_treeview(self):
        for i in self.proc_tree.get_children():
            self.proc_tree.delete(i)
        filter_text = self.search_var.get().lower()
        for pid, name, exe in self.all_processes:
            if filter_text in str(pid) or filter_text in name.lower():
                self.proc_tree.insert("", "end", iid=str(pid), values=(pid,name,exe))

    def on_search(self, event):
        self.update_treeview()

    def on_select_proc(self, event):
        sel = self.proc_tree.selection()
        if not sel:
            self.selected_pid = None
            return
        pid = int(sel[0])
        self.selected_pid = pid
        self.status_label.config(text=f"Selected PID {pid}")

    def select_by_pid(self):
        pid_str = simpledialog.askstring("Select PID", "Enter PID:")
        if not pid_str:
            return
        try:
            pid = int(pid_str)
            if self.proc_tree.exists(str(pid)):
                self.proc_tree.selection_set(str(pid))
                self.proc_tree.see(str(pid))
                self.selected_pid = pid
                self.status_label.config(text=f"Selected PID {pid}")
            else:
                messagebox.showerror("Error", "PID not in list. Refresh or enter another PID.")
        except ValueError:
            messagebox.showerror("Error", "Invalid PID.")

    def kill_selected(self):
        if not self.selected_pid:
            messagebox.showwarning("Warning", "No process selected.")
            return
        try:
            p = psutil.Process(self.selected_pid)
            p.kill()
            messagebox.showinfo("Killed", f"Process {self.selected_pid} killed.")
            self.refresh_process_list()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to kill: {e}")

    def detach_selected(self):
        """Attempt to unload the DLL (FreeLibrary) from the selected process."""
        if not self.selected_pid:
            messagebox.showwarning("Warning", "No process selected.")
            return

        # If a DLL path is selected in the UI, use its basename as module name.
        if self.dll_path:
            module_name = os.path.basename(self.dll_path)
        else:
            # ask for module name
            module_name = simpledialog.askstring("Unload DLL", "Enter module name to unload (e.g. mymod.dll):")
            if not module_name:
                return

        # confirm action with the user
        if not messagebox.askyesno("Confirm unload", f"Attempt to unload '{module_name}' from PID {self.selected_pid}?"):
            return

        self.status_label.config(text=f"Unloading {module_name} from PID {self.selected_pid} ...")
        # perform unload in a thread
        t = threading.Thread(target=self._do_unload, args=(self.selected_pid, module_name), daemon=True)
        t.start()

    def _do_unload(self, pid, module_name):
        res = unload_remote_library(pid, module_name)
        if res == "OK":
            messagebox.showinfo("Success", f"Unloaded {module_name} from PID {pid}.")
            self.status_label.config(text="Status: unload OK")
        else:
            messagebox.showerror("Failure", f"Unload failed: {res}")
            self.status_label.config(text=f"Status: unload failed ({res})")

    def browse_dll(self):
        path = filedialog.askopenfilename(title="Select DLL", filetypes=[("DLL files","*.dll"),("All files","*.*")])
        if path:
            self.dll_path = path
            self.dll_label.config(text=os.path.basename(path))
            self.status_label.config(text="Status: DLL selected")

    def open_dll_folder(self):
        if not self.dll_path:
            messagebox.showinfo("Info", "No DLL selected.")
            return
        folder = os.path.dirname(self.dll_path)
        if os.path.isdir(folder):
            os.startfile(folder)

    def inject_button(self):
        if not self.selected_pid:
            messagebox.showwarning("Warning", "Select a process first.")
            return
        if not self.dll_path:
            messagebox.showwarning("Warning", "Select a DLL first.")
            return

        t = threading.Thread(target=self._do_inject, args=(self.selected_pid, self.dll_path), daemon=True)
        t.start()

    def _do_inject(self, pid, dll_path):
        self.status_label.config(text=f"Injecting into PID {pid} ...")
        res = inject_dll(pid, dll_path)
        if res == "OK":
            messagebox.showinfo("Success", f"Injected {os.path.basename(dll_path)} into PID {pid}.")
            self.status_label.config(text="Status: injection OK")
        else:
            messagebox.showerror("Failure", f"Injection failed: {res}")
            self.status_label.config(text=f"Status: failed ({res})")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    try:
        style.theme_use('vista')
    except:
        pass
    app = InjectorGUI(root)
    root.mainloop()
