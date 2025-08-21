import paramiko
import getpass
import webbrowser

def print_branding():
    art = r"""
        ,----,                                                                                             
      ,/   .`|                                                                 ,--,                        
    ,`   .'  :             ___          ,-.             ,--,                 ,--.'|                        
  ;    ;     /           ,--.'|_    ,--/ /|           ,--.'|              ,--,  | :               ,---,    
.'___,/    ,'            |  | :,' ,--. :/ |           |  | :           ,---.'|  : '         ,--,,---.'|    
|    :     |             :  : ' : :  : ' /            :  : '           |   | : _' |       ,'_ /||   | :    
;    |.';  ;  ,--.--.  .;__,'  /  |  '  /    ,--.--.  |  ' |           :   : |.'  |  .--. |  | ::   : :    
`----'  |  | /       \ |  |   |   '  |  :   /       \ '  | |           |   ' '  ; :,'_ /| :  . |:     |,-. 
    '   :  ;.--.  .-. |:__,'| :   |  |   \ .--.  .-. ||  | :           '   |  .'. ||  ' | |  . .|   : '  | 
    |   |  ' \__\/: . .  '  : |__ '  : |. \ \__\/: . .'  : |__         |   | :  | '|  | ' |  | ||   |  / : 
    '   :  | ," .--.; |  |  | '.'||  | ' \ \," .--.; ||  | '.'|        '   : |  : ;:  | : ;  ; |'   : |: | 
    ;   |.' /  /  ,.  |  ;  :    ;'  : |--'/  /  ,.  |;  :    ;        |   | '  ,/ '  :  `--'   \   | '/ : 
    '---'  ;  :   .'   \ |  ,   / ;  |,'  ;  :   .'   \  ,   /         ;   : ;--'  :  ,      .-./   :    | 
           |  ,     .-./  ---`-'  '--'    |  ,     .-./---`-'          |   ,/       `--`----'   /    \  /  
            `--`---'                       `--`---'                    '---'                    `-'----'   
                                                                                                           """
    promo = """Proxy Maker by TatkalHub offers, letting you easily install IP/Proxy servers in just a few minutes with an effortless setup process.

Visit: tatkalhub.com

TatkalHub
"""
    print(art)
    print(promo)

def install_squid(ip, username, password, proxy_port, proxy_user, proxy_pass):
    commands = [
        "wget https://raw.githubusercontent.com/serverok/squid-proxy-installer/master/squid3-install.sh -O squid3-install.sh",
        "sudo bash squid3-install.sh",
        f"sudo /usr/bin/htpasswd -b -c /etc/squid/passwd {proxy_user} {proxy_pass}"
    ]
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(stdout.read().decode())
            err = stderr.read().decode()
            if err:
                print('Error:', err)
        ssh.close()
        print("Squid proxy installation and setup complete.")
    except Exception as e:
        print(f"SSH Connection/Command error: {e}")

def update_proxy_password(ip, username, password, proxy_user):
    proxy_pass = getpass.getpass("Enter new password for proxy user: ")
    cmd = f"sudo /usr/bin/htpasswd /etc/squid/passwd {proxy_user} {proxy_pass}"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print('Error:', err)
        ssh.close()
        print("Proxy password updated.")
    except Exception as e:
        print(f"SSH Connection/Command error: {e}")

def reboot_server(ip, username, password):
    cmd = "sudo reboot"
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        print(stdout.read().decode())
        err = stderr.read().decode()
        if err:
            print('Error:', err)
        ssh.close()
        print("Reboot command sent.")
    except Exception as e:
        print(f"SSH Connection/Command error: {e}")

def open_tatkalhub():
    webbrowser.open("https://tatkalhub.com")

def main():
    print_branding()
    print("Choose an option:")
    print("1. Install Squid Proxy")
    print("2. Reboot Linux Server")
    print("3. Buy IP/VPS (redirect to tatkalhub.com)")
    opt = input("Enter option number (1/2/3): ").strip()
    
    if opt == '1':
        ip = input("Enter server IP: ").strip()
        username = input("Enter server username (default: root): ").strip() or "root"
        password = getpass.getpass("Enter server password: ")
        proxy_port = input("Enter proxy port (default: 3128): ").strip() or "3128"
        proxy_user = input("Enter proxy username: ").strip()
        proxy_pass = getpass.getpass("Enter proxy password: ")
        install_squid(ip, username, password, proxy_port, proxy_user, proxy_pass)
        update = input("Want to update password for existing proxy user? (y/n): ").strip().lower()
        if update == 'y':
            proxy_user_again = input("Enter existing proxy username: ").strip()
            update_proxy_password(ip, username, password, proxy_user_again)
    elif opt == '2':
        ip = input("Enter server IP: ").strip()
        username = input("Enter server username (default: root): ").strip() or "root"
        password = getpass.getpass("Enter server password: ")
        reboot_server(ip, username, password)
    elif opt == '3':
        open_tatkalhub()
    else:
        print("Invalid option.")

if __name__ == '__main__':
    main()
