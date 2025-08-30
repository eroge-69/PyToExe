import webbrowser
import time

# URL de la page web que vous voulez ouvrir
url = "https://stake.games/fr?tab=rewards&modal=claimReload"

# Intervalle de temps en secondes (10 minutes = 600 secondes)
interval = 635

# Boucle infinie pour ouvrir la page toutes les 10 minutes
while True:
    webbrowser.open(url)
    time.sleep(interval)
