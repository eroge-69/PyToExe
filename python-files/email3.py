import os
import smtplib
from email.message import EmailMessage

# ==== Configuration ====
sender_email = "danialcomputers@gmail.com"
app_password = "natl rcdq rqju fswr"  # Gmail App Password
receiver_email = "danialcomputers@gmail.com"
folder_path = "C:\naq"  # Replace with your folder path

# ==== Function to Send Word Documents ====
def send_word_documents():
    msg = EmailMessage()
    msg['Subject'] = 'Automatic Backup: Word Documents'
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg.set_content("Attached are the Word documents from your folder.")

    files_sent = 0

    # Loop through files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.doc', '.docx')):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, 'rb') as f:
                file_data = f.read()
                msg.add_attachment(
                    file_data,
                    maintype='application',
                    subtype='octet-stream',
                    filename=filename
                )
                files_sent += 1

    if files_sent == 0:
        print("No Word documents found in the folder.")
        return

    # Send Email
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

    print(f"Successfully sent {files_sent} Word document(s) to {receiver_email}.")

# ==== Run the Function ====
send_word_documents()