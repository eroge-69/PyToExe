import importlib.util
import multiprocessing
import os
import resource
import ast
import sys
import logging
import time
import random
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.progress import Progress
from cryptography.fernet import Fernet
import psutil
import win32process
import win32con

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

key = Fernet.generate_key()
cipher = Fernet(key)

ALLOWED_MODULES = ["math", "random", "ctypes"]
RESTRICTED_FUNCTIONS = ["eval", "exec", "os.system", "subprocess.run"]

def encrypt_log(message):
    return cipher.encrypt(message.encode()).decode()

class ScriptValidator(ast.NodeVisitor):
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name not in ALLOWED_MODULES:
                raise ValueError(f"Importation de '{alias.name}' interdite")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module not in ALLOWED_MODULES:
            raise ValueError(f"Importation depuis '{node.module}' interdite")
        self.generic_visit(node)

    def visit_Name(self, node):
        if node.id in RESTRICTED_FUNCTIONS:
            raise ValueError(f"Fonction '{node.id}' interdite")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "sys":
            raise ValueError(f"Accès à 'sys.{node.attr}' interdit")
        self.generic_visit(node)

def check_process(process_name="cod.exe"):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == process_name.lower():
            console.print(Panel(f"[green]Processus {process_name} trouvé (PID: {proc.pid})[/green]"))
            return proc.pid
    console.print(Panel(f"[red]Processus {process_name} non trouvé[/red]"))
    return None

def check_script(script_path):
    with Progress() as progress:
        task = progress.add_task("[cyan]Validation...", total=100)
        time.sleep(random.uniform(0.1, 0.3))
        with open(script_path, "r") as f:
            code = f.read()
        progress.update(task, advance=30)
        tree = ast.parse(code)
        progress.update(task, advance=60)
        validator = ScriptValidator()
        validator.visit(tree)
        progress.update(task, advance=100)
        console.print(Panel("[green]Validation OK[/green]"))

def run_script(script_path, pid):
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (1, 1))
        resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, 50 * 1024 * 1024))
        resource.setrlimit(resource.RLIMIT_NOFILE, (5, 5))

        original_modules = sys.modules.copy()
        sys.modules.clear()
        sys.modules.update({k: v for k, v in original_modules.items() if k in ALLOWED_MODULES + ["builtins", "ctypes"]})

        try:
            process_handle = win32process.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, pid)
            console.print(Panel(f"[cyan]Connecté au processus {pid}[/cyan]"))
        except Exception as e:
            console.print(Panel(f"[red]Erreur connexion : {str(e)}[/red]"))
            return

        spec = importlib.util.spec_from_file_location("script_module", script_path)
        module = importlib.util.module_from_spec(spec)
        module.__import__ = lambda name, *args, **kwargs: safe_import(name, *args, **kwargs)
        with Progress() as progress:
            task = progress.add_task("[cyan]Exécution...", total=100)
            time.sleep(random.uniform(0.2, 0.5))
            spec.loader.exec_module(module)
            progress.update(task, advance=100)
            console.print(Panel("[green]Exécution OK[/green]"))

        sys.modules.clear()
        sys.modules.update(original_modules)
    except Exception as e:
        console.print(Panel(f"[red]Erreur : {str(e)}[/red]"))
        logger.error(encrypt_log(f"Erreur exécution : {str(e)}"))

def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name in ALLOWED_MODULES:
        return __import__(name, globals, locals, fromlist, level)
    raise ImportError(f"Module '{name}' interdit")

def list_scripts():
    script_dir = "scripts"
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)
        return []
    return [f for f in os.listdir(script_dir) if f.endswith(".py")]

def display_menu():
    table = Table(title="BO6 Cheat Executor")
    table.add_column("Option", style="cyan")
    table.add_column("Description", style="magenta")
    table.add_row("1", "Vérifier cod.exe")
    table.add_row("2", "Lister scripts")
    table.add_row("3", "Exécuter script")
    table.add_row("4", "Quitter")
    console.print(table)

def main():
    console.print(Panel("[yellow]BO6 Cheat Executor - Charge scripts depuis 'scripts/'[/yellow]"))
    pid = None
    while True:
        display_menu()
        choice = Prompt.ask("Option", choices=["1", "2", "3", "4"], default="1")
        if choice == "1":
            pid = check_process("cod.exe")
        elif choice == "2":
            scripts = list_scripts()
            if not scripts:
                console.print(Panel("[red]Aucun script dans 'scripts/'[/red]"))
            else:
                table = Table(title="Scripts disponibles")
                table.add_column("Numéro", style="cyan")
                table.add_column("Nom", style="magenta")
                for i, script in enumerate(scripts, 1):
                    table.add_row(str(i), script)
                console.print(table)
        elif choice == "3":
            if not pid:
                console.print(Panel("[red]Vérifiez d'abord cod.exe[/red]"))
                continue
            scripts = list_scripts()
            if not scripts:
                console.print(Panel("[red]Aucun script dans 'scripts/'[/red]"))
                continue
            script_idx = Prompt.ask("Numéro du script", choices=[str(i) for i in range(1, len(scripts) + 1)])
            script_path = os.path.join("scripts", scripts[int(script_idx) - 1])
            try:
                check_script(script_path)
                p = multiprocessing.Process(target=run_script, args=(script_path, pid))
                p.start()
                p.join(timeout=2)
                if p.is_alive():
                    p.terminate()
                    console.print(Panel("[red]Timeout : exécution trop longue[/red]"))
            except Exception as e:
                console.print(Panel(f"[red]Erreur : {str(e)}[/red]"))
                logger.error(encrypt_log(f"Erreur : {str(e)}"))
        elif choice == "4":
            console.print(Panel("[yellow]Arrêt[/yellow]"))
            break

if __name__ == "__main__":
    main()