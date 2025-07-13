import os
import shutil
import sys
import time
import ctypes
import webbrowser
from pyfiglet import Figlet
from rich.console import Console
from rich.prompt import Prompt

console = Console()
fig = Figlet(font='slant')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def typewriter(message, delay=0.04):
    for char in message:
        console.print(char, end="", style="white", highlight=False, soft_wrap=True)
        time.sleep(delay)
    print()

def print_ascii_rainbow(text):
    colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
    output = fig.renderText(text).splitlines()
    for i, line in enumerate(output):
        color = colors[i % len(colors)]
        console.print(line, style=color)

def main_sequence():
    typewriter("If you paid more than $15 for this you got scammed.")
    time.sleep(1)
    os.system('cls' if os.name == 'nt' else 'clear')
    print_ascii_rainbow("MINECRAFT")
    typewriter("Made by Kaz.")
    time.sleep(1)

    # -------------------------
    # Start your main program
    # -------------------------
    console.rule("[bold cyan]IOBit Unlocker Check[/bold cyan]")
    iobit_installed = Prompt.ask("Is IOBit Unlocker installed? (yes/no)").lower()
    if iobit_installed != "yes":
        console.print("\n[red]IOBit Unlocker is required. Opening your browser now...[/red]")
        webbrowser.open("https://cdn.iobit.com/dl/unlocker-setup.exe")
        console.print("[yellow]Download and install IOBit Unlocker, then run this script again.[/yellow]")
        return

    console.rule("[bold cyan]Locate SYSWOW64 DLL[/bold cyan]")
    syswow64_path = Prompt.ask("Enter full path to hacked SYSWOW64 'Windows.ApplicationModel.Store.dll'")
    if not os.path.exists(syswow64_path):
        console.print(f"[red]File not found at: {syswow64_path}[/red]")
        return

    console.rule("[bold cyan]Locate System32 DLL[/bold cyan]")
    system32_path = Prompt.ask("Enter full path to hacked System32 'Windows.ApplicationModel.Store.dll'")
    if not os.path.exists(system32_path):
        console.print(f"[red]File not found at: {system32_path}[/red]")
        return

    console.rule("[bold cyan]Manual Deletion with IOBit Unlocker[/bold cyan]")
    console.print(
        "\n1. Open IOBit Unlocker."
        "\n2. Add:\n"
        "   - C:\\Windows\\System32\\Windows.ApplicationModel.Store.dll\n"
        "   - C:\\Windows\\SysWOW64\\Windows.ApplicationModel.Store.dll"
        "\n3. Select 'Unlock & Delete' for each."
        "\n4. Accept UAC prompts."
    )
    input("\nPress Enter once both files are deleted...")

    console.rule("[bold cyan]Deploying DLLs[/bold cyan]")
    try:
        shutil.copy2(system32_path, r"C:\Windows\System32\Windows.ApplicationModel.Store.dll")
        console.print("[green]System32 DLL copied successfully.[/green]")
        shutil.copy2(syswow64_path, r"C:\Windows\SysWOW64\Windows.ApplicationModel.Store.dll")
        console.print("[green]SYSWOW64 DLL copied successfully.[/green]")
        console.print("[bold green]Deployment complete. You may need to restart your PC.[/bold green]")
    except PermissionError:
        console.print("[red]Permission denied. Please rerun as Administrator.[/red]")
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")

if __name__ == "__main__":
    if not is_admin():
        console.print(f"[red]{fig.renderText('RUN AS ADMIN')}[/red]")
        time.sleep(5)
        sys.exit(1)
    else:
        main_sequence()
