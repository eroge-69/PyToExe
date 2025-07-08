import time
from rich import print,inspect
from rich.table import Table
from rich.console import Console
from rich.progress import track


console = Console()
my_list=[1,2,3]
print("Hello, [bold magenta]World[/bold magenta]!", ":vampire:")
console.print("Hello", "World!", style="bold red")
console.print("Hi, boss!! i am here",":raccoon:")
console.print("Where there is a [bold cyan]Will[/bold cyan] there [u]is[/u] a [i]way[/i].")
inspect(my_list,methods=True)
table = Table(show_header=True, header_style="bold magenta")
table.add_column("Date", style="dim", width=12)
table.add_column("Title")
table.add_column("Production Budget", justify="right")
table.add_column("Box Office", justify="right")
table.add_row(
    "Dec 20, 2019", "Star Wars: The Rise of Skywalker", "$275,000,000", "$375,126,118"
)
table.add_row(
    "May 25, 2018",
    "[red]Solo[/red]: A Star Wars Story",
    "$275,000,000",
    "$393,151,347",
)
table.add_row(
    "Dec 15, 2017",
    "Star Wars Ep. VIII: The Last Jedi",
    "$262,000,000",
    "[bold]$1,332,539,889[/bold]",
)

console.print(table)
for step in track(range(100)):
    time.sleep(.2)
