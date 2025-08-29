import customtkinter as ctk
from tkinter import filedialog
import numpy as np
from PIL import Image
import random
import os
from datetime import datetime

# --- Backend Steganography Logic ---

def xor_crypt(data, key):
    key_len = len(key)
    if isinstance(data, bytes):
        data_bytes = bytearray(data)
    else:
        data_bytes = bytearray(data.encode('utf-8'))
    key_bytes = bytearray(key.encode('utf-8'))
    return bytes([data_bytes[i] ^ key_bytes[i % key_len] for i in range(len(data_bytes))])

def encode_message_in_image(img, secret_message, password):
    width, height = img.size
    n_pixels = width * height
    img = img.convert("RGB")
    img_array = np.array(img).astype(np.uint8)
    
    encrypted_message = xor_crypt(secret_message, password)
    delimiter = b"$$END$$"
    data_to_hide = encrypted_message + delimiter
    binary_data = ''.join(format(byte, '08b') for byte in data_to_hide)
    data_len = len(binary_data)
    
    total_capacity = n_pixels * 3
    if data_len > total_capacity:
        return None, "❌ Error: Message is too large for this image."

    # --- NEW ROBUST LOGIC ---
    # 1. Create a master list of all possible LSB locations (pixel_index * 3 + channel_index)
    all_locations = list(range(total_capacity))
    
    # 2. Shuffle this master list deterministically using the password
    random.seed(password)
    random.shuffle(all_locations)
    
    # 3. Use the first 'data_len' locations from the shuffled list for hiding
    locations_to_use = all_locations[:data_len]
    
    data_idx = 0
    for loc in locations_to_use:
        pixel_idx = loc // 3
        channel_idx = loc % 3
        row, col = divmod(pixel_idx, width)
        
        # Get the pixel's color value and modify the LSB
        pixel_val = img_array[row, col, channel_idx]
        new_pixel_val = (pixel_val & 0b11111110) | int(binary_data[data_idx])
        img_array[row, col, channel_idx] = new_pixel_val
        data_idx += 1
        
    return Image.fromarray(img_array), "✅ Message encoded successfully."

def decode_message_from_image(img, password):
    width, height = img.size
    n_pixels = width * height
    img = img.convert("RGB")
    img_array = np.array(img).astype(np.uint8)

    total_capacity = n_pixels * 3
    
    # --- NEW ROBUST LOGIC ---
    # 1. Regenerate the exact same shuffled master list of locations
    all_locations = list(range(total_capacity))
    random.seed(password)
    random.shuffle(all_locations)

    # 2. Extract LSBs in the exact same order until the delimiter is found
    binary_data = ""
    delimiter_bin = ''.join(format(byte, '08b') for byte in b"$$END$$")
    
    # Limit search to a reasonable amount to prevent hanging on non-stego images
    search_limit = min(total_capacity, len(all_locations))

    for i in range(search_limit):
        loc = all_locations[i]
        pixel_idx = loc // 3
        channel_idx = loc % 3
        row, col = divmod(pixel_idx, width)
        
        lsb = img_array[row, col, channel_idx] & 1
        binary_data += str(lsb)
        
        if binary_data.endswith(delimiter_bin):
            break
    else:
        return None, "❌ Error: Delimiter not found. Wrong password or no message."

    payload_binary = binary_data[:-len(delimiter_bin)]
    
    try:
        all_bytes = int(payload_binary, 2).to_bytes((len(payload_binary) + 7) // 8, byteorder='big')
        decrypted_message = xor_crypt(all_bytes, password)
        return decrypted_message.decode('utf-8', errors='ignore'), "✅ Message decoded successfully."
    except Exception:
        return None, "❌ Error: Failed to decode. Data might be corrupted."

# --- GUI Application (unchanged)---

class SteganographyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.colors = {"dark_gray": "#242424", "medium_gray": "#2b2b2b", "light_gray": "#323232", "text": "#dce4ee", "accent": "#00a98f", "accent_hover": "#008772", "success": "#2ecc71", "error": "#e74c3c"}
        self.title("Steganography Master")
        self.geometry("700x750")
        ctk.set_appearance_mode("Dark")
        self.configure(fg_color=self.colors["dark_gray"])
        
        self.input_image_path = ""
        self.stego_image_path = ""
        
        self.tab_view = ctk.CTkTabview(self, width=650, fg_color=self.colors["medium_gray"], segmented_button_selected_color=self.colors["accent"], segmented_button_selected_hover_color=self.colors["accent_hover"], segmented_button_unselected_color=self.colors["light_gray"])
        self.tab_view.pack(padx=20, pady=20, fill="both", expand=True)
        self.encode_tab = self.tab_view.add("Encode")
        self.decode_tab = self.tab_view.add("Decode")
        self.encode_tab.configure(fg_color=self.colors["medium_gray"])
        self.decode_tab.configure(fg_color=self.colors["medium_gray"])
        
        self.build_encode_tab()
        self.build_decode_tab()
        self.build_log_panel()
        self.build_status_bar()

    def build_log_panel(self):
        log_frame = ctk.CTkFrame(self, fg_color=self.colors["medium_gray"])
        log_frame.pack(padx=20, pady=(0, 10), fill="x")
        log_label = ctk.CTkLabel(log_frame, text="Live Log", text_color=self.colors["text"], font=ctk.CTkFont(weight="bold"))
        log_label.pack(pady=(5,0))
        self.log_textbox = ctk.CTkTextbox(log_frame, state="disabled", height=120, fg_color=self.colors["light_gray"], text_color=self.colors["text"], border_color=self.colors["accent"], border_width=1)
        self.log_textbox.pack(padx=10, pady=10, fill="x", expand=True)
        
    def log_message(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", formatted_message)
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def build_encode_tab(self):
        frame = self.encode_tab
        self.encode_image_label = ctk.CTkLabel(frame, text="Select an image to begin", text_color=self.colors["text"], wraplength=400)
        self.encode_image_label.pack(pady=(20, 5))
        select_img_button = ctk.CTkButton(frame, text="Select Image", fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"], command=self.select_encode_image)
        select_img_button.pack(pady=10)
        self.message_entry = ctk.CTkTextbox(frame, height=100, width=500, fg_color=self.colors["light_gray"], text_color=self.colors["text"], border_color=self.colors["accent"], border_width=1)
        self.message_entry.pack(pady=10)
        self.encode_password_entry = ctk.CTkEntry(frame, placeholder_text="Enter Password", show="*", width=300, fg_color=self.colors["light_gray"], border_color=self.colors["accent"])
        self.encode_password_entry.pack(pady=10)
        encode_button = ctk.CTkButton(frame, text="Encode and Save", fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"], command=self.run_encoding)
        encode_button.pack(pady=20, ipady=10)

    def build_decode_tab(self):
        frame = self.decode_tab
        self.decode_image_label = ctk.CTkLabel(frame, text="Select a stego-image to decode", text_color=self.colors["text"], wraplength=400)
        self.decode_image_label.pack(pady=(20, 5))
        select_stego_img_button = ctk.CTkButton(frame, text="Select Stego Image", fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"], command=self.select_decode_image)
        select_stego_img_button.pack(pady=10)
        self.decode_password_entry = ctk.CTkEntry(frame, placeholder_text="Enter Password", show="*", width=300, fg_color=self.colors["light_gray"], border_color=self.colors["accent"])
        self.decode_password_entry.pack(pady=20)
        decode_button = ctk.CTkButton(frame, text="Decode Message", fg_color=self.colors["accent"], hover_color=self.colors["accent_hover"], command=self.run_decoding)
        decode_button.pack(pady=10, ipady=10)
        self.revealed_message_label = ctk.CTkLabel(frame, text="Revealed Message:", text_color=self.colors["text"])
        self.revealed_message_label.pack(pady=(20, 5))
        self.revealed_message_text = ctk.CTkTextbox(frame, height=60, width=500, state="disabled", fg_color=self.colors["light_gray"], text_color=self.colors["text"], border_color=self.colors["accent"], border_width=1)
        self.revealed_message_text.pack(pady=10)
        
    def build_status_bar(self):
        self.status_label = ctk.CTkLabel(self, text="", text_color=self.colors["text"], height=25, fg_color=self.colors["medium_gray"])
        self.status_label.pack(side="bottom", fill="x", padx=20, pady=(0, 20))

    def update_status(self, message, is_error=False):
        color = self.colors["error"] if is_error else self.colors["success"]
        self.status_label.configure(text=message, text_color=color)
        self.log_message(f"Status: {message}")

    def select_encode_image(self):
        path = filedialog.askopenfilename(title="Select an Image", filetypes=(("PNG files", "*.png"), ("Bitmap files", "*.bmp"), ("All files", "*.*")))
        if path:
            self.input_image_path = path
            self.encode_image_label.configure(text=f"Selected: {os.path.basename(path)}")
            self.log_message(f"Source image loaded: {os.path.basename(path)}")
            self.update_status("Image loaded. Ready to encode.", is_error=False)

    def select_decode_image(self):
        path = filedialog.askopenfilename(title="Select a Stego-Image", filetypes=(("PNG files", "*.png"), ("All files", "*.*")))
        if path:
            self.stego_image_path = path
            self.decode_image_label.configure(text=f"Selected: {os.path.basename(path)}")
            self.log_message(f"Stego-image loaded: {os.path.basename(path)}")
            self.update_status("Stego-image loaded. Ready to decode.", is_error=False)

    def run_encoding(self):
        self.log_message("--- Starting Encode Process ---")
        if not self.input_image_path:
            self.update_status("❌ Error: Please select an image first.", is_error=True)
            return
        message = self.message_entry.get("1.0", "end-1c")
        password = self.encode_password_entry.get()
        if not message:
            self.update_status("❌ Error: Please enter a secret message.", is_error=True)
            return
        if not password:
            self.update_status("❌ Error: Password cannot be empty.", is_error=True)
            return
        
        self.log_message(f"Hiding message: '{message[:30]}...'")
        self.log_message(f"Raw password for encoding: '{password}'")
        
        try:
            with Image.open(self.input_image_path) as img:
                stego_image, status_msg = encode_message_in_image(img, message, password)
            if stego_image is None:
                self.update_status(status_msg, is_error=True)
                return
        except Exception as e:
            self.update_status(f"❌ Error: {e}", is_error=True)
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("PNG files", "*.png"),), title="Save Stego Image As...")
        if save_path:
            stego_image.save(save_path)
            self.log_message(f"Output image saved to: {os.path.basename(save_path)}")
            self.update_status(f"✅ Image saved successfully!", is_error=False)

    def run_decoding(self):
        self.log_message("--- Starting Decode Process ---")
        if not self.stego_image_path:
            self.update_status("❌ Error: Please select a stego-image first.", is_error=True)
            return
        password = self.decode_password_entry.get()
        if not password:
            self.update_status("❌ Error: Password cannot be empty.", is_error=True)
            return
        
        self.log_message(f"Password used for decoding: '{password}'")
        
        try:
            with Image.open(self.stego_image_path) as img:
                revealed_message, status_msg = decode_message_from_image(img, password)
        except Exception as e:
            self.update_status(f"❌ Error: {e}", is_error=True)
            return
        
        self.revealed_message_text.configure(state="normal")
        self.revealed_message_text.delete("1.0", "end")
        if revealed_message is not None:
            self.revealed_message_text.insert("1.0", revealed_message)
            self.log_message(f"Success! Revealed message: '{revealed_message[:30]}...'")
            self.update_status(status_msg, is_error=False)
        else:
            self.revealed_message_text.insert("1.0", "--- DECODING FAILED ---")
            self.update_status(status_msg, is_error=True)
        self.revealed_message_text.configure(state="disabled")

if __name__ == "__main__":
    app = SteganographyApp()
    app.mainloop()
