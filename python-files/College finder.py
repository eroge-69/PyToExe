import tkinter as tk
from tkinter import messagebox



def check_number():
    """
    Retrieves the number from the entry, performs checks using if-elif-else
    statements, and displays the result in a label.
    """
    try:
        number = int(entry.get())
        result_text = ""

        # First if-elif-else statement
        if number < 6246:
            result_text += "GMC Bhavnagar Round 1.\n"
        elif number < 9920:
            result_text += "GMC Bhavnagar Round 2\n"
        elif number < 11255:
            result_text += "GMC Bhavnagar Round 3 \n"

        # Second if-elif-else statement
        if number < 3080:
            result_text += "GMC Surat Round 1\n"
        elif number <  6419:
            result_text += " GMC Surat Round 2 \n"
            
        elif number < 6038:
            result_textv += "GMC Surat Round 3 \n"
            
        elif number < 9920:
            result_text += "GMC Surat Round 4\n"

        # Third if-elif-else statement
        if number < 2251:
            result_text += "GMC Baroda Round 1 \n"
        elif number < 2930:
            result_text += "GMC Baroda Round 2 \n"
        elif number < 3432:
            result_text += " GMC Baroda Round 3 \n"
      

        # Fourth if-elif-else statement
        if number < 5362:
            result_text += "MP Shah GMC Jamnagar Round 1\n"
        elif number < 9360:
            result_text += "MP Shah GMC Jamnagar Round 2\n"
        elif number < 9902:
            result_text += "MP Shah GMC Jamnagar Round 3 \n"

        # Fifth if-elif-else statement
        if number < 3922:
            result_text += "Pt DDU MC Rajkot Round 1\n"
        elif number < 8050:
            result_text += "Lt DDU MC Rajkot Round 2 \n"
        elif number <  7638:
            result_text += "Pt DDU MC Rajkot Round 3 \n"

        result_label.config(text=result_text)

    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid integer.")

# Create the main window
root = tk.Tk()
root.title("Integer Checker")
root.geometry("400x300")

# Create and place widgets
instruction_label = tk.Label(root, text="Enter your AIR:")
instruction_label.pack(pady=10)

entry = tk.Entry(root, width=30)
entry.pack(pady=5)

check_button = tk.Button(root, text="Check possible college (s)", command=check_number)
check_button.pack(pady=10)

result_label = tk.Label(root, text="", justify=tk.LEFT)
result_label.pack(pady=10)


#Information about College 

def check_info():
    if entry2.get() == "GMC Bhavnagar":
        result_label2.config(text ='Established: 1995\n Total fees: 1.13 L ')
        
    if entry2.get() == "GMC Surat":
        result_label2.config(text = ' Established: 1964 \n Total fees: 1.13 L')
        
    if entry2.get()== "GMC Baroda":
        result_label2.config(text = 'Established: 1949\n Total fees: 1.13L')
        
    if entry2.get()== "MP Shah GMC Jamnagar":
        result_label2.config(text = 'Established: 1954\n Total fees: 1.13L')        

    if entry2.get()== "Pt DDU MC Rajkot":
        result_label2.config(text = 'Established: 1995\n Total fees: 1.13L')

instruction_label2 = tk.Label(root, text = 'Enter your college name')
instruction_label2.pack(pady =10)

entry2 = tk.Entry(root, width=30)
entry2.pack(pady=25, side = 'top')


check_button2 = tk.Button(root, text="Check info about  possible college (s)", command=check_info)
check_button2.pack(pady=10)

result_label2 = tk.Label(root, text="", justify=tk.LEFT)
result_label2.pack(pady=10)

# Run the application
root.mainloop()