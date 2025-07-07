import re
import datetime
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, messagebox

# Function to parse log entries
def parse_log(file_path):
    entries = []
    with open(file_path, 'r') as file:
        for line in file:
            match = re.match(r'^(\d{2}_\d{2}_\d{2}-\d{2}:\d{2}:\d{2}\.\d{3}) .*? (TX|RX) : ([0-9A-F ]+)', line)
            if match:
                timestamp = datetime.datetime.strptime(match[1], "%y_%m_%d-%H:%M:%S.%f")
                direction = match[2]
                data = match[3].strip()
                entries.append({"timestamp": timestamp, "direction": direction, "data": data})
    return entries

# Function to identify errors
def identify_errors(entries):
    errors = []
    for entry in entries:
        if 'FF FF' in entry['data']:  # Example error pattern
            errors.append(entry)
    return errors

# Function to visualize data flow
def visualize_data_flow(entries):
    tx_times = [entry['timestamp'] for entry in entries if entry['direction'] == 'TX']
    rx_times = [entry['timestamp'] for entry in entries if entry['direction'] == 'RX']

    plt.figure(figsize=(10, 5))
    plt.plot(tx_times, [1] * len(tx_times), 'go', label='TX')
    plt.plot(rx_times, [0] * len(rx_times), 'ro', label='RX')
    plt.yticks([0, 1], ['RX', 'TX'])
    plt.xlabel('Time')
    plt.title('Data Flow Visualization')
    plt.legend()
    plt.grid(True)
    plt.show()

# GUI Interface
def run_gui():
    def open_file():
        file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file_path:
            entries = parse_log(file_path)
            errors = identify_errors(entries)

            result_text.delete('1.0', tk.END)
            result_text.insert(tk.END, f"Total Entries: {len(entries)}\n")
            result_text.insert(tk.END, f"Potential Errors Found: {len(errors)}\n")
            for error in errors:
                result_text.insert(tk.END, f"[{error['timestamp']}] {error['direction']} : {error['data']}\n")

            visualize_data_flow(entries)

    # Tkinter setup
    root = tk.Tk()
    root.title("Serial Log Analyzer")

    open_button = tk.Button(root, text="Open Log File", command=open_file)
    open_button.pack(pady=10)

    result_text = tk.Text(root, height=20, width=80)
    result_text.pack(padx=10, pady=10)

    root.mainloop()

# Main execution block
def main():
    run_gui()

if __name__ == "__main__":
    main()