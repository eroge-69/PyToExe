from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align
from rich.layout import Layout
from rich import box
from rich.live import Live
from rich.table import Table
from datetime import datetime
import itertools
import asyncio
import websockets
import pyperclip
import os
import time

console = Console()

def log(message: str, status: str = "✓", color: str = "green"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    console.print(f"[bold {color}]{status}[/] [dim]{timestamp}[/] • {message}")

def print_rainbow_banner():
    colors = ["red", "orange1", "yellow", "green", "cyan", "blue", "magenta"]
    banner_lines = [
        r" ███████╗ █████╗ ██╗  ██╗██╗███╗   ██╗",
        r" ██╔════╝██╔══██╗██║ ██╔╝██║████╗  ██║",
        r" █████╗  ███████║█████╔╝ ██║██╔██╗ ██║",
        r" ██╔══╝  ██╔══██║██╔═██╗ ██║██║╚██╗██║",
        r" ███████╗██║  ██║██║  ██╗██║██║ ╚████║",
        r" ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝"
    ]

    rainbow = itertools.cycle(colors)
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print()  # Top padding

    for line in banner_lines:
        text = Text()
        for char in line:
            text.append(char, style=next(rainbow) if char != " " else " ")
        console.print(Align.center(text))
        time.sleep(0.05)  # Optional animation delay

    console.print()
    panel = Panel.fit(
        Align.center("✅ [bold green]AUTOJOINER LOADED", vertical="middle"),
        title="[bold yellow]STATUS",
        border_style="bright_magenta",
        box=box.ROUNDED
    )
    console.print(panel)
    console.print()  # Bottom padding

async def handler(websocket):
    last_clip = ""
    while True:
        try:
            text = pyperclip.paste()
            is_gncode = "_G.CHB_ENC_CODE" in text and "loadstring" in text
            is_teleport = "TeleportService" in text and "TeleportToPlaceInstance" in text

            if text != last_clip and (is_gncode or is_teleport):
                await websocket.send(text)
                if is_gncode:
                    log("Auto-Join script (GN Code) sent to WebSocket!", "🚀", "cyan")
                else:
                    log("Teleport script detected and sent to WebSocket!", "🚀", "blue")
                last_clip = text
                pyperclip.copy("")  # Prevent re-send
            await asyncio.sleep(0.3)
        except websockets.ConnectionClosed:
            log("WebSocket disconnected.", "⚠️", "yellow")
            break

async def main():
    print_rainbow_banner()
    try:
        async with websockets.serve(handler, "localhost", 8765):
            log("Server is ready. Listening for copied join scripts...", "🔌")
            await asyncio.Future()  # Keep server alive
    except OSError as e:
        log(f"Server failed to start: {e}", "❌", "red")

asyncio.run(main())
