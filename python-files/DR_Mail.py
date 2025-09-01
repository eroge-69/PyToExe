import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import smtplib
import os
import pandas as pd
from email.message import EmailMessage
from ttkthemes import ThemedStyle

# SMTP server details
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

# Create the main application window
window = tk.Tk()
window.title("Mass Mail Sender")
window.geometry("800x700")

# Apply a themed style to the window
style = ThemedStyle(window)
style.set_theme("arc")

# Create a frame for the header
header_frame = ttk.Frame(window)
header_frame.pack(fill=tk.X)
inbox_label = ttk.Label(header_frame, text="DR.Mail", font=("Helvetica", 20, "bold"))
inbox_label.pack(side=tk.LEFT, padx=10, pady=10)

# Variable to store attachment paths
attachment_paths = []

# Function to handle the "Browse" button for selecting attachments
def browse_attachments():
    global attachment_paths
    attachment_paths = filedialog.askopenfilenames()
    attachment_entry.delete(0, tk.END)
    attachment_entry.insert(0, ", ".join(attachment_paths))

# Function to send the mass emails
def send_mass_emails():
    global attachment_paths  # Access the attachment_paths variable
    # Get the email details from the input fields
    email_address = email_entry.get()
    email_password = password_entry.get()
    email_subject = subject_entry.get()
    email_body = body_text.get("1.0", tk.END).strip()
    recipients_file = recipients_entry.get()
    start_row = start_row_entry.get()
    end_row = end_row_entry.get()

    # Check if any of the fields are empty
    if not all([email_address, email_password, email_subject, email_body, recipients_file, start_row, end_row]):
        messagebox.showerror("Error", "Please fill in all the fields.")
        return

    # Read email addresses from the Excel file based on the specified range
    try:
        df = pd.read_excel(recipients_file, header=None, usecols=[0], skiprows=int(start_row)-1, nrows=int(end_row)-int(start_row)+1)
        recipients = df[0].tolist()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read recipients file. Error: {str(e)}")
        return

    # Send emails to all recipients
    for recipient_email in recipients:
        try:
            # Create the email message object
            msg = EmailMessage()
            msg['From'] = email_address
            msg['To'] = recipient_email
            msg['Subject'] = email_subject

            # Set the email body
            msg.set_content(email_body)

            # Attach files to the email
            for attachment_path in attachment_paths:
                with open(attachment_path, "rb") as file:
                    file_data = file.read()
                    file_name = os.path.basename(attachment_path)
                    msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(email_address, email_password)
                server.send_message(msg)

            print(f"Email sent successfully to {recipient_email}")
        except Exception as e:
            error_message = f"Failed to send email to {recipient_email}. Error: {str(e)}"
            messagebox.showerror("Error", error_message)
            print(error_message)

    messagebox.showinfo("Success", "Mass emails sent successfully!")

# Create the email address input field
email_label = ttk.Label(window, text="Email Address:")
email_label.pack()
email_entry = ttk.Entry(window)
email_entry.pack()

# Create the password input field
password_label = ttk.Label(window, text="Password:")
password_label.pack()
password_entry = ttk.Entry(window, show="*")
password_entry.pack()

# Create the subject input field
subject_label = ttk.Label(window, text="Subject:")
subject_label.pack()
subject_entry = ttk.Entry(window)
subject_entry.pack()

# Create the body text input field
body_label = ttk.Label(window, text="Body:")
body_label.pack()
body_text = tk.Text(window, height=10, width=100)
body_text.pack()

# Create the attachment input field and browse button
attachment_label = ttk.Label(window, text="Attach Your Resume:")
attachment_label.pack()
attachment_entry = ttk.Entry(window)
attachment_entry.pack()
browse_button = ttk.Button(window, text="Browse", command=browse_attachments)
browse_button.pack()

# Create the recipients file browse button
recipients_label = ttk.Label(window, text="Recipients Excel File:")
recipients_label.pack()
recipients_entry = ttk.Entry(window)
recipients_entry.pack()

# Create the start row input field
start_row_label = ttk.Label(window, text="Start Row:")
start_row_label.pack()
start_row_entry = ttk.Entry(window)
start_row_entry.pack()

# Create the end row input field
end_row_label = ttk.Label(window, text="End Row:")
end_row_label.pack()
end_row_entry = ttk.Entry(window)
end_row_entry.pack()

def browse_recipients_file():
    recipients_file = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
    recipients_entry.delete(0, tk.END)
    recipients_entry.insert(0, recipients_file)

# Create the button to browse for the recipients file
browse_recipients_button = ttk.Button(window, text="Browse", command=browse_recipients_file)
browse_recipients_button.pack()

# Create the button to send the mass emails
send_button = ttk.Button(window, text="Send", command=send_mass_emails)
send_button.pack(side=tk.LEFT, padx=10, pady=10)

# Start the application
window.mainloop()