import pandas as pd
from datetime import datetime
import os

class EquipmentInventory:
    def __init__(self):
        # Создаем файлы, если они не существуют
        self.equipment_file = 'equipment.csv'
        self.issued_file = 'issued_equipment.csv'
        
        # Инициализируем файлы с заголовками, если они пустые
        if not os.path.exists(self.equipment_file):
            pd.DataFrame(columns=[
                'id', 'type', 'model', 'serial_number', 'purchase_date', 
                'cost', 'status', 'location'
            ]).to_csv(self.equipment_file, index=False)
            
        if not os.path.exists(self.issued_file):
            pd.DataFrame(columns=[
                'id', 'equipment_id', 'issued_to', 'department', 
                'issue_date', 'return_date', 'notes'
            ]).to_csv(self.issued_file, index=False)
    
    def add_equipment(self, equipment_data):
        """Добавление новой единицы техники"""
        df = pd.read_csv(self.equipment_file)
        
        # Генерируем новый ID
        new_id = df['id'].max() + 1 if not df.empty else 1
        equipment_data['id'] = new_id
        
        # Добавляем запись
        df = pd.concat([df, pd.DataFrame([equipment_data])], ignore_index=True)
        df.to_csv(self.equipment_file, index=False)
        print(f"Оборудование добавлено с ID: {new_id}")
    
    def issue_equipment(self, equipment_id, issued_to, department, notes=''):
        """Выдача техники сотруднику"""
        # Проверяем, доступно ли оборудование
        eq_df = pd.read_csv(self.equipment_file)
        if equipment_id not in eq_df['id'].values:
            print("Оборудование с таким ID не найдено!")
            return
            
        status = eq_df.loc[eq_df['id'] == equipment_id, 'status'].values[0]
        if status != 'Доступно':
            print(f"Оборудование не доступно для выдачи. Текущий статус: {status}")
            return
            
        # Обновляем статус оборудования
        eq_df.loc[eq_df['id'] == equipment_id, 'status'] = 'Выдано'
        eq_df.to_csv(self.equipment_file, index=False)
        
        # Добавляем запись о выдаче
        issue_df = pd.read_csv(self.issued_file)
        
        new_id = issue_df['id'].max() + 1 if not issue_df.empty else 1
        new_record = {
            'id': new_id,
            'equipment_id': equipment_id,
            'issued_to': issued_to,
            'department': department,
            'issue_date': datetime.now().strftime('%Y-%m-%d'),
            'return_date': '',
            'notes': notes
        }
        
        issue_df = pd.concat([issue_df, pd.DataFrame([new_record])], ignore_index=True)
        issue_df.to_csv(self.issued_file, index=False)
        print(f"Оборудование ID {equipment_id} выдано {issued_to}")
    
    def return_equipment(self, issue_id):
        """Возврат техники"""
        issue_df = pd.read_csv(self.issued_file)
        eq_df = pd.read_csv(self.equipment_file)
        
        if issue_id not in issue_df['id'].values:
            print("Запись о выдаче с таким ID не найдена!")
            return
            
        equipment_id = issue_df.loc[issue_df['id'] == issue_id, 'equipment_id'].values[0]
        
        # Обновляем статус оборудования
        eq_df.loc[eq_df['id'] == equipment_id, 'status'] = 'Доступно'
        eq_df.to_csv(self.equipment_file, index=False)
        
        # Обновляем запись о выдаче
        issue_df.loc[issue_df['id'] == issue_id, 'return_date'] = datetime.now().strftime('%Y-%m-%d')
        issue_df.to_csv(self.issued_file, index=False)
        print(f"Оборудование ID {equipment_id} возвращено на склад")
    
    def export_to_excel(self, filename='equipment_inventory.xlsx'):
        """Экспорт данных в Excel файл"""
        with pd.ExcelWriter(filename) as writer:
            # Экспорт списка оборудования
            eq_df = pd.read_csv(self.equipment_file)
            eq_df.to_excel(writer, sheet_name='Оборудование', index=False)
            
            # Экспорт истории выдачи
            issue_df = pd.read_csv(self.issued_file)
            issue_df.to_excel(writer, sheet_name='Выдачи', index=False)
        
        print(f"Данные экспортированы в файл: {filename}")
    
    def show_available_equipment(self):
        """Показать доступное оборудование"""
        df = pd.read_csv(self.equipment_file)
        available = df[df['status'] == 'Доступно']
        if available.empty:
            print("Нет доступного оборудования")
        else:
            print("Доступное оборудование:")
            print(available[['id', 'type', 'model', 'serial_number']])
    
    def show_issued_equipment(self):
        """Показать выданное оборудование"""
        eq_df = pd.read_csv(self.equipment_file)
        issue_df = pd.read_csv(self.issued_file)
        
        # Объединяем данные
        merged = pd.merge(
            issue_df[issue_df['return_date'] == ''],
            eq_df,
            left_on='equipment_id',
            right_on='id',
            suffixes=('_issue', '_equipment')
        )
        
        if merged.empty:
            print("Нет выданного оборудования")
        else:
            print("Выданное оборудование:")
            print(merged[['equipment_id', 'type', 'model', 'issued_to', 'department', 'issue_date']])

def main():
    inventory = EquipmentInventory()
    
    while True:
        print("\nСистема учета техники")
        print("1. Добавить новое оборудование")
        print("2. Выдать оборудование")
        print("3. Вернуть оборудование")
        print("4. Показать доступное оборудование")
        print("5. Показать выданное оборудование")
        print("6. Экспорт в Excel")
        print("7. Выход")
        
        choice = input("Выберите действие: ")
        
        if choice == '1':
            print("\nДобавление нового оборудования:")
            equipment = {
                'type': input("Тип оборудования: "),
                'model': input("Модель: "),
                'serial_number': input("Серийный номер: "),
                'purchase_date': input("Дата покупки (ГГГГ-ММ-ДД): "),
                'cost': float(input("Стоимость: ")),
                'status': 'Доступно',
                'location': input("Место хранения: ")
            }
            inventory.add_equipment(equipment)
        
        elif choice == '2':
            print("\nВыдача оборудования:")
            inventory.show_available_equipment()
            equipment_id = int(input("ID оборудования для выдачи: "))
            issued_to = input("ФИО сотрудника: ")
            department = input("Отдел: ")
            notes = input("Примечания (не обязательно): ")
            inventory.issue_equipment(equipment_id, issued_to, department, notes)
        
        elif choice == '3':
            print("\nВозврат оборудования:")
            inventory.show_issued_equipment()
            issue_id = int(input("ID записи о выдаче для возврата: "))
            inventory.return_equipment(issue_id)
        
        elif choice == '4':
            inventory.show_available_equipment()
        
        elif choice == '5':
            inventory.show_issued_equipment()
        
        elif choice == '6':
            filename = input("Имя файла для экспорта (по умолчанию equipment_inventory.xlsx): ") or 'equipment_inventory.xlsx'
            inventory.export_to_excel(filename)
        
        elif choice == '7':
            print("Выход из программы")
            break
        
        else:
            print("Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    main()