from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import xlwings as xw
from selenium.webdriver.chrome.options import Options

# === Paramètres de connexion ===
URL = "https://mgmt.data-research.fr/A4S/"
CONTEXT = "DATA"
USERNAME = "1047"
PASSWORD = "Data1047"

# === Chemin vers le fichier Excel ===
excel_path = r"C:\Users\Ardy.Andrianasolo\Documents\Sablier\SABLIER.xlsx"

# ---
# Fonction de parsing avancé avec rowspan/colspan
# ---
def parse_html_table_preserve_commas(table_tag):
    rows = table_tag.find_all("tr")
    if not rows:
        return pd.DataFrame()

    max_cols = max(sum(int(cell.get("colspan", 1)) for cell in row.find_all(["td", "th"])) for row in rows)

    grid = []
    row_spans = {}

    for row_idx, row in enumerate(rows):
        cells = row.find_all(["td", "th"])
        grid_row = []
        col_idx = 0

        while col_idx < max_cols:
            if (row_idx, col_idx) in row_spans:
                text, remaining = row_spans[(row_idx, col_idx)]
                grid_row.append(text)
                if remaining > 1:
                    row_spans[(row_idx + 1, col_idx)] = (text, remaining - 1)
                del row_spans[(row_idx, col_idx)]
                col_idx += 1
                continue

            if not cells:
                grid_row.append(None)
                col_idx += 1
                continue

            cell = cells.pop(0)
            text = cell.get_text(strip=True)
            colspan = int(cell.get("colspan", 1))
            rowspan = int(cell.get("rowspan", 1))

            for c in range(colspan):
                grid_row.append(text)
                if rowspan > 1:
                    row_spans[(row_idx + 1, col_idx)] = (text, rowspan - 1)
                col_idx += 1

        grid.append(grid_row)

    header_rows = [row for row in grid if any("th" in str(cell).lower() for cell in row)]
    data_rows = grid[len(header_rows):]

    if header_rows:
        headers = []
        for col in zip(*header_rows):
            col_parts = [part for part in col if part]
            headers.append(" > ".join(col_parts) if col_parts else "Colonne")
    else:
        headers = [f"Col_{i}" for i in range(max_cols)]

    df = pd.DataFrame(data_rows, columns=headers)
    return df

# ---
# Initialisation du navigateur
# ---
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 20)
driver.get(URL)

# Connexion
try:
    context_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
    context_input.clear()
    context_input.send_keys(CONTEXT, Keys.ENTER)
    time.sleep(2)

    all_inputs = driver.find_elements(By.TAG_NAME, "input")
    username_input = next((inp for inp in all_inputs if inp.get_attribute("type") == "text" and inp.is_displayed() and CONTEXT.lower() not in (inp.get_attribute("placeholder") or "").lower()), None)

    if not username_input:
        raise Exception("Champ identifiant introuvable")

    username_input.clear()
    username_input.send_keys(USERNAME)

    password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='password']")))
    password_input.clear()
    password_input.send_keys(PASSWORD)

    login_button = wait.until(EC.element_to_be_clickable((By.ID, "submit-btn")))
    login_button.click()
    time.sleep(5)

except Exception as e:
    print(f"⚠️ Erreur lors de la connexion : {e}")
    driver.quit()
    exit(1)

# ---
# Lecture des URLs depuis Excel
# ---
try:
    df_head = pd.read_excel(excel_path, sheet_name="HEAD", usecols="B", engine="openpyxl")
    urls = df_head.iloc[:, 0].dropna().tolist()
except FileNotFoundError:
    print(f"⚠️ Fichier Excel non trouvé : {excel_path}")
    driver.quit()
    exit(1)
except Exception as e:
    print(f"⚠️ Erreur lecture Excel : {e}")
    driver.quit()
    exit(1)

# Ouvrir Excel avec xlwings
try:
    wb = xw.Book(excel_path)
    source = wb.sheets["A"]
    destination = wb.sheets["B"]
    used_range = source.used_range
    destination.clear_contents()
    destination.range("A1").value = used_range.value
    
    front = wb.sheets["FRONT"]
    front.range("9:9").value = front.range("5:5").value

    sheet = wb.sheets["Base"]
    sheet.clear()
    sheet.range("E:AZ").number_format = "@"
except Exception as e:
    print(f"⚠️ Erreur ouverture fichier Excel : {e}")
    driver.quit()
    exit(1)

start_row = 1

# ---
# Traitement de chaque URL
# ---
for i, url in enumerate(urls, start=1):
    try:
        print(f"\n[{i}] Navigation vers : {url}")
        driver.get(url)

        wait.until(EC.frame_to_be_available_and_switch_to_it((By.ID, "ReportingFrame")))
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")

        if table:
            df_table = parse_html_table_preserve_commas(table)

            # === AJOUT 1 : Nettoyage de la 5ᵉ ligne ===
            if not df_table.empty and df_table.shape[0] >= 4:
                df_table.iloc[3] = [
                    str(val).split(" ")[0] if isinstance(val, str) else val
                    for val in df_table.iloc[3]
                ]

            # === AJOUT 2 : Nettoyage de la 1ère colonne (index 0) ===
            if not df_table.empty and df_table.shape[1] >= 1:
                df_table.iloc[:, 0] = df_table.iloc[:, 0].apply(
                    lambda x: re.sub(r"\s*\([^)]*\)\s*", "", str(x)) if pd.notna(x) else x
                )

            if not df_table.empty:
                # Extraire le ReportID de l’URL
                match = re.search(r"ViewReport/(\d+)", url)
                report_id = match.group(1) if match else None

                # Ajouter colonne ReportID
                df_table["ReportID"] = report_id
                cols = list(df_table.columns)
                cols.insert(0, cols.pop(cols.index("ReportID")))
                df_table = df_table[cols]

                # === AJOUT 3 : Colonne concaténée "Concat = ReportID ; Col1 ; Col2"
                if df_table.shape[1] >= 3:
                    df_table.insert(
                        0,
                        "Concat",
                        df_table.apply(
                            lambda row: f"{row['ReportID']}{row.iloc[1]}{row.iloc[2]}",
                            axis=1
                        )
                    )

                # Nettoyage colonnes
                df_table.columns = [
                    col if col else f"Unnamed_{i}" for i, col in enumerate(df_table.columns)
                ]
                df_table = df_table.loc[:, ~df_table.columns.duplicated()]

                num_rows, num_cols = df_table.shape
                end_col_letter = xw.utils.col_name(num_cols)
                sheet.range(f"A{start_row}").options(index=False, header=True).value = df_table

                print(f"✅ {len(df_table)} lignes ajoutées avec ReportID={report_id} à la ligne {start_row}.")
                start_row += num_rows + 2
            else:
                print("❌ Tableau trouvé mais vide.")
        else:
            print("❌ Aucun tableau trouvé sur la page.")

        driver.switch_to.default_content()

    except TimeoutException:
        print(f"⏱️ Timeout : tableau introuvable sur {url}.")
    except Exception as e:
        print(f"⚠️ Erreur pour {url} : {e}")

# ---
# Finalisation
# ---
driver.quit()

try:
    wb.save()
    print("\n✅ Données correctement écrites et sauvegardées dans Excel.")
except Exception as e:
    print(f"⚠️ Erreur à la sauvegarde du fichier Excel : {e}")
