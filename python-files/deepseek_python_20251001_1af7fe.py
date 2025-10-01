def create_html_directory(input_file, output_file):
    # Читаем данные из файла
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Начало HTML-документа
    html_content = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Справочник сотрудников</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                text-align: center;
                color: #333;
                margin-bottom: 30px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            th, td {
                padding: 12px 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }
            th {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
            }
            tr:hover {
                background-color: #f5f5f5;
            }
            .email {
                color: #0066cc;
            }
            .no-data {
                color: #999;
                font-style: italic;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .search-box {
                padding: 8px;
                width: 300px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Справочник сотрудников</h1>
                <input type="text" id="searchInput" class="search-box" placeholder="Поиск сотрудника..." onkeyup="searchTable()">
            </div>
            <table id="employeesTable">
                <thead>
                    <tr>
                        <th>ФИО</th>
                        <th>Номер кабинета</th>
                        <th>Должность</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Обрабатываем каждую строку файла
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split(',')
        
        # Обрабатываем данные (может быть от 3 до 4 частей)
        name = parts[0].strip() if len(parts) > 0 else ""
        room = parts[1].strip() if len(parts) > 1 else ""
        position = parts[2].strip() if len(parts) > 2 else ""
        email = parts[3].strip() if len(parts) > 3 else ""
        
        # Форматируем строку таблицы
        html_content += f'<tr>'
        html_content += f'<td>{name if name else "<span class=\"no-data\">Не указано</span>"}</td>'
        html_content += f'<td>{room if room else "<span class=\"no-data\">-</span>"}</td>'
        html_content += f'<td>{position if position else "<span class=\"no-data\">Не указана</span>"}</td>'
        
        if email:
            html_content += f'<td><a href="mailto:{email}" class="email">{email}</a></td>'
        else:
            html_content += f'<td><span class="no-data">Не указан</span></td>'
        
        html_content += f'</tr>\n'
    
    # Завершение HTML-документа с JavaScript для поиска
    html_content += """
                </tbody>
            </table>
            
            <script>
                function searchTable() {
                    const input = document.getElementById('searchInput');
                    const filter = input.value.toLowerCase();
                    const table = document.getElementById('employeesTable');
                    const tr = table.getElementsByTagName('tr');
                    
                    for (let i = 1; i < tr.length; i++) {
                        const td = tr[i].getElementsByTagName('td');
                        let found = false;
                        
                        for (let j = 0; j < td.length; j++) {
                            if (td[j]) {
                                const txtValue = td[j].textContent || td[j].innerText;
                                if (txtValue.toLowerCase().indexOf(filter) > -1) {
                                    found = true;
                                    break;
                                }
                            }
                        }
                        
                        if (found) {
                            tr[i].style.display = '';
                        } else {
                            tr[i].style.display = 'none';
                        }
                    }
                }
            </script>
        </div>
    </body>
    </html>
    """
    
    # Записываем HTML в файл
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f"HTML-справочник успешно создан: {output_file}")

# Использование программы
if __name__ == "__main__":
    input_filename = "AD_Users_Export.txt"
    output_filename = "employee_directory.html"
    
    create_html_directory(input_filename, output_filename)