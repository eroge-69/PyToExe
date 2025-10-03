import win32net
import win32netcon
import win32security
import win32api
import win32con
import sys
import ctypes

# Configurări
PASSWORD = "Parola123!"  # Parolă unică pentru toți utilizatorii (respectă cerințele de complexitate)
NUM_USERS = 5           # Numărul de utilizatori de creat
USER_PREFIX = "User"     # Prefix pentru numele utilizatorilor
IS_ADMIN = False        # True pentru administratori, False pentru utilizatori normali

def is_admin():
    """Verifică dacă scriptul rulează cu privilegii de administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def create_local_user(username, password, is_admin=False):
    """Creează un utilizator local cu parolă și setări specificate"""
    try:
        # Verifică dacă utilizatorul există deja
        try:
            win32net.NetUserGetInfo(None, username, 1)
            print(f"Utilizatorul '{username}' există deja. Se trece peste.")
            return False
        except win32net.error as e:
            if e.winerror != 2221:  # NERR_UserNotFound
                raise

        # Pregătește datele utilizatorului
        user_info = {
            'name': username,
            'password': password,
            'priv': win32netcon.USER_PRIV_USER,
            'home_dir': None,
            'comment': None,
            'flags': win32netcon.UF_NORMAL_ACCOUNT,
            'script_path': None
        }

        # Creează utilizatorul
        win32net.NetUserAdd(None, 1, user_info)

        # Setează parola să expire la prima logare
        user_info_3 = {
            'name': username,
            'password_expired': 1  # Forțează schimbarea parolei la prima logare
        }
        win32net.NetUserSetInfo(None, username, 3, user_info_3)

        # Adaugă utilizatorul în grupul corespunzător
        if is_admin:
            add_user_to_admin_group(username)
            print(f"Utilizatorul '{username}' a fost creat cu drepturi de administrator.")
        else:
            print(f"Utilizatorul '{username}' a fost creat cu drepturi standard.")

        return True

    except Exception as e:
        print(f"Eroare la crearea utilizatorului '{username}': {str(e)}")
        return False

def add_user_to_admin_group(username):
    """Adaugă un utilizator în grupul de administratori"""
    try:
        domain = win32api.GetComputerName()
        member_info = {
            'domainandname': f"{domain}\\{username}"
        }
        win32net.NetLocalGroupAddMembers(None, "Administrators", 3, [member_info])
    except Exception as e:
        print(f"Eroare la adăugarea în grupul de administratori: {str(e)}")
        raise

def main():
    """Funcția principală a scriptului"""
    if not is_admin():
        print("Eroare: Acest script trebuie rulat cu privilegii de administrator!")
        sys.exit(1)

    if sys.platform != "win32":
        print("Eroare: Acest script rulează doar pe Windows!")
        sys.exit(1)

    print(f"Se creează {NUM_USERS} utilizatori locali...")
    print(f"Parolă inițială: {PASSWORD}")
    print(f"Drepturi: {'Administrator' if IS_ADMIN else 'Utilizator standard'}")
    print("-" * 50)

    created_users = []
    for i in range(1, NUM_USERS + 1):
        username = f"{USER_PREFIX}{i}"
        if create_local_user(username, PASSWORD, IS_ADMIN):
            created_users.append(username)

    print("-" * 50)
    print(f"Proces încheiat. {len(created_users)} utilizatori creați cu succes:")
    for user in created_users:
        print(f"- {user}")

if __name__ == "__main__":
    main()