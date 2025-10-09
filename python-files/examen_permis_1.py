import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class ApplicationPermis(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Examen Blanc - Permis de Conduire Belge")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # Configuration des styles
        self.configurer_styles()
        
        # Variables
        self.questions = self.charger_questions()
        self.themes = {
            "all": "Tous les thèmes",
            "cyclistes": "Les Cyclistes", 
            "bandes": "Les Bandes de Circulation",
            "autoroute": "L'Autoroute",
            "route-automobiles": "Route pour Automobiles",
            "lieux-particuliers": "Lieux Particuliers"
        }
        
        self.reponses_utilisateur = []
        self.questions_examen = []
        self.question_actuelle = 0
        self.examen_en_cours = False
        
        self.creer_menu_principal()
    
    def configurer_styles(self):
        """Configure tous les styles utilisés dans l'application"""
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10, font=('Arial', 10))
        self.style.configure("Title.TLabel", font=('Arial', 16, 'bold'))
        self.style.configure("Question.TLabel", font=('Arial', 12))
        self.style.configure("Selected.TButton", background="#4CAF50", foreground="white")
        
    def charger_questions(self):
        """Charge toutes les questions"""
        return {
            "cyclistes": [
                {
                    "question": "Quelle est la vitesse maximale autorisée dans une zone cyclable ?",
                    "options": ["20 km/h", "30 km/h", "50 km/h", "70 km/h"],
                    "reponse_correcte": 1,
                    "explication": "Dans une zone cyclable, la vitesse maximale autorisée est de 30 km/h."
                },
                {
                    "question": "Qui est obligé d'emprunter une piste cyclable lorsqu'elle est praticable ?",
                    "options": ["Les cyclistes uniquement", "Les cyclistes et les cyclomoteurs classe A", "Tous les usagers", "Personne n'est obligé"],
                    "reponse_correcte": 1,
                    "explication": "Les cyclistes et les cyclomoteurs classe A sont obligés d'emprunter la piste cyclable lorsqu'elle est praticable."
                },
                {
                    "question": "À quel âge les enfants peuvent-ils rouler à vélo sur le trottoir en agglomération ?",
                    "options": ["Jusqu'à 8 ans", "Jusqu'à 10 ans", "Jusqu'à 12 ans", "À tout âge"],
                    "reponse_correcte": 1,
                    "explication": "Seuls les enfants de moins de 10 ans sont autorisés à rouler à vélo sur le trottoir en agglomération."
                },
                {
                    "question": "Que doivent faire les conducteurs lorsqu'un cycliste reprend sa place sur la chaussée à la fin d'une piste cyclable ?",
                    "options": ["Klaxonner pour l'avertir", "Accélérer pour passer avant", "Lui céder le passage", "Rien de particulier"],
                    "reponse_correcte": 2,
                    "explication": "Les conducteurs doivent céder le passage aux cyclistes qui reprennent leur place sur la chaussée à la fin d'une piste cyclable."
                }
            ],
            "bandes": [
                {
                    "question": "Sur quelle bande de circulation devez-vous normalement rouler ?",
                    "options": ["La bande de gauche", "La bande du milieu", "La bande de droite", "N'importe quelle bande"],
                    "reponse_correcte": 2,
                    "explication": "En conditions normales, les conducteurs doivent rouler sur la bande de droite."
                },
                {
                    "question": "Quand peut-on appliquer le principe de la tirette ?",
                    "options": ["Seulement sur autoroute", "Seulement en ville", "En cas de circulation fortement ralentie avec réduction de bandes", "À tout moment"],
                    "reponse_correcte": 2,
                    "explication": "Le principe de la tirette s'applique en cas de circulation fortement ralentie lorsqu'il y a réduction du nombre de bandes de circulation."
                }
            ],
            "autoroute": [
                {
                    "question": "Quelle est la vitesse maximale autorisée sur l'autoroute en conditions normales ?",
                    "options": ["90 km/h", "110 km/h", "120 km/h", "130 km/h"],
                    "reponse_correcte": 2,
                    "explication": "La vitesse maximale sur l'autoroute est de 120 km/h, à condition que les conditions de circulation le permettent."
                },
                {
                    "question": "Quelle est la vitesse minimale sur l'autoroute ?",
                    "options": ["50 km/h", "70 km/h", "90 km/h", "Il n'y a pas de vitesse minimale"],
                    "reponse_correcte": 1,
                    "explication": "Sur une autoroute, vous devez rouler à une vitesse minimale de 70 km/h lorsque les conditions le permettent."
                }
            ],
            "route-automobiles": [
                {
                    "question": "Quelle est la vitesse maximale sur une route pour automobiles hors agglomération en Région wallonne lorsque les sens de circulation sont divisés par une berme centrale ?",
                    "options": ["70 km/h", "90 km/h", "120 km/h", "130 km/h"],
                    "reponse_correcte": 2,
                    "explication": "Sur les routes pour automobiles hors agglomération en Région wallonne, avec berme centrale et au moins deux bandes par sens, la vitesse maximale est de 120 km/h."
                }
            ],
            "lieux-particuliers": [
                {
                    "question": "Quelle est la vitesse maximale en agglomération, sauf indication contraire ?",
                    "options": ["30 km/h", "50 km/h", "70 km/h", "90 km/h"],
                    "reponse_correcte": 1,
                    "explication": "En agglomération, la vitesse maximale autorisée est de 50 km/h, sauf dans la Région Bruxelles-Capitale où elle est de 30 km/h."
                }
            ]
        }
    
    def creer_menu_principal(self):
        """Crée le menu principal avec les boutons de thème"""
        self.effacer_ecran()
        
        # Titre
        titre = ttk.Label(self, text="EXAMEN BLANC - PERMIS DE CONDUIRE BELGE", 
                         style="Title.TLabel")
        titre.pack(pady=30)
        
        # Sous-titre
        sous_titre = ttk.Label(self, text="Choisissez un thème pour l'examen:", 
                              font=('Arial', 12))
        sous_titre.pack(pady=10)
        
        # Frame pour les boutons de thème
        frame_themes = ttk.Frame(self)
        frame_themes.pack(pady=30, padx=50, fill='both', expand=True)
        
        # Création des boutons pour chaque thème
        for i, (theme_key, theme_name) in enumerate(self.themes.items()):
            btn = ttk.Button(
                frame_themes,
                text=theme_name,
                command=lambda t=theme_key: self.commencer_examen(t),
                width=30
            )
            btn.pack(pady=8)
        
        # Bouton quitter
        btn_quitter = ttk.Button(
            self,
            text="Quitter l'application",
            command=self.quitter_application,
            style="TButton"
        )
        btn_quitter.pack(pady=20)
    
    def commencer_examen(self, theme):
        """Démarre un examen avec le thème sélectionné"""
        self.theme_actuel = theme
        self.questions_examen = self.preparer_questions(theme)
        self.reponses_utilisateur = [None] * len(self.questions_examen)
        self.question_actuelle = 0
        self.examen_en_cours = True
        
        self.afficher_question()
    
    def preparer_questions(self, theme):
        """Prépare les questions selon le thème choisi"""
        if theme == "all":
            # Mélange toutes les questions
            toutes_questions = []
            for questions_theme in self.questions.values():
                toutes_questions.extend(questions_theme)
            random.shuffle(toutes_questions)
            return toutes_questions[:5]  # 5 questions pour l'exemple
        else:
            questions_theme = self.questions[theme].copy()
            random.shuffle(questions_theme)
            return questions_theme[:5]  # Correction de la faute de frappe
    
    def afficher_question(self):
        """Affiche la question actuelle"""
        self.effacer_ecran()
        
        if not self.examen_en_cours or self.question_actuelle >= len(self.questions_examen):
            self.afficher_resultats()
            return
        
        question_data = self.questions_examen[self.question_actuelle]
        
        # Frame principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=50, pady=20)
        
        # En-tête avec progression
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=10)
        
        progression = ttk.Label(
            header_frame, 
            text=f"Question {self.question_actuelle + 1}/{len(self.questions_examen)}",
            font=('Arial', 10, 'bold')
        )
        progression.pack(side='left')
        
        # Barre de progression
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=10)
        
        pourcentage = (self.question_actuelle / len(self.questions_examen)) * 100
        progress_bar = ttk.Progressbar(progress_frame, length=400, maximum=100, value=pourcentage)
        progress_bar.pack(fill='x')
        
        # Question
        question_label = ttk.Label(
            main_frame,
            text=question_data['question'],
            style="Question.TLabel",
            wraplength=600
        )
        question_label.pack(pady=30)
        
        # Frame pour les options
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill='both', expand=True, pady=20)
        
        # Boutons pour chaque option
        self.boutons_options = []
        for i, option in enumerate(question_data['options']):
            btn = ttk.Button(
                options_frame,
                text=f"{chr(65 + i)}. {option}",
                command=lambda idx=i: self.selectionner_reponse(idx),
                width=60
            )
            btn.pack(pady=8)
            self.boutons_options.append(btn)
        
        # Frame pour la navigation
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill='x', pady=20)
        
        if self.question_actuelle > 0:
            btn_precedent = ttk.Button(
                nav_frame,
                text="← Question précédente",
                command=self.question_precedente
            )
            btn_precedent.pack(side='left')
        
        # Toujours afficher le bouton suivant, mais le désactiver si pas de réponse
        btn_suivant = ttk.Button(
            nav_frame,
            text="Question suivante →" if self.question_actuelle < len(self.questions_examen) - 1 else "Terminer l'examen",
            command=self.question_suivante if self.question_actuelle < len(self.questions_examen) - 1 else self.terminer_examen
        )
        btn_suivant.pack(side='right')
        
        # Si une réponse est déjà sélectionnée, mettre à jour l'apparence
        if self.reponses_utilisateur[self.question_actuelle] is not None:
            self.mettre_a_jour_apparence_boutons()
    
    def selectionner_reponse(self, index_reponse):
        """Enregistre la réponse sélectionnée"""
        self.reponses_utilisateur[self.question_actuelle] = index_reponse
        self.mettre_a_jour_apparence_boutons()
    
    def mettre_a_jour_apparence_boutons(self):
        """Met à jour l'apparence des boutons de réponse"""
        reponse_selectionnee = self.reponses_utilisateur[self.question_actuelle]
        for i, btn in enumerate(self.boutons_options):
            if i == reponse_selectionnee:
                btn.configure(style="Selected.TButton")
            else:
                btn.configure(style="TButton")
    
    def question_suivante(self):
        """Passe à la question suivante"""
        if self.question_actuelle < len(self.questions_examen) - 1:
            self.question_actuelle += 1
            self.afficher_question()
        else:
            self.terminer_examen()
    
    def question_precedente(self):
        """Retourne à la question précédente"""
        if self.question_actuelle > 0:
            self.question_actuelle -= 1
            self.afficher_question()
    
    def terminer_examen(self):
        """Termine l'examen et affiche les résultats"""
        # Compter les questions sans réponse
        questions_sans_reponse = self.reponses_utilisateur.count(None)
        
        if questions_sans_reponse > 0:
            reponse = messagebox.askyesno(
                "Questions sans réponse", 
                f"Il reste {questions_sans_reponse} question(s) sans réponse. Voulez-vous vraiment terminer l'examen ?"
            )
            if not reponse:
                return
        
        self.examen_en_cours = False
        self.afficher_resultats()
    
    def afficher_resultats(self):
        """Affiche les résultats de l'examen"""
        self.effacer_ecran()
        
        # Calcul du score
        score = 0
        total_questions = len(self.questions_examen)
        
        for i in range(total_questions):
            if self.reponses_utilisateur[i] == self.questions_examen[i]['reponse_correcte']:
                score += 1
        
        pourcentage = (score / total_questions) * 100
        
        # Frame principale
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=50, pady=30)
        
        # Titre
        titre = ttk.Label(main_frame, text="RÉSULTATS DE L'EXAMEN", style="Title.TLabel")
        titre.pack(pady=20)
        
        # Score
        score_text = f"Score: {score}/{total_questions} ({pourcentage:.1f}%)"
        score_label = ttk.Label(main_frame, text=score_text, font=('Arial', 14, 'bold'))
        score_label.pack(pady=10)
        
        # Message de résultat
        if pourcentage >= 80:
            resultat_text = "🎉 FÉLICITATIONS! Vous avez réussi l'examen!"
            couleur = "green"
        else:
            resultat_text = "❌ Dommage! Continuez à réviser!"
            couleur = "red"
        
        resultat_label = ttk.Label(main_frame, text=resultat_text, 
                                  font=('Arial', 12), foreground=couleur)
        resultat_label.pack(pady=10)
        
        # Détail des réponses (dans un cadre défilant)
        detail_frame = ttk.LabelFrame(main_frame, text="Détail des réponses")
        detail_frame.pack(fill='both', expand=True, pady=20)
        
        # Canvas et scrollbar pour le détail
        canvas = tk.Canvas(detail_frame)
        scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Ajouter chaque question avec le détail
        for i in range(total_questions):
            question_data = self.questions_examen[i]
            reponse_utilisateur = self.reponses_utilisateur[i]
            reponse_correcte = question_data['reponse_correcte']
            
            # Frame pour chaque question
            q_frame = ttk.Frame(scrollable_frame)
            q_frame.pack(fill='x', pady=10, padx=10)
            
            # Numéro de question
            num_label = ttk.Label(q_frame, text=f"Question {i+1}:", font=('Arial', 10, 'bold'))
            num_label.pack(anchor='w')
            
            # Question
            question_label = ttk.Label(q_frame, text=question_data['question'], 
                                      wraplength=600)
            question_label.pack(anchor='w', pady=(5, 0))
            
            # Réponse de l'utilisateur
            if reponse_utilisateur is not None:
                reponse_texte = question_data['options'][reponse_utilisateur]
                if reponse_utilisateur == reponse_correcte:
                    reponse_label = ttk.Label(q_frame, text=f"✅ Votre réponse: {reponse_texte}",
                                            foreground="green")
                else:
                    reponse_label = ttk.Label(q_frame, text=f"❌ Votre réponse: {reponse_texte}",
                                            foreground="red")
                reponse_label.pack(anchor='w', pady=(5, 0))
            else:
                reponse_label = ttk.Label(q_frame, text="⏰ Vous n'avez pas répondu à cette question",
                                        foreground="orange")
                reponse_label.pack(anchor='w', pady=(5, 0))
            
            # Réponse correcte (si erreur ou pas de réponse)
            if reponse_utilisateur != reponse_correcte:
                reponse_correcte_texte = question_data['options'][reponse_correcte]
                correct_label = ttk.Label(q_frame, text=f"✅ Réponse correcte: {reponse_correcte_texte}",
                                        foreground="green")
                correct_label.pack(anchor='w', pady=(2, 0))
            
            # Explication
            explication_label = ttk.Label(q_frame, text=f"💡 {question_data['explication']}",
                                        wraplength=600, foreground="blue")
            explication_label.pack(anchor='w', pady=(5, 0))
            
            # Séparateur
            if i < total_questions - 1:
                separateur = ttk.Separator(q_frame, orient='horizontal')
                separateur.pack(fill='x', pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Boutons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill='x', pady=20)
        
        btn_nouvel_examen = ttk.Button(
            btn_frame,
            text="Nouvel examen",
            command=self.creer_menu_principal
        )
        btn_nouvel_examen.pack(side='left', padx=10)
        
        btn_meme_theme = ttk.Button(
            btn_frame,
            text="Refaire le même thème",
            command=lambda: self.commencer_examen(self.theme_actuel)
        )
        btn_meme_theme.pack(side='left', padx=10)
        
        btn_quitter = ttk.Button(
            btn_frame,
            text="Quitter",
            command=self.quitter_application
        )
        btn_quitter.pack(side='right', padx=10)
    
    def effacer_ecran(self):
        """Efface tous les widgets de l'écran"""
        for widget in self.winfo_children():
            widget.destroy()
    
    def quitter_application(self):
        """Quitte l'application"""
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter l'application?"):
            self.destroy()

if __name__ == "__main__":
    app = ApplicationPermis()
    app.mainloop()