#!/usr/bin/env python3
"""
Logiciel de chiffrement de fichiers PHP
Récupère la variable d'environnement PGI, chiffre les fichiers .php du dossier /web
et les sauvegarde en .bin dans le dossier /www
"""

import os
import sys
import glob
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class PHPEncryptor:
    def __init__(self):
        self.source_dir = "/web"
        self.target_dir = "/www"
        self.encryption_key = None
        
    def get_environment_variable(self):
        """Récupère la variable d'environnement PGI"""
        pgi_value = os.getenv('PGI')
        if not pgi_value:
            raise ValueError("La variable d'environnement 'PGI' n'est pas définie")
        return pgi_value
    
    def generate_key_from_password(self, password):
        """Génère une clé de chiffrement à partir du mot de passe"""
        # Utilise un salt fixe pour que la même clé soit générée à chaque fois
        salt = b'php_encryptor_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_data(self, data):
        """Chiffre les données avec la clé"""
        fernet = Fernet(self.encryption_key)
        encrypted_data = fernet.encrypt(data)
        return encrypted_data
    
    def ensure_directories_exist(self):
        """Vérifie que les dossiers source et destination existent"""
        if not os.path.exists(self.source_dir):
            raise FileNotFoundError(f"Le dossier source '{self.source_dir}' n'existe pas")
        
        # Crée le dossier de destination s'il n'existe pas
        os.makedirs(self.target_dir, exist_ok=True)
        print(f"Dossier de destination: {self.target_dir}")
    
    def find_php_files(self):
        """Trouve tous les fichiers .php dans le dossier source"""
        php_pattern = os.path.join(self.source_dir, "*.php")
        php_files = glob.glob(php_pattern)
        
        if not php_files:
            print(f"Aucun fichier .php trouvé dans {self.source_dir}")
            return []
        
        print(f"Fichiers .php trouvés: {len(php_files)}")
        return php_files
    
    def encrypt_file(self, source_file):
        """Chiffre un fichier PHP et le sauvegarde en .bin"""
        try:
            # Lit le contenu du fichier PHP
            with open(source_file, 'rb') as f:
                file_content = f.read()
            
            # Chiffre le contenu
            encrypted_content = self.encrypt_data(file_content)
            
            # Génère le nom du fichier de destination
            source_filename = os.path.basename(source_file)
            base_name = os.path.splitext(source_filename)[0]
            target_filename = f"{base_name}.bin"
            target_path = os.path.join(self.target_dir, target_filename)
            
            # Sauvegarde le fichier chiffré
            with open(target_path, 'wb') as f:
                f.write(encrypted_content)
            
            print(f"✓ {source_filename} → {target_filename}")
            return True
            
        except Exception as e:
            print(f"✗ Erreur lors du chiffrement de {source_file}: {e}")
            return False
    
    def process_files(self):
        """Traite tous les fichiers PHP"""
        try:
            # 1. Récupère la variable d'environnement
            print("=== Récupération de la variable d'environnement PGI ===")
            pgi_value = self.get_environment_variable()
            print(f"Variable PGI récupérée: {'*' * len(pgi_value)}")  # Masque la valeur pour la sécurité
            
            # 2. Génère la clé de chiffrement
            print("\n=== Génération de la clé de chiffrement ===")
            self.encryption_key = self.generate_key_from_password(pgi_value)
            print("Clé de chiffrement générée avec succès")
            
            # 3. Vérifie les dossiers
            print("\n=== Vérification des dossiers ===")
            self.ensure_directories_exist()
            print(f"Dossier source: {self.source_dir}")
            
            # 4. Trouve les fichiers PHP
            print("\n=== Recherche des fichiers PHP ===")
            php_files = self.find_php_files()
            
            if not php_files:
                return
            
            # 5. Chiffre les fichiers
            print("\n=== Chiffrement des fichiers ===")
            success_count = 0
            
            for php_file in php_files:
                if self.encrypt_file(php_file):
                    success_count += 1
            
            # 6. Résumé
            print(f"\n=== Résumé ===")
            print(f"Fichiers traités avec succès: {success_count}/{len(php_files)}")
            print(f"Fichiers chiffrés sauvegardés dans: {self.target_dir}")
            
        except Exception as e:
            print(f"Erreur fatale: {e}")
            sys.exit(1)

def main():
    """Fonction principale"""
    print("=== CHIFFREUR DE FICHIERS PHP ===")
    print("Ce programme chiffre tous les fichiers .php du dossier /web")
    print("avec la clé de la variable d'environnement PGI")
    print("et les sauvegarde en .bin dans /www\n")
    
    encryptor = PHPEncryptor()
    encryptor.process_files()
    
    print("\n=== TRAITEMENT TERMINÉ ===")

if __name__ == "__main__":
    main()