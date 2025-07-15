import os
import smtplib
from email.message import EmailMessage

# Configuration
sender_email = "danialcomputers@gmail.com"
receiver_email = "danialcomputers@gmail.com"
app_password = "naqvi110#03124410359#####"  # Use Gmail App Password
folder_path = "C:\my doc"  # Change this

def send_word_files():
    msg = EmailMessage()
    msg["Subject"] = "Automatic Word Documents Backup"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content("Attached are all Word documents from your folder.")

    # Attach all .docx or .doc files
    for filename in os.listdir(folder_path):
        if filename.endswith(".docx") or filename.endswith(".doc"):
            filepath = os.path.join(folder_path, filename)
            with open(filepath, "rb") as file:
                file_data = file.read()
                msg.add_attachment(
                    file_data,
                    maintype="application",
                    subtype="octet-stream",
                    filename=filename
                )

    # Send email
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(sender_email, app_password)
        smtp.send_message(msg)

    print("Documents sent successfully.")

send_word_files()
