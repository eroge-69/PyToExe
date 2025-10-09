import os
from tkinter import *
from tkinter import messagebox
import smtplib
import email_password
import time, threading
import pymysql


def connection():
    global mycursor,conn

    try:
        conn = pymysql.connect(host='localhost', user='root', password='1234')
        mycursor = conn.cursor()
    except:
        messagebox.showerror('Error', 'Something went wrong, Please open MySQL app before running again')

    mycursor.execute('CREATE DATABASE IF NOT EXISTS inventory_data')
    mycursor.execute('USE inventory_data')
    mycursor.execute(
        'CREATE TABLE IF NOT EXISTS sup_data (invoice INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), contact VARCHAR(15), description VARCHAR(150))')
    mycursor.execute(
        'CREATE TABLE IF NOT EXISTS emp_data (empid INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), email VARCHAR('
        '50), gender VARCHAR(20), dob VARCHAR(30), contact VARCHAR(30), employment_type VARCHAR(50), education VARCHAR(50), '
        'work_shift VARCHAR(50), address VARCHAR(100), doj VARCHAR(30), salary VARCHAR(50), usertype VARCHAR(50), '
        'password VARCHAR(50))')
    mycursor.execute(
        'CREATE TABLE IF NOT EXISTS product_data (id INT AUTO_INCREMENT PRIMARY KEY NOT NULL, category VARCHAR(50), '
        'supplier VARCHAR(50), name VARCHAR(50), price VARCHAR(50), discount VARCHAR(50),price_after_discount VARCHAR(50), quantity VARCHAR(50), status VARCHAR(50))')
    mycursor.execute(
        'CREATE TABLE IF NOT EXISTS category_data (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), description VARCHAR(150))')

    mycursor.execute(
        'CREATE TABLE IF NOT EXISTS sales ('
        'sale_id INT AUTO_INCREMENT PRIMARY KEY, '
        'product_id INT, '
        'product_name VARCHAR(100),'
        'quantity_sold INT, '
        'sale_date DATE, '
        'sale_amount DECIMAL(10, 2), '
        'FOREIGN KEY (product_id) REFERENCES product_data(id))'
    )
    mycursor.execute("""
                                CREATE TABLE IF NOT EXISTS settings (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    tax_percentage FLOAT
                                )
                            """)


def email_thread(to_, name):
    t = threading.Thread(target=lambda: send_email(to_, name))
    t.setDaemon = True
    t.start()


def send_email(to_, name):
    global otp
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    email_ = email_password.myemail
    password_ = email_password.mypassword
    s.login(email_, password_)
    otp = int(time.strftime('%H%M%S')) + int(time.strftime('%S'))
    subj = 'StockApp- One Time Password'
    msg = f'Dear {name},\n\nYour OTP is {otp}.\n\nWith Regards,\nStockApp Team'
    msg = f'Subject:{subj}\n\n{msg}'
    s.sendmail(email_, to_, msg)
    check = s.ehlo()
    if check[0] == 250:
        return 'success'
    else:
        return 'fail'


def forget_password():
    def verify():
        if otpEntry.get() == str(otp):
            submitButton.config(state=NORMAL)
            verifyButton.config(state=DISABLED)
            messagebox.showinfo('Success', 'Verification is successful', parent=forget_window)

        else:
            messagebox.showerror('Error', 'Invalid OTP, try again', parent=forget_window)

    def submit():
        if newpassEntry.get() == '' or confirmEntry.get() == '':
            messagebox.showerror('Error', 'All fields are required', parent=forget_window)
        elif newpassEntry.get() != confirmEntry.get():
            messagebox.showerror('Error', 'Password mismatch', parent=forget_window)
        else:

            mycursor.execute('UPDATE emp_data SET password=%s WHERE empid=%s', (newpassEntry.get(), empIdEntry.get()))
            conn.commit()
            messagebox.showinfo('Success', 'Password is changed', parent=forget_window)
            forget_window.destroy()

    if empIdEntry.get() == '':
        messagebox.showerror('Error', 'Please enter employee id')
    else:

        mycursor.execute('SELECT email from emp_data WHERE empid=%s',
                         (empIdEntry.get(),))
        email = mycursor.fetchone()
        if email == None:
            messagebox.showerror('Error', 'Invalid employee id, try again')
        else:
            mycursor.execute('SELECT name from emp_data WHERE empid=%s', (empIdEntry.get(),))
            name = mycursor.fetchone()
            name = name[0]
            check = email_thread(email, name)
            if check == 'fail':
                messagebox.showerror('Error', 'Connection error, try again')
            else:

                forget_window = Toplevel()
                forget_window.grab_set()
                forget_window.title('Change Password')
                forget_window.config(bg='white')
                forgetImage = PhotoImage(file='forgot-password.png')
                forgetLogoLabel = Label(forget_window, image=forgetImage, bg='white')
                forgetLogoLabel.grid(row=0, column=0, pady=(10, 20))
                otpLabel = Label(forget_window, text='Check your Email for the OTP', font=('times new roman', 14),
                                 bg='white')
                otpLabel.grid(row=1, column=0, padx=50)
                otpEntry = Entry(forget_window, font=('times new roman', 14), bd=2)
                otpEntry.grid(row=2, column=0, padx=50, pady=(5, 0))

                verifyButton = Button(forget_window, text='Verify', font=('times new roman', 14), width=10,
                                      bg='#FDB441',
                                      cursor='hand2',

                                      command=verify)
                verifyButton.grid(row=3, column=0, pady=(20, 30), padx=50)

                newpassLabel = Label(forget_window, text='New Password', font=('times new roman', 14), bg='white')
                newpassLabel.grid(row=4, column=0, padx=50)
                newpassEntry = Entry(forget_window, font=('times new roman', 14), bd=2, show='*')
                newpassEntry.grid(row=5, column=0, padx=50, pady=(5, 10))

                confirmLabel = Label(forget_window, text='Confirm Password', font=('times new roman', 14),
                                     bg='white')
                confirmLabel.grid(row=6, column=0, padx=50)
                confirmEntry = Entry(forget_window, font=('times new roman', 14), bd=2, show='*')
                confirmEntry.grid(row=7, column=0, padx=50, pady=(5, 0))

                submitButton = Button(forget_window, text='Submit', font=('times new roman', 14), width=10,
                                      bg='#01CCF6',
                                      cursor='hand2',

                                      command=submit, state=DISABLED)
                submitButton.grid(row=8, column=0, pady=(20, 30), padx=50)

                forget_window.mainloop()


def check_empty_emp_data():
    mycursor.execute('SELECT COUNT(*) FROM emp_data')
    count = mycursor.fetchone()[0]
    return count == 0


def login(event=None):
    if empIdEntry.get() == '' or passwordEntry.get() == '':
        messagebox.showerror('Error', 'Fields cannot be empty')
    else:
        if check_empty_emp_data():
            # Use default credentials
            if empIdEntry.get() == '1' and passwordEntry.get() == '1234':
                messagebox.showinfo('Success', 'Login is successful')
                os.environ['EMP_ID'] = empIdEntry.get()
                root.destroy()
                os.system('python main.py')
            else:
                messagebox.showerror('Error',
                                     'No employee data found. Please log in using the default admin username and password.')
        else:
            mycursor.execute('SELECT usertype from emp_data WHERE empid=%s AND password=%s',
                             (empIdEntry.get(), passwordEntry.get()))
            user = mycursor.fetchone()
            if user == None:
                messagebox.showerror('Error', 'Invalid Employee Id or Password')
            else:
                messagebox.showinfo('Success', 'Login is successful')
                os.environ['EMP_ID'] = empIdEntry.get()
                root.destroy()
                if user[0] == 'Admin':
                    os.system('python main.py')
                else:
                    os.system('python billing.py')


logo_index = 0


def animate():
    global logo_index
    logoLabel.config(image=login_logos[logo_index])
    logo_index = (logo_index + 1) % len(login_logos)  # Move to the next image, wrapping around
    logoLabel.after(5000, animate)  # Schedule the next animation frame


def toggle_password():
    if passwordEntry.cget('show') == '*':
        passwordEntry.config(show='')
        toggle_button.config(image=open_eye_img)
    else:
        passwordEntry.config(show='*')
        toggle_button.config(image=close_eye_img)


root = Tk()
root.geometry('1000x600+50+50')
root.resizable(0, 0)
root.config(bg='white')
root.title('Login')
login_logos = [
    PhotoImage(file='login_logo1.png'),
    PhotoImage(file='login_logo2.png'),
    PhotoImage(file='login_logo3.png'),
    PhotoImage(file='login_logo4.png'),
    PhotoImage(file='login_logo5.png'),
    PhotoImage(file='login_logo6.png'),
    PhotoImage(file='login_logo7.png')
]
title = Label(root, text='Inventory Management System', font=('times new roman', 40), bg='#5097E0', fg='white')
title.place(x=0, y=0, relwidth=1)
logoLabel = Label(root, bg='white')
logoLabel.place(x=20, y=100)
rightFrame = Frame(root, bg='lightgray', height=500, width=400)
rightFrame.place(x=620, y=100)
logo = PhotoImage(file='login.png')
employeelogoLabel = Label(rightFrame, image=logo, bg='lightgray', bd=0)
employeelogoLabel.grid(row=0, column=0, pady=20)

empIdLabel = Label(rightFrame, text='Employee Id', font=('times new roman', 15), bg='lightgray')
empIdLabel.grid(row=1, column=0, sticky='w', padx=50)
empIdEntry = Entry(rightFrame, font=('times new roman', 15))
empIdEntry.grid(row=2, column=0, sticky='w', padx=50)

passwordLabel = Label(rightFrame, text='Password', font=('times new roman', 15), bg='lightgray')
passwordLabel.grid(row=3, column=0, sticky='w', padx=50, pady=(10, 0))

passwordEntry = Entry(rightFrame, font=('times new roman', 15), show='*')
passwordEntry.grid(row=4, column=0, sticky='w', padx=(50, 0))

open_eye_img = PhotoImage(file='open_eye.png')
close_eye_img = PhotoImage(file='close_eye.png')

toggle_button = Button(rightFrame, image=close_eye_img, command=toggle_password, bd=0, bg='lightgray',
                       activebackground='lightgray')
toggle_button.place(x=260, y=295)

forgetpassButton = Button(rightFrame, text='Forgot Password?', font=('times new roman', 12), bd=0, fg='#5097E0',
                          cursor='hand2', bg='lightgray', activebackground='lightgray',
                          command=forget_password)
forgetpassButton.grid(row=5, column=0, sticky='w', padx=45)

loginButton = Button(rightFrame, text='Login', font=('times new roman', 14), width=20, bg='#5097E0', cursor='hand2',
                     fg='white',
                     command=login)
loginButton.grid(row=6, column=0, pady=(20, 30), padx=50)

animate()

connection()
# Bind the Enter key to the login function
root.bind('<Return>', login)
root.mainloop()
