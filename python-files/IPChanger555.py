import os
import sys
import ctypes
import subprocess
import time
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

# --------- Admin Check ----------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def restart_as_admin():
    try:
        console.print("[yellow][!] Script needs Administrator privileges. Restarting with admin rights...[/yellow]")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
    except:
        console.print("[red]Admin permission denied! Exiting...[/red]")
        input("\nPress Enter to exit...")
        sys.exit()

# --------- Utility Functions ----------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    console.clear()

def run_cmd(cmd):
    """Run command and return output + error code"""
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout.strip(), result.stderr.strip(), result.returncode

def list_network_interfaces():
    """List active network adapters using netsh"""
    out, _, _ = run_cmd('netsh interface show interface')
    adapters = []
    for line in out.splitlines()[3:]:
        parts = line.split()
        if len(parts) >= 4:
            status, _, _, name = parts[0], parts[1], parts[2], " ".join(parts[3:])
            if status.lower() == "enabled":
                adapters.append({"name": name, "status": status})
    return adapters

def get_adapter_mode(adapter_name):
    """Check if adapter is in DHCP or Static mode"""
    output, _, _ = run_cmd(f'netsh interface ip show config name="{adapter_name}"')
    lines = [line.strip().lower() for line in output.splitlines() if line.strip()]

    for line in lines:
        if "dhcp enabled" in line:
            if "yes" in line:
                return "dhcp"
            elif "no" in line:
                return "static"
    return "unknown"

def get_adapter_details(adapter_name):
    """
    Get IP, Subnet, Gateway, DNS details accurately
    """
    output, _, _ = run_cmd(f'netsh interface ip show config name="{adapter_name}"')

    ip = "N/A"
    subnet = "N/A"
    gateway_list = []
    dns_list = []
    capture_dns = False

    for line in output.splitlines():
        line = line.strip()

        if not line:
            continue

        # IP Address
        if "IP Address" in line or "IPv4 Address" in line:
            ip_match = re.search(r"([\d]+\.[\d]+\.[\d]+\.[\d]+)", line)
            if ip_match:
                ip = ip_match.group(1)

        # Subnet Prefix / Mask
        if "Subnet Prefix" in line:
            mask_match = re.search(r"\(mask ([\d]+\.[\d]+\.[\d]+\.[\d]+)\)", line)
            if mask_match:
                subnet = mask_match.group(1)

        # Default Gateway
        if "Default Gateway" in line:
            gw = line.split(":")[-1].strip()
            if gw:
                gateway_list.append(gw)

        elif line.startswith("Gateway"):
            gw_match = re.search(r"([\d]+\.[\d]+\.[\d]+\.[\d]+)", line)
            if gw_match:
                gateway_list.append(gw_match.group(1))

        # DNS Servers section start
        if "DNS servers" in line:
            capture_dns = True
            continue

        if capture_dns:
            if re.match(r"^\d+\.\d+\.\d+\.\d+$", line):
                dns_list.append(line)
            elif line.startswith("Register") or line.startswith("Primary"):
                capture_dns = False

    gateway = ", ".join(gateway_list) if gateway_list else "N/A"
    dns = "\n".join(dns_list) if dns_list else "N/A"

    return ip, subnet, gateway, dns


def show_interfaces_table(adapters):
    """Show adapters in table format"""
    table = Table(title="Available Network Interfaces", style="cyan")
    table.add_column("Index", justify="center", style="magenta")
    table.add_column("Adapter Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Mode", style="cyan")
    table.add_column("IP Address", style="white")
    table.add_column("Subnet", style="white")
    table.add_column("Gateway", style="white")
    table.add_column("DNS Servers", style="white")

    for idx, ad in enumerate(adapters):
        mode = get_adapter_mode(ad['name'])
        ip, subnet, gateway, dns = get_adapter_details(ad['name'])
        mode_display = "DHCP" if mode == "dhcp" else "Static" if mode == "static" else "[red]Unknown[/red]"
        table.add_row(str(idx), ad['name'], ad['status'], mode_display, ip, subnet, gateway, dns)

    console.print(table)
    console.print(Panel.fit("[bold yellow]E : Exit / Close Window[/bold yellow]", style="red"))

# --------- Banner ----------
def animated_samchuck_banner():
    banner_lines = [
        "   ███████╗ █████╗ ███╗   ███╗   ██████╗██╗  ██╗██╗   ██╗ ██████╗██╗   ██╗",
        "   ██╔════╝██╔══██╗████╗ ████║  ██╔════╝██║  ██║╚██╗ ██╔╝██╔════╝██║   ██║",
        "   ███████╗███████║██╔████╔██║  ██║     ███████║ ╚████╔╝ ██║     ████████║",
        "   ╚════██║██╔══██║██║╚██╔╝██║  ██║     ██╔══██║  ╚██╔╝  ██║     ██╔═══██║",
        "   ███████║██║  ██║██║ ╚═╝ ██║  ╚██████╗██║  ██║   ██║   ╚██████╗██║   ██║",
        "   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝   ╚═════╝╚═╝  ╚═╝   ╚═╝    ╚═════╝╚═╝   ╚═╝",
        "                             S  A  M  C  H  U  C  K                       "
    ]
    for i in range(4):  # blink
        console.clear()
        color = "red" if i % 2 == 0 else "green"
        for line in banner_lines:
            console.print(f"[bold {color}]{line}[/bold {color}]")
        time.sleep(0.4)
    console.clear()
    for line in banner_lines:
        console.print(f"[bold green]{line}[/bold green]")
    console.print("\n[bold cyan]💻 Network Mode Switch Utility[/bold cyan] [red]by SamChuck[/red]\n")

# --------- Success Message ----------
def success_animation(msg):
    clear_screen()
    console.print(Panel.fit(f"[bold green]{msg}[/bold green]", style="green"))
    time.sleep(2)

# --------- Mode Switching ----------
def switch_to_dhcp(adapter_name):
    cmds = [
        f'netsh interface ip set address "{adapter_name}" dhcp',
        f'netsh interface ip set dns "{adapter_name}" dhcp'
    ]
    for cmd in cmds:
        _, err, code = run_cmd(cmd)
        if code != 0:
            return False, err
    return True, ""

def switch_to_static(adapter_name, ip, mask, gateway, dns_servers):
    """
    Set static IP using netsh without prefix length issue
    """
    cmd_ip = f'netsh interface ip set address name="{adapter_name}" static {ip} {mask} {gateway} 1'
    out, err, code = run_cmd(cmd_ip)

    if code != 0:
        return False, f"{err}\n{out}"

    dns_list = [dns.strip() for dns in dns_servers.split(",") if dns.strip()]
    if not dns_list:
        return True, ""  # agar DNS na diya ho to skip

    # Primary DNS
    out, err, code = run_cmd(f'netsh interface ip set dns name="{adapter_name}" static {dns_list[0]}')
    if code != 0:
        return False, f"{err}\n{out}"

    # Secondary DNS servers
    for dns in dns_list[1:]:
        run_cmd(f'netsh interface ip add dns name="{adapter_name}" {dns}')

    return True, ""

# --------- Main Menu ----------
def main_menu():
    while True:
        clear_screen()
        animated_samchuck_banner()

        adapters = list_network_interfaces()
        if not adapters:
            console.print("[red]No active adapters found![/red]")
            input("\nPress Enter to exit...")
            sys.exit()

        show_interfaces_table(adapters)

        choices = [str(i) for i in range(len(adapters))] + ["E", "e"]
        idx = Prompt.ask("[bold magenta]Select adapter index or E to Exit[/bold magenta]", choices=choices)

        if idx.lower() == "e":
            console.print("\n[yellow]Closing window...[/yellow]")
            sys.exit()

        adapter_name = adapters[int(idx)]['name']
        current_mode = get_adapter_mode(adapter_name)

        console.print(f"\n[cyan]1 : Switch to DHCP Mode[/cyan]")
        console.print(f"[cyan]2 : Switch to Static Mode[/cyan]")
        choice = Prompt.ask("[bold yellow]Enter your choice[/bold yellow]", choices=["1", "2"])

        if choice == "1":
            if current_mode == "dhcp":
                success_animation("ℹ️ This adapter is already in DHCP mode!")
                continue
            success, error = switch_to_dhcp(adapter_name)
            if success:
                success_animation("✅ DHCP Mode Activated Successfully!")
            else:
                console.print(Panel.fit(f"[red]❌ Operation Failed: {error}[/red]", style="red"))
                time.sleep(3)

        elif choice == "2":
            if current_mode == "static":
                change_ip = Confirm.ask("[yellow]This adapter is already in Static mode. Change IP?[/yellow]")
                if not change_ip:
                    continue
            ip = Prompt.ask("Enter IP Address (e.g. 192.168.1.100)")
            mask = Prompt.ask("Enter Subnet Mask (e.g. 255.255.255.0)")
            gateway = Prompt.ask("Enter Default Gateway (e.g. 192.168.1.1)")
            dns = Prompt.ask("Enter DNS Servers (comma separated, e.g. 8.8.8.8,8.8.4.4)")
            success, error = switch_to_static(adapter_name, ip, mask, gateway, dns)
            if success:
                success_animation("💣 Static Mode Activated Successfully!")
            else:
                console.print(Panel.fit(f"[red]❌ Operation Failed: {error}[/red]", style="red"))
                time.sleep(3)

        next_action = Prompt.ask("\n[cyan]1: Return to Main Menu | 2: Exit[/cyan]", choices=["1", "2"])
        if next_action == "2":
            console.print("\n[yellow]Closing window...[/yellow]")
            break

    input("\nPress Enter to exit...")

# --------- Run Program ----------
if __name__ == "__main__":
    if not is_admin():
        restart_as_admin()
    main_menu()
