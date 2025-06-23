
import tkinter
from tkinter import messagebox
root=tkinter.Tk()
def bhai_submit():
    name = name_textbox.get()
    email = email_textbox.get()
    phone = phone_textbox.get()

    if name and email and phone:
        # File mein data save karo
        with open("students_data.txt", "a") as file:
            file.write(f"{name}, {email}, {phone}\n")

        # Success message
        messagebox.showinfo("Status", "Data submitted and saved!")
    else:
        messagebox.showwarning("Warning", "Please fill all the fields")

root.geometry("300x400")
root.configure(bg="#ADD8E6")
root.title("Student Registration Form")
name_label=tkinter.Label(root, text="enter the name")
name_label.pack(anchor=tkinter.W,padx=10)
name_textbox=tkinter.Entry(root, width=30)
name_textbox.pack(anchor=tkinter.W,padx=10)

email_label=tkinter.Label(root, text="enter the email")
email_label.pack(anchor=tkinter.W,padx=10)
email_textbox=tkinter.Entry(root, width=30)
email_textbox.pack(anchor=tkinter.W,padx=10)

phone_label=tkinter.Label(root, text="enter the phone")
phone_label.pack(anchor=tkinter.W,padx=10)
phone_textbox=tkinter.Entry(root, width=30)
phone_textbox.pack(anchor=tkinter.W,padx=10)

submit_button=tkinter.Button(root, text="submit",command=bhai_submit)
submit_button.pack()
root.mainloop()
