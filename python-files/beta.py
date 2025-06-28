import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time
import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import nuitka

class ElectanParserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Electan Parser")
        self.root.geometry("600x400")

        # Переменные для хранения параметров
        self.base_url = tk.StringVar(value="https://electan.ru")
        self.election_id = tk.StringVar(value="10")
        self.tik_id = tk.StringVar(value="533")
        self.delay = tk.DoubleVar(value=0.01)
        self.parse_mode = tk.StringVar(value="parties")  # parties или uik_data

        # Создаем интерфейс
        self.create_widgets()

        # Для отображения лога
        self.log_text = tk.Text(self.root, height=10, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_widgets(self):
        # Фрейм для параметров
        params_frame = ttk.LabelFrame(self.root, text="Параметры парсера")
        params_frame.pack(fill=tk.X, padx=10, pady=5)

        # Поля ввода
        ttk.Label(params_frame, text="Базовый URL:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.base_url, width=50).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(params_frame, text="ID выборов:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.election_id).grid(row=1, column=1, sticky=tk.W)

        ttk.Label(params_frame, text="ID ТИК:").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.tik_id).grid(row=2, column=1, sticky=tk.W)

        ttk.Label(params_frame, text="Задержка (сек):").grid(row=3, column=0, sticky=tk.W)
        ttk.Entry(params_frame, textvariable=self.delay).grid(row=3, column=1, sticky=tk.W)

        # Радиокнопки для выбора режима
        mode_frame = ttk.LabelFrame(self.root, text="Режим парсинга")
        mode_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Radiobutton(mode_frame, text="Данные по партиям", variable=self.parse_mode, value="parties").pack(
            anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Данные по УИК", variable=self.parse_mode, value="uik_data").pack(anchor=tk.W)

        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(btn_frame, text="Начать парсинг", command=self.start_parsing).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="Экспорт лога", command=self.export_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Очистить лог", command=self.clear_log).pack(side=tk.LEFT)

    def log_message(self, message):
        """Добавляем сообщение в лог"""
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def clear_log(self):
        """Очищаем лог"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')

    def export_log(self):
        """Экспортируем лог в файл"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.get(1.0, tk.END))
                self.log_message(f"Лог сохранен в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить лог: {str(e)}")

    def start_parsing(self):
        """Запускаем парсинг в отдельном потоке"""
        if self.parse_mode.get() == "parties":
            parser = PartyParser(
                base_url=self.base_url.get(),
                election_id=self.election_id.get(),
                tik_id=self.tik_id.get(),
                delay=self.delay.get(),
                log_callback=self.log_message
            )
        else:
            parser = UikDataParser(
                base_url=self.base_url.get(),
                election_id=self.election_id.get(),
                tik_id=self.tik_id.get(),
                delay=self.delay.get(),
                log_callback=self.log_message
            )

        # Запускаем в отдельном потоке, чтобы не блокировать интерфейс
        threading.Thread(target=parser.run).start()


class BaseParser:
    def __init__(self, base_url, election_id, tik_id, delay, log_callback):
        self.base_url = base_url
        self.election_id = election_id
        self.tik_id = tik_id
        self.delay = delay
        self.log = log_callback
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_uik_list(self):
        """Получаем список всех УИК для заданного ТИК"""
        tik_url = f"{self.base_url}/election/{self.election_id}/tik/{self.tik_id}/"
        try:
            self.log(f"Загружаем страницу ТИК: {tik_url}")
            response = requests.get(tik_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Ищем все ссылки на УИК
            uik_numbers = []
            for a in soup.find_all('a', href=True):
                if f"/election/{self.election_id}/tik/{self.tik_id}/uik/" in a['href']:
                    try:
                        uik_num = int(a['href'].split('/')[-1])
                        uik_numbers.append(uik_num)
                    except ValueError:
                        continue

            # Удаляем дубликаты и сортируем
            uik_list = sorted(list(set(uik_numbers)))
            self.log(f"Найдено {len(uik_list)} УИК")
            return uik_list

        except Exception as e:
            self.log(f"Ошибка при получении списка УИК: {e}")
            return []

    def run(self):
        """Основной метод для запуска парсера (должен быть переопределен)"""
        raise NotImplementedError


class PartyParser(BaseParser):
    def parse_party_results(self, soup):
        """Парсим таблицу с результатами по партиям"""
        parties_data = []
        table = soup.find('table', class_='candidates-result')

        if not table:
            return parties_data

        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                party_name = cols[0].get_text(strip=True)
                votes = cols[1].get_text(strip=True)
                percentage = cols[2].get_text(strip=True)

                parties_data.append({
                    'Партия': party_name,
                    'Голоса': votes,
                    'Процент': percentage
                })

        return parties_data

    def parse_uik_page(self, uik_number):
        """Парсим данные с конкретной страницы УИК"""
        url = f"{self.base_url}/election/{self.election_id}/tik/{self.tik_id}/uik/{uik_number}"
        try:
            self.log(f"Обрабатываем УИК {uik_number}: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Основные данные
            data = {
                'УИК': uik_number,
                'Результаты партий': self.parse_party_results(soup)
            }

            return data

        except Exception as e:
            self.log(f"Ошибка при парсинге УИК {uik_number}: {e}")
            return None

    def save_to_csv(self, data, filename):
        """Сохраняем данные в CSV файл"""
        if not data:
            self.log("Нет данных для сохранения")
            return

        # Собираем все уникальные названия партий
        all_parties = set()
        for uik_data in data:
            for party in uik_data['Результаты партий']:
                all_parties.add(party['Партия'])

        # Сортируем партии по алфавиту
        sorted_parties = sorted(all_parties)

        # Создаем заголовки столбцов
        fieldnames = ['УИК']
        for party in sorted_parties:
            fieldnames.extend([f"{party} (голоса)", f"{party} (%)"])

        # Формируем строки данных
        rows = []
        for uik_data in data:
            row = {'УИК': uik_data['УИК']}
            for party in sorted_parties:
                found = False
                for p in uik_data['Результаты партий']:
                    if p['Партия'] == party:
                        row[f"{party} (голоса)"] = p['Голоса']
                        row[f"{party} (%)"] = p['Процент']
                        found = True
                        break
                if not found:
                    row[f"{party} (голоса)"] = '0'
                    row[f"{party} (%)"] = '0%'
            rows.append(row)

        # Сохраняем в CSV
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            self.log(f"Данные сохранены в {filename}")
        except Exception as e:
            self.log(f"Ошибка при сохранении файла: {e}")

    def run(self):
        """Основной метод для запуска парсера"""
        # Получаем список УИКов
        uik_numbers = self.get_uik_list()
        if not uik_numbers:
            self.log("Не удалось найти УИКи. Проверьте параметры и доступность сайта.")
            return

        # Собираем данные с каждого УИК
        all_data = []
        for i, uik_num in enumerate(uik_numbers, 1):
            data = self.parse_uik_page(uik_num)
            if data:
                all_data.append(data)
            time.sleep(self.delay)  # Задержка между запросами

        # Сохраняем результаты
        if all_data:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="party_results.csv"
            )
            if file_path:
                self.save_to_csv(all_data, file_path)
        else:
            self.log("Не удалось собрать данные")


class UikDataParser(BaseParser):
    def extract_percentage(self, soup, div_class):
        """Извлекаем процентное значение из div с указанным классом"""
        try:
            div = soup.find('div', class_=div_class)
            if div:
                # Берем последний текстовый элемент (число)
                text = div.find_all(text=True)[-1].strip()
                # Удаляем возможные символы кроме цифр и точки
                value = re.sub(r'[^\d.]', '', text)
                return f"{value}%"
        except:
            pass
        return "0%"

    def extract_info_value(self, soup, field_name):
        """Извлекаем числовое значение по названию поля"""
        try:
            # Ищем элемент, содержащий название поля
            element = soup.find(string=re.compile(field_name, re.IGNORECASE))
            if element:
                # Ищем число в том же или следующем элементе
                parent = element.parent
                text = parent.get_text(strip=True)
                # Ищем число после названия поля
                match = re.search(fr"{field_name}.*?(\d+)", text)
                if match:
                    return match.group(1)

                # Проверяем соседние элементы
                for sibling in parent.find_next_siblings():
                    sibling_text = sibling.get_text(strip=True)
                    if sibling_text and sibling_text.isdigit():
                        return sibling_text
        except:
            pass
        return "0"

    def parse_uik_page(self, uik_number):
        """Парсим данные с конкретной страницы УИК"""
        url = f"{self.base_url}/election/{self.election_id}/tik/{self.tik_id}/uik/{uik_number}"
        try:
            self.log(f"Обрабатываем УИК {uik_number}: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Основные данные
            data = {
                'УИК': uik_number,
                'Результат': self.extract_percentage(soup, 'ofresult'),
                'Явка': self.extract_percentage(soup, 'ofturnout'),
                'Избирателей': self.extract_info_value(soup, 'Избирателей'),
                'Получено бюллетеней': self.extract_info_value(soup, 'Получено бюллетеней'),
                'Выдано всего': self.extract_info_value(soup, 'Выдано всего'),
                'Выдано досрочно': self.extract_info_value(soup, 'Выдано досрочно'),
                'Выдано на участке': self.extract_info_value(soup, 'Выдано на участке'),
                'Выдано вне помещения': self.extract_info_value(soup, 'Выдано вне помещения'),
                'Бюллетеней в переносных ящиках': self.extract_info_value(soup, 'Бюллетеней в переносных ящиках'),
                'Бюллетеней в стационарных ящиках': self.extract_info_value(soup, 'Бюллетеней в стационарных ящиках'),
                'Бюллетеней в ящиках': self.extract_info_value(soup, 'Бюллетеней в ящиках'),
                'Действительных бюллетеней': self.extract_info_value(soup, 'Действительных бюллетеней'),
                'Недействительных бюллетеней': self.extract_info_value(soup, 'Недействительных бюллетеней'),
                'Утерянных бюллетеней': self.extract_info_value(soup, 'Утерянных бюллетеней'),
            }

            return data

        except Exception as e:
            self.log(f"Ошибка при парсинге УИК {uik_number}: {e}")
            return None

    def save_to_csv(self, data, filename):
        """Сохраняем данные в CSV файл"""
        if not data:
            self.log("Нет данных для сохранения")
            return

        # Определяем порядок столбцов
        fieldnames = [
            'УИК', 'Результат', 'Явка',
            'Избирателей', 'Получено бюллетеней', 'Выдано всего',
            'Выдано досрочно', 'Выдано на участке', 'Выдано вне помещения',
            'Бюллетеней в переносных ящиках', 'Бюллетеней в стационарных ящиках',
            'Бюллетеней в ящиках', 'Действительных бюллетеней',
            'Недействительных бюллетеней', 'Утерянных бюллетеней'
        ]

        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            self.log(f"Данные сохранены в {filename}")
        except Exception as e:
            self.log(f"Ошибка при сохранении файла: {e}")

    def run(self):
        """Основной метод для запуска парсера"""
        # Получаем список УИКов
        uik_numbers = self.get_uik_list()
        if not uik_numbers:
            self.log("Не удалось найти УИКи. Проверьте параметры и доступность сайта.")
            return

        # Собираем данные с каждого УИК
        all_data = []
        for i, uik_num in enumerate(uik_numbers, 1):
            data = self.parse_uik_page(uik_num)
            if data:
                all_data.append(data)
            time.sleep(self.delay)  # Задержка между запросами

        # Сохраняем результаты
        if all_data:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile="uik_data.csv"
            )
            if file_path:
                self.save_to_csv(all_data, file_path)
        else:
            self.log("Не удалось собрать данные")


if __name__ == "__main__":
    root = tk.Tk()
    app = ElectanParserApp(root)
    root.mainloop()