import time
import threading
import customtkinter
import vgamepad
import keyboard

class XboxControllerEmulator:
    def __init__(self):
        self.gamepad = None
        self.running = False
        self.fake_input_thread = None

    def start(self):
        if not self.running:
            self.gamepad = vgamepad.VX360Gamepad()
            self.running = True
            self.fake_input_thread = threading.Thread(target=self.send_fake_inputs, daemon=True)
            self.fake_input_thread.start()
            return True
        return False

    def stop(self):
        if self.running:
            self.running = False
            self.gamepad = None
            return True
        return False

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()

    def send_fake_inputs(self):
        while self.running:
            try:
                self.gamepad.left_joystick(x_value=1000, y_value=0)
                self.gamepad.update()
                time.sleep(0.2)
                self.gamepad.left_joystick(x_value=0, y_value=0)
                self.gamepad.update()
                time.sleep(2)
            except Exception as e:
                print(f"Lỗi input: {e}")
                break

class ModernUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("green")

        self.title("WZ Aim Assist")
        self.geometry("640x480")
        self.resizable(True, True)

        self.emulator = XboxControllerEmulator()

        self.status_label = customtkinter.CTkLabel(self, text="🔴 Tay cầm ảo chưa bật", font=("Segoe UI", 15))
        self.status_label.pack(pady=20)

        self.btn_start = customtkinter.CTkButton(self, text="🟢 Bật tay cầm ảo", width=200, command=self.start_controller)
        self.btn_start.pack(pady=8)

        self.btn_stop = customtkinter.CTkButton(self, text="🔴 Tắt tay cầm ảo", width=200, command=self.stop_controller)
        self.btn_stop.pack(pady=8)

        self.exit_btn = customtkinter.CTkButton(self, text="❌ Thoát", width=100, fg_color="#444", command=self.on_exit)
        self.exit_btn.pack(pady=15)

        self.listener_thread = threading.Thread(target=self.hotkey_listener, daemon=True)
        self.listener_thread.start()

        self.protocol("WM_DELETE_WINDOW", self.on_exit)

    def start_controller(self):
        if self.emulator.start():
            self.status_label.configure(text="🟢 Tay cầm ảo đang bật")

    def stop_controller(self):
        if self.emulator.stop():
            self.status_label.configure(text="🔴 Tay cầm ảo đã ngừng")

    def hotkey_listener(self):
        while True:
            try:
                if keyboard.is_pressed('f8'):
                    self.emulator.toggle()
                    self.status_label.configure(
                        text="🟢 Tay cầm ảo đang bật" if self.emulator.running else "🔴 Tay cầm ảo đã ngừng"
                    )
                    while keyboard.is_pressed('f8'):
                        time.sleep(0.1)

                if keyboard.is_pressed('ctrl') and keyboard.is_pressed('q'):
                    self.on_exit()
                    break

                time.sleep(0.1)
            except:
                break

    def on_exit(self):
        self.emulator.stop()
        self.destroy()

if __name__ == "__main__":
    app = ModernUI()
    app.mainloop()