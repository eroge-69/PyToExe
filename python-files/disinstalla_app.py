import subprocess

def get_installed_apps():
    ps_command = r'''
    Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
    Select-Object DisplayName, UninstallString |
    Where-Object { $_.DisplayName -and $_.UninstallString }
    '''
    result = subprocess.run(["powershell", "-Command", ps_command], capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    apps = []
    for line in lines[3:]:
        if line.strip():
            apps.append(line.strip())
    return apps

def main():
    apps = get_installed_apps()
    if not apps:
        print("Nessuna applicazione trovata o errore nella lettura.")
        return

    print("Applicazioni installate:")
    for i, app in enumerate(apps):
        print(f"{i + 1}. {app}")

    try:
        choice = int(input("\nInserisci il numero dell'applicazione da disinstallare: "))
        if 1 <= choice <= len(apps):
            selected_app = apps[choice - 1]
            uninstall_command = selected_app.split()[-1]
            print(f"\nAvvio disinstallazione di: {selected_app}")
            subprocess.run(["powershell", "-Command", uninstall_command])
        else:
            print("Numero non valido.")
    except ValueError:
        print("Input non valido. Inserisci un numero.")

if __name__ == "__main__":
    main()
