import flet as ft
import requests
import base64
import csv
import os
from bs4 import BeautifulSoup

def main(page: ft.Page):
    page.title = "Gelbeseiten Scraper"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 30
    page.window_width = 600
    page.window_height = 600

    # UI-Elemente
    ort_field = ft.TextField(label="Ort", autofocus=True)
    branche_field = ft.TextField(label="Branche")
    filename_field = ft.TextField(label="Dateiname", value="firmen_liste")
    save_path = ft.TextField(label="Speicherort", read_only=True)
    progress_bar = ft.ProgressBar(width=400, visible=False)
    status_text = ft.Text("", style=ft.TextThemeStyle.BODY_MEDIUM)
    result_text = ft.Text("", style=ft.TextThemeStyle.BODY_LARGE)
    
    # Speicherort auswählen
    def get_save_path(e: ft.FilePickerResultEvent):
        if e.path:
            save_path.value = e.path
            page.update()
    
    file_picker = ft.FilePicker(on_result=get_save_path)
    page.overlay.append(file_picker)
    
    # Hauptfunktion für das Scraping
    async def start_scraping(e):
        # Validierung der Eingaben
        if not ort_field.value or not branche_field.value:
            status_text.value = "Bitte Ort und Branche eingeben!"
            page.update()
            return
            
        if not save_path.value:
            status_text.value = "Bitte Speicherort auswählen!"
            page.update()
            return
            
        # UI zurücksetzen
        progress_bar.visible = True
        progress_bar.value = None  # Unbestimmter Fortschritt
        status_text.value = "Starte Scraping..."
        result_text.value = ""
        page.update()
        
        try:
            # Scraping-Prozess
            base_url = "https://www.gelbeseiten.de/suche/"
            headers = {"User-Agent": "Mozilla/5.0"}
            url = base_url + branche_field.value + "/" + ort_field.value
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                status_text.value = f"Fehler: HTTP-Status {response.status_code}"
                return
                
            soup = BeautifulSoup(response.text, "html.parser")
            firmen = []
            adressen = []
            telefon_nummern = []
            firmen_url = []
            eintrag = soup.select('.mod-Treffer')

            # Firmendaten extrahieren
            for firma in eintrag:
                name_tag = firma.select_one(".mod-Treffer__name")
                adress = firma.select_one(".mod-AdresseKompakt__adress-text")
                nummer = firma.select_one(".mod-TelefonnummerKompakt")
                
                firmen.append(name_tag.get_text(strip=True) if name_tag else "")
                adressen.append(adress.get_text(strip=True) if adress else "")
                telefon_nummern.append(nummer.get_text(strip=True) if nummer else "")

            # URLs extrahieren
            for article in soup.select("article.mod-Treffer"):
                website_div = article.select_one("div.mod-WebseiteKompakt")
                url = ""
                if website_div:
                    span = website_div.select_one("span.mod-WebseiteKompakt__text")
                    if span and span.has_attr("data-webseitelink"):
                        encoded_url = span["data-webseitelink"]
                        url = base64.b64decode(encoded_url).decode("utf-8")
                firmen_url.append(url)

            # CSV-Datei speichern
            full_path = os.path.join(save_path.value, f"{filename_field.value}.csv")
            with open(full_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow(["Name", "Adresse", "Telefon", "Website"])
                for i in range(len(firmen)):
                    writer.writerow([firmen[i], adressen[i], telefon_nummern[i], firmen_url[i]])
            
            # Erfolgsmeldung
            status_text.value = ""
            result_text.value = f"Erfolgreich gespeichert!\n{len(firmen)} Einträge in:\n{full_path}"
            
        except Exception as e:
            status_text.value = f"Fehler: {str(e)}"
        finally:
            progress_bar.visible = False
            page.update()

    # UI aufbauen
    page.add(
        ft.Text("Gelbeseiten Scraper", style=ft.TextThemeStyle.HEADLINE_MEDIUM),
        ort_field,
        branche_field,
        ft.Row([
            filename_field,
            ft.ElevatedButton(
                "Speicherort wählen",
                icon=ft.Icons.FOLDER_OPEN,
                on_click=lambda _: file_picker.get_directory_path()
            )
        ]),
        save_path,
        ft.ElevatedButton(
            "CSV erstellen",
            on_click=start_scraping,
            icon=ft.Icons.START,
            style=ft.ButtonStyle(padding=20)
        ),
        progress_bar,
        status_text,
        result_text
    )

# App starten
ft.app(target=main)