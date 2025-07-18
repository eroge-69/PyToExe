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

def get_selected_columns(tag_prefix, all_columns):
    return [col for col in all_columns if dpg.get_value(f"{tag_prefix}_{col}")] 

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

    dpg.set_value("status_text", " En cours...")
    dpg.configure_item("status_text", color=(255, 255, 0))
    dpg.set_value("log_output", "")

    if not input_file or not os.path.exists(input_file):
        dpg.set_value("log_output", " Fichier introuvable.")
        dpg.set_value("status_text", " Erreur")
        dpg.configure_item("status_text", color=(200, 0, 0))
        return

    try:
        ext = os.path.splitext(input_file)[1].lower()
        engine = "openpyxl" if ext in [".xls", ".xlsx", ".xlsm"] else \
                 "pyxlsb" if ext == ".xlsb" else \
                 "odf" if ext == ".ods" else None

        if not engine:
            dpg.set_value("log_output", " Format de fichier non pris en charge.")
            dpg.set_value("status_text", " Erreur")
            dpg.configure_item("status_text", color=(200, 0, 0))
            return

        df = pd.read_excel(input_file,sheet_name=dpg.get_value("sheet_file1"), engine=engine)
        
        # Check for empty values in specified columns
        columns = df.columns.str.strip().tolist()

        # Collect selected columns from checkboxes
        empty_columns = []
        for col in columns:
            checkbox_tag = f"empty_columns_{col}"
            if dpg.does_item_exist(checkbox_tag) and dpg.get_value(checkbox_tag):
                empty_columns.append(col)

        # Check for empty values in selected columns
        for col in empty_columns:
            if col in df.columns:
                empty_count = df[col].isna().sum()
                if empty_count > 0:
                    dpg.set_value("log_output", dpg.get_value("log_output") + f"\n {empty_count} valeur(s) vide(s) trouvée(s) dans la colonne '{col}'.")
            else:
                dpg.set_value("log_output", dpg.get_value("log_output") + f"\n Colonne '{col}' non trouvée dans le fichier.")

        if check_date:
            today = pd.Timestamp(datetime.today().date())
            df["Validation date"] = " OK"

            mask = ~df[status_column].str.lower().isin(["résolu", "fermé"])
            date_check = pd.to_datetime(df[date_column], errors='coerce')

            df.loc[mask & ((date_check.isna()) | (date_check <= today)), "Validation date"] = " Date invalide"

            invalid_count = (df["Validation date"] == " Date invalide").sum()
            if invalid_count > 0:
                dpg.set_value("log_output", dpg.get_value("log_output") + f"\n {invalid_count} ligne(s) ont une date invalide pour un statut non résolu/fermé.")

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
        dpg.set_value("log_output", dpg.get_value("log_output") + f"\n Erreur : {e}")
        dpg.set_value("status_text", " Erreur")
        dpg.configure_item("status_text", color=(200, 0, 0))
        

def compare_files_callback():
    file1 = dpg.get_value("excel_file")
    file2 = dpg.get_value("compare_file")
    sheet1 = dpg.get_value("sheet_file1")
    sheet2 = dpg.get_value("sheet_file2")

    if not file1 or not file2 or not os.path.exists(file1) or not os.path.exists(file2):
        dpg.set_value("log_output", dpg.get_value("log_output") + "\n Un ou deux fichiers sont manquants.")
        return

    try:
        df1 = pd.read_excel(file1, sheet_name=sheet1)
        df2 = pd.read_excel(file2, sheet_name=sheet2)
        
        dpg.set_value("log_output", dpg.get_value("log_output") + "\n✅ Les fichiers ont bien été chargés")

        df1.columns = df1.columns.str.strip()
        df2.columns = df2.columns.str.strip()

        all_cols1 = df1.columns.tolist()
        all_cols1 = df2.columns.tolist()

        cols1 = get_selected_columns("cols_file1_checkboxes", all_cols1)

        df1_subset = df1[cols1].copy()
        df2_subset = df2[cols1].copy()

        min_len = min(len(df1_subset), len(df2_subset))
        df1_subset = df1_subset.iloc[:min_len].reset_index(drop=True)
        df2_subset = df2_subset.iloc[:min_len].reset_index(drop=True)

        differences = []
        for i in range(min_len):
            row1 = df1_subset.iloc[i]
            row2 = df2_subset.iloc[i]
            dpg.set_value("log_output", dpg.get_value("log_output") + f"\n Ligne '{i}' chargée .")
            if not row1.equals(row2):
                dpg.set_value("log_output", dpg.get_value("log_output") + f"\n Ligne '{i}' est differente ." )
                combined = pd.concat([row1, row2], axis=1)
                combined.columns = ['Original', 'Modified']
                combined.insert(0, 'Row', i)
                differences.append(combined)

        if differences:
            result_df = pd.concat(differences, axis=0)
            result_df.to_excel("differences_side_by_side.xlsx", index=False)
            dpg.set_value("log_output", dpg.get_value("log_output") + "\n📄 Différences enregistrées dans 'differences_side_by_side.xlsx'.")
        else:
            dpg.set_value("log_output", dpg.get_value("log_output") + "\n✅ Les fichiers sont identiques pour les colonnes sélectionnées.")

    except Exception as e:
        dpg.set_value("log_output", dpg.get_value("log_output") + f"\n Erreur lors de la comparaison : {e}")




        

# Global toggle state
hidecreds = {"value": False}


def toggle_hidecreds():
    hidecreds["value"] = not hidecreds["value"]
    new_label = "Hide" if hidecreds["value"] else "Show"
    dpg.set_item_label("toggle_button", new_label)
    if dpg.is_item_shown("preview_window"):
        dpg.hide_item("preview_window")
    else:
        dpg.show_item("preview_window")
        



def update_column_checkboxes(tag_prefix, columns):
    # First, delete all existing checkboxes under the parent tag
    if dpg.does_item_exist(tag_prefix):
        dpg.delete_item(tag_prefix, children_only=True)

    # Then, add new checkboxes
    for col in columns:
        checkbox_tag = f"{tag_prefix}_{col}"
        dpg.add_checkbox(label=col, tag=checkbox_tag, parent=tag_prefix)
x²


def on_sheet1_selected(sender, app_data):
    file1 = dpg.get_value("excel_file")
    if file1 and os.path.exists(file1):
        df = pd.read_excel(file1, sheet_name=app_data, nrows=0)
        columns = df.columns.str.strip().tolist()

        update_column_checkboxes("cols_file1_checkboxes", columns)
        dpg.delete_item("empty_columns", children_only=True)  # Clear previous checkboxes
        update_column_checkboxes("empty_columns", columns)

def on_sheet2_selected(sender, app_data):
    file2 = dpg.get_value("compare_file")
    if file2 and os.path.exists(file2):
        df = pd.read_excel(file2, sheet_name=app_data, nrows=0)
        columns = df.columns.str.strip().tolist()


dpg.create_context()
dpg.create_viewport(title='Traitement Excel Audit', width=1220, height=720)

# --- Image de fond ---
image_loaded = False
try:
    with dpg.texture_registry(show=False):
        width, height, channels, data = dpg.load_image("guibackground.png")
        dpg.add_static_texture(width, height, data, tag="bg_texture")
        image_loaded = True
except Exception as e:
    print(f"❌ Failed to load background image: {e}")

# --- Thème ---
with dpg.theme(tag="dark_blue_red_theme"):
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 40), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Text, (220, 220, 230), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Header, (90, 20, 20), category=dpg.mvThemeCat_Core)
        dpg.add_theme_color(dpg.mvThemeCol_Button, (60, 70, 100), category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5, category=dpg.mvThemeCat_Core)
        dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 6, category=dpg.mvThemeCat_Core)

# --- Callbacks ---
def file1_selected_callback(sender, app_data):
    file_path = app_data['file_path_name']
    dpg.set_value("excel_file", file_path)
    try:
        xls = pd.ExcelFile(file_path)
        sheet_names = xls.sheet_names
        dpg.configure_item("sheet_file1", items=sheet_names)
        dpg.set_value("sheet_file1", sheet_names[0])
        on_sheet1_selected(None, sheet_names[0])
    except Exception as e:
        log = dpg.get_value("log_output") or ""
        dpg.set_value("log_output", log + f"\n❌ Erreur fichier 1 : {e}")

def file2_selected_callback(sender, app_data):
    file_path = app_data['file_path_name']
    dpg.set_value("compare_file", file_path)
    try:
        xls = pd.ExcelFile(file_path)
        dpg.configure_item("sheet_file2", items=xls.sheet_names)
    except Exception as e:
        log = dpg.get_value("log_output") or ""
        dpg.set_value("log_output", log + f"\n❌ Erreur fichier 2 : {e}")

# --- File dialogs (hors fenêtres) ---
with dpg.file_dialog(directory_selector=False, show=False, callback=file1_selected_callback, tag="file_dialog_id", width=700, height=400):
    for ext in [".xlsx", ".xls", ".xlsm", ".xlsb", ".ods"]:
        dpg.add_file_extension(ext, color=(0, 255, 0, 255))

with dpg.file_dialog(directory_selector=False, show=False, callback=file2_selected_callback, tag="file_dialog_compare", width=700, height=400):
    for ext in [".xlsx", ".xls", ".xlsm", ".xlsb", ".ods"]:
        dpg.add_file_extension(ext, color=(0, 255, 0, 255))

# --- Fenêtre principale ---
with dpg.window(label="🧪 Traitement Excel Audit", width=880, height=700, pos=(10, 10)):
    dpg.bind_theme("dark_blue_red_theme")

    with dpg.collapsing_header(label="Fichier Excel", default_open=True):
        dpg.add_button(label="Parcourir un fichier Excel", callback=lambda: dpg.configure_item("file_dialog_id", show=True))
        dpg.add_input_text(label="Chemin du fichier Excel", tag="excel_file", width=600, readonly=True)

    with dpg.collapsing_header(label="⚙️ Paramètres de traitement", default_open=True):
        dpg.add_input_text(label="Colonne du nom", tag="name_column", width=300, default_value="Affecté à")
        dpg.add_input_text(label="Colonne du status", tag="status_column", width=300, default_value="État")
        dpg.add_input_text(label="Colonne de Date de prochaine revue", tag="date_column", width=300, default_value="Date de prochaine revue")
        dpg.add_checkbox(label="Vérifier les dates", tag="check_date", default_value=True)
        dpg.add_input_text(label="Colonne des n° d'incident", tag="pb_column", width=300, default_value="Numéro")
        dpg.add_text("Colonnes vides")
        dpg.add_child_window(tag="empty_columns", width=400, height=100, border=True)

    with dpg.collapsing_header(label="📤 Export & Exécution", default_open=True):
        dpg.add_input_text(label="Nombre extrait", tag="nb_wished", width=200)
        dpg.add_input_text(label="Nom du fichier de sortie", tag="output_file", width=400, default_value="output_random.xlsx")
        dpg.add_button(label="Exécuter", callback=process_excel_callback)
        dpg.add_text("⏳ En attente", tag="status_text", color=(150, 150, 150))

    with dpg.collapsing_header(label="📝 Journal de traitement", default_open=False):
        dpg.add_input_text(tag="log_output", multiline=True, readonly=True, width=830, height=300)
        dpg.add_button(label="Show", tag="toggle_button", callback=toggle_hidecreds)

# --- Fenêtre de comparaison ---
with dpg.window(label="🧪 Comparaison de fichiers", width=300, height=450, pos=(911, 30)):
    dpg.bind_theme("dark_blue_red_theme")

    dpg.add_button(label="Parcourir un deuxième fichier Excel", callback=lambda: dpg.configure_item("file_dialog_compare", show=True))
    dpg.add_text("Chemin du deuxième fichier")
    dpg.add_input_text(tag="compare_file", width=300, readonly=True)

    with dpg.collapsing_header(label="📊 Comparaison de fichiers", default_open=True):
        dpg.add_text("Feuille à utiliser (fichier 1)")
        dpg.add_combo(tag="sheet_file1", items=[], width=290, callback=on_sheet1_selected)
        dpg.add_text("Colonnes à comparer (fichier 1)")
        dpg.add_child_window(tag="cols_file1_checkboxes", width=270, height=150, border=True)
        dpg.add_text("Feuille à utiliser (fichier 2)")
        dpg.add_combo(tag="sheet_file2", items=[], width=290, callback=on_sheet2_selected)
        dpg.add_button(label="Comparer les fichiers", callback=compare_files_callback)

# --- Image preview ---
if image_loaded:
    with dpg.window(label="Made By Jules", tag="preview_window", width=300, height=250, pos=(910, 20), no_resize=True, no_move=True):
        with dpg.drawlist(width=300, height=250):
            dpg.draw_image("bg_texture", pmin=(0, 0), pmax=(300, 250))
        dpg.hide_item("preview_window")

# --- Lancement ---
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
