import sys
from zk import ZK, const
from datetime import datetime

def fetch_logs(ip, port):
    zk = ZK(ip, port=port, timeout=5, password=0, force_udp=False, ommit_ping=False)
    try:
        conn = zk.connect()
        conn.disable_device()

        print("EnrollNo,Timestamp,Status")
        for att in conn.get_attendance():
            timestamp = att.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            print(f"{att.user_id},{timestamp},{att.status}")

        conn.enable_device()
        conn.disconnect()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python get_log.py <ip> <port>")
    else:
        ip = sys.argv[1]
        port = int(sys.argv[2])
        fetch_logs(ip, port)
