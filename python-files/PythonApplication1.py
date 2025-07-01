import os
import time
from pathlib import Path
import ctypes
import subprocess

def open_and_close_edge_in_sandbox():
    # ������������ ���������� ��������� "%PUBLIC%" � ����������� ����
    public_dir = os.path.expandvars("%PUBLIC%")
    sandbox_path = Path(public_dir) / "Documents/sandbox-profile"

    # ������� ���������� �������, ���� ��� �� ����������
    if not sandbox_path.exists():
        sandbox_path.mkdir(parents=True, exist_ok=True)

    # ��������� �������� ��������� ������ ��� ������� Edge
    edge_command = r'"Microsoft Edge"'
    start_url = "https://mastermf.ru/catalog/kukhonnye_moyki_i_smesiteli/"
    command_line_args = f'--profile-path="{sandbox_path}" --open-url={start_url}'

    # ��������� �������������� ������� ��� ������� ���������
    full_cmd = f'sandbox {edge_command} "{command_line_args}"'

    try:
        # ��������� ������� Edge � ���������
        proc = subprocess.Popen(full_cmd, shell=True)
        
        # ��� �������, ����� ���� ����� �����������
        time.sleep(1)

        # ���������� ������� �������� ���� ����
        HWND_BROADCAST = 0xffff
        WM_CLOSE = 0x0010
        user32 = ctypes.windll.user32
        user32.SendMessageTimeoutW(HWND_BROADCAST, WM_CLOSE, 0, 0, 0x0002, 1000, None)

        # ��� ���������� �������� � ���������� ���������� ���������
        proc.wait()
    except Exception as e:
        print(f"��������� ������: {e}")

if __name__ == "__main__":
    while True:
        open_and_close_edge_in_sandbox()
        time.sleep(60)  # ����� ����� ������������ (60 ������)



