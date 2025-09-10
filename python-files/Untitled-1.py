with open('C:\Users\user\Desktop\Doc.txt', 'w', encoding='utf-8') as f:
    f.write('Это первая строка.\n')
    f.write('Это вторая строка.\n')
    lines = ['Третья строка\n', 'Четвертая строка\n']
    f.writelines(lines)