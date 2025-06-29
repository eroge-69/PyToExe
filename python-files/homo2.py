import os
import time
import getpass
import random
import string
from datetime import datetime

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def simulate_vpn_connection():
    print("\n\033[97m--- Secure VPN Authentication Required ---\033[0m")
    for attempt in range(3):
        vpn_user = input("VPN User: ")
        vpn_pass = getpass.getpass("VPN Password: ")
        if vpn_user.lower() == "csewing" and vpn_pass == "1207":
            print("\n\033[94m" + "="*85)
            print(" "*22 + "DEUTSCHE BANK AG – VPN ACCESS GATEWAY")
            print("="*85 + "\033[0m")
            print("\n\033[97m--- Establishing Secure Connection ---\033[0m")
            for msg in [
                "Establishing encrypted tunnel...",
                "Connecting to Deutsche Bank Secure Gateway...",
                "Negotiating security protocols...",
                "Validating credentials...",
                "Finalizing VPN session...",
            ]:
                print(f"\033[93m{msg}\033[0m", end="", flush=True)
                for _ in range(random.randint(8, 14)):
                    print("▓", end="", flush=True)
                    time.sleep(random.uniform(0.03, 0.08))
                print(" \033[92m[OK]\033[0m")
                time.sleep(random.uniform(0.3, 0.7))
            print("\033[92mVPN authentication successful. Secure connection established.\033[0m")
            time.sleep(1.2)
            return True
        else:
            print("\033[91mInvalid VPN credentials. Please try again.\033[0m")
            time.sleep(1.5)
    print("\033[91mMaximum VPN authentication attempts exceeded. Exiting...\033[0m")
    exit(1)

def generate_session_id():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
    random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    return f"DBAG-{timestamp}-{random_string}"

def print_banner(session_id):
    print("\033[94m" + "="*85)
    print(" "*12 + "DEUTSCHE BANK AG – WEALTH MANAGEMENT DIVISION")
    print(" "*30 + f"SESSION ID: {session_id}")
    print("="*85 + "\033[0m")

def typewriter(message, color="", delay=0.03):
    if color:
        print(color, end="", flush=True)
    for char in message:
        print(char, end="", flush=True)
        time.sleep(delay)
    if color:
        print("\033[0m", end="", flush=True)
    print()

def loading_bar(task, duration=2):
    print(f"\n\033[93m{task}\033[0m", end="", flush=True)
    steps = random.randint(25, 35)
    for _ in range(steps):
        print("▓", end="", flush=True)
        time.sleep(duration/steps + random.uniform(-0.01, 0.01))
    print(" \033[92m[OK]\033[0m")

def authenticate_user():
    print("\n\033[97m--- Deutsche Bank Officer Authentication ---\033[0m")
    username = input("Employee ID: ")
    password = getpass.getpass("Security Code: ")
    if username.lower() == "gbritez" and password == "7664":
        typewriter(f"\nAuthentication successful. Access granted to Senior Wealth Officer Gregor Britez (Employee No.: DBAG7701).", "\033[92m")
        time.sleep(random.uniform(1, 1.5))
        return True
    else:
        typewriter("\nAuthentication failed. Invalid credentials.", "\033[91m")
        time.sleep(random.uniform(1.5, 2.5))
        return False

def input_wallets_and_shares():
    wallets = {}
    print("\nEnter beneficiary wallets and their share percentages.")
    print("When done, just press Enter on the wallet address.\n")
    total_share = 0.0
    i = 1
    while True:
        wallet = input(f"Wallet address #{i} (or press Enter to finish): ").strip()
        if not wallet:
            break
        if not (wallet.startswith("0x") and len(wallet) == 42 and all(c in string.hexdigits for c in wallet[2:])):
            print("\033[91mInvalid wallet address format. Must start with '0x' and be 42 hexadecimal characters.\033[0m")
            continue
        try:
            pct = float(input(f"Share for wallet #{i} (as percentage, e.g. 12.5): "))
        except ValueError:
            print("\033[91mInvalid input. Please enter a numeric value.\033[0m")
            continue
        if pct <= 0 or pct > 100:
            print("\033[91mShare must be between 0 and 100.\033[0m")
            continue
        wallets[wallet] = pct / 100.0
        total_share += pct / 100.0
        i += 1
    if not wallets:
        print("\033[91mAt least one wallet must be provided.\033[0m")
        return input_wallets_and_shares()
    if abs(total_share - 1.0) > 0.001:
        print("\033[93mWarning: Total share is not exactly 100%. It is {:.2f}%.\033[0m".format(total_share * 100))
    return wallets

def confirm_homologation(wallets):
    print("\n\033[96m" + "="*30 + " TRANSACTION CONFIRMATION " + "="*30 + "\033[0m")
    typewriter("Distribution to recipient wallets:", "\033[97m")
    for w, pct in wallets.items():
        typewriter(f"  → Wallet Address: {w} - Share: {pct*100:.2f}%", "\033[94m")
    typewriter(f"\nTotal Distribution: {sum(wallets.values())*100:.2f}%", "\033[93m")
    print("\033[96m" + "="*75 + "\033[0m\n")
    while True:
        choice = input("Confirm authorization and execute? (y/n): ").lower()
        if choice in ['y', 'n']:
            return choice == 'y'
        typewriter("Invalid input. Please enter 'y' or 'n'.", "\033[91m")

def process_and_validate(wallets):
    print("\n\033[93mProcessing transaction...", end="")
    time.sleep(random.uniform(0.5, 1))
    typewriter("Initializing Deutsche Bank secure routing protocols...", "\033[93m")
    loading_bar("[DBAG Infrastructure] Establishing secure core connection", random.uniform(2, 3))
    loading_bar("[BaFin Compliance] Running KYC/AML check", random.uniform(1.5, 2.5))
    loading_bar("[SWIFT Secure Channel] Establishing FIN handshake...", random.uniform(1, 2))
    time.sleep(random.uniform(0.2, 0.8))
    print("\033[92m[SWIFT Network] Handshake confirmed. Secure session active.\033[0m")

    print("\n\033[93m[Validation] Checking wallet addresses...\033[0m")
    time.sleep(random.uniform(1, 2))
    for i, w in enumerate(wallets.keys()):
        print(f"\033[94m[Validation] Wallet {i+1}/{len(wallets)}: {w} ... \033[0m", end="")
        time.sleep(random.uniform(0.8, 1.5))
        if not (w.startswith("0x") and len(w) == 42 and all(c in string.hexdigits for c in w[2:])):
            typewriter(f"\033[91m[Error] Invalid wallet format.\033[0m")
            return False
        elif random.random() < 0.03:  # realistic: lower chance of compliance trigger
            typewriter(f"\033[91m[Warning] Compliance alarm triggered.\033[0m")
            return False
        else:
            print("\033[92m[OK]\033[0m")

    print("\n\033[92mAll wallet addresses validated. Transaction approved.\033[0m")
    return True

def show_homologation_and_audit(wallets):
    print("\n\033[96m==== TRANSACTION AUTHORIZATION IN PROGRESS ====\033[0m")
    loading_bar("Logging to Deutsche Bank Distributed Ledger...", random.uniform(3, 4))

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f %Z%z")
    audit_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=12))
    print(f"\n\033[90m--- TRANSACTION AUDIT LOG - {now} ---")
    print(f"[AUDIT REFERENCE]: {audit_reference}")
    for w, pct in wallets.items():
        print(f"[BENEFICIARY]: {w} | [SHARE]: {pct*100:.2f}%")
    print(f"[SECURITY CODE]: DBAG-AUTH-{audit_reference[:6]}")
    # Realistic simulated IP (not just random 10-200)
    simulated_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
    print(f"[ORIGIN IP]: {simulated_ip}")
    print(f"[AUTHORIZING OFFICER]: Gregor Britez")
    print(f"[STATUS]: AUTHORIZATION COMPLETED – IMMUTABLE ENTRY\033[0m")

def main():
    clear()
    while True:
        session_id = generate_session_id()
        clear()
        print_banner(session_id)

        if simulate_vpn_connection():
            clear()
            print_banner(session_id)

            typewriter("\nPending transaction request loaded. Waiting for officer input...", "\033[93m")
            time.sleep(random.uniform(1.5, 3))

            wallets = input_wallets_and_shares()

            if process_and_validate(wallets):
                if confirm_homologation(wallets):
                    show_homologation_and_audit(wallets)
                    print("\n\033[95m" + "="*80)
                    print(" "*16 + "DEUTSCHE BANK SECURITY NOTICE")
                    print(" "*4 + "- Security codes must never be shared.")
                    print(" "*4 + "- Deutsche Bank will never ask for your full credentials.")
                    print(" "*4 + "- Regularly check your client portal for suspicious activities.")
                    print("="*80 + "\033[0m")
                    print("\n\033[92mTransaction successfully authorized and logged.\033[0m")
                    input("Press Enter to return to the main screen...")
                else:
                    print("\n\033[91mTransaction cancelled by officer. No changes made.\033[0m")
                    input("Press Enter to return to the main screen...")
            else:
                print("\n\033[91mTransaction failed due to validation errors.\033[0m")
                input("Press Enter to return to the main screen...")

if __name__ == "__main__":
    main()