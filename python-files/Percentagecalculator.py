from tkinter import *

def main():
    global window2, entries
    window.withdraw()  
    window2 = Toplevel(window) 
    window2.title("Percentage Calculator")
    window2.config(bg="#00ff00")
    window2.geometry("1300x1300")
    entries = {}

    Label(window2, text="Enter Names: ", font=("Impact", 30), bg="#00ff00").grid(column=0, row=0, columnspan=2)

    for i in range(1, 9):
        Label(window2, text=f"Subject number {i}: ", font=("Impact", 30), bg="#00ff00").grid(column=0, row=i)
        entry = Entry(window2, font=("Impact", 25))
        entry.grid(column=1, row=i)
        entries[f"subj{i}"] = entry  

    Button(window2, command=wind3, text="Continue", font=("Impact", 24), fg="red", bg="blue",
           activebackground="red", activeforeground="blue").grid(column=0, row=9, columnspan=2)


def wind3():
    global window2, window3, entries, obtained_entries, total_entries, result_label
    window2.withdraw() 
    window3 = Toplevel(window2)  
    window3.title("Percentage Calculator")
    window3.config(bg="#00ff00")
    
    window3.geometry("800x600")

    subjects = [entries[f"subj{i}"].get() for i in range(1, 9) if entries[f"subj{i}"].get().strip()]

    
    Label(window3, text="Subject", font=("Impact", 28, "bold"), fg="Black", bg="#00ff00").grid(column=0, row=0, padx=10, pady=10)
    Label(window3, text="Obtained Marks", font=("Impact", 28, "bold"), fg="Black", bg="#00ff00").grid(column=1, row=0, padx=10, pady=10)
    Label(window3, text="Total Marks", font=("Impact", 28, "bold"), fg="Black", bg="#00ff00").grid(column=2, row=0, padx=10, pady=10)

    obtained_entries = []
    total_entries = []

    
    for idx, subject in enumerate(subjects, start=1):
        Label(window3, text=subject, font=("Impact", 28), fg="Black", bg="#00ff00").grid(column=0, row=idx, padx=10, pady=5, sticky=W)

        obtained_entry = Entry(window3, font=("Impact", 23), width=10)
        obtained_entry.grid(column=1, row=idx, padx=10, pady=5)
        obtained_entries.append(obtained_entry)

        total_entry = Entry(window3, font=("Impact", 23), width=10)
        total_entry.grid(column=2, row=idx, padx=10, pady=5)
        total_entries.append(total_entry)

    
    submit_button = Button(window3, text="Submit", font=("Impact", 24), fg="red", bg="blue",
                           activebackground="red", activeforeground="blue",
                           command=lambda: calculate_percentage(window3, obtained_entries, total_entries))
    submit_button.grid(column=0, row=len(subjects)+1, columnspan=3, pady=20)

    
    result_label = Label(window3, text="", font=("Impact", 28), fg="Black", bg="#00ff00")
    result_label.grid(column=0, row=len(subjects)+2, columnspan=3, pady=20)


def calculate_percentage(window3, obtained_entries, total_entries):
    try:
        total_obtained = 0
        total_max = 0

        for obt_entry, tot_entry in zip(obtained_entries, total_entries):
            obtained = obt_entry.get().strip()
            total = tot_entry.get().strip()

            if not obtained or not total:
                
                continue

            obtained_val = float(obtained)
            total_val = float(total)

            if obtained_val > total_val:
                result_label.config(text="Error: Obtained marks cannot exceed total marks.")
                return

            total_obtained += obtained_val
            total_max += total_val

        if total_max == 0:
            result_label.config(text="Error: Total marks must be greater than zero.")
            return

        percentage = (total_obtained / total_max) * 100
        result_label.config(text=f"Total Percentage: {percentage:.2f}%")
    except ValueError:
        result_label.config(text="Error: Please enter valid numeric values.")


window = Tk()
window.geometry("1200x600")
window.title("Percentage Calculator")
window.config(bg="#00ff00")

Label(window, text="Instructions", font=("Impact", 30), bg="#00ff00").pack(side=TOP)
Label(window, text="Enter the names of the subject only you need, No need to fill the rest of the names.", 
      font=("Impact", 25), bg="#00ff00").pack()

Button(window, command=main, text="Continue", font=("Impact", 24), fg="red", bg="blue",
       activebackground="red", activeforeground="blue").pack()

window.mainloop()

