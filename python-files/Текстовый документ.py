# simple_money_tracker.py
import json
from datetime import datetime
from typing import List, Dict

class SimpleMoneyTracker:
    def __init__(self):
        self.income_categories = ["биржа", "рассылка", "фриланс", "инвестиции", "другое"]
        self.expense_categories = ["чтение", "обучение", "транспорт", "еда", "жилье", "развлечения", "другое"]
        self.operations: List[Dict] = []
        
    def add_operation(self, is_income: bool, amount: float, category: str, description: str = ""):
        """Добавление операции"""
        if is_income and category not in self.income_categories:
            raise ValueError(f"Неверная категория дохода. Доступные: {self.income_categories}")
        elif not is_income and category not in self.expense_categories:
            raise ValueError(f"Неверная категория расхода. Доступные: {self.expense_categories}")
            
        operation = {
            'date': datetime.now().strftime("%d.%m.%Y %H:%M"),
            'type': 'доход' if is_income else 'расход',
            'category': category,
            'amount': amount,
            'description': description
        }
        
        self.operations.append(operation)
        print(f"✅ Добавлена операция: {operation}")
        
    def get_totals(self):
        """Получение итогов"""
        total_income = sum(op['amount'] for op in self.operations if op['type'] == 'доход')
        total_expense = sum(op['amount'] for op in self.operations if op['type'] == 'расход')
        balance = total_income - total_expense
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance
        }
    
    def show_summary(self):
        """Показать сводку"""
        totals = self.get_totals()
        
        print("\n" + "="*50)
        print("СВОДКА ПО УЧЕТУ ДЕНЕЖНЫХ СРЕДСТВ")
        print("="*50)
        print(f"Всего операций: {len(self.operations)}")
        print(f"Общий доход: {totals['total_income']:.2f} ₽")
        print(f"Общий расход: {totals['total_expense']:.2f} ₽")
        print(f"Баланс: {totals['balance']:.2f} ₽")
        print("="*50)
        
    def show_operations(self):
        """Показать все операции"""
        print("\nСПИСОК ОПЕРАЦИЙ:")
        for i, op in enumerate(self.operations, 1):
            print(f"{i}. {op['date']} - {op['type']} ({op['category']}): {op['amount']:.2f} ₽ - {op['description']}")
            
    def save_to_file(self, filename="money_tracker.json"):
        """Сохранить данные в файл"""
        data = {
            'operations': self.operations,
            'income_categories': self.income_categories,
            'expense_categories': self.expense_categories
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ Данные сохранены в файл: {filename}")
        
    def load_from_file(self, filename="money_tracker.json"):
        """Загрузить данные из файла"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            self.operations = data['operations']
            print(f"✅ Данные загружены из файла: {filename}")
            
        except FileNotFoundError:
            print("⚠️ Файл не найден, начинаем с чистого листа")

# Пример использования
def main():
    tracker = SimpleMoneyTracker()
    
    # Добавляем операции
    tracker.add_operation(True, 15000.50, "биржа", "Заработок на бирже")
    tracker.add_operation(True, 5000.00, "рассылка", "Email рассылка")
    tracker.add_operation(False, 2000.00, "чтение", "Покупка книг")
    tracker.add_operation(False, 500.00, "транспорт", "Такси")
    tracker.add_operation(False, 3000.00, "обучение", "Онлайн-курсы")
    
    # Показываем операции
    tracker.show_operations()
    
    # Показываем сводку
    tracker.show_summary()
    
    # Сохраняем данные
    tracker.save_to_file()

if __name__ == "__main__":
    main()