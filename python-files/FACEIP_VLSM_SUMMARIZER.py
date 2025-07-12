
import tkinter as tk
from tkinter import messagebox

def ip_to_binary(ip):
    return ''.join([format(int(octet), '08b') for octet in ip.split('.')])

def binary_to_ip(bin_str):
    return '.'.join(str(int(bin_str[i:i+8], 2)) for i in range(0, 32, 8))

def calculate_vlsm():
    try:
        base_ip = entry_ip.get()
        hosts = list(map(int, entry_hosts.get().split(',')))
        hosts.sort(reverse=True)
        result = []
        current_ip = list(map(int, base_ip.split('.')))
        for h in hosts:
            bits = 32
            while (2 ** (32 - bits)) - 2 < h:
                bits -= 1
            subnet_size = 2 ** (32 - bits)
            subnet_ip = '.'.join(map(str, current_ip))
            result.append(f"{subnet_ip}/{bits} ({subnet_size} IPs)")
            current_ip[3] += subnet_size
            for i in reversed(range(1, 4)):
                if current_ip[i] > 255:
                    current_ip[i] -= 256
                    current_ip[i-1] += 1
        output.delete(0, tk.END)
        output.insert(tk.END, "VLSM Subnets:")
        for line in result:
            output.insert(tk.END, line)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def summarize_ips():
    try:
        ip_lines = entry_summarize.get("1.0", tk.END).strip().split()
        ip_binaries = [ip_to_binary(ip.split('/')[0])[:int(ip.split('/')[1])] for ip in ip_lines]
        min_len = min(len(b) for b in ip_binaries)
        summary_prefix = ""
        for i in range(min_len):
            bits = set(b[i] for b in ip_binaries)
            if len(bits) == 1:
                summary_prefix += bits.pop()
            else:
                break
        summary_ip = binary_to_ip(summary_prefix.ljust(32, '0'))
        output.insert(tk.END, f"Summarized: {summary_ip}/{len(summary_prefix)}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

root = tk.Tk()
root.title("FACEIP VLSM & Summarization Tool - SynthTape TVLINE Co.")
root.geometry("500x500")
tk.Label(root, text="Base IP for VLSM:").pack()
entry_ip = tk.Entry(root)
entry_ip.insert(0, "192.168.0.0")
entry_ip.pack()
tk.Label(root, text="Hosts per Subnet (comma separated):").pack()
entry_hosts = tk.Entry(root)
entry_hosts.insert(0, "60,30,10,2")
entry_hosts.pack()
tk.Button(root, text="Calculate VLSM", command=calculate_vlsm).pack(pady=10)

tk.Label(root, text="Enter IPs with CIDR (one per line) for Summarization:").pack()
entry_summarize = tk.Text(root, height=5)
entry_summarize.insert("1.0", "192.168.0.0/26\n192.168.0.64/26\n192.168.0.128/26")
entry_summarize.pack()
tk.Button(root, text="Summarize IPs", command=summarize_ips).pack(pady=10)

output = tk.Listbox(root)
output.pack(expand=True, fill=tk.BOTH)
root.mainloop()
