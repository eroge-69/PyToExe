# intruder_game.py (Enhanced CLI Horror Game)
import os
import sys
import time
import random
import platform
import getpass
import subprocess
import ctypes
import msvcrt
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

# === AUTO-INSTALL DEPENDENCIES ===
required = ['rich']
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])
        os.execl(sys.executable, sys.executable, *sys.argv)

# === SYSTEM INFO ===
user = getpass.getuser()
system = platform.system()
release = platform.release()
hostname = platform.node()
start_time = time.strftime("%H:%M:%S")
start_date = time.strftime("%Y-%m-%d")
current_hour = int(time.strftime("%H"))
is_critical_hour = current_hour == 0  # Midnight

console = Console()
radars = [f"Radar {i}" for i in range(1, 9)]  # 8 sectors
active_intruder = None
face_shown = False
boot_completed = False

# === PLAYER STATE ===
player_score = 0

# === CATCH PROBABILITY ===
def calculate_probability():
    base = int(time.strftime("%S"))
    bonus = 20 if is_critical_hour else 0
    score_factor = min(20, player_score)  # max +20% for high score
    return min(100, base + bonus + score_factor)

def boot_animation():
    console.print("[bold cyan]=== INTRUDER.EXE DEFENSE SYSTEM ===[/bold cyan]")
    console.print(f"[dim]Booted at {start_time} on {start_date}[/dim]")
    console.print(f"[dim]Logged in as: {user}@{hostname}[/dim]")
    console.print("\nInitializing sensors:")
    for i in range(0, calculate_probability()+1, 10):
        bar = "[" + "=" * (i // 10) + " " * ((100 - i) // 10) + "]"
        console.print(f"{bar} {i}%", end='\r')
        time.sleep(0.1)
    console.print("\n[bold green]System ready.[/bold green]\n")
    global boot_completed
    boot_completed = True

def show_popup(title, text):
    try:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)
    except Exception:
        pass

def breakthrough_error():
    console.print("\n[bold red]⛔ SYSTEM FAILURE: [CRIT.EXE::EXCEPTION_THROWN][/bold red]")
    console.print("[red]>>> Unhandled exception in core process INTPY :: 0x0000FFAA[/red]")
    show_popup("INTRUDER.EXE - CRITICAL ERROR", "INTPY process failed. Entity breach confirmed.")
    time.sleep(3)
    glitch_sequence()

def flatline_command(sector_num):
    global active_intruder, player_score
    try:
        if int(sector_num) == radars.index(active_intruder) + 1:
            console.print(f"[bold green]✅ Sector {sector_num} neutralized.[/bold green]")
            player_score += 1
            time.sleep(2)
            reset_to_idle()
            return True
        else:
            console.print(f"[bold red]❌ Incorrect sector. Entity advanced.[/bold red]")
            player_score = max(0, player_score - 1)
            return False
    except:
        return False

def glitch_face():
    global face_shown
    if face_shown:
        return
    face_shown = True
    door = """
    [bold red]
       _________
      |         |
      |   OPEN  |
      |   DOOR  |   !
      |_________|
    [/bold red]
    """
    print(door)
    time.sleep(3)

def leave_payload():
    with open("I_SEE_YOU.txt", "w") as f:
        f.write(f"YOU LET THEM IN.\nUSER: {user}\nTIME: {start_time}\n")

def glitch_sequence():
    glitch_face()
    leave_payload()
    console.print("\n[bold red]THE DOOR IS OPEN.[/bold red]")
    show_popup("DOOR OPENED", "They are in.")
    time.sleep(2)
    os._exit(1)

def draw_minimap():
    table = Table(title="[bold]SECTOR MAP[/bold]", box=box.ROUNDED)
    for i in range(1, 9):
        label = f"Sector {i}"
        if active_intruder == f"Radar {i}":
            label += " [bold red]![/bold red]"
        table.add_column(label, justify="center")
    table.add_row(*([" "] * 8))
    console.print(table)

def draw_probability_bar():
    prob = calculate_probability()
    bar = "[" + "=" * (prob // 10) + " " * ((100 - prob) // 10) + "]"
    console.print(f"[bold magenta]Catch Probability:[/bold magenta] {bar} {prob}%\n")

def response_timer():
    timeout = 10
    console.print("[bold green]>>> flatline [sector_number][/bold green] (10s)")
    start = time.time()
    response = ""
    while time.time() - start < timeout:
        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if char in ['\r', '\n']:
                break
            response += char
        time.sleep(0.05)
    if not response:
        breakthrough_error()
        return False
    parts = response.strip().lower().split()
    if len(parts) == 2 and parts[0] == "flatline" and parts[1].isdigit():
        return flatline_command(parts[1])
    else:
        breakthrough_error()
        return False

def reset_to_idle():
    global active_intruder
    active_intruder = None
    clear_screen()
    show_header()

def alert_sequence():
    global active_intruder
    while True:
        prob = calculate_probability()
        base_min = 60
        base_max = 600
        delay = int(base_max - (base_max - base_min) * (prob / 100))
        if prob > 80 and random.random() < 0.25:
            delay = random.randint(5, 15)
        hour = int(time.strftime("%H"))
        if hour in range(0, 3):
            delay = max(10, int(delay * 0.7))
        elif hour in range(6, 18):
            delay = int(delay * 1.2)

        remaining = delay
        while remaining > 0:
            clear_screen()
            show_header()
            draw_probability_bar()
            draw_minimap()
            console.print("[bold cyan]INTELLIGENT SECURITY DETECTOR[/bold cyan]")
            console.print(f"[yellow]Next likely intrusion event in:[/yellow] {remaining} seconds")
            time.sleep(1)
            current_prob = calculate_probability()
            if current_prob >= 40:
                remaining -= random.randint(4, 9)
            else:
                remaining += random.randint(1, 3)
            if remaining < 0:
                remaining = 0
        active_intruder = random.choice(radars)
        clear_screen()
        show_header()
        draw_probability_bar()
        draw_minimap()
        console.print(f"\n[bold yellow]🚨 ALERT: Motion on {active_intruder}[/bold yellow]\n")
        success = response_timer()
        if not success:
            return
        time.sleep(1)
        reset_to_idle()

def show_header():
    console.print("[bold cyan]=== INTRUDER.EXE DEFENSE SYSTEM ===[/bold cyan]")
    console.print(f"[dim]Booted at {start_time} on {start_date}[/dim]")
    console.print(f"[dim]Logged in as: {user}@{hostname}[/dim]")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    boot_animation()
    reset_to_idle()
    alert_sequence()

if __name__ == "__main__":
    main()
