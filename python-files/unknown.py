import secrets
import string
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import itertools
from PIL import Image, ImageTk 


ascii_chars = string.ascii_letters + string.digits + string.punctuation
hindi_chars = ''.join([chr(i) for i in range(0x0900, 0x097F + 1)])
tamil_chars = ''.join([chr(i) for i in range(0x0B80, 0x0BFF + 1)])
all_chars = ascii_chars + hindi_chars + tamil_chars


current_reverse_map = None
current_key_filename = None


def generate_random_32char_key(chars_to_map):
    key_map = {}
    reverse_map = {}
    for char in chars_to_map:
        token = ''.join(secrets.choice(all_chars) for _ in range(32))
        while token in key_map.values():
            token = ''.join(secrets.choice(all_chars) for _ in range(32))
        key_map[char] = token
        reverse_map[token] = char
    return key_map, reverse_map

def encrypt(message, key_map):
    encrypted_parts = []
    for c in message:
        token = key_map.get(c, '?')
        encrypted_parts.append(f"{len(token):03d}{token}")  
    return ''.join(encrypted_parts)

def decrypt(ciphertext, reverse_map):
    decrypted_list = []
    i = 0
    while i < len(ciphertext):
        if i + 3 > len(ciphertext):
            decrypted_list.append('?')
            break
        token_len_str = ciphertext[i:i + 3]
        try:
            token_len = int(token_len_str)
        except ValueError:
            decrypted_list.append('?')
            break
        i += 3
        token = ciphertext[i:i + token_len]
        i += token_len
        decrypted_list.append(reverse_map.get(token, '?'))
    return ''.join(decrypted_list)

def save_key_to_file_plaintext(key_map, charset_name="ASCII+DEVA+TAMIL"):
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"key_{date_str}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"DATE={date_str}\n")
        f.write(f"CHARSET={charset_name}\n")
        for char, token in key_map.items():
            f.write(f"{char}={token}\n")
    return filename

def load_key_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        first = f.readline().strip()
        second = f.readline().strip()
        key_map = {}
        if first.startswith("DATE=") and second.startswith("CHARSET="):
            for line in f:
                if '=' in line:
                    char, token = line.strip().split('=', 1)
                    key_map[char] = token
                else: 
                    print(f"Skipping malformed line in key file: {line.strip()}")
        else:
            f.seek(0)
            for line in f:
                if '=' in line:
                    char, token = line.strip().split('=', 1)
                    key_map[char] = token
                else:
                    print(f"Skipping malformed line in key file: {line.strip()}")
    reverse_map = {v: k for k, v in key_map.items()}
    return key_map, reverse_map



def thread_safe_update(widget, text):
    widget.config(state=tk.NORMAL)
    widget.delete("1.0", tk.END)
    widget.insert(tk.END, text)
    widget.config(state=tk.DISABLED)

def thread_safe_label_update(label, text):
    label.config(text=text)

def flash_label(label, times=3, interval=200):
    def task(count=0):
        if count >= times * 2:
            label.config(fg="#ffdd57")  
            return
        label.config(fg="#ffffff" if count % 2 == 0 else "#ffdd57")
        root.after(interval, task, count + 1)
    task()


def encrypt_action():
    def task():
        message = encrypt_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Enter a message to encrypt!")
            return
        key_map, _ = generate_random_32char_key(all_chars)
        encrypted_message = encrypt(message, key_map) 
        root.after(0, thread_safe_update, encrypt_result_text, encrypted_message)
        key_file = save_key_to_file_plaintext(key_map, "ASCII+DEVA+TAMIL")
        root.after(0, thread_safe_label_update, decrypt_key_label, f"Loaded Key File: {key_file}")
        flash_label(decrypt_key_label)
        _, rev = load_key_from_file(key_file)
        global current_reverse_map, current_key_filename
        current_reverse_map = rev
        current_key_filename = key_file
        messagebox.showinfo("Key Saved", f"Key saved to file: {key_file}")
    threading.Thread(target=task).start()

def copy_encrypted_message():
    encrypted_message = encrypt_result_text.get("1.0", tk.END).strip()
    if encrypted_message:
        root.clipboard_clear()
        root.clipboard_append(encrypted_message)
        messagebox.showinfo("Copied", "Encrypted message copied!")
    else:
        messagebox.showwarning("Warning", "No encrypted message to copy!")

def load_key_file_dialog():
    filename = filedialog.askopenfilename(title="Select Key File", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
    if not filename:
        return
    try:
        _, rev = load_key_from_file(filename)
        global current_reverse_map, current_key_filename
        current_reverse_map = rev
        current_key_filename = filename
        thread_safe_label_update(decrypt_key_label, f"Loaded Key File: {filename}")
        flash_label(decrypt_key_label)
        messagebox.showinfo("Key Loaded", f"Key file loaded: {filename}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load key file.\n{e}")

def decrypt_action():
    def task():
        encrypted_message = decrypt_text.get("1.0", tk.END).strip()
        if not encrypted_message:
            messagebox.showwarning("Warning", "Paste encrypted message!")
            return
        global current_reverse_map, current_key_filename
        if current_reverse_map is None:
            filename = filedialog.askopenfilename(title="Select Key File (required)", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
            if not filename:
                messagebox.showwarning("Warning", "You must select a key file to decrypt.")
                return
            try:
                _, rev = load_key_from_file(filename)
                current_reverse_map = rev
                current_key_filename = filename
                root.after(0, thread_safe_label_update, decrypt_key_label, f"Loaded Key File: {filename}")
                flash_label(decrypt_key_label)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load key file.\n{e}")
                return
        try:
            decrypted_message = decrypt(encrypted_message, current_reverse_map)  
            root.after(0, thread_safe_update, decrypt_result_text, decrypted_message)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to decrypt message.\n{e}")
    threading.Thread(target=task).start()

root = tk.Tk()
root.title("ZENVORK - Quantum Proof Encryptor")
root.geometry("1000x700")
root.configure(bg="#1e1e1e")

frame_bg = "#2a2a2a"
text_bg = "#1f1f1f"
text_fg = "#ffffff"
button_bg = "#4b6cf7"
button_fg = "#ffffff"


header = tk.Frame(root, bg="#121212", height=100) 
header.pack(fill="x")

try:
    
    logo_image = Image.open("SmartSelect_20250924_225911_Google.jpg")
    logo_image = logo_image.resize((150, 70), Image.Resampling.LANCZOS) 
    zenvork_logo = ImageTk.PhotoImage(logo_image)

    logo_label = tk.Label(header, image=zenvork_logo, bg="#121212")
    logo_label.image = zenvork_logo 
    logo_label.pack(side="left", padx=20, pady=5)

    
    tk.Label(header, text="Secure Quantum Message Encryption", fg="#cccccc", bg="#121212", font=("Consolas", 10)).pack(side="left", padx=10, pady=5)

except FileNotFoundError:
    print("Logo file 'zenvork_logo.png' not found. Displaying text header instead.")
    
    header_label = tk.Label(header, text="ZENVORK", fg="#4b6cf7", bg="#121212", font=("Consolas", 18, "bold"))
    header_label.pack(side="left", padx=20)
    tk.Label(header, text="Secure Quantum Message Encryption", fg="#cccccc", bg="#121212", font=("Consolas", 10)).pack(side="left", padx=10)
   
    def shimmer_header():
        colors = itertools.cycle(["#4b6cf7", "#6e82f7", "#4b6cf7"])
        def update():
            if 'header_label' in globals(): 
                header_label.config(fg=next(colors))
            root.after(500, update)
        update()
    shimmer_header()
except Exception as e:
    print(f"An error occurred while loading the logo: {e}")
   
    header_label = tk.Label(header, text="ZENVORK", fg="#4b6cf7", bg="#121212", font=("Consolas", 18, "bold"))
    header_label.pack(side="left", padx=20)
    tk.Label(header, text="Secure Quantum Message Encryption", fg="#cccccc", bg="#121212", font=("Consolas", 10)).pack(side="left", padx=10)
    def shimmer_header():
        colors = itertools.cycle(["#4b6cf7", "#6e82f7", "#4b6cf7"])
        def update():
            if 'header_label' in globals():
                header_label.config(fg=next(colors))
            root.after(500, update)
        update()
    shimmer_header()


main_frame = tk.Frame(root, bg=frame_bg)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

encrypt_frame = tk.LabelFrame(main_frame, text="Encrypt Message", bg=frame_bg, fg="#ffffff", font=("Consolas", 12, "bold"), padx=10, pady=10)
encrypt_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

tk.Label(encrypt_frame, text="Enter your message:", bg=frame_bg, fg=text_fg).pack(anchor="w")
encrypt_text = scrolledtext.ScrolledText(encrypt_frame, height=10, bg=text_bg, fg=text_fg, insertbackground="#ffffff")
encrypt_text.pack(fill="both", padx=5, pady=5)

btn_frame = tk.Frame(encrypt_frame, bg=frame_bg)
btn_frame.pack(pady=5)
btn_encrypt = tk.Button(btn_frame, text="Encrypt & Save Key", bg=button_bg, fg=button_fg, command=encrypt_action)
btn_encrypt.pack(side="left", padx=5)
btn_copy = tk.Button(btn_frame, text="Copy Encrypted Message", bg=button_bg, fg=button_fg, command=copy_encrypted_message)
btn_copy.pack(side="left", padx=5)

tk.Label(encrypt_frame, text="Encrypted Message:", bg=frame_bg, fg=text_fg).pack(anchor="w")
encrypt_result_text = scrolledtext.ScrolledText(encrypt_frame, height=10, bg=text_bg, fg="#ffdd57", insertbackground="#ffffff", state=tk.DISABLED)
encrypt_result_text.pack(fill="both", padx=5, pady=5)

decrypt_frame = tk.LabelFrame(main_frame, text="Decrypt Message", bg=frame_bg, fg="#ffffff", font=("Consolas", 12, "bold"), padx=10, pady=10)
decrypt_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

tk.Label(decrypt_frame, text="Paste encrypted message:", bg=frame_bg, fg=text_fg).pack(anchor="w")
decrypt_text = scrolledtext.ScrolledText(decrypt_frame, height=10, bg=text_bg, fg=text_fg, insertbackground="#ffffff")
decrypt_text.pack(fill="both", padx=5, pady=5)

btn_frame_decrypt = tk.Frame(decrypt_frame, bg=frame_bg)
btn_frame_decrypt.pack(pady=5)
btn_decrypt = tk.Button(btn_frame_decrypt, text="Decrypt Message", bg=button_bg, fg=button_fg, command=decrypt_action)
btn_decrypt.pack(side="left", padx=5)
#btn_load_key = tk.Button(btn_frame_decrypt, text="Load Key File", bg="#ff5757", fg=btton_fg, command=load_key_file_dialog)
#btn_load_key.pack(side="left", padx=5)

decrypt_key_label = tk.Label(decrypt_frame, text="No key file loaded.", bg=frame_bg, fg="#ffdd57", font=("Consolas", 10))
decrypt_key_label.pack(anchor="w", pady=(5, 0))

tk.Label(decrypt_frame, text="Decrypted Message:", bg=frame_bg, fg=text_fg).pack(anchor="w")
decrypt_result_text = scrolledtext.ScrolledText(decrypt_frame, height=10, bg=text_bg, fg="#ffdd57", insertbackground="#ffffff", state=tk.DISABLED)
decrypt_result_text.pack(fill="both", padx=5, pady=5)

status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W, bg="#2a2a2a", fg="#cccccc")
status_bar.pack(side=tk.BOTTOM, fill=tk.X)

root.mainloop()
