# simple_steps_ui.py

from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

TARGET = "ILoveBSMCH"

def step_one(s):
    return s[::-1]

def step_two(s):
    return s[-1] + s[:-1]

def step_three(s):
    return s[1] + s[0] + s[2:]

def validate(user_input):
    if len(user_input) != 10:
        return False
    t1 = step_one(user_input)
    t2 = step_two(t1)
    t3 = step_three(t2)
    return t3 == TARGET

if __name__ == "__main__":
    console.print(Panel.fit("[bold cyan]🔍 Welcome to the BSMCH Challenge![/bold cyan]"))
    console.print("Your goal: find the [bold]magic word[/bold] that reveals your love for BSMCH.\n")

    try:
        user_input = Prompt.ask("[bold yellow]Enter the magic word[/bold yellow]")
    except EOFError:
        console.print("\n[bold red]⚠️ No input detected. Exiting.[/bold red]")
        exit(1)

    if validate(user_input):
        console.print("[bold green]✅ You really do love BSMCH!![/bold green]")
    else:
        console.print("[bold red]❌ Wrong! Try again.[/bold red]")
