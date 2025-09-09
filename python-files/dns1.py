import flet as ft
import subprocess
import sys
import ctypes
import threading
import re
import platform
import time
from dataclasses import dataclass


# ---------------- Admin elevation ----------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def relaunch_as_admin():
    params = " ".join(f'"{arg}"' for arg in sys.argv)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)

# ---------------- PowerShell helpers ----------------
def run_powershell(ps_command):
    args = [
        "powershell",
        "-NoProfile",
        "-NonInteractive",
        "-NoLogo",
        "-WindowStyle", "Hidden",
        "-ExecutionPolicy", "Bypass",
        "-Command", ps_command
    ]

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0

    creationflags = 0
    if hasattr(subprocess, "CREATE_NO_WINDOW"):
        creationflags |= subprocess.CREATE_NO_WINDOW

    completed = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        startupinfo=startupinfo,
        creationflags=creationflags
    )
    ok = (completed.returncode == 0)
    return ok, completed.stdout.strip(), completed.stderr.strip()

def ps_quote(s):
    return s.replace("'", "''")

# ---------------- DNS operations ----------------
def list_adapters():
    cmd = r"Get-NetAdapter | Where-Object {$_.Status -eq 'Up'} | Select-Object -ExpandProperty Name"
    ok, out, err = run_powershell(cmd)
    if ok and out:
        return sorted(set([line.strip() for line in out.splitlines() if line.strip()]))
    
    cmd2 = r"Get-DnsClient | Select-Object -ExpandProperty InterfaceAlias | Sort-Object -Unique"
    ok2, out2, err2 = run_powershell(cmd2)
    if ok2 and out2:
        return sorted(set([line.strip() for line in out2.splitlines() if line.strip()]))
    raise RuntimeError(err or err2 or "Failed to enumerate adapters")

def get_current_dns(adapter):
    cmd = f"Get-DnsClientServerAddress -InterfaceAlias '{ps_quote(adapter)}' -AddressFamily IPv4 | Select-Object -ExpandProperty ServerAddresses"
    ok, out, err = run_powershell(cmd)
    if not ok:
        raise RuntimeError(err or "Failed to read DNS")
    lines = [l.strip() for l in out.splitlines() if l.strip()]
    return lines

def set_dns(adapter, servers):
    array_literal = "(" + ",".join([f"'{s}'" for s in servers]) + ")"
    cmd = f"Set-DnsClientServerAddress -InterfaceAlias '{ps_quote(adapter)}' -ServerAddresses {array_literal}"
    ok, out, err = run_powershell(cmd)
    if not ok:
        raise RuntimeError(err or "Failed to set DNS")

def reset_dns(adapter):
    cmd = f"Set-DnsClientServerAddress -InterfaceAlias '{ps_quote(adapter)}' -ResetServerAddresses"
    ok, out, err = run_powershell(cmd)
    if not ok:
        raise RuntimeError(err or "Failed to reset DNS")

def flush_dns_cache():
    cmd = "Clear-DnsClientCache"
    ok, out, err = run_powershell(cmd)
    if not ok:
        raise RuntimeError(err or "Failed to flush DNS cache")

# ---------------- Validation ----------------
ip_regex = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
def valid_ipv4(ip):
    if not ip_regex.match(ip):
        return False
    parts = [int(p) for p in ip.split(".")]
    return all(0 <= p <= 255 for p in parts)

# ---------------- Data Classes ----------------
@dataclass
class DNSPreset:
    name: str
    primary: str
    secondary: str
    description: str
    icon: str
    color: str

# ---------------- Main App ----------------
class DNSManagerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DNS Manager"
        self.page.window.resizable = True
        self.page.window.minimized = False
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 15
        
        
        
        # Theme Colors
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLUE_400,
                secondary=ft.Colors.CYAN_400,
                surface=ft.Colors.GREY_900,
                background=ft.Colors.BLACK,
            )
        )
        
        self.selected_adapter = None
        self.adapters = []
        self.logs = []
        
        # DNS Presets with metadata
        self.presets = [
            DNSPreset("Custom", "", "", "Configure your own DNS servers", ft.Icons.SETTINGS, ft.Colors.GREY_600),
            DNSPreset("Google", "8.8.8.8", "8.8.4.4", "Fastest & reliable public DNS", ft.Icons.SPEED, ft.Colors.BLUE_400),
            DNSPreset("Cloudflare", "1.1.1.1", "1.0.0.1", "Privacy-focused, most reliable", ft.Icons.SHIELD, ft.Colors.ORANGE_400),
            DNSPreset("Cloudflare Security", "1.1.1.2", "1.0.0.2", "Malware & phishing protection", ft.Icons.SECURITY, ft.Colors.ORANGE_600),
            DNSPreset("Quad9", "9.9.9.9", "149.112.112.112", "Best privacy & malware protection", ft.Icons.LOCK, ft.Colors.GREEN_400),
            DNSPreset("OpenDNS", "208.67.222.222", "208.67.220.220", "Cisco's reliable DNS service", ft.Icons.BUSINESS, ft.Colors.PURPLE_400),
            DNSPreset("AdGuard", "94.140.14.14", "94.140.15.15", "Best ad blocking DNS", ft.Icons.BLOCK, ft.Colors.RED_400),
            DNSPreset("Comodo Secure", "8.26.56.26", "8.20.247.20", "Security-focused DNS", ft.Icons.VERIFIED_USER, ft.Colors.TEAL_400),
            DNSPreset("CleanBrowsing", "185.228.168.9", "185.228.169.9", "Family-friendly filtering", ft.Icons.FAMILY_RESTROOM, ft.Colors.LIGHT_BLUE_400),
            DNSPreset("DNS.Watch", "84.200.69.80", "84.200.70.40", "Germany-based privacy DNS", ft.Icons.VISIBILITY, ft.Colors.AMBER_400),
            DNSPreset("UncensoredDNS", "91.239.100.100", "89.233.43.71", "Privacy-focused, uncensored DNS from Denmark", ft.Icons.VISIBILITY_OFF, ft.Colors.AMBER_400),
            DNSPreset("Mullvad DNS", "194.242.2.2", "194.242.2.3", "Privacy-first DNS from Mullvad VPN", ft.Icons.PRIVACY_TIP, ft.Colors.GREEN_600),
            DNSPreset("Neustar UltraDNS", "156.154.70.2", "156.154.71.2", "Enterprise-grade security DNS", ft.Icons.VERIFIED, ft.Colors.PURPLE_600),
            DNSPreset("Yandex DNS", "77.88.8.8", "77.88.8.1", "Russian DNS with basic, safe & family modes", ft.Icons.WARNING, ft.Colors.RED_600),
        ]
        
        self.selected_preset = self.presets[0]
        self.build_ui()
        
        # Load adapters in background
        threading.Thread(target=self.load_adapters_async, daemon=True).start()
    
    def build_ui(self):
        # Header
        self.header = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DNS, size=32, color=ft.Colors.BLUE_400),
                ft.Text("DNS Manager", size=24, weight=ft.FontWeight.BOLD),
                ft.Container(expand=True),
                
                
            ]),
            padding=20,
            
            border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.OUTLINE)),
        )
        
        # Adapter selection card
        self.adapter_dropdown = ft.Dropdown(
            label="Network Adapter",
            hint_text="Select a network adapter",
            prefix_icon=ft.Icons.ROUTER,
            expand=True,
            on_change=self.on_adapter_change,
        )
        
        self.refresh_btn = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_color=ft.Colors.PRIMARY,
            tooltip="Refresh adapters",
            on_click=lambda _: self.load_adapters_async_wrapper(),
        )
        
        self.current_dns_text = ft.Text(
            "Select an adapter to view current DNS",
            size=12,
            color=ft.Colors.GREY_500,
        )
        
        self.adapter_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        self.adapter_dropdown,
                        self.refresh_btn,
                    ]),
                    
                    self.current_dns_text,
                ]),
                
                padding=20,
            ),
            elevation=2,
        )
        
        # DNS Presets grid
        self.preset_grid = ft.GridView(
            expand=True,
            runs_count=3,
            max_extent=280,
            child_aspect_ratio=1.2,
            spacing=10,
            run_spacing=10,
            padding=ft.padding.symmetric(horizontal=20),
        )
        self.preset_group = ft.RadioGroup(
            value=self.selected_preset.name,
            on_change=self.on_preset_group_change,   # optional; keep if you want to react to dot clicks
            content=self.preset_grid
        )
    
        
        for preset in self.presets:
            self.preset_grid.controls.append(self.create_preset_card(preset))
        
        # Custom DNS inputs
        self.primary_dns = ft.TextField(
            label="Primary DNS",
            hint_text="e.g., 8.8.8.8",
            prefix_icon=ft.Icons.LOOKS_ONE,
            on_change=self.validate_dns_input,
        )
        
        self.secondary_dns = ft.TextField(
            label="Secondary DNS",
            hint_text="e.g., 8.8.4.4",
            prefix_icon=ft.Icons.LOOKS_TWO,
            on_change=self.validate_dns_input,
        )
        
        self.custom_dns_container = ft.Container(
            content=ft.Row([
                self.primary_dns,
                self.secondary_dns,
            ], spacing=20),
            padding=ft.padding.only(left=20, right=20, bottom=10),
        )
        
        # Action buttons
        self.apply_btn = ft.ElevatedButton(
            "Apply DNS",
            icon=ft.Icons.CHECK_CIRCLE,
            on_click=self.apply_dns,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_700,
            ),
        )
        
        self.reset_btn = ft.OutlinedButton(
            "Reset to Automatic",
            icon=ft.Icons.RESTORE,
            on_click=self.reset_dns,
        )
        
        self.flush_btn = ft.OutlinedButton(
            "Flush DNS Cache",
            icon=ft.Icons.CLEANING_SERVICES,
            on_click=self.flush_cache,
        )
        
        self.action_buttons = ft.Container(
            content=ft.Row([
                self.apply_btn,
                self.reset_btn,
                self.flush_btn,
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=20),
            padding=20,
        )
        
        # Status/Log area
        self.log_list = ft.ListView(
            expand=True,
            spacing=5,
            padding=ft.padding.all(10),
            auto_scroll=True,
        )
        
        self.log_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.TERMINAL, size=20),
                        ft.Text("Activity Log", weight=ft.FontWeight.BOLD),
                        ft.Container(expand=True),
                        ft.IconButton(
                            icon=ft.Icons.CLEAR_ALL,
                            icon_size=20,
                            tooltip="Clear logs",
                            on_click=self.clear_logs,
                        ),
                    ]),
                    ft.Divider(height=1),
                    ft.Container(
                        content=self.log_list,
                        height=150,
                        border=ft.border.all(1, ft.Colors.OUTLINE),
                        border_radius=5,
                    ),
                ]),
                padding=20,
            ),
            elevation=2,
        )
        
        # Main layout
        self.page.add(
            ft.Column([
                self.header,
                ft.Container(
                    content=ft.Column([
                        self.adapter_card,
                        ft.Text("DNS Presets", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PRIMARY),
                        ft.Container(
                            content=self.preset_group,
                            height=300,
                        ),
                        self.custom_dns_container,
                        self.action_buttons,
                        self.log_card,
                    ], spacing=20),
                    padding=ft.padding.only(top=20),
                    expand=True,
                    
                    
                ),
            ], expand=True, spacing=0,scroll=ft.ScrollMode.ADAPTIVE)
        )
    
    def create_preset_card(self, preset: DNSPreset):
        def on_click(e):
            self.select_preset(preset)
        
        card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Icon(preset.icon, size=24, color=preset.color),
                        ft.Container(expand=True),
                        ft.Radio(value=preset.name, fill_color=preset.color),
                    ]),
                    ft.Text(preset.name, size=16, weight=ft.FontWeight.W_500),
                    ft.Text(preset.description, size=11, color=ft.Colors.GREY_400),
                    ft.Container(height=5),
                    ft.Column([
                        ft.Text(f"Primary: {preset.primary}" if preset.primary else "Custom configuration", 
                               size=10, color=ft.Colors.GREY_500),
                        ft.Text(f"Secondary: {preset.secondary}" if preset.secondary else "", 
                               size=10, color=ft.Colors.GREY_500),
                    ], spacing=2),
                ], spacing=5),
                padding=15,
                on_click=on_click,
                ink=True,
            ),
            elevation=1,
        )
        
        # Store reference for selection
        card.data = preset
        return card
    
    def select_preset(self, preset: DNSPreset):
        self.preset_group.value = preset.name      # this checks the right radio
        self.selected_preset = preset
        self.primary_dns.value = preset.primary
        self.secondary_dns.value = preset.secondary
        self.add_log(f"Selected preset: {preset.name}", ft.Colors.BLUE_400)
        self.page.update()

    def on_preset_group_change(self, e: ft.ControlEvent):
        name = e.control.value
        preset = next((p for p in self.presets if p.name == name), None)
        if preset:
            self.selected_preset = preset
            self.primary_dns.value = preset.primary
            self.secondary_dns.value = preset.secondary
            self.page.update()

    
    
    def close_dialog(self, dlg):
        dlg.open = False
        self.page.update()
    
    def load_adapters_async(self):
        try:
            self.add_log("Loading network adapters...", ft.Colors.YELLOW_700)
            self.adapters = list_adapters()
            
            # Update UI in main thread
            self.adapter_dropdown.options = [
                ft.dropdown.Option(adapter) for adapter in self.adapters
            ]
            if self.adapters:
                self.adapter_dropdown.value = self.adapters[0]
                self.selected_adapter = self.adapters[0]
                self.show_current_dns()
            
            self.add_log(f"Loaded {len(self.adapters)} adapter(s)", ft.Colors.GREEN_400)
        except Exception as e:
            self.add_log(f"Error loading adapters: {e}", ft.Colors.RED_400)
        
        self.page.update()
    
    def load_adapters_async_wrapper(self):
        threading.Thread(target=self.load_adapters_async, daemon=True).start()
    
    def on_adapter_change(self, e):
        self.selected_adapter = e.control.value
        self.show_current_dns()
    
    def show_current_dns(self):
        if not self.selected_adapter:
            return
        
        try:
            servers = get_current_dns(self.selected_adapter)
            if servers:
                self.current_dns_text.value = f"Current DNS: {', '.join(servers)}"
                self.current_dns_text.color = ft.Colors.GREEN_400
            else:
                self.current_dns_text.value = "Using automatic DNS (DHCP)"
                self.current_dns_text.color = ft.Colors.BLUE_400
        except Exception as e:
            self.current_dns_text.value = f"Error reading DNS: {e}"
            self.current_dns_text.color = ft.Colors.RED_400
        
        self.page.update()
    
    def validate_dns_input(self, e):
        value = e.control.value.strip()
        if value and not valid_ipv4(value):
            e.control.error_text = "Invalid IPv4 address"
        else:
            e.control.error_text = None
        self.page.update()
    
    def apply_dns(self, e):
        if not self.selected_adapter:
            self.show_error("Please select a network adapter first")
            return
        
        primary = self.primary_dns.value.strip()
        secondary = self.secondary_dns.value.strip()
        
        if not primary:
            self.show_error("Primary DNS is required")
            return
        
        if not valid_ipv4(primary):
            self.show_error("Invalid primary DNS address")
            return
        
        if secondary and not valid_ipv4(secondary):
            self.show_error("Invalid secondary DNS address")
            return
        
        servers = [primary]
        if secondary:
            servers.append(secondary)
        
        def apply_async():
            try:
                self.add_log(f"Applying DNS to {self.selected_adapter}...", ft.Colors.YELLOW_700)
                set_dns(self.selected_adapter, servers)
                self.add_log(f"DNS applied successfully: {', '.join(servers)}", ft.Colors.GREEN_400)
                self.show_current_dns()
                self.show_success("DNS settings applied successfully!")
            except Exception as ex:
                self.add_log(f"Error: {ex}", ft.Colors.RED_400)
                self.show_error(f"Failed to apply DNS: {ex}")
        
        threading.Thread(target=apply_async, daemon=True).start()
    
    def reset_dns(self, e):
        if not self.selected_adapter:
            self.show_error("Please select a network adapter first")
            return
        
        def reset_async():
            try:
                self.add_log(f"Resetting DNS for {self.selected_adapter}...", ft.Colors.YELLOW_700)
                reset_dns(self.selected_adapter)
                self.add_log("DNS reset to automatic (DHCP)", ft.Colors.GREEN_400)
                self.show_current_dns()
                self.show_success("DNS reset to automatic successfully!")
            except Exception as ex:
                self.add_log(f"Error: {ex}", ft.Colors.RED_400)
                self.show_error(f"Failed to reset DNS: {ex}")
        
        threading.Thread(target=reset_async, daemon=True).start()
    
    def flush_cache(self, e):
        def flush_async():
            try:
                self.add_log("Flushing DNS cache...", ft.Colors.YELLOW_700)
                flush_dns_cache()
                self.add_log("DNS cache flushed successfully", ft.Colors.GREEN_400)
                self.show_success("DNS cache flushed successfully!")
            except Exception as ex:
                self.add_log(f"Error: {ex}", ft.Colors.RED_400)
                self.show_error(f"Failed to flush cache: {ex}")
        
        threading.Thread(target=flush_async, daemon=True).start()
    
    def add_log(self, message: str, color=None):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = ft.Row([
            ft.Text(f"[{timestamp}]", size=11, color=ft.Colors.GREY_500),
            ft.Text(message, size=12, color=color or ft.Colors.GREY_300),
        ], spacing=10)
        self.log_list.controls.append(log_entry)
        if len(self.log_list.controls) > 100:
            self.log_list.controls.pop(0)
        self.page.update()
    
    def clear_logs(self, e):
        self.log_list.controls.clear()
        self.page.update()
    
    def show_success(self, message: str):
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.GREEN_700,
            action="OK",
        )
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()
    
    def show_error(self, message: str):
        snack = ft.SnackBar(
            content=ft.Text(message),
            bgcolor=ft.Colors.RED_700,
            action="OK",
        )
        self.page.snack_bar = snack
        snack.open = True
        self.page.update()

def main(page: ft.Page):
    DNSManagerApp(page)

if __name__ == "__main__":
    if platform.system() != "Windows":
        print("This tool supports Windows only.")
        sys.exit(1)
    
    if not is_admin():
        relaunch_as_admin()
        sys.exit(0)
    
    ft.app(target=main)
