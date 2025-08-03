import os
import datetime

FICHIER_MEMOIRE = "memoire.txt"
HEADER_MEMOIRE = "mektoub"  # Header ajouté au fichier mémoire
memoire = []

# Affichage du titre MEKTOUB au lancement
def afficher_titre():
    print("""
===========================
         MEKTOUB
===========================
DDDD   N   N    AAAAA     BBBBB   III  OOO    Bio script
  D   D  NN  N   A     A    B    B   I   O   O  
  D   D  N N N   AAAAAAA    BBBBB    I   O   O   
  D   D  N  NN   A     A    B    B   I   O   O     
  DDDD   N   N   A     A  O BBBBB   III  OOO        

dévelloper par own3, avant de l'utiliser, sachez que chaque lettre a une histoire/un cliché qui lui ait propre 
et sont tres symbolique, de part la forme des lettres.
Pour comprendre il suffit d'avoir juste un peu de jugeote et ce croire en agravité...

Les lettres sont comme des "Token", et traduise chacune une image, ou un phenomene. elles sont calculable et peuvent etre "Vectoriser" C.A.D :
Il vous faut choisir un "Modulo", il sert a admettre une base vectorielle de calcul, pour le classique ( A1 - Z26 ) cela seras 26 de base (les 26 lettres de l'alphabet qui seras = Z0ouZ26)
Ex : AY(1+25) = 26 = 0. Par contre AYA = 27 sous modulo 26 il donnerait 1A car = 27 etc... 30 sous modulo 26 serait = a 4D, par contre sous modulo 27, 30 = 3C et 30 = 24X + 6F = 3C. PIGE ! 
( Pour influencer sur une valeur, il suffit de choisir le "multiplicateur" voulu, en ce fiant au lexique du code juste en bas )
Exemple : ANGE Modulo_26(Les 26 lettres de l'alphabet en vecteur de calcul = 1 ) + Multiplicateur_23 ( SHEYTAN) donne o15 ( Sang ) 
	: CE qui fait ANGE = 4 = 27 lettres, et dans son sensemble avec un modulo 26 = A1, pour en revenir au Multiplicateur, ANGE x 23 = ANGE(1A)+(4x23)=15
															   ou ANGE x 23 = ANGE(27)Avec Modulo 27 x(SHEYTAN) = 14N

En temp normal, de simple lettres avec des valeurs numérique ne veulent rien dire, ici je vous prouve le contraire.
===================================================================================================================================


Voici un tableau recensant Lettres, Valeurs numérique, et mot clef en "MAJUSCULE", Je rappel que le modulo est sur une base 26.
--------------------------------------------------------------------------------------------------------------------------------------
A=1= Regard, Musique, Sexe, Ange, Aile, Code, Ombre, Amalgame, Valeur, Rêve,démon   					1A = [EXACT]
B=2= Atome, Aime, Programme, Nouvelle, Bourse, Mémoire.									2B = [AIR]    				
C=3= Sublime, Système, envie	  											3C = [BEAU]
D=4= Surface, Noir.													4D = [MIROIR]
E=5= Phare, Bonheur, Tendresse, Lumiere, Archange, Vénus, Célérité, Guêpe, Charmante, Mathématique, vérité,Masse	5E = [HARMONIE]
F=6= Feu, Gravité, Blanc, Hazard, Viol, Alcool.										6F = [CHAOS]  
G=7= Or, Original, Diable, Violence, Illusion, scandale									7G = [DEESSE] 
H=8= Logique, Allah, Respect, Peur, Subliminal, Futur. 									8H = [CONSCIENCE]
I=9= Mort, Image.													9I = [MEMORIA]
J=10= Vie, Racolage, Pute, Poison, Passé.					               				10J = [IMPACT]
K=11= Energie, Cannabis, Nicotine, Odeur, Flux, Capter, Haine, Virginité, embellir 	       				11K = [JOULE - KANALISER]
L=12= Onde, Thermique, Jour, Nuit, Morale, oublie				               				12L = [ALPHA - POUVOIR]
M=13= Naturel, Fierté, Triste, Mélodie, Argent.visage, miel								13M = [JOIE]
N=14= Bleu, Rouge, Inverse, Artiste, Moteur, Trader.					       				14N = [DYNAMIQUE] 
O=15= Sang, Péché, Sentiment, émotion, Aura.  						       				15O = [PASSION]
P=16= Paradis, Femme, Amour, Physique, Verre, Roi, électron, cliché	                       				16P = [REPONSE]
Q=17= Lionne, Attraction, Abus, juge							       				17Q = [DOMINATION - JEUX DE GRAND ;) ]
R=18= Dignité, Frelon, Essence, Cancer.  						       				18R = [RÉSILIENCE]
S=19= Corde, Vin, Souvenir, Maladie, serpent  						       				19S = [FUSIONELLE]
T=20= Matière, Symphonie, Abyme, Abeille.					       		        		20T = [FLASH]
U=21= Chimie, Consommation, Union, inconscient, Présent, muscle  			       				21U = [RETENTION]
V=22= Basique, Acide, Guerre, Brutal, Point, Son, Charme, Névrose, Dualité, Réalité.	       				22V = [VECTEUR]    
W=23= Inceste, Phase, Peine.								       				23W = [SHEYTAN]
X=24= Soleïl, Interaction, Vrai, Lion, Flamme, Paix, Vengeance, Raison, Cosmique.		  			24X = [PUISSANCE]
Y=25= Reine, Origine, Agonie, pleure, mystique		                               	         			25Y = [ARCHETYPE]   
Z=26= Faux, 0, Laid, Jessy.								       				26Z = [NUL0]
""")

# --------------------------
# Gestion de la mémoire
# --------------------------

def charger_memoire():
    """Charge la mémoire depuis le fichier"""
    memoire.clear()
    if not os.path.isfile(FICHIER_MEMOIRE):
        return
    with open(FICHIER_MEMOIRE, "r", encoding="utf-8") as f:
        lignes = f.readlines()
        if not lignes:
            return
        # Vérifier si le header est présent et l'ignorer
        if lignes[0].strip() == HEADER_MEMOIRE:
            lignes = lignes[1:]
        for ligne in lignes:
            ligne = ligne.strip()
            if not ligne:
                continue
            try:
                entree, val_str, date_str = ligne.split("||")
                val = int(val_str)
                memoire.append((entree, val, date_str))
            except ValueError:
                print(f"[!] Ligne corrompue ignorée : {ligne}")

def sauvegarder_memoire():
    """Sauvegarde la mémoire sur disque avec header"""
    with open(FICHIER_MEMOIRE, "w", encoding="utf-8") as f:
        f.write(HEADER_MEMOIRE + "\n")  # écriture du header
        for entree, val, date_str in memoire:
            f.write(f"{entree}||{val}||{date_str}\n")

def ajouter_memoire(entree, valeur):
    """Ajoute une valeur à la mémoire avec horodatage"""
    horodatage = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    memoire.append((entree, valeur, horodatage))
    sauvegarder_memoire()

def afficher_memoire():
    """Affiche la mémoire"""
    if not memoire:
        print("Mémoire vide.")
        return
    print("\n--- Contenu de la mémoire ---")
    for i, (entree, valeur, date_str) in enumerate(memoire):
        print(f"{i:02d} : {entree} = {valeur}  ({date_str})")

def supprimer_memoire():
    """Permet de supprimer un élément de la mémoire"""
    afficher_memoire()
    if not memoire:
        return
    choix = input("Indice à supprimer (R pour retour) : ").strip().lower()
    if choix == "r":
        return
    try:
        idx = int(choix)
        if 0 <= idx < len(memoire):
            memoire.pop(idx)
            sauvegarder_memoire()
            print("Élément supprimé avec succès.")
        else:
            print("Indice invalide.")
    except ValueError:
        print("Entrée invalide.")

# --------------------------
# Conversion et calculs
# --------------------------

def lettre_en_chiffre_detail(texte):
    """Convertit un mot en valeur numérique et affiche le détail"""
    texte = texte.upper()
    total = 0
    details = []
    for lettre in texte:
        if lettre.isalpha():
            valeur = ord(lettre) - 64
            details.append(f"{lettre}({valeur})")
            total += valeur
    print(" + ".join(details) + f" = {total}")
    return total

def chiffre_en_lettres(nombre):
    """Convertit un nombre en notation alphabétique (style Excel)"""
    if nombre <= 0:
        return ""
    lettres = ""
    while nombre > 0:
        nombre -= 1
        lettres = chr((nombre % 26) + 65) + lettres
        nombre //= 26
    return lettres

def appliquer_modulo(valeur):
    choix = input("Appliquer un modulo ? (O/N) : ").strip().lower()
    if choix == "o":
        while True:
            try:
                modulo = int(input("Modulo choisi (nombre entier > 0) : "))
                if modulo > 0:
                    valeur_mod = valeur % modulo
                    print(f"Valeur après modulo {modulo} : {valeur_mod}")
                    return valeur_mod
                else:
                    print("Veuillez entrer un entier strictement positif.")
            except ValueError:
                print("Entrée invalide.")
    return valeur

def afficher_resultat(valeur):
    choix = input("Afficher en lettres (L) ou en chiffres (C) ? (L/C) : ").strip().lower()
    if choix == "l":
        print("Résultat en lettres :", chiffre_en_lettres(valeur))
    else:
        print("Résultat en chiffres :", valeur)

def convertir_texte_ou_nombre(texte):
    """Convertit une entrée en nombre (soit c'est un entier, soit calcul de lettres)"""
    try:
        return int(texte)
    except ValueError:
        return lettre_en_chiffre_detail(texte)

def demander_texte(prompt):
    texte = input(prompt).strip()
    if texte.lower() == "r":
        return None
    return texte

def traiter_operation(entree1, entree2, operation):
    val1 = convertir_texte_ou_nombre(entree1)
    val2 = convertir_texte_ou_nombre(entree2) if entree2 is not None else None

    if operation == "+":
        res = val1 + val2
        print(f"{val1} + {val2} = {res}")
    elif operation == "-":
        res = val1 - val2
        print(f"{val1} - {val2} = {res}")
    elif operation == "*":
        res = val1 * val2
        print(f"{val1} * {val2} = {res}")
    elif operation == "²":
        res = val1 * val1
        print(f"{val1}² = {res}")
    else:
        print("Opération inconnue.")
        return

    res = appliquer_modulo(res)
    afficher_resultat(res)
    ajouter_memoire(f"{entree1} {operation} {entree2 if entree2 is not None else ''}".strip(), res)

def menu():
    afficher_titre()
    charger_memoire()
    while True:
        print("\nMenu principal :")
        print("1 : Conversion lettres -> chiffres")
        print("2 : Multiplication")
        print("3 : Carré")
        print("4 : Addition ou soustraction")
        print("5 : Mémoire dynamique")
        print("6 : Quitter")
        choix = input("Votre choix : ").strip()
        if choix == "1":
            texte = demander_texte("Mot à convertir (R pour retour) : ")
            if texte is None:
                continue
            val = lettre_en_chiffre_detail(texte)
            val = appliquer_modulo(val)
            afficher_resultat(val)
            ajouter_memoire(texte, val)

        elif choix == "2":
            e1 = demander_texte("Multiplicande (R pour retour) : ")
            if e1 is None:
                continue
            e2 = demander_texte("Multiplicateur (R pour retour) : ")
            if e2 is None:
                continue
            traiter_operation(e1, e2, "*")

        elif choix == "3":
            e1 = demander_texte("Nombre à mettre au carré (R pour retour) : ")
            if e1 is None:
                continue
            traiter_operation(e1, None, "²")

        elif choix == "4":
            e1 = demander_texte("Premier terme (R pour retour) : ")
            if e1 is None:
                continue
            op = input("Opération (+ ou -) : ").strip()
            if op not in ("+", "-"):
                print("Opération non reconnue.")
                continue
            e2 = demander_texte("Deuxième terme (R pour retour) : ")
            if e2 is None:
                continue
            traiter_operation(e1, e2, op)

        elif choix == "5":
            while True:
                print("\n--- Mémoire dynamique ---")
                print("A : Afficher la mémoire")
                print("S : Supprimer une entrée")
                print("O : Opération entre deux entrées")
                print("T : Trier la mémoire par valeur")
                print("R : Retour au menu principal")
                choix_memoire = input("Votre choix : ").strip().lower()
                if choix_memoire == "a":
                    afficher_memoire()
                elif choix_memoire == "s":
                    supprimer_memoire()
                elif choix_memoire == "o":
                    afficher_memoire()
                    if len(memoire) < 2:
                        print("Pas assez d'éléments pour faire une opération.")
                        continue
                    try:
                        i1 = int(input("Indice premier élément : "))
                        i2 = int(input("Indice deuxième élément : "))
                        if 0 <= i1 < len(memoire) and 0 <= i2 < len(memoire):
                            op = input("Opération (+, -, *, ²) : ").strip()
                            if op == "²":
                                traiter_operation(memoire[i1][0], None, op)
                            else:
                                traiter_operation(memoire[i1][0], memoire[i2][0], op)
                        else:
                            print("Indices invalides.")
                    except ValueError:
                        print("Entrée invalide.")
                elif choix_memoire == "t":
                    memoire.sort(key=lambda x: x[1])
                    print("Mémoire triée par valeur (croissante).")
                    afficher_memoire()
                elif choix_memoire == "r":
                    break
                else:
                    print("Choix non reconnu.")

        elif choix == "6":
            print("Au revoir.")
            break
        else:
            print("Choix non valide.")

if __name__ == "__main__":
    menu()
