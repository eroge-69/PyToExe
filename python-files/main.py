import base64
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import urllib.parse
import time
import hmac
import hashlib
import struct

# ---------------------- TOTP FUNCTIONS ----------------------
def get_totp_token(secret):
    key = base64.b32decode(secret.upper() + '=' * ((8 - len(secret) % 8) % 8))
    msg = struct.pack('>Q', int(time.time()) // 30)
    hmac_digest = hmac.new(key, msg, hashlib.sha1).digest()
    ob = hmac_digest[19] & 15
    token = (struct.unpack(">I", hmac_digest[ob:ob + 4])[0] & 0x7fffffff) % 1000000
    return f"{token:06d}"

# ---------------------- PROTOBUF DECODER ----------------------
# Minimal decoder for Google Authenticator's MigrationPayload

class OTPEntry:
    def __init__(self, name, issuer, secret):
        self.name = name
        self.issuer = issuer
        self.secret = base64.b32encode(secret).decode('utf-8').replace('=', '')

# Protobuf wire types
VARINT = 0
LENGTH_DELIM = 2


def read_varint(data, idx):
    shift = 0
    result = 0
    while True:
        byte = data[idx]
        idx += 1
        result |= (byte & 0x7F) << shift
        if not byte & 0x80:
            break
        shift += 7
    return result, idx


def parse_otp_entries(data):
    idx = 0
    entries = []

    while idx < len(data):
        tag, idx = read_varint(data, idx)
        field_num = tag >> 3
        wire_type = tag & 0x07

        if field_num == 1 and wire_type == LENGTH_DELIM:  # Repeated OTPParameters
            length, idx = read_varint(data, idx)
            sub_data = data[idx:idx + length]
            idx += length

            name = issuer = secret = None
            sub_idx = 0
            while sub_idx < len(sub_data):
                sub_tag, sub_idx = read_varint(sub_data, sub_idx)
                sub_field = sub_tag >> 3
                sub_wire = sub_tag & 0x07

                if sub_wire == LENGTH_DELIM:
                    sub_len, sub_idx = read_varint(sub_data, sub_idx)
                    val = sub_data[sub_idx:sub_idx + sub_len]
                    sub_idx += sub_len

                    if sub_field == 1:
                        name = val.decode()
                    elif sub_field == 2:
                        issuer = val.decode()
                    elif sub_field == 3:
                        secret = val
            if name and secret:
                entries.append(OTPEntry(name, issuer or '', secret))
        else:
            if wire_type == LENGTH_DELIM:
                l, idx = read_varint(data, idx)
                idx += l
            elif wire_type == VARINT:
                _, idx = read_varint(data, idx)
            else:
                break
    return entries


# ---------------------- APP UI ----------------------
class AuthApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Authenticator App")
        self.accounts = []

        self.tree = ttk.Treeview(root, columns=("Issuer", "Name", "Code"), show='headings')
        self.tree.heading("Issuer", text="Issuer")
        self.tree.heading("Name", text="Account")
        self.tree.heading("Code", text="Current Code")
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Import from Link", command=self.import_from_link).pack(side=tk.LEFT, padx=5)
        self.refresh()

    def refresh(self):
        self.tree.delete(*self.tree.get_children())
        for acc in self.accounts:
            code = get_totp_token(acc.secret)
            self.tree.insert('', 'end', values=(acc.issuer, acc.name, code))
        self.root.after(1000, self.refresh)

    def import_from_link(self):
        link = simpledialog.askstring("Import", "Paste otpauth-migration link:")
        if not link:
            return

        try:
            parsed = urllib.parse.urlparse(link)
            if not parsed.scheme.startswith("otpauth-migration"):
                raise ValueError("Not a valid otpauth-migration link")

            data_encoded = urllib.parse.parse_qs(parsed.query).get("data", [None])[0]
            if not data_encoded:
                raise ValueError("Missing data parameter")

            data = base64.urlsafe_b64decode(data_encoded + '===')
            new_accounts = parse_otp_entries(data)
            self.accounts.extend(new_accounts)
            messagebox.showinfo("Success", f"Imported {len(new_accounts)} account(s).")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import: {e}")


if __name__ == '__main__':
    root = tk.Tk()
    app = AuthApp(root)
    root.mainloop()
