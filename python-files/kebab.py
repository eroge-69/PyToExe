from PIL import Image
import tkinter as tk
import os

window = tk.Tk()
window.title("Calculator")
window.geometry("800x400")

entry = tk.Entry(window, width=100)
entry.pack(pady=10) 

class Kebab:
    def __init__ (self):
        self.image_name = entry.get()

    def check_format(self):
        file_types = ['jpg', 'jpeg', 'png']
        if any(str(self.image_name).lower().endswith(extension) for extension in file_types):
            return True
        else:
            print(f"Unsupported file format for {self.image_name}. Supported formats are: {', '.join(file_types)}")
            return False
    
    def check_size(self):
        try:
            with Image.open(self.image_name) as img:
                width, height = img.size
                self.size = (width, height)
        except FileNotFoundError:
            print(f"File not found: {self.image_name}")
        except Exception as e:
            print(f"An error occurred: {e}")
        
    def image_resize(self):
        try:
            self.aspect_ratio = self.size[0]  / self.size[1]
            with Image.open(self.image_name) as img:
                new_width = 300
                new_height = int(new_width / self.aspect_ratio * 0.55)
                img = img.resize((new_width, new_height))
                img.save(self.image_name)
        except FileNotFoundError:
            print(f"File not found: {self.image_name}")
        except Exception as e:
            print(f"An error occurred: {e}")
    
    def image_convert(self):
        try:
            with Image.open(self.image_name) as img:
                img = img.convert("L")
                img.save(self.image_name)
        except FileNotFoundError:
            print(f"File not found: {self.image_name}")
        except Exception as e:
            print(f"An error occurred: {e}")

    def ascii_remap(self):
        ascii_chars = "@%#*+=-:. "
        try:
            with Image.open(self.image_name) as img:
                pixels = list(img.getdata())
                ascii_image = ""
                for i, pixel in enumerate(pixels):
                    index = pixel * (len(ascii_chars) - 1) // 255
                    ascii_image += ascii_chars[index]
                    if (i + 1) % 300 == 0:
                        ascii_image += "\n"
                with open("output.txt", "w", encoding="utf-8") as file:
                    file.write(ascii_image)
                    os.startfile("output.txt")
        except FileNotFoundError:
            print(f"File not found: {self.image_name}")
        except Exception as e:
            print(f"An error occurred: {e}")

def process_image():
    kebab = Kebab()
    kebab.check_format()
    kebab.check_size()
    kebab.image_resize()
    kebab.image_convert()
    kebab.ascii_remap()

number1 = tk.Button(window, text = 'Обработать фото', command = process_image)
number1.pack(side=tk.LEFT, padx = 10, pady = 10)

window.mainloop()