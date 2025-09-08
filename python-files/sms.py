import xml.etree.ElementTree as ET
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox


def extract_sms(xml_file, output_file):
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        with open(output_file, "w", encoding="utf-8") as f:
            for sms in root.findall("sms"):
                msg_type = sms.attrib.get("type", "").strip()
                body = sms.attrib.get("body", "").strip()
                date_str = sms.attrib.get("readable_date", "").strip()

                if not body:
                    continue

                if msg_type == "1":  # Received
                    sender = sms.attrib.get("contact_name", "").strip()
                    if not sender or sender.lower() == "null":
                        sender = sms.attrib.get("address", "Unknown")
                elif msg_type == "2":  # Sent
                    sender = "Jack Murray"
                else:
                    sender = "Unknown"

                f.write(f"{date_str} - {sender}\n")
                f.write(f"{body}\n\n")

        messagebox.showinfo("Success", f"Export complete!\nSaved to:\n{output_file}")

    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")


def select_file():
    xml_file = filedialog.askopenfilename(
        title="Select SMS Backup XML",
        filetypes=[("XML Files", "*.xml"), ("All Files", "*.*")]
    )
    if xml_file:
        output_file = os.path.splitext(xml_file)[0] + "_messages.txt"
        extract_sms(xml_file, output_file)


# --- Modern Dark UI Setup ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

root = ctk.CTk()
root.title("SMS XML Extractor")
root.geometry("420x220")

# Remove the default square icon
try:
    root.iconbitmap("")  # Clears the default tkinter icon
except:
    pass  # fallback if OS ignores

# Title
title_label = ctk.CTkLabel(root, text="SMS Backup Extractor", font=("Segoe UI", 20, "bold"))
title_label.pack(pady=(20, 10))

# Instruction
label = ctk.CTkLabel(root, text="Select your SMS backup XML file to extract messages.", font=("Segoe UI", 13))
label.pack(pady=(0, 20))

# Buttons Frame
btn_frame = ctk.CTkFrame(root, fg_color="transparent")
btn_frame.pack(pady=10)

browse_btn = ctk.CTkButton(btn_frame, text="Browse XML File", command=select_file, corner_radius=15, width=150)
browse_btn.grid(row=0, column=0, padx=15)

root.mainloop()