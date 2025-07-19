import smtplib
from email.message import EmailMessage
import csv
from datetime import datetime

def check_smtp(email, app_password, recipient=None):
    result = {
        "name": "madara smtp",
        "email": email,
        "status": "",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(email, app_password)
            print(f"[madara smtp] [+] Login successful for: {email}")

            if recipient:
                msg = EmailMessage()
                msg['Subject'] = 'SMTP Check Success'
                msg['From'] = email
                msg['To'] = recipient
                msg.set_content('madara smtp test message.')

                smtp.send_message(msg)
                print(f"[madara smtp] [+] Test email sent to {recipient}")
            result["status"] = "Success"
    except smtplib.SMTPAuthenticationError:
        print(f"[madara smtp] [-] Auth failed for: {email}")
        result["status"] = "Auth Failed"
    except Exception as e:
        print(f"[madara smtp] [-] Connection error for {email}: {e}")
        result["status"] = f"Error: {str(e)}"
    return result

def save_to_csv(data, filename="smtp_check_log.csv"):
    fieldnames = ["name", "email", "status", "timestamp"]
    try:
        with open(filename, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if file.tell() == 0:  # write header only if file is new
                writer.writeheader()
            writer.writerow(data)
        print(f"[madara smtp] [+] Result saved to {filename}")
    except Exception as e:
        print(f"[madara smtp] [-] Error saving to CSV: {e}")

# Example usage
email = "your_email@gmail.com"
app_password = "your_16_char_app_password"
recipient = "test@example.com"  # Optional

result = check_smtp(email, app_password, recipient)
save_to_csv(result)