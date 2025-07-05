import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import telnetlib
import socket
import threading
import binascii
import struct


def tea_encrypt(v, k):
    v0, v1 = v
    delta = 0x9E3779B9
    sum = 0
    for _ in range(32):
        sum = (sum + delta) & 0xFFFFFFFF
        v0 = (v0 + (((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1])) ) & 0xFFFFFFFF
        v1 = (v1 + (((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3])) ) & 0xFFFFFFFF
    return v0, v1

def parse_tea_keys(entries):
    try:
        return [int(entry.get(), 16) for entry in entries]
    except:
        return None

class TcpProtocolClient:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Protocol Client")

        self.protocol = tk.StringVar(value="TCP")

        # ����� �����
        tk.Label(root, text="Protocol:").grid(row=0, column=0, sticky='e')
        ttk.Combobox(root, textvariable=self.protocol, values=["TCP"], width=7).grid(row=0, column=1)

        self.ip_entry = tk.Entry(root)
        self.ip_entry.insert(0, "127.0.0.1") #�����������
        self.ip_entry.grid(row=0, column=2, sticky="we")

        self.port_entry = tk.Entry(root, width=6)
        self.port_entry.insert(0, "23")
        self.port_entry.grid(row=0, column=3)

        self.connect_button = tk.Button(root, text="Connect", command=self.connect)
        self.connect_button.grid(row=0, column=4)

        self.disconnect_button = tk.Button(root, text="Disconnect", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=5)

        self.hex_mode = tk.BooleanVar()
        tk.Checkbutton(root, text="HEX Mode", variable=self.hex_mode).grid(row=0, column=6, sticky="w")

        # TEA keys
        tk.Label(root, text="TEA Keys:").grid(row=1, column=0, sticky='e')
        self.tea_keys = [tk.Entry(root, width=10) for _ in range(4)]
        for i, e in enumerate(self.tea_keys):
            e.insert(0, f"{(i+1)*0x01020304:08X}")
            e.grid(row=1, column=i+1)
        tk.Button(root, text="Send TEA Auth", command=self.send_tea_auth).grid(row=1, column=5)

        # ����� ����
        self.output = scrolledtext.ScrolledText(root, wrap=tk.WORD)
        self.output.grid(row=2, column=0, columnspan=7, padx=5, pady=5, sticky="nsew")

        # ������ �����
        self.send_entry = tk.Entry(root)
        self.send_entry.grid(row=3, column=0, columnspan=6, sticky="we", padx=5)
        self.send_button = tk.Button(root, text="Send", command=self.send)
        self.send_button.grid(row=3, column=6)

        # ����������������
        for col in range(7):
            root.grid_columnconfigure(col, weight=1)
        root.grid_rowconfigure(2, weight=1)

        self.connection = None
        self.running = False

    def connect(self):
        proto = self.protocol.get()
        try:
            if proto == "TCP":
                self.connection = telnetlib.Telnet(self.ip_entry.get(), int(self.port_entry.get()), timeout=5)
                self.receiver_thread = threading.Thread(target=self.receive_tcp, daemon=True)
            else:
                raise Exception("Unknown protocol")

            self.running = True
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.log(f"[Connected] via {proto}")
            self.receiver_thread.start()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def disconnect(self):
        self.running = False
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.log("[Disconnected]")

    def send(self):
        if not self.connection:
            return
        msg = self.send_entry.get()
        if self.hex_mode.get():
            try:
                data = binascii.unhexlify(msg.replace(" ", ""))
            except:
                self.log("[HEX Error] Invalid HEX")
                return
        else:
            data = msg.encode('utf-8')

        proto = self.protocol.get()
        try:
            if proto == "TCP":
                self.connection.write(data)
            self.log(f"> {msg}")
        except Exception as e:
            self.log(f"[Send Error] {e}")

    def receive_tcp(self):
        while self.running:
            try:
                data = self.connection.read_very_eager()
                if data:
                    self.display_data(data)
            except:
                pass

    def send_tea_auth(self):
        keys = parse_tea_keys(self.tea_keys)
        if not keys:
            self.log("[TEA Error] Invalid keys")
            return

        plain = (0x00000000, 0x00000001)
        enc = tea_encrypt(plain, keys)
        auth = struct.pack(">2I", *enc)

        if self.connection:
            try:
                proto = self.protocol.get()
                if proto == "TCP":
                    self.connection.write(auth)
                self.log(f"[TEA] Auth sent: {auth.hex().upper()}")
            except Exception as e:
                self.log(f"[TEA Error] {e}")
        else:
            self.log("[TEA] Not connected")

    def display_data(self, data):
        if self.hex_mode.get():
            msg = binascii.hexlify(data).decode('ascii').upper()
        else:
            msg = data.decode('utf-8', errors='ignore')
        self.log(msg)

    def log(self, message):
        self.output.config(state=tk.NORMAL)
        self.output.insert(tk.END, message + "\n")
        self.output.see(tk.END)
        self.output.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    app = TcpProtocolClient(root)
    root.minsize(300,200 )
    root.mainloop()
