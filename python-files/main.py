import torch
import psutil
from diffusers import StableDiffusionPipeline
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import sys

def detect_device_and_level():
    """Xác định thiết bị và phân loại mức độ phần cứng."""
    if torch.cuda.is_available():
        device = "cuda"
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
        if vram_gb < 4:
            level = "weak"
        elif vram_gb < 8:
            level = "medium"
        else:
            level = "strong"
    else:
        device = "cpu"
        ram_gb = psutil.virtual_memory().total / (1024 ** 3)
        cpu_count = psutil.cpu_count(logical=False)
        if ram_gb < 4 or cpu_count < 2:
            level = "weak"
        elif ram_gb < 8:
            level = "medium"
        else:
            level = "strong"

    return device, level

def choose_model(level):
    """Chọn mô hình phù hợp với mức phần cứng."""
    if level == "weak":
        return "stabilityai/sd-turbo"
    elif level == "medium":
        return "runwayml/stable-diffusion-v1-5"
    else:
        return "stabilityai/stable-diffusion-xl-base-1.0"

def generate_image(content: str, save_path: str):
    """Sinh ảnh từ prompt và lưu lại."""
    device, level = detect_device_and_level()
    model_id = choose_model(level)

    print(f"[INFO] Detected: {device.upper()} | Level: {level.upper()} → Model: {model_id}")

    pipe = StableDiffusionPipeline.from_pretrained(
        model_id,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )

    pipe.to(device)
    image = pipe(content).images[0]
    image.save(save_path)
    print(f"[OK] Saved to: {save_path}")
    messagebox.showinfo("Done", f"Image saved at:\n{save_path}")

def main():
    print("Please type the content of the image you want to generate.")
    user_content = input(">>> ")
    print("Please type in the name of the image file (no extension needed).")
    image_name = input(">>> ")

    root = tk.Tk()
    root.withdraw()  # Ẩn cửa sổ chính
    selected_folder = filedialog.askdirectory(title="Choose where to save the image")

    if selected_folder:
        save_path = os.path.join(selected_folder, image_name + ".png")
        print("Generating...")
        generate_image(user_content, save_path)
    else:
        print("No folder selected. Exiting...")
        sys.exit()

if __name__ == "__main__":
    while True:
        main()
