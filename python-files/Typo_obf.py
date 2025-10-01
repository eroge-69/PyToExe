# Typo_obf_clip.py
import tkinter as tk
from tkinter import simpledialog, messagebox
import os, hashlib, base64, zlib, json

PASSWORD_FILE = "password.txt"

# --- Encoded data block (replace the placeholder with the string printed by helper_make_block.py) ---
# Example:
# _ENC = b"""<very-long-base64-text>"""
_ENC = b'''eJxlkttu2kAQhl9l4qtWoiiYM3cpIYS0pDSHklRI1rKeEktm19pdl6CId+/OGGOgN/a3M//8M3v4CFJ0Dk3kdKTy9RJNMICP4Mp/g1Y3qEHwlbDZIBwSdhmvCXstwhFHGW8IGyHhmLDfJ7xlLZdN2Ix971jQIfxG2Gbtd8JOj3DKURbc8zjs8IO7cXTGZpeEPxnZ4YG7scMjj8PRJy5j7TO3aBL+4jIefc7jsOCFMGTBK8/QJvzNDmGw81ycFJ1ZcXp8ZpckGJK0QTQlColuiZpEL0QtomeiNtE9UYfolahLdEfUIxoT9YkeuHMqlpha7mfRRS5xKVL2ER3MhLUbbWIqoWRm9DpzlL1JjHVgcgUxOpQO4wugiq3ODWT7sgHVpXqVqMr22LJIVaYj5Xd+Wr3BVOo1VvXzInCcW9sVZa6kRGthbIS3Yf81qryqnPpVFcV3bjl809oiCAU6c4lWg4Vq1GGkpI4RnrxoocI6XCOvh/6zUM06DN+EWuHheBaq5WveE0f2qGTVszAqw+c7pSHAaUBWDUqZQZun7tyEdxTjkXkxVRk+N+eJP9lMSPxiMRNG+FP5PCjl500KM26CxrCNMdrs11HiZzDGXzRlJuUCZO7/yh3u7KLUo59le3zfIIVS2sESgXMH5cZoxfc3Jzh1srmU/BZzvtsyFPm3eOLt12ALzZ88TbeH4kjyTcWnkxSx/ys2why91In6K9IkrhL7JzNLUfgnI4uX06hBWINmDbSBVj3Y7f4BgFZvDQ=='''  # <<< REPLACE THIS with the b"""...""" printed by helper_make_block.py

def _decode_block(b64bytes):
    try:
        comp = base64.b64decode(b64bytes)
        text = zlib.decompress(comp).decode('utf-8')
        return json.loads(text)
    except Exception as e:
        messagebox.showerror("Error", "Mapping decode failed: " + str(e))
        raise

# Load hidden data
data = _decode_block(_ENC)
letter_to_number = data.get("letter_to_number", {})
number_to_letter = data.get("number_to_letter", {})
labels = data.get("labels", {})

# Combine both maps for encoding
secret_map = {}
secret_map.update(letter_to_number)
secret_map.update(number_to_letter)
reverse_map = {v: k for k, v in secret_map.items()}

# --- password helpers ---
def _hash(p: str) -> str:
    return hashlib.sha256(p.encode('utf-8')).hexdigest()

def _get_stored_hash():
    if os.path.exists(PASSWORD_FILE):
        with open(PASSWORD_FILE, 'r') as f:
            return f.read().strip()
    return None

def _set_password(pwd: str):
    with open(PASSWORD_FILE, 'w') as f:
        f.write(_hash(pwd))

# --- encode / decode ---
def encode_text(t: str) -> str:
    out = []
    for ch in t.upper():
        out.append(secret_map.get(ch, '?'))
    return ' '.join(out)

def decode_text(code: str) -> str:
    out = []
    for token in code.split():
        out.append(reverse_map.get(token, '?'))
    return ''.join(out)

def copy_to_clipboard_and_show(root, title, text):
    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
    except Exception:
        pass
    messagebox.showinfo(title, f"{text}\n\n(Automatically copied to clipboard)")

# --- change password flow ---
def change_password_flow():
    while True:
        cur = simpledialog.askstring(labels.get("chg_current","Enter current password:"), labels.get("chg_current","Enter current password:"), show='*')
        if cur is None:
            return
        if _hash(cur) != _get_stored_hash():
            messagebox.showerror(labels.get("err","Error"), labels.get("err_incorrect","Incorrect current password!"))
            continue
        newp = simpledialog.askstring(labels.get("chg_new","Enter new password:"), labels.get("chg_new","Enter new password:"), show='*')
        if not newp:
            messagebox.showerror(labels.get("err","Error"), labels.get("err_empty","Password cannot be empty!"))
            continue
        _set_password(newp)
        messagebox.showinfo(labels.get("succ","Success"), labels.get("succ_changed","Password changed successfully!"))
        return

# --- UI main ---
def main():
    root = tk.Tk()
    root.withdraw()

    if _get_stored_hash() is None:
        # first run: set password
        p = simpledialog.askstring(labels.get("set_title","Set Password"), labels.get("set_prompt","First run: set your password"), show='*')
        if not p:
            messagebox.showerror(labels.get("err","Error"), labels.get("err_empty","Password cannot be empty!"))
            return
        _set_password(p)
        messagebox.showinfo(labels.get("succ","Success"), labels.get("succ_set","Password set successfully!"))

    # login
    pin = simpledialog.askstring(labels.get("login_title","Password"), labels.get("login_prompt","Enter password:"), show='*')
    if pin is None or _hash(pin) != _get_stored_hash():
        messagebox.showerror(labels.get("err","Error"), labels.get("err_wrong","Wrong password!"))
        return

    messagebox.showinfo(labels.get("welcome_title","Welcome"), labels.get("welcome_msg","Access Granted"))

    while True:
        choice = simpledialog.askstring(labels.get("menu_title","Menu"),
            labels.get("menu_text","Choose an option:\n1. Encode Text\n2. Decode Code\n3. Change Password\n4. Exit"))
        if choice == "1":
            txt = simpledialog.askstring(labels.get("enc_title","Encode"), labels.get("enc_prompt","Enter text to encode:"))
            if txt is not None:
                result = encode_text(txt)
                copy_to_clipboard_and_show(root, labels.get("enc_result_title","Encoded"), result)
        elif choice == "2":
            c = simpledialog.askstring(labels.get("dec_title","Decode"), labels.get("dec_prompt","Enter code (space-separated):"))
            if c is not None:
                result = decode_text(c)
                copy_to_clipboard_and_show(root, labels.get("dec_result_title","Decoded"), result)
        elif choice == "3":
            change_password_flow()
        elif choice == "4" or choice is None:
            break
        else:
            messagebox.showwarning(labels.get("warn_title","Invalid"), labels.get("warn_text","Please choose 1, 2, 3, or 4."))

if __name__ == '__main__':
    main()
