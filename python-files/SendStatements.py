import smtplib
import os
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import logging
from shutil import move

# Set up logging
logging.basicConfig(filename='send_log.txt', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Email server settings (you can modify these based on your email provider)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_EMAIL = "jack.cfi@gmail.com"
SMTP_PASSWORD = "tpch qdrp fivt hguf"

# Folder paths
SOURCE_FOLDER = "tosend"
DEST_FOLDER = "sent"
EXCEL_FILE = "Email List.xlsx"

# Email body message
EMAIL_BODY = """
Dear Customer,

Please find attached your Accounts Receievable statement from CFI. 
Your prompt payment is appreciated.

If you have any questions, feel free to reach out.

Thank-you.

Chatham Fuel Injection
"""

# Function to send email with attachment
def send_email(to_email, file_path):
    # Prepare the message
    msg = MIMEMultipart()
    msg['From'] = 'sales@chathamfuel.com'
    msg['To'] = to_email
    msg['Subject'] = "Statement from CFI"
    
    # Attach the body message
    msg.attach(MIMEText(EMAIL_BODY, 'plain'))
    
    # Attach the PDF file
    try:
        with open(file_path, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
            msg.attach(part)
        
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail('sales@chathamfuel.com', to_email, msg.as_string())
        logging.info(f"Success: {to_email} {file_path}")
        print(f"Success: {to_email} {file_path}")
        
        return True
    except Exception as e:
        logging.error(f"Failed: {to_email} with error: {e}")
        print(f"Failed: {to_email} with error: {e}")
        return False

# Function to process the Excel file and send emails
def process_emails():
    # Load the Excel file
    try:
        df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
    except Exception as e:
        logging.error(f"Failed to read: {EXCEL_FILE}: {e}")
        print(f"Failed to read: {EXCEL_FILE}: {e}")
        return
    
    # Process each row in the Excel file
    for index, row in df.iterrows():
      
        filename = str(row.get('Act')) + '.pdf'
        # Ensure the filename is valid and has a PDF extension
        if not pd.isnull(filename):  #and filename.lower().endswith('.pdf'):
            file_path = os.path.join(SOURCE_FOLDER, filename)
            
            if os.path.exists(file_path):
                # Send the email with the file
                email = row.get('Email')
                # Skip if email is missing
                if pd.isnull(email):
                    logging.warning(f"Skipping {file_path} : Missing email")
                    print(f"Skipping {file_path} : Missing email")
                    continue

                if send_email(email, file_path):
                    # Move the file to the 'sent' folder
                    try:
                        move(file_path, os.path.join(DEST_FOLDER, filename))
                        #logging.info(f"Success: Moved {filename} to {DEST_FOLDER}")
                        #print(f"Success: Moved {filename} to {DEST_FOLDER}")
                    except Exception as e:
                        logging.error(f"Failed to move file {filename}: {e}")
                        print(f"Failed to move file {filename}: {e}")
            #else:
            #    logging.error(f"File {filename} not found in {SOURCE_FOLDER}")
            #    print(f"File {filename} not found in {SOURCE_FOLDER}")
        else:
            logging.warning(f"Skipping row {index + 1}: Invalid filename")
            print(f"Skipping row {index + 1}: Invalid filename")

if __name__ == "__main__":
    process_emails()
