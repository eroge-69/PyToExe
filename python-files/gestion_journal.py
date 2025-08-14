import os
import subprocess
import tempfile
import re
from datetime import datetime
from colorama import Fore, Style, init
from prompt_toolkit import prompt
from prompt_toolkit.shortcuts import prompt as prompt_dialog
from prompt_toolkit.shortcuts import message_dialog
from prompt_toolkit.validation import Validator, ValidationError

# Initialise Colorama pour que les couleurs fonctionnent sur tous les terminaux
init(autoreset=True)

# --- Définir le répertoire de travail au début du programme ---
# Récupère le chemin absolu du répertoire où se trouve le script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Change le répertoire de travail pour ce dossier
os.chdir(script_dir)

# --- Fonctions utilitaires ---

def clear_screen():
    """Efface l'écran du terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def afficher_menu_principal():
    """Affiche le menu principal du programme."""
    clear_screen()
    print(f"\n{Fore.RED}--- Journal de Bord Cyberpunk Red ---{Style.RESET_ALL}")
    print(f"{Fore.CYAN}1.{Style.RESET_ALL} Créer un nouveau journal")
    print(f"{Fore.CYAN}2.{Style.RESET_ALL} Ouvrir un journal existant")
    print(f"{Fore.CYAN}3.{Style.RESET_ALL} Quitter")

def afficher_menu_journal(nom_fichier):
    """Affiche le menu pour gérer un journal spécifique."""
    clear_screen()
    print(f"\n{Fore.RED}--- Vous gérez le journal : {Fore.MAGENTA}{nom_fichier}{Fore.RED} ---{Style.RESET_ALL}")
    print(f"{Fore.CYAN}1.{Style.RESET_ALL} Ajouter un nouvel Arc")
    print(f"{Fore.CYAN}2.{Style.RESET_ALL} Ajouter une nouvelle Scène")
    print(f"{Fore.CYAN}3.{Style.RESET_ALL} Afficher le contenu du journal")
    print(f"{Fore.CYAN}4.{Style.RESET_ALL} Générer un PDF")
    print(f"{Fore.CYAN}5.{Style.RESET_ALL} Outils d'édition avancée")
    print(f"{Fore.CYAN}6.{Style.RESET_ALL} Retour au menu principal")

def afficher_menu_edition(nom_fichier):
    """Affiche le menu d'édition pour le journal."""
    clear_screen()
    print(f"\n{Fore.RED}--- Outils d'édition pour : {Fore.MAGENTA}{nom_fichier}{Fore.RED} ---{Style.RESET_ALL}")
    print(f"{Fore.CYAN}1.{Style.RESET_ALL} Modifier le titre du fichier")
    print(f"{Fore.CYAN}2.{Style.RESET_ALL} Modifier un Arc (titre)")
    print(f"{Fore.CYAN}3.{Style.RESET_ALL} Modifier une Scène (titre ou contenu)")
    print(f"{Fore.CYAN}4.{Style.RESET_ALL} Retirer un Arc complet")
    print(f"{Fore.CYAN}5.{Style.RESET_ALL} Retirer une Scène")
    print(f"{Fore.CYAN}6.{Style.RESET_ALL} Réinitialiser le journal (supprimer tout le contenu)")
    print(f"{Fore.CYAN}7.{Style.RESET_ALL} Retour à la gestion du journal")

def ecrire_texte(texte_initial=""):
    """
    Permet à l'utilisateur d'écrire un bloc de texte.
    Les instructions expliquent comment gérer les sauts de ligne en Markdown.
    """
    print(f"{Fore.YELLOW}Éditeur de texte - Mode Markdown.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  - Pour un saut de ligne forcé, ajoutez deux espaces à la fin de la ligne.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  - Pour un nouveau paragraphe, laissez une ligne vide.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}  - Pour valider, appuyez sur ESC puis Entrée (ou Alt+Entrée sur Windows).{Style.RESET_ALL}")
    
    # Utilise prompt_toolkit pour une saisie de texte sur plusieurs lignes
    saisie = prompt_dialog("> ", multiline=True, default=texte_initial)
    
    return saisie

# --- Fonctions de gestion des fichiers ---

def creer_journal():
    """Crée un nouveau fichier journal Markdown."""
    clear_screen()
    nom_fichier = input(f"{Fore.CYAN}Nom du nouveau journal : {Style.RESET_ALL}")
    nom_fichier_complet = f"{nom_fichier}.md"
    
    if os.path.exists(nom_fichier_complet):
        print(f"{Fore.YELLOW}Le fichier '{nom_fichier_complet}' existe déjà. Retour au menu.{Style.RESET_ALL}")
        input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        return

    try:
        with open(nom_fichier_complet, 'w', encoding='utf-8') as f:
            f.write(f"# Journal de bord : {nom_fichier}\n\n")
        print(f"{Fore.GREEN}Le journal '{nom_fichier_complet}' a été créé avec succès. Bienvenue dans Night City !{Style.RESET_ALL}")
        input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        gerer_journal(nom_fichier_complet)
    except IOError as e:
        print(f"{Fore.RED}Erreur lors de la création du fichier : {e}{Style.RESET_ALL}")
        input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")

def ouvrir_journal():
    """Affiche la liste des journaux existants et permet d'en choisir un."""
    clear_screen()
    fichiers = [f for f in os.listdir('.') if f.endswith('.md')]
    if not fichiers:
        print(f"{Fore.YELLOW}Aucun journal trouvé. Veuillez en créer un d'abord.{Style.RESET_ALL}")
        input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        return
    
    print(f"\n{Fore.MAGENTA}Journaux disponibles : {Style.RESET_ALL}")
    for i, f in enumerate(fichiers, 1):
        print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {f}")
    
    try:
        choix = int(input(f"{Fore.CYAN}Sélectionnez un journal (numéro) : {Style.RESET_ALL}"))
        if 1 <= choix <= len(fichiers):
            nom_fichier = fichiers[choix - 1]
            gerer_journal(nom_fichier)
        else:
            print(f"{Fore.YELLOW}Numéro invalide.{Style.RESET_ALL}")
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
    except ValueError:
        print(f"{Fore.YELLOW}Veuillez entrer un nombre.{Style.RESET_ALL}")
        input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")

# --- Fonctions d'édition ---

def reinitialiser_journal(nom_fichier):
    """Efface tout le contenu d'un fichier journal sauf le titre initial."""
    clear_screen()
    confirmation = input(f"{Fore.RED}ATTENTION : Cette action va supprimer TOUT le contenu du journal '{nom_fichier}'. Confirmez-vous ? (oui/non) : {Style.RESET_ALL}")
    if confirmation.lower() == "oui":
        try:
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                nom_base = os.path.splitext(nom_fichier)[0]
                f.write(f"# Journal de bord : {nom_base}\n\n")
            print(f"{Fore.GREEN}Le journal '{nom_fichier}' a été réinitialisé avec succès.{Style.RESET_ALL}")
        except IOError as e:
            print(f"{Fore.RED}Erreur lors de la réinitialisation du fichier : {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}Réinitialisation annulée.{Style.RESET_ALL}")


def modifier_titre_fichier(nom_fichier_actuel):
    """Permet de renommer le fichier journal et son titre interne."""
    clear_screen()
    nouveau_nom = input(f"{Fore.CYAN}Entrez le nouveau nom pour le journal (sans extension) : {Style.RESET_ALL}")
    if not nouveau_nom:
        print(f"{Fore.YELLOW}Opération annulée.{Style.RESET_ALL}")
        return nom_fichier_actuel

    nouveau_nom_complet = f"{nouveau_nom}.md"
    try:
        os.rename(nom_fichier_actuel, nouveau_nom_complet)
        
        with open(nouveau_nom_complet, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        contenu_modifie = re.sub(r'# Journal de bord : .*\n', f'# Journal de bord : {nouveau_nom}\n', contenu, 1)
        
        with open(nouveau_nom_complet, 'w', encoding='utf-8') as f:
            f.write(contenu_modifie)
            
        print(f"{Fore.GREEN}Le journal a été renommé en '{nouveau_nom_complet}' avec succès !{Style.RESET_ALL}")
        return nouveau_nom_complet
    except OSError as e:
        print(f"{Fore.RED}Erreur lors du renommage du fichier : {e}{Style.RESET_ALL}")
        return nom_fichier_actuel

def modifier_entite(nom_fichier, type_entite, entite_regex, titre_regex):
    """Fonction générique pour modifier un titre d'entité (Arc ou Scène)."""
    clear_screen()
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        entites = re.findall(entite_regex, contenu, re.DOTALL)
        if not entites:
            print(f"{Fore.YELLOW}Aucun(e) {type_entite} trouvé(e) dans le journal.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.MAGENTA}Liste des {type_entite}s disponibles : {Style.RESET_ALL}")
        for i, entite in enumerate(entites, 1):
            titre = re.search(titre_regex, entite)
            if titre:
                print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {titre.group(1).strip()}")
        
        choix = int(input(f"{Fore.CYAN}Sélectionnez le/la {type_entite} à modifier (numéro) : {Style.RESET_ALL}"))
        if 1 <= choix <= len(entites):
            entite_a_modifier = entites[choix - 1]
            nouveau_titre = input(f"{Fore.CYAN}Entrez le nouveau titre pour le/la {type_entite} : {Style.RESET_ALL}")
            
            titre_original = re.search(titre_regex, entite_a_modifier).group(1)
            entite_modifiee = entite_a_modifier.replace(titre_original, nouveau_titre)
            
            contenu_modifie = contenu.replace(entite_a_modifier, entite_modifiee)
            
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                f.write(contenu_modifie)
            print(f"{Fore.GREEN}{type_entite} modifié(e) avec succès !{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Numéro invalide.{Style.RESET_ALL}")
    except (IOError, ValueError, IndexError) as e:
        print(f"{Fore.RED}Erreur lors de la modification de l'entité : {e}{Style.RESET_ALL}")
        
def modifier_scene(nom_fichier):
    """Permet de modifier le titre ou le contenu d'une scène."""
    clear_screen()
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            contenu = f.read()

        scenes = re.findall(r'(### \[.*?\] – .*?(?=\n\n###|## Arc|# Journal de bord|\Z))', contenu, re.DOTALL)
        if not scenes:
            print(f"{Fore.YELLOW}Aucune scène trouvée dans le journal.{Style.RESET_ALL}")
            return

        print(f"\n{Fore.MAGENTA}Liste des scènes disponibles : {Style.RESET_ALL}")
        for i, scene in enumerate(scenes, 1):
            titre_scene = scene.split('\n')[0].strip(' #')
            print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {titre_scene}")

        choix = int(input(f"{Fore.CYAN}Sélectionnez la scène à modifier (numéro) : {Style.RESET_ALL}"))
        if 1 <= choix <= len(scenes):
            scene_a_modifier = scenes[choix - 1]
            titre_actuel_scene = scene_a_modifier.split('\n')[0].strip(' #')
            
            print(f"\n{Fore.MAGENTA}Vous avez choisi la scène : {titre_actuel_scene}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}1.{Style.RESET_ALL} Modifier le titre de la scène (date, heure, lieu)")
            print(f"{Fore.CYAN}2.{Style.RESET_ALL} Modifier le contenu de la scène")
            choix_modification = input(f"{Fore.CYAN}Votre choix : {Style.RESET_ALL}")
            
            if choix_modification == "1":
                nouvelle_date = input(f"{Fore.YELLOW}Nouvelle date (ex: 13/08/2045) : {Style.RESET_ALL}")
                nouvelle_heure = input(f"{Fore.YELLOW}Nouvelle heure (ex: 09h42) : {Style.RESET_ALL}")
                nouveau_lieu = input(f"{Fore.YELLOW}Nouveau lieu : {Style.RESET_ALL}")
                nouveau_titre = f"### [{nouvelle_date} – {nouvelle_heure}] – {nouveau_lieu}"
                
                scene_modifiee = scene_a_modifier.replace(scene_a_modifier.split('\n')[0], nouveau_titre, 1)
                
            elif choix_modification == "2":
                print(f"{Fore.MAGENTA}Contenu actuel de la scène : {Style.RESET_ALL}")
                contenu_initial = scene_a_modifier.split('\n', 1)[1].strip()
                nouveau_contenu = ecrire_texte(contenu_initial)
                
                titre_scene = scene_a_modifier.split('\n', 1)[0]
                nouveau_bloc_scene = f"{titre_scene}\n\n{nouveau_contenu}"
                scene_modifiee = scene_a_modifier.replace(scene_a_modifier, nouveau_bloc_scene)
                
            else:
                print(f"{Fore.YELLOW}Choix invalide.{Style.RESET_ALL}")
                return

            contenu_modifie = contenu.replace(scene_a_modifier, scene_modifiee)
            
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                f.write(contenu_modifie)
            print(f"{Fore.GREEN}Scène modifiée avec succès !{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Numéro invalide.{Style.RESET_ALL}")
            
    except (IOError, ValueError, IndexError) as e:
        print(f"{Fore.RED}Erreur lors de la modification de la scène : {e}{Style.RESET_ALL}")
        
def retirer_entite(nom_fichier, type_entite, entite_regex):
    """Fonction générique pour retirer une entité (Arc ou Scène)."""
    clear_screen()
    try:
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        entites = re.findall(entite_regex, contenu, re.DOTALL)
        if not entites:
            print(f"{Fore.YELLOW}Aucun(e) {type_entite} trouvé(e) dans le journal.{Style.RESET_ALL}")
            return
        
        print(f"\n{Fore.MAGENTA}Liste des {type_entite}s disponibles : {Style.RESET_ALL}")
        for i, entite in enumerate(entites, 1):
            titre = entite.split('\n')[0].strip(' #')
            print(f"{Fore.CYAN}{i}.{Style.RESET_ALL} {titre}")
            
        choix = int(input(f"{Fore.CYAN}Sélectionnez le/la {type_entite} à retirer (numéro) : {Style.RESET_ALL}"))
        if 1 <= choix <= len(entites):
            entite_a_retirer = entites[choix - 1]
            contenu_modifie = contenu.replace(entite_a_retirer, '').strip()
            
            with open(nom_fichier, 'w', encoding='utf-8') as f:
                f.write(contenu_modifie)
            print(f"{Fore.GREEN}{type_entite} retiré(e) avec succès !{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Numéro invalide.{Style.RESET_ALL}")
    except (IOError, ValueError, IndexError) as e:
        print(f"{Fore.RED}Erreur lors du retrait de l'entité : {e}{Style.RESET_ALL}")
        
# --- Boucle principale pour la gestion d'un journal ouvert ---

def gerer_journal(nom_fichier):
    """Boucle principale pour la gestion d'un journal ouvert."""
    while True:
        afficher_menu_journal(nom_fichier)
        choix_gestion = input(f"{Fore.CYAN}Votre choix : {Style.RESET_ALL}")

        if choix_gestion == "1":
            clear_screen()
            titre_arc = input(f"{Fore.YELLOW}Titre du nouvel Arc : {Style.RESET_ALL}")
            with open(nom_fichier, 'a', encoding='utf-8') as f:
                f.write(f"\n---\n\n## Arc : {titre_arc}\n\n")
            print(f"{Fore.GREEN}Nouvel Arc ajouté.{Style.RESET_ALL}")
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        
        elif choix_gestion == "2":
            clear_screen()
            date_str = input(f"{Fore.YELLOW}Date de la scène (ex: 13/08/2045) : {Style.RESET_ALL}")
            heure_str = input(f"{Fore.YELLOW}Heure de la scène (ex: 09h42) : {Style.RESET_ALL}")
            lieu = input(f"{Fore.YELLOW}Lieu (ex: Penthouse, Centre-ville) : {Style.RESET_ALL}")
            
            entete = f"### [{date_str} – {heure_str}] – {lieu}\n\n"
            
            texte_scene = ecrire_texte()
            
            with open(nom_fichier, 'a', encoding='utf-8') as f:
                f.write(f"\n\n{entete}{texte_scene}")
            print(f"{Fore.GREEN}Nouvelle scène ajoutée.{Style.RESET_ALL}")
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
            
        elif choix_gestion == "3":
            clear_screen()
            try:
                with open(nom_fichier, 'r', encoding='utf-8') as f:
                    print(f"\n{Fore.MAGENTA}--- Contenu du journal ---{Style.RESET_ALL}")
                    print(f.read())
                    print(f"{Fore.MAGENTA}--------------------------{Style.RESET_ALL}")
            except IOError as e:
                print(f"{Fore.RED}Erreur lors de la lecture du fichier : {e}{Style.RESET_ALL}")
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        
        elif choix_gestion == "4":
            clear_screen()
            generer_pdf(nom_fichier)
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        
        elif choix_gestion == "5":
            nom_fichier = gerer_edition(nom_fichier)

        elif choix_gestion == "6":
            break
        
        else:
            print(f"{Fore.YELLOW}Choix invalide. Veuillez réessayer.{Style.RESET_ALL}")
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")

def gerer_edition(nom_fichier):
    """Boucle de gestion pour le menu d'édition."""
    while True:
        afficher_menu_edition(nom_fichier)
        choix_edition = input(f"{Fore.CYAN}Votre choix : {Style.RESET_ALL}")
        
        if choix_edition == "1":
            nom_fichier = modifier_titre_fichier(nom_fichier)
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        elif choix_edition == "2":
            arc_entite_regex = r'(## Arc : .*?(?=\n\n---|\n\n## Arc|\Z))'
            arc_titre_regex = r'## Arc : (.*)'
            modifier_entite(nom_fichier, "Arc", arc_entite_regex, arc_titre_regex)
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        elif choix_edition == "3":
            modifier_scene(nom_fichier)
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        elif choix_edition == "4":
            arc_retirer_regex = r'(\n---\n\n## Arc : .*?(?=\n\n---|\n\n## Arc|\Z))'
            retirer_entite(nom_fichier, "Arc", arc_retirer_regex)
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        elif choix_edition == "5":
            scene_retirer_regex = r'(\n\n### \[.*?\] – .*?(?=\n\n###|\n\n---\n|## Arc|\Z))'
            retirer_entite(nom_fichier, "Scène", scene_retirer_regex)
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        elif choix_edition == "6":
            reinitialiser_journal(nom_fichier)
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
        elif choix_edition == "7":
            break
        else:
            print(f"{Fore.YELLOW}Choix invalide. Veuillez réessayer.{Style.RESET_ALL}")
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")
    return nom_fichier

# --- Fonction de génération de PDF avec template intégré ---

def generer_pdf(nom_fichier):
    """
    Génère un PDF à partir du fichier Markdown en utilisant Pandoc.
    Le template LaTeX est intégré dans le code pour éviter les dépendances externes.
    """
    latex_template_content = r"""
\documentclass[12pt, a4paper]{article}

% --- Paramètres de base ---
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage[left=2cm, right=2cm, top=2.5cm, bottom=2.5cm]{geometry}
\usepackage{xcolor}
\usepackage{hyperref}

% --- Couleurs inspirées de Cyberpunk ---
\definecolor{cyberRed}{RGB}{255, 0, 85}
\definecolor{cyberBlack}{RGB}{20, 20, 20}
\definecolor{cyberGrey}{RGB}{150, 150, 150}

% --- Mise en page et style ---
\pagestyle{plain}
\renewcommand{\familydefault}{\sfdefault} % Police sans-serif (comme 'Arial')
\setlength{\parindent}{0pt} % Retirer l'indentation
\setlength{\parskip}{1em} % Espacer les paragraphes
\hypersetup{colorlinks=true, linkcolor=cyberRed}

% --- Titres des Arcs et Scènes ---
\usepackage{titlesec}
\titleformat{\section}[block]{\Huge\bfseries\color{cyberRed}}{}{0pt}{}
\titlespacing*{\section}{0pt}{2em}{1em}
\titleformat{\subsection}[hang]{\Large\bfseries\color{cyberGrey}}{}{0pt}{}
\titlespacing*{\subsection}{0pt}{1.5em}{1em}

% --- Début du document ---
\begin{document}

% Corps du document, rempli par Pandoc
$body$

\end{document}
"""

    nom_pdf = nom_fichier.replace('.md', '.pdf')
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.tex', encoding='utf-8') as temp_template_file:
            temp_template_file.write(latex_template_content)
            temp_template_path = temp_template_file.name
        
        commande = [
            "pandoc",
            nom_fichier,
            "-o", nom_pdf,
            "--template", temp_template_path,
            "--pdf-engine=pdflatex"
        ]
        
        print(f"\n{Fore.MAGENTA}Génération du PDF '{nom_pdf}' en cours...{Style.RESET_ALL}")
        
        subprocess.run(commande, check=True, capture_output=True, text=True)
        print(f"{Fore.GREEN}✅ PDF généré avec succès ! Fichier disponible : {nom_pdf}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}\n[⚠️ ERREUR] : Pandoc ou le moteur LaTeX (pdflatex) n'est pas installé ou introuvable.{Style.RESET_ALL}")
        print(f"{Fore.RED}Veuillez vous assurer que ces deux programmes sont installés et accessibles dans le PATH de votre système.{Style.RESET_ALL}")
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}\n[⚠️ ERREUR] : Une erreur est survenue lors de la génération du PDF.{Style.RESET_ALL}")
        print(f"{Fore.RED}Détails de l'erreur Pandoc :\n{e.stderr}{Style.RESET_ALL}")
    finally:
        if 'temp_template_path' in locals() and os.path.exists(temp_template_path):
            os.remove(temp_template_path)

# --- Boucle principale du programme ---

def main():
    """Point d'entrée principal du programme."""
    while True:
        afficher_menu_principal()
        choix = input(f"{Fore.CYAN}Votre choix : {Style.RESET_ALL}")
        
        if choix == "1":
            creer_journal()
        elif choix == "2":
            ouvrir_journal()
        elif choix == "3":
            print(f"{Fore.GREEN}Merci d'avoir utilisé le journal. Au revoir !{Style.RESET_ALL}")
            break
        else:
            print(f"{Fore.YELLOW}Choix invalide. Veuillez réessayer.{Style.RESET_ALL}")
            input(f"{Fore.MAGENTA}Appuyez sur Entrée pour continuer...{Style.RESET_ALL}")

if __name__ == "__main__":
    main()