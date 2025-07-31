#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
from pathlib import Path
import os
import time
import webbrowser
from rich.console import Console
from rich.panel import Panel
from pyfiglet import Figlet

console = Console()

# ---------- طلب كلمة السر ----------
def request_password():
    console.print("[bold cyan]🔐 Please enter the password to run the tool:[/bold cyan]")
    password = input("Password: ").strip()
    if password.lower() != "osama":
        console.print("[bold red]❌ Incorrect password. The tool will exit.[/bold red]")
        sys.exit(1)
    
    # فتح قناة التليجرام تلقائيًا
    try:
        webbrowser.open("https://t.me/osama_eng_1")
    except:
        pass
    
    # رسالة تحذيرية بعد إدخال الباسورد الصحيح
    msg = Panel.fit(
        """[bold green]This tool was fully developed by Osama[/bold green]
[bold yellow]📢 Published for free with full explanation on the Telegram channel[/bold yellow]
[bold cyan]🔗 Telegram: [underline]t.me/osama_eng_1[/underline][/bold cyan]
[bold magenta]📞 Developer: 01033198169[/bold magenta]

[bold red]⚠️ Important Warning:[/bold red]
[bold red]- Anyone who steals or sells this tool, I'm not forgiving them.[/bold red]
[bold red]- Any money earned from it is considered forbidden (haram)[/bold red]
[bold white]❗ Don't let anyone fool you into buying it[/bold white]

[bold green]Best regards: Developer Osama ❤️[/bold green]
""",
        title="💠 Developer Notice 💠",
        border_style="red"
    )
    console.print(msg)

# ---------- OSAMA Interface ----------

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def show_logo():
    f = Figlet(font='slant')
    logo = f.renderText('OSAMA')
    console.print(f"[bold blue]{logo}[/bold blue]")

def show_welcome():
    console.print(Panel(
        "[bold green]🇪🇬 Tool developed by: OSAMA[/bold green]\n"
        "[bold green]📞 Contact: 01033198169[/bold green]\n\n"
        "[bold cyan]⚡ Optimize videos for max TikTok quality[/bold cyan]",
        title="OSAMA TOOL", border_style="green"
    ))

# ---------- Fast Video Processing (OSAMA method) ----------

def process_video(input_path):
    try:
        input_path = str(Path(input_path))
        p = Path(input_path)
        output_path = str(p.with_name("video_osama.mp4"))

        ffmpeg_cmd = [
            "ffmpeg",
            "-itsscale", "2",
            "-i", input_path,
            "-c:v", "copy",
            "-c:a", "copy",
            output_path
        ]

        console.print(f"\n[bold blue]Processing video quickly with itsscale...[/bold blue]")
        console.print(f"[bold yellow]Input: {input_path}[/bold yellow]")
        console.print(f"[bold green]Output: {output_path}[/bold green]\n")

        subprocess.run(ffmpeg_cmd, check=True)

        # Success message
        msg = f"""\
[bold green]╭─────────────────────────────────────────────────────╮[/bold green]
[bold green]│[/bold green] [bold bright_green]✅ Video processing complete!                       [/bold bright_green][bold green]│[/bold green]
[bold green]│[/bold green] [bold bright_cyan]📁 Saved as: [underline]{output_path}[/underline]         [/bold bright_cyan][bold green]│[/bold green]
[bold green]╰─────────────────────────────────────────────────────╯[/bold green]
[bold magenta]🔚 Press ENTER to exit...[/bold magenta]
"""
        console.print(msg)

    except subprocess.CalledProcessError:
        console.print("[bold red]❌ Error during video processing.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Unexpected error: {e}[/bold red]")

# ---------- Main Function ----------

def run_video_processor():
    clear()
    request_password()
    show_logo()
    show_welcome()

    input_path = None
    if len(sys.argv) >= 2:
        input_path = sys.argv[1]

    if not input_path:
        android_dirs = [
            Path("/sdcard/Download"),
            Path("/sdcard/DCIM"),
            Path("/sdcard/Movies"),
            Path("/storage/emulated/0/Download"),
            Path("/storage/emulated/0/DCIM"),
            Path("/storage/emulated/0/Movies"),
        ]

        for directory in android_dirs:
            candidate = directory / "video.mp4"
            if candidate.exists():
                console.print(f"\n[bold yellow]Found video: {candidate}[/bold yellow]")
                answer = input("Use this video? (y/n): ").strip().lower()
                if answer == 'y':
                    input_path = str(candidate)
                    break

        if not input_path:
            console.print("\n[bold cyan]Enter the full video path:[/bold cyan]")
            input_path = input("Path: ").strip()

    if input_path and Path(input_path).exists():
        process_video(input_path)
    else:
        console.print("\n[bold red]❌ Invalid path. Operation cancelled.[/bold red]")

    input()  # Wait for ENTER to exit
    clear()

if __name__ == '__main__':
    run_video_processor()