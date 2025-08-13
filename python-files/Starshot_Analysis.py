from fileinput import filename

from networkx.utils import open_file
from pylinac import Starshot
import tkinter as tk
from tkinter import filedialog
from tkPDFViewer import tkPDFViewer as pdf
from datetime import datetime

root = tk.Tk()
root.title("Starshot Anlysis by PC")
root.geometry("500x300")
root.resizable(False, False)


text_var = tk.StringVar()
text_var.set("")
label = tk.Label(root,
                 textvariable=text_var,
                 anchor=tk.CENTER,
                 bg="skyblue",
                 height=35,
                 width=35,
                 bd=3,
                 font=("Arial", 16, "bold"),
                 cursor="",
                 fg="red",
                 padx=15,
                 pady=15,
                 justify=tk.CENTER,
                 relief=tk.RAISED,
                 underline=0,
                 wraplength=250
                )
label.pack(pady=5)

def import_file():
    filename = filedialog.askopenfilename(parent=root, filetypes=[("All files", "*")])
    print(filename)
    file_label = tk.Label(root, text=filename)
    file_label.place(x=50, y=5)
    def analyze():
        from pylinac import Starshot
        mystar = Starshot(filename, dpi = 105, sid = 1000)
        mystar.analyze(radius=0.5, tolerance=1.0)
        print(mystar.results())
        data = mystar.results_data()
        data.tolerance_mm
        data.passed
        data_dict = mystar.results_data(as_dict=True)
        data_dict['passed']
        date = datetime.now().strftime("-%d-%m-%Y")
        mystar.publish_pdf(f'Gantry_Starshot-{date}.pdf',open_file=True)
    button = tk.Button(root, text="Gantry-analyze", command=analyze)
    button.config(width=30, height=2)
    button.place(x=200, y=25)

button = tk.Button(root, text="Gantry-Starshot", command=import_file)
button.place(x=50, y=30)

def import_file():
    filename = filedialog.askopenfilename(parent=root, filetypes=[("All files", "*")])
    print(filename)
    file_label = tk.Label(root, text=filename)
    file_label.place(x=50, y=70)
    def analyze():
        from pylinac import Starshot
        mystar = Starshot(filename, dpi = 105, sid = 1000)
        mystar.analyze(radius=0.5, tolerance=1.0)
        print(mystar.results())
        data = mystar.results_data()
        data.tolerance_mm
        data.passed
        data_dict = mystar.results_data(as_dict=True)
        data_dict['passed']
        date = datetime.now().strftime("-%d-%m-%Y")
        mystar.publish_pdf(f'Collimator_Starshot-{date}.pdf', open_file=True)
    button = tk.Button(root, text="Collimator-analyze", command=analyze)
    button.config(width=30, height=2)
    button.place(x=200, y=90)

button = tk.Button(root, text="Collimator-Starshot", command=import_file)
button.place(x=50, y=95)

def import_file():
    filename = filedialog.askopenfilename(parent=root, filetypes=[("All files", "*")])
    print(filename)
    file_label = tk.Label(root, text=filename)
    file_label.place(x=50, y=135)
    def analyze():
        from pylinac import Starshot
        mystar = Starshot(filename, dpi = 105, sid = 1000)
        mystar.analyze(radius=0.5, tolerance=1.0)
        print(mystar.results())
        data = mystar.results_data()
        data.tolerance_mm
        data.passed
        data_dict = mystar.results_data(as_dict=True)
        data_dict['passed']
        date = datetime.now().strftime("-%d-%m-%Y")
        mystar.publish_pdf(f'Couch_Starshot-{date}.pdf', open_file=True)
    button = tk.Button(root, text="Couch-analyze", command=analyze)
    button.place(x=200, y=155)
    button.config(width=30, height=2)


button = tk.Button(root, text="Couch-Starshot", command=import_file)
button.place(x=50, y=160)



button_exit = tk.Button(root,
                 text="EXIT",
                 bg="skyblue",
                 bd=3,
                 font=("Arial", 14, "bold"),
                 cursor="",
                 fg="red",
                 command=root.destroy)

button_exit.place(x=50, y=220)
button_exit.config(width=30, height=2)
root.mainloop()


filedialog.asksaveasfile(initialfile='Couch-Starshot.pdf', defaultextension=".pdf",filetypes=[("PDF files", "*.pdf")]),