import ctypes
import os
import time
import win32process
import win32con
import win32gui
import win32api

def set_timer_precision():
    winmm = ctypes.WinDLL("winmm")
    winmm.timeBeginPeriod(1)

def reserve_memory(size_mb=500):
    size = size_mb * 1024 * 1024
    ctypes.windll.kernel32.VirtualAlloc(
        0, size, 0x3000, 0x04
    )

def create_fake_window():
    class_name = "FakeMapleClass"
    wndclass = win32gui.WNDCLASS()
    wndclass.lpfnWndProc = lambda hWnd, msg, wParam, lParam: win32gui.DefWindowProc(hWnd, msg, wParam, lParam)
    wndclass.lpszClassName = class_name
    wndclass.hInstance = win32api.GetModuleHandle(None)
    atom = win32gui.RegisterClass(wndclass)

    hwnd = win32gui.CreateWindow(
        atom,
        "Fake Maple Booster",
        win32con.WS_OVERLAPPEDWINDOW,
        100, 100, 400, 200,
        0, 0, wndclass.hInstance, None
    )
    win32gui.ShowWindow(hwnd, win32con.SW_SHOWNORMAL)
    win32gui.SetForegroundWindow(hwnd)
    return hwnd

def optimize_process():
    handle = win32api.GetCurrentProcess()
    win32process.SetPriorityClass(handle, win32process.HIGH_PRIORITY_CLASS)

def induce_memory_pressure():
    print("[*] 2GB 가짜 메모리 점유로 압축 유도")
    block = ctypes.windll.kernel32.VirtualAlloc(
        0, 2 * 1024 * 1024 * 1024, 0x3000, 0x04
    )
    print("[*] WorkingSet 정리")
    ctypes.windll.psapi.EmptyWorkingSet(os.getpid())

def init_gpu():
    try:
        print("[*] DirectX 초기화 DLL 호출")
        dx = ctypes.WinDLL("dx_init.dll")
        dx.init_d3d()
    except Exception as e:
        print("[!] DLL 호출 실패:", e)

if __name__ == "__main__":
    set_timer_precision()
    reserve_memory(500)
    hwnd = create_fake_window()
    optimize_process()
    induce_memory_pressure()
    init_gpu()
    print("[*] 모든 시스템 트리거 완료. 이 상태로 게임을 실행하면 됩니다.")
    input("엔터 키를 누르면 종료됩니다.")
