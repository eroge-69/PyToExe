import paramiko
import datetime
import os


def run_ssh_command(ip, username, password, commands):
    print(f"Connecting to {ip}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=username, password=password, timeout=10)
        # Try each command until one works
        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()
            # If we got output and no error about unknown command, use this result
            if output and not "Unknown command" in error:
                ssh.close()
                return output
        # If we got here, none of the commands worked
        ssh.close()
        return f"Error: None of the commands worked. Last error: {error}"
    except Exception as e:
        return f"Connection error: {str(e)}"


def main():
    # Base directory for backups
    backup_dir = 'C:/Users/Administrator/Desktop/New folder'
    # Create directory if it doesn't exist
    os.makedirs(backup_dir, exist_ok=True)
    # Current date/time for filename
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    # List of possible commands to try
    commands = [
        "show running-configuration",
        "sonic-cli -c 'show running-configuration'",
        "show running-config"
    ]
    # Define all switches in a list to avoid repetition
    switches = [
        {"ip": "192.168.3.17", "username": "fastlink", "password": "Hello.World123!", "name": "Dell_Switch"},
        {"ip": "172.27.3.122", "username": "fastlink", "password": "Hello.World123!", "name": "BLeaf_switch1"},
        {"ip": "172.27.3.121", "username": "fastlink", "password": "Hello.World123!", "name": "BLeaf_switch2"},
        {"ip": "172.27.3.126", "username": "fastlink", "password": "Hello.World123!", "name": "Spine_switch1"},
        {"ip": "172.27.3.125", "username": "fastlink", "password": "Hello.World123!", "name": "Spine_switch2"},
        {"ip": "172.27.3.124", "username": "fastlink", "password": "Hello.World123!", "name": "Leaf_switch1"},
        {"ip": "172.27.3.123", "username": "fastlink", "password": "Hello.World123!", "name": "Leaf_switch2"},
        {"ip": "172.27.3.120", "username": "fastlink", "password": "Hello.World123!", "name": "Aggregate_switch1"},
        {"ip": "172.27.3.26", "username": "fastlink", "password": "Hello.World123!", "name": "BLeaf_switch1_lab"},
        {"ip": "172.27.3.25", "username": "fastlink", "password": "Hello.World123!", "name": "BLeaf_switch2_lab"},
        {"ip": "172.27.3.30", "username": "fastlink", "password": "Hello.World123!", "name": "Spine_Switch1_lab"},
        {"ip": "172.27.3.29", "username": "fastlink", "password": "Hello.World123!", "name": "Spine_Switch2_lab"},
        {"ip": "172.27.3.28", "username": "fastlink", "password": "Hello.World123!", "name": "Leaf_switch1_lab"},
        {"ip": "172.27.3.27", "username": "fastlink", "password": "Hello.World123!", "name": "Leaf_switch2_lab"},
        {"ip": "172.27.3.24", "username": "fastlink", "password": "Hello.World123!", "name": "Aggregate_switch2"},
        {"ip": "192.168.3.18", "username": "fastlink", "password": "Hello.World123!", "name": "Core_SW2"}
    ]

    # Back up each switch
    for switch in switches:
        result = run_ssh_command(switch["ip"], switch["username"], switch["password"], commands)
        file_path = f'{backup_dir}/{switch["name"]}_{switch["ip"]}_{timestamp}.txt'
        with open(file_path, 'w') as file:
            file.write(result)
        print(f"Backup completed for {switch['name']} ({switch['ip']})")


if __name__ == "__main__":
    main()