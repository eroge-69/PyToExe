import pandas as pd

# Creiamo un dizionario con i turni
turni = {
    "Giorno": ["Martedì", "Mercoledì", "Giovedì", "Giovedì", "Giovedì", "Giovedì", "Giovedì", "Venerdì", "Venerdì", "Venerdì", "Venerdì", "Venerdì", "Sabato", "Sabato", "Sabato", "Sabato", "Sabato", "Domenica", "Domenica", "Domenica", "Domenica"],
    "Orario": ["Tutto il giorno", "15:00-21:00", "10:00-11:00", "11:00-14:30", "14:30-15:30", "15:30-17:00", "17:00-19:00", "10:00-11:00", "11:00-14:30", "14:30-15:30", "15:30-19:30", "19:30-00:00", "10:00-11:00", "11:00-14:30", "14:30-15:30", "15:30-19:30", "19:30-00:00", "09:00-11:00", "11:00-14:30", "14:30-15:30", "15:30-20:00"],
    "Presenze": ["Tu", "Tu + G", "Tu", "Tu + S", "S", "G + S", "Tu + G + S", "Tu", "Tu + G", "G", "G + S", "Tu + S", "Tu", "Tu + S", "S", "G + S", "Tu + G", "Tu", "Tu + G", "G", "Tu (con allestitore)"]
}

# Creiamo il DataFrame
df_turni = pd.DataFrame(turni)

# Salviamo in Excel
file_path = "/mnt/data/Turni_Barcolana57.xlsx"
df_turni.to_excel(file_path, index=False)
file_path
