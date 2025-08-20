import subprocess
import sys
import os
from pathlib import Path

def install_dependencies():
    """Installa automaticamente le dipendenze necessarie"""
    required_packages = ['pandas', 'openpyxl']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} già installato")
        except ImportError:
            print(f"Installazione di {package} in corso...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} installato con successo")
            except subprocess.CalledProcessError:
                print(f"✗ Errore nell'installazione di {package}")
                return False
    
    return True

def main():
    # Installazione dipendenze
    print("Verifica e installazione dipendenze...")
    if not install_dependencies():
        print("ERRORE: Impossibile installare le dipendenze necessarie")
        input("Premi Invio per uscire...")
        return
    
    # Importazione delle librerie dopo l'installazione
    try:
        import pandas as pd
        import shutil
        import math
    except ImportError as e:
        print(f"ERRORE: Impossibile importare le librerie: {e}")
        input("Premi Invio per uscire...")
        return
    
    try:
        # Definizione dei percorsi
        desktop_path = Path.home() / "Desktop"
        input_folder = desktop_path / "input"
        output_folder = desktop_path / "output"
        images_folder = input_folder / "immagini"
        
        # Verifica esistenza delle cartelle e file necessari
        required_paths = [
            input_folder,
            output_folder,
            images_folder,
            input_folder / "DataEntry.xlsx",
            input_folder / "Arianna.xlsx",
            input_folder / "Template.xlsx"
        ]
        
        for path in required_paths:
            if not path.exists():
                raise FileNotFoundError(f"Percorso mancante: {path}")
        
        print("Tutti i file e cartelle necessari sono presenti.")
        
        # Apertura del file DataEntry
        print("Apertura file DataEntry...")
        dataentry_df = pd.read_excel(input_folder / "DataEntry.xlsx")
        
        # Verifica presenza delle colonne necessarie
        required_columns = ['nome file', 'anno accademico', 'numero di protocollo', 'tipo protocollo']
        for col in required_columns:
            if col not in dataentry_df.columns:
                raise ValueError(f"Colonna '{col}' non trovata in DataEntry")
        
        # Generazione elenco E1
        print("Generazione elenco E1...")
        dataentry_df['concatenazione'] = dataentry_df['numero di protocollo'].astype(str) + dataentry_df['tipo protocollo'].astype(str)
        E1 = dataentry_df[['concatenazione', 'nome file']].copy()
        
        # Memorizzazione costante K1
        K1 = dataentry_df['anno accademico'].iloc[0]
        print(f"Costante K1 (anno accademico): {K1}")
        
        # Calcolo numero iterazioni V1
        unique_values = E1['concatenazione'].nunique()
        V1 = math.ceil(unique_values / 100)
        print(f"Numero iterazioni V1: {V1}")
        
        # Apertura file Arianna
        print("Apertura file Arianna...")
        arianna_df = pd.read_excel(input_folder / "Arianna.xlsx")
        
        # Verifica presenza delle colonne necessarie in Arianna
        if 'id' not in arianna_df.columns or 'numerazione' not in arianna_df.columns:
            raise ValueError("Colonne 'id' o 'numerazione' non trovate in Arianna")
        
        # Creazione dizionario per lookup Arianna
        arianna_lookup = dict(zip(arianna_df['numerazione'], arianna_df['id']))
        
        # Ottenimento valori univoci per E2
        E2 = E1['concatenazione'].unique().tolist()
        
        # Iterazioni principali
        for iteration in range(1, V1 + 1):
            print(f"\n--- Iterazione {iteration} di {V1} ---")
            
            # Nome file per questa iterazione
            N1 = f"{K1}_{iteration}"
            print(f"Nome file: {N1}")
            
            # Caricamento template
            template_path = input_folder / "Template.xlsx"
            
            # Lettura di tutti i fogli del template
            template_sheets = pd.read_excel(template_path, sheet_name=None)
            
            # Verifica presenza dei fogli necessari
            if 'Collezione' not in template_sheets or 'Parte di collezione' not in template_sheets:
                raise ValueError("Fogli 'Collezione' o 'Parte di collezione' non trovati nel Template")
            
            collezione_df = template_sheets['Collezione'].copy()
            parte_collezione_df = template_sheets['Parte di collezione'].copy()
            
            # Calcolo range per questa iterazione
            start_idx = (iteration - 1) * 100
            end_idx = min(iteration * 100, len(E2))
            current_E2_values = E2[start_idx:end_idx]
            
            print(f"Elaborazione valori da {start_idx} a {end_idx-1} ({len(current_E2_values)} valori)")
            
            # Compilazione foglio Collezione
            print("Compilazione foglio Collezione...")
            
            # Assicurarsi che ci siano abbastanza righe nel DataFrame
            while len(collezione_df) < len(current_E2_values) + 1:
                collezione_df = pd.concat([collezione_df, pd.DataFrame([{}])], ignore_index=True)
            
            # Inserimento valori in colonna C "Segnatura/ID"
            for i, value in enumerate(current_E2_values):
                segnatura_id = f"{K1}_{value}"
                collezione_df.at[i + 1, 'Segnatura/ID'] = segnatura_id
                
                # Compilazione colonna E "Arianna ID"
                if value in arianna_lookup:
                    collezione_df.at[i + 1, 'Arianna ID'] = arianna_lookup[value]
                else:
                    print(f"Attenzione: valore {value} non trovato in Arianna")
            
            # Compilazione foglio "Parte di collezione"
            print("Compilazione foglio Parte di collezione...")
            
            # Ottenimento valori corrispondenti da E1
            current_segnature = [f"{K1}_{val}" for val in current_E2_values]
            matching_rows = E1[E1['concatenazione'].isin(current_E2_values)].copy()
            
            # Aggiunta della segnatura con K1
            matching_rows['segnatura_completa'] = K1 + "_" + matching_rows['concatenazione']
            
            # Assicurarsi che ci siano abbastanza righe
            while len(parte_collezione_df) < len(matching_rows) + 1:
                parte_collezione_df = pd.concat([parte_collezione_df, pd.DataFrame([{}])], ignore_index=True)
            
            # Compilazione delle colonne
            for i, (_, row) in enumerate(matching_rows.iterrows()):
                parte_collezione_df.at[i + 1, 'Segnatura/ID'] = row['segnatura_completa']
                parte_collezione_df.at[i + 1, 'Nome'] = row['nome file']
                parte_collezione_df.at[i + 1, 'A'] = f"/{N1}/{row['nome file']}"
            
            # Aggiornamento dei fogli nel dizionario
            template_sheets['Collezione'] = collezione_df
            template_sheets['Parte di collezione'] = parte_collezione_df
            
            # Salvataggio del file Excel
            output_file_path = output_folder / f"{N1}.xlsx"
            print(f"Salvataggio file: {output_file_path}")
            
            with pd.ExcelWriter(output_file_path, engine='openpyxl') as writer:
                for sheet_name, df in template_sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Creazione sottocartella e copia immagini
            print("Creazione sottocartella e copia immagini...")
            subfolder_path = output_folder / N1
            subfolder_path.mkdir(exist_ok=True)
            
            # Ottenimento lista file immagini da copiare
            images_to_copy = matching_rows['nome file'].unique()
            copied_count = 0
            missing_images = []
            
            for image_name in images_to_copy:
                source_image_path = images_folder / image_name
                if source_image_path.exists():
                    destination_path = subfolder_path / image_name
                    if not destination_path.exists():  # Evita duplicati
                        shutil.copy2(source_image_path, destination_path)
                        copied_count += 1
                else:
                    missing_images.append(image_name)
            
            print(f"Copiate {copied_count} immagini")
            if missing_images:
                print(f"Attenzione: {len(missing_images)} immagini non trovate: {missing_images[:5]}{'...' if len(missing_images) > 5 else ''}")
        
        print(f"\nElaborazione completata con successo!")
        print(f"Creati {V1} file Excel e relative cartelle di immagini")
        
    except FileNotFoundError as e:
        print(f"ERRORE: {e}")
    except ValueError as e:
        print(f"ERRORE: {e}")
    except Exception as e:
        print(f"ERRORE imprevisto: {e}")
        import traceback
        traceback.print_exc()
    
    # Pausa finale per permettere di leggere i messaggi
    input("\nPremi Invio per uscire...")

if __name__ == "__main__":
    main()