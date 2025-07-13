import os
import sys
import time
import webbrowser
import socket
import dns.resolver
import whois
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from datetime import datetime
from random import randint, choice

console = Console()

# === WHOIS + DNS ВСТРОЕННЫЕ МОДУЛИ ===
def whois_hunter(domain):
    try:
        result = whois.whois(domain)
        return str(result)
    except Exception as e:
        return f"[WHOIS ERROR] {e}"

def dns_recon(domain):
    try:
        ip = socket.gethostbyname(domain)
    except Exception as e:
        ip = f"[IP ERROR] {e}"

    dns_info = {"A": [], "NS": [], "MX": [], "TXT": []}
    for rtype in dns_info.keys():
        try:
            answers = dns.resolver.resolve(domain, rtype)
            dns_info[rtype] = [str(r) for r in answers]
        except:
            dns_info[rtype] = ["-"]

    return ip, dns_info

def run_script(mode):
    console.rule(f"[bold cyan]{mode} РЕЗУЛЬТАТЫ")
    domain = console.input("🌐 Введите домен для анализа: ").strip()

    if mode == "WHOIS Hunter":
        result = whois_hunter(domain)
        console.print(result)
    elif mode == "DNS Recon":
        ip, dns_info = dns_recon(domain)
        console.print(f"🌐 Домен: {domain}\n📡 IP: {ip}")
        for k, v in dns_info.items():
            console.rule(f"[bold blue]{k} записи")
            console.print("\n".join(v))
    time.sleep(2)

def open_url(url):
    console.print(f"[bold yellow]🔎 Открываю:[/bold yellow] {url}")
    webbrowser.open(url)
    time.sleep(1)

# === ОСНОВНОЙ OSINT-МЕНЮ ===
def run_osint_menu():
    while True:
        console.rule("[bold magenta]📁 OSINT-МЕНЮ", style="bold magenta")
        console.print("[1] WHOIS Hunter")
        console.print("[2] DNS Recon")
        console.print("[3] Telegram Search")
        console.print("[4] VK Profile Check")
        console.print("[5] TikTok Username Check")
        console.print("[6] Instagram Profile Check")
        console.print("[7] YouTube Channel Check")
        console.print("[8] Pinterest Profile Check")
        console.print("[0] Выход\n")
        user_choice = console.input("[bold green]Выбор модуля:[/bold green] ").strip()

        if user_choice == "1":
            run_script("WHOIS Hunter")
        elif user_choice == "2":
            run_script("DNS Recon")
        elif user_choice == "3":
            username = console.input("[cyan]🔍 Введите username:[/cyan] ").strip()
            open_url(f"https://t.me/{username}")
        elif user_choice == "4":
            username = console.input("[cyan]🔍 Введите username:[/cyan] ").strip()
            open_url(f"https://vk.com/{username}")
        elif user_choice == "5":
            username = console.input("[cyan]🔍 Введите username:[/cyan] ").strip()
            open_url(f"https://tiktok.com/@{username}")
        elif user_choice == "6":
            username = console.input("[cyan]🔍 Введите username:[/cyan] ").strip()
            open_url(f"https://instagram.com/{username}")
        elif user_choice == "7":
            username = console.input("[cyan]🔍 Введите username:[/cyan] ").strip()
            open_url(f"https://youtube.com/@{username}")
        elif user_choice == "8":
            username = console.input("[cyan]🔍 Введите username:[/cyan] ").strip()
            open_url(f"https://pinterest.com/{username}")
        elif user_choice == "0":
            console.print("[red]👋 До встречи, агент BLACK RECON.[/red]")
            sys.exit()
        else:
            console.print("[red]❌ Неверный выбор.[/red]")
            time.sleep(1)

# === АНИМАЦИЯ + СТИЛЬ ===
def glitch_line(text, delay=0.01):
    glitch_chars = ['#', '%', '$', '!', '*', '@']
    for _ in range(5):
        fake = ''.join(choice(glitch_chars) for _ in range(len(text)))
        console.print(f"[bold red]{fake}[/bold red]", end='\r')
        time.sleep(0.03)
    console.print(f"[bold green]{text}[/bold green]")

def show_banner():
    console.print(Panel.fit("\U0001F9E0 [bold white on green] BLACK RECON SYSTEM BOOTING [/bold white on green]", border_style="bold green"))

def authorize():
    key = console.input("[bold cyan]\U0001F512 Введите ключ доступа:[/bold cyan] ")
    if key.strip() != "recon2025":
        console.print("[bold red]❌ Доступ запрещён. Сигнал тревоги активирован.[/bold red]")
        sys.exit()
    console.print("[bold green]✅ Успешная авторизация. Добро пожаловать, агент BLACK RECON.[/bold green]")
    time.sleep(1)

def load_modules():
    modules = [
        "🧠 Инициализация ядра OSINT",
        "📡 Активация сетевого сканера",
        "🕵️ Подключение к зеркалам разведданных",
        "💾 Загрузка логов",
        "🔐 Дешифровка потоков",
        "🛰️ Синхронизация с ReconNet"
    ]
    with Progress(TextColumn("[bold yellow]{task.description}"), BarColumn(), transient=True) as progress:
        for module in modules:
            task = progress.add_task(module, total=100)
            for _ in range(randint(3, 7)):
                progress.update(task, advance=randint(10, 30))
                time.sleep(0.2)
            progress.update(task, completed=100)
            time.sleep(0.3)

def main_terminal():
    console.rule("[bold green]>>> BLACK RECON ONLINE <<<")
    glitch_line("📂 SYSTEM STATUS: READY")
    glitch_line("💻 ВХОД В ТЕРМИНАЛ УСПЕШЕН")
    console.rule("[bold red]СИСТЕМА ГОТОВА К ВЗЛОМУ")

def intro():
    os.system("cls" if os.name == "nt" else "clear")
    show_banner()
    console.print(Panel("[bold cyan]Запуск боевого интерфейса...[/bold cyan]", border_style="cyan"))
    time.sleep(1.5)
    authorize()
    console.print("[cyan]📡 Загрузка системных модулей...[/cyan]")
    time.sleep(1)
    load_modules()
    main_terminal()

if __name__ == "__main__":
    intro()
    run_osint_menu()
