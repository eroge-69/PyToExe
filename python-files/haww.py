
 
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

window = Tk()

window.title("hawdah")

class Hawdah:
    def __init__(self, master):
        self.master = master
        master.title("Hawdah")

        self.upload_button = tk.Button(master, text="Upload .hwd File", command=self.upload_file)
        self.upload_button.pack(pady=10)

        self.roll_button = tk.Button(master, text="Roll", command=self.roll_file)
        self.roll_button.pack(pady=10)

        self.hwd_file = None

    def upload_file(self):
        self.hwd_file = filedialog.askopenfilename(
            title="Select .hwd file",
            filetypes=[("HWD files", "*.hwd")]
        )
        if self.hwd_file:
            messagebox.showinfo("File Selected", f"File selected: {os.path.basename(self.hwd_file)}")

    def roll_file(self):
        if self.hwd_file is None or not os.path.exists(self.hwd_file):
            messagebox.showerror("Error", "Invalid hwd")
            return

        with open(self.hwd_file, 'r') as file:
            found = False
            for line in file:
                if " 00file.hwd00 " in line:
                    found = True
                    break

            if found:
                image_file = os.path.join(os.path.dirname(self.hwd_file), "file.jpg")
                if os.path.exists(image_file):
                    self.display_image(image_file)
                else:
                    messagebox.showerror("Error", "Image file not found.")
            else:
                messagebox.showerror("Error", "Invalid hwd")

    def display_image(self, image_file):
        img = Image.open(image_file)
        img.thumbnail((400, 400))  # Resize to fit in window
        img = ImageTk.PhotoImage(img)

        img_window = tk.Toplevel(self.master)
        img_window.title("Image Viewer")
        label = tk.Label(img_window, image=img)
        label.image = img  # Keep a reference
        label.pack()

if __name__ == "__main__":
    root = tk.Tk()
    hawder = Hawder(root)
    root.mainloop()


