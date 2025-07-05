import sys
import subprocess
from datetime import datetime
import os

def main():
    # Lấy tên file được gọi proxy (adb.exe hoặc ldconsole.exe)
    prog_name = os.path.basename(sys.argv[0]).lower()
    args = sys.argv[1:]

    # Map tên proxy thành file thực
    real_exec_map = {
        "adb.exe": "adb_real.exe",
        "ldconsole.exe": "ldconsole_real.exe"
    }

    if prog_name not in real_exec_map:
        print(f"Error: Proxy called as unexpected filename {prog_name}")
        sys.exit(1)

    real_exec = real_exec_map[prog_name]

    # Log file riêng cho từng proxy
    log_file = f"{prog_name}_proxy_log.txt"

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} Called {prog_name} with args: {' '.join(args)}\n")

    # Chạy file thực với tham số gốc, chuyển tiếp output chuẩn, lỗi chuẩn
    try:
        proc = subprocess.run([real_exec] + args, stdout=sys.stdout, stderr=sys.stderr)
        sys.exit(proc.returncode)
    except FileNotFoundError:
        print(f"Error: Real executable {real_exec} not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
