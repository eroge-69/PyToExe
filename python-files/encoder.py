import tkinter as tk
from tkinter import filedialog, messagebox

def to_bitstring(data: bytes) -> str:
    return ''.join(f"{byte:08b}" for byte in data)

def from_bitstring(bits: str) -> bytes:
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))

def custom_encode(data: bytes) -> str:
    bits = to_bitstring(data)

    encoded = []
    last = bits[0]
    count = 1

    for b in bits[1:]:
        if b == last:
            count += 1
        else:
            encoded.append(f"{last}x{count}")  # value first, count second
            count = 1
            last = b
    encoded.append(f"{last}x{count}")  # final run
    return " ".join(encoded)

def custom_decode(encoded: str) -> bytes:
    parts = encoded.strip().split()
    bits = "".join(val * int(count) for part in parts for val, count in [part.split("x")])
    return from_bitstring(bits)

def encode_file():
    file_path = filedialog.askopenfilename(
        title="Select PNG file",
        filetypes=[("PNG Images", "*.png")]
    )
    if not file_path:
        return

    try:
        with open(file_path, "rb") as f:
            data = f.read()

        encoded = custom_encode(data)

        save_path = filedialog.asksaveasfilename(
            title="Save encoded file",
            defaultextension=".toast",
            filetypes=[("Toast files", "*.toast")]
        )
        if not save_path:
            return

        with open(save_path, "w") as f:
            f.write(encoded)

        messagebox.showinfo("Success", f"File encoded and saved as:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def decode_file():
    file_path = filedialog.askopenfilename(
        title="Select .toast file",
        filetypes=[("Toast files", "*.toast")]
    )
    if not file_path:
        return

    try:
        with open(file_path, "r") as f:
            encoded = f.read()

        decoded = custom_decode(encoded)

        save_path = filedialog.asksaveasfilename(
            title="Save decoded PNG",
            defaultextension=".png",
            filetypes=[("PNG Images", "*.png")]
        )
        if not save_path:
            return

        with open(save_path, "wb") as f:
            f.write(decoded)

        messagebox.showinfo("Success", f"File decoded and saved as:\n{save_path}")
    except Exception as e:
        messagebox.showerror("Error", str(e))


# GUI
root = tk.Tk()
root.title("Reversed Toast Encoder")
root.geometry("300x150")

label = tk.Label(root, text="Choose an option:", font=("Arial", 14))
label.pack(pady=10)

encode_btn = tk.Button(root, text="Encode PNG → TOAST", command=encode_file, width=20, height=2)
encode_btn.pack(pady=5)

decode_btn = tk.Button(root, text="Decode TOAST → PNG", command=decode_file, width=20, height=2)
decode_btn.pack(pady=5)

root.mainloop()
