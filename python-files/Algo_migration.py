import subprocess
import getpass

# -----------------------------
#  Lister les comptes locaux
# -----------------------------
def get_local_users():
    try:
        powershell_cmd = 'Get-LocalUser | Select-Object -ExpandProperty Name'
        result = subprocess.run(["powershell", "-Command", powershell_cmd], capture_output=True, text=True, check=True)
        users = result.stdout.strip().splitlines()
        return users
    except subprocess.CalledProcessError as e:
        print(f" Erreur PowerShell lors de la récupération des utilisateurs : {e}")
        return []

# -----------------------------
#  Créer un compte local admin
# -----------------------------
def create_local_admin(username, password):
    try:
        subprocess.run(['net', 'user', username, password, '/add'], check=True)
        try:
            subprocess.run(['net', 'localgroup', 'Administrators', username, '/add'], check=True)
            group = "Administrators"
        except subprocess.CalledProcessError:
            subprocess.run(['net', 'localgroup', 'Administrateurs', username, '/add'], check=True)
            group = "Administrateurs"
        print(f" Compte local '{username}' créé et ajouté au groupe '{group}'.")
    except subprocess.CalledProcessError as e:
        print(f" Erreur lors de la création du compte : {e}")

# -----------------------------
#  Supprimer un compte local
# -----------------------------
def delete_local_user(username):
    try:
        subprocess.run(['net', 'user', username, '/delete'], check=True)
        print(f" Le compte local '{username}' a été supprimé avec succès.")
    except subprocess.CalledProcessError as e:
        print(f" Erreur lors de la suppression du compte : {e}")

# ----------------------
#  Inscrire dans Entra ID / Intune
# ----------------------
def enroll_device():
    print(" Lancement de l'inscription de l'appareil dans Entra ID / Intune...")
    try:
        subprocess.run(["start", "ms-device-enrollment:?mode=mdm"], shell=True)
        print(" Fenêtre d'inscription lancée. Suivez les étapes à l'écran.")
    except subprocess.CalledProcessError as e:
        print(f" Erreur lors de l'inscription : {e}")

# -----------------------------
#  Menu principal
# -----------------------------
def main():
    while True:
        print("\n============================")
        print(" GESTION DES COMPTES / ENTRA ID")
        print("============================")
        print("1.  Ajouter un compte local administrateur")
        print("2.  Supprimer un compte local")
        print("3.  Afficher les comptes")
        print("4.  Inscrire l’appareil dans Entra ID / Intune")
        print("5.  Quitter")

        choice = input("\n Que veux-tu faire ? (1-5) : ").strip()

        if choice == '1':
            username = input("Nom du nouveau compte : ").strip()
            password = getpass.getpass("Mot de passe du compte : ")
            create_local_admin(username, password)

        elif choice == '2':
            users = get_local_users()
            if not users:
                print(" Aucun utilisateur trouvé.")
                continue

            print("\n Utilisateurs locaux :")
            for i, user in enumerate(users, 1):
                print(f"{i}. {user}")

            user_choice = input("\nNom exact du compte à supprimer : ").strip()
            if user_choice not in users:
                print(f" Le compte '{user_choice}' n'existe pas.")
                continue

            confirm = input(f" Supprimer '{user_choice}' ? (oui/non) : ").strip().lower()
            if confirm in ['oui', 'o', 'yes', 'y']:
                delete_local_user(user_choice)
            else:
                print(" Suppression annulée.")

        elif choice == '3':
            users = get_local_users()
            print("\n Comptes locaux actuels :")
            for user in users:
                print(f"  - {user}")

        elif choice == '4':
            enroll_device()

        elif choice == '5':
            print(" Fin du script.")
            break

        else:
            print(" Choix invalide. Réessaie.")

if __name__ == "__main__":
    main()
