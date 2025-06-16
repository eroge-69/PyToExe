import json
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Optional
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import os

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrelloDataExtractor:
    """Clase para extraer y procesar datos de Trello"""
    
    def __init__(self):
        # Patrón actualizado para extraer el número de ticket
        self.ticket_pattern = re.compile(r'-0000-(\d+)-')
        self.alternative_pattern = re.compile(r'-(\d+)-.*?(\d+)-')
        self.general_pattern = re.compile(r'-(?!0000)(\d{4})-')
    
    def extract_ticket_number(self, card_name: str) -> Optional[str]:
        """Extrae el número de ticket de la tarjeta basado en su nombre."""
        if not card_name:
            return None
        
        # Método 1: Buscar patrón específico -0000-XXXX-
        match = self.ticket_pattern.search(card_name)
        if match:
            return match.group(1)
        
        # Método 2: Buscar el segundo número en la secuencia
        match = self.alternative_pattern.search(card_name)
        if match:
            return match.group(2)
        
        # Método 3: Buscar cualquier número de 4 dígitos que no sea 0000
        match = self.general_pattern.search(card_name)
        if match:
            return match.group(1)
        
        # Método 4: Buscar todos los números y tomar el segundo válido
        numbers = re.findall(r'\d+', card_name)
        if len(numbers) >= 2:
            filtered_numbers = [num for num in numbers if num != '0000' and len(num) >= 3]
            if filtered_numbers:
                return filtered_numbers[0]
        
        return None
    
    def process_card_action(self, action: Dict, board_name: str) -> Optional[Dict]:
        """Procesa una acción individual y extrae información de la tarjeta"""
        action_data = action.get('data', {})
        card_info = action_data.get('card', {})
        list_info = action_data.get('list', {})
        
        if not card_info or 'id' not in card_info:
            return None
        
        card_name = card_info.get('name', 'Sin nombre')
        member_creator = action_data.get('memberCreator', {})
        
        return {
            'ID': card_info['id'],
            'Nombre_Tarjeta': card_name,
            'Lista_Actual': list_info.get('name', 'Sin lista'),
            'Número_Ticket': self.extract_ticket_number(card_name),
            'Fecha_Ultima_Actividad': action.get('date', ''),
            'Tipo_Ultima_Accion': action.get('type', ''),
            'Tablero': board_name,
            'Miembro_Creador': member_creator.get('fullName', 'Sin nombre'),
            'Avatar_Creador': member_creator.get('avatarUrl', ''),
            'Acción': action.get('type', ''),
            'Fecha_Creación': card_info.get('dateLastActivity', ''),
            'Descripción': card_info.get('desc', ''),
            'Lista_ID': list_info.get('id', ''),
            'Lista_Nombre': list_info.get('name', '')
        }
    
    def extract_trello_data(self, json_file_path: Path) -> pd.DataFrame:
        """Extrae información de tarjetas de un JSON de Trello"""
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except UnicodeDecodeError:
            try:
                with open(json_file_path, 'r', encoding='latin-1') as file:
                    data = json.load(file)
            except Exception as e:
                raise ValueError(f"Error de codificación: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error al decodificar JSON: {e}")
        
        board_name = data.get('name', 'Sin nombre')
        actions = data.get('actions', [])
        
        if not actions:
            return pd.DataFrame()
        
        unique_cards = {}
        
        for action in actions:
            card_data = self.process_card_action(action, board_name)
            if card_data:
                card_id = card_data['ID']
                if card_id not in unique_cards:
                    unique_cards[card_id] = card_data
        
        df = pd.DataFrame(list(unique_cards.values()))
        
        if not df.empty and 'Fecha_Ultima_Actividad' in df.columns:
            df['Fecha_Ultima_Actividad'] = pd.to_datetime(
                df['Fecha_Ultima_Actividad'], 
                errors='coerce'
            ).dt.strftime('%Y-%m-%d %H:%M:%S')
        
        return df

class ExcelExporter:
    """Clase para exportar datos a Excel con formato"""
    
    @staticmethod
    def save_to_excel(df: pd.DataFrame, output_file: Path) -> None:
        """Guarda el DataFrame en un archivo Excel con formato"""
        
        if df.empty:
            raise ValueError("No hay datos para exportar")
        
        try:
            with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Tarjetas_Trello', index=False)
                
                workbook = writer.book
                worksheet = writer.sheets['Tarjetas_Trello']
                
                for column in worksheet.columns:
                    column_letter = column[0].column_letter
                    max_length = max(
                        len(str(cell.value)) if cell.value else 0 
                        for cell in column
                    )
                    adjusted_width = min(max(max_length + 2, 12), 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
        except PermissionError:
            raise PermissionError(f"No se puede escribir el archivo. Cierra Excel si está abierto.")
        except Exception as e:
            raise Exception(f"Error al guardar archivo: {e}")

class TrelloExtractorApp:
    """Aplicación principal con interfaz gráfica"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Extractor de Datos de Trello v1.0")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        
        # Configurar icon si existe
        try:
            if hasattr(sys, '_MEIPASS'):
                icon_path = os.path.join(sys._MEIPASS, 'icon.ico')
            else:
                icon_path = 'icon.ico'
            self.root.iconbitmap(icon_path)
        except:
            pass  # Sin icono si no existe
        
        self.json_file_path = tk.StringVar()
        self.output_file_path = tk.StringVar()
        self.extractor = TrelloDataExtractor()
        self.exporter = ExcelExporter()
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        
        # Configurar estilo
        style = ttk.Style()
        style.theme_use('clam')
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_label = tk.Label(
            main_frame, 
            text="🔄 Extractor de Datos de Trello",
            font=("Segoe UI", 18, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 20))
        
        subtitle_label = tk.Label(
            main_frame,
            text="Convierte archivos JSON de Trello en hojas de Excel organizadas",
            font=("Segoe UI", 10),
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Paso 1: Archivo JSON
        step1_frame = ttk.LabelFrame(main_frame, text=" 📁 Paso 1: Seleccionar archivo JSON ", padding=15)
        step1_frame.pack(fill=tk.X, pady=(0, 15))
        
        json_frame = ttk.Frame(step1_frame)
        json_frame.pack(fill=tk.X)
        
        self.json_entry = ttk.Entry(json_frame, textvariable=self.json_file_path, font=("Consolas", 9))
        self.json_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        json_btn = ttk.Button(json_frame, text="Examinar", command=self.browse_json_file, width=12)
        json_btn.pack(side=tk.RIGHT)
        
        # Paso 2: Archivo de salida
        step2_frame = ttk.LabelFrame(main_frame, text=" 💾 Paso 2: Ubicación de salida ", padding=15)
        step2_frame.pack(fill=tk.X, pady=(0, 15))
        
        output_frame = ttk.Frame(step2_frame)
        output_frame.pack(fill=tk.X)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file_path, font=("Consolas", 9))
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        output_btn = ttk.Button(output_frame, text="Examinar", command=self.browse_output_file, width=12)
        output_btn.pack(side=tk.RIGHT)
        
        # Área de resultados
        results_frame = ttk.LabelFrame(main_frame, text=" 📊 Información del proceso ", padding=15)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.info_text = tk.Text(
            text_frame, 
            wrap=tk.WORD, 
            font=("Consolas", 9),
            bg="#f8f9fa",
            fg="#2c3e50"
        )
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de acción
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón principal
        self.process_btn = tk.Button(
            button_frame,
            text="🚀 PROCESAR ARCHIVO",
            command=self.process_file,
            font=("Segoe UI", 11, "bold"),
            bg="#3498db",
            fg="white",
            height=2,
            cursor="hand2"
        )
        self.process_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="🗑️ Limpiar", command=self.clear_fields, width=15)
        clear_btn.pack(side=tk.RIGHT)
        
        # Información inicial
        self.add_info("=== BIENVENIDO AL EXTRACTOR DE TRELLO ===")
        self.add_info("")
        self.add_info("📋 INSTRUCCIONES:")
        self.add_info("  1. Exporta tu tablero desde Trello en formato JSON")
        self.add_info("  2. Selecciona el archivo JSON usando 'Examinar'")
        self.add_info("  3. Elige dónde guardar el Excel resultante")
        self.add_info("  4. Haz clic en 'PROCESAR ARCHIVO'")
        self.add_info("")
        self.add_info("✨ El programa extraerá automáticamente:")
        self.add_info("  • Nombres de tarjetas")
        self.add_info("  • Números de ticket")
        self.add_info("  • Listas actuales")
        self.add_info("  • Fechas y miembros")
        self.add_info("=" * 50)
        
    def add_info(self, text):
        """Añade texto al área de información"""
        self.info_text.insert(tk.END, text + "\n")
        self.info_text.see(tk.END)
        self.root.update()
        
    def browse_json_file(self):
        """Seleccionar archivo JSON"""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo JSON de Trello",
            filetypes=[
                ("Archivos JSON", "*.json"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=os.path.expanduser("~/Desktop")
        )
        if filename:
            self.json_file_path.set(filename)
            self.add_info(f"✅ Archivo seleccionado: {Path(filename).name}")
            
    def browse_output_file(self):
        """Seleccionar ubicación de salida"""
        filename = filedialog.asksaveasfilename(
            title="Guardar archivo Excel como",
            defaultextension=".xlsx",
            filetypes=[
                ("Archivos Excel", "*.xlsx"),
                ("Todos los archivos", "*.*")
            ],
            initialdir=os.path.expanduser("~/Desktop"),
            initialfile="tarjetas_trello.xlsx"
        )
        if filename:
            self.output_file_path.set(filename)
            self.add_info(f"💾 Guardar como: {Path(filename).name}")
            
    def clear_fields(self):
        """Limpiar campos"""
        self.json_file_path.set("")
        self.output_file_path.set("")
        self.info_text.delete(1.0, tk.END)
        self.add_info("🗑️ Campos limpiados. Listo para procesar nuevo archivo.")
        
    def validate_inputs(self):
        """Validar entradas"""
        if not self.json_file_path.get():
            messagebox.showerror("❌ Error", "Selecciona un archivo JSON")
            return False
            
        if not self.output_file_path.get():
            messagebox.showerror("❌ Error", "Selecciona ubicación de salida")
            return False
            
        if not Path(self.json_file_path.get()).exists():
            messagebox.showerror("❌ Error", "El archivo JSON no existe")
            return False
            
        return True
        
    def process_file(self):
        """Procesar archivo principal"""
        if not self.validate_inputs():
            return
            
        json_path = Path(self.json_file_path.get())
        output_path = Path(self.output_file_path.get())
        
        try:
            self.process_btn.config(state="disabled", text="⏳ PROCESANDO...")
            self.add_info("")
            self.add_info("🔄 INICIANDO PROCESAMIENTO...")
            self.add_info(f"📄 Archivo: {json_path.name}")
            
            # Extraer datos
            df = self.extractor.extract_trello_data(json_path)
            
            if df.empty:
                self.add_info("⚠️ No se encontraron tarjetas en el archivo")
                messagebox.showwarning("Advertencia", "No hay tarjetas para procesar")
                return
                
            self.show_summary(df)
            
            # Guardar Excel
            self.add_info("💾 Generando archivo Excel...")
            self.exporter.save_to_excel(df, output_path)
            
            self.add_info("")
            self.add_info("🎉 ¡PROCESO COMPLETADO EXITOSAMENTE!")
            self.add_info(f"📊 Total de tarjetas procesadas: {len(df)}")
            self.add_info(f"💾 Archivo guardado: {output_path.name}")
            self.add_info("=" * 50)
            
            # Confirmar éxito
            result = messagebox.askyesno(
                "✅ ¡Éxito!",
                f"Se procesaron {len(df)} tarjetas correctamente.\n\n"
                f"Archivo guardado como: {output_path.name}\n\n"
                f"¿Deseas abrir la carpeta donde se guardó?"
            )
            
            if result:
                import subprocess
                subprocess.Popen(f'explorer /select,"{output_path}"', shell=True)
                
        except Exception as e:
            error_msg = f"❌ Error: {str(e)}"
            self.add_info(error_msg)
            messagebox.showerror("Error", error_msg)
            
        finally:
            self.process_btn.config(state="normal", text="🚀 PROCESAR ARCHIVO")
            
    def show_summary(self, df):
        """Mostrar resumen de datos"""
        self.add_info("")
        self.add_info("📈 RESUMEN DE DATOS EXTRAÍDOS:")
        self.add_info(f"   Total de tarjetas: {len(df)}")
        
        if not df.empty:
            # Por lista
            lista_counts = df['Lista_Actual'].value_counts()
            self.add_info("")
            self.add_info("📋 Tarjetas por lista:")
            for lista, count in lista_counts.head(10).items():
                self.add_info(f"   • {lista}: {count}")
                
            # Tickets
            with_ticket = df[df['Número_Ticket'].notna()]
            without_ticket = df[df['Número_Ticket'].isna()]
            
            self.add_info("")
            self.add_info("🎫 Números de ticket:")
            self.add_info(f"   ✅ Con número: {len(with_ticket)}")
            self.add_info(f"   ❌ Sin número: {len(without_ticket)}")
            
            if not with_ticket.empty:
                self.add_info("")
                self.add_info("🔍 Ejemplos de tickets encontrados:")
                for i, (name, ticket) in enumerate(with_ticket[['Nombre_Tarjeta', 'Número_Ticket']].head(3).values):
                    name_short = name[:40] + "..." if len(name) > 40 else name
                    self.add_info(f"   {i+1}. #{ticket} - {name_short}")
                    
    def run(self):
        """Ejecutar aplicación"""
        self.root.mainloop()

def main():
    """Función principal"""
    try:
        app = TrelloExtractorApp()
        app.run()
    except Exception as e:
        messagebox.showerror("Error Fatal", f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()

