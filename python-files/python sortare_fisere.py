import os
import shutil
import sys

def sorteaza_fisere_dupa_extensie(cale_director):
    """
    Sortează fișierele dintr-un director dat, creând sub-directoare
    pentru fiecare extensie și mutând fișierele corespunzătoare.
    """
    # Verifică dacă directorul există
    if not os.path.isdir(cale_director):
        print(f"Eroare: Directorul '{cale_director}' nu există sau nu este valid.")
        return

    print(f"\n--- Începe sortarea fișierelor în: {cale_director} ---")

    # Parcurge toate elementele din director
    for nume_element in os.listdir(cale_director):
        cale_completa_element = os.path.join(cale_director, nume_element)

        # Ignoră directoarele existente
        if os.path.isdir(cale_completa_element):
            continue

        # Extrage numele de bază și extensia fișierului
        nume_baza, extensie = os.path.splitext(nume_element)
        
        # Procesează doar fișierele cu extensie
        if extensie:
            # Elimină punctul din extensie (ex: ".txt" devine "txt")
            extensie_fara_punct = extensie[1:].lower() 

            # Creează calea către directorul de destinație (ex: 'cale/catre/director/txt')
            director_destinatie = os.path.join(cale_director, extensie_fara_punct)

            # Creează directorul de destinație dacă nu există
            if not os.path.exists(director_destinatie):
                try:
                    os.makedirs(director_destinatie)
                    print(f"  > Creat directorul: '{extensie_fara_punct}/'")
                except OSError as e:
                    print(f"Eroare la crearea directorului '{director_destinatie}': {e}")
                    continue

            # Mută fișierul
            try:
                shutil.move(cale_completa_element, director_destinatie)
                print(f"  > Mutat: '{nume_element}' în '{extensie_fara_punct}/'")
            except shutil.Error as e:
                print(f"Eroare la mutarea fișierului '{nume_element}': {e}")
            except Exception as e:
                print(f"Eroare neașteptată la mutarea fișierului '{nume_element}': {e}")
        else:
            print(f"  > Ignorat: '{nume_element}' (fără extensie)")
    
    print(f"--- Sortare finalizată pentru: {cale_director} ---\n")

# --- Cum să folosești scriptul ---
if __name__ == "__main__":
    # Dacă rulezi scriptul direct, va cere calea
    if len(sys.argv) > 1:
        director_de_sortat = sys.argv[1]
    else:
        director_de_sortat = input("Introduceți calea completă a directorului de sortat (ex: C:/Users/NumeleMeu/Descarcari sau /home/utilizator/Downloads): ")

    sorteaza_fisere_dupa_extensie(director_de_sortat)
    print("Programul a rulat. Verificați directorul specificat.")