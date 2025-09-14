import os
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
from PIL import Image, ImageDraw, ImageTk
import qrcode
from qrcode.constants import ERROR_CORRECT_H

# ---------- QR Generation ----------
def generate_qr_custom(data, fg_color="black", bg_color="white", box_size=10,
                       dot_shape="square", eye_frame_shape="square",
                       eye_ball_shape="square", logo_path=None):
    qr = qrcode.QRCode(
        version=1,
        error_correction=ERROR_CORRECT_H,
        box_size=box_size,
        border=4
    )
    qr.add_data(data)
    qr.make(fit=True)
    matrix = qr.get_matrix()
    size = len(matrix) * box_size
    img = Image.new("RGB", (size, size), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw modules
    for y,row in enumerate(matrix):
        for x,cell in enumerate(row):
            if cell:
                top_left = (x*box_size, y*box_size)
                bottom_right = ((x+1)*box_size, (y+1)*box_size)
                if dot_shape=="circle":
                    draw.ellipse([top_left, bottom_right], fill=fg_color)
                elif dot_shape=="rounded":
                    radius = box_size//2
                    draw.rounded_rectangle([top_left, bottom_right], radius=radius, fill=fg_color)
                else:
                    draw.rectangle([top_left, bottom_right], fill=fg_color)

    # Add Logo
    if logo_path and os.path.exists(logo_path):
        try:
            logo = Image.open(logo_path)
            max_logo_size = size//4
            logo.thumbnail((max_logo_size,max_logo_size))
            x = (size - logo.width)//2
            y = (size - logo.height)//2
            img.paste(logo,(x,y), logo if logo.mode=="RGBA" else None)
        except:
            pass

    return img

# ---------- GUI ----------
class QRMonkeyApp:
    def __init__(self, root):
        self.root=root
        self.root.title("QR Monkey Style QR Generator")
        self.root.geometry("950x650")

        # Left Panel
        self.left = tk.Frame(root)
        self.left.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        # Right Panel (Preview)
        self.right = tk.Frame(root)
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # QR Data
        tk.Label(self.left,text="Enter QR Data / URL:").pack(pady=5)
        self.entry_data = tk.Entry(self.left,width=40)
        self.entry_data.pack(pady=5)
        self.entry_data.bind("<KeyRelease>", lambda e: self.update_preview())

        # QR Color
        tk.Label(self.left,text="QR Color (Default Black)").pack(pady=5)
        self.fg_color="black"
        tk.Button(self.left,text="Pick QR Color",command=self.pick_fg_color).pack(pady=5)

        # Background
        tk.Label(self.left,text="Background:").pack(pady=5)
        self.bg_var=tk.StringVar(value="white")
        tk.Radiobutton(self.left,text="White",variable=self.bg_var,value="white",command=self.update_preview).pack()
        tk.Radiobutton(self.left,text="Transparent",variable=self.bg_var,value="transparent",command=self.update_preview).pack()

        # Module Size
        tk.Label(self.left,text="Module Size:").pack(pady=5)
        self.box_size_var=tk.IntVar(value=10)
        tk.Spinbox(self.left,from_=1,to=50,textvariable=self.box_size_var,command=self.update_preview).pack(pady=5)

        # Logo
        tk.Label(self.left,text="Optional Logo:").pack(pady=5)
        self.logo_path=""
        tk.Button(self.left,text="Select Logo",command=self.select_logo).pack(pady=5)

        # Dot Shape
        tk.Label(self.left,text="Dot Shape:").pack(pady=5)
        self.dot_shape_var = tk.StringVar(value="square")
        ttk.Combobox(self.left,textvariable=self.dot_shape_var,values=["square","circle","rounded"]).pack(pady=5)
        self.dot_shape_var.trace("w", lambda *args: self.update_preview())

        # Eye Frame Shape
        tk.Label(self.left,text="Eye Frame Shape:").pack(pady=5)
        self.eye_frame_var=tk.StringVar(value="square")
        ttk.Combobox(self.left,textvariable=self.eye_frame_var,values=["square","circle","rounded"]).pack(pady=5)
        self.eye_frame_var.trace("w", lambda *args: self.update_preview())

        # Eye Ball Shape
        tk.Label(self.left,text="Eye Ball Shape:").pack(pady=5)
        self.eye_ball_var=tk.StringVar(value="square")
        ttk.Combobox(self.left,textvariable=self.eye_ball_var,values=["square","circle","rounded"]).pack(pady=5)
        self.eye_ball_var.trace("w", lambda *args: self.update_preview())

        # Output Folder
        tk.Label(self.left,text="Select Save Folder:").pack(pady=5)
        self.save_folder=""
        tk.Button(self.left,text="Choose Folder",command=self.select_folder).pack(pady=5)

        # Output Format
        tk.Label(self.left,text="Output Format:").pack(pady=5)
        self.format_var = ttk.Combobox(self.left,values=["PNG","PDF","EPS","SVG"])
        self.format_var.current(0)
        self.format_var.pack(pady=5)

        # Generate Button
        tk.Button(self.left,text="Generate QR Code",bg="#4CAF50",fg="white",command=self.generate_qr,width=25,height=2).pack(pady=20)

        # Live Preview
        tk.Label(self.right,text="Live Preview:").pack(pady=5)
        self.preview_label=tk.Label(self.right)
        self.preview_label.pack(pady=10)

        self.update_preview()

    # ---------- Selection ----------
    def pick_fg_color(self):
        color = colorchooser.askcolor(title="Pick QR Color")
        if color[1]: self.fg_color=color; self.update_preview()

    def select_logo(self):
        path=filedialog.askopenfilename(filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.bmp")])
        if path:self.logo_path=path; self.update_preview()

    def select_folder(self):
        folder=filedialog.askdirectory()
        if folder:self.save_folder=folder

    # ---------- Update Preview ----------
    def update_preview(self):
        data=self.entry_data.get() or "Preview"
        bg="white" if self.bg_var.get()=="white" else None
        img=generate_qr_custom(
            data=data,
            fg_color=self.fg_color,
            bg_color=bg or "white",
            box_size=self.box_size_var.get(),
            dot_shape=self.dot_shape_var.get(),
            eye_frame_shape=self.eye_frame_var.get(),
            eye_ball_shape=self.eye_ball_var.get(),
            logo_path=self.logo_path
        )
        img.thumbnail((300,300))
        self.img_tk=ImageTk.PhotoImage(img)
        self.preview_label.config(image=self.img_tk)

    # ---------- Generate QR ----------
    def generate_qr(self):
        data=self.entry_data.get()
        if not data: messagebox.showerror("Error","Please enter QR data"); return
        if not self.save_folder: messagebox.showerror("Error","Select save folder"); return
        fg=self.fg_color
        bg="white" if self.bg_var.get()=="white" else None
        out_format=self.format_var.get()
        img=generate_qr_custom(
            data=data,
            fg_color=fg,
            bg_color=bg or "white",
            box_size=self.box_size_var.get(),
            dot_shape=self.dot_shape_var.get(),
            eye_frame_shape=self.eye_frame_var.get(),
            eye_ball_shape=self.eye_ball_var.get(),
            logo_path=self.logo_path
        )
        # File name
        filename=data.replace(" ","_").replace("/","_").replace("\\","_")
        os.makedirs(self.save_folder,exist_ok=True)
        save_path=os.path.join(self.save_folder,f"{filename}.{out_format.lower()}")
        img.save(save_path)
        messagebox.showinfo("Success",f"QR Code saved as:\n{save_path}")
        self.update_preview()

# ---------- Main ----------
if __name__=="__main__":
    root=tk.Tk()
    app=QRMonkeyApp(root)
    root.mainloop()
