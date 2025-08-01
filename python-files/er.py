import ctypes
import os
import time
from ctypes import wintypes

# Hedef prosesin adı (CS 1.6 için)
target_process_name = "hl.exe"

# DLL'in yolu (burada örnek bir DLL)
dll_path = r"C:\Users\efosb\Desktop\esp.dll"

# Process ID almak için win32api kullanalım
def get_process_id(process_name):
    for proc in os.popen('tasklist'):
        if process_name in proc:
            pid = int(proc.split()[1])
            return pid
    return None

# DLL Enjekte Etme Fonksiyonu
def inject_dll(pid, dll_path):
    # kernel32.dll'yi yükleyelim
    kernel32 = ctypes.WinDLL('kernel32')

    # Process handle almak
    h_process = kernel32.OpenProcess(0x1F0FFF, False, pid)  # PROCESS_ALL_ACCESS = 0x1F0FFF

    if not h_process:
        print("Hedef işleme erişilemiyor!")
        return

    # DLL'in tam yolunu almak
    dll_path_c = ctypes.create_string_buffer(dll_path.encode('utf-8'))

    # LoadLibraryA adresini bulalım
    load_library_addr = kernel32.GetProcAddress(kernel32.GetModuleHandleW('kernel32.dll'), b'LoadLibraryA')

    if not load_library_addr:
        print("LoadLibraryA fonksiyonu bulunamadı!")
        return

    # Thread oluşturmak ve DLL'i yüklemek
    thread_id = wintypes.DWORD(0)
    remote_thread = kernel32.CreateRemoteThread(
        h_process, None, 0, load_library_addr, dll_path_c, 0, ctypes.byref(thread_id)
    )

    if not remote_thread:
        print("Remote thread oluşturulamadı!")
        return

    print("DLL başarıyla enjekte edildi!")
    kernel32.CloseHandle(h_process)

# CS 1.6'nın process ID'sini al
pid = get_process_id(target_process_name)

if pid:
    print(f"Process ID bulundu: {pid}")
    inject_dll(pid, dll_path)
else:
    print(f"{target_process_name} bulunamadı!")
