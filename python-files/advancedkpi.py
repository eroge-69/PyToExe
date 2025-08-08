import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from datetime import datetime

import os

# Define path to store KPI data/files
# Use os.path.join for cross-platform compatibility
strpath = os.path.join("C:", os.sep, "KPI Calculation")

# open recent tree data on start
recent_entries_file = os.path.join(strpath, "recent_entries.csv")
# Create the directory if it doesn't exist
os.makedirs(strpath, exist_ok=True)

# create the main window
frmPercentage = tk.Tk()
frmPercentage.geometry("1280x720")
frmPercentage.title("10 to  9 IT Service Desk")
frmPercentage.configure(background="blue")
frmPercentage.resizable(False, False)

# add a logo at the top
from PIL import Image, ImageTk

# Load the image 
banner_image = Image.open("logobanner109.png")
banner_image = banner_image.resize((1280, 100), Image.LANCZOS)
banner_photo = ImageTk.PhotoImage(banner_image)

# Create label with image
logo_Label = tk.Label(frmPercentage, image=banner_photo, bg="blue")
logo_Label.image = banner_photo # keep a reference!
logo_Label.pack(side="top", fill="x")

# Consultant Name
lblName = tk.Label(frmPercentage, text="Consultant's Name:", width=20, height=2, bg="light blue")
lblName.place(x=175, y=160)

tbxName = tk.Entry(frmPercentage, bg="white")
tbxName.place(x=475, y=160, width=150, height=35)

# Labels for input fields
IblMaxNum = tk.Label(frmPercentage, text="Maximum Number:", width=20, height=2, bg="light blue")
IblMaxNum.place(x=175, y=230)

IblNumAch = tk.Label(frmPercentage, text="Number Achieved:", width=20, height=2, bg="light blue")
IblNumAch.place(x=175, y=300)

IblPercentage = tk.Label(frmPercentage, text="Percentage:", width=20, height=2, bg="light blue")
IblPercentage.place(x=175, y=370)

# Entry widgets for input
tbxMaxNum = tk.Entry(frmPercentage, bg="white")
tbxMaxNum.place(x=475, y=230, width=150, height=35)

tbxNumAch = tk.Entry(frmPercentage, bg="white")
tbxNumAch.place(x=475, y=300, width=150, height=35)

# Output label for percentage
IblPercentage2 = tk.Label(frmPercentage, text="", width=22, height=3, bg="white")
IblPercentage2.place(x=320, y=360)
IblPercentage2.place_forget() # hide at startup

# Recent entries Table 
columns = ("Name", "Percentage", "Date")
recent_tree = ttk.Treeview(frmPercentage, columns=columns, show="headings", height=15)

# Define table headings
recent_tree.heading("Name", text="Name")
recent_tree.heading("Percentage", text="Percentage")
recent_tree.heading("Date", text="Date")

# Define colum widths
recent_tree.column("Name", width=150)
recent_tree.column("Percentage", width=100)
recent_tree.column("Date", width=180)

# Place table on the right side of the window 
recent_tree.place(x=650, y=160, width=400, height=400)

# Define tags for green and red rows
recent_tree.tag_configure("green", background="light green")
recent_tree.tag_configure("red", background="light coral")

# load table data at start
import csv
if  os.path.exists(recent_entries_file):
        with open(recent_entries_file, newline="") as f:
            reader = csv.reader(f)
            next(reader, None) # SKIP Header
            for row in reader:
                if len(row)== 3:
                   name, percent, date_str = row
                   tag = "green" if float(percent.strip('%')) >=80 else "red"
                   recent_tree.insert("", "end", values=(name, percent, date_str), tags=(tag,))
                
            

# Function to calculate KPI 
def calculate_percentage():
    try:
         # Ensure consultant name is entered before calculating
        if not tbxName.get().strip():
            messagebox.showerror("Input Error", "Please enter a consultant's name.")
            return
        
        # Get the input data
        max_num = float(tbxMaxNum.get())
        num_achieved = float(tbxNumAch.get()) 

        # Prevent division by zero
        if max_num == 0:
            messagebox.showerror("Input Error", "Maximum Number cannot be zero!")
            return

        # Calculate the percentage
        percentage  = (num_achieved / max_num) * 100

        # Show label again
        IblPercentage2.place(x=320, y=370)

        # Bring the label to the front so it's on top of the button
        IblPercentage2.lift()


        # display the percentage 
        IblPercentage2.config(text=f"{percentage:.2f}%")

        # Show a red or green Label Based on KPI value 
        if percentage >= 80:
            IblPercentage2.config(bg="light green", text=f"{percentage:.2f}% WELL DONE!")
        else:
            IblPercentage2.config(bg="light coral", text=f"{percentage:.2f}% TERRIBLE!")
        
        # Save the data 
        save_data(max_num, num_achieved, percentage)

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers!")

# Function to save data 
def save_data(max_num, num_achieved, percentage):

    # Save the data to the KPI folder
    file_path = os.path.join(strpath, f"{tbxName.get()}.txt")
    with open(file_path, "w") as file:
        file.write(f"{tbxName.get()}\n")
        file.write(f"{max_num}\n")
        file.write(f"{num_achieved}\n")
        file.write(f"{percentage:.2f}%\n")

    # Add to recent entries table with color tag
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tag = "green" if percentage >= 80 else "red"
    recent_tree.insert("", "end", values=(tbxName.get(), f"{percentage:.2f}%", date_now), tags=(tag,))


    # Keep only the last 14 entries
    if len(recent_tree.get_children())> 14:
        first_item = recent_tree.get_children()[0]
        recent_tree.delete(first_item)
    
    # save table data to file
    with open(recent_entries_file, "w", newline="") as f:
        import csv
        writer = csv.writer(f)
        writer.writerow(["Name", "Percentage", "Date"])
        for row_id in recent_tree.get_children():
            writer.writerow(recent_tree.item(row_id)["values"])
                        

def Clear():
    tbxName.delete(0, 'end')
    tbxMaxNum.delete(0, 'end')
    tbxNumAch.delete(0, 'end')
    IblPercentage2.place_forget() # Hide it until next calculation

def openfile():
    Clear()
    strfilename = filedialog.askopenfilename(
        initialdir=strpath,
        title="Select Employees KPI File",
        filetypes=[("All Files", "*.*")]
    )
   
    if not strfilename:
        return

    

    count = 0
    if strfilename:
        with open(strfilename) as file:
            txtText = file.readlines()
            for line in txtText:
                count += 1
                if count == 1:
                    tbxName.insert(0, line.strip())
                elif count == 2:
                    tbxMaxNum.insert(0, line.strip())
                elif count == 3:
                    tbxNumAch.insert(0, line.strip())
                else:
                    break

# Button to trigger the calculation 
btnCalculate = tk.Button(frmPercentage, text="Calculate", width=20, height=2, command=calculate_percentage)
btnCalculate.place(x=475, y=370)

# Open button to load KPI file
btnOpen = tk.Button(frmPercentage, text="Open", command=openfile, width=20, height=2, bg="light blue", fg="black")
btnOpen.place(x=475, y=420)

# Button to exit the application 
btnExit = tk.Button(frmPercentage, text="Exit", width=20, height=2, command=frmPercentage.quit)
btnExit.place(x=320, y=500)


# Main event loop
frmPercentage.mainloop()