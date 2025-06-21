import re
import csv

def extract_upd_data(text):
    # Разделяем текст на отдельные УПД по уникальному разделителю
    delimiter = "Приложение № 1 к постановлению Правительства Российской Федерации от 26.12.2011 № 1137"
    parts = text.split(delimiter)
    # Первый элемент пустой, берем следующие 20 УПД
    upd_list = parts[1:21]  
    
    results = []
    for upd in upd_list:
        try:
            # Извлекаем номер и дату УПД
            invoice_match = re.search(r'Счет-фактура №\s*(\d+)\s*от\s*(\d{2}\.\d{2}\.\d{4})', upd)
            invoice_number = invoice_match.group(1) if invoice_match else ""
            invoice_date = invoice_match.group(2) if invoice_match else ""

            # Извлекаем продавца
            seller_match = re.search(r'Продавец\t(.*?)\t\(2\)', upd)
            seller = seller_match.group(1).strip() if seller_match else ""

            # Извлекаем покупателя
            buyer_match = re.search(r'Покупатель\t(.*?)\t\(6\)', upd)
            buyer = buyer_match.group(1).strip() if buyer_match else ""

            # Извлекаем данные товара
            product_match = re.search(r'Бетон М-350[^\n]*', upd)
            if product_match:
                product_line = product_match.group()
                cols = [col.strip() for col in product_line.split('\t') if col.strip()]
                
                # Проверяем количество колонок и извлекаем данные
                if len(cols) >= 13:
                    unit = cols[5] if len(cols) > 5 else ""
                    quantity = cols[6] if len(cols) > 6 else ""
                    price = cols[7] if len(cols) > 7 else ""
                    total_without_tax = cols[8] if len(cols) > 8 else ""
                    tax_rate = cols[10] if len(cols) > 10 else ""
                    tax_sum = cols[11] if len(cols) > 11 else ""
                    total_with_tax = cols[12] if len(cols) > 12 else ""
                else:
                    unit = quantity = price = total_without_tax = tax_rate = tax_sum = total_with_tax = ""
            else:
                unit = quantity = price = total_without_tax = tax_rate = tax_sum = total_with_tax = ""

            # Извлекаем транспортную накладную
            transport_match = re.search(r'Транспортная накладная № \d+ от \d{1,2} \w+ \d{4} г\.', upd)
            transport = transport_match.group() if transport_match else ""

            # Формируем запись
            results.append([
                invoice_number, invoice_date, seller, buyer, "Бетон М-350",
                unit, quantity, price, total_without_tax, tax_rate,
                tax_sum, total_with_tax, transport
            ])
        except Exception as e:
            print(f"Ошибка обработки УПД: {str(e)}")
            continue
            
    return results

# Чтение файла
with open('Бетон 22.txt', 'r', encoding='utf-8') as file:
    content = file.read()

# Извлечение данных
data = extract_upd_data(content)

# Запись в CSV
headers = [
    '№ УПД', 'Дата', 'Продавец', 'Покупатель', 'Товар', 
    'Ед. изм.', 'Кол-во', 'Цена за ед. (₽)', 'Сумма без НДС (₽)',
    'Ставка НДС', 'Сумма НДС (₽)', 'Всего с НДС (₽)', 
    'Транспортная накладная'
]

with open('upd_report.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(headers)
    writer.writerows(data)