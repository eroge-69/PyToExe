import tkinter as tk
from tkinter import scrolledtext, messagebox

def parse_heartbeat(hex_string):
    from struct import unpack

    try:
        bytes_data = [int(b, 16) for b in hex_string.strip().split()]
    except ValueError:
        return ["❌ Error: Invalid hex format."]

    if len(bytes_data) < 40:
        return ["❌ Error: Heartbeat too short or incomplete."]

    output = []
    output.append("=== Parsed Heartbeat Packet ===\n")

    output.append(f"Header: 0x{bytes_data[0]:02X} → {'Valid' if bytes_data[0] == 0x48 else 'Invalid'} (Should be 0x48)")
    output.append(f"Length: {bytes_data[1]} bytes of payload")
    output.append(f"Protocol Version: {bytes_data[2]}")
    output.append(f"Device Type: {bytes_data[3]}")
    output.append(f"Device ID: {bytes_data[4]}")
    output.append(f"Reserved: 0x{bytes_data[5]:02X}")
    output.append(f"Command: 0x{bytes_data[6]:02X} → {'Heartbeat' if bytes_data[6] == 0x00 else 'Other'}")
    output.append(f"Serial Number: {bytes_data[7]}")
    
    status_byte = bytes_data[8]
    status_map = {0x00: 'Idle', 0x01: 'Initializing', 0x02: 'Busy', 0x03: 'Error'}
    output.append(f"Status Byte: 0x{status_byte:02X} → {status_map.get(status_byte, 'Unknown')}")

    output.append(f"Inside Temp: {bytes_data[9]}°C")
    output.append(f"Condenser Temp: {bytes_data[10]}°C")
    output.append(f"Outside Temp: {bytes_data[11]}°C")

    load_cell = (bytes_data[12] << 8) | bytes_data[13]
    output.append(f"Load Cell Reading: {load_cell}")

    input_status = bytes_data[14:18]
    output.append(f"Input Status (raw): {' '.join(f'{b:02X}' for b in input_status)}")

    output_status = bytes_data[18:20]
    output.append(f"Output Status (raw): {' '.join(f'{b:02X}' for b in output_status)}")

    x_axis = (bytes_data[20] << 8) | bytes_data[21]
    y_axis = (bytes_data[22] << 8) | bytes_data[23]
    z_axis = (bytes_data[24] << 8) | bytes_data[25]
    output.append(f"X Axis Position: {x_axis} mm")
    output.append(f"Y Axis Position: {y_axis} mm")
    output.append(f"Z Axis Position: {z_axis} mm")

    motor_currents = bytes_data[26:29]
    output.append(f"Motor Current X/A: {motor_currents[0]/10:.1f} A")
    output.append(f"Motor Current Y/B: {motor_currents[1]/10:.1f} A")
    output.append(f"Motor Current Z/C: {motor_currents[2]/10:.1f} A")

    error_status = bytes_data[29:37]
    if any(error_status):
        output.append("⚠️ Error Status: Non-zero values detected")
        output.append(f"Raw: {' '.join(f'{b:02X}' for b in error_status)}")
    else:
        output.append("Error Status: No errors reported")

    output.append(f"Checksum: 0x{bytes_data[-2]:02X}")
    output.append(f"Tail: 0x{bytes_data[-1]:02X} → {'Valid' if bytes_data[-1] == 0x54 else 'Invalid'} (Should be 0x54)")

    return output

def run_parser():
    hex_input = input_text.get("1.0", tk.END).strip()
    if not hex_input:
        messagebox.showwarning("No Input", "Please paste a heartbeat hex line.")
        return

    result = parse_heartbeat(hex_input)
    output_box.config(state='normal')
    output_box.delete("1.0", tk.END)
    output_box.insert(tk.END, "\n".join(result))
    output_box.config(state='disabled')

# GUI Setup
root = tk.Tk()
root.title("Heartbeat Byte Decoder")
root.geometry("800x600")

tk.Label(root, text="Paste Heartbeat Hex Line Below:").pack(pady=5)
input_text = scrolledtext.ScrolledText(root, height=4, font=("Courier", 10))
input_text.pack(padx=10, fill=tk.X)

tk.Button(root, text="Parse Heartbeat", command=run_parser, height=2, bg="lightblue").pack(pady=10)

tk.Label(root, text="Parsed Output:").pack(pady=5)
output_box = scrolledtext.ScrolledText(root, state='disabled', font=("Courier", 10))
output_box.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

root.mainloop()
