def month_to_season(month_number):
    month_number = int(input('Введите название месяца:'))
    
    if month_number in (1, 2, 12):
        return 'Зима'

    elif month_number in (3, 4, 5):
        return 'Весна'

    elif month_number in (6, 7, 8):
        return 'Лето'

    elif month_number in (9, 10, 11):
        return 'Осень'

    else:
        return 'Некорректный номер месяца'


print(month_to_season(1-12))

       
        
