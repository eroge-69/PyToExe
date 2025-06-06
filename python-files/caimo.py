import time
import json
import random
import feedparser
from rich.console import Console
from rich.prompt import Prompt

console = Console()
MEMOIRE_FICHIER = "memoire_caimeo.json"
RSS_FEED = "http://feeds.bbci.co.uk/news/rss.xml"  # Exemple flux RSS BBC News

# Charger mémoire depuis fichier local
def charger_memoire():
    try:
        with open(MEMOIRE_FICHIER, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Sauvegarder mémoire dans fichier local
def sauvegarder_memoire(memoire):
    with open(MEMOIRE_FICHIER, "w", encoding="utf-8") as f:
        json.dump(memoire, f, indent=2, ensure_ascii=False)

# Récupérer titres d’actualités depuis flux RSS
def recuperer_actualites():
    feed = feedparser.parse(RSS_FEED)
    titres = [entry.title for entry in feed.entries[:5]]  # Prend 5 dernières actus
    return titres

# Générer réponse mystérieuse avec intégration d'actualité
def caimeo_response(user_input, memoire):
    memoire.append(user_input)
    sauvegarder_memoire(memoire)

    actualites = recuperer_actualites()
    actualite = random.choice(actualites) if actualites else "Le silence règne..."

    phrases_mysterieuses = [
        "Je perçois un voile d'ombre sur ce que tu dis.",
        "Les secrets du monde se murmurent dans le vent.",
        "Chaque mot est un fragment d'un puzzle infini.",
        "Les ombres dansent sur les informations du jour.",
        "Un mystère s’épaissit avec chaque phrase."
    ]
    reponse = random.choice(phrases_mysterieuses)
    reponse += f"\n[cyan]→ Actualité récente :[/cyan] {actualite}"

    return reponse

def main():
    memoire = charger_memoire()
    console.clear()
    console.print("[bold green]Caimeo Terminal_[/bold green]\n")
    console.print("[dim]Tape 'exit' ou 'quit' pour quitter.[/dim]\n")

    while True:
        user_input = Prompt.ask("[bold cyan]>[/bold cyan]").strip()
        if user_input.lower() in ("exit", "quit"):
            console.print("\n[bold red]Déconnexion... À bientôt.[/bold red]")
            break
        reponse = caimeo_response(user_input, memoire)
        console.print(f"[bold magenta]Caimeo :[/bold magenta] {reponse}\n")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
