# -*- coding: utf-8 -*-
import socket
import datetime
import csv
import os
import shutil
import re
import threading
import Tkinter as tk
import ttk
import tkMessageBox as messagebox

# ===================== CONFIGURATION =====================
CSV_FOLDER = r"C:\HL7\CSV_IN"
ARCHIVE_FOLDER = r"C:\HL7\archive"
HOST = '0.0.0.0'
PORT = 8080

if not os.path.exists(ARCHIVE_FOLDER):
    os.makedirs(ARCHIVE_FOLDER)
if not os.path.exists(CSV_FOLDER):
    os.makedirs(CSV_FOLDER)

# helper minimal pour convertir en unicode (Python 2)
def _to_unicode(s):
    if s is None:
        return u""
    if isinstance(s, unicode):
        return s
    # s is bytes / str
    for enc in ("utf-8", "cp1252", "latin-1"):
        try:
            return s.decode(enc)
        except:
            pass
    try:
        return unicode(s)
    except:
        try:
            return unicode(str(s), "utf-8")
        except:
            return u""

# ===================== FONCTIONS SERVEUR HL7 =====================
stop_server_event = threading.Event()

def _sanitize_filename_component(s):
    s = s.strip()
    s = re.sub(r'[^A-Za-z0-9._-]+', '_', s)
    s = re.sub(r'_+', '_', s).strip('_')
    return s or "UNKNOWN"

def _parse_hl7_ts_to_date(ts):
    ts = ts.strip()
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d%H%M", "%Y%m%d%H", "%Y%m%d"):
        try:
            return datetime.datetime.strptime(ts, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def extraire_pid(message_hl7):
    for segment in message_hl7.split('\r'):
        if segment.startswith("PID"):
            champs = segment.split('|')
            if len(champs) > 3:
                pid3 = champs[3]
                pid3_first = pid3.split('^', 1)[0] if pid3 else ""
                return pid3_first or "UNKNOWN"
    return "UNKNOWN"

def extraire_date_test(message_hl7):
    for segment in message_hl7.split('\r'):
        if segment.startswith("OBR"):
            champs = segment.split('|')
            if len(champs) > 7 and champs[7]:
                d = _parse_hl7_ts_to_date(champs[7])
                if d:
                    return d
            if len(champs) > 22 and champs[22]:
                d = _parse_hl7_ts_to_date(champs[22])
                if d:
                    return d
    patterns = [r"\b\d{14}\b", r"\b\d{12}\b", r"\b\d{10}\b", r"\b\d{8}\b"]
    for pat in patterns:
        m = re.search(pat, message_hl7)
        if m:
            d = _parse_hl7_ts_to_date(m.group(0))
            if d:
                return d
    return None

def extraire_segments_utiles(message_hl7):
    lignes = []
    for segment in message_hl7.split('\r'):
        if segment.startswith("PID") or segment.startswith("OBR"):
            lignes.append(segment.split('|'))
        elif segment.startswith("OBX"):
            champs = segment.split('|')
            champs_sans_22_26 = [val for i, val in enumerate(champs, start=1) if not (22 <= i <= 26)]
            lignes.append(champs_sans_22_26)
    return lignes

def generer_ack(message_hl7):
    control_id = ""
    for segment in message_hl7.split('\r'):
        if segment.startswith("MSH"):
            champs = segment.split('|')
            if len(champs) > 9:
                control_id = champs[9]
            break
    ack = (
        "MSH|^~\\&|RECEIVER|LAB|SENDER|HOSPITAL|{ts}||ACK^A01|{cid}|P|2.3\r"
        "MSA|AA|{cid}\r"
    ).format(ts=datetime.datetime.now().strftime("%Y%m%d%H%M%S"), cid=control_id)
    return "\x0b" + ack + "\x1c\x0d"

def start_hl7_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    s.bind((HOST, PORT))
    s.listen(5)
    print "Serveur HL7 en écoute sur {}:{}...".format(HOST, PORT)

    try:
        while not stop_server_event.is_set():
            try:
                conn, addr = s.accept()
            except socket.timeout:
                continue
            print "Connexion depuis", addr
            data = b""
            try:
                while True:
                    chunk = conn.recv(1024)
                    if not chunk:
                        break
                    data += chunk
                    if b'\x1c\x0d' in data:
                        encodings = ["utf-8", "latin-1", "cp1252"]
                        message_hl7 = None
                        for enc in encodings:
                            try:
                                message_hl7 = data.decode(enc).strip('\x0b\x1c\x0d')
                                print "Message HL7 reçu (encodage {})".format(enc)
                                break
                            except:
                                continue

                        if message_hl7 is None:
                            print "Impossible de décoder le message HL7"
                            data = b""
                            continue

                        patient_id, code_txt, patient_name = "UNKNOWN", "", ""
                        for segment in message_hl7.split('\r'):
                            if segment.startswith("PID"):
                                champs = segment.split('|')
                                if len(champs) > 3:
                                    patient_id = champs[3].strip() or "UNKNOWN"
                                if len(champs) > 4:
                                    code_txt = champs[4].strip()
                                if len(champs) > 5:
                                    patient_name = champs[5].strip()
                                break

                        date_test = extraire_date_test(message_hl7)

                        if patient_id != "UNKNOWN":
                            pid_for_name   = _sanitize_filename_component(patient_id)
                            code_for_name  = _sanitize_filename_component(code_txt)
                            name_for_name  = _sanitize_filename_component(patient_name)
                            date_for_name  = date_test or datetime.date.today().strftime("%Y-%m-%d")

                            nom_fichier = "{}_{}_{}_{}.csv".format(pid_for_name, code_for_name, name_for_name, date_for_name)
                            path_csv = os.path.join(CSV_FOLDER, nom_fichier)

                            lignes_utiles = extraire_segments_utiles(message_hl7)
                            with open(path_csv, "wb") as f:
                                writer = csv.writer(f)
                                writer.writerows(lignes_utiles)
                            print "Message enregistré dans", nom_fichier
                        else:
                            print "Message sans PID ignoré"

                        ack_msg = generer_ack(message_hl7)
                        conn.sendall(ack_msg.encode('utf-8'))
                        print "ACK envoyé"
                        data = b""
            finally:
                conn.close()
    finally:
        s.close()

# ===================== INTERFACE CSV =====================
class CSVViewer(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("KT6400_FNS /G_Khaled 0771644202")
        self.geometry("330x500")
        self.server_thread = None

        self.server_label = tk.Label(self, text="Serveur démarré sur {}:{}".format(HOST, PORT), fg="green", font=("Arial", 10, "bold"))
        self.server_label.pack(pady=5)

        self.start_server()

        self.combo = ttk.Combobox(self, width=80)
        self.combo.pack(pady=5)

        self.text = tk.Text(self, wrap="word", font=("Consolas", 10))
        self.text.pack(fill="both", expand=True)

        btn_frame = tk.Frame(self)
        btn_frame.pack(side="bottom", fill="x", pady=5)

        tk.Button(btn_frame, text="Imprimer", command=self.imprimer).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Archiver", command=self.archiver).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Archiver Tout", command=self.archiver_tout).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Import Archive", command=self.import_archive).pack(side="left", padx=5)

        self.update_file_list()
        self.combo.bind("<<ComboboxSelected>>", lambda e: self.show_csv())

    def start_server(self):
        if not self.server_thread or not self.server_thread.is_alive():
            self.server_thread = threading.Thread(target=start_hl7_server)
            self.server_thread.daemon = True
            self.server_thread.start()
            print "Serveur HL7 démarré automatiquement sur {}:{}".format(HOST, PORT)

    def update_file_list(self):
        try:
            files = [f for f in os.listdir(CSV_FOLDER) if f.lower().endswith(".csv")]
            files.sort()
            current = list(self.combo["values"])
            if files != current:
                self.combo["values"] = files
                if files and not self.combo.get():
                    self.combo.set(files[0])
                    self.show_csv()
        except Exception as e:
            print "Erreur maj fichiers:", e
        self.after(2000, self.update_file_list)

    def show_csv(self):
        filename = self.combo.get()
        if not filename:
            return
        path = os.path.join(CSV_FOLDER, filename)
        try:
            lines_raw = []
            with open(path, "rb") as f:
                reader = csv.reader(f, delimiter=",")
                for row in reader:
                    lines_raw.append(row)

            if len(lines_raw) > 5:
                lines_raw = lines_raw[:-5]

            rows = []
            for raw_row in lines_raw:
                raw = [(col.strip() if col is not None else "") for col in raw_row]
                if not any((c for c in raw if c != "")):
                    continue

                code = raw[0].upper() if len(raw) > 0 else ""

                if code == "PID":
                    if len(raw) > 6:
                        code_id = raw[3].strip() if len(raw) > 3 else ""
                        numero   = raw[4].strip() if len(raw) > 4 else ""
                        nom      = raw[5].strip() if len(raw) > 5 else ""
                        texte = "{} {} {}".format(code_id, numero, nom).strip()
                        if texte:
                            rows.append({"type": "text", "text": texte})
                    continue

                if code == "OBX":
                    if raw and raw[-1].strip().upper() == "F":
                        raw = raw[:-1]

                    test_field = raw[3] if len(raw) > 3 else ""
                    test_field = test_field.replace("^", "").strip().upper()

                    valeur = raw[5] if len(raw) > 5 else ""
                    unite = raw[6] if len(raw) > 6 else ""
                    reference = raw[7] if len(raw) > 7 else ""
                    indicateur = raw[8] if len(raw) > 8 else ""

                    if indicateur.strip().upper() == "F":
                        indicateur = ""

                    if test_field or valeur or unite or reference or indicateur:
                        rows.append({"type": "obx",
                                     "cols": [test_field, valeur, unite, reference, indicateur]})
                    continue

                added = False
                for c in raw:
                    s = c.strip()
                    m = re.search(r"\b\d{14}\b", s)
                    if m:
                        ts = m.group(0)
                        date_part = "{}/{}/{}".format(ts[6:8], ts[4:6], ts[0:4])
                        time_part = "{}:{}:{}".format(ts[8:10], ts[10:12], ts[12:14])
                        value = "\n{}                  {}\n".format(date_part, time_part)
                        rows.append({"type": "text", "text": value})
                        added = True
                        break
                if added:
                    continue

                cols_after_code = [c for c in raw[1:] if c != ""]
                value = None
                for c in cols_after_code:
                    if any(ch.isalpha() for ch in c) and len(c) > 2:
                        value = c
                        break
                if value:
                    rows.append({"type": "text", "text": value})
                    continue

                for c in cols_after_code:
                    if re.match(r"^-?\d+(\.\d+)?$", c):
                        value = c
                        break
                if value:
                    rows.append({"type": "text", "text": value})
                    continue

                if cols_after_code:
                    longest = max(cols_after_code, key=lambda s: len(s))
                    if len(longest.strip()) > 1:
                        rows.append({"type": "text", "text": longest.strip()})
                        continue

            # --- Correction alignement: conversion en unicode + monospace font ---
            col_widths = [0] * 5
            for item in rows:
                if item["type"] == "obx":
                    for i, val in enumerate(item["cols"]):
                        uval = _to_unicode(val)
                        col_widths[i] = max(col_widths[i], len(uval))

            self.text.configure(font=("Courier New", 10))  # police monospace
            self.text.delete(1.0, tk.END)

            if rows:
                for item in rows:
                    if item["type"] == "text":
                        self.text.insert(tk.END, _to_unicode(item["text"]) + "\n")
                    else:
                        cols = item["cols"]
                        parts = []
                        for i, val in enumerate(cols):
                            uval = _to_unicode(val)
                            # même si vide on ajoute des espaces pour garder la colonne
                            parts.append(uval.ljust(col_widths[i]))
                        line = "  ".join(parts).rstrip()
                        self.text.insert(tk.END, line + "\n")
            else:
                self.text.insert(tk.END, "[Aucune donnée pertinente trouvée]")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def imprimer(self):
        try:
            contenu = self.text.get(1.0, tk.END).strip()
            if not contenu:
                messagebox.showwarning("Attention", "Aucun contenu à imprimer")
                return
            temp_file = "(FNS).txt"
            with open(temp_file, "w") as f:
                f.write("\n\n\n")
                f.write("EPSP Laghouat\n")
                f.write("______________________________________\n\n")
                f.write(contenu.encode("utf-8"))
            os.startfile(temp_file, "print")
            messagebox.showinfo("Impression", "Document envoyé à l’imprimante.")
        except Exception as e:
            messagebox.showerror("Erreur impression", str(e))

    def archiver(self):
        filename = self.combo.get()
        if not filename:
            messagebox.showwarning("Attention", "Aucun fichier sélectionné")
            return
        src = os.path.join(CSV_FOLDER, filename)
        dst = os.path.join(ARCHIVE_FOLDER, filename)
        try:
            shutil.move(src, dst)
            messagebox.showinfo("Archiver", "{} déplacé vers {}".format(filename, ARCHIVE_FOLDER))
            self.combo.set("")
            self.text.delete(1.0, tk.END)
            self.update_file_list()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def archiver_tout(self):
        try:
            files = [f for f in os.listdir(CSV_FOLDER) if f.lower().endswith(".csv")]
            if not files:
                messagebox.showinfo("Archiver Tout", "Aucun fichier à archiver.")
                return
            for f in files:
                src = os.path.join(CSV_FOLDER, f)
                dst = os.path.join(ARCHIVE_FOLDER, f)
                shutil.move(src, dst)
            messagebox.showinfo("Archiver Tout", "{} fichiers déplacés vers {}".format(len(files), ARCHIVE_FOLDER))
            self.combo.set("")
            self.text.delete(1.0, tk.END)
            self.update_file_list()
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

    def import_archive(self):
        try:
            files = [f for f in os.listdir(ARCHIVE_FOLDER) if f.lower().endswith(".csv")]
            if not files:
                messagebox.showinfo("Import Archive", "Aucun fichier disponible dans l’archive.")
                return

            popup = tk.Toplevel(self)
            popup.title("Importer depuis Archive")
            popup.geometry("330x100")

            lbl = tk.Label(popup, text="Sélectionnez un fichier dans l’archive :")
            lbl.pack(pady=5)

            combo_arc = ttk.Combobox(popup, values=files, width=50)
            combo_arc.pack(pady=5)
            combo_arc.set(files[0])

            def do_import():
                filename = combo_arc.get()
                src = os.path.join(ARCHIVE_FOLDER, filename)
                dst = os.path.join(CSV_FOLDER, filename)
                try:
                    shutil.move(src, dst)
                    messagebox.showinfo("Import Archive", "{} importé dans {}".format(filename, CSV_FOLDER))
                    popup.destroy()
                    self.update_file_list()
                    self.combo.set(filename)
                    self.show_csv()
                except Exception as e:
                    messagebox.showerror("Erreur", str(e))

            tk.Button(popup, text="Importer", command=do_import).pack(pady=5)

        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# ===================== MAIN =====================
if __name__ == "__main__":
    app = CSVViewer()
    app.mainloop()