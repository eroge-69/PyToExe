import paramiko
import time
import getpass
import ipaddress
import subprocess
import platform

def validate_ip(ip):
    """验证给定的IP地址是否有效"""
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def parse_ip_input():
    """获取IP范围或逗号分隔的IP地址并返回有效的IP列表"""
    while True:
        ip_input = input("请输入有效的IPv4地址范围或多个IP地址（如 192.168.1.100-192.168.1.110 或 192.168.1.100,192.168.2.200）: ").strip()
        ip_list = []
        
        # 检查是否是一个范围
        if '-' in ip_input:
            try:
                start_ip, end_ip = ip_input.split('-')
                start = ipaddress.ip_address(start_ip.strip())
                end = ipaddress.ip_address(end_ip.strip())
                ip_list.extend(ipaddress.summarize_address_range(start, end))
            except ValueError:
                print("错误：无效的IP地址范围")
                continue
        else:
            # 检查是否是多个IP
            ips = ip_input.split(',')
            for ip in ips:
                if validate_ip(ip.strip()):
                    ip_list.append(ip.strip())
                else:
                    print(f"错误：无效的IP地址 {ip.strip()}")
                    break
            else:
                return ip_list
        
        print("请重新输入有效的IP地址范围或多个IP地址。")

def ping_ip(ip):
    """Ping一个IP地址以检查可达性"""
    try:
        # 检查操作系统
        if platform.system().lower() == 'windows':
            output = subprocess.check_output(['ping', '-n', '1', str(ip)], stderr=subprocess.STDOUT, universal_newlines=True)
        else:
            output = subprocess.check_output(['ping', '-c', '1', str(ip)], stderr=subprocess.STDOUT, universal_newlines=True)
        return True
    except subprocess.CalledProcessError:
        return False

def ssh_connect(ip, password):
    """SSH连接"""
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(ip, port=22, username='admin', password=password)
        return client
    except paramiko.AuthenticationException:
        print(f"认证失败: {ip}，请检查密码")
        return None
    except Exception as e:
        print(f"连接 {ip} 失败: {str(e)}")
        return None

def execute_commands(channel, commands, wait_time=1):
    """执行一系列命令"""
    for cmd in commands:
        channel.send(cmd + '\n')
        time.sleep(wait_time)

def main_loop():
    while True:
        # 配置项列表
        config_items = [
            'wireless.device_radio0.arp_hb_en',
            'wireless.device_radio0.arp_hb_int',
            'wireless.device_radio0.arp_hb_timeout',
            'wireless.device_radio0.arp_hb_kick_en',
            'wireless.device_radio0.arp_hb_reload_en',
            'wireless.device_radio0.arp_hb_reload_pct',  
            'wireless.device_radio1.arp_hb_en',
            'wireless.device_radio1.arp_hb_int',
            'wireless.device_radio1.arp_hb_timeout',
            'wireless.device_radio1.arp_hb_kick_en',
            'wireless.device_radio1.arp_hb_reload_en',
            'wireless.device_radio1.arp_hb_reload_pct',
        ]

        ip_list = parse_ip_input()  # 获取IP列表
        ssh_password = getpass.getpass("请输入SSH密码(admin用户): ").strip()

        reachable_ips = []  # 用于存储可达的IP

        # 检查每个IP的可达性并存储
        for ip in ip_list:
            # 检查IP可达性
            if ping_ip(ip):
                print(f"IP地址 {ip} 可达")
                reachable_ips.append(ip)
            else:
                print(f"IP地址 {ip} 不可达 (unreachable)")

        # 确保有可达的IP进行配置
        if not reachable_ips:
            print("没有可达的IP，结束程序。")
            return

        # 获取配置项的输入
        commands = []
        print("\n请输入各配置项的值（直接回车保留原值）:")
        for item in config_items:
            value = input(f"{item} [新值]: ").strip()
            if value:  # 只添加非空值
                cmd = f'uci -c /etc/awrt/config set {item}="{value}"'
                commands.append(cmd)

        # 确认是否保存配置
        confirm = input("所有配置项已写入文件后，是否确认保存？(yes/no): ").strip().lower()
        if confirm == 'yes':
            commands.append('save_and_apply_config')  # 添加保存命令

        # 对所有可达IP应用收集到的命令
        for ip in reachable_ips:
            print(f"\n正在对 IP 地址 {ip} 应用配置。")
            client = ssh_connect(ip, ssh_password)
            if not client:
                continue
            
            try:
                channel = client.invoke_shell()
                
                # Root提权流程
                channel.send('sudo -s\n')
                time.sleep(1)
                if channel.recv_ready():
                    channel.recv(4096)
                
                channel.send('superwifi123\n')
                time.sleep(2)
                
                # 验证root权限
                channel.send('whoami\n')
                time.sleep(1)
                output = channel.recv(4096).decode()
                if 'root' not in output:
                    print("错误：获取root权限失败")
                    client.close()
                    continue

                # 检查版本
                channel.send('/sbin/uci -c /etc/awrt/status get about.about_software.version\n')
                time.sleep(2)
                version = channel.recv(4096).decode()
                print(f"当前版本: {version.split('\r\n')[-2].strip()}")

                # 执行所有命令
                execute_commands(channel, commands, wait_time=2)

                # 验证配置
                channel.send('uci -c /etc/awrt/config show wireless | grep arp_hb\n')
                time.sleep(3)
                config_output = channel.recv(4096).decode()
                print("\n修改后的配置:")
                print('\n'.join([line for line in config_output.split('\n') if 'arp_hb' in line]))

                channel.send('awrt-reload wireless\n')
                time.sleep(5)
                print(f"IP地址 {ip} 的配置已重新加载")

            except Exception as e:
                print(f"应用配置给 {ip} 时发生错误: {str(e)}")
            finally:
                client.close()

        # 继续或退出
        continue_choice = input("\n是否继续操作？(y/n): ").strip().lower()
        if continue_choice != 'y':
            print("退出程序。")
            break

if __name__ == "__main__":
    main_loop()