import tkinter as tk
from tkinter import messagebox, END

valid_users = {
    "Andreas": "NEA",
    "q": "q"
}

show = False

def validate_login():
    userid = username_entry.get()
    password = password_entry.get()
    if userid in valid_users and valid_users[userid] == password:
        messagebox.showinfo("Login Successful", "Welcome")
        hide_login_widgets()
        main_menu()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")

def show_pass():
    global show
    show = not show
    if show:
        password_entry.config(show="")
        show_chars.config(text="Hide")
    else:
        password_entry.config(show="*")
        show_chars.config(text="Show")

def create_login_widgets():
    global username_label, username_entry
    global password_label, password_entry
    global show_chars, login_button

    username_label = tk.Label(root, text="User ID:", font=label_font)
    username_entry = tk.Entry(root, font=entry_font, width=18)
    password_label = tk.Label(root, text="Password:", font=label_font)
    password_entry = tk.Entry(root, show="*", font=entry_font, width=18)
    show_chars = tk.Button(root, text="Show", font=login_font, command=show_pass)
    login_button = tk.Button(root, text="Login", font=login_font, command=validate_login)
    

def hide_login_widgets():
    username_label.place_forget()
    username_entry.place_forget()
    password_label.place_forget()
    password_entry.place_forget()
    show_chars.place_forget()
    login_button.place_forget()
    username_entry.delete(0, END)
    password_entry.delete(0, END)
    

def login_main():
    create_login_widgets()
    show_login_widgets()

def main_menu():
    global create_survey

    create_survey = tk.Button(root, text="Make Survey", font=label_font)
    create_survey.place(x=550, y=300)
    logout = tk.Button(root, text="LOGOUT", font=login_font, command=show_login_widgets)
    logout.place(x=1170, y=670)

def show_login_widgets():
    global create_survey

    try:    
        create_survey.place_forget()
    except NameError:
        pass
    username_label.place(x=430, y=300)
    username_entry.place(x=530, y=300, height=36)
    password_label.place(x=400, y=350)
    password_entry.place(x=530, y=350, height=36)
    show_chars.place(x=790, y=350, height=36)
    login_button.place(x=550, y=400)

root = tk.Tk()
root.title("Student Survey Maker")
root.overrideredirect(True)
root.geometry("{0}x{1}+0+0".format(root.winfo_screenwidth(), root.winfo_screenheight()))

title = tk.Text(root, height=2, width=32)
title.place(x=500, y=30)
title.tag_configure('bold_italics', font=('Arial', 18, 'bold', 'italic'))
title.insert(tk.END, "Student Survey Maker", 'bold_italics')
title.config(state='disabled')

label_font = ('Arial', 18, 'bold')
login_font = ('Arial', 15, 'bold')
entry_font = ('Arial', 18)

login_main()

exit_button = tk.Button(root, text="EXIT", font=login_font, command=root.destroy)
exit_button.place(x=1210, y=10)

root.mainloop()