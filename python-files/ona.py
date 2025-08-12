import serial
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial.tools.list_ports
from datetime import datetime

COMMANDS = [
    "SET eeprom select MODULE0",
    "test usb ext1",
    "test usb ext2",
    "Test FPGA 0",
    "test AMB-FPGA-GPIO 0 A",
    "test AMB-FPGA-GPIO 0 B",
    "SET SUBMODULE 0 A POWER ON",
    "SET SUBMODULE 0 B POWER ON",
    "test BATTLOOPBACK 2K4K0",
    "test LOOPBACK-CLOCK 2K4K0",
    "test BATTLOOPBACK 2K4K1",
    "test LOOPBACK-CLOCK 2K4K1"
]

BAUDRATE = 115200
STEP_TIMEOUT = 60


class UUTTesterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ONA_800 v.1")

        self.serial_port = None
        self.log_data = ""

        main_frame = tk.Frame(root)
        main_frame.pack(padx=10, pady=10)

        control_frame = tk.Frame(main_frame)
        control_frame.grid(row=0, column=0, sticky="n")

        tk.Label(control_frame, text="เลือก COM Port:").pack()
        self.combobox = ttk.Combobox(control_frame, values=self.get_com_ports(), state="readonly", width=30)
        self.combobox.pack(pady=2)

        tk.Button(control_frame, text="Refresh", command=self.refresh_com_ports).pack(pady=2)

        self.sn_var = tk.StringVar()
        tk.Label(control_frame, text="Serial Number:").pack()
        self.sn_entry = tk.Entry(control_frame, textvariable=self.sn_var, state="readonly", width=30)
        self.sn_entry.pack(pady=2)

        tk.Button(control_frame, text="เริ่มทดสอบ", command=self.run_test).pack(pady=5)
        tk.Button(control_frame, text="บันทึก Log", command=self.save_log).pack(pady=2)
        tk.Button(control_frame, text="Clear Log", command=self.clear_log).pack(pady=2)

        self.status_label = tk.Label(control_frame, text="สถานะ: ยังไม่เริ่ม", fg="blue")
        self.status_label.pack(pady=10)

        log_frame = tk.Frame(main_frame)
        log_frame.grid(row=0, column=1, padx=10)

        tk.Label(log_frame, text="ผลลัพธ์ / Log:").pack(anchor="w")
        text_frame = tk.Frame(log_frame)
        text_frame.pack()

        self.result_box = tk.Text(text_frame, height=25, width=80, wrap=tk.NONE)
        self.result_box.pack(side=tk.LEFT, fill=tk.BOTH)

        scrollbar = tk.Scrollbar(text_frame, command=self.result_box.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.result_box.config(yscrollcommand=scrollbar.set)

        self.result_box.tag_config("pass", foreground="green")
        self.result_box.tag_config("fail", foreground="red")
        self.result_box.tag_config("normal", foreground="black")

    def get_com_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]

    def refresh_com_ports(self):
        self.combobox['values'] = self.get_com_ports()

    def save_log(self):
        if not self.log_data:
            messagebox.showwarning("คำเตือน", "ไม่มีข้อมูลให้บันทึก")
            return

        filename = filedialog.asksaveasfilename(defaultextension=".txt",
                                                filetypes=[("Text files", "*.txt")])
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_data)
            messagebox.showinfo("บันทึกแล้ว", f"บันทึกไฟล์: {filename}")

    def clear_log(self):
        self.result_box.delete(1.0, tk.END)
        self.log_data = ""
        self.sn_var.set("")
        self.status_label.config(text="สถานะ: ล้างแล้ว", fg="blue")

    def show_result_popup(self, result, sn):
        popup = tk.Toplevel(self.root)
        popup.title("ผลลัพธ์")
        popup.geometry("400x200")
        popup.resizable(False, False)

        if result == "PASS":
            icon = "✅"
            message = "ทดสอบผ่าน"
            color = "green"
        else:
            icon = "❌"
            message = "ทดสอบไม่ผ่าน"
            color = "red"

        frame = tk.Frame(popup, padx=20, pady=20)
        frame.pack(expand=True, fill=tk.BOTH)

        icon_label = tk.Label(frame, text=icon, font=("Arial", 60), fg=color)
        icon_label.pack(pady=(0, 15))

        text_label = tk.Label(frame, text=message, font=("Arial", 24, "bold"), fg=color)
        text_label.pack(pady=(0, 20))

        tk.Button(frame, text="ปิด", command=popup.destroy).pack(pady=5)

        # Center popup
        self.root.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - 200
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - 100
        popup.geometry(f"+{x}+{y}")

    def run_test(self):
        selected_port = self.combobox.get()
        if not selected_port:
            messagebox.showwarning("Warning", "กรุณาเลือก COM port ก่อน")
            return

        self.clear_log()
        self.status_label.config(text="สถานะ: กำลังทดสอบ...", fg="orange")
        overall_result = "PASS"

        try:
            with serial.Serial(selected_port, BAUDRATE, timeout=1) as ser:
                # อ่าน SN
                sn_command = "get eeprom records solution"
                self.log(f"[{datetime.now().strftime('%H:%M:%S')}] ส่ง: {sn_command}")
                ser.write((sn_command + "\r\n").encode())

                serial_number = "N/A"
                start_time = time.time()
                while True:
                    if ser.in_waiting:
                        line = ser.readline().decode(errors='ignore').strip()
                        if not line:
                            continue

                        self.log(f"[{datetime.now().strftime('%H:%M:%S')}] รับ: {line}")

                        if "ProductSerialNumber" in line:
                            parts = line.split(":")
                            if len(parts) == 2:
                                serial_number = parts[1].strip()
                                self.sn_var.set(serial_number)

                        if line.strip().endswith("BIST>"):
                            break

                    if time.time() - start_time > 10:
                        self.log(f"[{datetime.now().strftime('%H:%M:%S')}] รับ: (timeout)")
                        break

                    self.root.update()

                # เริ่มคำสั่งทดสอบ
                for cmd in COMMANDS:
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.log(f"[{timestamp}] ส่ง: {cmd}")
                    ser.write((cmd + "\r\n").encode())

                    final_response = ""
                    start_time = time.time()

                    is_set_command = cmd.strip().upper().startswith("SET")
                    is_test_command = cmd.strip().upper().startswith("TEST")

                    while True:
                        if ser.in_waiting:
                            line = ser.readline().decode(errors='ignore').strip()
                            if not line:
                                continue

                            line_upper = line.upper()
                            t_resp = datetime.now().strftime("%H:%M:%S")

                            if is_set_command and line_upper == "OK":
                                final_response = "PASS (จาก SET: OK)"
                                self.log(f"[{t_resp}] รับ: OK")
                                self.log(f"[{t_resp}] → PASS")
                                break

                            if is_test_command:
                                if "PASS:" in line_upper or "FAIL:" in line_upper:
                                    final_response = line
                                    self.log(f"[{t_resp}] รับ: {final_response}")
                                    break

                            if line_upper == "OK":
                                self.log(f"[{t_resp}] รับ: OK")

                        if time.time() - start_time > STEP_TIMEOUT:
                            final_response = "(timeout)"
                            t_resp = datetime.now().strftime("%H:%M:%S")
                            self.log(f"[{t_resp}] รับ: {final_response}")
                            break

                        self.root.update()

                    if ("FAIL" in final_response.upper() or
                        "timeout" in final_response.lower()):
                        overall_result = "FAIL"

                    self.result_box.insert(tk.END, "\n")
                    self.root.update()

            final_text = "ทดสอบผ่าน" if overall_result == "PASS" else "ทดสอบไม่ผ่าน"
            final_color = "green" if overall_result == "PASS" else "red"
            self.status_label.config(text=f"สถานะ: {final_text}", fg=final_color)
            self.log(f"\n==== RESULT: {overall_result} ====\n")

            self.show_result_popup(overall_result, self.sn_var.get())

        except Exception as e:
            messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")
            self.status_label.config(text="สถานะ: เกิดข้อผิดพลาด", fg="red")

    def log(self, message):
        msg_upper = message.upper()
        if "PASS" in msg_upper:
            tag = "pass"
        elif "FAIL" in msg_upper or "ERROR" in msg_upper or "TIMEOUT" in msg_upper:
            tag = "fail"
        else:
            tag = "normal"

        self.result_box.insert(tk.END, message + "\n", tag)
        self.result_box.see(tk.END)
        self.log_data += message + "\n"


# ---- เริ่มโปรแกรม ----
if __name__ == "__main__":
    root = tk.Tk()
    app = UUTTesterApp(root)
    root.mainloop()
