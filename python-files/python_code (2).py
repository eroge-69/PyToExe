import re
to = input("Введи тех.описание:").lower()
#to = 'Кабель; парной скрутки с круглым поперечным сечением; структура без пустот, с заполнением из негигроскопичных материалов (Ex); без брони; индивидуальное экранирование пар/троек (ИЭ); общий экран (ОЭ); изоляция оболочки из поливинилхлоридного пластиката пониженной горючести; не распространяющий горение при групповой прокладке по категории А (нг(А)); с пониженным дымо- и газовыделением (LS); Жила медная луженая; не ниже 2 класса по ГОСТ 22483-2021; Номинальное напряжение переменного тока до 0,5 кВ; Номинальное напряжение постоянного тока до 0,75 кВ; Температура окружающей среды от минус 60 °C до плюс 42 °C при эксплуатации; Минимальная температура прокладки кабеля, без предварительного подогрева - минус 25 °C; Цвет наружного покрова: синий; Маркировка жил: черный/BK(+), белый/WH(-) в паре; -; пронумерованные пары/тройки; количество жил: 2x2; номинальное сечение жил 1,0 мм2; Стойкий к воздействию солнечного излучения (Ф); Исполнение по ГОСТ Р МЭК 60079-14-2013, п. 9.3.2; Ёмкостное сопротивление между проводниками пары не более 0,14 скФ/км, при частоте 1 кГц; Индуктивность проводников одной пары на витке не более 0,9 мГн/км; -; -; -; Срок службы 30 лет; Хранение на открытой площадке не менее 2 лет / Тип 2i Ex (ОЭ)(ИЭ) нг(А)-LS Ф ХЛ; -;- 2x2x1,0'.lower()
name = ["" for i in range(30)]
if len(to.split(";")) > 3:
    to_part = to.split(";")
elif len(to.split(",")) > 3:
    to_part = to.split(",")
elif len(to.split(".")) > 3:
    to_part = to.split(".")
#print(to_part)
ex = False
hf = False
ls = False
n8 = False
name[1] = "МК"
if 'ex' in to or 'ех' in to or 'негигроскопичных' in to or 'термостойкий' in to:
    name[0] = 'ЭТМИКАБ '  
    ex = True
else:
    name[4] = 'Ш'
    
for cl in to_part:
    
    if ex == True and ('изоляция' in cl and 'из' in cl) or ('изоляцией' in cl and 'из' in cl):
        if ('поливинилхлоридного' in cl) or ('ПВХ' in cl):
            name[2] = 'В'
        elif 'безгалогенная' in cl:
            name[2] = 'П'
            hf = True
        elif 'сшитый полиолефин' in cl or 'сшитого полиолефина' in cl:
            name[2] = 'Пс'
        elif 'кремнийорганическая резина' in cl or 'кремнийорганической резины' in cl:
            name[2] = 'Ро'
        elif 'этиленпропиленовая резина' in cl or 'этиленпропиленовой резины' in cl:
            name[2] = 'Рк'
        elif 'термопластичный' in cl or 'термопластичного' in cl:
            print('3')
            name[2] = 'Т'

    if 'индивидуальное' in cl or 'с индивидуальным' in cl or 'индивидуальными' in cl or 'индивидуальный' in cl:
        if ex == True:
            if 'алюмофлекс' in cl and 'комбинированный' in cl:
                name[24] = ' Эк '
            elif 'луженых' in to or 'лужёных' in to:
                name[24] = "Эл"
            elif'алюмофлекс' in cl:
                name[24] = ' Эф '
            else:
                name[24] = ' Эф '
        else:
            name[3] = 'Э'
            if ('оплётка' in cl and 'луженых' in cl) or ('оплетка' in cl and 'луженых' in cl):
                    name[22] = 'э'
            if 'оплетка' in cl or 'оплётка' in cl:
                    name[22] = 'эм'
            else:
                name[22] = 'эа'
            
                
        
    if 'общий экран' in cl or 'с общим экраном' in cl or ('с общим' in cl and 'экраном' in cl):
          if ex == True:
              if ('алюмофлекс' in cl and 'комбинированный' in cl) or ('алюмофлекс' in cl and 'комбинированным' in cl):
                  name[3] = 'Эк'
              elif 'луженых' in to or 'лужёных' in to:
                  name[3] = "Эл"
              elif'алюмофлекс' in cl:
                  name[3] = 'Эф'
              else:
                  name[3] = 'Эф'
          else:
            name[3] = 'Э'
            if ('оплётка' in cl and 'луженых' in cl) or ('оплетка' in cl and 'луженых' in cl):
                    name[24] = 'Л '
            if 'оплетка' in cl or 'оплётка' in cl:
                    name[24] = 'Э '
            else:
                name[24] = 'Эа '

    if 'пониженным'in cl and 'дымо'in cl :
        name[12] = 'LS '
        ls = True
        name[8] = 'В'
    
    if 'огнестойкий'in cl or 'Огнестойикий'in cl:
        name[11] = 'FR'
    
    if 'жила' in cl and ('лужёная' in cl or 'луженая' in cl):
        name[21] = "л "
    if ('стойкий' in cl and "(ф)" in cl) or ('солнечного излучения' in cl):
        name[25] = "УФ "
    if 'цвет наружного' in cl:
        if cl.split(':') != '':
            name[29] = cl.split(':')[1]
        elif cl.split(';') != '':
            name[29] = cl.split(';')[1]
        elif cl.split('-') != '':
            name[29] = cl.split('-')[1]
    if 'безгалогенная' in cl or 'безгалогенной' in cl:
        hf = True
        name[9] = 'П'
    if 'хл' in cl:
        name[13] = '-ХЛ '
    if 'водоблокировка' in cl or 'водоблокировкой' in cl:
        pass
    if 'броня' in cl or 'бронёй' in cl or 'броней' in cl:
        if 'проволоки' in cl or 'проволокой' in cl or 'проволкой' in cl or 'проволок' in cl:
            name[8] = 'К'
        else:
            name[8] = 'Б'
    if 'пониженной пожарной опасности' in cl:
        ls = True
    if 'номинальное сечение' in cl or 'номинальным сечением' in cl:
        z = re.findall(r"\d+", cl)
        counter = 0
        for a in z:
            name[17] += a
            if counter == 0:
                name[17] += '.'
                counter += 1
        name[17] = name[17][:-1]
        
    if 'количество' in cl and 'жил' in cl:
        if cl.split(':') != '':
            name[15] = cl.split(':')[1] + 'x'
        elif cl.split(';') != '':
            name[15] = cl.split(';')[1] + 'x'
        elif cl.split('-') != '':
            name[15] = cl.split('-')[1] + 'x'
    if '' in cl:
        pass
    if 'общей' in cl and 'скрутки' in cl:
        n8 = True
name[10] = 'нг(А)-'
if n8 == True:
    name[8] = ''
if hf == False and ls == False:
    name[9] = "Т"
if hf == True:
    name[12] = 'HF'
if ex == False and name[24] != '' and name[22] != '':
    name[14] = '('
    name[23] = ')'
end_name = ''
for i in name:
    if i != '':
        end_name += i
print(end_name)