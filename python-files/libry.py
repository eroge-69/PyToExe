from tkinter import *
from tkinter import ttk
import tkinter.messagebox as messagebox
import pyodbc
from PIL import Image, ImageTk


try:
    conn_str=(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'r'DBQ=E:\New folder (2)\libry.accdb;')
    # Establish the connection+
    Conn = pyodbc.connect(conn_str)
    print('Database connected successfully')

    # Create cursor object to execute SQL commands
    cursor = Conn.cursor()

except pyodbc.Error as e:
    print('Connection error:', e)

def insert():
    # Get data from entry fields
    book_name = bkname.get()
    writer = bkwri.get()
    price = bkpr.get()
    isbn = bkisb.get()
    date = bkdate.get()
    book_num = bknum.get()
    company = bkcom.get()
    book_type_num = bktynum.get()
    short_note = stnot.get("1.0", END).strip()  # Get all text from Text widget
    book_type = bktyp.get()

    # Validate mandatory fields (optional, you can skip or customize)
    if not book_name or not writer:
        messagebox.showwarning("Input Error", "Book Name and Writer are required.")
        return

    try:
        # Insert into Access database
        cursor.execute("""
            INSERT INTO libry (bkname, bkwri, bkpr, bkisb, bkdate, bknum, bkcom, bktynum, stnot, bktyp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (book_name, writer, price, isbn, date, book_num, company, book_type_num, short_note, book_type))

        Conn.commit()  # Commit changes to the database
        messagebox.showinfo("Success", "Record inserted successfully!")
        display()  # Refresh the Treeview to show the new record

        # Clear the fields after insertion
        bkname.delete(0, END)
        bkwri.delete(0, END)
        bkpr.delete(0, END)
        bkisb.delete(0, END)
        bkdate.delete(0, END)
        bknum.delete(0, END)
        bkcom.delete(0, END)
        bktynum.delete(0, END)
        stnot.delete("1.0", END)
        bktyp.set('')

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error inserting data:\n{e}")

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"An error occurred: {e}")

        display()
    
    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error updating record:\n{e}")

    # Get the selected item in the Treeview
    selected_item = memrecords_r.selection()
    
    if not selected_item:
        messagebox.showwarning("Selection Needed", "Please select a record to update.")
        return
    
    try:
        # Get updated values from entry boxes
        new_bkname = bkname.get()
        new_bkwri = bkwri.get()
        new_bkpr = bkpr.get()
        new_bkisb = bkisb.get()
        new_bkdate = bkdate.get()
        new_bknum = bknum.get()
        new_bkcom = bkcom.get()
        new_bktynum = bktynum.get()
        new_stnot = stnot.get("1.0", END).strip()
        new_bktyp = bktyp.get()

        # Get the old record from Treeview
        record = memrecords_r.item(selected_item[0], 'values')
        old_bkname = record[0]   # using Book Name as identifier

        # Update query (⚠ safer to use ISBN instead of bkname if possible)
        cursor.execute("""
            UPDATE libry
            SET bkname=?, bkwri=?, bkpr=?, bkisb=?, bkdate=?, bknum=?, bkcom=?, bktynum=?, stnot=?, bktyp=?
            WHERE bkname=?
        """, (new_bkname, new_bkwri, new_bkpr, new_bkisb, new_bkdate, new_bknum, new_bkcom, new_bktynum, new_stnot, new_bktyp, old_bkname))
        
        Conn.commit()

        # Refresh Treeview
        display()

        messagebox.showinfo("Success", "Record updated successfully!")

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error updating record:\n{e}")

    book_name = bkname.get()  # Unique key to find the record

    if book_name == "":
        messagebox.showwarning("Input Error", "Please enter the Book Name to update")
        return

    try:
        # Update the database record
        cursor.execute("""
            UPDATE libry SET 
                bkwri=?,
                bkpr=?,
                bkisb=?,
                bkdate=?,
                bknum=?,
                bkcom=?,
                bktynum=?,
                stnot=?,
                bktyp=?
            WHERE bkname=?
        """, (
            bkwri.get(),
            bkpr.get(),
            bkisb.get(),
            bkdate.get(),
            bknum.get(),
            bkcom.get(),
            bktynum.get(),
            stnot.get('1.0', END).strip(),
            bktyp.get(),
            book_name
        ))
        
        Conn.commit()  # Save changes to database
        messagebox.showinfo("Success", f"Record for '{book_name}' updated successfully!")
        display()  # Refresh the Treeview

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error updating data: {e}")


def display():
    # Clear the Treeview first to avoid duplicates
    for item in memrecords_r.get_children():
        memrecords_r.delete(item)

    try:
        cursor.execute("SELECT bkname, bkwri, bkpr, bkisb, bkdate, bknum, bkcom, bktynum, stnot, bktyp FROM libry")  # replace 'books' with your table name
        rows = cursor.fetchall()

        for row in rows:
            memrecords_r.insert('', END, values=row)

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", str(e))

        
def search():
    bk_number = bknum.get()  # get the book number from entry
    if not bk_number:
        messagebox.showwarning("Input Error", "Please enter a Book Number to search")
        return

    try:
        # Fetch data for the given bknum
        cursor.execute("SELECT * FROM libry WHERE bknum=?", (bk_number,))
        row = cursor.fetchone()
        
        if row:
            # Assuming your table columns match the entry order
            bkname.delete(0, END)
            bkname.insert(0, row.bkname)

            bkwri.delete(0, END)
            bkwri.insert(0, row.bkwri)

            bkpr.delete(0, END)
            bkpr.insert(0, row.bkpr)

            bkisb.delete(0, END)
            bkisb.insert(0, row.bkisb)

            bkdate.delete(0, END)
            bkdate.insert(0, row.bkdate)

            bkcom.delete(0, END)
            bkcom.insert(0, row.bkcom)

            bktynum.delete(0, END)
            bktynum.insert(0, row.bktynum)

            stnot.delete('1.0', END)
            stnot.insert(END, row.stnot)

            bktyp.set(row.bktyp)
        else:
            messagebox.showinfo("Not Found", f"No book found with Book Number: {bk_number}")

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error searching data: {e}")



def delete():
    book_name = bkname.get()  # Use the Book Name as the key

    if book_name == "":
        messagebox.showwarning("Input Error", "Please enter the Book Name to delete")
        return

    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{book_name}'?")
    if not confirm:
        return

    try:
        # Delete the record from the database
        cursor.execute("DELETE FROM libry WHERE bkname=?", (book_name,))
        Conn.commit()  # Save changes
        messagebox.showinfo("Deleted", f"Record for '{book_name}' deleted successfully!")

        # Clear entry boxes
        bkname.delete(0, END)
        bkwri.delete(0, END)
        bkpr.delete(0, END)
        bkisb.delete(0, END)
        bkdate.delete(0, END)
        bknum.delete(0, END)
        bkcom.delete(0, END)
        bktynum.delete(0, END)
        stnot.delete('1.0', END)
        bktyp.set('')

        display()  # Refresh the Treeview

    except pyodbc.Error as e:
        messagebox.showerror("Database Error", f"Error deleting data: {e}")
        
#======================join libry window
     
def open_new_window():
    
    try:
        
        conn_str=(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'r'DBQ=E:\New folder (2)\libry.accdb;')
        # Establish the connection+
        Conn = pyodbc.connect(conn_str)
        print('Database connected successfully')
        # Create cursor object to execute SQL commands
        cursor = Conn.cursor()
    except pyodbc.Error as e:
        print('Connection error:', e)
        
    def update1():
        try:
            # Get values from the form
            student_name = name.get()
            adm_number = adnum.get()
            student_id = idnum.get()
            reg_date = rejdate.get()
            student_address = addres.get()
            student_age = age.get()

            # Check if Admission Number is provided
            if adm_number == "":
                messagebox.showwarning("Input Error", "Admission Number is required to update a record!")
                return

            # Update the record in database
            cursor.execute("""
                UPDATE register
                SET name = ?, idnum = ?, rejdate = ?, addres = ?, age = ?
                WHERE adnum = ?
            """, (student_name, student_id, reg_date, student_address, student_age, adm_number))

            Conn.commit()  # Save changes


        except pyodbc.Error as e:
            print("Database error:", e)
            
    def delete1():
        try:
            adm_number = adnum.get()  # Get Admission Number from entry box

            if adm_number == "":
                messagebox.showwarning("Input Error", "Please enter an Admission Number to delete!")
                return

            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete record with Admission Number {adm_number}?")
            if not confirm:
                return

            # Execute delete query
            cursor.execute("DELETE FROM register WHERE adnum = ?", (adm_number,))
            Conn.commit()

            messagebox.showinfo("Success", "Record deleted successfully!")

            # Clear form and refresh table
            clear()
            display1()

        except pyodbc.Error as e:
            print("Database error:", e)
            messagebox.showerror("Error", f"Could not delete data: {e}")


    def display1():
        try:
            # Clear existing records in Treeview
            for row in memrecords_r.get_children():
                memrecords_r.delete(row)

            # Fetch data from the database
            cursor.execute("SELECT name, adnum, idnum, rejdate, addres, age FROM register")
            rows = cursor.fetchall()

            # Insert data into the Treeview
            for row in rows:
                memrecords_r.insert('', END, values=row)

        except pyodbc.Error as e:
            print("Database error:", e)
            messagebox.showerror("Error", f"Could not fetch data: {e}")
    def search1():
        try:
            search_adnum = adnum1.get()  # Get Admission Number ONLY from search box

            if search_adnum == "":
                messagebox.showwarning("Input Error", "Please enter an Admission Number to search!")
                return

            # Query the database
            cursor.execute("""
                SELECT name, idnum, rejdate, addres, age, adnum
                FROM register
                WHERE adnum = ?
            """, (search_adnum,))
            row = cursor.fetchone()

            if row:
                # Insert record values into entry boxes
                name.delete(0, END)
                name.insert(0, row[0])

                idnum.delete(0, END)
                idnum.insert(0, row[1])

                rejdate.delete(0, END)
                rejdate.insert(0, row[2])

                addres.delete(0, END)
                addres.insert(0, row[3])

                age.delete(0, END)
                age.insert(0, row[4])

                adnum.delete(0, END)
                adnum.insert(0, row[5])  # Admission Number goes into adnum field

            else:
                messagebox.showinfo("Not Found", "No record found with this Admission Number.")
                clear()

        except pyodbc.Error as e:
            print("Database error:", e)
            messagebox.showerror("Error", f"Could not search data: {e}")

    def exit1():
        join_win.destroy()
        
    def clear1():
        name.delete(0, END)
        adnum.delete(0, END)
        adnum1.delete(0, END)
        idnum.delete(0, END)
        rejdate.delete(0, END)
        addres.delete(0, END)
        age.delete(0, END)
        
    def insert1():
        try:
            # Get values from the form
            student_name = name.get()
            adm_number = adnum.get()
            student_id = idnum.get()
            reg_date = rejdate.get()
            student_address = addres.get()
            student_age = age.get()

            # Basic validation (optional)
            if student_name == "" or adm_number == "" or student_id == "":
                messagebox.showwarning("Input Error", "Name, Admission Number, and ID are required!")
                return

            
            cursor.execute("""
                INSERT INTO register (name, adnum, idnum, rejdate, addres, age)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_name, adm_number, student_id, reg_date, student_address, student_age))

            Conn.commit()  # Save changes
            messagebox.showinfo("Success", "Record inserted successfully!")

            # Clear the form after insertion
            clear()

            # Refresh the Treeview to show new data
            display()

        except pyodbc.Error as e:
            print("Database error:", e)
            messagebox.showerror("Error", f"Could not insert data: {e}")


    #===intar face
    join_win = Toplevel(win) 
    join_win.title("Register")
    join_win.geometry("800x600+200+100")
    join_win.configure(bg="#0e3257")
    join_win.resizable(0, 0)
    #==frame
    Lframe = Frame(join_win, bd=5, width=800, height=600, relief=RIDGE, bg="#298514")
    Lframe.grid(column=0, row=0)
    viewframe1 = Frame(Lframe, bd=5, width=790, height=230, relief=RIDGE, bg="#643EAB")
    viewframe1.place(x=0, y=360)
    
    #===entry
    name = Entry(Lframe, font='none 12', width=20)
    name.place(x=130, y=100)    
    adnum= Entry(Lframe, font='none 13', width=20)
    adnum.place(x=430, y=260)
    idnum= Entry(Lframe, font='none 12', width=20)
    idnum.place(x=130, y=180)
    rejdate = Entry(Lframe, font='none 12', width=20)
    rejdate.place(x=130, y=260)
    adnum1= Entry(Lframe, font='none 13', width=10)
    adnum1.place(x=590, y=12)   
    addres = Entry(Lframe, font='none 12', width=20)
    addres.place(x=430, y=180)
    age= Spinbox(Lframe, from_=1, to=100, font="none 12", width=15)
    age.place(x=430, y=100)
    
    #===lables
    
    Label(Lframe, text='Rejister now', font='none 20', bg="#298514", fg="#FFFFFF").place(x=300, y=10)
    Label(Lframe, text='  ------------', font='none 20', bg="#298514", fg="#2F0750").place(x=300, y=40)
    
    Label(Lframe, text='Addmn', font='none 12', bg="#298514", fg="#2F0750").place(x=360, y=260)
    Label(Lframe, text='number', font='none 12', bg="#298514", fg="#2F0750").place(x=360, y=285)
    Label(Lframe, text='Name', font='none 12', bg="#298514", fg="#2F0750").place(x=10, y=100)
    Label(Lframe, text='ID number or', font='none 12', bg="#298514", fg="#2F0750").place(x=10, y=180)
    Label(Lframe, text=' Student', font='none 12', bg="#298514", fg="#2F0750").place(x=10, y=210)    
    Label(Lframe, text='Age', font='none 12', bg="#298514", fg="#2F0750").place(x=360, y=100)
    Label(Lframe, text='Date of regis', font='none 12', bg="#298514", fg="#2F0750").place(x=10, y=260)
    Label(Lframe, text='Addres', font='none 12', bg="#298514", fg="#2F0750").place(x=360, y=180)
    
    
    # ==== Treeview 
    scroll_y_r = Scrollbar(viewframe1, orient=VERTICAL)

    memrecords_r = ttk.Treeview(
        viewframe1,
        height=15,
        columns=('name', 'adnum', 'idnum', 'rejdate', 'addres', 'age'),
        yscrollcommand=scroll_y_r.set
    )

    scroll_y_r.pack(side=RIGHT, fill=Y)

    memrecords_r.heading('name', text=' Name')
    memrecords_r.heading('adnum', text='Addmim Num')
    memrecords_r.heading('idnum', text='ID Num')
    memrecords_r.heading('rejdate', text='Rejis Date')
    memrecords_r.heading('addres', text='Addres')
    memrecords_r.heading('age', text='Age')

    memrecords_r['show'] = 'headings'

    memrecords_r.column('name', width=190, anchor=W)
    memrecords_r.column('adnum', width=100, anchor=W)
    memrecords_r.column('idnum', width=100, anchor=W)
    memrecords_r.column('rejdate', width=100, anchor=W)
    memrecords_r.column('addres', width=175, anchor=W)
    memrecords_r.column('age', width=100, anchor=W)
    memrecords_r.pack(fill=BOTH, expand=1)
    

    #===button
    Button(Lframe, text="Insert", font='none 12 bold',bg="#1D431E", fg="white", width=10,command=insert1).place(x=670, y=120)
    Button(Lframe, text="Display", font='none 12 bold',bg="#4B2551", fg="white", width=10,command=display1).place(x=670, y=160)
    Button(Lframe, text="Update", font='none 12 bold',bg="#1A3E51", fg="white", width=10,command=update1).place(x=670, y=200)
    Button(Lframe, text="Delete", font='none 12 bold',bg="#481e59", fg="white", width=10,command=delete1).place(x=670, y=240)
    Button(Lframe, text="Clear", font='none 12 bold',bg="#572927", fg="white", width=10,command=clear1).place(x=670, y=280)
    Button(Lframe, text="Exit", font='none 12 bold',bg="#421A37", fg="white", width=10, command=exit1).place(x=670, y=320)
    btn_img = Image.open("E:/New folder (2)/112.PNG")
    btn_img = btn_img.resize((30, 30))
    btn_photo = ImageTk.PhotoImage(btn_img)   
    Button(Lframe, image=btn_photo, text=" Search", compound=LEFT,
        font='none 12 bold', bg="#362C81", fg="white", width=90,height=20, command=search1).place(x=690, y=10)

    #
    Button(join_win, text="Close", font="none 12 bold", bg="#6A4760", fg="white", command=join_win.destroy).pack(pady=20)

#============================= send window    

def send_window():
    
    try:
        
        conn_str=(r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'r'DBQ=E:\New folder (2)\libry.accdb;')
        # Establish the connection+
        Conn = pyodbc.connect(conn_str)
        print('Database connected successfully')
        # Create cursor object to execute SQL commands
        cursor = Conn.cursor()
    except pyodbc.Error as e:
        print('Connection error:', e)
        
    def display_send_data():
        try:
            conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                        r'DBQ=E:\New folder (2)\libry.accdb;')
            Conn = pyodbc.connect(conn_str)
            cursor = Conn.cursor()
            cursor.execute("SELECT sendate, sentime, adnum, bknum, offedate, offertime FROM resew") 
            rows = cursor.fetchall()

            # Clear existing data in Treeview
            memrecords_r.delete(*memrecords_r.get_children())

            # Insert fetched data into Treeview
            for row in rows:
                memrecords_r.insert('', 'end', values=row)

            Conn.close()
        except pyodbc.Error as e:
            print("Database error:", e)

    def insert_send_data():
        try:
            # Get data from entry widgets
            s_date = sendate.get()
            s_time = sentime.get()
            admission = adnum.get()
            book_num = bknum.get()
            offer_date = offedate.get()
            offer_time = offertime.get()

            # Validation (optional but recommended)
            if not (s_date and s_time and admission and book_num):
                messagebox.showwarning("Input Error", "Please fill all required fields!")
                return

            # Connect to database
            conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                        r'DBQ=E:\New folder (2)\libry.accdb;')
            Conn = pyodbc.connect(conn_str)
            cursor = Conn.cursor()

            # Insert data
            cursor.execute("""
                INSERT INTO resew (sendate, sentime, adnum, bknum, offedate, offertime)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (s_date, s_time, admission, book_num, offer_date, offer_time))

            # Commit and close
            Conn.commit()
            Conn.close()

            # Update Treeview
            display_send_data()  # Refresh the display after insert

            messagebox.showinfo("Success", "Data inserted successfully!")

            # Clear entry boxes after insert
            sendate.delete(0, END)
            sentime.delete(0, END)
            adnum.delete(0, END)
            bknum.delete(0, END)
            offedate.delete(0, END)
            offertime.delete(0, END)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def delete_send_data():
        try:
            admission = adnum.get()  # Get the Admission Number from entry

            if not admission:
                messagebox.showwarning("Input Error", "Please enter the Admission Number to delete!")
                return

            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete record with Admission Number {admission}?")
            if not confirm:
                return

            # Connect to database
            conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                        r'DBQ=E:\New folder (2)\libry.accdb;')
            Conn = pyodbc.connect(conn_str)
            cursor = Conn.cursor()

            # Execute DELETE query
            cursor.execute("DELETE FROM resew WHERE adnum = ?", (admission,))
            Conn.commit()
            Conn.close()

            # Refresh Treeview
            display_send_data()

            messagebox.showinfo("Success", f"Record with Admission Number {admission} deleted successfully!")

            # Clear the entry box
            adnum.delete(0, END)

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def search_number():
        try:
            book_number = bknum.get() 
            if not book_number:
                messagebox.showwarning("Input Error", "Please enter a Book Number to search!")
                return

            # Connect to database
            conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                        r'DBQ=E:\New folder (2)\libry.accdb;')
            Conn = pyodbc.connect(conn_str)
            cursor = Conn.cursor()

            # Fetch record matching Book Number
            cursor.execute("SELECT sendate, sentime, adnum, bknum, offedate, offertime FROM resew WHERE bknum = ?", (book_number,))
            record = cursor.fetchone()
            Conn.close()

            if record:
                # Fill entry boxes with fetched data
                sendate.delete(0, END)
                sendate.insert(0, record[0])

                sentime.delete(0, END)
                sentime.insert(0, record[1])

                adnum.delete(0, END)
                adnum.insert(0, record[2])

                bknum.delete(0, END)
                bknum.insert(0, record[3])

                offedate.delete(0, END)
                offedate.insert(0, record[4])

                offertime.delete(0, END)
                offertime.insert(0, record[5])

            else:
                messagebox.showinfo("Not Found", "No record found with this Book Number.")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def update_send_data():
        try:
            # Get values from entry widgets
            s_date = sendate.get()
            s_time = sentime.get()
            admission = adnum.get()
            book_number = bknum.get()
            offer_date = offedate.get()
            offer_time = offertime.get()

            # Validation
            if not book_number:
                messagebox.showwarning("Input Error", "Please enter Book Number to update the record!")
                return

            # Connect to database
            conn_str = (r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                        r'DBQ=E:\New folder (2)\libry.accdb;')
            Conn = pyodbc.connect(conn_str)
            cursor = Conn.cursor()

            # Update query
            cursor.execute("""
                UPDATE resew
                SET sendate = ?, sentime = ?, adnum = ?, offedate = ?, offertime = ?
                WHERE bknum = ?
            """, (s_date, s_time, admission, offer_date, offer_time, book_number))

            Conn.commit()
            Conn.close()

            # Refresh Treeview
            display_send_data()

            messagebox.showinfo("Success", f"Record with Book Number {book_number} updated successfully!")

        except pyodbc.Error as e:
            messagebox.showerror("Database Error", f"Error: {e}")

    def clear_send_entries():
        sendate.delete(0, END)
        sentime.delete(0, END)
        adnum.delete(0, END)
        bknum.delete(0, END)
        offedate.delete(0, END)
        offertime.delete(0, END)

    #====widow
    
    send_win = Toplevel(win)
    send_win.title("Send Window")
    send_win.geometry("800x600+200+100")
    send_win.configure(bg="#247cd4")
    send_win.resizable(0, 0)

    Sframe = Frame(send_win, bd=5, width=800, height=600, relief=RIDGE, bg="#66234E")
    Sframe.grid(column=0, row=0)

    viewframe2 = Frame(Sframe, bd=5, width=880, height=220, relief=RIDGE, bg="#66234E")
    viewframe2.place(x=0, y=360)



    # === Labels
    Label(Sframe, text='Send Book', font='none 20 bold', bg="#66234E", fg="white").place(x=300, y=10)
    Label(Sframe, text='Send Date', font='none 12', bg="#66234E", fg="white").place(x=500, y=100)
    Label(Sframe, text='Send Time', font='none 12', bg="#66234E", fg="white").place(x=10, y=100)
    Label(Sframe, text='Admission Number', font='none 12', bg="#66234E", fg="white").place(x=10, y=150)
    Label(Sframe, text='Book Number', font='none 12', bg="#66234E", fg="white").place(x=10, y=200)
    Label(Sframe, text='Offer Date', font='none 12', bg="#66234E", fg="white").place(x=10, y=250)
    Label(Sframe, text='Offer Time', font='none 12', bg="#66234E", fg="white").place(x=10, y=300)

    # === Entry widgets
    sendate = Entry(Sframe, font='none 12', width=20)
    sendate.place(x=590, y=100)

    sentime = Entry(Sframe, font='none 12', width=20)
    sentime.place(x=200, y=100)

    adnum = Entry(Sframe, font='none 12', width=20)
    adnum.place(x=200, y=150)

    bknum = Entry(Sframe, font='none 12', width=20)
    bknum.place(x=200, y=200)

    offedate = Entry(Sframe, font='none 12', width=20)
    offedate.place(x=200, y=250)

    offertime = Entry(Sframe, font='none 12', width=20)
    offertime.place(x=200, y=300)

    # === Buttons
# === Buttons inside Sframe
    Button(Sframe, text="Insert", font='none 12 bold', bg="#1D431E", fg="white", width=10,command= insert_send_data).place(x=500, y=150)
    Button(Sframe, text="Display", font='none 12 bold', bg="#4B2551", fg="white", width=10,command= display_send_data).place(x=670, y=150)
    Button(Sframe, text="Update", font='none 12 bold', bg="#1A3E51", fg="white", width=10,command=update_send_data).place(x=500, y=200)
    Button(Sframe, text="Delete", font='none 12 bold', bg="#481e59", fg="white", width=10,command=delete_send_data ).place(x=670, y=200)
    Button(Sframe, text="Clear", font='none 12 bold', bg="#572927", fg="white", width=10,command=clear_send_entries).place(x=500, y=250)
    Button(Sframe, text="Search", font='none 12 bold', bg="#421A37", fg="white", width=10,command=search_number).place(x=670, y=250)
    Button(Sframe, text="Exit", font='none 12 bold', bg="#421A37", fg="white", width=10,).place(x=670, y=300)

    scroll_y_r = Scrollbar(viewframe2, orient=VERTICAL)

    memrecords_r = ttk.Treeview(
        viewframe2,
        height=10,
        columns=('sendate', 'sentime', 'adnum', 'bknum', 'offedate', 'offertime'),
        yscrollcommand=scroll_y_r.set
    )

    scroll_y_r.pack(side=RIGHT, fill=Y)

    memrecords_r.heading('sendate', text='Send Date')
    memrecords_r.heading('sentime', text='Send Time')
    memrecords_r.heading('adnum', text='Admission Number')
    memrecords_r.heading('bknum', text='Book Number')
    memrecords_r.heading('offedate', text='Offer Date')
    memrecords_r.heading('offertime', text='Offer Time')

    memrecords_r['show'] = 'headings'

    memrecords_r.column('sendate', width=130, anchor=W)
    memrecords_r.column('sentime', width=130, anchor=W)
    memrecords_r.column('adnum', width=130, anchor=W)
    memrecords_r.column('bknum', width=130, anchor=W)
    memrecords_r.column('offedate', width=120, anchor=W)
    memrecords_r.column('offertime', width=120, anchor=W)

    memrecords_r.pack(fill=BOTH, expand=1)



#========================clear funshan

def clear():
    # Clear all Entry widgets
    bkname.delete(0, END)
    bkwri.delete(0, END)
    bkpr.delete(0, END)
    bkisb.delete(0, END)
    bkdate.delete(0, END)
    bknum.delete(0, END)
    bkcom.delete(0, END)
    bktynum.delete(0, END)

    # Clear Text widget
    stnot.delete('1.0', END)

    # Reset Combobox
    bktyp.set('')

def move_left(event):
    event.widget.tk_focusPrev().focus_set()

def move_right(event):
    event.widget.tk_focusNext().focus_set()


def exit_program():
    win.destroy()
#======================================= main window
win = Tk()
win.configure(bg="#b9cae7")
win.geometry('1370x762+85+20')
win.title('STORS')
win.resizable(0, 0)

#========================= frame
M_Frame = Frame(win, bd=5, width=1360, height=650, bg="#000000", relief=RIDGE)
M_Frame.grid()

Lframe = Frame(M_Frame, bd=5, width=1362, height=755, relief=RIDGE, bg="#3A4E8A")
Lframe.grid(column=0, row=0)

viewframe1 = Frame(Lframe, bd=5, width=1351, height=369, relief=RIDGE, bg='cadet blue')
viewframe1.place(x=0, y=400)

#======================== labels
Label(Lframe, text=' මහජන පුස්තකාලය පොලොන්නරුව ',font='none 20', bg="#3A4E8A", fg="#FFFFFF", width=39, height=1).place(x=340, y=15)
Label(Lframe, text=' ------------------------- ',font='none 20', bg="#3A4E8A", fg="#2DCA6C", width=39).place(x=340, y=51)

Label(Lframe, text='Book Name', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=10, y=100)
Label(Lframe, text='Writer', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=450, y=100)
Label(Lframe, text='books type', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=835, y=100)
Label(Lframe, text='Price RS', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=1100, y=100)
Label(Lframe, text='ISBN Number', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=10, y=150)
Label(Lframe, text='Date', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=370, y=150)
Label(Lframe, text='Book Num', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=600, y=150)
Label(Lframe, text='Company Name', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=890, y=150)
Label(Lframe, text='Book type', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=580, y=214)
Label(Lframe, text='Number', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=580, y=235)
Label(Lframe, text='Short not ', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=10, y=225)
Label(Lframe, text='about book ', font='none 12', bg="#3A4E8A", fg="#FFFFFF").place(x=10, y=255)

#=========================== entry
bkname = Entry(Lframe, font='none 13', width=30)
bkname.place(x=130, y=100)

bkwri = Entry(Lframe, font='none 12', width=30)
bkwri.place(x=510, y=100)

bkpr = Entry(Lframe, font='none 12', width=15)
bkpr.place(x=1180, y=100)

bkisb = Entry(Lframe, font='none 12', width=20)
bkisb.place(x=130, y=150)

bkdate = Entry(Lframe, font='none 12', width=15)
bkdate.place(x=420, y=150)

bknum= Entry(Lframe, font='none 12', width=15)
bknum.place(x=690, y=150)

bkcom = Entry(Lframe, font='none 12', width=31)
bkcom.place(x=1038, y=150)

bktynum = Entry(Lframe, font='none 12', width=20)
bktynum.place(x=680, y=215)

stnot = Text(Lframe, font='none 12', width=45, height=9)
stnot.place(x=130, y=215)

bktyp = ttk.Combobox(Lframe, width=17, values=['නවකථා', 'කෙටිකථා', 'කාව්‍ය සංග්‍රහ'])
bktyp.place(x=930, y=100)


#===============================buttons
Button(Lframe, text="Insert", font='none 12 bold',bg="#4C734D", fg="white", width=10,command=insert).place(x=950, y=240)
Button(Lframe, text="Search", font='none 12 bold',bg="#3D4D5D", fg="white", width=10,command=search).place(x=1080, y=240)
Button(Lframe, text="Display", font='none 12 bold',bg="#65476A", fg="white", width=10,command=display ).place(x=1220, y=240)
Button(Lframe, text="Update", font='none 12 bold',bg="#3F535E", fg="white", width=10,command=update).place(x=950, y=290)
Button(Lframe, text="Delete", font='none 12 bold',bg="#63486e", fg="white", width=10,command=delete).place(x=1080, y=290)
Button(Lframe, text="Clear", font='none 12 bold',bg="#6e4a48", fg="white", width=10,command=clear).place(x=1220, y=290)
Button(Lframe, text="Exit", font='none 12 bold',bg="#6A4760", fg="white", width=10, command=win.destroy).place(x=1220, y=340)



#============================== join libry window

Button(Lframe, text="Join libery", font='none 12 bold', bg="#2c5f2d", fg="white", width=12, command=open_new_window).place(x=800, y=340)


#============================== join send bob window

Button(Lframe, text="Send books", font='none 12 bold', bg="#2c5f2d", fg="white", width=12, command=send_window).place(x=600, y=340)


# ================== Treeview ==================
scroll_y_r = Scrollbar(viewframe1, orient=VERTICAL)

memrecords_r = ttk.Treeview(
    viewframe1,
    height=15,
    columns=('bkname', 'bkwri', 'bkpr', 'bkisb', 'bkdate', 'bknum', 'bkcom', 'bktynum', 'stnot', 'bktyp'),
    yscrollcommand=scroll_y_r.set
)

scroll_y_r.pack(side=RIGHT, fill=Y)

memrecords_r.heading('bkname', text='Book Name')
memrecords_r.heading('bkwri', text='Writer')
memrecords_r.heading('bkpr', text='Price RS')
memrecords_r.heading('bkisb', text='ISBN Number')
memrecords_r.heading('bkdate', text='Date')
memrecords_r.heading('bknum', text='Book Num')
memrecords_r.heading('bkcom', text='Company Name')
memrecords_r.heading('bktynum', text='Book type Number')
memrecords_r.heading('stnot', text='Short not')
memrecords_r.heading('bktyp', text='books type')


memrecords_r['show'] = 'headings'

memrecords_r.column('bkname', width=190, anchor=W)
memrecords_r.column('bkwri', width=130, anchor=W)
memrecords_r.column('bkpr', width=100, anchor=W)
memrecords_r.column('bkisb', width=100, anchor=W)
memrecords_r.column('bkdate', width=100, anchor=W)
memrecords_r.column('bknum', width=100, anchor=W)
memrecords_r.column('bkcom', width=100, anchor=W)
memrecords_r.column('bktynum', width=80, anchor=W)
memrecords_r.column('stnot', width=324, anchor=W)
memrecords_r.column('bktyp', width=100, anchor=W)


memrecords_r.pack(fill=BOTH, expand=1)

#========================================= add key

bkname.focus_set()
win.bind('<Control_L>', lambda event: exit_program())
win.bind('<Control_R>', lambda event: exit_program())
win.bind('<Alt-x>', lambda event: insert())
win.bind('<Alt-X>', lambda event: insert())
win.bind('<Alt-s>', lambda event: search())
win.bind('<Alt-S>', lambda event: search())
win.bind('<Alt-z>', lambda event: display())
win.bind('<Alt-Z>', lambda event: display())
win.bind('<Alt-d>', lambda event: delete())
win.bind('<Alt-D>', lambda event: delete())
win.bind('<Alt-a>', lambda event: update())
win.bind('<Alt-A>', lambda event: update())
win.bind('<Alt-c>', lambda event: clear())
win.bind('<Alt-c>', lambda event: clear())



# Arrow key bindings
bkname.bind('<Right>', move_right)
bkwri.bind('<Right>', move_right)
bkpr.bind('<Right>', move_right)
bkisb.bind('<Right>', move_right)
bkdate.bind('<Right>', move_right)
bknum.bind('<Right>', move_right)
bkcom.bind('<Right>', move_right)
bktynum.bind('<Right>', move_right)
stnot.bind('<Right>', move_right)



bkwri.bind('<Left>', move_left)
bkpr.bind('<Left>', move_left)
bkisb.bind('<Left>', move_left)
bkdate.bind('<Left>', move_left)
bknum.bind('<Left>', move_left)
bkcom.bind('<Left>', move_left)
bktynum.bind('<Left>', move_left)
stnot.bind('<Left>', move_left)
bktyp.bind('<Left>', move_left)



win.mainloop()
