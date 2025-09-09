#!/usr/bin/env python3
"""
Windchill PDF extractor - CSV darabjegyzékből PDF-ek letöltése - VÉGLEGES VERZIÓ
"""

import csv
import os
import requests
import json
import re
from pathlib import Path
import logging
from urllib.parse import quote
import time

# Logging beállítás
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindchillConnector:
    def __init__(self, base_url, username, password):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.csrf_token = None
        self.authenticate()
    
    def authenticate(self):
        """Bejelentkezés és CSRF token lekérése"""
        try:
            csrf_url = f"{self.base_url}/servlet/odata/"
            headers = {
                'Content-Type': 'application/json',
                'CSRF_NONCE': 'Fetch'
            }
            
            logger.info("CSRF token lekérése...")
            response = self.session.get(csrf_url, headers=headers, 
                                     auth=(self.username, self.password))
            
            if response.status_code == 200:
                self.csrf_token = response.headers.get('CSRF_NONCE')
                logger.info("Sikeres bejelentkezés és CSRF token lekérése")
                return True
            else:
                logger.error(f"Hiba a bejelentkezés során: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Hiba az authentikáció során: {e}")
            return False
    
    def normalize_drawing_number(self, drawing_number):
        """
        Rajzszám normalizálása - eltávolítja a -A, -B, -C stb. végződéseket
        """
        # Eltávolítjuk a végéről a -betű mintázatot (pl. -A, -B, -C)
        normalized = re.sub(r'-[A-Z]$', '', drawing_number.upper())
        return normalized
    
    def search_all_documents_by_number(self, drawing_number):
        """ÖSSZES dokumentum keresése rajzszám alapján"""
        try:
            # Normalizáljuk a rajzszámot
            normalized_drawing = self.normalize_drawing_number(drawing_number)
            
            search_url = f"{self.base_url}/servlet/odata/DocMgmt/Documents"
            
            # Keresési szűrők - mind az eredeti, mind a normalizált rajzszámmal
            filters = [
                f"contains(Number,'{drawing_number}')",
                f"contains(Name,'{drawing_number}')",
                f"contains(tolower(Number),'{drawing_number.lower()}')",
                f"contains(tolower(Name),'{drawing_number.lower()}')"
            ]
            
            # Ha különbözik a normalizált verzió, akkor azt is hozzáadjuk
            if normalized_drawing != drawing_number:
                filters.extend([
                    f"contains(Number,'{normalized_drawing}')",
                    f"contains(Name,'{normalized_drawing}')",
                    f"contains(tolower(Number),'{normalized_drawing.lower()}')",
                    f"contains(tolower(Name),'{normalized_drawing.lower()}')"
                ])
            
            all_documents = []
            
            for filter_expr in filters:
                try:
                    params = {
                        '$filter': filter_expr,
                        '$select': 'ID,Number,Name,Description'
                    }
                    
                    response = self.session.get(search_url, params=params,
                                             auth=(self.username, self.password))
                    
                    if response.status_code == 200:
                        data = response.json()
                        documents = data.get('value', [])
                        
                        for doc in documents:
                            # Duplikációk elkerülése
                            if not any(existing['ID'] == doc['ID'] for existing in all_documents):
                                all_documents.append(doc)
                    
                except Exception as filter_error:
                    logger.debug(f"Keresési szűrő hiba: {filter_error}")
            
            return all_documents
                
        except Exception as e:
            logger.error(f"Hiba a keresés során {drawing_number}: {e}")
            return []
    
    def get_pdf_content_from_document(self, document_id, document_name):
        """PDF tartalom keresése és lekérése dokumentumból"""
        try:
            all_content_info = []
            
            # Primary Content ellenőrzése
            try:
                content_url = f"{self.base_url}/servlet/odata/DocMgmt/Documents('{document_id}')/PrimaryContent"
                response = self.session.get(content_url, auth=(self.username, self.password))
                
                if response.status_code == 200:
                    try:
                        content_info = response.json()
                        all_content_info.append(('Primary', content_info))
                    except json.JSONDecodeError:
                        all_content_info.append(('Primary Binary', {
                            'content': response.content,
                            'size': len(response.content)
                        }))
                        
            except Exception as e:
                logger.debug(f"Primary content hiba: {e}")
            
            # ContentItems ellenőrzése
            try:
                content_url = f"{self.base_url}/servlet/odata/DocMgmt/Documents('{document_id}')/ContentItems"
                response = self.session.get(content_url, auth=(self.username, self.password))
                
                if response.status_code == 200:
                    content_items = response.json().get('value', [])
                    for item in content_items:
                        all_content_info.append(('ContentItem', item))
                        
            except Exception as e:
                logger.debug(f"ContentItems hiba: {e}")
            
            # PDF keresése a tartalomban
            for content_type, content_info in all_content_info:
                filename = content_info.get('FileName', 'unknown')
                mime_type = content_info.get('MimeType', '')
                format_type = content_info.get('Format', '')
                
                # PDF azonosítás
                is_pdf = (
                    'pdf' in filename.lower() or
                    'pdf' in mime_type.lower() or 
                    'pdf' in format_type.lower() or
                    filename.lower().endswith('.pdf')
                )
                
                if is_pdf:
                    return content_info
            
            return None
                
        except Exception as e:
            logger.error(f"Hiba a PDF tartalom lekérésekor {document_id}: {e}")
            return None
    
    def download_file_from_url(self, download_url):
        """Fájl letöltése URL alapján"""
        try:
            response = self.session.get(download_url, auth=(self.username, self.password))
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Letöltési hiba: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Hiba a fájl letöltésekor: {e}")
            return None
    
    def find_and_download_pdf(self, drawing_number, output_path):
        """PDF keresése és letöltése"""
        # Dokumentumok keresése
        documents = self.search_all_documents_by_number(drawing_number)
        
        if not documents:
            return False
        
        # PDF keresése a dokumentumokban
        for doc in documents:
            doc_id = doc.get('ID')
            doc_name = doc.get('Name', 'N/A')
            
            # Csak PDF dokumentumokat vizsgálunk (optimalizáció)
            if 'pdf' in doc_name.lower():
                pdf_content_info = self.get_pdf_content_from_document(doc_id, doc_name)
                
                if pdf_content_info:
                    file_content = None
                    filename = pdf_content_info.get('FileName', 'unknown.pdf')
                    
                    # Letöltés
                    if 'Content' in pdf_content_info and 'URL' in pdf_content_info['Content']:
                        file_content = self.download_file_from_url(pdf_content_info['Content']['URL'])
                    elif 'content' in pdf_content_info:
                        file_content = pdf_content_info['content']
                    
                    if file_content and file_content.startswith(b'%PDF'):
                        # Fájl mentése - javított verzió a szintaxis hiba miatt
                        invalid_chars = r'[<>:"/\\|?*]'
                        safe_filename = re.sub(invalid_chars, '_', drawing_number)
                        final_filename = f"{safe_filename}.pdf"
                        file_path = output_path / final_filename
                        
                        with open(file_path, 'wb') as f:
                            f.write(file_content)
                        
                        logger.info(f"✓ PDF letöltve: {final_filename} ({len(file_content)} bytes)")
                        return True
        
        return False

class CSVProcessor:
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
    
    def extract_drawing_numbers(self):
        """Rajzszámok kinyerése a CSV-ből"""
        drawing_numbers = set()
        
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # APS- kezdetű rajzszámok keresése
                aps_matches = re.findall(r'APS-[\w\-]+', content)
                
                for match in aps_matches:
                    drawing_numbers.add(match)
                
        except Exception as e:
            logger.error(f"Hiba a CSV feldolgozás során: {e}")
            return []
        
        return sorted(list(drawing_numbers))

class WindchillPDFExtractor:
    def __init__(self, windchill_url, username, password, output_dir="downloaded_pdfs"):
        self.windchill = WindchillConnector(windchill_url, username, password)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def process_csv_and_download_all(self, csv_file_path):
        """Főfolyamat - ÖSSZES rajzszám feldolgozása"""
        start_time = time.time()
        
        # CSV feldolgozás
        processor = CSVProcessor(csv_file_path)
        drawing_numbers = processor.extract_drawing_numbers()
        
        if not drawing_numbers:
            logger.warning("Nem találhatóak rajzszámok a CSV-ben")
            return
        
        logger.info("="*80)
        logger.info("WINDCHILL PDF LETÖLTÉS - TELJES FELDOLGOZÁS")
        logger.info("="*80)
        logger.info(f"Feldolgozandó rajzszámok: {len(drawing_numbers)}")
        logger.info(f"Célmappa: {self.output_dir.absolute()}")
        logger.info(f"Kezdés: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
        
        # PDF-ek letöltése
        successful_downloads = 0
        failed_downloads = []
        
        for i, drawing_number in enumerate(drawing_numbers, 1):
            logger.info(f"[{i:2d}/{len(drawing_numbers)}] {drawing_number}")
            
            try:
                # Ellenőrizzük, hogy már létezik-e a fájl
                invalid_chars = r'[<>:"/\\|?*]'
                safe_filename = re.sub(invalid_chars, '_', drawing_number)
                expected_filename = f"{safe_filename}.pdf"
                expected_path = self.output_dir / expected_filename
                
                if expected_path.exists():
                    logger.info(f"    -> Már létezik: {expected_filename}")
                    successful_downloads += 1
                    continue
                
                success = self.windchill.find_and_download_pdf(drawing_number, self.output_dir)
                
                if success:
                    successful_downloads += 1
                else:
                    failed_downloads.append(drawing_number)
                    logger.warning(f"    -> ✗ Nem található PDF")
                    
            except Exception as e:
                logger.error(f"    -> HIBA: {e}")
                failed_downloads.append(drawing_number)
            
            # Rövid szünet a szerver terhelésének csökkentéséhez
            time.sleep(0.1)
        
        # Végleges összesítő
        end_time = time.time()
        duration = end_time - start_time
        
        logger.info("="*80)
        logger.info("VÉGSŐ EREDMÉNYEK")
        logger.info("="*80)
        logger.info(f"Feldolgozási idő: {duration:.1f} másodperc")
        logger.info(f"Összes rajzszám: {len(drawing_numbers)}")
        logger.info(f"Sikeres letöltések: {successful_downloads}")
        logger.info(f"Sikertelen letöltések: {len(failed_downloads)}")
        logger.info(f"Sikerességi arány: {(successful_downloads/len(drawing_numbers)*100):.1f}%")
        logger.info(f"Letöltött fájlok helye: {self.output_dir.absolute()}")
        
        if failed_downloads:
            logger.info(f"\nSikertelen rajzszámok ({len(failed_downloads)} db):")
            for failed in failed_downloads:
                logger.info(f"  - {failed}")
        
        logger.info("="*80)
        logger.info("BEFEJEZVE")
        logger.info("="*80)

# Használat
if __name__ == "__main__":
    # Konfiguráció
    WINDCHILL_URL = "http://windchill.alprosys.local/Windchill"
    USERNAME = "kukoricaj"
    PASSWORD = "123456Qwas"
    
    # CSV fájl bekérése
    print("="*60)
    print("WINDCHILL PDF LETÖLTŐ")
    print("="*60)
    
    while True:
        csv_file = input("Add meg a CSV fájl nevét (pl. APS-31467-121-00.csv): ").strip()
        
        if not csv_file:
            print("Kérlek adj meg egy fájlnevet!")
            continue
            
        # .csv kiterjesztés hozzáadása, ha nincs
        if not csv_file.lower().endswith('.csv'):
            csv_file += '.csv'
            
        # Ellenőrizzük, hogy létezik-e a fájl
        if not os.path.exists(csv_file):
            print(f"HIBA: A '{csv_file}' fájl nem található!")
            print("Kérlek ellenőrizd a fájlnevet és hogy a fájl a szkript könyvtárában van-e.")
            continue
        else:
            print(f"CSV fájl megtalálva: {csv_file}")
            break
    
    try:
        extractor = WindchillPDFExtractor(WINDCHILL_URL, USERNAME, PASSWORD)
        
        # TELJES feldolgozás
        extractor.process_csv_and_download_all(csv_file)
        
        input("\nNyomj ENTER-t a kilépéshez...")
        
    except KeyboardInterrupt:
        logger.info("Felhasználó által megszakítva")
    except Exception as e:
        logger.error(f"Fő hiba: {e}")
        import traceback
        logger.error(traceback.format_exc())
        input("\nNyomj ENTER-t a kilépéshez...")