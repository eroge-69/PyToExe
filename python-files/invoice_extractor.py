import json
import tkinter as tk
from tkinter import filedialog, scrolledtext, ttk, messagebox
import re
from typing import Dict, List, Tuple
import os
from datetime import datetime
from pdfrw import PdfReader, PdfWriter, PageMerge
import shutil
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
import fitz
import sys
class InvoiceExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Générateur de Factures PDF")
        self.root.geometry("500x100")
        
        # Variables pour stocker les données
        self.structure = {}
        self.extracted_data = {}
        self.current_content = ""
        
        self.setup_ui()
        self.load_structure()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame pour les boutons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=0, column=0, pady=(0, 20), sticky=(tk.W, tk.E))
        button_frame.columnconfigure(1, weight=1)
        
        # Boutons
        self.select_button = ttk.Button(
            button_frame,
            text="Sélectionner Facture (.txt)",
            command=self.select_file,
            width=25
        )
        self.select_button.grid(row=0, column=0, padx=(0, 10))

        # Label de statut
        self.status_label = ttk.Label(button_frame, text="Prêt à traiter une facture", foreground="blue")
        self.status_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        # Progress Bar
        self.progress = ttk.Progressbar(button_frame, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=1, column=0, columnspan=4, pady=10)        
        # Configuration du redimensionnement
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
    def load_structure(self):
        """Charge la structure JSON améliorée"""
        default_structure = {
            "ANCHOR": "* * * D U P L I C A T A * * *",
            "PAGE_STRUCTURE": {
                "page": {
                    "pattern": r"Page:\s*(\d+)",
                    "allow_multiple": True
                },
                "date_time": {
                    "pattern": r"DATE:\s*(.+)",
                    "allow_multiple": False
                }
            },
            "HEADER": {
                "invoice_number": {
                    "pattern": r"^([A-Z]{2}\d{6})\s+",
                    "line_contains": ["FH", "FL", "FEX", "FD", "PR", "AD", "AH", "AL", "AE"]
                },
                "invoice_date": {
                    "pattern": r"(\d{2}/\d{2}/\d{2})",
                    "context": "after_invoice_number"
                },
                "order_number": {
                    "pattern": r"N°\s*CO:\s*([A-Z]{2}\d{6})",
                    "alternative_pattern": r"([A-Z]{2}\d{6})"
                },
                "code_client": {
                    "pattern": r"(\d{6})",
                    "position": "right_side"
                },
                "reference_numbers": {
                    "pattern": r"(LP\d{6}/BL\d{6})",
                    "alternative_pattern": r"(LP\d{6})"
                },
                "offer_number": {
                    "pattern": r"N°\s*Offre:\s*([A-Z0-9]+)"
                },
                "client_details": {
                    "lines_after_anchor": [3, 4, 5, 6],
                    "exclude_patterns": [r"^\s*$", r"Page:", r"DATE:", r"^\d{8,}", r"\* \* \*"]
                },
                "identification_code": {
                    "pattern": r"(\d{6}[A-Z]/[A-Z]/[A-Z]/\d{3})"
                }
            },
            "PRODUCTS": {
                "product_line_pattern": r"^(\d{9})\s+(.+?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)%?\s*$",
                "alternative_extraction": True
            },
            "TOTALS": {
                "patterns": {
                    "total_gross": r"MONTANT BRUT:\s*([\d,.]+)",
                    "total_net_ht": r"TOTAL NET HT:\s*([\d,.]+)",
                    "total_vat": r"TOTAL TVA\s*:\s*([\d,.]+)",
                    "stamp_duty": r"TIMBRE\s*:\s*([\d,.]+)",
                    "total_due": r"NET A PAYER\s*:\s*([\d,.]+)",
                    "amount_in_words": {
                        "start_pattern": r"ARRETEE LA PRESENTE FACTURE A LA SOMME DE",
                        "extract_next_line": True
                    }
                }
            }
        }
        
        try:
            if os.path.exists('structure.json'):
                with open('structure.json', 'r', encoding='utf-8') as f:
                    self.structure = json.load(f)
            else:
                self.structure = default_structure
        except Exception as e:
            print(f"Erreur lors du chargement de structure.json: {e}")
            self.structure = default_structure
            
    def select_file(self):
        file_paths = filedialog.askopenfilenames(
            title="Sélectionner un ou plusieurs fichiers de facture",
            filetypes=[("Fichiers texte", "*.txt"), ("Tous les fichiers", "*.*")]
        )

        if not file_paths:
            return

        total_steps = len(file_paths) * 100
        self.progress["maximum"] = total_steps
        self.progress["value"] = 0
        self.root.update()

        for idx, file_path in enumerate(file_paths):
            try:
                self.process_file(file_path)
                self.generate_pdf_invoice(sub_progress_steps=100)
                self.root.update()
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de traiter le fichier:\n{file_path}\n\n{str(e)}")

        self.progress["value"] = total_steps
        self.status_label.config(text=f"{len(file_paths)} factures PDF générées avec succès.", foreground="green")

    def process_file(self, file_path: str) -> Dict:
        """Traite le fichier de facture avec extraction améliorée"""
        content = self.read_file_with_encoding(file_path)
        self.current_content = content
        
        # Séparation des pages
        pages = content.split('\f') if '\f' in content else [content]
        
        # Initialisation des données extraites
        self.extracted_data = {
            'PAGE_STRUCTURE': {},
            'HEADER': {},
            'PRODUCTS': [],
            'TOTALS': {}
        }
        
        # Extraction améliorée
        self.extract_page_structure_improved(pages)
        self.extract_header_improved(pages[0])
        self.extract_products_improved(pages)
        self.extract_totals_improved(content)
        
        return self.extracted_data
        
    def read_file_with_encoding(self, file_path: str) -> str:
        """Lit le fichier avec gestion des différents encodages"""
        encodings = ['utf-8', 'ISO-8859-1', 'cp1252', 'latin-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue
        
        raise Exception("Impossible de lire le fichier avec les encodages supportés")
        
    def extract_page_structure_improved(self, pages: List[str]):
        """Extraction améliorée de la structure de page"""
        page_numbers = []
        date_time = ""
        
        for page in pages:
            page_match = re.search(r'Page:\s*(\d+)', page)
            if page_match:
                page_numbers.append(page_match.group(1))
            
            if not date_time:
                date_match = re.search(r'DATE:\s*(.+)', page)
                if date_match:
                    date_time = date_match.group(1).strip()
        
        self.extracted_data['PAGE_STRUCTURE']['pages'] = page_numbers
        if date_time:
            self.extracted_data['PAGE_STRUCTURE']['date_time'] = date_time
            
    def extract_header_improved(self, first_page: str):
        """Extraction améliorée de l'en-tête (sans dépendance obligatoire à D U P L I C A T A)"""
        lines = first_page.split('\n')

        anchor_line = -1
        for i, line in enumerate(lines):
            if "* * * D U P L I C A T A * * *" in line:
                anchor_line = i
                break

        # Fallback: use line after 'DATE:' if DUPLICATA not found
        if anchor_line == -1:
            for i, line in enumerate(lines):
                if "DATE:" in line:
                    anchor_line = i
                    break

        # If no anchor found, use beginning of the page as fallback
        search_start = anchor_line + 1 if anchor_line != -1 else 0
        search_end = min(search_start + 15, len(lines))

        client_details = []

        for i in range(search_start, search_end):
            line = lines[i].strip()

            if (not line or 'Page:' in line or 'DATE:' in line or '* * *' in line):
                continue

            # Main header line
            main_line_pattern = r'^([A-Z]{2}\d{6})\s+(\d{2}/\d{2}/\d{2})\s+N°\s*CO:\s*([A-Z]{2}\d{6})\s+(\d{6})'
            main_match = re.match(main_line_pattern, line)
            if main_match:
                self.extracted_data['HEADER']['invoice_number'] = main_match.group(1)
                self.extracted_data['HEADER']['invoice_date'] = main_match.group(2)
                self.extracted_data['HEADER']['order_number'] = main_match.group(3)
                self.extracted_data['HEADER']['code_client'] = main_match.group(4)

            if not self.extracted_data['HEADER'].get('invoice_number'):
                invoice_match = re.search(r'^([A-Z]{2}\d{6})', line)
                if invoice_match:
                    self.extracted_data['HEADER']['invoice_number'] = invoice_match.group(1)
                    date_match = re.search(r'(\d{2}/\d{2}/\d{2})', line)
                    if date_match:
                        self.extracted_data['HEADER']['invoice_date'] = date_match.group(1)

            if not self.extracted_data['HEADER'].get('order_number'):
                order_match = re.search(r'N°\s*CO:\s*([A-Z]{2}\d{6})', line)
                if order_match:
                    self.extracted_data['HEADER']['order_number'] = order_match.group(1)

            if not self.extracted_data['HEADER'].get('code_client'):
                id_match = re.search(r'([A-Z]{2}\d{6})\s+(\d{6})', line)
                if id_match:
                    self.extracted_data['HEADER']['code_client'] = id_match.group(2)

            if not self.extracted_data['HEADER'].get('reference_numbers'):
                ref_match = re.search(r'(LP\d{6}/BL\d{6})', line)
                if ref_match:
                    self.extracted_data['HEADER']['reference_numbers'] = ref_match.group(1)

            if not self.extracted_data['HEADER'].get('offer_number'):
                offer_match = re.search(r'N°\s*Offre:\s*([A-Z0-9]+)', line)
                if offer_match:
                    self.extracted_data['HEADER']['offer_number'] = offer_match.group(1)

            # Add client details lines if not starting with known patterns
            if (not re.match(r'^[A-Z]{2}\d{6}', line)) and ("Offre" not in line):
                client_details.append(line)

        client_details = '\n'.join(client_details)
        if "Tél:" not in client_details:
            client_details += "\nTél: 72 462 188    Fax: 72 462 833"

        offer_number = self.extracted_data['HEADER'].get('offer_number', '')
        if offer_number:
            client_details += f"\nN° Offre:{offer_number}"

        self.extracted_data['HEADER']['client_details'] = client_details.strip()

    def extract_products_improved(self, pages: List[str]):
        """Extraction améliorée des produits"""
        for page in pages:
            lines = page.split('\n')
            
            for line in lines:
                line_stripped = line.strip()
                
                if re.match(r'^\d{9}', line_stripped):
                    product = {}
                    
                    pattern = r'^(\d{9})\s+(.+?)\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)%?\s*$'
                    match = re.match(pattern, line_stripped)
                    
                    if match:
                        product['product_code'] = match.group(1)
                        product['product_name'] = match.group(2).strip()
                        product['quantity'] = match.group(3)
                        product['unit_price'] = match.group(4)
                        product['line_total'] = match.group(5)
                        product['vat_rate'] = match.group(6) + '%'
                    else:
                        parts = line_stripped.split()
                        if len(parts) >= 3:
                            product['product_code'] = parts[0]
                            
                            text_parts = []
                            numeric_parts = []
                            
                            for part in parts[1:]:
                                if re.match(r'^\d+\.?\d*$', part) or part.endswith('%'):
                                    numeric_parts.append(part)
                                else:
                                    text_parts.append(part)
                            
                            if text_parts:
                                product['product_name'] = ' '.join(text_parts)
                            
                            if len(numeric_parts) >= 3:
                                product['quantity'] = numeric_parts[0]
                                product['unit_price'] = numeric_parts[1]
                                product['line_total'] = numeric_parts[2]
                                
                                for part in numeric_parts:
                                    if part.endswith('%'):
                                        product['vat_rate'] = part
                                        break
                                    elif part in ['7.0', '18.0', '19.0', '6.0']:
                                        product['vat_rate'] = part + '%'
                                        break
                    
                    if not product.get('product_name'):
                        name_match = re.search(r'^\d{9}\s+(.+?)\s+\d+\s+[\d.]+', line_stripped)
                        if name_match:
                            product['product_name'] = name_match.group(1).strip()
                    
                    if not product.get('vat_rate'):
                        vat_match = re.search(r'([\d.]+)%\s*$', line_stripped)
                        if vat_match:
                            product['vat_rate'] = vat_match.group(1) + '%'
                    
                    if product and product.get('product_code'):
                        self.extracted_data['PRODUCTS'].append(product)
                        
    def extract_totals_improved(self, content: str):
        """Extraction améliorée des totaux"""
        lines = content.split('\n')
        
        patterns = {
            'total_gross': r'MONTANT BRUT:\s*([\d,.]+)',
            'total_net_ht': r'TOTAL NET HT:\s*([\d,.]+)',
            'total_vat': r'TOTAL TVA\s*:\s*([\d,.]+)',
            'stamp_duty': r'TIMBRE\s*:\s*([\d,.]+)',
            'total_due': r'NET A PAYER\s*:\s*([\d,.]+)'
        }
        
        for field, pattern in patterns.items():
            for line in lines:
                match = re.search(pattern, line)
                if match:
                    self.extracted_data['TOTALS'][field] = match.group(1)
                    break
        
        # Extraction du montant en lettres
        for i, line in enumerate(lines):
            if "ARRETEE LA PRESENTE FACTURE A LA SOMME DE" in line:
                if i + 1 < len(lines):
                    amount_words = lines[i + 1].strip()
                    if amount_words:
                        self.extracted_data['TOTALS']['amount_in_words'] = amount_words
                break
    
    def generate_pdf_invoice(self, sub_progress_steps=100):
        if not self.extracted_data:
            return

        if getattr(sys, 'frozen', False):
            current_dir = os.path.dirname(sys.executable)
        else:
            current_dir = os.path.dirname(os.path.abspath(__file__))
        factures_dir = os.path.join(current_dir, "factures")
        if not os.path.exists(factures_dir):
            os.makedirs(factures_dir)

        template_path = os.path.join(current_dir, "template.pdf")
        if not os.path.exists(template_path):
            messagebox.showerror("Erreur", f"template.pdf est manquant dans {current_dir}")
            return

        invoice_number = self.extracted_data.get('HEADER', {}).get('invoice_number', 'UNKNOWN')
        output_pdf = os.path.join(factures_dir, f"{invoice_number}.pdf")

        header = self.extracted_data.get('HEADER', {})
        totals = self.extracted_data.get('TOTALS', {})
        page_structure = self.extracted_data.get('PAGE_STRUCTURE', {})

        products = self.extracted_data['PRODUCTS']
        products_per_page = 10
        total_pages = max(1, (len(products) + products_per_page - 1) // products_per_page)

        template_doc = fitz.open(template_path)
        template_page = template_doc[0]
        output_doc = fitz.open()

        for page_num in range(total_pages):
            new_page = output_doc.new_page(width=template_page.rect.width, height=template_page.rect.height)
            new_page.show_pdf_page(new_page.rect, template_doc, 0)
            if page_num < total_pages - 1:
                rect_height = 100
                rect = fitz.Rect(0, new_page.rect.height - rect_height, new_page.rect.width, new_page.rect.height)
                new_page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))

            replacements = {
                '{{invoice_number}}': header.get('invoice_number', ''),
                '{{order_number }}': header.get('order_number', ''),
                '{{reference_numbers}}': header.get('reference_numbers', ''),
                '{{code_client }}': header.get('code_client', ''),
                '{{invoice_date}}': header.get('invoice_date', ''),
                '{{date_time}}': page_structure.get('date_time', ''),
                '{{pages}}': str(page_num + 1),
            }

            start_idx = page_num * products_per_page
            end_idx = min(start_idx + products_per_page, len(products))
            products_on_page = products[start_idx:end_idx]

            for i in range(10):
                if i < len(products_on_page):
                    prod = products_on_page[i]
                    replacements[f'{{{{product_code_{i}}}}}'] = prod.get('product_code', '')
                    replacements[f'{{{{product_name _{i}}}}}'] = prod.get('product_name', '')
                    replacements[f'{{{{quantity_{i}}}}}'] = prod.get('quantity', '')
                    replacements[f'{{{{unit_price _{i}}}}}'] = prod.get('unit_price', '')
                    replacements[f'{{{{line_total_{i}}}}}'] = prod.get('line_total', '')
                    replacements[f'{{{{vat_rate_{i}}}}}'] = prod.get('vat_rate', '')
                else:
                    replacements[f'{{{{product_code_{i}}}}}'] = ''
                    replacements[f'{{{{product_name _{i}}}}}'] = ''
                    replacements[f'{{{{quantity_{i}}}}}'] = ''
                    replacements[f'{{{{unit_price _{i}}}}}'] = ''
                    replacements[f'{{{{line_total_{i}}}}}'] = ''
                    replacements[f'{{{{vat_rate_{i}}}}}'] = ''

            if page_num == total_pages - 1:
                replacements.update({
                    '{{total_gross}}': totals.get('total_gross', ''),
                    '{{total_net_ht}}': totals.get('total_net_ht', ''),
                    '{{total_vat }}': totals.get('total_vat', ''),
                    '{{stamp_duty}}': totals.get('stamp_duty', ''),
                    '{{total_due}}': totals.get('total_due', ''),
                    '{{amount_in_words}}': totals.get('amount_in_words', ''),
                })
            else:
                for key in ['{{total_gross}}', '{{total_net_ht}}', '{{total_vat }}',
                            '{{stamp_duty}}', '{{total_due}}', '{{amount_in_words}}']:
                    replacements[key] = ''

            client_details = header.get('client_details', '').strip()
            if client_details:
                client_details_lines = client_details.split('\n')
                for i, line in enumerate(client_details_lines):
                    placeholder = f'{{{{client_details_{i}}}}}'
                    replacements[placeholder] = line.strip()
                replacements['{{client_details}}'] = client_details.replace('\n', ' ')
            else:
                replacements['{{client_details}}'] = ''

            self.replace_pdf_placeholders(new_page, replacements)

            # Update progress smoothly within sub-step
            self.progress.step(sub_progress_steps / total_pages)
            self.root.update()

        output_doc.save(output_pdf)
        template_doc.close()
        output_doc.close()

    def replace_pdf_placeholders(self, page, replacements):
        for placeholder, value in replacements.items():
            if not value:
                value = ""
            text_instances = page.search_for(placeholder)
            for inst in text_instances:
                rect = fitz.Rect(inst.x0, inst.y0, inst.x1, inst.y1)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                x,y=inst[:2]
                y+=7
                page.insert_text((x,y), str(value), fontsize=8, fontname="helv", color=(0, 0, 0))
        
    def run(self):
        """Lance l'application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = InvoiceExtractor()
    app.run()