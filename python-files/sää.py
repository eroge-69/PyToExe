import requests
from rich.console import Console
from rich.table import Table

console = Console()

kaupungit = ["Äänekoski","Helsinki","Jyväskylä","Tikkakoski"]
table = Table(title="Ja Sää", style="cyan")
table.add_column("Kaupunki", justify="center")
table.add_column("Lämpötila (Celsius)", justify="center")
for kaupunki in kaupungit:
    
    lampo = requests.get(f"http://wttr.in/{kaupunki}?m&format=%t").text ### f poistaa {} merkit ja antaa "kaupunki" sisällön
    
    table.add_row(kaupunki, lampo)

console.print(table)