import string
import random
import customtkinter

# CTk Settings
customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

# App Window
app = customtkinter.CTk()
app.geometry("500x450")
app.title("Password Generator")

# Title Label
title_label = customtkinter.CTkLabel(app, text="PASSWORD GENERATOR", font=("Arial", 20))
title_label.pack(pady=10)

# Entry: Number of Passwords
passn_label = customtkinter.CTkLabel(app, text="How many passwords?")
passn_label.pack()
passn_entry = customtkinter.CTkEntry(app)
passn_entry.pack(pady=5)

# Entry: Length of Passwords
length_label = customtkinter.CTkLabel(app, text="How many letters per password?")
length_label.pack()
length_entry = customtkinter.CTkEntry(app)
length_entry.pack(pady=5)

# Checkbox: Include Special Characters
special_chars_var = customtkinter.BooleanVar()
special_chars_checkbox = customtkinter.CTkCheckBox(app, text="Include Special Characters", variable=special_chars_var)
special_chars_checkbox.pack(pady=5)

# Output Box
output_box = customtkinter.CTkTextbox(app, width=400, height=150)
output_box.pack(pady=10)

# Password Generator Function
def generate_passwords():
    try:
        num_passwords = int(passn_entry.get())
        length = int(length_entry.get())
        if num_passwords < 1 or length < 1:
            output_box.delete("1.0", "end")
            output_box.insert("end", "Please enter positive numbers.")
            return
    except ValueError:
        output_box.delete("1.0", "end")
        output_box.insert("end", "Please enter valid numbers.")
        return

    output_box.delete("1.0", "end")

    letters = string.ascii_letters
    digits = string.digits
    specials = string.punctuation if special_chars_var.get() else ""
    all_chars = letters + digits + specials

    for _ in range(num_passwords):
        password = ''.join(random.choice(all_chars) for _ in range(length))
        output_box.insert("end", password + "\n")

# Generate Button
generate_button = customtkinter.CTkButton(master=app, text="Generate Passwords", command=generate_passwords)
generate_button.pack(pady=10)

# Run App
app.mainloop()
