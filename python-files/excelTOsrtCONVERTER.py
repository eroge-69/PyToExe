import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
import os

def convert_excel_to_srt(filepath, fps=25):
    # Leggi Excel
    df = pd.read_excel(filepath)

    # Prova a trovare le colonne giuste
    start_col = next((col for col in df.columns if "IN" in col.upper()), None)
    end_col = next((col for col in df.columns if "OUT" in col.upper()), None)
    text_col = next((col for col in df.columns if "TEXT" in col.upper()), None)

    if not start_col or not end_col or not text_col:
        raise ValueError("Colonne 'IN', 'OUT' o 'TEXT' non trovate nel file Excel!")

    subtitles = []
    for i, row in df.iterrows():
        try:
            start_time = str(row[start_col]).strip()
            end_time = str(row[end_col]).strip()
            text = str(row[text_col]).strip()

            # Salta righe vuote
            if not start_time or not end_time or not text or text.lower() == "nan":
                continue

            def to_srt_time(t):
                parts = t.split(":")
                if len(parts) == 2:  # mm:ss
                    m, s = parts
                    h = 0
                    f = 0
                elif len(parts) == 3:  # hh:mm:ss
                    h, m, s = parts
                    f = 0
                elif len(parts) == 4:  # hh:mm:ss:ff
                    h, m, s, f = parts
                else:
                    return "00:00:00,000"

                h, m, s, f = int(h), int(m), int(s), int(f)
                ms = int((f / fps) * 1000)
                return f"{h:02}:{m:02}:{s:02},{ms:03}"

            start_tc = to_srt_time(start_time)
            end_tc = to_srt_time(end_time)

            # Se fine ≤ inizio → aggiungi 2s
            if end_tc <= start_tc:
                h, m, s, ms = map(int, [start_tc[:2], start_tc[3:5], start_tc[6:8], start_tc[9:]])
                s += 2
                if s >= 60:
                    m += 1
                    s -= 60
                if m >= 60:
                    h += 1
                    m -= 60
                end_tc = f"{h:02}:{m:02}:{s:02},{ms:03}"

            subtitles.append(f"{len(subtitles)+1}\n{start_tc} --> {end_tc}\n{text}\n")

        except Exception as e:
            print(f"Errore alla riga {i}: {e}")
            continue

    # Salvataggio
    output_path = os.path.splitext(filepath)[0] + ".srt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines("\n".join(subtitles))

    return output_path


def main():
    root = tk.Tk()
    root.withdraw()

    messagebox.showinfo("Subtitle Converter", "Seleziona il file Excel da convertire in SRT")

    filepath = filedialog.askopenfilename(
        title="Seleziona il file Excel",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if not filepath:
        messagebox.showwarning("Annullato", "Nessun file selezionato.")
        return

    fps = simpledialog.askinteger("FPS", "Inserisci il frame rate (default = 25):", initialvalue=25)

    try:
        output = convert_excel_to_srt(filepath, fps)
        messagebox.showinfo("Conversione completata", f"Sottotitoli salvati in:\n{output}")
    except Exception as e:
        messagebox.showerror("Errore", f"Si è verificato un errore:\n{e}")


if __name__ == "__main__":
    main()
