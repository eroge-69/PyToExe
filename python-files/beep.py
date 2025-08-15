import time
import winsound

def beep_per_second(X):
    if X < 1:
        print("Numero di beep deve essere almeno 1")
        return
    if X > 2000:
        print("Massimo 2000 beep consentiti")
        X = 2000
    for i in range(X):
        print(f"Beep {i+1}/{X}")
        winsound.Beep(1000, 200)  # frequenza 1000 Hz, durata 200 ms
        time.sleep(1)  # pausa 1 secondo

if __name__ == "__main__":
    try:
        X = int(input("Quanti beep vuoi? "))
        beep_per_second(X)
    except ValueError:
        print("Inserisci un numero intero valido")
