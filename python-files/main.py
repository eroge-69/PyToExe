import qrcode
from PIL import Image
import json
import argparse
import customtkinter as ctk
from tkinter import filedialog, messagebox
import cv2
import os
import sys

def encode_json_to_qr(json_file, output_file):
    """Encode JSON file to QR code image"""
    try:
        # Check if input file exists
        if not os.path.exists(json_file):
            print(f"Error: JSON file '{json_file}' not found.")
            return False
            
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in file '{json_file}': {e}")
        return False
    except Exception as e:
        print(f"Error reading JSON file '{json_file}': {e}")
        return False
    
    try:
        # Create QR code with better error correction
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(data, ensure_ascii=False))
        qr.make(fit=True)
        
        # Create QR code image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        qr_img.save(output_file)
        print(f"QR Code successfully saved as '{output_file}'")
        return True
    except Exception as e:
        print(f"Error creating QR code: {e}")
        return False

def decode_qr_to_json(image_file, output_file=None):
    """Decode QR code image back to JSON"""
    try:
        # Check if input file exists
        if not os.path.exists(image_file):
            print(f"Error: Image file '{image_file}' not found.")
            return False
            
        detector = cv2.QRCodeDetector()
        img = cv2.imread(image_file)
        
        if img is None:
            print(f"Error: Unable to read image file '{image_file}'. Check if it's a valid image format.")
            return False
            
        data, _, _ = detector.detectAndDecode(img)
        
        if not data:
            print("No QR code detected in the image or QR code is empty.")
            return False
            
        try:
            json_data = json.loads(data)
            pretty_json = json.dumps(json_data, indent=4, ensure_ascii=False)
        except json.JSONDecodeError as e:
            print(f"Error: QR code contains invalid JSON data: {e}")
            return False
        
        if output_file:
            try:
                # Ensure output directory exists
                output_dir = os.path.dirname(output_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                    
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(pretty_json)
                print(f"JSON successfully saved to '{output_file}'")
            except Exception as e:
                print(f"Error writing JSON file '{output_file}': {e}")
                return False
        else:
            print("Decoded JSON:")
            print(pretty_json)
            
        return True
        
    except Exception as e:
        print(f"Unexpected error during QR decoding: {e}")
        return False

def gui():
    """Launch the GUI interface"""
    def generate_qr():
        json_text = text_input.get("1.0", ctk.END).strip()
        
        if not json_text:
            messagebox.showwarning("Empty Input", "Please enter some JSON data.")
            return
            
        try:
            # Validate JSON
            json_obj = json.loads(json_text)
            json_str = json.dumps(json_obj, ensure_ascii=False)
        except json.JSONDecodeError as e:
            messagebox.showerror("Invalid JSON", f"JSON parsing error:\n{str(e)}")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
            title="Save QR Code As"
        )
        
        if file_path:
            try:
                # Create QR code with better settings
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(json_str)
                qr.make(fit=True)
                
                qr_img = qr.make_image(fill_color="black", back_color="white")
                qr_img.save(file_path)
                messagebox.showinfo("Success", f"QR Code successfully saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create QR code:\n{str(e)}")

    def load_json_file():
        """Load JSON from file into the text editor"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Open JSON File"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Validate and format JSON
                json_obj = json.loads(content)
                formatted_json = json.dumps(json_obj, indent=4, ensure_ascii=False)
                
                # Clear and insert formatted JSON
                text_input.delete("1.0", ctk.END)
                text_input.insert("1.0", formatted_json)
                
            except json.JSONDecodeError as e:
                messagebox.showerror("Invalid JSON", f"The selected file contains invalid JSON:\n{str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")

    def decode_qr():
        """Decode QR code from image file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif"), ("All files", "*.*")],
            title="Open QR Code Image"
        )
        
        if file_path:
            try:
                detector = cv2.QRCodeDetector()
                img = cv2.imread(file_path)
                
                if img is None:
                    messagebox.showerror("Error", "Unable to read the selected image file.")
                    return
                    
                data, _, _ = detector.detectAndDecode(img)
                
                if not data:
                    messagebox.showwarning("No QR Code", "No QR code detected in the image.")
                    return
                    
                try:
                    json_obj = json.loads(data)
                    formatted_json = json.dumps(json_obj, indent=4, ensure_ascii=False)
                    
                    # Clear and insert decoded JSON
                    text_input.delete("1.0", ctk.END)
                    text_input.insert("1.0", formatted_json)
                    
                    messagebox.showinfo("Success", "QR code decoded successfully!")
                    
                except json.JSONDecodeError:
                    messagebox.showerror("Invalid Data", "The QR code does not contain valid JSON data.")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Failed to decode QR code:\n{str(e)}")

    # Set up the GUI
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("QSON - JSON to QR Code Tool")
    root.geometry("700x600")
    root.minsize(500, 400)

    try:
        root.iconbitmap("QSON_logo.ico")
    except Exception as e:
        print(f"Error setting app icon: {e}")

        root.mainloop()

    # Main frame
    main_frame = ctk.CTkFrame(master=root)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Title
    title_label = ctk.CTkLabel(
        master=main_frame, 
        text="QSON - JSON ↔ QR Code Tool", 
        font=("Segoe UI", 20, "bold")
    )
    title_label.pack(pady=(10, 5))

    # Instructions
    instruction_label = ctk.CTkLabel(
        master=main_frame,
        text="Enter JSON data below or load from file:",
        font=("Segoe UI", 14)
    )
    instruction_label.pack(pady=5)

    # Button frame
    button_frame = ctk.CTkFrame(master=main_frame)
    button_frame.pack(pady=10, fill="x")

    # Load JSON button
    load_button = ctk.CTkButton(
        master=button_frame,
        text="Load JSON File",
        command=load_json_file,
        width=120
    )
    load_button.pack(side="left", padx=5)

    # Decode QR button
    decode_button = ctk.CTkButton(
        master=button_frame,
        text="Decode QR Code",
        command=decode_qr,
        width=120
    )
    decode_button.pack(side="left", padx=5)

    # Text input area
    text_input = ctk.CTkTextbox(
        master=main_frame,
        font=("Consolas", 12),
        height=350,
        wrap="word"
    )
    text_input.pack(padx=10, pady=10, fill="both", expand=True)

    # Generate QR button
    generate_button = ctk.CTkButton(
        master=main_frame,
        text="Generate QR Code",
        command=generate_qr,
        font=("Segoe UI", 14, "bold"),
        height=40
    )
    generate_button.pack(pady=15)

    # Start the GUI
    root.mainloop()

def cli():
    """Command line interface"""
    parser = argparse.ArgumentParser(
        description="QSON - A tool to convert JSON data to QR codes and vice versa",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python qson.py encode data.json qr_code.png
  python qson.py decode qr_code.png --output decoded.json
  python qson.py  # Launch GUI
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Encode command
    enc_parser = subparsers.add_parser("encode", help="Encode JSON file into QR code")
    enc_parser.add_argument("json_file", help="Path to input JSON file")
    enc_parser.add_argument("output_file", help="Path to save QR code PNG image")

    # Decode command
    dec_parser = subparsers.add_parser("decode", help="Decode QR code image back to JSON")
    dec_parser.add_argument("image_file", help="Path to QR code image file")
    dec_parser.add_argument("--output", "-o", help="Path to save decoded JSON file (optional)")

    args = parser.parse_args()

    if args.command == "encode":
        success = encode_json_to_qr(args.json_file, args.output_file)
        sys.exit(0 if success else 1)
    elif args.command == "decode":
        success = decode_qr_to_json(args.image_file, args.output)
        sys.exit(0 if success else 1)
    else:
        # No command specified, launch GUI
        gui()

if __name__ == "__main__":
    cli()