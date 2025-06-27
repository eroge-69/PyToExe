import os
import smtplib
import time
import threading
import random
import string
import queue
import sys
import requests
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formataddr

RED = '\33[31m'
GREEN = '\33[32m'
YELLOW = '\33[33m'
CYAN = '\33[36m'
WHITE = '\33[37m'

stop_flag = threading.Event()
remaining_emails = 0
remaining_lock = threading.Lock()
custom_sender_name = None

successful_logins = 0
total_accounts = 0
success_lock = threading.Lock()

first_names = [
    "Max", "Sophie", "Lukas", "Emily", "Ben", "Emma", "Finn", "Lea", "Paul", "Marie",
    "Leon", "Hannah", "Elias", "Anna", "Noah", "Mia", "Luis", "Laura", "Tim", "Lina",
    "Felix", "Clara", "Julian", "Amelie", "Moritz", "Mila", "Tom", "Lilly", "Jan", "Nele",
    "Fabian", "Johanna", "Erik", "Luisa", "Nico", "Helena", "Jonas", "Fiona", "Tobias", "Lara",
    "Simon", "Paula", "Jannis", "Greta", "Daniel", "Franziska", "David", "Annika", "Kevin", "Ronja",
    "Sebastian", "Mira", "Philipp", "Nina", "Dennis", "Sarah", "Matthias", "Antonia", "Stefan", "Alina",
    "Johannes", "Melissa", "Oliver", "Theresa", "Christian", "Vanessa", "Florian", "Katharina", "Markus", "Julia",
    "Alexander", "Lisa", "Martin", "Carina", "Patrick", "Peter", "Monika", "Heiko", "Anja", "Dirk",
    "Tanja", "Uwe", "Katrin", "Ralf", "Silke", "Frank", "Melanie", "Jürgen", "Gabi", "Holger",
    "Jens", "Petra", "Rainer", "Birgit", "Thorsten", "Heike", "Dieter", "Sabrina", "Bernd", "Stefanie",
    "Lothar", "Sandra", "Reinhard", "Kerstin", "Wolfgang", "Nicole", "Manfred", "Claudia", "Andreas", "Elke",
    "John", "Emma", "William", "Olivia", "James", "Ava", "Logan", "Isabella", "Lucas", "Sophia",
    "Henry", "Charlotte", "Alexander", "Amelia", "Michael", "Harper", "Ethan", "Evelyn", "Daniel", "Abigail",
    "Matthew", "Ella", "Joseph", "Scarlett", "David", "Grace", "Jackson", "Chloe", "Samuel", "Lily",
    "Sebastian", "Victoria", "Aiden", "Aria", "Owen", "Penelope", "Wyatt", "Layla", "Gabriel", "Riley",
    "Carter", "Zoey", "Jayden", "Nora", "Luke", "Lillian", "Grayson", "Addison", "Levi", "Aubrey",
    "Isaac", "Ellie", "Anthony", "Stella", "Dylan", "Natalie", "Lincoln", "Zoe", "Joshua", "Leah",
    "Andrew", "Hazel", "Christopher", "Violet", "Nathan", "Aurora", "Thomas", "Savannah", "Caleb", "Audrey",
    "Ryan", "Brooklyn", "Asher", "Bella", "Nathaniel", "Claire", "Aaron", "Skylar", "Charles", "Lucy",
    "Christian", "Anna", "Hunter", "Caroline", "Adrian", "Genesis", "Leo", "Kennedy", "Jonathan", "Sadie",
    "Isaiah", "Aaliyah", "Thomas", "Allison", "Brayden", "Gabriella", "Eli", "Madelyn", "Landon", "Cora",
    "Nicholas", "Ruby", "Julian", "Serenity", "Hudson", "Autumn", "Robert", "Peyton", "Easton", "Elena",
    "Jaxon", "Naomi", "Everett", "Alice", "Miles", "Eliana", "Cole", "Kinsley", "Declan", "Ariana",
    "Carson", "Gabrielle", "Parker", "Maya", "Xavier", "Allie", "Weston", "London", "Greyson", "Faith",
    "Jason", "Josephine", "Chase", "Emery", "Micah", "Lyla", "Zachary", "Ayla", "Bentley", "Rose",
    "Ayden", "Isla", "Axel", "Hadley", "Brody", "Delilah", "Maxwell", "Bailey", "Camden", "Maria",
    "Roman", "Quinn", "Gael", "Jade", "Ryker", "Taylor", "Diego", "Morgan", "Kaiden", "Brielle"
]

last_names = [
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Hoffmann", "Schäfer",
    "Koch", "Bauer", "Richter", "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann", "Braun",
    "Krüger", "Hofmann", "Hartmann", "Lange", "Schmitt", "Werner", "Schmitz", "Krause", "Meier", "Lehmann",
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson",
    "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts",
    "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker", "Cruz", "Edwards", "Collins", "Reyes",
    "Stewart", "Morris", "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper"
]

name_combinations = random.sample([f"{fn} {ln}" for fn in first_names for ln in last_names], k=len(first_names)*len(last_names))
name_iterator = iter(name_combinations)

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    banner = """
                                             _ _               _             
                                            (_) |             | |            
  _ __ ___ _____   _    __ _ _ __ ___   __ _ _| |  _ __  _   _| | _____ _ __ 
 | '__/ __|_  / | | |  / _` | '_ ` _ \\ / _` | | | | '_ \\| | | | |/ / _ \\ '__|
 | |  \\__ \\/ /| |_| | | (_| | | | | | | (_| | | | | | | | |_| |   <  __/ |   
 |_|  |___/___|\\__, |  \\__, |_| |_| |_|\\__,_|_|_| |_| |_|\\__,_|_|\\_\\___|_|   
                __/ |   __/ |                                                
               |___/   |___/                                                 
"""
    print(RED + banner)
    print(CYAN + "Socials: https://reaszy.com/")

def read_credentials():
    credentials = []
    try:
        with open("key.txt", "r") as f:
            for line in f:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    credentials.append((parts[0], parts[1]))
    except FileNotFoundError:
        pass
    return credentials

def generate_random_suffix(length=5):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def is_valid_email(email):
    pattern = r'^[^@\s]+@[^@\s]+\.[^@\s]+$'
    return re.match(pattern, email) is not None

def email_sender_worker(sender_email, password, recipient_email, base_subject, message_body,
                        task_queue, is_html, login_barrier, attachment_list, delay_range):
    global remaining_emails, successful_logins
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(sender_email, password)
        with success_lock:
            successful_logins += 1
            print(GREEN + f"[{successful_logins:02}/{total_accounts}][{sender_email}] Login successful.")
    except Exception as e:
        print(RED + f"[{sender_email}] Login failed: {e}")
        login_barrier.abort()
        return
    try:
        login_barrier.wait()
    except threading.BrokenBarrierError:
        return
    time.sleep(random.uniform(*delay_range))
    while not task_queue.empty() and not stop_flag.is_set():
        try:
            task_queue.get_nowait()
        except queue.Empty:
            break
        if stop_flag.is_set():
            break
        unique_code = generate_random_suffix()
        full_subject = base_subject + f" | {unique_code}" if base_subject else ""
        final_message_body = message_body.strip() + f"<br><br>(ID: {unique_code})" if is_html else message_body.strip() + f"\n\n(ID: {unique_code})"
        msg = MIMEMultipart("mixed")
        msg["Subject"] = full_subject
        if custom_sender_name:
            display_name = custom_sender_name
        else:
            try:
                display_name = next(name_iterator)
            except StopIteration:
                display_name = "Anonymous Sender"
        msg["From"] = formataddr((display_name, sender_email))
        msg["To"] = recipient_email
        mime_part = MIMEText(final_message_body, "html" if is_html else "plain")
        msg.attach(mime_part)
        for filename, filedata in attachment_list:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(filedata)
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")
            msg.attach(part)
        try:
            server.sendmail(sender_email, recipient_email, msg.as_string())
            with remaining_lock:
                remaining_emails -= 1
                print(GREEN + f"[→] {sender_email} -> {recipient_email} | {unique_code} | {remaining_emails} remaining")
        except Exception as e:
            print(RED + f"[{sender_email}] Send failed: {e}")
            task_queue.put(1)
        if stop_flag.is_set():
            break
        time.sleep(random.uniform(*delay_range))

    server.quit()

def prompt_return_or_exit():
    print(YELLOW + "\nPress Enter to return.")
    input()
    return True

def run_email_sender():
    global remaining_emails, custom_sender_name, total_accounts
    stop_flag.clear()

    while True:
        choice = input(YELLOW + "Choose sender name type - (r)andom real names or (c)ustom name? " + WHITE).strip().lower()
        if choice == "r":
            custom_sender_name = None
            break
        elif choice == "c":
            custom_sender_name = input(YELLOW + "Enter your custom sender name: "+ WHITE).strip()
            break
        else:
            print(RED + "Invalid input. Please type 'r' or 'c'." + WHITE)

    credentials = read_credentials()
    if not credentials:
        print(RED + "No credentials found in key.txt. Exiting." + WHITE)
        input()
        return False

    total_accounts = len(credentials)

    while True:
        try:
            while True:
                try:
                    num_recipients = int(input(YELLOW + "How many recipients?: " + WHITE))
                    if num_recipients > 0:
                        break
                except ValueError:
                    pass
                print(RED + "Please enter a valid number." + WHITE)

            recipients = []
            print(YELLOW + "Enter recipient email addresses (one per line):" + WHITE)
            for i in range(1, num_recipients + 1):
                while True:
                    email = input(YELLOW + f"{i}: " + WHITE).strip()
                    if is_valid_email(email):
                        recipients.append(email)
                        break
                    else:
                        print(RED + "Invalid email format. Please enter a valid email like name@domain.com." + WHITE)

            base_subject = input(YELLOW + "Subject (optional): " + WHITE).strip()

            print(YELLOW + "Enter your message (multiline, html support, type 'END' + enter to finish):" + WHITE)
            message_lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                message_lines.append(line)
            message_body = "\n".join(message_lines).strip()

            while True:
                html_input = input(YELLOW + "Is this message HTML? (y/n): " + WHITE).strip().lower()
                if html_input in ["y", "n"]:
                    is_html = html_input == "y"
                    break
                else:
                    print(RED + "Invalid input. Please enter 'y' or 'n'." + WHITE)

            while True:
                try:
                    num_attachments = int(input(YELLOW + "How many files do you want to attach?: " + WHITE))
                    if num_attachments >= 0:
                        break
                except ValueError:
                    pass
                print(RED + "Please enter a valid number (0 or higher)." + WHITE)

            attachment_list = []
            for i in range(1, num_attachments + 1):
                while True:
                    path = input(YELLOW + f"Enter path or URL for file {i}: " + WHITE).strip().strip('"')
                    try:
                        if path.startswith("http://") or path.startswith("https://"):
                            print(YELLOW + f"Downloading: {path}" + WHITE)
                            response = requests.get(path)
                            response.raise_for_status()
                            file_data = response.content
                            file_name = path.split("/")[-1]
                        else:
                            print(YELLOW + f"Reading file: {path}" + WHITE)
                            file_name = os.path.basename(path)
                            with open(path, "rb") as f:
                                file_data = f.read()
                        attachment_list.append((file_name, file_data))
                        print(GREEN + f"Attached: {file_name}" + WHITE)
                        break
                    except Exception as e:
                        print(RED + f"Failed to attach {path}: {e}" + WHITE)

            while True:
                try:
                    total_to_send = int(input(YELLOW + "Number of emails to send to each recipient: " + WHITE))
                    if total_to_send > 0:
                        break
                except ValueError:
                    print(RED + "Please enter a valid positive number." + WHITE)

            while True:
                speed = input(YELLOW + "Speed? (f = fast, n = normal, s = slow, v = very slow): " + WHITE).strip().lower()
                if speed == "f":
                    delay_range = (1, 5)
                    break
                elif speed == "n":
                    delay_range = (4, 12)
                    break
                elif speed == "s":
                    delay_range = (7, 16)
                    break
                elif speed == "v":
                    delay_range = (20, 60)
                    break
                else:
                    print(RED + "Invalid input. Enter f, n, s, or v." + WHITE)

            break
        except (KeyboardInterrupt, EOFError):
            return False

    with remaining_lock:
        remaining_emails = total_to_send * len(recipients)

    total_emails_needed = total_to_send * len(recipients)
    selected_credentials = random.sample(credentials, min(len(credentials), total_emails_needed))

    login_barrier = threading.Barrier(len(selected_credentials))
    threads = []

    task_queues = []
    for recipient in recipients:
        q = queue.Queue()
        for _ in range(total_to_send):
            q.put(1)
        task_queues.append((recipient, q))

    index = 0
    for email, pwd in selected_credentials:
        if index >= len(task_queues):
            index = 0
        recipient, task_queue = task_queues[index]
        index += 1

        t = threading.Thread(target=email_sender_worker,
                             args=(email, pwd, recipient, base_subject, message_body,
                                   task_queue, is_html, login_barrier, attachment_list, delay_range),
                             daemon=True)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    if remaining_emails <= 0 and not stop_flag.is_set():
        print(GREEN + f"\nSuccessfully sent {total_to_send * len(recipients)} emails." + WHITE)
    else:
        print(RED + "\nSending was stopped." + WHITE)

    return prompt_return_or_exit()

try:
    while True:
        clear()
        print_banner()
        should_continue = run_email_sender()
        if not should_continue:
            break
except Exception as e:
    print(RED + f"\nAn error occurred: {e}" + WHITE)
    input(WHITE + "\nPress Enter to exit." + WHITE)
except KeyboardInterrupt:
    print(RED + "\nInterrupted." + WHITE)
    input(WHITE + "\nPress Enter to exit." + WHITE)