import tkinter as tk
from tkinter import ttk, messagebox
import serial
import time
import json
import threading
import os

# === Motor Communication Functions ===
def calculate_checksum(packet):
    return 0xFF - (sum(packet[3:]) % 256)

def build_packet(servo_id, command, factors):
    header = [0xFF, 0xFF, 0xFF]
    size = len(factors) + 2
    body = [servo_id, size, command] + factors
    checksum = calculate_checksum(header + body)
    return bytearray(header + body + [checksum])

def echo_servo(ser, sid):
    ser.write(build_packet(sid, 0xF1, []))
    time.sleep(0.01)
    resp = ser.read(10)
    return resp.startswith(b'\xFF\xFF\xFF') and resp[3] == sid

def send_force_on(ser, sid):
    ser.write(build_packet(sid, 0xF3, [0x80, 0x01]))
    time.sleep(0.01)

def set_speed(ser, sid, speed):
    spd_l, spd_h = speed & 0xFF, (speed >> 8) & 0xFF
    ser.write(build_packet(sid, 0xF3, [0x88, spd_l, spd_h]))
    time.sleep(0.01)

def set_current(ser, sid, current):
    cur_l, cur_h = current & 0xFF, (current >> 8) & 0xFF
    ser.write(build_packet(sid, 0xF3, [0x8A, cur_l, cur_h]))
    time.sleep(0.01)

def move_to_position(ser, sid, pos):
    pos_l, pos_h = pos & 0xFF, (pos >> 8) & 0xFF
    ser.write(build_packet(sid, 0xF3, [0x86, pos_l, pos_h]))
    time.sleep(0.01)

# === Persistent Storage ===
CONFIG_FILE = "motor_settings.json"

def load_settings():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"speed": 512, "pos1": 1000, "pos2": 3000}

def save_settings(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

# === GUI Application ===
class MotorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MightyZap Motor Control")
        self.settings = load_settings()

        self.ser = None
        self.servo_id = None

        self.setup_ui()
        threading.Thread(target=self.connect_motor, daemon=True).start()

    def setup_ui(self):
        self.speed_label = ttk.Label(self.root, text=f"Speed: {self.settings['speed']}")
        self.speed_label.pack(pady=5)

        self.speed_slider = ttk.Scale(self.root, from_=1, to=1023, orient="horizontal",
                                      command=self.update_speed_label)
        self.speed_slider.set(self.settings["speed"])
        self.speed_slider.pack(fill="x", padx=20)

        # Position 1
        self.pos1_frame = ttk.Frame(self.root)
        self.pos1_frame.pack(pady=10)
        self.pos1_entry = ttk.Entry(self.pos1_frame, width=10)
        self.pos1_entry.insert(0, str(self.settings["pos1"]))
        self.pos1_entry.pack(side="left", padx=5)
        self.pos1_button = ttk.Button(self.pos1_frame, text="Move to Position 1",
                                      command=self.move_pos1)
        self.pos1_button.pack(side="left", padx=5)

        # Position 2
        self.pos2_frame = ttk.Frame(self.root)
        self.pos2_frame.pack(pady=10)
        self.pos2_entry = ttk.Entry(self.pos2_frame, width=10)
        self.pos2_entry.insert(0, str(self.settings["pos2"]))
        self.pos2_entry.pack(side="left", padx=5)
        self.pos2_button = ttk.Button(self.pos2_frame, text="Move to Position 2",
                                      command=self.move_pos2)
        self.pos2_button.pack(side="left", padx=5)

    def update_speed_label(self, value):
        speed = int(float(value))
        self.speed_label.config(text=f"Speed: {speed}")
        self.settings["speed"] = speed
        self.apply_speed(speed)
        save_settings(self.settings)

    def connect_motor(self):
        try:
            self.ser = serial.Serial(port='COM8', baudrate=57600, bytesize=8,
                                     parity='N', stopbits=1, timeout=0.1)
            for sid in range(0, 11):
                if echo_servo(self.ser, sid):
                    self.servo_id = sid
                    break
            if self.servo_id is None:
                raise Exception("No servo found.")

            send_force_on(self.ser, self.servo_id)
            set_speed(self.ser, self.servo_id, self.settings["speed"])
            set_current(self.ser, self.servo_id, 800)

        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")

    def apply_speed(self, speed):
        if self.ser and self.servo_id is not None:
            set_speed(self.ser, self.servo_id, speed)

    def move_pos1(self):
        try:
            pos = int(self.pos1_entry.get())
            self.settings["pos1"] = pos
            save_settings(self.settings)
            if self.ser and self.servo_id is not None:
                move_to_position(self.ser, self.servo_id, pos)
        except ValueError:
            messagebox.showerror("Invalid Input", "Position 1 must be an integer.")

    def move_pos2(self):
        try:
            pos = int(self.pos2_entry.get())
            self.settings["pos2"] = pos
            save_settings(self.settings)
            if self.ser and self.servo_id is not None:
                move_to_position(self.ser, self.servo_id, pos)
        except ValueError:
            messagebox.showerror("Invalid Input", "Position 2 must be an integer.")

# === Entry Point ===
if __name__ == "__main__":
    root = tk.Tk()
    app = MotorApp(root)
    root.mainloop()
