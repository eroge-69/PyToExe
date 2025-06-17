from datetime import datetime, timedelta  # Import datetime module for displaying current date
import tkinter as tk
from tkinter import messagebox
from sqlite3 import connect
from PIL import Image, ImageTk
from customtkinter import *
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Initialize the main window
win = CTk()
# Set window dimensions
width = 1600
height = 1000
sys_width = win.winfo_screenwidth()
sys_height = win.winfo_screenheight()
c_x = int(sys_width / 2 - width / 2)
c_y = int(sys_height / 2 - height / 2)
win.geometry(f"{width}x{height}+{c_x}+{c_y}")
win.resizable(False, False)



############        IMGAES         ########################################################


dash_icon1 = Image.open("dashboard_a.png")  
dash_icon1 = dash_icon1.resize((30, 30))  
dash_icon1 = ImageTk.PhotoImage(dash_icon1)

dash_icon2 = Image.open("dashboard_b.png")  
dash_icon2 = dash_icon2.resize((30, 30))  
dash_icon2 = ImageTk.PhotoImage(dash_icon2)

delete_icon = Image.open("delete.png")  
delete_icon = delete_icon.resize((30, 30))
delete_icon = ImageTk.PhotoImage(delete_icon)

issue_book_icon1 = Image.open("book_b.png")
issue_book_icon1 = issue_book_icon1.resize((30, 30))
issue_book_icon1 = ImageTk.PhotoImage(issue_book_icon1)

issue_book_icon2 = Image.open("book_a.png")
issue_book_icon2 = issue_book_icon2.resize((30, 30))
issue_book_icon2 = ImageTk.PhotoImage(issue_book_icon2)

stock_icon1 = Image.open("stock_b.png")
stock_icon1 = stock_icon1.resize((30, 30))
stock_icon1 = ImageTk.PhotoImage(stock_icon1)

stock_icon2 = Image.open("stock_a.png")
stock_icon2 = stock_icon2.resize((30, 30))
stock_icon2 = ImageTk.PhotoImage(stock_icon2)

info_icon1 = Image.open("info_b.png")
info_icon1 = info_icon1.resize((30, 30))
info_icon1 = ImageTk.PhotoImage(info_icon1)

info_icon2 = Image.open("info_a.png")
info_icon2 = info_icon2.resize((30, 30))
info_icon2 = ImageTk.PhotoImage(info_icon2)

exit_icon = Image.open("logout_b.png") 
exit_icon = exit_icon.resize((30, 30))  
exit_icon = ImageTk.PhotoImage(exit_icon)

calender_icon = Image.open("calender.png")
calender_icon = calender_icon.resize((30, 30))
calender_icon = ImageTk.PhotoImage(calender_icon)

right_icon = Image.open("right.png")
right_icon = right_icon.resize((30, 30))
right_icon = ImageTk.PhotoImage(right_icon)

left_icon = Image.open("left.png")
left_icon = left_icon.resize((30, 30))
left_icon = ImageTk.PhotoImage(left_icon)

borrowed_icon = Image.open("borrowed.png")
borrowed_icon = borrowed_icon.resize((45, 45))
borrowed_icon = ImageTk.PhotoImage(borrowed_icon)

overdue_icon = Image.open("overdue.png")
overdue_icon = overdue_icon.resize((45, 45))
overdue_icon = ImageTk.PhotoImage(overdue_icon)

total_books_icon = Image.open("total books.png")
total_books_icon = total_books_icon.resize((45, 45))
total_books_icon = ImageTk.PhotoImage(total_books_icon)

pdf_icon = Image.open("pdf.png")
pdf_icon = pdf_icon.resize((30, 30))
pdf_icon = ImageTk.PhotoImage(pdf_icon)




# Connect to the SQLite database (or create it if it doesn't exist)
conn = connect("library.db")
cursor = conn.cursor()

# Create the users table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS issued_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT NOT NULL,
    student_class TEXT NOT NULL,
    student_section TEXT NOT NULL,
    book_name TEXT NOT NULL,
    issue_date TEXT NOT NULL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_name_sp TEXT NOT NULL,
    book_type_sp TEXT NOT NULL,
    quantity_sp TEXT NOT NULL,
    publisher_name_sp TEXT NOT NULL,
    author_name_sp TEXT NOT NULL,
    ISBN_code_sp TEXT NOT NULL,
    price_sp TEXT NOT NULL,
    date_sp TEXT NOT NULL
)
""")
conn.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS removed_stock (
    book_name TEXT PRIMARY KEY,
    book_type TEXT,
    publisher_name TEXT,
    author_name TEXT,
    ISBN_code TEXT,
    price TEXT,
    last_removed_date TEXT
);
""")
conn.commit()



#####################        FUNTIONS         #################################################################################


def login():
    username = login_username_entry.get().strip()
    password = login_password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Input Error", "All fields are required!")
        return

    cursor.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    if user:
        show_welcome_page(username)
        check_overdue_books()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def refresh_home_labels():
    date_label.configure(text=datetime.now().strftime("%d-%m-%Y"))

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def signup():
    username = signup_username_entry.get().strip()
    password = signup_password_entry.get().strip()

    if not username or not password:
        messagebox.showerror("Input Error", "All fields are required!")
        return

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        messagebox.showinfo("Signup Successful",
                            "Account created successfully!")
        show_welcome_page(username)
    except Exception as e:
        messagebox.showerror("Signup Failed", "Username already exists!")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def logout():
    response = messagebox.askyesno("Logout", "Do you want to logout?")
    if response:
        main_page.quit()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def issue_book_button():
    # Get data from entries
    student_name = name_entry.get().strip()
    student_class = class_entry_var.get().strip()
    student_section = section_entry_var.get().strip()
    book_name = book_name_entry.get().strip()
    issue_date = date_entry.get().strip()

    if not student_name or not student_class or not student_section or not book_name or not issue_date:
        messagebox.showerror("Input Error", "All fields are required!")
        return

    # Check if book exists in stock and has enough quantity
    cursor.execute("SELECT quantity_sp FROM stock WHERE book_name_sp = ?", (book_name,))
    stock_data = cursor.fetchone()

    if not stock_data:
        messagebox.showerror("Stock Error", f"The book '{book_name}' is not available in stock!")
        return

    stock_quantity = int(stock_data[0])  # Convert to integer

    if stock_quantity <= 0:
        messagebox.showerror("Stock Error", f"The book '{book_name}' is out of stock!")
        return

    try:
        # Issue the book by adding an entry
        cursor.execute("""
        INSERT INTO issued_books (student_name, student_class, student_section, book_name, issue_date)
        VALUES (?, ?, ?, ?, ?)""",
        (student_name, student_class, student_section, book_name, issue_date))

        # Reduce book quantity in stock
        new_quantity = stock_quantity - 1
        cursor.execute("UPDATE stock SET quantity_sp = ? WHERE book_name_sp = ?", (new_quantity, book_name))

        conn.commit()
        messagebox.showinfo("Success", "Book issued successfully!")

        # Refresh issued books and dashboard stats
        load_issued_books()
        update_dashboard_stats()

        # Clear input fields
        name_entry.delete(0, tk.END)
        book_name_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        class_entry_var.set("Class")
        section_entry_var.set("Section")
        date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def remove_issued_book(entry_frame, student_name, book_name):
    try:
        confirm = messagebox.askyesno("Withdraw", f"Are you sure you want to return '{book_name}'?")
        if not confirm:
            return

        # Check if the book exists in stock
        cursor.execute("SELECT quantity_sp FROM stock WHERE book_name_sp = ?", (book_name,))
        stock_data = cursor.fetchone()

        if stock_data:  # ✅ If book exists in stock, just increase quantity
            stock_quantity = int(stock_data[0])
            new_quantity = stock_quantity + 1
            cursor.execute("UPDATE stock SET quantity_sp = ? WHERE book_name_sp = ?", (new_quantity, book_name))
        else:  # ✅ If book was removed, restore from `removed_stock`
            cursor.execute("SELECT * FROM removed_stock WHERE book_name = ?", (book_name,))
            book_details = cursor.fetchone()

            if book_details:
                cursor.execute("""
                    INSERT INTO stock (book_name_sp, book_type_sp, quantity_sp, publisher_name_sp, author_name_sp, ISBN_code_sp, price_sp, date_sp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (book_details[0], book_details[1], 1,  # Restored with 1 quantity
                      book_details[2], book_details[3], book_details[4], book_details[5], datetime.now().strftime("%d-%m-%Y")))
                
                # ✅ Remove book from `removed_stock` after restoring it
                cursor.execute("DELETE FROM removed_stock WHERE book_name = ?", (book_name,))

        # ✅ Remove the book from `issued_books`
        cursor.execute("DELETE FROM issued_books WHERE student_name = ? AND book_name = ?", (student_name, book_name))
        conn.commit()

        entry_frame.destroy()
        update_dashboard_stats()  # Refresh stock & issued book count
        load_books_in_stock()  # Refresh stock page

        messagebox.showinfo("Success", f"Book '{book_name}' returned successfully!")

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")






# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def add_issued_book_entry(student_name, student_class, student_section, book_name, issue_date):
    # Create a frame for the issued book entry
    entry_frame = CTkFrame(filter_frame, fg_color="white", border_width=1, border_color="black",width=1200)
    entry_frame.pack(fill="x",pady=10, padx=10, ipady=15)

    # Display book details
    entry_label = entry_label = CTkLabel(entry_frame, text=f"""Name: {student_name}      Class & Section: {student_class}-{student_section}

Book Name: {book_name}      Issued on: {issue_date}""", font=("berlin sans fb", 30), fg_color="white", width=110, height=10,justify="left")
    entry_label.pack(side="left", padx=(10,0))

    # Add remove button
    remove_button = CTkButton(entry_frame, text="",image=delete_icon, font=("berlin sans fb", 25),width=45,height=60, fg_color="red", text_color="white", hover_color="darkred", command=lambda: remove_issued_book(entry_frame, student_name, book_name))
    remove_button.pack(side="right",padx=(0,10))

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def filter_issued_books(event):
    search_text = name_filter.get().strip().lower()
    
    # Clear current entries
    for widget in filter_frame.winfo_children():
        widget.destroy()

    try:
        cursor.execute("SELECT student_name, student_class, student_section, book_name, issue_date FROM issued_books")
        issued_books = cursor.fetchall()

        filtered_books = [book for book in issued_books if search_text in book[0].lower()]

        if not filtered_books:
            empty_label = CTkLabel(filter_frame, text="No matching record found.", font=("berlin sans fb", 25))
            empty_label.pack(pady=10)
        else:
            for book in filtered_books:
                add_issued_book_entry(*book)

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

# Function to load all issued books when withdraw page opens
def load_issued_books():
    name_filter.delete(0, tk.END)  # Clear search bar before loading
    try:
        cursor.execute("SELECT student_name, student_class, student_section, book_name, issue_date FROM issued_books ORDER BY issue_date DESC")
        issued_books = cursor.fetchall()

        # Clear current entries
        for widget in filter_frame.winfo_children():
            widget.destroy()

        if not issued_books:
            empty_label = CTkLabel(filter_frame, text="No issued book found.", font=("berlin sans fb", 25))
            empty_label.pack(pady=10)
        else:
            for book in issued_books:
                add_issued_book_entry(*book)

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

    name_filter.bind("<KeyRelease>", filter_issued_books)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def add_book_to_stock():
    book_name_sp = book_name_entry_S_P.get().strip()
    book_type_sp = book_type_var_S_P.get().strip()
    quantity_sp = quantity_entry_S_P.get().strip()
    publisher_name_sp = publisher_name_entry_S_P.get().strip()
    author_name_sp = author_name_entry_S_P.get().strip()
    ISBN_code_sp = ISBN_entry_S_P.get().strip()
    price_sp = price_entry_S_P.get().strip()
    date_sp = date_entry_S_P.get().strip()

    if not book_name_sp or not book_type_sp or not quantity_sp or not publisher_name_sp or not author_name_sp or not ISBN_code_sp or not price_sp or not date_sp:
        messagebox.showerror("Input Error", "All fields are required!")
        return

    try:
        # Insert data into database
        cursor.execute("""
        INSERT INTO stock (book_name_sp, book_type_sp, quantity_sp, publisher_name_sp, author_name_sp, ISBN_code_sp, price_sp, date_sp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (book_name_sp, book_type_sp, quantity_sp, publisher_name_sp, author_name_sp, ISBN_code_sp, price_sp, date_sp))
        conn.commit()
        messagebox.showinfo("Success", "Book issued successfully!")

        # Add the new entry to the withdraw page UI
        load_books_in_stock()
        update_dashboard_stats()

        # Clear input fields
        book_name_entry_S_P.delete(0, tk.END)
        book_type_var_S_P.set("Book Type")
        quantity_entry_S_P.delete(0, tk.END)
        publisher_name_entry_S_P.delete(0, tk.END)
        author_name_entry_S_P.delete(0, tk.END)
        ISBN_entry_S_P.delete(0, tk.END)
        price_entry_S_P.delete(0, tk.END)
        date_entry_S_P.delete(0, tk.END)
        date_entry_S_P.insert(0, datetime.now().strftime("%d-%m-%Y"))

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def remove_book_from_stock(entry_frame_S_P, book_name_sp, ISBN_code_sp):
    try:
        confirm = messagebox.askyesno("Remove Stock", f"Are you sure you want to remove '{book_name_sp}' from stock?")
        if not confirm:
            return

        # Fetch book details before deleting
        cursor.execute("SELECT book_name_sp, book_type_sp, publisher_name_sp, author_name_sp, ISBN_code_sp, price_sp FROM stock WHERE book_name_sp = ?", (book_name_sp,))
        book_details = cursor.fetchone()

        if book_details:
            # ✅ Use INSERT OR REPLACE to avoid primary key error
            cursor.execute("""
                INSERT OR REPLACE INTO removed_stock (book_name, book_type, publisher_name, author_name, ISBN_code, price, last_removed_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (book_details[0], book_details[1], book_details[2], book_details[3], book_details[4], book_details[5], datetime.now().strftime("%d-%m-%Y")))

        # Remove book from stock
        cursor.execute("DELETE FROM stock WHERE book_name_sp = ?", (book_name_sp,))
        conn.commit()

        entry_frame_S_P.destroy()
        update_dashboard_stats()  # Refresh dashboard
        messagebox.showinfo("Success", f"Book '{book_name_sp}' removed from stock!")

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")



# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def add_stock_book_entry(book_name_sp, book_type_sp, quantity_sp, publisher_name_sp, author_name_sp, ISBN_code_sp, price_sp,date_sp):
    # Create a frame for the issued book entry
    entry_frame_S_P = CTkFrame(filter_frame_S_P, fg_color="white", border_width=1, border_color="black",width=1200)
    entry_frame_S_P.pack(fill="x",pady=10, padx=10, ipady=15)

    # Display book details
    entry_label_S_P = CTkLabel(entry_frame_S_P, text=f"""Book Name: {book_name_sp}      Book Type: {book_type_sp}      Quantity: {quantity_sp}

Publisher: {publisher_name_sp}      Author: {author_name_sp}

ISBN Code: {ISBN_code_sp}    Price: {price_sp}    Date: {date_sp}""", font=("berlin sans fb", 30), fg_color="white", width=110, height=10,justify="left")
    entry_label_S_P.pack(side="left",padx=(10,0))

    # Add remove button
    remove_button_S_P = CTkButton(entry_frame_S_P, text="",image=delete_icon, font=("berlin sans fb", 25),width=45,height=60, fg_color="red", text_color="white", hover_color="darkred", command=lambda: remove_book_from_stock(entry_frame_S_P, book_name_sp, ISBN_code_sp))
    remove_button_S_P.pack(side="right",padx=(0,10))

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def filter_books_in_stock(event):
    search_text = name_filter_S_P.get().strip().lower()
    
    # Clear current entries
    for widget in filter_frame_S_P.winfo_children():
        widget.destroy()

    try:
        cursor.execute("SELECT book_name_sp, book_type_sp, quantity_sp, publisher_name_sp, author_name_sp, ISBN_code_sp, price_sp, date_sp FROM stock")
        stock = cursor.fetchall()

        filtered_books = [book for book in stock if search_text in book[0].lower() or search_text in book[4].lower() or search_text in book[5].lower()]

        if not filtered_books:
            empty_label = CTkLabel(filter_frame_S_P, text="No matching record found.", font=("berlin sans fb", 25))
            empty_label.pack(pady=10)
        else:
            for book in filtered_books:
                add_stock_book_entry(*book)

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def load_books_in_stock():
    name_filter_S_P.delete(0, tk.END)  # Clear search bar before loading
    try:
        cursor.execute("SELECT book_name_sp, book_type_sp, quantity_sp, publisher_name_sp, author_name_sp, ISBN_code_sp, price_sp, date_sp FROM stock ORDER BY date_sp DESC")
        stock = cursor.fetchall()

        # Clear current entries
        for widget_sp in filter_frame_S_P.winfo_children():
            widget_sp.destroy()

        if not stock:
            empty_label_S_P = CTkLabel(filter_frame_S_P, text="No such book found.", font=("berlin sans fb", 25))
            empty_label_S_P.pack(pady=10)
        else:
            for book_sp in stock:
                add_stock_book_entry(*book_sp)

    except Exception as e:
        messagebox.showerror("Database Error", f"An error occurred: {str(e)}")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def check_overdue_books():
    today = datetime.now().date()  # Get today's date (without time)
    
    # Fetch issued books from the database
    cursor.execute("SELECT student_name, book_name, issue_date FROM issued_books")
    issued_books = cursor.fetchall()

    overdue_books = []
    for student_name, book_name, issue_date in issued_books:
        try:
            # Convert issue_date string to datetime object
            issue_date_obj = datetime.strptime(issue_date, "%d-%m-%Y").date()  # Extract only the date
            
            # Calculate overdue days (if more than 3 days)
            overdue_days = (today - issue_date_obj).days - 3  # Exclude first 3 days
            
            if overdue_days > 0:  # Apply fine only if overdue
                fine_amount = overdue_days * 10  # ₹10 per day
                overdue_books.append(f"Student: {student_name} | Book: {book_name} | Issued on: {issue_date} | Fine: ₹{fine_amount}")
        except ValueError:
            print(f"Skipping invalid date: {issue_date}")  # Debugging invalid dates

    if overdue_books:
        overdue_message = "The following books are overdue with applicable fines:\n\n" + "\n".join(overdue_books)
        messagebox.showwarning("Overdue Books", overdue_message)
    else:
        print("No overdue books.")  # Debugging output


# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def update_dashboard_stats():
    # Fetch total books in stock
    cursor.execute("SELECT SUM(quantity_sp) FROM stock")
    total_books = cursor.fetchone()[0]
    total_books = total_books if total_books else 0  # Handle None case

    # Fetch total issued books
    cursor.execute("SELECT COUNT(*) FROM issued_books")
    total_issued_books = cursor.fetchone()[0]

    # Fetch overdue books manually by converting dates in Python
    today = datetime.now()
    overdue_cutoff = today - timedelta(days=3)

    cursor.execute("SELECT issue_date FROM issued_books")
    issued_books = cursor.fetchall()

    overdue_count = 0
    for row in issued_books:
        try:
            issue_date_obj = datetime.strptime(row[0], "%d-%m-%Y")
            if issue_date_obj < overdue_cutoff:
                overdue_count += 1
        except ValueError:
            print(f"Skipping invalid date: {row[0]}")  # Debugging

    # Update labels
    total_books_label.configure(text=f"{total_books}")
    total_issued_books_label.configure(text=f"{total_issued_books}")
    overdue_books_label.configure(text=f"{overdue_count}")

    # Schedule the function to run again after 5 seconds
    home_page.after(1000, update_dashboard_stats)  # Refresh every 5 seconds
# Binding the search filter function to the search bar
    name_filter_S_P.bind("<KeyRelease>", filter_books_in_stock)

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def generate_issued_books_report():
    
    confirm = messagebox.askyesno("PDF Report", "Are you sure to create PDF report?")
    if not confirm:
        return

    # Fetch all issued books from the database
    cursor.execute("SELECT student_name, book_name, issue_date FROM issued_books")
    issued_books = cursor.fetchall()

    # Set the PDF file name
    pdf_file = "Issued_Books_Report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)

    # Add title to the PDF
    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 750, "Library Issued Books Report")

    # Column Headers
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 720, "Student Name")
    c.drawString(300, 720, "Book Name")
    c.drawString(500, 720, "Issue Date")
    
    c.line(100, 715, 550, 715)  # Draw line below headers

    # Populate Data
    y_position = 700
    c.setFont("Helvetica", 12)

    for student_name, book_name, issue_date in issued_books:
        c.drawString(100, y_position, student_name)
        c.drawString(300, y_position, book_name)
        c.drawString(500, y_position, issue_date)
        y_position -= 20  # Move down for the next entry

    c.save()  # Save the PDF

    messagebox.showinfo("Success", f"Issued Books Report saved as '{pdf_file}'!")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def generate_stock_report():
    
    confirm = messagebox.askyesno("PDF Report", "Are you sure to create PDF report?")
    if not confirm:
        return

    cursor.execute("SELECT book_name_sp, author_name_sp, ISBN_code_sp, quantity_sp FROM stock")
    stock_books = cursor.fetchall()

    pdf_file = "Library_Stock_Report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)

    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 750, "Library Stock Report")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 720, "Book Name")
    c.drawString(250, 720, "Author")
    c.drawString(350, 720, "ISBN Code")
    c.drawString(470, 720, "Quantity")

    c.line(100, 715, 550, 715)

    y_position = 700
    c.setFont("Helvetica", 12)

    for book_name, author, ISBN_code1, quantity in stock_books:
        c.drawString(100, y_position, book_name)
        c.drawString(250, y_position, author)
        c.drawString(350, y_position, ISBN_code1)
        c.drawString(470, y_position, str(quantity))
        y_position -= 20

    c.save()
    messagebox.showinfo("Success", f"Stock Report saved as '{pdf_file}'!")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def generate_overdue_books_report():
    
    confirm = messagebox.askyesno("PDF Report", "Are you sure to create PDF report?")
    if not confirm:
        return
        
    today = datetime.now()
    overdue_cutoff = today - timedelta(days=3)

    cursor.execute("SELECT student_name, book_name, issue_date FROM issued_books")
    issued_books = cursor.fetchall()

    pdf_file = "Overdue_Books_Report.pdf"
    c = canvas.Canvas(pdf_file, pagesize=letter)

    c.setFont("Helvetica-Bold", 20)
    c.drawString(200, 750, "Overdue Books Report")

    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, 720, "Student Name")
    c.drawString(300, 720, "Book Name")
    c.drawString(500, 720, "Issue Date")

    c.line(100, 715, 550, 715)

    y_position = 700
    c.setFont("Helvetica", 12)

    for student_name, book_name, issue_date in issued_books:
        try:
            issue_date_obj = datetime.strptime(issue_date, "%d-%m-%Y")
            if issue_date_obj < overdue_cutoff:
                c.drawString(100, y_position, student_name)
                c.drawString(300, y_position, book_name)
                c.drawString(500, y_position, issue_date)
                y_position -= 20
        except ValueError:
            print(f"Skipping invalid date: {issue_date}")  # Debugging

    c.save()
    messagebox.showinfo("Success", f"Overdue Books Report saved as '{pdf_file}'!")

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

def show_login_frame():
    signup_frame.place_forget()
    main_page.place_forget()
    login_frame.place(relx=0.5, rely=0.5, anchor="center",)

def show_signup_frame():
    login_frame.place_forget()
    main_page.place_forget()
    signup_frame.place(relx=0.5, rely=0.5, anchor="center")

def show_welcome_page(username):
    login_frame.place_forget()
    signup_frame.place_forget()
    issue_book_page.place_forget()
    stock_page.place_forget()
    main_page.place(relx=0.5, rely=0.5, anchor="center")
    hello_label1.configure(text=username)
    update_dashboard_stats()

def open_main_home_page():
    dash_button.configure(fg_color="#f65867",image=dash_icon1)
    issue_book.configure(fg_color="#353334",image=issue_book_icon1)
    stock_button.configure(fg_color="#353334",image=stock_icon1)
    info_button.configure(fg_color="#353334",image=info_icon1)
    issue_book_page.place_forget()
    stock_page.place_forget()
    home_page.place(x=0,y=0)
    generate_issued_book_report_btn.place(x=1030, y=330)
    generate_overdue_report_btn.place(x=1530, y=330)
    generate_stock_report_btn.place(x=530, y=330)

def open_issue_book_page():
    date_label.place_forget()
    dash_button.configure(fg_color="#353334",image=dash_icon2)
    issue_book.configure(fg_color="#f65867",image=issue_book_icon2)
    stock_button.configure(fg_color="#353334",image=stock_icon1)
    info_button.configure(fg_color="#353334",image=info_icon1)
    withdraw_page.place_forget()
    issue_book_page.place(x=0,y=0)  
    stock_page.place_forget()  
    generate_issued_book_report_btn.place_forget()
    generate_overdue_report_btn.place_forget()
    generate_stock_report_btn.place_forget()

def open_stock_page():
    date_label.place_forget()
    dash_button.configure(fg_color="#353334",image=dash_icon2)
    issue_book.configure(fg_color="#353334",image=issue_book_icon1)
    stock_button.configure(fg_color="#f65867",image=stock_icon2)
    info_button.configure(fg_color="#353334",image=info_icon1)
    issue_book_page.place_forget()
    view_stock_page.place_forget()
    stock_page.place(x=0,y=0)
    generate_issued_book_report_btn.place_forget()
    generate_overdue_report_btn.place_forget()
    generate_stock_report_btn.place_forget()

def open_info_page():
    date_label.place_forget()
    dash_button.configure(fg_color="#353334",image=dash_icon2)
    issue_book.configure(fg_color="#353334",image=issue_book_icon1)
    stock_button.configure(fg_color="#353334",image=stock_icon1)
    info_button.configure(fg_color="#f65867",image=info_icon2)
    issue_book_page.place_forget()
    stock_page.place_forget()
    home_page.place_forget()
    generate_issued_book_report_btn.place_forget()
    generate_overdue_report_btn.place_forget()
    generate_stock_report_btn.place_forget()

def open_withdraw_page():
    withdraw_page.place(x=0,y=0)
    back_button.place(x=10,y=10)
    load_issued_books()

def back_button_W_P():
    withdraw_page.place_forget()

def open_view_stock_page():
    view_stock_page.place(x=0,y=0)
    back_button_S_P.place(x=10,y=10)
    load_books_in_stock()

def back_button_S_P2():
    view_stock_page.place_forget()

# @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@




#############################        LOGIN PAGE         ##################################################################################################################




login_frame = CTkFrame(win, width=1600, height=1000, fg_color="black")

login_box = CTkFrame(login_frame, fg_color="black",border_color="grey", border_width=1)
login_box.place(relx=0.5, rely=0.5, anchor="center")

login_label = CTkLabel(login_box, text="Login", font=("berlin sans fb", 44),text_color="#f65867")
login_label.pack(pady=20)

login_username_entry = CTkEntry(login_box, width=300, height=50, placeholder_text="Username", font=("berlin sans fb", 24),text_color="white",fg_color="black",border_color="black")
login_username_entry.pack(padx=10, pady=15)

line16 = CTkFrame(login_box,height=4,width=285,fg_color="grey",corner_radius=50)
line16.place(x=15,y=145)

login_password_entry = CTkEntry(login_box, show="*", width=300,height=50, placeholder_text="Password", font=("berlin sans fb", 24),text_color="white",fg_color="black",border_color="black")
login_password_entry.pack(pady=5)

line17 = CTkFrame(login_box,height=4,width=285,fg_color="grey",corner_radius=50)
line17.place(x=15,y=215)

login_button = CTkButton(login_box, text="Login", command=login, height=50, font=("berlin sans fb", 30),fg_color="#f65867", text_color="white", border_width=1, border_color="#545454", hover_color="black")
login_button.pack(pady=10)

goto_signup_button = CTkButton(login_box, text="", command=show_signup_frame, height=10, width=10, font=("berlin sans fb", 20), fg_color="black", text_color="black", border_width=1, border_color="black", hover_color="black")
goto_signup_button.place(x=139,y=44)



############        SIGNUP PAGE         #############################################################################################################



signup_frame = CTkFrame(win, width=1600, height=1000, fg_color="black")

signup_box = CTkFrame(signup_frame, fg_color="black",border_color="grey", border_width=1)
signup_box.place(relx=0.5, rely=0.5, anchor="center")

signup_label = CTkLabel(signup_box, text="Signup", font=("berlin sans fb", 44),text_color="#f65867")
signup_label.pack(pady=20)

signup_username_entry = CTkEntry(signup_box, width=300, height=50, placeholder_text="Username",text_color="white", font=("berlin sans fb", 24),fg_color="black",border_color="black")
signup_username_entry.pack(pady=15, padx=10)

line18 = CTkFrame(signup_box,height=4,width=285,fg_color="grey",corner_radius=50)
line18.place(x=15,y=145)

signup_password_entry = CTkEntry(signup_box, show="*", width=300,height=50, placeholder_text="Password",text_color="white", font=("berlin sans fb", 24),fg_color="black",border_color="black")
signup_password_entry.pack(pady=5)

line19 = CTkFrame(signup_box,height=4,width=285,fg_color="grey",corner_radius=50)
line19.place(x=15,y=215)

signup_button = CTkButton(signup_box, text="Signup", command=signup, height=50, font=("berlin sans fb", 30), fg_color="#f65867", text_color="white", border_width=1, border_color="#545454", hover_color="black")
signup_button.pack(pady=5)

goto_login_button = CTkButton(signup_box, text="Login", command=show_login_frame, height=40, width=100, font=("berlin sans fb", 20), fg_color="#f65867", text_color="white", border_width=1, border_color="#545454", hover_color="black")
goto_login_button.pack(padx=10,pady=10)



############        MAIN PAGE         ##################################################################$#$$$$$$$$$$$$##########################




main_page = CTkFrame(win, width=1600, height=1000, fg_color="#353334")

main_content = CTkFrame(main_page, width=1520, height=1000,corner_radius=20, fg_color="#353334")
main_content.place(x=95, y=5)

dash_button = CTkButton(main_page, text="", image=dash_icon1, width=60, height=60, corner_radius=10, fg_color="#f65867",hover_color="#f65867",command=open_main_home_page)
dash_button.place(x=10, y=20)

issue_book = CTkButton(main_page, text="", image=issue_book_icon1, width=60, height=60, corner_radius=10, fg_color="#353334",hover_color="#f65867", command=open_issue_book_page)
issue_book.place(x=10, y=120)

stock_button = CTkButton(main_page, text="", image=stock_icon1, width=60, height=60, corner_radius=10, fg_color="#353334",hover_color="#f65867", command=open_stock_page)
stock_button.place(x=10, y=220)

info_button = CTkButton(main_page, text="", image=info_icon1, width=60, height=60, corner_radius=10, fg_color="#353334",hover_color="#f65867", command=open_info_page)
info_button.place(x=10, y=320)

logout_button = CTkButton(main_page, text="", image=exit_icon, command=lambda: logout(), width=60, height=60, corner_radius=10,fg_color="#353334", hover_color="red")
logout_button.place(x=10, y=930)



#################  HOME PAGE   #################################################################################################################



home_page = CTkFrame(main_content,width=1550,height=1050,corner_radius=50,fg_color="#201c1d")
home_page.place(x=0,y=0)

generate_stock_report_btn = CTkButton(main_page, text="",image=pdf_icon, command=generate_stock_report,width=40, font=("berlin sans fb", 20), fg_color="#4d4949", hover_color="#4d4949",bg_color="#4d4949")
generate_stock_report_btn.place(x=530, y=330)

generate_issued_book_report_btn = CTkButton(main_page, text="",image=pdf_icon, command=generate_issued_books_report,width=40, font=("berlin sans fb", 20), fg_color="#4d4949", hover_color="#4d4949",bg_color="#4d4949")
generate_issued_book_report_btn.place(x=1030, y=330)

generate_overdue_report_btn = CTkButton(main_page,text="",image=pdf_icon, command=generate_overdue_books_report,width=40, font=("berlin sans fb", 20), fg_color="#4d4949", hover_color="#4d4949",bg_color="#4d4949")
generate_overdue_report_btn.place(x=1530, y=330)

hello_label = CTkLabel(home_page,text="Hello,",text_color="white",font=("berlin sans fb",60))
hello_label.place(x=50,y=50)

hello_label1 = CTkLabel(home_page,text="",text_color="#f65867",font=("berlin sans fb",60))
hello_label1.place(x=195,y=50)

total_books = CTkFrame(home_page,fg_color="#4d4949",corner_radius=30,height=200,width=480)
total_books.place(x=15,y=170)

total_books_line = CTkLabel(total_books,text="Total Books In Library",text_color="white",font=("berlin sans fb",30))
total_books_line.place(x=30,y=150)

total_books_label = CTkLabel(total_books,text="",text_color="white",font=("berlin sans fb",50))
total_books_label.place(x=30,y=20)

total_books_img = CTkLabel(total_books,image=total_books_icon,text="",fg_color="#4d4949",height=65,width=65,corner_radius=20)
total_books_img.place(x=380,y=20)

total_issued_books = CTkFrame(home_page,fg_color="#4d4949",corner_radius=30,height=200,width=480)
total_issued_books.place(x=513,y=170)

total_issued_books_line = CTkLabel(total_issued_books,text="Issued Books",text_color="white",font=("berlin sans fb",30))
total_issued_books_line.place(x=30,y=150)

total_issued_books_label = CTkLabel(total_issued_books,text="sdf",text_color="white",font=("berlin sans fb",50))
total_issued_books_label.place(x=30,y=20)

total_issued_books_img = CTkLabel(total_issued_books,image=borrowed_icon,text="",fg_color="#4d4949",height=65,width=65,corner_radius=20)
total_issued_books_img.place(x=380,y=20)

overdue_books = CTkFrame(home_page,fg_color="#4d4949",corner_radius=30,height=200,width=480)
overdue_books.place(x=1010,y=170)

overdue_books_line = CTkLabel(overdue_books,text="Overdue Books",text_color="white",font=("berlin sans fb",30))
overdue_books_line.place(x=30,y=150)

overdue_books_label = CTkLabel(overdue_books,text="sdf",text_color="white",font=("berlin sans fb",50))
overdue_books_label.place(x=30,y=20)

overdue_books_img = CTkLabel(overdue_books,image=overdue_icon,text="",fg_color="#4d4949",height=65,width=65,corner_radius=20)
overdue_books_img.place(x=380,y=20)

date_label = CTkLabel(home_page, text="", font=("berlin sans fb", 26), fg_color="white")
date_label.place(relx=0.9, rely=0.5, anchor="center")  # Top-right corner





#################  ISSUE BOOK PAGE    ############################################################################################################



issue_book_page = CTkFrame(main_content,width=1550,height=1050,corner_radius=50,fg_color="#201c1d")
issue_book_page.place(x=0,y=5)

issue_page_label = CTkLabel(issue_book_page,text="Issue Book",font=("berlin sans fb",60))
issue_page_label.place(x=500,y=10)

name_entry = CTkEntry(issue_book_page,height=100,width=635,placeholder_text="Student's Name",corner_radius=10,font=("berlin sans fb",40),fg_color="#201c1d",border_color="#201c1d")
name_entry.place(x=10,y=100)

line1 = CTkFrame(issue_book_page,height=5,width=600,fg_color="grey",corner_radius=50)
line1.place(x=20,y=185)

class_entry_var = StringVar(value="Class")
class_entry = CTkOptionMenu(issue_book_page,width=317.5,height=100,corner_radius=10,text_color="Black",button_color="white",fg_color="white",button_hover_color="white",dropdown_font=("berlin sans fb",30),dropdown_fg_color="white",dropdown_hover_color="#fffd75",variable=class_entry_var,values=["1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th","11th","12th"],font=("berlin sans fb",40))
class_entry.place(x=655,y=100)

line12 = CTkFrame(issue_book_page,height=5,width=282.5,fg_color="grey",corner_radius=50)
line12.place(x=665,y=185)

section_entry_var = StringVar(value="Section")
section_entry = CTkOptionMenu(issue_book_page,width=307.5,height=100,corner_radius=10,text_color="black",button_color="white",fg_color="white",button_hover_color="white",dropdown_font=("berlin sans fb",30),dropdown_fg_color="white",dropdown_hover_color="#fffd75",variable=section_entry_var,values=["A","B","C","D","E"],font=("berlin sans fb",40))
section_entry.place(x=982.5,y=100)

line13 = CTkFrame(issue_book_page,height=5,width=282.5,fg_color="grey",corner_radius=50)
line13.place(x=992.5,y=185)

book_name_entry = CTkEntry(issue_book_page,height=100,width=635,placeholder_text="Book Name",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
book_name_entry.place(x=10,y=220)

line2 = CTkFrame(issue_book_page,height=5,width=600,fg_color="grey",corner_radius=50)
line2.place(x=20,y=305)

date_entry = CTkEntry(issue_book_page, height=100, width=555, font=("berlin sans fb", 40), fg_color="white", border_color="white")
date_entry.insert(0, datetime.now().strftime("%d-%m-%Y"))  # Automatically set today's date

date_entry.place(x=655,y=220)

line3 = CTkFrame(issue_book_page,height=5,width=525,fg_color="grey",corner_radius=50)
line3.place(x=665,y=305)


issue_button = CTkButton(issue_book_page,height=100,width=500,text="Issue",font=("Berlin Sans FB",50),text_color="black",fg_color="#ffd963",hover_color="#fffd75",command=issue_book_button)
issue_button.place(x=140,y=800)

withdraw_button = CTkButton(issue_book_page,height=100,width=500,text="Withdraw",font=("Berlin Sans FB",50),text_color="black",fg_color="#ffd963",hover_color="#fffd75",command=open_withdraw_page)
withdraw_button.place(x=660,y=800)



#################         WITHDRAW PAGE         ##########################################################################################################33



withdraw_page = CTkFrame(issue_book_page,width=1550,height=1050,corner_radius=50,fg_color="#201c1d")
withdraw_page.place(x=0,y=5)

back_button = CTkButton(withdraw_page,text="Back",text_color="black",font=("berlin sans fb",30),width=50,height=50,corner_radius=10,fg_color="#ffd963",hover_color="#fffd75",command=back_button_W_P)
back_button.place(x=10,y=10)

name_filter = CTkEntry(withdraw_page,height=80,width=600,placeholder_text="Student's Name",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
name_filter.place(x=10,y=100)

line14 = CTkFrame(withdraw_page,height=5,width=565,fg_color="grey",corner_radius=50)
line14.place(x=20,y=165)

filter_frame = CTkScrollableFrame(withdraw_page,width=1280,height=790,fg_color="white")
filter_frame.place(x=0,y=190)



#######################            STOCK PAGE                #####################################################################################




stock_page = CTkFrame(main_content,width=1550,height=1050,corner_radius=50,fg_color="#201c1d")
stock_page.place(x=0,y=5)

stock_label = CTkLabel(stock_page,text="Stock Page",font=("berlin sans fb",60))
stock_label.place(x=500,y=10)

book_name_entry_S_P = CTkEntry(stock_page,height=100,width=635,placeholder_text="Book Name",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
book_name_entry_S_P.place(x=10,y=100)

line4 = CTkFrame(stock_page,height=5,width=600,fg_color="grey",corner_radius=50)
line4.place(x=20,y=185)

book_type_var_S_P = StringVar(value="Book Type")
book_type_entry_S_P = CTkOptionMenu(stock_page,width=317.5,height=100,corner_radius=10,text_color="black",button_color="white",fg_color="white",button_hover_color="white",dropdown_font=("berlin sans fb",30),dropdown_fg_color="white",dropdown_hover_color="#fffd75",variable=book_type_var_S_P,values=["Acedemic","Comic","Novel","Magazine","Dictionary"],font=("berlin sans fb",40))
book_type_entry_S_P.place(x=655,y=100)

line11 = CTkFrame(stock_page,height=5,width=282.5,fg_color="grey",corner_radius=50)
line11.place(x=665,y=185)

quantity_entry_S_P = CTkEntry(stock_page,height=100,width=307.5,placeholder_text="Quantity",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
quantity_entry_S_P.place(x=982.5,y=100)

line5 = CTkFrame(stock_page,height=5,width=272.5,fg_color="grey",corner_radius=50)
line5.place(x=992.5,y=185)

publisher_name_entry_S_P = CTkEntry(stock_page,height=100,width=635,placeholder_text="Publisher Name",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
publisher_name_entry_S_P.place(x=10,y=220)

line6 = CTkFrame(stock_page,height=5,width=600,fg_color="grey",corner_radius=50)
line6.place(x=20,y=305)

author_name_entry_S_P = CTkEntry(stock_page,height=100,width=635,placeholder_text="Author Name",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
author_name_entry_S_P.place(x=655,y=220)

line7 = CTkFrame(stock_page,height=5,width=600,fg_color="grey",corner_radius=50)
line7.place(x=665,y=305)

ISBN_entry_S_P = CTkEntry(stock_page,height=100,width=400,placeholder_text="ISBN Code",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
ISBN_entry_S_P.place(x=10,y=340)

line8 = CTkFrame(stock_page,height=5,width=365,fg_color="grey",corner_radius=50)
line8.place(x=20,y=425)

price_entry_S_P = CTkEntry(stock_page,height=100,width=400,placeholder_text="Price",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
price_entry_S_P.place(x=420,y=340)

line9 = CTkFrame(stock_page,height=5,width=365,fg_color="grey",corner_radius=50)
line9.place(x=430,y=425)

date_entry_S_P = CTkEntry(stock_page, height=100, width=380, font=("berlin sans fb", 40), fg_color="white", border_color="white")
date_entry_S_P.insert(0, datetime.now().strftime("%d-%m-%Y"))  # Automatically set today's date

date_entry_S_P.place(x=830,y=340)

line10 = CTkFrame(stock_page,height=5,width=355,fg_color="grey",corner_radius=50)
line10.place(x=840,y=425)

add_book_button_S_P = CTkButton(stock_page,height=100,width=500,text="Add Book",font=("Berlin Sans FB",50),text_color="black",fg_color="#ffd963",hover_color="#fffd75",command=add_book_to_stock)
add_book_button_S_P.place(x=140,y=800)

view_stock_button_S_P = CTkButton(stock_page,height=100,width=500,text="View Stock",font=("Berlin Sans FB",50),text_color="black",fg_color="#ffd963",hover_color="#fffd75",command=open_view_stock_page)
view_stock_button_S_P.place(x=660,y=800)



####################         VIEW STOCK PAGE          ############################################################################################################################################################




view_stock_page = CTkFrame(stock_page,width=1550,height=1050,corner_radius=50,fg_color="#201c1d")
view_stock_page.place(x=0,y=5)

back_button_S_P = CTkButton(view_stock_page,text="Back",text_color="black",font=("berlin sans fb",30),width=50,height=50,corner_radius=10,fg_color="#ffd963",hover_color="#fffd75",command=back_button_S_P2)
back_button_S_P.place(x=10,y=10)

name_filter_S_P = CTkEntry(view_stock_page,height=80,width=600,placeholder_text="Student's Name",corner_radius=10,font=("berlin sans fb",40),fg_color="white",border_color="white")
name_filter_S_P.place(x=10,y=100)

line15 = CTkFrame(view_stock_page,height=5,width=565,fg_color="grey",corner_radius=50)
line15.place(x=20,y=165)

filter_frame_S_P = CTkScrollableFrame(view_stock_page,width=1280,height=790,fg_color="white")
filter_frame_S_P.place(x=0,y=190)


refresh_home_labels()
show_login_frame()


win.mainloop()

# Close the database connection when the app closes
conn.close()