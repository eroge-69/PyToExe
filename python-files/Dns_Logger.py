# Create a simple DNS logging proxy script and accompanying README and systemd service file.

from textwrap import dedent
from datetime import datetime

dns_logger_code = dedent("""
#!/usr/bin/env python3
# dns_logger.py
#
# A lightweight DNS logging proxy for home networks.
# - Listens on UDP/53
# - Logs query timestamp, client IP, and requested domain (QNAME)
# - Forwards queries to an upstream resolver and relays the response
#
# Requirements: Python 3.8+, run with sudo (port 53 needs root)
# Limitations:
# - Only logs classic DNS over UDP (port 53). It cannot see DNS-over-HTTPS (DoH) or DNS-over-TLS (DoT).
# - If devices use DoH/DoT, you won't see their queries here.
#
# Usage:
#   sudo python3 dns_logger.py --upstream 1.1.1.1 --bind 0.0.0.0 --port 53 --log-file dns_queries.csv
#
# After running, point your router's DNS to this machine's IP address.

import argparse
import asyncio
import csv
import ipaddress
import os
from datetime import datetime

def parse_qname(packet: bytes, offset: int = 12) -> str:
    \"\"\"Parse a DNS QNAME starting at offset (default after 12-byte header).
    Returns the domain as a string. Assumes an uncompressed QNAME in the question section.
    Handles simple compression pointers for safety.
    \"\"\"
    labels = []
    jumped = False
    original_offset = offset
    max_len = len(packet)
    # Prevent infinite loops
    seen_offsets = set()

    while True:
        if offset >= max_len:
            return ""
        length = packet[offset]
        # Compression pointer: 11xxxxxx
        if (length & 0xC0) == 0xC0:
            if offset + 1 >= max_len:
                return ""
            # Pointer: next 14 bits are the offset
            pointer = ((length & 0x3F) << 8) | packet[offset + 1]
            if pointer in seen_offsets:
                return ""
            seen_offsets.add(pointer)
            offset = pointer
            jumped = True
            continue
        if length == 0:
            # End of name
            if not jumped:
                # Move offset past the zero byte and QTYPE/QCLASS (not used)
                pass
            break
        offset += 1
        if offset + length > max_len:
            return ""
        label = packet[offset: offset + length]
        try:
            labels.append(label.decode('ascii'))
        except UnicodeDecodeError:
            labels.append(label.decode('idna', errors='ignore'))
        offset += length

    domain = ".".join(labels)
    return domain

class DNSLoggerProtocol(asyncio.DatagramProtocol):
    def __init__(self, upstream_host: str, upstream_port: int, log_file: str):
        super().__init__()
        self.upstream_host = upstream_host
        self.upstream_port = upstream_port
        self.transport = None
        self.log_file = log_file
        # Prepare CSV with header if new
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp_utc", "client_ip", "qname"])

    def connection_made(self, transport):
        self.transport = transport
        sock = transport.get_extra_info('socket')
        if sock is not None:
            try:
                sock.setsockopt(0, 25, 1)  # IP_TOS low delay (best-effort); ignore if not supported
            except Exception:
                pass

    def datagram_received(self, data: bytes, addr):
        client_ip, client_port = addr
        # Parse QNAME from the query
        domain = parse_qname(data)
        # Log asynchronously
        ts = datetime.utcnow().isoformat(timespec="seconds") + "Z"
        try:
            with open(self.log_file, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([ts, client_ip, domain])
        except Exception:
            pass

        # Forward to upstream and reply back
        asyncio.create_task(self.forward_and_reply(data, addr))

    async def forward_and_reply(self, data: bytes, addr):
        try:
            loop = asyncio.get_running_loop()
            # Create a temporary UDP socket to query upstream
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: asyncio.DatagramProtocol(),
                remote_addr=(self.upstream_host, self.upstream_port)
            )
            transport.sendto(data)
            # Wait for response with timeout
            try:
                fut = loop.create_future()

                def on_response(d, a):
                    if not fut.done():
                        fut.set_result((d, a))

                class _Resp(asyncio.DatagramProtocol):
                    def datagram_received(self, d, a):
                        on_response(d, a)

                # Replace protocol with one that captures the response
                transport.close()
                # Re-open with capture protocol
                transport2, protocol2 = await loop.create_datagram_endpoint(
                    _Resp, remote_addr=(self.upstream_host, self.upstream_port)
                )
                transport2.sendto(data)
                resp_data, _ = await asyncio.wait_for(fut, timeout=2.0)
                # Send response back to original client
                if self.transport is not None:
                    self.transport.sendto(resp_data, addr)
                transport2.close()
            except asyncio.TimeoutError:
                # No response; ignore
                pass
        except Exception:
            pass

async def main():
    parser = argparse.ArgumentParser(description="DNS logging proxy")
    parser.add_argument("--bind", default="0.0.0.0", help="Bind address (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=53, help="Listen port (default: 53; requires root)")
    parser.add_argument("--upstream", default="1.1.1.1", help="Upstream DNS server (default: 1.1.1.1)")
    parser.add_argument("--upstream-port", type=int, default=53, help="Upstream DNS port (default: 53)")
    parser.add_argument("--log-file", default="dns_queries.csv", help="CSV log output file")
    args = parser.parse_args()

    # Validate upstream IP/host
    try:
        # If it's an IP, validate; if hostname, ignore
        ipaddress.ip_address(args.upstream)
    except ValueError:
        # Hostname is acceptable
        pass

    print(f"[DNS-LOGGER] Starting on {args.bind}:{args.port}, forwarding to {args.upstream}:{args.upstream_port}")
    print(f"[DNS-LOGGER] Logging to {args.log_file}")
    loop = asyncio.get_running_loop()
    # Create UDP endpoint
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DNSLoggerProtocol(args.upstream, args.upstream_port, args.log_file),
        local_addr=(args.bind, args.port)
    )

    try:
        await asyncio.Future()  # Run forever
    finally:
        transport.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except PermissionError:
        print("PermissionError: Binding to port 53 requires elevated privileges. Try running with sudo.")
    except KeyboardInterrupt:
        print("\\nShutting down.")
""")

readme = dedent(f"""
DNS Logging Proxy (Home Network)
================================

What this does
--------------
- Records *domain names* that devices on your Wi-Fi resolve via DNS (UDP/53).
- Logs to a CSV file with timestamp (UTC), client IP, and domain.
- Forwards queries to an upstream resolver (Cloudflare 1.1.1.1 by default).

What it does *not* do
---------------------
- It does not show exact pages or search terms.
- It cannot see DNS-over-HTTPS (DoH) or DNS-over-TLS (DoT) traffic.
- It should only be used on networks you administer, with appropriate consent.

Quick start
-----------
1) Put `dns_logger.py` on a computer always connected to your router (Linux, macOS, or Windows WSL).
2) Run it with elevated privileges (port 53 is privileged):
   sudo python3 dns_logger.py --upstream 1.1.1.1 --bind 0.0.0.0 --port 53 --log-file /var/log/dns_queries.csv

3) In your router's admin UI, set the **Primary DNS server** to the IP address of this computer.
   (Leave Secondary blank temporarily to force usage; later you can set it to the same box for redundancy.)

4) Test from a device on your Wi-Fi:
   - Visit a couple of sites.
   - Check the CSV log (e.g., `tail -f /var/log/dns_queries.csv`) and confirm entries appear.

Viewing the logs
----------------
The log file is a CSV. Columns:
- timestamp_utc, client_ip, qname

Import into Excel/Google Sheets or use `grep`/`awk` to filter per device IP.

Running as a systemd service (Linux)
------------------------------------
1) Copy the service file below to `/etc/systemd/system/dns-logger.service`
2) Edit the path to Python and the script as needed.
3) Then:

   sudo systemctl daemon-reload
   sudo systemctl enable dns-logger
   sudo systemctl start dns-logger
   sudo systemctl status dns-logger

Security / ethics
-----------------
- Use only on networks you own/manage and with the knowledge of users (family, employees).
- Laws vary by location. If in doubt, seek legal guidance.
- Consider telling users that DNS is being logged for safety/compliance.

Limitations & tips
------------------
- Devices that use DoH/DoT will bypass this. Some routers let you disable DoH or block known DoH endpoints.
- This tool only handles UDP DNS. Most home DNS is UDP; some queries may use TCP (rare).
- If you prefer an off-the-shelf solution with a UI, consider Pi-hole or OpenDNS.

""")

service_file = dedent("""
# /etc/systemd/system/dns-logger.service
[Unit]
Description=DNS Logging Proxy
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/dns-logger/dns_logger.py --upstream 1.1.1.1 --bind 0.0.0.0 --port 53 --log-file /var/log/dns_queries.csv
User=root
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
""")

# Write files
with open('/mnt/data/dns_logger.py', 'w') as f:
    f.write(dns_logger_code)

with open('/mnt/data/README_DNS_LOGGER.txt', 'w') as f:
    f.write(readme)

with open('/mnt/data/dns-logger.service', 'w') as f:
    f.write(service_file)

# Provide paths back
('/mnt/data/dns_logger.py', '/mnt/data/README_DNS_LOGGER.txt', '/mnt/data/dns-logger.service', datetime.utcnow().isoformat())

