import qrcode
import tkinter as tk
from tkinter import simpledialog, messagebox
import json

def generate_qr():
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    try:
        # Get user input
        box_id = simpledialog.askstring("Box ID", "Enter Box ID (e.g. BOX-001):")
        prefix = simpledialog.askstring("Prefix", "Enter serial prefix (e.g. SN):")
        start = simpledialog.askinteger("Start", "Starting number (e.g. 1):")
        end = simpledialog.askinteger("End", "Ending number (e.g. 10):")
        
        if None in [box_id, prefix, start, end]:
            return
            
        # Generate serials
        serials = [f"{prefix}{num}" for num in range(start, end+1)]
        
        # Create QR data
        data = {
            "box_id": box_id,
            "serials": serials,
            "count": len(serials)
        }
        
        # Generate QR
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(json.dumps(data))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save file
        filename = f"{box_id}_{prefix}{start}-{prefix}{end}.png"
        img.save(filename)
        messagebox.showinfo("Success", f"QR saved as:\n{filename}")
        
    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    generate_qr()