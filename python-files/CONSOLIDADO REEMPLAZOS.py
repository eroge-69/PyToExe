import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, portrait
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class CSVSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV Search App")
        
        self.load_button = tk.Button(root, text="Cargar CSV", command=self.load_csv)
        self.load_button.pack(pady=10)
        
        self.search_label = tk.Label(root, text="Buscar nombre:")
        self.search_label.pack(pady=5)
        
        self.search_entry = tk.Entry(root)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<KeyRelease>", self.update_search_results)
        
        self.search_dropdown = ttk.Combobox(root, state="readonly")
        self.search_dropdown.pack(pady=5)
        self.search_dropdown.bind("<<ComboboxSelected>>", self.update_search_entry)
        
        self.search_results = ttk.Treeview(root, columns=("Reemplazo", "Fecha Inicio", "Fecha Término", "Unidad/Subunidad", "Días", "Secuencia"), show='headings')
        self.search_results.heading("Reemplazo", text="Reemplazo")
        self.search_results.heading("Fecha Inicio", text="Fecha Inicio")
        self.search_results.heading("Fecha Término", text="Fecha Término")
        self.search_results.heading("Unidad/Subunidad", text="Unidad/Subunidad")
        self.search_results.heading("Días", text="Días")
        self.search_results.heading("Secuencia", text="Secuencia")
        self.search_results.pack(pady=20, fill=tk.BOTH, expand=True)
        
        self.export_button = tk.Button(root, text="Exportar a HTML", command=self.export_to_html)
        self.export_button.pack(pady=10)
        
        self.export_pdf_button = tk.Button(root, text="Exportar a PDF", command=self.export_to_pdf)
        self.export_pdf_button.pack(pady=10)
        
        self.export_cuarto_turno_pdf_button = tk.Button(root, text="Exportar Listado Cuarto Turno (PDF)", command=self.export_cuarto_turno_pdf)
        self.export_cuarto_turno_pdf_button.pack(pady=10)
        
        self.df = None
        self.filtered_data = None
    
    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            try:
                self.df = pd.read_csv(file_path, encoding='utf-8')
                messagebox.showinfo("Carga exitosa", "Archivo CSV cargado correctamente con codificación utf-8.")
                self.update_search_dropdown()
            except UnicodeDecodeError:
                try:
                    self.df = pd.read_csv(file_path, encoding='latin1')
                    messagebox.showinfo("Carga exitosa", "Archivo CSV cargado correctamente con codificación latin1.")
                    self.update_search_dropdown()
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo cargar el archivo CSV: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo CSV: {e}")
    
    def update_search_dropdown(self):
        if self.df is not None:
            names = self.df['Reemplazo 1'].tolist()
            self.search_dropdown['values'] = sorted(set(names))
    
    def update_search_entry(self, event):
        selected_name = self.search_dropdown.get()
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, selected_name)
        self.update_search_results(event)
    
    def update_search_results(self, event):
        search_query = self.search_entry.get().lower()
        if self.df is not None:
            results = self.df[(self.df['Reemplazo 1'].str.lower().str.contains(search_query)) | 
                              (self.df['Reemplazo 2'].str.lower().str.contains(search_query)) | 
                              (self.df['Reemplazo 3'].str.lower().str.contains(search_query))]
            
            self.filtered_data = []  # Para almacenar los datos filtrados
            covered_periods = {}  # Diccionario para almacenar los períodos por unidad
            
            for row in self.search_results.get_children():
                self.search_results.delete(row)
            
            for _, row in results.iterrows():
                start_date = datetime.strptime(row['Fecha Inicio'], '%d/%m/%Y')
                end_date = datetime.strptime(row['Fecha Término'], '%d/%m/%Y')
                period_key = (start_date, end_date, row['Unidad/Subunidad'])
                
                # Determinar el nombre correcto del reemplazo según el criterio de búsqueda
                if search_query in row['Reemplazo 1'].lower():
                    name = row['Reemplazo 1']
                elif search_query in row['Reemplazo 2'].lower():
                    name = row['Reemplazo 2']
                else:
                    name = row['Reemplazo 3']
                
                # Sumar 1 al cálculo de días para incluir el primer día
                days = (end_date - start_date).days + 1
                
                # Verificar si el período ya está cubierto
                if period_key not in covered_periods:
                    covered_periods[period_key] = days
                    self.search_results.insert("", "end", values=(name, row['Fecha Inicio'], row['Fecha Término'], row['Unidad/Subunidad'], days, row['Secuencia']))
                    self.filtered_data.append((name, row['Fecha Inicio'], row['Fecha Término'], row['Unidad/Subunidad'], days, row['Secuencia']))
            
            # Mostrar el contador de días por unidad
            unit_days = self.calculate_unit_days_diagram()
            for unit, days in unit_days.items():
                self.search_results.insert("", "end", values=("", "", "", unit, days), tags=("unit_total",))
    
    def export_to_html(self):
        if self.filtered_data:
            df_filtered = pd.DataFrame(self.filtered_data, columns=["Reemplazo", "Fecha Inicio", "Fecha Término", "Unidad/Subunidad", "Días", "Secuencia"])
            html_file = "resultados_busqueda.html"
            df_filtered.to_html(html_file, index=False)
            webbrowser.open('file://' + os.path.realpath(html_file))
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron resultados para la búsqueda.")
    
    def export_to_pdf(self):
        if self.filtered_data:
            pdf_file = f"Consolidado Turnos Reemplazantes_{datetime.now().strftime('%Y')}.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            elements = []
            
            # Título del PDF
            styles = getSampleStyleSheet()
            title = Paragraph(f"Consolidado Turnos Registrados en Intranet", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))
            
            # Datos para la tabla principal
            data = [["Reemplazo", "Fecha Inicio", "Fecha Término", "Unidad/Subunidad", "Días", "Secuencia"]]
            data.extend([row[:6] for row in self.filtered_data])
            
            # Crear la tabla principal y aplicar estilo
            table = Table(data)
            style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)])
            table.setStyle(style)
            
            elements.append(table)
            elements.append(Spacer(1, 12))
            
            # Calcular totales por unidad y secuencia
            unit_days_diagram = self.calculate_unit_days_diagram()
            turn_type_days = self.calculate_turn_type_days()
            
            # Tabla para los días y turnos
            day_turn_table_data = [["Unidad/Subunidad", "Días Diurnos", "Días Cuarto Turno"]]
            for unit in unit_days_diagram:
                day_turn_table_data.append([unit, turn_type_days[unit]["Di"], turn_type_days[unit]["Cuarto"]])
            day_turn_table = Table(day_turn_table_data)
            day_turn_table.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                                 ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                                 ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                                 ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                                 ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
            elements.append(day_turn_table)
            elements.append(Spacer(1, 12))
            
            doc.build(elements)
            webbrowser.open('file://' + os.path.realpath(pdf_file))
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron resultados para la búsqueda.")
    
    def export_cuarto_turno_pdf(self):
        if self.df is not None:
            pdf_file = f"listado_cuarto_turno_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            doc = SimpleDocTemplate(pdf_file, pagesize=portrait(letter))
            elements = []

            # Título del PDF
            styles = getSampleStyleSheet()
            title = Paragraph(f"Listado de Funcionarios Reemplazantes con Cuarto Turno", styles['Title'])
            elements.append(title)
            elements.append(Spacer(1, 12))

            # Filtrar los datos para obtener solo los de cuarto turno
            cuarto_turno_data = [row for _, row in self.df.iterrows() if row['Secuencia'].upper() != "DI" and row['Reemplazo 1'] != "---" and row['Reemplazo 1'] != ""]

            # Crear una lista de funcionarios únicos que realizan cuarto turno
            cuarto_turno_funcionarios = {}
            for row in cuarto_turno_data:
                if row['Reemplazo 1'] not in cuarto_turno_funcionarios:
                    cuarto_turno_funcionarios[row['Reemplazo 1']] = set()
                cuarto_turno_funcionarios[row['Reemplazo 1']].add(row['Unidad/Subunidad'])

            # Organizar y enumerar los funcionarios por orden alfabético
            sorted_funcionarios = sorted(cuarto_turno_funcionarios.items(), key=lambda x: x[0])

            # Crear datos para la tabla
            table_data = [["#", "Nombre", "Unidad/Subunidad"]]
            for index, (funcionario, unidades) in enumerate(sorted_funcionarios, start=1):
                unidades_str = ", ".join(unidades)
                table_data.append([index, funcionario, unidades_str])

            # Crear la tabla y aplicar estilo
            table = Table(table_data)
            style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.gray),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black)])
            table.setStyle(style)

            elements.append(table)

            doc.build(elements)
            webbrowser.open('file://' + os.path.realpath(pdf_file))
        else:
            messagebox.showinfo("Sin resultados", "No se encontraron resultados para la búsqueda.")
    
    def check_overlap(self, period1, period2):
        return not (period1[1] < period2[0] or period1[0] > period2[1])
    
    def calculate_unit_days_diagram(self, data=None):
        if data is None:
            data = self.filtered_data
            
        unit_days = {}
        unit_periods = {}

        for _, start_date, end_date, unit, days, _ in data:
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')

            if unit not in unit_periods:
                unit_periods[unit] = set()
            
            current_date = start_date
            while current_date <= end_date:
                unit_periods[unit].add(current_date)
                current_date += timedelta(days=1)
        
        for unit, periods in unit_periods.items():
            unit_days[unit] = len(periods)
        
        return unit_days
    
    def calculate_turn_type_days(self):
        turn_type_days = {}
        for row in self.filtered_data:
            unit = row[3]
            turn_type = "Di" if "DI" in row[5].upper() else "Cuarto"
            if unit not in turn_type_days:
                turn_type_days[unit] = {"Di": set(), "Cuarto": set()}
            days_set = turn_type_days[unit][turn_type]
            start_date = datetime.strptime(row[1], '%d/%m/%Y')
            end_date = datetime.strptime(row[2], '%d/%m/%Y')
            for day_delta in range((end_date - start_date).days + 1):
                day = start_date + timedelta(days=day_delta)
                if day not in turn_type_days[unit]["Di"] and day not in turn_type_days[unit]["Cuarto"]:
                    days_set.add(day)
        for unit, types in turn_type_days.items():
            for turn_type, days_set in types.items():
                turn_type_days[unit][turn_type] = len(days_set)
        return turn_type_days

if __name__ == "__main__":
    root = tk.Tk()
    app = CSVSearchApp(root)
    root.mainloop()
