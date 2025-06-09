from netmiko import ConnectHandler

ip_list = ["192.168.41.65", "192.168.41.63", "192.168.41.64"]  # لیست IP سوئیچ‌ها
target_ip = "172.30.12.104"  # IP مورد نظر شما

for switch_ip in ip_list:
    device = {
        'device_type': 'cisco_ios',
        'host': switch_ip,
        'username': 'nitc',
        'password': 'C!sc0@ccee$$2024@',
    }
    try:
        connection = ConnectHandler(**device)
        output = connection.send_command(f"show ip dhcp snooping binding | include {target_ip}")
        if target_ip in output:
            print(f"IP {target_ip} found on Switch: {switch_ip}")
            print(output)
        connection.disconnect()
    except Exception as e:
        print(f"Failed to connect to {switch_ip}: {e}")
        
input("\nPress Enter to exit...")
