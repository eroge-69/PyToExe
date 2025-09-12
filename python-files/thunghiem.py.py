import snap7 
from snap7.util import get_bool, set_bool
import tkinter as tk
from tkinter import messagebox

window = tk.Tk()
window.title("MTS Intelligent Control Suite for S7-1200 PLC")
window.geometry("800x600")

label = tk.Label(window, text="""
███    ███ ████████ ███████ 
████  ████    ██    ██      
██ ████ ██    ██    ███████ 
██  ██  ██    ██         ██ 
██      ██    ██    ███████ 
""", font=("Consolas", 20), fg="grey")
label.pack(pady=20)

frame_connect = tk.Frame(window)
frame_connect.pack()

tk.Label(frame_connect, text="IP của PLC:").pack()
ip_entry = tk.Entry(frame_connect, width=30)
ip_entry.pack(pady=5)

tk.Label(frame_connect, text="Rack:").pack()
rack_entry = tk.Entry(frame_connect, width=30)
rack_entry.pack(pady=5)

tk.Label(frame_connect, text="Slot:").pack()
slot_entry = tk.Entry(frame_connect, width=30)
slot_entry.pack(pady=5)

label_status = tk.Label(frame_connect, text="")
label_status.pack(pady=10)

plc = snap7.client.Client()

# Tạo frame điều khiển nhưng chưa hiển thị
frame_control = tk.Frame(window)
label_input = tk.Label(frame_control, text="I0.0 = ?")
label_output = tk.Label(frame_control, text="Q0.0 = ?")
led = tk.Label(frame_control, width=4, height=2, bg="red")
btn_read = tk.Button(frame_control, text="Đọc I0.0", command=lambda: read_input())
btn_write = tk.Button(frame_control, text="Bật/Tắt Q0.0", command=lambda: write_output())

def update_led(state):
    led.config(bg="green" if state else "red")

def read_input():
    try:
        data = plc.read_area(0x81, 0, 0, 1)
        bit = get_bool(data, 0, 0)
        label_input.config(text="I0.0 = " + ("ON" if bit else "OFF"))
        update_led(bit)
    except:
        label_input.config(text="I0.0 = LỖI")

def write_output():
    try:
        data = plc.read_area(0x82, 0, 0, 1)
        current = get_bool(data, 0, 0)
        set_bool(data, 0, 0, not current)
        plc.write_area(0x82, 0, 0, data)
        label_output.config(text="Q0.0 = " + ("ON" if not current else "OFF"))
        update_led(not current)
    except:
        label_output.config(text="Q0.0 = LỖI")

def show_control_frame():
    frame_control.pack(pady=20)
    label_input.pack(pady=5)
    label_output.pack(pady=5)
    led.pack(pady=5)
    btn_read.pack(pady=5)
    btn_write.pack(pady=5)

def connect_plc():
    ip = ip_entry.get()
    try:
        rack = int(rack_entry.get())
        slot = int(slot_entry.get())
    except ValueError:
        messagebox.showerror("Lỗi dữ liệu", "Rack và Slot phải là số nguyên!")
        return
    try:
        plc.connect(ip, rack, slot)
        if plc.get_connected():
            messagebox.showinfo("Thành công", "Kết nối thành công tới PLC!")
            frame_connect.pack_forget()  # Ẩn form nhập IP
            show_control_frame()         # Hiện các nút điều khiển
            read_input()                 # Đọc trạng thái đầu vào
        else:
            messagebox.showwarning("Thất bại", "Không thể kết nối tới PLC!")
    except Exception as e:
        messagebox.showerror("Lỗi kết nối", f"Lỗi: {e}")

connect_button = tk.Button(frame_connect, text="Kết nối PLC", command=connect_plc)
connect_button.pack(pady=10)

window.mainloop()
