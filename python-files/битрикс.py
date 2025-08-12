import requests
import tkinter as tk
from tkinter import scrolledtext, messagebox

class BitrixTimeManApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bitrix24 TimeMan Control")
        self.root.geometry("600x500")
        
        # Основные параметры
        self.base_url = "https://bitrix.legis-s.ru/rest/722/i4qak16uk31pfu6p"
        self.user_id = 825
        self.source = "FINGERPRINT_SCANNER"
        
        # Создаем кнопки и элементы интерфейса
        self.create_widgets()
    
    def create_widgets(self):
        # Фрейм для отображения статуса
        self.status_frame = tk.LabelFrame(self.root, text="Статус", padx=10, pady=10)
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(self.status_frame, height=8)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Кнопка проверки статуса
        self.btn_status = tk.Button(self.root, text="Проверить статус", 
                                  command=self.get_status,
                                  height=2, bg="#e6f3ff")
        self.btn_status.pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопка начала работы
        self.btn_start = tk.Button(self.root, text="Начать/Продолжить рабочий день", 
                                  command=self.start_workday,
                                  height=2, bg="#e6ffe6")
        self.btn_start.pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопка перерыва
        self.btn_pause = tk.Button(self.root, text="Перерыв", 
                                 command=self.pause_workday,
                                 height=2, bg="#fffae6")
        self.btn_pause.pack(fill=tk.X, padx=10, pady=5)
        
        # Кнопка завершения дня
        self.btn_end = tk.Button(self.root, text="Завершить рабочий день", 
                               command=self.end_workday,
                               height=2, bg="#ffe6e6")
        self.btn_end.pack(fill=tk.X, padx=10, pady=5)
    
    def make_request(self, endpoint):
        url = f"{self.base_url}/{endpoint}.json?USER_ID={self.user_id}&SOURCE={self.source}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP Error {response.status_code}", "response": response.text}
        except Exception as e:
            return {"error": str(e)}
    
    def display_response(self, response):
        self.status_text.delete(1.0, tk.END)
        if "error" in response:
            self.status_text.insert(tk.END, f"Ошибка: {response['error']}\n")
        else:
            self.status_text.insert(tk.END, "Успешный запрос:\n")
            for key, value in response.items():
                self.status_text.insert(tk.END, f"{key}: {value}\n")
    
    def get_status(self):
        response = self.make_request("timeman.status")
        self.display_response(response)
    
    def start_workday(self):
        response = self.make_request("timeman.open")
        self.display_response(response)
        # После начала дня проверяем статус
        self.get_status()
    
    def pause_workday(self):
        response = self.make_request("timeman.pause")
        self.display_response(response)
        # После перерыва проверяем статус
        self.get_status()
    
    def end_workday(self):
        response = self.make_request("timeman.close")
        self.display_response(response)
        # После завершения дня проверяем статус
        self.get_status()

if __name__ == "__main__":
    root = tk.Tk()
    app = BitrixTimeManApp(root)
    root.mainloop()