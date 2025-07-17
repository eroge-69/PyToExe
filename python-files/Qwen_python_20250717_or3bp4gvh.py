from core.smtp_handler import SMTPHandler
from core.lead_generator import generate_leads, save_leads
from core.utils import read_file_lines, delay
import random

def main():
    print("[+] Loading SMTPs...")
    smtps = read_file_lines("data/smtps.txt")
    handler = SMTPHandler(smtps)
    handler.check_smtps()

    print("[+] Loading content...")
    messages = read_file_lines("data/messages.txt")
    subjects = read_file_lines("data/subjects.txt")
    links = read_file_lines("data/links.txt")

    print("[+] Generating leads...")
    leads = generate_leads(200)
    save_leads(leads)

    print("[+] Starting spam campaign...")
    handler.connect()
    for lead in read_file_lines("data/leads.txt"):
        subject = random.choice(subjects)
        message = random.choice(messages).replace("{link}", random.choice(links))
        if not handler.send_email(lead, subject, message):
            print("[!] Switching SMTP...")
        delay(2, 0.5)

    print("[+] Campaign finished.")

if __name__ == "__main__":
    main()