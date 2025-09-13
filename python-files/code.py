import paramiko

# Read username and password from credentials.txt
with open("credentials.txt", "r") as cred_file:
    username = cred_file.readline().strip()
    password = cred_file.readline().strip()

# Read IP addresses from IP_addresses.txt
with open("IP_addresses.txt", "r") as ip_file:
    ip_addresses = ip_file.readlines()

# Initialize SSH client
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Loop through each IP address and attempt to shut down the remote system
for ip in ip_addresses:
    ip = ip.strip()
    print(f"Attempting to shut down {ip}...")
    try:
        client.connect(ip, username=username, password=password)
        stdin, stdout, stderr = client.exec_command("shutdown /s /f /t 0")
        print(f"Shutdown command sent to {ip}")
    except Exception as e:
        print(f"Failed to connect or execute command on {ip}: {e}")
    finally:
        client.close()
