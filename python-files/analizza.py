import json
import sys
import os
from rich import print
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm

console = Console()


def get_path(filename):
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.dirname(__file__), filename)

with open(get_path('result.json'), 'r', encoding='utf-8') as file:
    dati = json.load(file)

lista_campionati = list(dati.keys())

def prendi_over(campionato, soglia):
    terreno = "sconosciuto"

    for anno, match_ in dati[campionato].items():
        res = {}
        over_totali = 0
        
        if anno == "terreno":
            terreno = match_
            continue

        for match in match_:
            fase_girone = match["fase_girone"]
            numero_game = sum(int(ch) for ch in match["risultato"] if ch.isdigit())
            
            if fase_girone not in res:
                res[fase_girone] = 0

            if numero_game > soglia:
                res[fase_girone] += 1
                over_totali += 1

        console.print(f"TOTALE OVER [green]{anno}[/green]: {over_totali}")
        
        for girone, numero_over in res.items():
            console.print(f"[bold yellow]{girone}[/bold yellow]: {numero_over} over")
            
        console.print("")
    
# Titolo iniziale
console.clear()
console.print(Panel("[bold cyan]Analizzatore Statistiche Tennis[/bold cyan]", expand=False))

continua = True

while continua:
    # Input soglia over
    while True:
        input_str = Prompt.ask("Inserisci la soglia per il calcolo degli over (es: 19.5)")
        try:
            soglia_over = float(input_str)
            if soglia_over * 10 % 10 == 5:
                break
            else:
                console.print("[red]Il numero deve terminare con .5[/red]")
        except ValueError:
            console.print("[red]Inserisci un numero valido (es: 19.5)[/red]")


    # Menu selezione campionato
    console.print("\n[bold]Campionati disponibili:[/bold]")
    for i, campionato in enumerate(lista_campionati, start=1):
        console.print(f"[green]{i}[/green]. {campionato}")

    indice = IntPrompt.ask("Seleziona il numero del campionato", choices=[str(i) for i in range(1, len(lista_campionati)+1)])
    campionato_selezionato = lista_campionati[indice - 1]

    # ESEGUI ANALISI QUI
    console.print(f"\n[bold yellow]Analizzando[/bold yellow] [cyan]{campionato_selezionato}[/cyan] con soglia [green]{soglia_over}[/green]...\n")
    
    prendi_over(campionato_selezionato, soglia_over)

    # Continua?
    continua = Confirm.ask("Vuoi avviare una nuova ricerca?")




            
    
