import asyncio
import ipaddress
import platform

# Determine the correct ping command parameters
IS_WINDOWS = platform.system().lower() == "windows"
PING_COUNT_PARAM = "-n" if IS_WINDOWS else "-c"
PING_TIMEOUT_PARAM = "-w" if IS_WINDOWS else "-W"
TIMEOUT = "1000" if IS_WINDOWS else "1"

async def ping(ip):
    """Asynchronously ping an IP address."""
    process = await asyncio.create_subprocess_exec(
        "ping", PING_COUNT_PARAM, "1", PING_TIMEOUT_PARAM, TIMEOUT, str(ip),
        stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL
    )
    await process.communicate()
    if process.returncode == 0:
        print(f"[+] {ip} is reachable")
    else:
        print(f"[-] {ip} is unreachable")

async def scan_subnet(subnet):
    """Asynchronously scan all hosts in the subnet."""
    try:
        network = ipaddress.ip_network(subnet, strict=False)
        print(f"Scanning subnet: {subnet}")

        tasks = [ping(ip) for ip in network.hosts()]
        await asyncio.gather(*tasks)

    except ValueError as e:
        print(f"Invalid subnet: {e}")

if __name__ == "__main__":
    subnet_input = input("Enter subnet (e.g., 192.168.1.0/24): ")
    asyncio.run(scan_subnet(subnet_input))
    input("done")
