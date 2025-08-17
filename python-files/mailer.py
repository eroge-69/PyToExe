import smtplib
import os
import sys
import time
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, as_completed

from colorama import init, Fore, Style

init(autoreset=True)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def cursor_up(n=1):
    print(f"\033[{n}A", end='')

def read_smtps_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    return [tuple(line.split('|')) for line in lines]

def read_smtps_from_line(line):
    return [tuple(s.strip().split('|')) for s in line.split(',') if s.strip()]

def test_smtp(host, port, user, pwd):
    try:
        server = smtplib.SMTP(host, int(port), timeout=10)
        server.starttls()
        server.login(user, pwd)
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)

def read_emails(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def send_email(smtp_info, to_email, subject, body, timeout=10):
    host, port, user, pwd = smtp_info
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html', 'utf-8'))
    try:
        server = smtplib.SMTP(host, int(port), timeout=timeout)
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, to_email, msg.as_string())
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)

def p(msg, prefix='[+]'):
    if msg.strip() == "":
        print()
    else:
        print(f"{prefix} {msg}")

def input_with_prefix(prompt):
    if prompt.strip() == "":
        print()
        return input()
    else:
        return input(prompt)

def color_white(text):
    return Fore.LIGHTWHITE_EX + Style.BRIGHT + text + Style.RESET_ALL

def color_red(text):
    return Fore.LIGHTRED_EX + Style.BRIGHT + text + Style.RESET_ALL

def color_gray(text):
    return Fore.LIGHTBLACK_EX + text + Style.RESET_ALL

def color_green(text):
    return Fore.LIGHTGREEN_EX + Style.BRIGHT + text + Style.RESET_ALL

def color_yellow(text):
    return Fore.LIGHTYELLOW_EX + Style.BRIGHT + text + Style.RESET_ALL

def main():
    clear_console()
    p(color_yellow("=== Mail Sender (SMTP Rotatif/Unique) ===\n"), color_yellow('[!]'))
    mode = ""
    while mode not in ['1', '2']:
        p(color_white("Choisissez le mode :"), color_yellow('[?]'))
        p(color_white("1. SMTP unique"), color_yellow('[?]'))
        p(color_white("2. SMTP rotatif"), color_yellow('[?]'))
        mode = input_with_prefix(color_yellow("[?] Entrez 1 ou 2 : ")).strip()
        clear_console()

    smtp_list = []
    if mode == '1':
        p(color_white("Entrez le SMTP au format : HOTE|PORT|EMAIL|MOTDEPASSE"), color_yellow('[?]'))
        smtp_line = input_with_prefix(color_yellow("[?] SMTP : ")).strip()
        try:
            host, port, user, pwd = smtp_line.split('|')
            smtp_list = [(host, port, user, pwd)]
        except:
            p(color_red("Format invalide. Sortie."), color_red('[-]'))
            return
    else:
        p(color_white("SMTP rotatif. Choisissez la méthode d'entrée :"), color_yellow('[?]'))
        p(color_white("1. fichier.txt (un par ligne : HOTE|PORT|EMAIL|MOTDEPASSE)"), color_yellow('[?]'))
        p(color_white("2. Manuel (séparé par des virgules : HOTE|PORT|EMAIL|MOTDEPASSE,HOTE|PORT|EMAIL|MOTDEPASSE,...)"), color_yellow('[?]'))
        rot_mode = ""
        while rot_mode not in ['1', '2']:
            rot_mode = input_with_prefix(color_yellow("[?] Entrez 1 ou 2 : ")).strip()
        if rot_mode == '1':
            filename = input_with_prefix(color_yellow("[?] Entrez le chemin vers fichier.txt : ")).strip()
            if not os.path.isfile(filename):
                p(color_red("Fichier introuvable. Sortie."), color_red('[-]'))
                return
            smtp_list = read_smtps_from_file(filename)
        else:
            smtp_line = input_with_prefix(color_yellow("[?] Entrez les SMTPs séparés par des virgules : ")).strip()
            smtp_list = read_smtps_from_line(smtp_line)
        if not smtp_list:
            p(color_red("Aucun SMTP valide trouvé. Sortie."), color_red('[-]'))
            return

    print()
    print(color_yellow("Test des SMTP(s)..."))
    valid_smtps = []
    invalid_smtps = []
    lock = Lock()
    results = [None] * len(smtp_list)

    def smtp_test_worker(idx, smtp):
        host, port, user, pwd = smtp
        ok, err = test_smtp(host, port, user, pwd)
        with lock:
            results[idx] = (ok, smtp, err)
            valids = sum(1 for r in results if r and r[0])
            invalids = sum(1 for r in results if r and not r[0])
            cursor_up(2)
            print(color_green(f"Valides   : {str(valids).rjust(4)}{' ' * 4}"))
            print(color_red(f"Invalides : {str(invalids).rjust(4)}{' ' * 4}"))

    print(color_green("Valides   :    0    "))
    print(color_red("Invalides :    0    "))

    max_workers = len(smtp_list)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for idx, smtp in enumerate(smtp_list):
            futures.append(executor.submit(smtp_test_worker, idx, smtp))
        for f in futures:
            f.result()

    for r in results:
        if r is None:
            continue
        ok, smtp, err = r
        if ok:
            valid_smtps.append(smtp)
        else:
            invalid_smtps.append((smtp, err))

    if not valid_smtps:
        p(color_red("Aucun SMTP valide. Sortie."), color_red('[-]'))
        return
    smtp_list = valid_smtps

    print()
    print(color_white("Entrez le chemin vers le fichier .txt contenant les emails destinataires (un par ligne) :"))
    email_file = input_with_prefix(color_yellow("[?] Fichier : ")).strip()
    if not os.path.isfile(email_file):
        p(color_red("Fichier introuvable. Sortie."), color_red('[-]'))
        return
    recipients = read_emails(email_file)
    if not recipients:
        p(color_red("Aucun destinataire trouvé. Sortie."), color_red('[-]'))
        return

    print()
    print(color_green(f"[+] {len(recipients)} emails trouvés dans la liste."))
    while True:
        workers_input = input_with_prefix(color_yellow("[?] Combien de workers pour envoyer les emails ? (1 par défaut) : ")).strip()
        if workers_input == "":
            num_workers = 1
            break
        try:
            num_workers = int(workers_input)
            if num_workers < 1:
                print(color_red("Le nombre de workers doit être au moins 1."))
            else:
                break
        except ValueError:
            print(color_red("Veuillez entrer un nombre entier valide."))

    print()
    print(color_white("Entrez l'objet de l'email :"))
    subject = input_with_prefix(color_yellow("[?] Objet : ")).strip()
    print()
    print(color_white("Entrez le chemin vers le fichier HTML pour le corps de l'email :"))
    html_path = input_with_prefix(color_yellow("[?] Fichier HTML : ")).strip()
    if not os.path.isfile(html_path):
        p(color_red("Fichier HTML introuvable. Sortie."), color_red('[-]'))
        return
    with open(html_path, 'r', encoding='utf-8') as f:
        body = f.read()

    total = len(recipients)
    sent = 0
    failed = 0
    lock = Lock()
    progress = {'sent': 0, 'failed': 0}
    email_status = {}  # email: (status, smtp_used, error)
    max_retries = len(smtp_list)
    num_width = len(str(total))
    summary_lines = 7

    def print_summary(current_email="", status="", sent=0, failed=0, retry_list=None, current_smtp=None):
        percent = int(round((sent) / total * 100)) if total > 0 else 100
        retry_count = len(retry_list) if retry_list else 0
        total_str = f"{total:>{num_width}}"
        sent_str = f"{sent:>{num_width}}"
        failed_str = f"{failed:>{num_width}}"
        retry_str = f"{retry_count:>{num_width}}"
        percent_str = f"{percent:>3}"
        pad = 6
        print(color_white(f"Total :     {total_str}{' ' * pad}"))
        print(color_green(f"Envoyés :   {sent_str}{' ' * pad}"))
        print(color_red(f"Échecs :    {failed_str}{' ' * pad}"))
        if current_email:
            max_email_len = 60
            email_disp = (current_email[:max_email_len] + '...') if len(current_email) > max_email_len else current_email
            status_disp = f"{email_disp} -> {status}"
            status_disp = status_disp + ' ' * (max_email_len + 20 - len(status_disp)) if len(status_disp) < (max_email_len + 20) else status_disp
            if "ECHEC" in status:
                print(color_red(f"Actuel :    {status_disp}"))
            elif "ENVOYÉ" in status:
                print(color_green(f"Actuel :    {status_disp}"))
            else:
                print(color_white(f"Actuel :    {status_disp}"))
        else:
            print(color_white("Actuel :    " + " " * (num_width + 30)))
        print(color_yellow(f"Progression : {percent_str}%{' ' * pad}"))
        if retry_count > 0:
            print(color_red(f"En attente de retry : {retry_str}{' ' * pad}"))
        else:
            print(color_white(f"En attente de retry : {retry_str}{' ' * pad}"))
        if current_smtp:
            smtp_disp = f"{current_smtp[0]}|{current_smtp[1]}|{current_smtp[2]}"
            smtp_disp = smtp_disp + ' ' * (40 - len(smtp_disp)) if len(smtp_disp) < 40 else smtp_disp
            print(color_yellow(f"SMTP courant : {smtp_disp}"))
        else:
            print(color_yellow("SMTP courant : N/A" + " " * 30))

    for i in range(summary_lines):
        print()
    cursor_up(summary_lines)
    print_summary(sent=0, failed=0, retry_list=[], current_smtp=smtp_list[0] if smtp_list else None)

    print()
    print(color_yellow("Début de l'envoi...\n"))

    # --- SEND ALL EMAILS SIMULTANEOUSLY, RETRY WITH DIFFERENT SMTPs IF FAIL ---

    # For each email, try all SMTPs in order until one works, up to max_retries
    # All emails are sent in parallel (up to a high concurrency limit)
    # Each email's retries use a different SMTP (rotating)

    # Prepare retry tracking
    retry_list = []
    max_parallel = min(1000, total)  # Don't spawn more than 1000 threads

    def send_email_with_retries(to_email):
        nonlocal sent, failed
        last_err = ""
        smtp_used = None
        for attempt in range(max_retries):
            smtp_idx = attempt % len(smtp_list)
            smtp = smtp_list[smtp_idx]
            ok, err = send_email(smtp, to_email, subject, body, timeout=10)
            with lock:
                if ok:
                    sent += 1
                    email_status[to_email] = ("ENVOYÉ" if attempt == 0 else f"ENVOYÉ (RETRY {attempt})", smtp, "")
                    status = color_green(email_status[to_email][0])
                    cursor_up(summary_lines)
                    print_summary(
                        current_email=to_email,
                        status=status,
                        sent=sent,
                        failed=failed,
                        retry_list=retry_list,
                        current_smtp=smtp
                    )
                    return
                else:
                    last_err = err
        with lock:
            failed += 1
            email_status[to_email] = ("ECHEC", smtp, last_err)
            retry_list.append(to_email)
            status = color_red(f"ECHEC ({last_err})")
            cursor_up(summary_lines)
            print_summary(
                current_email=to_email,
                status=status,
                sent=sent,
                failed=failed,
                retry_list=retry_list,
                current_smtp=smtp
            )

    # Send all emails in parallel
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = {executor.submit(send_email_with_retries, email): email for email in recipients}
        for f in as_completed(futures):
            pass  # All progress is handled in send_email_with_retries

    print()
    print(color_yellow("Terminé.\n"))
    failed_list = [(email, email_status[email][2]) for email in recipients if email_status.get(email, ("", "", ""))[0].startswith("ECHEC")]
    if failed_list:
        p(color_red("Emails en échec :"), color_red('[-]'))
        for email, err in failed_list:
            print(color_red(f"[-] {email} : {err}"))
    retry_left = [email for email in recipients if email_status.get(email, ("", "", ""))[0].startswith("ECHEC")]
    if retry_left:
        p(color_red("Emails en attente de retry non envoyés :"), color_red('[-]'))
        for email in retry_left:
            print(color_red(f"[-] {email}"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color_red("\n[!] Arrêté par l'utilisateur."))