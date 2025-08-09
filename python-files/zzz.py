import win32gui
import win32con
import win32api
import random
import ctypes
import threading
import time

# Windows MessageBox icon flags
MB_OK = 0x0
ICON_TYPES = [
    0x10,  # MB_ICONERROR (Stop icon)
    0x30,  # MB_ICONWARNING (Exclamation)
    0x40,  # MB_ICONINFORMATION (Info icon)
]

class RedWindow:
    def __init__(self):
        self.class_name = "RedBGWindow"
        self.state = None  # yes / no / maybe
        self.z_positions = [(random.randint(0, 700), random.randint(0, 500)) for _ in range(50)]

        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = self.wnd_proc
        wc.lpszClassName = self.class_name
        wc.hInstance = win32api.GetModuleHandle(None)
        win32gui.RegisterClass(wc)

        self.hwnd = win32gui.CreateWindow(
            self.class_name,
            "ZZZ.EXE",
            win32con.WS_OVERLAPPEDWINDOW,
            100,
            100,
            800,
            600,
            0,
            0,
            wc.hInstance,
            None
        )

        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOWNORMAL)
        win32gui.UpdateWindow(self.hwnd)

        # Start thread for random popups
        threading.Thread(target=self.random_popups_thread, daemon=True).start()

    def random_popups_thread(self):
        while True:
            time.sleep(random.uniform(3, 7))  # random delay between 3-7 seconds
            icon = random.choice(ICON_TYPES)
            ctypes.windll.user32.MessageBoxW(
                0,
                "Random popup says hello!",
                "Random Popup",
                MB_OK | icon
            )

    def draw_tunnel_effect(self, hdc, center_x, center_y):
        max_radius = 300
        step = 20
        for r in range(max_radius, 0, -step):
            color_val = int(255 * (r / max_radius))
            brush = win32gui.CreateSolidBrush(win32api.RGB(color_val, 0, 0))  # shades of red
            win32gui.SelectObject(hdc, brush)
            win32gui.Ellipse(hdc, center_x - r, center_y - r, center_x + r, center_y + r)
            win32gui.DeleteObject(brush)

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_DESTROY:
            win32gui.PostQuitMessage(0)
            return 0

        elif msg == win32con.WM_LBUTTONDOWN:
            x = win32api.LOWORD(lparam)
            y = win32api.HIWORD(lparam)

            if 500 <= x <= 560 and 515 <= y <= 545:
                self.state = "yes"
                win32gui.InvalidateRect(hwnd, None, False)
                return 0
            if 570 <= x <= 630 and 515 <= y <= 545:
                self.state = "no"
                win32gui.InvalidateRect(hwnd, None, False)
                return 0
            if 640 <= x <= 720 and 515 <= y <= 545:
                self.state = "maybe"
                win32gui.InvalidateRect(hwnd, None, False)
                return 0

        elif msg == win32con.WM_PAINT:
            ps = win32gui.PAINTSTRUCT()
            hdc, ps = win32gui.BeginPaint(hwnd)

            # Draw tunnel effect background at center of window (800x600)
            self.draw_tunnel_effect(hdc, 400, 300)

            # Draw scattered "ZZZ.EXE" texts on top
            win32gui.SetTextColor(hdc, win32api.RGB(255, 255, 255))
            win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
            for x, y in self.z_positions:
                win32gui.TextOut(hdc, x, y, "ZZZ.EXE", len("ZZZ.EXE"))

            # Draw black bottom bar with buttons & text
            black_brush = win32gui.CreateSolidBrush(win32api.RGB(0, 0, 0))
            win32gui.FillRect(hdc, (0, 500, 800, 600), black_brush)

            win32gui.TextOut(hdc, 20, 520, "There are no rules. Do you like me?", len("There are no rules. Do you like me?"))

            win32gui.DrawEdge(hdc, (500, 515, 560, 545), win32con.BDR_RAISEDOUTER, win32con.BF_RECT)
            win32gui.TextOut(hdc, 510, 520, "YES", 3)

            win32gui.DrawEdge(hdc, (570, 515, 630, 545), win32con.BDR_RAISEDOUTER, win32con.BF_RECT)
            win32gui.TextOut(hdc, 580, 520, "NO", 2)

            win32gui.DrawEdge(hdc, (640, 515, 720, 545), win32con.BDR_RAISEDOUTER, win32con.BF_RECT)
            win32gui.TextOut(hdc, 655, 520, "MAYBE", 5)

            if self.state == "yes":
                win32gui.TextOut(hdc, 370, 280, "(:", 2)
            elif self.state == "no":
                win32gui.TextOut(hdc, 370, 280, "):", 2)
            elif self.state == "maybe":
                win32gui.TextOut(hdc, 370, 280, ":/", 2)

            win32gui.EndPaint(hwnd, ps)
            return 0

        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def run(self):
        while True:
            msg = win32gui.GetMessage(self.hwnd, 0, 0)
            if not msg:
                break
            win32gui.TranslateMessage(msg)
            win32gui.DispatchMessage(msg)

if __name__ == "__main__":
    app = RedWindow()
    app.run()