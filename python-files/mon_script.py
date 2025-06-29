import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding as rsa_padding
from cryptography.hazmat.primitives import hashes

script_folder = os.path.dirname(__file__)
files_folder = os.path.join(script_folder, "files")
keys_folder = os.path.join(files_folder, "keys")
rsa_folder = os.path.join(script_folder, "rsa_keys")

os.makedirs(keys_folder, exist_ok=True)
os.makedirs(files_folder, exist_ok=True)
os.makedirs(rsa_folder, exist_ok=True)

def menu():
    while True:
        print("\n=== MENU DE CHIFFREMENT ===")
        print("1. Chiffrer un fichier")
        print("2. Déchiffrer un fichier")
        print("3. Générer des clés RSA")
        print("4. Quitter")
        choice = input("Votre choix : ").strip()

        if choice == "1":
            encrypt_file()
        elif choice == "2":
            decrypt_file()
        elif choice == "3":
            generate_rsa_keys()
        elif choice == "4":
            break
        else:
            print("Choix invalide.")

def encrypt_file():
    file_name = input("Nom du fichier à chiffrer (dans /files) : ").strip()
    algo = input("Algorithme (fernet / aes / rsa) : ").strip().lower()
    file_path = os.path.join(files_folder, file_name)

    if not os.path.isfile(file_path):
        print("Fichier introuvable.")
        return

    with open(file_path, "rb") as f:
        data = f.read()

    base_name, ext = os.path.splitext(file_name)

    if algo == "fernet":
        key = Fernet.generate_key()
        cipher = Fernet(key)
        encrypted_data = cipher.encrypt(data)
        key_info = {"algo": "fernet", "key": key.decode(), "ext": ext}

    elif algo == "aes":
        key = os.urandom(32)
        iv = os.urandom(16)
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        encryptor = cipher.encryptor()
        encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
        key_info = {
            "algo": "aes",
            "key": base64.b64encode(key).decode(),
            "iv": base64.b64encode(iv).decode(),
            "ext": ext
        }

    elif algo == "rsa":
        public_path = os.path.join(rsa_folder, "public.pem")
        if not os.path.exists(public_path):
            print("Générer d'abord les clés RSA.")
            return
        with open(public_path, "rb") as f:
            public_key = serialization.load_pem_public_key(f.read())
        encrypted_data = public_key.encrypt(
            data,
            rsa_padding.OAEP(
                mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        key_info = {"algo": "rsa", "ext": ext}

    else:
        print("Algorithme inconnu.")
        return

    encrypted_path = os.path.join(files_folder, base_name + ".crypted")
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)

    key_path = os.path.join(keys_folder, base_name + ".key")
    with open(key_path, "w") as f:
        json.dump(key_info, f, indent=4)

    os.remove(file_path)
    print("Fichier chiffré et clé sauvegardée.")

def decrypt_file():
    encrypted_name = input("Nom du fichier à déchiffrer (dans /files) : ").strip()
    encrypted_path = os.path.join(files_folder, encrypted_name)
    base_name = os.path.splitext(encrypted_name)[0]
    key_path = os.path.join(keys_folder, base_name + ".key")

    if not os.path.isfile(encrypted_path) or not os.path.isfile(key_path):
        print("Fichier ou clé introuvable.")
        return

    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()

    with open(key_path, "r") as f:
        key_info = json.load(f)

    algo = key_info["algo"]

    if algo == "fernet":
        key = key_info["key"].encode()
        cipher = Fernet(key)
        decrypted_data = cipher.decrypt(encrypted_data)

    elif algo == "aes":
        key = base64.b64decode(key_info["key"])
        iv = base64.b64decode(key_info["iv"])
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        decryptor = cipher.decryptor()
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        unpadder = padding.PKCS7(128).unpadder()
        decrypted_data = unpadder.update(padded_data) + unpadder.finalize()

    elif algo == "rsa":
        private_path = os.path.join(rsa_folder, "private.pem")
        if not os.path.exists(private_path):
            print("Clé privée RSA manquante.")
            return
        with open(private_path, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        decrypted_data = private_key.decrypt(
            encrypted_data,
            rsa_padding.OAEP(
                mgf=rsa_padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

    else:
        print("Algorithme inconnu dans le fichier clé.")
        return

    decrypted_path = os.path.join(files_folder, base_name + key_info["ext"])
    with open(decrypted_path, "wb") as f:
        f.write(decrypted_data)

    print("Fichier déchiffré :", decrypted_path)

def generate_rsa_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()

    private_path = os.path.join(rsa_folder, "private.pem")
    public_path = os.path.join(rsa_folder, "public.pem")

    with open(private_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open(public_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("Clés RSA générées et sauvegardées.")

menu()