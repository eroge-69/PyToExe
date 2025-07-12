#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Python pour l'impression directe sur imprimante thermique
Usage: python thermal_printer.py <printer_name> <html_content>
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path
import win32print
import win32api
import win32con
from datetime import datetime

class ThermalPrinter:
    def __init__(self):
        self.default_printer = None
        self.thermal_printer = None
        self.load_config()
    
    def load_config(self):
        """Charge la configuration depuis un fichier JSON"""
        config_file = Path("printer_config.json")
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.default_printer = config.get('default_printer')
                    self.thermal_printer = config.get('thermal_printer_name')
            except Exception as e:
                print(f"Erreur lors du chargement de la configuration: {e}")
    
    def save_config(self):
        """Sauvegarde la configuration dans un fichier JSON"""
        config = {
            'default_printer': self.default_printer,
            'thermal_printer_name': self.thermal_printer,
            'last_updated': datetime.now().isoformat()
        }
        try:
            with open("printer_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la configuration: {e}")
    
    def get_available_printers(self):
        """Récupère la liste des imprimantes disponibles"""
        printers = []
        try:
            for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS):
                printers.append(printer[2])
        except Exception as e:
            print(f"Erreur lors de la récupération des imprimantes: {e}")
        return printers
    
    def detect_thermal_printer(self):
        """Détecte automatiquement une imprimante thermique"""
        printers = self.get_available_printers()
        thermal_keywords = ['pos', 'thermal', 'receipt', 'ticket', '58', '80', 'epson tm', 'star tsp']
        
        for printer in printers:
            printer_lower = printer.lower()
            if any(keyword in printer_lower for keyword in thermal_keywords):
                return printer
        
        return None
    
    def set_default_printer(self, printer_name):
        """Définit l'imprimante par défaut"""
        try:
            win32print.SetDefaultPrinter(printer_name)
            return True
        except Exception as e:
            print(f"Erreur lors de la définition de l'imprimante par défaut: {e}")
            return False
    
    def print_html_direct(self, html_content, printer_name=None, copies=1):
        """Imprime directement le contenu HTML sur l'imprimante spécifiée"""
        try:
            # Créer un fichier temporaire HTML
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html_file = f.name
            
            # Créer un fichier temporaire pour les paramètres d'impression
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(f"Copies: {copies}\n")
                f.write(f"Printer: {printer_name or 'Default'}\n")
                temp_config_file = f.name
            
            # Utiliser wkhtmltopdf pour convertir HTML en PDF puis imprimer
            # Si wkhtmltopdf n'est pas disponible, utiliser une méthode alternative
            if self._has_wkhtmltopdf():
                return self._print_with_wkhtmltopdf(temp_html_file, printer_name, copies)
            else:
                return self._print_with_browser(temp_html_file, printer_name, copies)
                
        except Exception as e:
            print(f"Erreur lors de l'impression: {e}")
            return False
        finally:
            # Nettoyer les fichiers temporaires
            try:
                os.unlink(temp_html_file)
                os.unlink(temp_config_file)
            except:
                pass
    
    def _has_wkhtmltopdf(self):
        """Vérifie si wkhtmltopdf est installé"""
        try:
            subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, check=True)
            return True
        except:
            return False
    
    def _print_with_wkhtmltopdf(self, html_file, printer_name, copies):
        """Imprime en utilisant wkhtmltopdf"""
        try:
            # Créer un fichier PDF temporaire
            pdf_file = html_file.replace('.html', '.pdf')
            
            # Convertir HTML en PDF
            cmd = [
                'wkhtmltopdf',
                '--page-size', '80mm',
                '--margin-top', '0',
                '--margin-right', '0',
                '--margin-bottom', '0',
                '--margin-left', '0',
                '--print-media-type',
                html_file,
                pdf_file
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            # Imprimer le PDF
            if printer_name:
                self.set_default_printer(printer_name)
            
            win32api.ShellExecute(0, "print", pdf_file, None, ".", 0)
            
            # Nettoyer
            os.unlink(pdf_file)
            return True
            
        except Exception as e:
            print(f"Erreur avec wkhtmltopdf: {e}")
            return False
    
    def _print_with_browser(self, html_file, printer_name, copies):
        """Imprime en utilisant le navigateur par défaut"""
        try:
            # Créer un fichier HTML avec auto-impression
            auto_print_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Impression Thermique</title>
    <style>
        @media print {{
            @page {{
                size: 80mm auto;
                margin: 0;
            }}
            body {{
                margin: 0;
                padding: 0;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            }}
        }}
    </style>
    <script>
        window.onload = function() {{
            window.print();
            setTimeout(function() {{
                window.close();
            }}, 1000);
        }};
    </script>
</head>
<body>
{self._read_file_content(html_file)}
</body>
</html>
"""
            
            # Sauvegarder le fichier avec auto-impression
            auto_print_file = html_file.replace('.html', '_print.html')
            with open(auto_print_file, 'w', encoding='utf-8') as f:
                f.write(auto_print_html)
            
            # Ouvrir avec le navigateur par défaut
            if printer_name:
                self.set_default_printer(printer_name)
            
            win32api.ShellExecute(0, "open", auto_print_file, None, ".", 0)
            
            # Nettoyer après un délai
            import threading
            import time
            def cleanup():
                time.sleep(5)
                try:
                    os.unlink(auto_print_file)
                except:
                    pass
            
            threading.Thread(target=cleanup, daemon=True).start()
            return True
            
        except Exception as e:
            print(f"Erreur avec le navigateur: {e}")
            return False
    
    def _read_file_content(self, file_path):
        """Lit le contenu d'un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier: {e}")
            return ""
    
    def print_from_stdin(self):
        """Lit le contenu HTML depuis stdin et l'imprime"""
        try:
            # Lire les arguments de ligne de commande
            if len(sys.argv) < 2:
                print("Usage: python thermal_printer.py <printer_name> [copies]")
                return False
            
            printer_name = sys.argv[1] if len(sys.argv) > 1 else None
            copies = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            
            # Lire le contenu HTML depuis stdin
            html_content = sys.stdin.read()
            
            if not html_content.strip():
                print("Aucun contenu HTML fourni")
                return False
            
            # Imprimer
            success = self.print_html_direct(html_content, printer_name, copies)
            
            if success:
                print("Impression réussie")
                return True
            else:
                print("Échec de l'impression")
                return False
                
        except Exception as e:
            print(f"Erreur: {e}")
            return False

def main():
    """Fonction principale"""
    printer = ThermalPrinter()
    
    # Si aucun argument, afficher l'aide
    if len(sys.argv) == 1:
        print("=== Imprimante Thermique Python ===")
        print("Usage:")
        print("  python thermal_printer.py <printer_name> [copies] < html_file")
        print("  echo '<html>...</html>' | python thermal_printer.py <printer_name>")
        print("\nImprimantes disponibles:")
        for p in printer.get_available_printers():
            print(f"  - {p}")
        print(f"\nImprimante thermique détectée: {printer.detect_thermal_printer()}")
        return
    
    # Exécuter l'impression
    success = printer.print_from_stdin()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 