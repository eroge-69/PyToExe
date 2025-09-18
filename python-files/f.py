import pyvisa
from PIL import Image
import io

def get_screenshot_usb(instrument_address, filename='oscilloscope_screenshot.png'):
    """
    Connecte à l'oscilloscope Keysight via USB, capture l'écran et l'enregistre.

    Args:
        instrument_address (str): L'adresse USB de l'instrument.
        filename (str): Le nom du fichier où enregistrer la capture.
    """
    # Crée un gestionnaire de ressources VISA
    rm = pyvisa.ResourceManager()
    print(f"Tentative de connexion à l'instrument à l'adresse: {instrument_address}")

    try:
        # Ouvre la connexion USB avec l'oscilloscope
        scope = rm.open_resource(instrument_address)
        scope.timeout = 20000  # 20 secondes

        # 1. Envoie la commande pour définir le format d'image en PNG
        scope.write(":DISPlay:DATA:FORMat PNG")

        # 2. Lit les données binaires de l'écran
        print("Capture de l'écran en cours...")
        binary_image_data = scope.query_binary_values(":DISPlay:DATA? PNG", datatype='B')

        # 3. Ferme la connexion
        scope.close()
        print("Connexion fermée.")

        # 4. Convertit les données binaires en image avec Pillow
        image = Image.open(io.BytesIO(bytearray(binary_image_data)))

        # 5. Sauvegarde l'image dans un fichier
        image.save(filename)
        print(f"La capture d'écran a été enregistrée sous le nom: {filename}")

    except Exception as e:
        print(f"Une erreur est survenue : {e}")
        print("Veuillez vérifier l'adresse de l'instrument et la connexion USB.")

# --- Utilisation du script ---
# Remplacez l'adresse ci-dessous par l'adresse USB de votre oscilloscope.
# Cette adresse a généralement le format 'USB0::xxxxx::xxxx::xxxx::0::INSTR'
adresse_de_linstrument = 'USB0::1234::5678::MY_SERIAL::0::INSTR'  # Exemple d'adresse USB

get_screenshot_usb(adresse_de_linstrument)
