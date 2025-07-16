import os
os.environ["DEARPYGUI_FORCE_SOFTWARE_RENDERING"] = "1"
import random
import pandas as pd
from datetime import datetime
import dearpygui.dearpygui as dpg
import sys
import traceback

def log_exceptions(exctype, value, tb):
    with open("error_log.txt", "w", encoding="utf-8") as f:
        traceback.print_exception(exctype, value, tb, file=f)

sys.excepthook = log_exceptions


def process_excel_callback():
    input_file = dpg.get_value("excel_file")
    name_column = dpg.get_value("name_column") or "Affecté à"
    status_column = dpg.get_value("status_column") or "État"
    date_column = dpg.get_value("date_column") or "Date de prochaine revue"
    pb_column = dpg.get_value("pb_column") or "Numéro"
    nb_wished = dpg.get_value("nb_wished")
    output_file_txt = "output_tab.txt"
    output_file_rows = dpg.get_value("output_file") or "output_rows.xlsx"
    check_date = dpg.get_value("check_date")

    dpg.set_value("status_text", "⏳ En cours...")
    dpg.configure_item("status_text", color=(255, 255, 0))
    dpg.set_value("log_output", "")

    if not input_file or not os.path.exists(input_file):
        dpg.set_value("log_output", "❌ Fichier introuvable.")
        dpg.set_value("status_text", "❌ Erreur")
        dpg.configure_item("status_text", color=(200, 0, 0))
        return

    try:
        ext = os.path.splitext(input_file)[1].lower()
        engine = "openpyxl" if ext in [".xls", ".xlsx", ".xlsm"] else \
                 "pyxlsb" if ext == ".xlsb" else \
                 "odf" if ext == ".ods" else None

        if not engine:
            dpg.set_value("log_output", "❌ Format de fichier non pris en charge.")
            dpg.set_value("status_text", "❌ Erreur")
            dpg.configure_item("status_text", color=(200, 0, 0))
            return

        df = pd.read_excel(input_file, engine=engine)

        if check_date:
            today = pd.Timestamp(datetime.today().date())
            df["Validation date"] = "✅ OK"

            mask = ~df[status_column].str.lower().isin(["résolu", "fermé"])
            date_check = pd.to_datetime(df[date_column], errors='coerce')

            df.loc[mask & ((date_check.isna()) | (date_check <= today)), "Validation date"] = "❌ Date invalide"

            invalid_count = (df["Validation date"] == "❌ Date invalide").sum()
            if invalid_count > 0:
                dpg.set_value("log_output", dpg.get_value("log_output") + f"\n⚠️ {invalid_count} ligne(s) ont une date invalide pour un statut non résolu/fermé.")

        names = df[name_column].dropna().unique()
        listNP = []
        rows_to_export = []

        for idx, name in enumerate(names, 1):
            dpg.set_value("log_output", dpg.get_value("log_output") + f"\n➡️ Traitement du nom {idx}/{len(names)}: {name}")
            listPB = df[df[name_column] == name][pb_column].dropna().unique().tolist()
            if listPB:
                if nb_wished and nb_wished.isdigit():
                    selected_kbs = random.sample(listPB, min(int(nb_wished), len(listPB)))
                else:
                    selected_kbs = listPB
                result = f"{name}: {', '.join(selected_kbs)} ;"
                listNP.append(result)
                dpg.set_value("log_output", dpg.get_value("log_output") + f"\n✅ Ajouté {len(selected_kbs)} valeurs pour '{name}'")

                for kb in selected_kbs:
                    row = df[df[pb_column] == kb].iloc[0].to_dict()
                    rows_to_export.append(row)
            else:
                dpg.set_value("log_output", dpg.get_value("log_output") + f"\n⚠️ Aucune valeur trouvée pour '{name}'")

        with open(output_file_txt, "w", encoding="utf-8", newline='') as f:
            for line in listNP:
                f.write(line + "\n")

        pd.DataFrame(rows_to_export).to_excel(output_file_rows, index=False, engine="openpyxl")
        df.to_excel("full_output_with_validation.xlsx", index=False, engine="openpyxl")

        dpg.set_value("log_output", dpg.get_value("log_output") + f"\n✅ Terminé ! Résumé dans {output_file_txt}, données dans {output_file_rows}, validation dans full_output_with_validation.xlsx")
        dpg.set_value("status_text", "✅ Terminé")
        dpg.configure_item("status_text", color=(0, 200, 0))

    except Exception as e:
        dpg.set_value("log_output", dpg.get_value("log_output") + f"\n❌ Erreur : {e}")
        dpg.set_value("status_text", "❌ Erreur")
        dpg.configure_item("status_text", color=(200, 0, 0))

# GUI setup
dpg.create_context()
dpg.create_viewport(title='Traitement Excel Audit', width=850, height=700)

with dpg.window(label="Excel Processor", width=830, height=680):
    def file_selected_callback(sender, app_data):
        dpg.set_value("excel_file", app_data['file_path_name'])

    with dpg.file_dialog(directory_selector=False, show=False, callback=file_selected_callback, tag="file_dialog_id", width=700, height=400):
        dpg.add_file_extension(".xlsx", color=(0, 255, 0, 255))
        dpg.add_file_extension(".xls")
        dpg.add_file_extension(".xlsm")
        dpg.add_file_extension(".xlsb")
        dpg.add_file_extension(".ods")

    dpg.add_button(label="Parcourir un fichier Excel", callback=lambda: dpg.show_item("file_dialog_id"))
    dpg.add_input_text(label="Chemin du fichier Excel", tag="excel_file", width=600, readonly=True)

    dpg.add_input_text(label="Colonne du nom (laisser si par défaut)", tag="name_column", width=300, default_value="Affecté à")
    dpg.add_input_text(label="Colonne du status (fermé, ouvert...)", tag="status_column", width=300, default_value="État")
    dpg.add_input_text(label="Colonne de Date de prochaine revue", tag="date_column", width=300, default_value="Date de prochaine revue")
    dpg.add_checkbox(label="Vérifier les dates de prochaine revue", tag="check_date", default_value=True)
    dpg.add_input_text(label="Colonne des n° d'incident", tag="pb_column", width=300, default_value="Numéro")
    dpg.add_input_text(label="Nombre extrait (laisser vide pour tout)", tag="nb_wished", width=200)
    dpg.add_input_text(label="Nom du fichier de sortie (.xlsx)", tag="output_file", width=400, default_value="output_rows.xlsx")
    dpg.add_button(label="Exécuter", callback=process_excel_callback)
    dpg.add_text("⏳ En attente", tag="status_text", color=(150, 150, 150))
    dpg.add_input_text(label="Log", tag="log_output", multiline=True, readonly=True, width=800, height=300)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
