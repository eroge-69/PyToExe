import subprocess

# Imposta il nome del dispositivo Miracast
miracast_device = "Xhadapter-2D1A06"

# Imposta la password del dispositivo Miracast
miracast_password = "12345678

# Funzione per connettersi al dispositivo Miracast
def connetti_miracast():
    try:
        # Utilizza netsh per connetterti al dispositivo Miracast
        subprocess.run(["netsh", "wlan", "connect", "name=" + miracast_device, "key=" + miracast_password])
        print("Connesso al dispositivo Miracast!")
    except Exception as e:
        print("Errore durante la connessione: " + str(e))

# Funzione per condividere lo schermo del computer
def condividi_schermo():
    try:
        # Utilizza ms-settings per aprire le impostazioni di condivisione schermo
        subprocess.run(["ms-settings", "connect"])
        print("Schermo condiviso con il dispositivo Miracast!")
    except Exception as e:
        print("Errore durante la condivisione dello schermo: " + str(e))

# Esegui le funzioni per connettersi al dispositivo Miracast e condividere lo schermo del computer
connetti_miracast()
condividi_schermo()