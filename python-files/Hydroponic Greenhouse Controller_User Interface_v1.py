import socket
import tkinter as tk
from tkinter import font

# --- Communication parameters ---
UDP_IP = "10.0.0.133"   # Arduino IP address
UDP_PORT = 2390         # Arduino listening port
REFRESH_RATE = 2000     # ms (Tkinter uses milliseconds)

# --- UDP socket setup ---
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)  # timeout in case Arduino does not respond

# --- Variables to request ---
command = "Read All"
variable_labels = [
    " Time",
    " Temperature (°C)",
    " Humidity (%)",
    " Fan Mode",
    " Light Mode",
    " Light Type Mode",
    " Pump Mode",
    " Fan State",
    " Light State",
    " Pump State",
    " Temp Low",
    " Temp High",
    " Day Time",
    " Night Time",
    " Pump Cycle Time"
]
number_of_variables = len(variable_labels)

# --- Globals ---
variable_values = ["Empty"] * number_of_variables
value_entries = []
root = None


# Conversion cm to pixels
def cm_to_px(cm):
    return int(cm * 37.8)


def create_ui():
    global root, value_entries
    value_entries = []

    # Dimensions principales
    window_width_cm = 16
    window_height_cm = 20
    size_cm = 10

    root.title("Hydroponic Greenhouse Controller")
    root.geometry(f"{cm_to_px(window_width_cm)}x{cm_to_px(window_height_cm)}")

    # Police Calibri 20pt
    calibri_font = font.Font(family="Calibri", size=20)

    # Titre
    title_frame = tk.Frame(root, bg="#00B050", width=cm_to_px(size_cm))
    title_frame.pack(pady=5)
    title_label = tk.Label(
        title_frame,
        text="Hydroponic Greenhouse Controller",
        bg="#00B050", fg="white", font=calibri_font,
        width=cm_to_px(size_cm)//10, anchor='center'
    )
    title_label.pack(padx=5, pady=5)

    # Entêtes colonnes
    header_frame = tk.Frame(root)
    header_frame.pack(pady=5)

    var_name_label = tk.Label(header_frame, text=" Variable name",
                              bg="#2F75B5", fg="white", font=calibri_font,
                              width=cm_to_px(size_cm/2)//10, anchor='w')
    var_name_label.grid(row=0, column=0, padx=2, pady=2)

    value_label = tk.Label(header_frame, text=" Value",
                           bg="#2F75B5", fg="white", font=calibri_font,
                           width=cm_to_px(size_cm/2)//10, anchor='w')
    value_label.grid(row=0, column=1, padx=2, pady=2)

    # Labels variables + entries
    for i, var in enumerate(variable_labels):
        var_label = tk.Label(header_frame, text=var,
                             bg="#DDEBF7", fg="black", font=calibri_font,
                             width=cm_to_px(size_cm/2)//10, anchor='w')
        var_label.grid(row=i+1, column=0, padx=2, pady=2)

        val_entry = tk.Entry(header_frame, bg="#DDEBF7", fg="black",
                             font=calibri_font, width=cm_to_px(size_cm/2)//10,
                             justify='left')
        val_entry.insert(0, variable_values[i])
        val_entry.grid(row=i+1, column=1, padx=2, pady=2)
        value_entries.append(val_entry)


def update_values(values):
    """Update the UI with new values."""
    for i in range(number_of_variables):
        value_entries[i].delete(0, tk.END)
        value_entries[i].insert(0, values[i])


def request_variables():
    """Send command and receive variable values via UDP."""
    global variable_values
    try:
        sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
        response, _ = sock.recvfrom(1024)
        response = response.decode().strip()
        for i in range(number_of_variables):
            response, _ = sock.recvfrom(1024)
            response = response.decode().strip()
            if "=" in response:
                variable_values[i] = response.split("=", 1)[1]
            else:
                variable_values[i] = "Empty"
    except socket.timeout:
        print("[Warning] Timeout waiting for Arduino response.")
    except Exception as e:
        print(f"[Error] {e}")


def periodic_update():
    """Request variables and refresh UI on a timer."""
    request_variables()

    print("-" * 40)
    for i in range(number_of_variables):
        print(f"{variable_labels[i]} = {variable_values[i]}")

    update_values(variable_values)

    # schedule next call
    root.after(REFRESH_RATE, periodic_update)


def main():
    global root
    root = tk.Tk()
    create_ui()

    # start periodic update
    root.after(REFRESH_RATE, periodic_update)

    root.mainloop()


if __name__ == "__main__":
    main()
