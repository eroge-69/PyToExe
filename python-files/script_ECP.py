import subprocess
import os

def change_dns():
    # ��������� ����� ��������������
    if not os.getuid() == 0:
        print("������ ������� ���� ��������������")
        return

    # DNS ������ ��� ���������
    primary_dns = "10.41.129.131"
    secondary_dns = "10.41.129.130"
    
    # �������� ��� ��������� �������� ��������
    try:
        # ���������� ������� Windows ��� ��������� ����� ��������
        result = subprocess.run(
            ['wmic', 'nicconfig', 'where', 'ipenabled=true', 'get', 'caption'],
            capture_output=True,
            text=True
        )
        adapter_name = result.stdout.split('\n')[1].strip()
        
        # ��������� ������� ��� ��������� DNS
        dns_commands = [
            f'netsh interface ip set dns "{adapter_name}" static {primary_dns} primary',
            f'netsh interface ip add dns "{adapter_name}" {secondary_dns} index=2'
        ]
        
        # ��������� �������
        for command in dns_commands:
            subprocess.run(command, shell=True)
            
        print("DNS ������� ���������!")
        
    except Exception as e:
        print(f"������ ��� ��������� DNS: {str(e)}")

if __name__ == "__main__":
    change_dns()
