from ahk import AHK
from PIL import Image, ImageTk
import os
import json
import time
import requests
from tkinter import (
    Tk, Label, Button, filedialog, messagebox, Text, Scrollbar, Toplevel,
    Canvas, Scale, HORIZONTAL, StringVar, Entry
)
from pynput import keyboard
from collections import defaultdict
import threading
import webbrowser
import pyautogui
import tkinter as tk

satiricalNotice = False

image_path = None
pixel_size = 20
hover_delay = 0.1
typing_retry_delay = 0.1
stop_script = False
ahk = AHK()

PROGRAM_VERSION = 1.0

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "stop_key": "esc",
    "color_tolerance": 30,
    "mouse_speed": 5,
    "canvas_start_x": 664,
    "canvas_start_y": 176,
    "color_wheel_button": [1091, 830],
    "hex_input_box": [1091, 733]
}

config = None
stop_key = None
color_tolerance = None
mouse_speed = None
canvas_start_x = None
canvas_start_y = None
color_wheel_button = None
hex_input_box = None

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    else:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

stop_script = False

def on_press(key):
    global stop_script
    try:
        if key == keyboard.Key.esc:
            print("ESC pressed! Stopping the script...")
            stop_script = True
            return False
    except Exception as e:
        print(f"Error: {e}")

listener = keyboard.Listener(on_press=on_press)
listener.start()

time.sleep(2)

def focus_roblox_window():
    script = """
    SetTitleMatchMode, 2
    IfWinExist, Roblox
    {
        WinActivate
    }
    Return
    """
    ahk.run_script(script)
    time.sleep(1)

def type_hex_color(hex_color):
    for _ in range(3):
        ahk.type(hex_color)
        time.sleep(typing_retry_delay)
        ahk.send("{Enter}")
        time.sleep(typing_retry_delay)
        return

def round_color(value, tolerance):
    return max(0, min(255, (value // tolerance) * tolerance))

def paint_color(color, pixels, console, total_pixels, painted_pixels):
    global stop_script, mouse_speed
    ahk.mouse_move(color_wheel_button[0], color_wheel_button[1], speed=mouse_speed)
    ahk.click()
    time.sleep(hover_delay / mouse_speed)
    ahk.mouse_move(hex_input_box[0], hex_input_box[1], speed=mouse_speed)
    ahk.click()
    type_hex_color(color)
    ahk.mouse_move(color_wheel_button[0], color_wheel_button[1], speed=mouse_speed)
    ahk.click()
    for x, y in pixels:
        if stop_script:
            return
        target_x = canvas_start_x + x * pixel_size
        target_y = canvas_start_y + y * pixel_size
        ahk.mouse_move(target_x, target_y, speed=mouse_speed)
        ahk.click()
        painted_pixels[0] += 1
        remaining_pixels = total_pixels - painted_pixels[0]
        progress_percent = (painted_pixels[0] / total_pixels) * 100
        console.delete(1.0, "end")
        console.insert("end", f"{painted_pixels[0]}/{total_pixels} pixels painted\n")
        console.insert("end", f"{remaining_pixels} remaining\n")
        console.insert("end", f"{progress_percent:.2f}% complete\n")
        console.see("end")

def paint_canvas(image_path, console):
    global stop_script
    try:
        image = Image.open(image_path).convert("RGB")
        pixel_art = get_tolerant_color_image(image, color_tolerance)
    except FileNotFoundError:
        messagebox.showerror("Error", "Image not found. Please select a valid image.")
        return

    color_groups = defaultdict(list)
    pixels = pixel_art.load()
    total_pixels = 32 * 32
    painted_pixels = [0]

    for row in range(32):
        for col in range(32):
            r, g, b = pixels[col, row]
            hex_color = f"{r:02x}{g:02x}{b:02x}"
            color_groups[hex_color].append((col, row))

    console.delete(1.0, "end")
    console.insert("end", f"Grouped into {len(color_groups)} colors\n")
    console.see("end")

    for color, pixel_list in color_groups.items():
        if stop_script:
            return
        paint_color(color, pixel_list, console, total_pixels, painted_pixels)
    messagebox.showinfo("Done", "Drawing completed!")

def get_tolerant_color_image(image, tolerance):
    image = image.resize((32, 32), Image.Resampling.BOX)
    pixels = image.load()
    for row in range(32):
        for col in range(32):
            r, g, b = pixels[col, row]
            r = round_color(r, tolerance)
            g = round_color(g, tolerance)
            b = round_color(b, tolerance)
            pixels[col, row] = (r, g, b)
    return image
    image = image.resize((32, 32), Image.Resampling.BOX)
    pixels = image.load()
    for row in range(32):
        for col in range(32):
            r, g, b = pixels[col, row]
            r = round_color(r, tolerance)
            g = round_color(g, tolerance)
            b = round_color(b, tolerance)
            pixels[col, row] = (r, g, b)
    for row in range(32):
        if 21 < 32:
            pixels[20, row] = pixels[21, row]
    for col in range(32):
        if 20 < 32:
            pixels[col, 19] = pixels[col, 20]
    return image

def confirm_preview(preview_canvas, console):
    if messagebox.askyesno("Confirm Preview", "Does the preview look correct?"):
        console.insert("end", "Preview confirmed. Starting drawing...\n")
        start_drawing(console)
    else:
        console.insert("end", "Preview rejected. Please adjust the image or tolerance.\n")

def start_drawing(console):
    global stop_script, image_path
    if not image_path:
        messagebox.showerror("Error", "Please upload an image before starting.")
        return
    stop_script = False
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    focus_roblox_window()
    threading.Thread(target=paint_canvas, args=(image_path, console)).start()

def upload_image(preview_canvas, tolerance):
    def upload_from_computer():
        global image_path
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            image_path = file_path
            messagebox.showinfo("Image Uploaded", f"Selected Image: {file_path}")
            show_preview(preview_canvas, tolerance)
            upload_window.destroy()

    def upload_from_url():
        def fetch_image():
            try:
                url = url_entry.get()
                if not os.path.exists("downloaded_images"):
                    os.makedirs("downloaded_images")
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                file_name = f"downloaded_image_{timestamp}.png"
                downloaded_path = os.path.join("downloaded_images", file_name)
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(downloaded_path, "wb") as f:
                    f.write(response.content)
                global image_path
                image_path = downloaded_path
                messagebox.showinfo("Download Complete", f"Image downloaded successfully.\nSaved as: {file_name}")
                show_preview(preview_canvas, tolerance)
                url_window.destroy()
                upload_window.destroy()
            except (requests.exceptions.RequestException, IOError) as e:
                messagebox.showerror("Error", f"Failed to fetch or save the image.\n{e}")

        url_window = Toplevel(upload_window)
        url_window.title("Download Image")
        url_window.geometry("400x200")
        Label(url_window, text="Enter Image URL:").pack(pady=10)
        url_entry = Entry(url_window, width=50)
        url_entry.pack(pady=10)
        Button(url_window, text="Download", command=fetch_image).pack(pady=10)

    upload_window = Toplevel()
    upload_window.title("Upload Image")
    upload_window.geometry("400x200")
    Label(upload_window, text="Choose how to upload the image:", font=("Arial", 14)).pack(pady=20)
    Button(upload_window, text="Upload from Computer", command=upload_from_computer, width=25).pack(pady=10)
    Button(upload_window, text="Upload from URL", command=upload_from_url, width=25).pack(pady=10)
    Button(upload_window, text="Cancel", command=upload_window.destroy, width=25).pack(pady=10)

def show_preview(preview_canvas, tolerance):
    global image_path
    if not image_path:
        return
    try:
        image = Image.open(image_path).convert("RGB")
        pixel_art = get_tolerant_color_image(image, tolerance)
        preview_image = ImageTk.PhotoImage(image=pixel_art.resize((128, 128), Image.Resampling.NEAREST))
        preview_canvas.delete("all")
        preview_canvas.create_image(0, 0, anchor="nw", image=preview_image)
        preview_canvas.image = preview_image
    except Exception as e:
        messagebox.showerror("Error", f"Failed to generate preview:\n{e}")

def show_mouse_info():
    mouse_window = tk.Toplevel()
    mouse_window.title("Mouse Coordinates")
    mouse_window.geometry("300x100")
    mouse_window.resizable(False, False)
    label = tk.Label(mouse_window, text="Move your mouse to see coordinates...", font=("Arial", 12))
    label.pack(pady=10)
    coords_label = tk.Label(mouse_window, text="", font=("Arial", 14), fg="blue")
    coords_label.pack(pady=10)
    running = True
    def update_coordinates():
        while running:
            x, y = pyautogui.position()
            coords_label.config(text=f"X: {x}, Y: {y}")
            coords_label.update()
            time.sleep(0.1)
    def on_close():
        nonlocal running
        running = False
        mouse_window.destroy()
    mouse_window.protocol("WM_DELETE_WINDOW", on_close)
    threading.Thread(target=update_coordinates, daemon=True).start()

def configure_options(preview_canvas):
    global stop_key, color_tolerance, mouse_speed
    global canvas_start_x, canvas_start_y, color_wheel_button, hex_input_box
    options_window = Toplevel()
    options_window.title("Options")
    options_window.geometry("500x600")
    Label(options_window, text="Stop Keybind:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
    stop_key_var = StringVar(value=stop_key)
    keybind_label = Label(options_window, text="Press a key...", relief="sunken", width=20)
    keybind_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
    def capture_key(event):
        nonlocal stop_key_var
        keybind_label.config(text=f"Key: {event.keysym}")
        stop_key_var.set(event.keysym)
    keybind_label.bind("<Key>", capture_key)
    keybind_label.focus_set()
    Label(options_window, text="Color Tolerance:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
    tolerance_slider = Scale(options_window, from_=1, to=255, orient=HORIZONTAL, length=300)
    tolerance_slider.set(color_tolerance)
    tolerance_slider.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w")
    Label(options_window, text="Mouse Speed:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
    speed_slider = Scale(options_window, from_=1, to=10, orient=HORIZONTAL, length=300)
    speed_slider.set(mouse_speed)
    speed_slider.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="w")
    Label(options_window, text="Canvas Start X:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
    canvas_start_x_var = StringVar(value=str(canvas_start_x))
    canvas_start_x_entry = Entry(options_window, textvariable=canvas_start_x_var, width=15)
    canvas_start_x_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")
    Label(options_window, text="Canvas Start Y:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
    canvas_start_y_var = StringVar(value=str(canvas_start_y))
    canvas_start_y_entry = Entry(options_window, textvariable=canvas_start_y_var, width=15)
    canvas_start_y_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")
    Label(options_window, text="Color Wheel Button (X, Y):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
    color_wheel_button_x_var = StringVar(value=str(color_wheel_button[0]))
    color_wheel_button_y_var = StringVar(value=str(color_wheel_button[1]))
    color_wheel_button_x_entry = Entry(options_window, textvariable=color_wheel_button_x_var, width=7)
    color_wheel_button_y_entry = Entry(options_window, textvariable=color_wheel_button_y_var, width=7)
    color_wheel_button_x_entry.grid(row=5, column=1, padx=5, pady=5, sticky="w")
    color_wheel_button_y_entry.grid(row=5, column=2, padx=5, pady=5, sticky="w")
    Label(options_window, text="Hex Input Box (X, Y):").grid(row=6, column=0, padx=10, pady=5, sticky="w")
    hex_input_box_x_var = StringVar(value=str(hex_input_box[0]))
    hex_input_box_y_var = StringVar(value=str(hex_input_box[1]))
    hex_input_box_x_entry = Entry(options_window, textvariable=hex_input_box_x_var, width=7)
    hex_input_box_y_entry = Entry(options_window, textvariable=hex_input_box_y_var, width=7)
    hex_input_box_x_entry.grid(row=6, column=1, padx=5, pady=5, sticky="w")
    hex_input_box_y_entry.grid(row=6, column=2, padx=5, pady=5, sticky="w")
    def save_options():
        global stop_key, color_tolerance, mouse_speed
        global canvas_start_x, canvas_start_y, color_wheel_button, hex_input_box
        stop_key = stop_key_var.get()
        color_tolerance = int(tolerance_slider.get())
        if color_tolerance < 30:
            messagebox.showwarning("Low Tolerance Warning", "A color tolerance below 30 may make rendering take longer.")
        elif color_tolerance >= 50:
            messagebox.showwarning("High Tolerance Warning", "A color tolerance of 50 or above may reduce image quality.")
        mouse_speed = int(speed_slider.get())
        canvas_start_x = int(canvas_start_x_var.get())
        canvas_start_y = int(canvas_start_y_var.get())
        color_wheel_button = [int(color_wheel_button_x_var.get()), int(color_wheel_button_y_var.get())]
        hex_input_box = [int(hex_input_box_x_var.get()), int(hex_input_box_y_var.get())]
        config = {
            "stop_key": stop_key,
            "color_tolerance": color_tolerance,
            "mouse_speed": mouse_speed,
            "canvas_start_x": canvas_start_x,
            "canvas_start_y": canvas_start_y,
            "color_wheel_button": color_wheel_button,
            "hex_input_box": hex_input_box,
        }
        save_config(config)
        show_preview(preview_canvas, color_tolerance)
        options_window.destroy()
    Button(options_window, text="Save", command=save_options).grid(row=7, column=1, padx=10, pady=20, sticky="w")
    Button(options_window, text="Show Mouse Coordinates", command=show_mouse_info).grid(row=7, column=1, padx=40, pady=20)

def show_help():
    global satiricalNotice
    if not satiricalNotice:
        messagebox.showinfo("Notice,", "The exaggerated and humorous language within the instructions is satirical and is NOT directed at any individual or group. Hopefully, you find it amusing and enjoy using the tool.")
        satiricalNotice = True
    help_window = Toplevel()
    help_window.title("Help")
    help_window.geometry("500x400")
    help_text = """Alright, you talentless fuck, here’s how to use this pixel art tool because apparently you’re too goddamn incompetent to draw a stick figure on your own. Pathetic.

Features (That You Don’t Deserve):
- Upload an image from your shitty computer or yank one off the internet via URL because your hands are too shaky to make anything worthwhile.
- Mess with the Options menu—canvas start positions, color tolerance, mouse speed, blah blah blah—like you’re some kind of artist when we both know you’re not.
- Auto-draw pixel art on your sad little canvas since your brain can’t handle doing it manually.

--- Instructions (Pay Attention, Dipshit) ---
1. Upload Image: Click that 'Upload Image' button and pick something or paste a URL. What, did you think you’d sketch it yourself? Hilarious.

2. Options Menu (Try Not to Fuck This Up):
    2a: Stop Keybind: Pick a key to slam when you inevitably panic and need to stop the script.
    2b: Color Tolerance: Crank this to lump colors together because your dumb ass can’t tell shades apart. 
    2c: Mouse Speed: Speed up or slow down the cursor—I recommend setting it to 1 since you’re already slow as shit.
    2d: Canvas Start X/Y: Tell it where to start on your canvas, because spatial awareness isn’t your thing.
    2e: Color Wheel Button and Hex Input Box: Set where your color tools live. Good luck figuring out what “hex” even means, genius.
    2f: Save Settings: Hit save to 'config.json' so you don’t have to redo this every time your smooth brain forgets.

3. Press 'Draw': Watch the magic happen while you sit there drooling, pretending you contributed.

--- Other Bullshit ---

Tips (Not That You’ll Get It):
- Use square images (32x32 is best) unless you want it to look like a dumpster fire. Oh wait, that’s your default.
- Color tolerance under 30? Takes forever. Over 50? Looks like ass. Pick your poison, Picasso.

Need Help? (Of Course You Do):

- Cry to me (Frindow) on Discord or drop a whiny comment on GitHub. I’ll try not to laugh too hard at your expense.


Now go pretend you’re an artist, you helpless bastard. This tool’s doing all the work while your dumbass takes all the credit."""
    Label(help_window, text="Help and Instructions", font=("Arial", 14)).pack(pady=10)
    help_textbox = Text(help_window, wrap="word", width=60, height=20)
    help_textbox.insert("1.0", help_text)
    help_textbox.config(state="disabled")
    help_textbox.pack(padx=10, pady=10)
    Button(help_window, text="Close", command=help_window.destroy).pack(pady=10)

def create_gui():
    global stop_key, color_tolerance, mouse_speed
    global canvas_start_x, canvas_start_y, color_wheel_button, hex_input_box
    global config
    config = load_config()
    stop_key = config["stop_key"]
    color_tolerance = config["color_tolerance"]
    mouse_speed = config["mouse_speed"]
    canvas_start_x = config["canvas_start_x"]
    canvas_start_y = config["canvas_start_y"]
    color_wheel_button = config["color_wheel_button"]
    hex_input_box = config["hex_input_box"]
    root = Tk()
    root.title("Pixel Art Drawer")
    root.geometry("500x600")
    Label(root, text="Starving Artists AutoDraw", font=("Arial", 16)).pack(pady=10)
    preview_canvas = Canvas(root, width=128, height=128, bg="white")
    preview_canvas.pack(pady=5)
    Button(root, text="Upload Image", command=lambda: upload_image(preview_canvas, color_tolerance), width=20).pack(pady=10)
    Button(root, text="Draw", command=lambda: confirm_preview(preview_canvas, console), width=20).pack(pady=5)
    Button(root, text="Options", command=lambda: configure_options(preview_canvas), width=20).pack(pady=10)
    Button(root, text="Help", command=show_help, width=20).pack(pady=10)
    Button(root, text="Exit", command=root.quit, width=20).pack(pady=10)
    scrollbar = Scrollbar(root)
    scrollbar.pack(side="right", fill="y")
    global console
    console = Text(root, wrap="word", height=10, yscrollcommand=scrollbar.set)
    console.pack(padx=10, pady=10, fill="both", expand=True)
    scrollbar.config(command=console.yview)
    root.mainloop()

if __name__ == "__main__":
    create_gui()
