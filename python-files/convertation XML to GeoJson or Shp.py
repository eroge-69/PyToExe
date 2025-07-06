import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET
import json
import geopandas as gpd
from shapely.geometry import shape


class XMLConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("XML to GeoJSON/SHP Converter")
        self.root.geometry("600x400")
        
        # Переменные
        self.input_file = tk.StringVar()
        self.output_format = tk.StringVar(value="geojson")
        
        # Создание интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        # Фрейм для ввода файла
        input_frame = ttk.LabelFrame(self.root, text="Входной XML-файл", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Файл:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(input_frame, textvariable=self.input_file, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(input_frame, text="Обзор...", command=self.browse_input_file).grid(row=0, column=2)
        
        # Фрейм для выбора формата
        format_frame = ttk.LabelFrame(self.root, text="Выходной формат", padding=10)
        format_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Radiobutton(format_frame, text="GeoJSON", variable=self.output_format, value="geojson").pack(anchor=tk.W)
        ttk.Radiobutton(format_frame, text="Shapefile (SHP)", variable=self.output_format, value="shp").pack(anchor=tk.W)
        
        # Фрейм для кнопки конвертации
        convert_frame = ttk.Frame(self.root, padding=10)
        convert_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(convert_frame, text="Конвертировать", command=self.convert_file).pack(pady=10)
        
        # Статус бар
        self.status_bar = ttk.Label(self.root, text="Готово", relief=tk.SUNKEN)
        self.status_bar.pack(fill=tk.X, padx=10, pady=5, side=tk.BOTTOM)
    
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Выберите XML файл",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file.set(file_path)
            self.status_bar.config(text=f"Выбран файл: {os.path.basename(file_path)}")
    
    def convert_file(self):
        input_path = self.input_file.get()
        if not input_path:
            messagebox.showerror("Ошибка", "Пожалуйста, выберите входной XML файл")
            return
        
        if not os.path.exists(input_path):
            messagebox.showerror("Ошибка", "Указанный файл не существует")
            return
        
        try:
            # Парсинг XML
            tree = ET.parse(input_path)
            root = tree.getroot()
            
            # Создаем GeoDataFrame (это упрощенный пример, вам нужно адаптировать под вашу структуру XML)
            features = []
            
            # Пример для XML с геометрией в GeoJSON-подобном формате
            for feature in root.findall('.//feature'):
                properties = {}
                geometry = None
                
                for prop in feature.findall('property'):
                    name = prop.get('name')
                    value = prop.get('value')
                    properties[name] = value
                
                geom_element = feature.find('geometry')
                if geom_element is not None:
                    try:
                        geom_json = json.loads(geom_element.text)
                        geometry = shape(geom_json)
                    except Exception as e:
                        print(f"Ошибка обработки геометрии: {e}")
                
                if geometry is not None:
                    features.append({
                        'type': 'Feature',
                        'properties': properties,
                        'geometry': geometry
                    })
            
            if not features:
                messagebox.showerror("Ошибка", "Не найдено геометрических объектов в XML")
                return
            
            # Создаем GeoDataFrame
            gdf = gpd.GeoDataFrame.from_features(features)
            
            # Определяем выходной файл
            output_dir = os.path.dirname(input_path)
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            if self.output_format.get() == "geojson":
                output_path = os.path.join(output_dir, f"{base_name}.geojson")
                gdf.to_file(output_path, driver='GeoJSON')
            else:
                output_path = os.path.join(output_dir, base_name)
                gdf.to_file(output_path, driver='ESRI Shapefile')
            
            messagebox.showinfo("Успех", f"Файл успешно конвертирован в {output_path}")
            self.status_bar.config(text=f"Конвертация завершена: {os.path.basename(output_path)}")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при конвертации: {str(e)}")
            self.status_bar.config(text="Ошибка при конвертации")


if __name__ == "__main__":
    root = tk.Tk()
    app = XMLConverterApp(root)
    root.mainloop()