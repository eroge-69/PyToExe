import os
import subprocess
import shutil
import tkinter as tk
from tkinter import messagebox, scrolledtext

TOOLS = ["subfinder", "httpx", "gau", "gf", "nuclei"]

# Install missing tools
def check_and_install_tools():
    for tool in TOOLS:
        if not shutil.which(tool):
            console_output.insert(tk.END, f"[!] {tool} not found. Please install it manually or use WSL.\n")

def run_recon():
    domain = domain_entry.get().strip()
    if not domain:
        messagebox.showwarning("Input Error", "Please enter a domain.")
        return

    output_dir = f"recon/{domain}"
    os.makedirs(output_dir, exist_ok=True)

    console_output.insert(tk.END, f"[*] Starting recon for {domain}\n")

    check_and_install_tools()

    tools = {
        "subfinder": f"subfinder -d {domain} -silent > {output_dir}/subdomains.txt",
        "httpx": f"httpx -l {output_dir}/subdomains.txt -silent > {output_dir}/live.txt",
        "gau": f"gau {domain} > {output_dir}/urls.txt",
        "gf-xss": f"type {output_dir}\\urls.txt | gf xss > {output_dir}\\xss.txt",
        "gf-sqli": f"type {output_dir}\\urls.txt | gf sqli > {output_dir}\\sqli.txt",
        "gf-lfi": f"type {output_dir}\\urls.txt | gf lfi > {output_dir}\\lfi.txt",
        "nuclei": f"mkdir {output_dir}\\nuclei && nuclei -l {output_dir}\\live.txt -severity high,critical -silent -o {output_dir}\\nuclei\\high_critical.txt"
    }

    for name, cmd in tools.items():
        console_output.insert(tk.END, f"[+] Running {name}...\n")
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError:
            console_output.insert(tk.END, f"[!] {name} failed\n")

    console_output.insert(tk.END, "\n[+] Recon complete!\n")
    console_output.insert(tk.END, f"[+] Results saved in {output_dir}\n")


# GUI Setup
root = tk.Tk()
root.title("HOF Recon Tool - GUI Edition (Windows)")
root.geometry("750x520")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Enter Target Domain:").grid(row=0, column=0, padx=5)
domain_entry = tk.Entry(frame, width=50)
domain_entry.grid(row=0, column=1, padx=5)

tk.Button(frame, text="Start Recon", command=run_recon, bg="#4CAF50", fg="white").grid(row=0, column=2, padx=5)

console_output = scrolledtext.ScrolledText(root, width=95, height=25, bg="black", fg="lime")
console_output.pack(pady=10)

root.mainloop()
