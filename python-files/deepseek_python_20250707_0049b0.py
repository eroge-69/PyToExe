import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import schedule
import pytz
import configparser
import logging
from win10toast import ToastNotifier
import threading

# Configuration de base
VERSION = "1.0"
APP_NAME = "Turfoo Quinte Automatique"
CONFIG_FILE = "quinte_config.ini"
LOG_FILE = "quinte_system.log"
ICON_FILE = "quinte_icon.ico"

# Configuration des opérateurs SMS
CARRIER_DOMAINS = {
    'airtelgabon': 'sms.airtelgabon.com',
    'orange': 'orange.fr',
    'sfr': 'sfr.fr',
    'free': 'free.fr',
    'bouygues': 'bouyguestelecom.fr'
}

# Configuration des points
POINTS_PAR_POSITION = {
    1: 50, 2: 25, 3: 13, 4: 6, 
    5: 3, 6: 1, 7: 1, 8: 1
}

# Sources de pronostics
SOURCES = [
    "Le Parisien",
    "Le Progrès de Lyon",
    "WeekEnd",
    "Midi Libre",
    "Le Quotidien de la Réunion"
]

class QuinteSystem:
    def __init__(self):
        self.tz_gabon = pytz.timezone('Africa/Libreville')
        self.toaster = ToastNotifier()
        self.config = self.load_config()
        self.running = True
        self.logger = self.setup_logger()
        
        # Afficher notification de démarrage
        self.show_notification(f"{APP_NAME} démarré", "Le système fonctionne en arrière-plan")
        
    def setup_logger(self):
        """Configure le système de journalisation"""
        logger = logging.getLogger('QuinteSystem')
        logger.setLevel(logging.INFO)
        
        # Format des logs
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # Handler pour fichier log
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Handler pour console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    def load_config(self):
        """Charge ou crée la configuration"""
        config = configparser.ConfigParser()
        
        # Créer la configuration par défaut si elle n'existe pas
        if not os.path.exists(CONFIG_FILE):
            config['EMAIL'] = {
                'sender': 'dkprods777@gmail.com',
                'password': '',
                'receiver': 'dkprods777@gmail.com'
            }
            config['SMS'] = {
                'phone': '+24174599459',
                'carrier': 'airtelgabon'
            }
            config['SETTINGS'] = {
                'first_run': '1'
            }
            
            with open(CONFIG_FILE, 'w') as configfile:
                config.write(configfile)
        
        # Lire la configuration
        config.read(CONFIG_FILE)
        return config
    
    def show_notification(self, title, message):
        """Affiche une notification Windows"""
        try:
            self.toaster.show_toast(
                title,
                message,
                icon_path=ICON_FILE if os.path.exists(ICON_FILE) else None,
                duration=5,
                threaded=True
            )
        except Exception as e:
            self.logger.error(f"Erreur notification: {str(e)}")
    
    def get_quinte_pronos(self):
        """Récupère les pronostics depuis Turfoo"""
        try:
            url = "https://www.turfoo.fr/pronostics-pmu/tierce/presse/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept-Language': 'fr-FR,fr;q=0.9'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            course_title = soup.find('h1', class_='entry-title').text.strip()
            self.logger.info(f"Course identifiée: {course_title}")
            
            # Vérification du type de course
            if "trot attelé" not in course_title.lower():
                return None, course_title, "Pas de course de trot attelé aujourd'hui", None
            
            # Extraction de l'heure de la course
            course_time = None
            time_tag = soup.find('span', class_='heure-course')
            if time_tag:
                course_time = time_tag.text.strip()
                self.logger.info(f"Heure de la course: {course_time}")
            
            table = soup.find('table', class_='tablepress')
            if not table:
                raise Exception("Tableau des pronostics introuvable")
            
            pronos = {}
            for row in table.find_all('tr')[1:]:
                cells = row.find_all('td')
                if len(cells) < 6:
                    continue
                    
                site_name = cells[0].text.strip()
                if site_name in SOURCES:
                    chevaux = []
                    for i in range(1, 9):
                        if i < len(cells):
                            cheval = cells[i].text.strip()
                            if cheval:
                                chevaux.append(cheval)
                    pronos[site_name] = chevaux
            
            return pronos, course_title, None, course_time
            
        except Exception as e:
            self.logger.error(f"Erreur scraping: {str(e)}")
            return None, None, str(e), None
    
    def apply_special_trick(self, pronos):
        """Applique la méthode de calcul spéciale"""
        points_par_cheval = {}
        for site, chevaux in pronos.items():
            for position, cheval in enumerate(chevaux, start=1):
                pts = POINTS_PAR_POSITION.get(position, 0)
                points_par_cheval[cheval] = points_par_cheval.get(cheval, 0) + pts
        
        # Tri par points décroissants
        sorted_chevaux = sorted(points_par_cheval.items(), key=lambda x: x[1], reverse=True)
        return sorted_chevaux
    
    def send_email(self, subject, body, is_html=False):
        """Envoie un email"""
        try:
            sender = self.config['EMAIL']['sender']
            password = self.config['EMAIL']['password']
            receiver = self.config['EMAIL']['receiver']
            
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MIMEText(body, 'html'))
            else:
                msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            
            self.logger.info("Email envoyé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur envoi email: {str(e)}")
            return False
    
    def send_sms(self, message):
        """Envoie un SMS"""
        try:
            phone = self.config['SMS']['phone']
            carrier = self.config['SMS']['carrier'].lower()
            
            if carrier not in CARRIER_DOMAINS:
                self.logger.error(f"Opérateur non pris en charge: {carrier}")
                return False
                
            sender = self.config['EMAIL']['sender']
            password = self.config['EMAIL']['password']
            sms_gateway = f"{phone}@{CARRIER_DOMAINS[carrier]}"
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, sms_gateway, message)
            server.quit()
            
            self.logger.info("SMS envoyé avec succès")
            return True
        except Exception as e:
            self.logger.error(f"Erreur envoi SMS: {str(e)}")
            return False
    
    def generate_report(self, pronos, course_title, resultats, course_time=None, is_update=False):
        """Génère le rapport de pronostics"""
        now_gabon = datetime.now(self.tz_gabon).strftime('%d/%m/%Y %H:%M')
        
        if is_update:
            subject = f"🔄 Mise à jour Pronostics Quinte - {datetime.now(self.tz_gabon).strftime('%d/%m/%Y')}"
            header = "MISE À JOUR DES PRONOSTICS (1h avant la course)"
        else:
            subject = f"🏇 Pronostics Quinte du Jour - {datetime.now(self.tz_gabon).strftime('%d/%m/%Y')}"
            header = "PRONOSTICS INITIAUX"
        
        # Version texte pour SMS et notification
        text_content = f"{header}\n\n"
        text_content += f"Course: {course_title}\n"
        if course_time:
            text_content += f"Heure: {course_time}\n"
        text_content += f"Date: {now_gabon}\n\n"
        
        text_content += "Votre sélection :\n"
        for i, (cheval, points) in enumerate(resultats[:5], 1):
            text_content += f"{i}. {cheval} ({points} points)\n"
        
        text_content += "\nBonne chance pour vos paris!"
        
        return subject, text_content
    
    def daily_task(self, is_update=False):
        """Tâche principale exécutée aux heures programmées"""
        self.logger.info(f"Début de la tâche {'de mise à jour' if is_update else 'quotidienne'}")
        
        try:
            # Récupération des pronostics
            pronos, course_title, error, course_time = self.get_quinte_pronos()
            
            if error:
                # Gestion des erreurs
                if "trot attelé" in error:
                    msg = "Pas de course de trot attelé aujourd'hui"
                    self.show_notification("Pas de course", msg)
                else:
                    msg = f"Erreur: {error}"
                    self.show_notification("Erreur système", msg)
                
                # Envoi notification
                email_subject = "Turfoo Quinte - Notification"
                self.send_email(email_subject, msg)
                self.send_sms(msg)
                return
            
            # Application de la méthode de calcul
            resultats = self.apply_special_trick(pronos)
            
            # Génération du rapport
            subject, text_report = self.generate_report(
                pronos, course_title, resultats, course_time, is_update
            )
            
            # Envoi des notifications
            email_sent = self.send_email(subject, text_report)
            sms_sent = self.send_sms(text_report)
            
            # Notification Windows
            if email_sent and sms_sent:
                notif_msg = "Pronostics envoyés par email et SMS"
            elif email_sent:
                notif_msg = "Pronostics envoyés par email"
            elif sms_sent:
                notif_msg = "Pronostics envoyés par SMS"
            else:
                notif_msg = "Échec de l'envoi des notifications"
            
            self.show_notification("Pronostics Quinte", notif_msg)
            self.logger.info("Tâche terminée avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur dans la tâche: {str(e)}")
            self.show_notification("Erreur système", f"Une erreur s'est produite: {str(e)}")
    
    def schedule_tasks(self):
        """Planifie les tâches quotidiennes"""
        # Premier envoi à 10h30 (heure du Gabon)
        schedule.every().day.at("10:30").do(lambda: self.daily_task()).tag("daily")
        self.logger.info("Tâche programmée: Envoi quotidien à 10h30")
        
        # Vérification pour le deuxième envoi (1h avant la course)
        def check_second_send():
            now = datetime.now(self.tz_gabon)
            if now.hour >= 12:
                # En pratique, on utiliserait l'heure réelle de la course
                # Pour cet exemple, supposons une course à 15h30
                course_time = now.replace(hour=15, minute=30, second=0, microsecond=0)
                if now >= (course_time - timedelta(hours=1)) and now < course_time:
                    self.daily_task(is_update=True)
        
        schedule.every(10).minutes.do(check_second_send)
        self.logger.info("Vérification programmée pour l'envoi 1h avant la course")
    
    def run(self):
        """Point d'entrée principal de l'application"""
        self.logger.info(f"=== {APP_NAME} v{VERSION} ===")
        self.logger.info("Chargement de la configuration...")
        
        # Vérifier la configuration email
        if not self.config['EMAIL']['password']:
            self.logger.error("Mot de passe email non configuré!")
            self.show_notification(
                "Configuration requise", 
                "Veuillez configurer votre mot de passe email dans quinte_config.ini"
            )
            return
        
        # Planifier les tâches
        self.schedule_tasks()
        
        # Boucle principale
        self.logger.info("Démarrage de la boucle principale...")
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            self.logger.info("Arrêt demandé par l'utilisateur")
        except Exception as e:
            self.logger.error(f"Erreur critique: {str(e)}")
        finally:
            self.logger.info("Arrêt du système")

def create_shortcut():
    """Crée un raccourci dans le dossier Démarrage"""
    if getattr(sys, 'frozen', False):
        app_path = sys.executable
    else:
        app_path = os.path.abspath(__file__)
    
    startup_dir = os.path.join(
        os.getenv('APPDATA'), 
        'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
    )
    shortcut_path = os.path.join(startup_dir, "QuinteSystem.lnk")
    
    if not os.path.exists(shortcut_path):
        try:
            import winshell
            from win32com.client import Dispatch
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = app_path
            shortcut.WorkingDirectory = os.path.dirname(app_path)
            shortcut.IconLocation = os.path.join(os.path.dirname(app_path), ICON_FILE)
            shortcut.save()
            return True
        except Exception as e:
            print(f"Erreur création raccourci: {str(e)}")
            return False
    return True

if __name__ == "__main__":
    # Créer le raccourci de démarrage
    create_shortcut()
    
    # Démarrer le système
    system = QuinteSystem()
    system.run()