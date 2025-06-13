import tkinter as tk
import random
from random_word import RandomWords

r = RandomWords()
random_char = ""
pass1=""

Letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
Numbers = "0123456789"
Special = "!@#$%^&*()-_=+[]{}|;:,.<>?/~`"
password = r.get_random_word()
for item in range(random.randint(1, 4)):
    password += random.choice(Letters)
for item in range(random.randint(1, 4)):
    password += random.choice(Special)
for item in range(random.randint(1, 4)):
    password += random.choice(Numbers)

p=""

def Generate():
    textbox.delete("1.0", tk.END)
    list_from_string = list(password)
    random.shuffle(list_from_string)
    final=p.join(list_from_string)
    textbox.insert(tk.END, final)
    with open("password.txt", "w") as file:
        file.write(final)

# Create the main window
root = tk.Tk()

root.title("Password generator")

# Create a 1x16 textbox
#textbox = tk.Label(root, height=1, width=16)
#textbox.pack(pady=10) # pady is applied here, within the pack() method
textbox = tk.Text(root, height=6, width=45, wrap=tk.WORD)
textbox.grid(row=8, column=1)
# Create a button labeled "Generate"
generate_button = tk.Button(root, text="Generate", command=Generate)
generate_button.grid(row=9, column=1, pady=10)  # pady is applied here, within the grid() method
 # pady is applied here, within the pack() method

# Run the Tkinter event loop
root.mainloop()