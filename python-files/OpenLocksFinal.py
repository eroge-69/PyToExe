import socket
import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os
import subprocess
import platform

# Cesta k logu ve složce uživatele
LOG_FILE = os.path.expanduser("~/kerong_log.txt")

def log(text: str):
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            f.write(f"{ts} {text}\n")
    except Exception as e:
        print(f"Chyba při zápisu logu: {e}")

def compute_checksum(data):
    return sum(data) & 0xFF

def build_unlock_command(cu_addr, lock_no):
    combined = (cu_addr << 4) | lock_no
    command = [0x02, combined, 0x31, 0x03]
    checksum = compute_checksum(command)
    command.append(checksum)
    return bytes(command)

def is_board_online(ip: str, port: int = 4001, timeout: float = 1.0) -> bool:
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception:
        return False

def send_open_command(ip: str, port: int, cu_addr: int, lock_no: int):
    command = build_unlock_command(cu_addr, lock_no)
    log(f"W: Odesílám příkaz: {'-'.join(f'{b:02X}' for b in command)}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, port))
            s.sendall(command)
            try:
                response = s.recv(1024)
                if response:
                    log(f"R: Přijatá odpověď: {'-'.join(f'{b:02X}' for b in response)}")
                else:
                    log("R: Žádná odpověď")
            except socket.timeout:
                log("R: Timeout na odpověď")
            return "✅ Příkaz odeslán."
    except Exception as e:
        log(f"Chyba odeslání: {e}")
        return f"❌ Chyba: {e}"

def open_log_file():
    try:
        if platform.system() == "Windows":
            os.startfile(LOG_FILE)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", LOG_FILE])
        else:  # Linux
            subprocess.call(["xdg-open", LOG_FILE])
    except Exception as e:
        messagebox.showerror("Chyba", f"Nelze otevřít log: {e}")

def create_gui():
    def check_status():
        ip_address = ip_entry.get().strip()
        if not ip_address:
            board_status_label.config(text="Board status: ?", fg="blue")
            return
        if is_board_online(ip_address):
            board_status_label.config(text="Board online ✅", fg="green")
        else:
            board_status_label.config(text="Board offline ❌", fg="red")

    def open_box():
        ip_address = ip_entry.get().strip()
        board_no_input = board_entry.get().strip()
        box_no_input = box_entry.get().strip()

        if not ip_address:
            messagebox.showerror("Chyba", "Zadejte IP adresu pointu.")
            return
        if not board_no_input.isdigit() or not box_no_input.isdigit():
            messagebox.showerror("Chyba", "Zadejte platná čísla pro board a schránku.")
            return

        cu_addr = int(board_no_input)
        lock_no = int(box_no_input)
        if lock_no < 0 or lock_no > 47:
            messagebox.showerror("Chyba", "Číslo schránky musí být 0–47.")
            return

        if not is_board_online(ip_address):
            messagebox.showwarning("Board offline", f"CU {cu_addr} na IP {ip_address} není dostupný.")
            board_status_label.config(text="Board offline ❌", fg="red")
            return

        board_status_label.config(text="Board online ✅", fg="green")
        response = send_open_command(ip_address, 4001, cu_addr, lock_no)
        messagebox.showinfo("Výsledek", f"CU: {cu_addr}, Schránka: {lock_no}\n{response}")

    def open_all_boxes():
        ip_address = ip_entry.get().strip()
        board_no_input = board_entry.get().strip()

        if not ip_address or not board_no_input.isdigit():
            messagebox.showerror("Chyba", "Zadejte IP adresu a číslo boardu.")
            return

        if not messagebox.askyesno("Potvrzení", "Opravdu chcete otevřít VŠECHNY schránky?"):
            return

        cu_addr = int(board_no_input)

        if not is_board_online(ip_address):
            messagebox.showwarning("Board offline", f"CU {cu_addr} na IP {ip_address} není dostupný.")
            board_status_label.config(text="Board offline ❌", fg="red")
            return

        board_status_label.config(text="Board online ✅", fg="green")

        result = ""
        for lock_no in range(0, 16):  # 0–15 (změň podle počtu schránek)
            response = send_open_command(ip_address, 4001, cu_addr, lock_no)
            result += f"Schránka {lock_no}: {response}\n"

        messagebox.showinfo("Výsledek", result)

    def clear_log():
        try:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.write("")
            messagebox.showinfo("Log", "Log byl vymazán.")
        except Exception as e:
            messagebox.showerror("Chyba", f"Nelze vymazat log: {e}")

    root = tk.Tk()
    root.title("Kerong Box Opener")
    root.geometry("400x450")

    tk.Label(root, text="IP adresa pointu (Teltonika):").pack(pady=5)
    ip_entry = tk.Entry(root, width=30)
    ip_entry.pack(pady=5)
    ip_entry.insert(0, "10.24.12.193")

    tk.Label(root, text="Číslo CU boardu (0–255):").pack(pady=5)
    board_entry = tk.Entry(root, width=10)
    board_entry.pack(pady=5)

    tk.Label(root, text="Číslo schránky (0–47):").pack(pady=5)
    box_entry = tk.Entry(root, width=10)
    box_entry.pack(pady=5)

    check_button = tk.Button(root, text="Zkontrolovat dostupnost boardu", command=check_status)
    check_button.pack(pady=5)

    open_button = tk.Button(root, text="Otevřít schránku", command=open_box)
    open_button.pack(pady=10)

    open_all_button = tk.Button(root, text="Otevřít VŠECHNY schránky na boardu", command=open_all_boxes, bg="red", fg="white")
    open_all_button.pack(pady=5)

    clear_log_button = tk.Button(root, text="Vymazat log", command=clear_log)
    clear_log_button.pack(pady=5)

    show_log_button = tk.Button(root, text="Zobrazit log", command=open_log_file)
    show_log_button.pack(pady=5)

    board_status_label = tk.Label(root, text="Board status: ?", fg="blue")
    board_status_label.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
