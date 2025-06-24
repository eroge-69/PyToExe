import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import os
import threading
import urllib.parse
from pathlib import Path

class PubChemDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("PubChem 3D SWF Downloader")
        self.root.geometry("600x400")
        
        # Переменные
        self.compound_name = tk.StringVar()
        self.save_directory = tk.StringVar(value=os.getcwd())
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Готов к загрузке")
        
        self.setup_ui()
        
    def setup_ui(self):
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Поле ввода названия соединения
        ttk.Label(main_frame, text="Название соединения:").grid(row=0, column=0, sticky=tk.W, pady=5)
        compound_entry = ttk.Entry(main_frame, textvariable=self.compound_name, width=50)
        compound_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Выбор папки для сохранения
        ttk.Label(main_frame, text="Папка для сохранения:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.save_directory, width=40).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="Обзор", command=self.browse_directory).grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # Кнопка загрузки
        download_btn = ttk.Button(main_frame, text="Скачать 3D формулу", command=self.start_download)
        download_btn.grid(row=2, column=0, columnspan=3, pady=20)
        
        # Прогресс-бар
        ttk.Label(main_frame, text="Прогресс:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Статус
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=4, column=0, columnspan=3, pady=10)
        
        # Текстовое поле для логов
        ttk.Label(main_frame, text="Лог:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        
        log_frame = ttk.Frame(main_frame)
        log_frame.grid(row=5, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, width=50)
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        main_frame.rowconfigure(5, weight=1)
        
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.save_directory.set(directory)
            
    def log_message(self, message):
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status):
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def update_progress(self, value):
        self.progress_var.set(value)
        self.root.update_idletasks()
        
    def start_download(self):
        compound = self.compound_name.get().strip()
        if not compound:
            messagebox.showerror("Ошибка", "Введите название соединения")
            return
            
        if not os.path.exists(self.save_directory.get()):
            messagebox.showerror("Ошибка", "Выберите существующую папку")
            return
            
        # Запуск загрузки в отдельном потоке
        thread = threading.Thread(target=self.download_compound, args=(compound,))
        thread.daemon = True
        thread.start()
        
    def get_russian_to_english_translation(self, compound_name):
        """Словарь переводов русских названий соединений на английский"""
        translations = {
            # Основные соединения
            'вода': 'water',
            'кофеин': 'caffeine',
            'аспирин': 'aspirin',
            'глюкоза': 'glucose',
            'этанол': 'ethanol',
            'метанол': 'methanol',
            'ацетон': 'acetone',
            'бензол': 'benzene',
            'толуол': 'toluene',
            'фенол': 'phenol',
            'анилин': 'aniline',
            'мочевина': 'urea',
            'мочевая кислота': 'uric acid',
            'лимонная кислота': 'citric acid',
            'уксусная кислота': 'acetic acid',
            'молочная кислота': 'lactic acid',
            'аскорбиновая кислота': 'ascorbic acid',
            'витамин с': 'vitamin c',
            'витамин а': 'vitamin a',
            'витамин е': 'vitamin e',
            'витамин д': 'vitamin d',
            'холестерин': 'cholesterol',
            'адреналин': 'adrenaline',
            'серотонин': 'serotonin',
            'дофамин': 'dopamine',
            'инсулин': 'insulin',
            'пенициллин': 'penicillin',
            'морфин': 'morphine',
            'кодеин': 'codeine',
            'никотин': 'nicotine',
            'тестостерон': 'testosterone',
            'эстроген': 'estrogen',
            'прогестерон': 'progesterone',
            'кортизол': 'cortisol',
            'тироксин': 'thyroxine',
            'гемоглобин': 'hemoglobin',
            'хлорофилл': 'chlorophyll',
            'каротин': 'carotene',
            'ментол': 'menthol',
            'камфора': 'camphor',
            'ванилин': 'vanillin',
            'сахароза': 'sucrose',
            'фруктоза': 'fructose',
            'лактоза': 'lactose',
            'крахмал': 'starch',
            'целлюлоза': 'cellulose',
            'хитин': 'chitin',
            'коллаген': 'collagen',
            'кератин': 'keratin',
            'меланин': 'melanin',
            'гистамин': 'histamine',
            'тирамин': 'tyramine',
            'триптофан': 'tryptophan',
            'фенилаланин': 'phenylalanine',
            'тирозин': 'tyrosine',
            'лейцин': 'leucine',
            'изолейцин': 'isoleucine',
            'валин': 'valine',
            'аланин': 'alanine',
            'глицин': 'glycine',
            'серин': 'serine',
            'треонин': 'threonine',
            'цистеин': 'cysteine',
            'метионин': 'methionine',
            'аспарагин': 'asparagine',
            'глутамин': 'glutamine',
            'аспарагиновая кислота': 'aspartic acid',
            'глутаминовая кислота': 'glutamic acid',
            'лизин': 'lysine',
            'аргинин': 'arginine',
            'гистидин': 'histidine',
            'пролин': 'proline'
        }
        
        # Проверяем точное совпадение
        compound_lower = compound_name.lower().strip()
        if compound_lower in translations:
            return translations[compound_lower]
        
        # Проверяем частичные совпадения
        for russian, english in translations.items():
            if russian in compound_lower or compound_lower in russian:
                return english
                
        return compound_name  # Возвращаем оригинальное название если перевод не найден
    
    def get_compound_cid(self, compound_name):
        """Получение CID соединения по названию"""
        try:
            # Сначала пробуем перевести с русского на английский
            english_name = self.get_russian_to_english_translation(compound_name)
            
            # Если название было переведено, логируем это
            if english_name != compound_name:
                self.log_message(f"Переведено '{compound_name}' -> '{english_name}'")
            
            # Пробуем поиск с переведенным названием
            cid = self._search_compound_by_name(english_name)
            if cid:
                return cid
            
            # Если не найдено, пробуем с оригинальным названием
            if english_name != compound_name:
                self.log_message(f"Поиск с оригинальным названием: {compound_name}")
                cid = self._search_compound_by_name(compound_name)
                if cid:
                    return cid
            
            return None
                
        except Exception as e:
            self.log_message(f"Ошибка при получении CID: {str(e)}")
            return None
    
    def _search_compound_by_name(self, compound_name):
        """Поиск соединения по названию в PubChem"""
        try:
            # Кодируем название для URL (поддерживает UTF-8)
            encoded_name = urllib.parse.quote(compound_name, safe='', encoding='utf-8')
            url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{encoded_name}/cids/JSON"
            
            self.log_message(f"Поиск CID для: {compound_name}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'IdentifierList' in data and 'CID' in data['IdentifierList']:
                    cid = data['IdentifierList']['CID'][0]
                    self.log_message(f"Найден CID: {cid}")
                    return cid
                else:
                    self.log_message("CID не найден в ответе")
                    return None
            else:
                self.log_message(f"Ошибка HTTP: {response.status_code}")
                return None
                
        except Exception as e:
            self.log_message(f"Ошибка поиска: {str(e)}")
            return None
            
    def download_3d_structure(self, cid):
        """Загрузка 3D структуры в SWF формате"""
        try:
            # URL для получения 3D структуры в SWF формате
            swf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/record/SDF/?record_type=3d&response_type=display"
            
            self.log_message(f"Попытка загрузки 3D структуры для CID: {cid}")
            
            # Альтернативный URL для 3D визуализации
            viewer_url = f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}#section=3D-Conformer"
            
            # Поскольку PubChem больше не предоставляет прямые SWF файлы,
            # попробуем получить SDF файл 3D структуры
            sdf_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/SDF?record_type=3d"
            
            response = requests.get(sdf_url, timeout=30)
            
            if response.status_code == 200:
                compound_name = self.compound_name.get().strip()
                safe_name = "".join(c for c in compound_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                
                # Сохраняем как SDF файл (3D структура)
                filename = f"{safe_name}_CID_{cid}_3D.sdf"
                filepath = os.path.join(self.save_directory.get(), filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                    
                self.log_message(f"3D структура сохранена: {filename}")
                self.log_message(f"Ссылка на 3D визуализацию: {viewer_url}")
                return True
            else:
                self.log_message(f"Ошибка загрузки 3D структуры: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_message(f"Ошибка при загрузке 3D структуры: {str(e)}")
            return False
            
    def download_compound(self, compound_name):
        """Основная функция загрузки"""
        try:
            self.update_status("Поиск соединения...")
            self.update_progress(10)
            
            # Получаем CID
            cid = self.get_compound_cid(compound_name)
            if not cid:
                self.update_status("Ошибка: соединение не найдено")
                self.log_message("Соединение не найдено в базе PubChem")
                return
                
            self.update_progress(30)
            self.update_status("Загрузка 3D структуры...")
            
            # Загружаем 3D структуру
            success = self.download_3d_structure(cid)
            
            if success:
                self.update_progress(100)
                self.update_status("Загрузка завершена успешно")
                self.log_message("Загрузка завершена успешно!")
                messagebox.showinfo("Успех", "3D структура успешно загружена!")
            else:
                self.update_status("Ошибка загрузки")
                self.log_message("Не удалось загрузить 3D структуру")
                messagebox.showerror("Ошибка", "Не удалось загрузить 3D структуру")
                
        except Exception as e:
            self.update_status("Ошибка")
            self.log_message(f"Общая ошибка: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.update_progress(0)

def main():
    root = tk.Tk()
    app = PubChemDownloader(root)
    root.mainloop()

if __name__ == "__main__":
    main()