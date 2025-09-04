import os, sys
import io
import traceback
import threading
from tkinter import *
from tkinter import ttk, filedialog, messagebox

try:
    from PIL import Image, ImageTk
except (ImportError, ModuleNotFoundError):
    os.system(f"{sys.executable} -m pip install pillow")
    from PIL import Image, ImageTk
try:

    import cv2
except (ImportError, ModuleNotFoundError):
    os.system(f"{sys.executable} -m pip install opencv-python")
    import cv2
try:
    import qrcode
except (ImportError, ModuleNotFoundError):
    os.system(f"{sys.executable} -m pip install qrcode[pil]")
    import qrcode

# ---------- Config ----------
ECC_MAP = {
    "L (7%)": qrcode.constants.ERROR_CORRECT_L,
    "M (15%)": qrcode.constants.ERROR_CORRECT_M,
    "Q (25%)": qrcode.constants.ERROR_CORRECT_Q,
    "H (30%)": qrcode.constants.ERROR_CORRECT_H,
}
DEFAULT_ECC = "M (15%)"

# ---------- Helpers ----------
def pil_to_png_bytes(pil_img):
    bio = io.BytesIO()
    pil_img.save(bio, format="PNG")
    return bio.getvalue()

def make_qr_image(text, ecc_label, box_size, border):
    if text is None: text = ""
    if not isinstance(text, str): text = str(text)
    ecc_val = ECC_MAP.get(ecc_label, ECC_MAP[DEFAULT_ECC])
    qr = qrcode.QRCode(
        version=None,
        error_correction=ecc_val,
        box_size=max(1, int(box_size)),
        border=max(1, int(border)),
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")

def decode_qr_from_path(path):
    if not path or not os.path.exists(path):
        return None
    img = cv2.imread(path)
    if img is None:
        return None
    detector = cv2.QRCodeDetector()
    data, points, _ = detector.detectAndDecode(img)
    return data if data else None

# ---------- GUI ----------
root = Tk()
root.title("Royal QR Generator , With Camera ")
root.geometry("900x500")

qr_png_bytes = None
cam_running = False
cap = None

# ---------- Layout ----------
# Left controls
frame_controls = Frame(root)
frame_controls.pack(side=LEFT, padx=10, pady=10, fill=Y)

Label(frame_controls, text="Text to encode:").pack(anchor=W)
text_input = Text(frame_controls, height=8, width=50)
text_input.pack()

# QR options
frame_opts = Frame(frame_controls)
frame_opts.pack(pady=5, fill=X)

Label(frame_opts, text="Error correction:").grid(row=0, column=0)
ecc_combo = ttk.Combobox(frame_opts, values=list(ECC_MAP.keys()), state="readonly")
ecc_combo.set(DEFAULT_ECC)
ecc_combo.grid(row=0, column=1, padx=5)

Label(frame_opts, text="Box size:").grid(row=0, column=2)
box_spin = Spinbox(frame_opts, from_=2, to=30, width=5)
box_spin.delete(0, END)
box_spin.insert(0, "8")
box_spin.grid(row=0, column=3, padx=5)

Label(frame_opts, text="Border:").grid(row=0, column=4)
border_spin = Spinbox(frame_opts, from_=1, to=10, width=5)
border_spin.delete(0, END)
border_spin.insert(0, "4")
border_spin.grid(row=0, column=5, padx=5)

# Buttons
frame_buttons = Frame(frame_controls)
frame_buttons.pack(pady=5, fill=X)

def generate_qr():
    global qr_png_bytes
    try:
        text = text_input.get("1.0", END).strip()
        if not text:
            messagebox.showwarning("No text", "Please enter some text to encode.")
            return
        ecc = ecc_combo.get()
        box = int(box_spin.get())
        border = int(border_spin.get())
        img = make_qr_image(text, ecc, box, border)
        qr_png_bytes = pil_to_png_bytes(img)
        img_preview = ImageTk.PhotoImage(img.resize((320,320)))
        img_label.configure(image=img_preview)
        img_label.image = img_preview
        save_btn.config(state=NORMAL)
        decoded_text.delete("1.0", END)
        decoded_text.insert(END, text)
    except Exception:
        messagebox.showerror("Error", traceback.format_exc())

def save_qr():
    if not qr_png_bytes:
        messagebox.showinfo("Nothing to save", "Generate a QR first.")
        return
    path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image","*.png")])
    if path:
        try:
            with open(path, "wb") as f:
                f.write(qr_png_bytes)
            messagebox.showinfo("Saved", f"Saved:\n{path}")
        except Exception:
            messagebox.showerror("Error", traceback.format_exc())

def clear_all():
    text_input.delete("1.0", END)
    decoded_text.delete("1.0", END)
    img_label.configure(image="")
    save_btn.config(state=DISABLED)

def open_qr_image():
    path = filedialog.askopenfilename(filetypes=[("Images",".png;.jpg;.jpeg;.bmp;*.webp")])
    if path:
        decoded = decode_qr_from_path(path)
        if decoded:
            decoded_text.delete("1.0", END)
            decoded_text.insert(END, decoded)
            text_input.delete("1.0", END)
            text_input.insert(END, decoded)
        else:
            messagebox.showinfo("Decode", "No QR detected.")
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((512,512))
            img_preview = ImageTk.PhotoImage(img)
            img_label.configure(image=img_preview)
            img_label.image = img_preview
            save_btn.config(state=DISABLED)
        except:
            pass

def copy_decoded():
    text = decoded_text.get("1.0", END).strip()
    if not text:
        messagebox.showinfo("Nothing to copy", "Nothing to copy.")
        return
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copied", "Copied to clipboard.")

gen_btn = Button(frame_buttons, text="Generate QR", command=generate_qr)
gen_btn.pack(side=LEFT, padx=2)
save_btn = Button(frame_buttons, text="Save QR…", command=save_qr, state=DISABLED)
save_btn.pack(side=LEFT, padx=2)
clear_btn = Button(frame_buttons, text="Clear", command=clear_all)
clear_btn.pack(side=LEFT, padx=2)
open_btn = Button(frame_buttons, text="Open QR Image…", command=open_qr_image)
open_btn.pack(side=LEFT, padx=2)
copy_btn = Button(frame_buttons, text="Copy Decoded", command=copy_decoded)
copy_btn.pack(side=LEFT, padx=2)

Label(frame_controls, text="Decoded / Current text:").pack(anchor=W, pady=(5,0))
decoded_text = Text(frame_controls, height=6, width=50)
decoded_text.pack()

# Right: QR Preview
frame_preview = Frame(root)
frame_preview.pack(side=RIGHT, padx=10, pady=10, fill=BOTH, expand=True)
Label(frame_preview, text="QR Preview:").pack()
img_label = Label(frame_preview, bg="white", width=320, height=320)
img_label.pack(pady=5)

# ---------- Camera QR ----------
def camera_window():
    cam_win = Toplevel(root)
    cam_win.title("Camera QR Decoder")

    cam_img_label = Label(cam_win)
    cam_img_label.pack()

    cam_decoded_var = StringVar()
    Label(cam_win, text="Decoded:").pack()
    cam_decoded_entry = Entry(cam_win, textvariable=cam_decoded_var, width=50)
    cam_decoded_entry.pack()

    cam_index_var = StringVar(value="0")
    Label(cam_win, text="Camera index:").pack()
    cam_index_entry = Entry(cam_win, textvariable=cam_index_var, width=6)
    cam_index_entry.pack()
    
    def start_camera():
        global cam_running, cap
        index = int(cam_index_var.get() or "0")
        cap = cv2.VideoCapture(index)
        if not cap.isOpened():
            messagebox.showerror("Error", "Unable to open camera. Try index 0,1,2…")
            return
        cam_running = True
        threading.Thread(target=cam_loop, daemon=True).start()
    
    def cam_loop():
        global cam_running, cap
        detector = cv2.QRCodeDetector()
        while cam_running and cap:
            ret, frame = cap.read()
            if not ret:
                continue
            data, points, _ = detector.detectAndDecode(frame)
            if data:
                cam_decoded_var.set(data)
                decoded_text.delete("1.0", END)
                decoded_text.insert(END, data)
                text_input.delete("1.0", END)
                text_input.insert(END, data)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(frame_rgb)
            img_pil.thumbnail((800, 600))
            img_preview = ImageTk.PhotoImage(img_pil)
            cam_img_label.configure(image=img_preview)
            cam_img_label.image = img_preview

    def stop_camera():
        global cam_running, cap
        cam_running = False
        if cap:
            cap.release()
            cap = None
        cam_win.destroy()

    Button(cam_win, text="Start", command=start_camera).pack(side=LEFT, padx=5)
    Button(cam_win, text="Close", command=stop_camera).pack(side=LEFT, padx=5)
    Button(cam_win, text="Copy", command=lambda: root.clipboard_append(cam_decoded_var.get())).pack(side=LEFT, padx=5)

cam_btn = Button(frame_controls, text="Decode from Camera", command=camera_window)
cam_btn.pack(pady=5)

root.mainloop()