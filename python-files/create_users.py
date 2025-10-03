import subprocess
import os

def run_powershell_command(command):
    """Execută o comandă PowerShell și returnează output-ul și codul de ieșire."""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        print(f"❌ Eroare la executarea comenzii PowerShell:\n{e.stderr}")
        return None, e.returncode

def create_local_user(username, password, is_admin=False, expire_days=30):
    """
    Creează un utilizator local în Windows 10.
    
    :param username: Numele utilizatorului
    :param password: Parola utilizatorului
    :param is_admin: Dacă este administrator (True) sau utilizator obișnuit (False)
    :param expire_days: Număr de zile până la expirarea parolei
    """
    print(f"\n🚀 Creare utilizator: {username}")

    # 1. Creează utilizatorul
    cmd_create = f'net user "{username}" "{password}" /add /expires:{expire_days} /active:yes'
    stdout, code = run_powershell_command(cmd_create)
    if code != 0:
        print(f"❌ Eroare la crearea utilizatorului {username}")
        return False

    # 2. Forțează schimbarea parolei la prima logare
    cmd_password_change = f'wmic useraccount where name="{username}" set PasswordChangeRequired=true'
    stdout, code = run_powershell_command(cmd_password_change)
    if code != 0:
        print(f"⚠️ Nu s-a putut forța schimbarea parolei pentru {username}")

    # 3. Adaugă în grupul corespunzător
    group = "Administrators" if is_admin else "Users"
    cmd_add_group = f'net localgroup "{group}" "{username}" /add'
    stdout, code = run_powershell_command(cmd_add_group)
    if code != 0:
        print(f"❌ Eroare la adăugarea în grupul {group} pentru {username}")
        return False

    print(f"✅ Utilizatorul {username} a fost creat cu succes!")
    print(f"   ➤ Rol: {'Administrator' if is_admin else 'Utilizator'}")
    print(f"   ➤ Parola expiră în {expire_days} zile")
    print(f"   ➤ Schimbarea parolei este obligatorie la prima logare")

    return True

def main():
    print("🔧 Generator de utilizatori locali pentru Windows 10")
    print("=" * 50)

    # Verifică dacă rulează ca administrator
    if not os.environ.get('USERNAME') == 'SYSTEM' and not os.path.exists(r'C:\Windows\System32\cmd.exe'):
        try:
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if not is_admin:
                print("❗ Scriptul trebuie rulat cu drepturi de administrator!")
                input("Apasă ENTER pentru a închide...")
                return
        except:
            pass  # Dacă nu se poate verifica, continuă cu atenție

    # Configurație
    base_username = "U"      # Prefix pentru numele utilizatorilor
    password = "Parola123!"     # Parolă comună (poți schimba)
    num_users = 3               # Câți utilizatori să creeze
    expire_days = 30            # Zile până la expirarea parolei
    admin_count = 1             # Primii X utilizatori sunt administratori

    print(f"📝 Configurație:")
    print(f"   ➤ Prefix nume: {base_username}")
    print(f"   ➤ Parolă: {password}")
    print(f"   ➤ Număr utilizatori: {num_users}")
    print(f"   ➤ Expire după: {expire_days} zile")
    print(f"   ➤ Administratori: primii {admin_count}\n")

    # Creează utilizatorii
    for i in range(1, num_users + 1):
        username = f"{base_username}{i:03d}"
        is_admin = i <= admin_count
        create_local_user(username, password, is_admin, expire_days)

    print("\n🎉 Toți utilizatorii au fost creați cu succes!")
    input("Apasă ENTER pentru a închide...")

if __name__ == "__main__":
    main()