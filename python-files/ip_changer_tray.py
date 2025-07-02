import subprocess
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw

# Create a simple black-and-white tray icon
def create_image():
    image = Image.new('RGB', (64, 64), color='black')
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill='white')
    return image

# Functions to execute IP change commands
def set_static_ip(icon, item):
    commands = [
        'netsh interface ip set address "Ethernet" static 192.168.0.21 255.255.255.0 192.168.0.1',
        'netsh interface ip add dns "Ethernet" addr="192.168.0.8"',
        'netsh interface ip add dns "Ethernet" addr="192.168.0.10"',
    ]
    for cmd in commands:
        subprocess.call(cmd, shell=True)

def enable_dhcp(icon, item):
    commands = [
        'netsh interface ip set address "Ethernet" source=dhcp',
        'netsh interface ip set dnsservers "Ethernet" source=dhcp',
    ]
    for cmd in commands:
        subprocess.call(cmd, shell=True)

def exit_app(icon, item):
    icon.stop()

# Tray icon and menu
icon = Icon("IPChanger")
icon.icon = create_image()
icon.menu = Menu(
    MenuItem("Set Static IP", set_static_ip),
    MenuItem("Enable DHCP", enable_dhcp),
    MenuItem("Exit", exit_app)
)

icon.run()
