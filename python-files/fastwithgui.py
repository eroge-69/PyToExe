import os
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import time
import threading

# Setup window
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Cozy Text Creator 🍩")
app.geometry("400x700")
app.resizable(False, False)

generated_lines = []
animate_text = True  # Control animation toggle

# --- Functions ---
def generate_text():
    global generated_lines
    
    try:
        count = int(entry_count.get())
        text = entry_text.get()

        output_text.delete("0.0", "end")
        generated_lines = []
        
        button_generate.configure(state="disabled")
        button_toggle_animation.configure(state="disabled")
        progress_bar.start()
        
        if animate_text:
            # Animated generation
            for i in range(1, count + 1):
                line = f"{i}. {text}"
                output_text.insert("end", "")
                for char in line:
                    output_text.insert("end", char)
                    app.update()
                    time.sleep(0.03)
                output_text.insert("end", "\n")
                generated_lines.append(line)
        else:
            # Instant generation (no animation)
            for i in range(1, count + 1):
                line = f"{i}. {text}"
                output_text.insert("end", f"{line}\n")
                generated_lines.append(line)
                app.update()  # Still update UI to show progress
        
    except ValueError:
        messagebox.showerror("Oops!", "Please enter a valid number.")
    finally:
        button_generate.configure(state="normal")
        button_toggle_animation.configure(state="normal")
        progress_bar.stop()

def toggle_animation():
    global animate_text
    animate_text = not animate_text
    if animate_text:
        button_toggle_animation.configure(text="⚡ Skip Animation", 
                                        fg_color="#FFDAC1", 
                                        hover_color="#E2F0CB")
    else:
        button_toggle_animation.configure(text="✏️ Enable Animation", 
                                        fg_color="#B5EAD7", 
                                        hover_color="#C7CEEA")

def save_file():
    if not generated_lines:
        messagebox.showwarning("Warning", "Generate text before saving!")
        return

    file_path = filedialog.asksaveasfilename(
        defaultextension=".txt",
        initialdir=os.path.join(os.path.expanduser('~'), 'Documents'),
        title="Save File",
        filetypes=(("Text files", "*.txt"), ("All files", "*.*"))
    )

    if file_path:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(generated_lines))
        messagebox.showinfo("Success", f"File saved:\n{file_path}")

def toggle_mode():
    current_mode = ctk.get_appearance_mode()
    if current_mode == "Light":
        ctk.set_appearance_mode("Dark")
        button_toggle_mode.configure(text="☀️ Light Mode")
    else:
        ctk.set_appearance_mode("Light")
        button_toggle_mode.configure(text="🌙 Dark Mode")

# --- UI Elements ---
try:
    bg_image = ctk.CTkImage(light_image=Image.open("bg.jpg"),
                           dark_image=Image.open("bg.jpg"),
                           size=(400, 700))
    background_label = ctk.CTkLabel(app, image=bg_image, text="")
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    background_label.lower()
except Exception as e:
    print(f"Error loading background image: {e}")
    app.configure(fg_color="#f5f5f5")

content_frame = ctk.CTkFrame(app, fg_color="transparent")
content_frame.pack(pady=20, padx=20, fill="both", expand=True)

label_title = ctk.CTkLabel(content_frame, 
                         text="Cozy Text Creator 🍩", 
                         font=("Caveat", 26, "bold"), 
                         text_color="#333333")
label_title.pack(pady=10)

# Input Frame
input_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
input_frame.pack(pady=10)

entry_count = ctk.CTkEntry(input_frame, 
                         placeholder_text="How many times?", 
                         width=200, 
                         font=("Caveat", 14),
                         fg_color="white",
                         text_color="#333333")
entry_count.pack(pady=5)

entry_text = ctk.CTkEntry(input_frame, 
                        placeholder_text="What to write?", 
                        width=200, 
                        font=("Caveat", 14),
                        fg_color="white",
                        text_color="#333333")
entry_text.pack(pady=5)

# Button Frame
button_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
button_frame.pack(pady=10)

button_generate = ctk.CTkButton(button_frame, 
                              text="Generate 🍬", 
                              command=lambda: threading.Thread(target=generate_text).start(), 
                              width=180, 
                              font=("Caveat", 14), 
                              fg_color="#FF9AA2", 
                              hover_color="#FFB7B2",
                              text_color="white")
button_generate.pack(pady=5)

button_toggle_animation = ctk.CTkButton(button_frame, 
                                     text="⚡ Skip Animation", 
                                     command=toggle_animation, 
                                     width=180, 
                                     font=("Caveat", 12), 
                                     fg_color="#FFDAC1", 
                                     hover_color="#E2F0CB",
                                     text_color="#333333")
button_toggle_animation.pack(pady=5)

# Progress bar
progress_bar = ctk.CTkProgressBar(content_frame, 
                                width=300, 
                                mode="indeterminate",
                                fg_color="#B5EAD7",
                                progress_color="#FF9AA2")
progress_bar.pack(pady=5)
progress_bar.set(0)

# Other buttons
button_save = ctk.CTkButton(content_frame, 
                          text="Save 📂", 
                          command=save_file, 
                          width=200, 
                          font=("Caveat", 14), 
                          fg_color="#FFDAC1", 
                          hover_color="#E2F0CB",
                          text_color="#333333")
button_save.pack(pady=10)

button_toggle_mode = ctk.CTkButton(content_frame, 
                                 text="🌙 Dark Mode", 
                                 command=toggle_mode, 
                                 width=200, 
                                 font=("Caveat", 14), 
                                 fg_color="#B5EAD7", 
                                 hover_color="#C7CEEA",
                                 text_color="#333333")
button_toggle_mode.pack(pady=10)

# Output text
output_text = ctk.CTkTextbox(content_frame, 
                           width=320, 
                           height=250, 
                           font=("Caveat", 14), 
                           text_color="#333333", 
                           corner_radius=10,
                           fg_color="#ffffff",
                           scrollbar_button_color="#B5EAD7")
output_text.pack(pady=10)

app.mainloop()