import threading
import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import can
import cantools
import time

class SteeringSignalViewer:
    def __init__(self, master, dbc_path, interface='pcan', channel='PCAN_USBBUS1', bitrate=1000000):
        self.master = master
        self.filter_id = 0x212
        self.validation_id = 0x213
        self.command_id = 0x214
        self.inputs_id = 0x211

        self.db = cantools.database.load_file(dbc_path)
        for cid in [self.filter_id, self.validation_id, self.inputs_id]:
            if not self.db.get_message_by_frame_id(cid):
                raise ValueError(f"Missing CAN ID 0x{cid:X} in DBC.")

        self.display_signals = {
            'stw_rt02_abs':   ("ABS Rotary",      720, 170),
            'stw_rt01_tc':    ("TC Rotary",       446, 170),
            'stw_tw01_left':  ("Left Thumbwheel",  115, 390),
            'stw_tw02_right': ("Right Thumbwheel", 1050, 390)
        }

        self.display_inputs = {
            'stw_sw15_shift_up':  ("Up",    1025, 400),
            'stw_sw16_shift_down':("Down",    51, 400),
            'stw_sw14_flash_left':("  BL",    300, 130),
            'stw_sw13_flash_right':("  BR",  770, 130),
            'stw_sw12_pit':       ("Pit",           1008, 200),
            'stw_sw11_mrk':       ("MRK",           1017, 230),
            'stw_sw04_ack':       ("Ack",           400, 350),
            'stw_sw10_wip':       ("WIP",         1023, 260),
            'stw_sw09_fcy':       ("FCY",           675, 350),
            'stw_sw08_drk':       ("DRK",           675, 410),
            'stw_sw07_dis':       ("DIS",           675, 460),
            'stw_sw06_str':       ("STR",           400, 460),
            'stw_sw05_rvs':       ("RVS",           400, 410),
            'stw_sw03_crk':       ("CRK",           53, 230),
            'stw_sw01_hb':        ("HB",            64, 200)
        }

        self.expected_213 = {
            'stw_sw_ver_major': 1,
            'stw_sw_ver_minor': 6,
            'stw_hw_rev': 2
        }

        self._ready_to_trigger = False
        self._trigger_loop_active = False
        self._force_send_active = False
        self._default_send_active = False

        self.bus = can.Bus(interface=interface, channel=channel, bitrate=bitrate)

        img_path = r"C:\Users\wayne.diggines\Documents\992EOL.jpg"
        self.bg_image = Image.open(img_path)
        self.bg_tk = ImageTk.PhotoImage(self.bg_image)

        self.canvas = tk.Canvas(master, width=self.bg_image.width, height=self.bg_image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.bg_tk, anchor='nw')

        self.font = font.Font(size=12, weight="bold")
        self.small_font = font.Font(size=10)

        self.canvas.create_text(20, 20, text="Firmware:", anchor='nw', font=self.font, fill='black')
        self.status_text = self.canvas.create_text(100, 20, text="—", anchor='nw', font=self.font, fill='black')

        self.ver_items = {}
        self.canvas.create_text(20, 60, text="SW Major:", anchor='nw', font=self.small_font, fill='black')
        self.ver_items['stw_sw_ver_major'] = self.canvas.create_text(85, 60, text='—', anchor='nw', font=self.small_font, fill='blue')
        self.canvas.create_text(20, 80, text="SW Minor:", anchor='nw', font=self.small_font, fill='black')
        self.ver_items['stw_sw_ver_minor'] = self.canvas.create_text(85, 80, text='—', anchor='nw', font=self.small_font, fill='blue')
        self.canvas.create_text(20, 100, text="HW Rev:", anchor='nw', font=self.small_font, fill='black')
        self.ver_items['stw_hw_rev'] = self.canvas.create_text(75, 100, text='—', anchor='nw', font=self.small_font, fill='blue')

        self.items = {}
        for sig_name, (label, x, y) in self.display_signals.items():
            val_id = self.canvas.create_text(x, y - 25, text='—', anchor='s', font=self.font, fill='cyan')
            self.canvas.create_text(x, y, text=label, anchor='s', font=self.font, fill='white')
            self.items[sig_name] = val_id

        self.input_items = {}
        for sig_name, (label, x, y) in self.display_inputs.items():
            self.canvas.create_text(x, y, text=f"{label}:", anchor='nw', font=self.font, fill='white')
            val_id = self.canvas.create_text(x + 50, y, text='—', anchor='nw', font=self.font, fill='cyan')
            self.input_items[sig_name] = val_id

        self.force_button = tk.Button(master, text="100% White", width=20, command=self._toggle_force_send)
        self.force_button.pack(pady=5)
        self.default_button = tk.Button(master, text="Default", width=20, command=self._toggle_default_send)
        self.default_button.pack(pady=5)

        self._running = True
        threading.Thread(target=self._listen_signals_loop, daemon=True).start()
        threading.Thread(target=self._read_version_loop, daemon=True).start()
        threading.Thread(target=self._trigger_loop, daemon=True).start()
        threading.Thread(target=self._fallback_loop, daemon=True).start()
        threading.Thread(target=self._listen_inputs_loop, daemon=True).start()

    def _listen_signals_loop(self):
        while self._running:
            msg = self.bus.recv(timeout=1.0)
            if msg and msg.arbitration_id == self.filter_id:
                try:
                    decoded = self.db.decode_message(msg.arbitration_id, msg.data)
                    self.master.after(0, self._update_signals, decoded)
                except:
                    continue

    def _read_version_loop(self):
        while self._running:
            msg = self.bus.recv(timeout=1.0)
            if msg and msg.arbitration_id == self.validation_id:
                try:
                    decoded = self.db.decode_message(msg.arbitration_id, msg.data)
                    self.master.after(0, self._update_versions, decoded)
                except:
                    continue

    def _listen_inputs_loop(self):
        while self._running:
            msg = self.bus.recv(timeout=1.0)
            if msg and msg.arbitration_id == self.inputs_id:
                try:
                    decoded = self.db.decode_message(msg.arbitration_id, msg.data)
                    self.master.after(0, self._update_inputs, decoded)
                except:
                    continue

    def _update_signals(self, decoded):
        for sig_name, item_id in self.items.items():
            if sig_name in decoded:
                val = str(decoded[sig_name])
                self.canvas.itemconfigure(item_id, text=val)
                self.canvas.itemconfigure(item_id, fill='lime' if val == "Zero" else 'red')
        self._check_trigger_condition()

    def _update_inputs(self, decoded):
        for sig_name, item_id in self.input_items.items():
            if sig_name in decoded:
                val = str(decoded[sig_name])
                self.canvas.itemconfigure(item_id, text=val)
                self.canvas.itemconfigure(item_id, fill='lime' if val == "Open" else 'red')

    def _update_versions(self, decoded):
        is_good = True
        for name, item_id in self.ver_items.items():
            val = decoded.get(name)
            if val is not None:
                self.canvas.itemconfigure(item_id, text=str(val))
                if val != self.expected_213.get(name):
                    is_good = False
        self.canvas.itemconfigure(
            self.status_text,
            text="GOOD" if is_good else "BAD",
            fill='lime' if is_good else 'red'
        )
        self._check_trigger_condition()

    def _check_trigger_condition(self):
        if self._force_send_active or self._default_send_active:
            self._ready_to_trigger = False
            return

        fw = self.canvas.itemcget(self.status_text, "text")
        all_zero = all(self.canvas.itemcget(self.items[name], "text") == "Zero" for name in self.display_signals)

        was_ready = self._ready_to_trigger
        self._ready_to_trigger = (fw == "GOOD" and all_zero)

        if self._ready_to_trigger and not was_ready:
            messagebox.showinfo("READY", "WHEEL IS READY TO TEST")

    def _trigger_loop(self):
        while self._running:
            if self._ready_to_trigger and not self._trigger_loop_active and not self._force_send_active and not self._default_send_active:
                self._trigger_loop_active = True
                try:
                    while self._ready_to_trigger and not self._force_send_active and not self._default_send_active:
                        self._send_custom_frame([0x07, 0x22])
                        time.sleep(0.2)
                        self._send_custom_frame([0x00, 0x22])
                        time.sleep(0.2)
                finally:
                    self._trigger_loop_active = False
            time.sleep(0.1)

    def _fallback_loop(self):
        while self._running:
            time.sleep(0.2)
            if not self._ready_to_trigger and not self._force_send_active and not self._default_send_active:
                self._send_custom_frame([0x00, 0x11])

    def _toggle_force_send(self):
        if not self._force_send_active:
            self._force_send_active = True
            self._default_send_active = False
            self._ready_to_trigger = False
            self._trigger_loop_active = False
            self.force_button.config(relief='sunken', text="100% White ACTIVE")
            self.default_button.config(relief='raised', text="Default")
            threading.Thread(target=self._force_send_loop, daemon=True).start()
        else:
            self._force_send_active = False
            self.force_button.config(relief='raised', text="100% White")

    def _toggle_default_send(self):
        if not self._default_send_active:
            self._default_send_active = True
            self._force_send_active = False
            self._ready_to_trigger = False
            self._trigger_loop_active = False
            self.default_button.config(relief='sunken', text="Default ACTIVE")
            self.force_button.config(relief='raised', text="100% White")
            threading.Thread(target=self._default_send_loop, daemon=True).start()
        else:
            self._default_send_active = False
            self.default_button.config(relief='raised', text="Default")

    def _force_send_loop(self):
        while self._force_send_active:
            self._send_custom_frame([0x07, 0x55])
            time.sleep(0.2)

    def _default_send_loop(self):
        while self._default_send_active:
            self._send_custom_frame([0x00, 0x00])
            time.sleep(0.2)

    def _send_custom_frame(self, byte_list):
        try:
            msg = can.Message(arbitration_id=self.command_id, data=bytes(byte_list), is_extended_id=False)
            self.bus.send(msg)
        except can.CanError:
            print("Failed to send frame.")

    def stop(self):
        self._running = False
        self.bus.shutdown()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Steering Wheel Monitor")

    viewer = SteeringSignalViewer(
        master=root,
        dbc_path=r"C:\Users\wayne.diggines\Downloads\bf1systems-Porsche-Cup-Gen-2-Steering-Wheel_0-7.dbc",
        interface='pcan',
        channel='PCAN_USBBUS1',
        bitrate=1000000
    )

    root.protocol("WM_DELETE_WINDOW", lambda: (viewer.stop(), root.destroy()))
    root.mainloop()
