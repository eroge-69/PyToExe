from tkinter import Tk, Button, messagebox
import serial
import threading
import time

window = Tk()
window.title("TNC Communication")
window.geometry("700x700")
window.configure(bg="lightblue")

ser = None
command_running = False
reader_thread = None

def initialize_serial():
    global ser
    try:
        ser = serial.Serial(port="COM8", baudrate=115200, timeout=1)
        print("Serial port opened successfully.")
    except Exception as e:
        print(f"Error opening serial port: {e}")
        ser = None

def read_from_serial(timeout=10):
    global ser, command_running

    start_time = time.time()
    while command_running:
        try:
            if ser and ser.in_waiting:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Received from TNC: {line}")
        except Exception as e:
            print(f"Error reading serial: {e}")
            break

        if time.time() - start_time > timeout:
            print("10 seconds reached. Auto stopping...")
            stop_communication(auto=True)
            break

        time.sleep(0.05)

def send_command():
    global ser
    try:
        ser.write(b'start\n')
        print("Start command sent.")
    except Exception as e:
        print(f"Error sending start: {e}")
        messagebox.showerror("Error", f"Error sending start: {e}")

def start_communication():
    global command_running, reader_thread
    if ser is None:
        messagebox.showerror("Error", "Serial port not initialized.")
        return

    if not command_running:
        command_running = True
        send_command()
        reader_thread = threading.Thread(target=read_from_serial, args=(10,), daemon=True)
        reader_thread.start()

def stop_communication(auto=False):
    global command_running
    if ser is None:
        messagebox.showerror("Error", "Serial port not initialized.")
        return

    if command_running:
        command_running = False
        try:
            ser.write(b'stop\n')
            print("Stop command sent to TNC.")
            if not auto:
                messagebox.showinfo("Stopped", "Manual stop successful.")
        except Exception as e:
            print(f"Error sending stop: {e}")
            if not auto:
                messagebox.showerror("Error", f"Error sending stop: {e}")

# UI Buttons
start_button = Button(window, text="Start", command=start_communication, bg="green", fg="white")
start_button.pack(pady=10)

stop_button = Button(window, text="Stop (Manual)", command=stop_communication, bg="red", fg="white")
stop_button.pack(pady=10)

if __name__ == "__main__":
    initialize_serial()
    window.mainloop()

    # Cleanup
    if ser and ser.is_open:
        ser.close()
    print("Serial port closed.")