# Installer le module Selenium avant tout :
# commande : Install-Module -Name Selenium -Scope CurrentUser



from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Chemin vers votre fichier contenant les liens
fichier_liens = r'C:\My Program Files\Test Click Chrome.txt'

# Initialiser le navigateur Edge
driver = webdriver.Edge()  # Si le driver est dans le PATH
# Si le driver n'est pas dans le PATH, indiquez le chemin complet :
# driver = webdriver.Edge(executable_path=r'chemin\vers\msedgedriver.exe')

# Lire tous les liens depuis le fichier
with open(fichier_liens, 'r') as fichier:
    liens = [ligne.strip() for ligne in fichier if ligne.strip()]

# Parcourir chaque lien
for lien in liens:
    driver.get(lien)
    time.sleep(3)  # Attendre que la page se charge
    
    try:
        # Trouver le bouton par son ID
        bouton = driver.find_element(By.ID, "9136348254313162615")
        bouton.click()
        print(f"Cliqué sur le bouton pour {lien}")
    except Exception as e:
        print(f"Erreur pour {lien} : {e}")
    
    time.sleep(2)

# Fermer le navigateur
driver.quit()