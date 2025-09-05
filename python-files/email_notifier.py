import imaplib
import email
from email.header import decode_header
from time import sleep
from plyer import notification
import logging

# ----------- CONFIG -----------
EMAIL_ACCOUNT = "mike12123434@gmail.com"
# IMPORTANT: Gmail requires an App Password for accessing your account via IMAP/SMTP.
# Generate one from your Google Account security settings:
# https://myaccount.google.com/apppasswords
EMAIL_PASSWORD = "fmfe oqyc csze pchq"  # Replace with your actual App Password
IMAP_SERVER = "imap.gmail.com"
CHECK_INTERVAL_SECONDS = 60  # How often to check for new emails (in seconds)
NOTIFICATION_TIMEOUT_SECONDS = 10  # How long the notification stays visible
MAX_NOTIFICATION_TITLE_LENGTH = 64  # Max length for Windows notification title
MAX_NOTIFICATION_MESSAGE_LENGTH = 128 # Max length for Windows notification message
# -------------------------------

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def truncate_text(text, length):
    """Truncates text to a specified length, adding '...' if shortened."""
    if len(text) <= length:
        return text
    return text[:length-3] + "..."

def get_email_subject(msg):
    """
    Decodes and returns the subject of an email message.
    Handles potential encoding issues.
    """
    subject_header = msg["Subject"]
    if not subject_header:
        return "No Subject"

    decoded_parts = decode_header(subject_header)
    subject = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            try:
                # Try decoding with specified encoding or utf-8 as fallback
                subject += part.decode(encoding if encoding else "utf-8", errors="replace")
            except (UnicodeDecodeError, LookupError):
                # If decoding fails, use a placeholder or a more robust fallback
                subject += "[Undecodable Subject]"
        else:
            subject += part
    return subject

def check_emails():
    """Connects to Gmail, checks for unseen emails, and displays notifications."""
    try:
        logging.info("Connecting to IMAP server...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")
        logging.info("Successfully logged in and selected inbox.")

        # Search for unseen emails
        status, messages = mail.search(None, '(UNSEEN)')
        if status != 'OK':
            logging.error(f"Error searching for unseen emails: {status}")
            mail.logout()
            return

        unseen_email_ids = messages[0].split()

        if not unseen_email_ids:
            logging.info("No new unseen emails found.")
            mail.logout()
            return

        logging.info(f"Found {len(unseen_email_ids)} unseen email(s).")

        # Fetch and process each unseen email
        for email_id in unseen_email_ids:
            try:
                status, msg_data = mail.fetch(email_id, '(RFC822)')
                if status != 'OK':
                    logging.warning(f"Could not fetch email ID {email_id.decode()}: {status}")
                    continue

                msg = email.message_from_bytes(msg_data[0][1])

                subject = get_email_subject(msg)

                # Truncate subject for notification
                truncated_subject = truncate_text(subject, MAX_NOTIFICATION_MESSAGE_LENGTH)

                # Prepare notification content
                notification_title = truncate_text("New Email Received", MAX_NOTIFICATION_TITLE_LENGTH)
                notification_message = f"Subject: {truncated_subject}"

                # Display notification
                logging.info(f"Displaying notification for email: '{subject}'")
                notification.notify(
                    title=notification_title,
                    message=notification_message,
                    timeout=NOTIFICATION_TIMEOUT_SECONDS,
                    app_name="Email Notifier" # Optional: sets the app name for the notification
                )
            except Exception as email_err:
                logging.error(f"Error processing email ID {email_id.decode()}: {email_err}", exc_info=True)

        mail.logout()
        logging.info("Logged out from IMAP server.")

    except imaplib.IMAP4.error as imap_err:
        logging.error(f"IMAP Error: {imap_err}. Please check your email account, password, and network connection.", exc_info=True)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    logging.info("Email notifier started. Checking for emails every {} seconds.".format(CHECK_INTERVAL_SECONDS))
    # Optional: Perform an initial check immediately upon starting
    # check_emails()

    while True:
        try:
            check_emails()
            logging.info(f"Waiting for {CHECK_INTERVAL_SECONDS} seconds until next check.")
            sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logging.info("Email notifier stopped by user.")
            break
        except Exception as loop_err:
            logging.error(f"Error in main loop: {loop_err}. Attempting to continue.", exc_info=True)
            sleep(CHECK_INTERVAL_SECONDS) # Wait before retrying to avoid rapid error loops