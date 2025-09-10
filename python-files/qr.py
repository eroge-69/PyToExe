import os
import csv
import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox, ttk
from PIL import Image, ImageTk
from barcode import EAN13, Code128, Code39, ITF, UPC, gs1, DataMatrix
from barcode.writer import ImageWriter
import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H

# ===== Helper Functions =====
def choose_color(var):
    color_code = colorchooser.askcolor(title="Choose Color")
    if color_code[1]:
        var.set(color_code[1])

def choose_folder(var):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        var.set(folder_selected)

def choose_logo(var, preview_label):
    file_selected = filedialog.askopenfilename(filetypes=[("Image files","*.png;*.jpg;*.jpeg;*.bmp")])
    if file_selected:
        var.set(file_selected)
        img = Image.open(file_selected)
        img.thumbnail((100,100))
        img_tk = ImageTk.PhotoImage(img)
        preview_label.config(image=img_tk)
        preview_label.image = img_tk

def cm_to_rgb(cmyk):
    # Simple CMYK to RGB approximation
    c, m, y, k = [float(x)/100 for x in cmyk]
    r = 255 * (1-c)*(1-k)
    g = 255 * (1-m)*(1-k)
    b = 255 * (1-y)*(1-k)
    return int(r), int(g), int(b)

def generate_barcode(code_number, code_type, fg_color, output_folder, out_format, logo_path):
    if not code_number:
        return

    barcode_class = None
    if code_type == "EAN13":
        if len(code_number)!=12 or not code_number.isdigit(): return
        barcode_class = EAN13
    elif code_type=="CODE128":
        barcode_class = Code128
    elif code_type=="CODE39":
        barcode_class = Code39
    elif code_type=="ITF-14":
        barcode_class = ITF
    elif code_type=="UPC-A":
        barcode_class = UPC
    elif code_type=="GS1-128":
        barcode_class = gs1.GS1_128
    elif code_type=="DataMatrix":
        barcode_class = DataMatrix
    else:
        return

    if not output_folder:
        output_folder = "barcodes"
        os.makedirs(output_folder, exist_ok=True)

    barcode = barcode_class(code_number, writer=ImageWriter())
    filename = os.path.join(output_folder, code_number)
    options = {"foreground": fg_color}
    barcode.save(filename, options)

    # Logo overlay
    if logo_path:
        try:
            img = Image.open(f"{filename}.png")
            logo_img = Image.open(logo_path)
            logo_img.thumbnail((img.width//4,img.height//4))
            x = (img.width - logo_img.width)//2
            y = (img.height - logo_img.height)//2
            img.paste(logo_img,(x,y), logo_img if logo_img.mode=='RGBA' else None)
            img.save(f"{filename}.png")
        except:
            pass

    if out_format.lower()=="pdf":
        if not filename.endswith(".pdf"):
            os.rename(f"{filename}.png", f"{filename}.pdf")

def generate_qr(code_number, fg_color, bg_color, error_level, logo_path, output_folder, out_format):
    if not code_number: return

    ec_dict = {"L": ERROR_CORRECT_L, "M": ERROR_CORRECT_M, "Q": ERROR_CORRECT_Q, "H": ERROR_CORRECT_H}
    qr = qrcode.QRCode(
        version=1,
        error_correction=ec_dict.get(error_level,"M"),
        box_size=10,
        border=4,
    )
    qr.add_data(code_number)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fg_color, back_color=bg_color).convert("RGB")

    # Logo overlay
    if logo_path:
        try:
            logo_img = Image.open(logo_path)
            logo_img.thumbnail((img.width//4, img.height//4))
            x = (img.width - logo_img.width)//2
            y = (img.height - logo_img.height)//2
            img.paste(logo_img,(x,y), logo_img if logo_img.mode=='RGBA' else None)
        except:
            pass

    if not output_folder:
        output_folder = "barcodes"
        os.makedirs(output_folder, exist_ok=True)

    filename = os.path.join(output_folder, code_number)
    if out_format.lower()=="pdf":
        img.save(f"{filename}.pdf")
    else:
        img.save(f"{filename}.png")

# ===== GUI Functions =====
def generate_single_barcode_gui():
    generate_barcode(
        entry_number.get(),
        type_var.get(),
        color_var.get(),
        folder_var.get(),
        format_var.get(),
        logo_var.get()
    )
    messagebox.showinfo("Success","✅ Barcode generated!")

def generate_single_qr_gui():
    generate_qr(
        entry_qr.get(),
        fg_color_var.get(),
        bg_color_var.get(),
        error_var.get(),
        logo_qr_var.get(),
        folder_var.get(),
        format_var.get()
    )
    messagebox.showinfo("Success","✅ QR Code generated!")

def generate_batch_gui():
    csv_file = filedialog.askopenfilename(filetypes=[("CSV files","*.csv")])
    if not csv_file: return
    with open(csv_file,newline='',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = row.get("Code") or row.get("code")
            btype = row.get("Type") or type_var.get()
            if btype.lower() in ["qr","qrcode"]:
                generate_qr(code, fg_color_var.get(), bg_color_var.get(), error_var.get(), logo_qr_var.get(), folder_var.get(), format_var.get())
            else:
                generate_barcode(code, btype, color_var.get(), folder_var.get(), format_var.get(), logo_var.get())
    messagebox.showinfo("Batch Done","✅ Batch processing completed!")

# ===== GUI =====
root = tk.Tk()
root.title("Pro+ QR Monkey Style Barcode & QR Generator")
root.geometry("700x750")
root.resizable(False,False)

tabs = ttk.Notebook(root)
tab_barcode = ttk.Frame(tabs)
tab_qr = ttk.Frame(tabs)
tab_batch = ttk.Frame(tabs)
tabs.add(tab_barcode,text="Single Barcode")
tabs.add(tab_qr,text="Single QR Code")
tabs.add(tab_batch,text="Batch CSV")
tabs.pack(expand=1,fill="both")

# ---- Barcode Tab ----
tk.Label(tab_barcode,text="Enter Barcode Number/Text:").pack(anchor="w", padx=10,pady=5)
entry_number = tk.Entry(tab_barcode,width=40)
entry_number.pack(padx=10,pady=5)

tk.Label(tab_barcode,text="Select Barcode Type:").pack(anchor="w", padx=10)
type_var = tk.StringVar(value="CODE128")
tk.OptionMenu(tab_barcode,type_var,"EAN13","CODE128","CODE39","ITF-14","UPC-A","GS1-128","DataMatrix").pack(padx=10,pady=5)

tk.Label(tab_barcode,text="Barcode Color:").pack(anchor="w", padx=10)
color_var = tk.StringVar(value="#000000")
tk.Button(tab_barcode,text="Choose Color",command=lambda: choose_color(color_var),bg="#2196F3",fg="white").pack(padx=10,pady=5)

tk.Label(tab_barcode,text="Output Folder:").pack(anchor="w", padx=10)
folder_var = tk.StringVar()
tk.Button(tab_barcode,text="Choose Folder",command=lambda: choose_folder(folder_var),bg="#FF9800",fg="white").pack(padx=10,pady=5)

tk.Label(tab_barcode,text="Optional Logo:").pack(anchor="w", padx=10)
logo_var = tk.StringVar()
tk.Button(tab_barcode,text="Choose Logo",command=lambda: choose_logo(logo_var,tk.Label(tab_barcode)),bg="#9C27B0",fg="white").pack(padx=10,pady=5)

tk.Label(tab_barcode,text="Output Format:").pack(anchor="w", padx=10)
format_var = tk.StringVar(value="PNG")
tk.OptionMenu(tab_barcode,format_var,"PNG","PDF","SVG","EPS").pack(padx=10,pady=5)

tk.Button(tab_barcode,text="Generate Barcode",command=generate_single_barcode_gui,bg="#4CAF50",fg="white",width=30).pack(pady=20)

# ---- QR Tab ----
tk.Label(tab_qr,text="Enter QR Code Data:").pack(anchor="w", padx=10,pady=5)
entry_qr = tk.Entry(tab_qr,width=40)
entry_qr.pack(padx=10,pady=5)

tk.Label(tab_qr,text="Foreground Color:").pack(anchor="w", padx=10)
fg_color_var = tk.StringVar(value="#000000")
tk.Button(tab_qr,text="Choose Color",command=lambda: choose_color(fg_color_var),bg="#2196F3",fg="white").pack(padx=10,pady=5)

tk.Label(tab_qr,text="Background Color:").pack(anchor="w", padx=10)
bg_color_var = tk.StringVar(value="#FFFFFF")
tk.Button(tab_qr,text="Choose Color",command=lambda: choose_color(bg_color_var),bg="#9C27B0",fg="white").pack(padx=10,pady=5)

tk.Label(tab_qr,text="Error Correction Level:").pack(anchor="w", padx=10)
error_var = tk.StringVar(value="M")
tk.OptionMenu(tab_qr,error_var,"L","M","Q","H").pack(padx=10,pady=5)

tk.Label(tab_qr,text="Optional Logo:").pack(anchor="w", padx=10)
logo_qr_var = tk.StringVar()
logo_preview = tk.Label(tab_qr)
logo_preview.pack(padx=10,pady=5)
tk.Button(tab_qr,text="Choose Logo",command=lambda: choose_logo(logo_qr_var,logo_preview),bg="#9C27B0",fg="white").pack(padx=10,pady=5)

tk.Label(tab_qr,text="Output Format:").pack(anchor="w", padx=10)
tk.OptionMenu(tab_qr,format_var,"PNG","PDF","SVG","EPS").pack(padx=10,pady=5)

tk.Button(tab_qr,text="Generate QR Code",command=generate_single_qr_gui,bg="#4CAF50",fg="white",width=30).pack(pady=20)

# ---- Batch Tab ----
tk.Label(tab_batch,text="CSV must contain 'Code' and optional 'Type' (Barcode or QR)").pack(anchor="w", padx=10,pady=5)
tk.Button(tab_batch,text="Select CSV & Generate Batch",command=generate_batch_gui,bg="#FF5722",fg="white",width=30).pack(pady=30)

root.mainloop()
