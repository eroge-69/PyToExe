import sys
import json

sys.path.extend(['.', '..'])

#Создаём пустой словарь
#TODO: Возможно лучше использовать словарь словарей?
mb_dict = {}

class Record:
     def __init__(self, list):
          self.name = list[1]
          self.type = list[2]
          self.access = list[3]
          self.min = list[4]
          self.max = list[5]
          self.read_err = list[6]
          self.write_err = list[7]
          self.all = list[1:]
          print(f"Создана запись под адресом: {list[0]}")

#TODO: Скрипт сильно зависит от построчной формы записи словаря(modbus) в .c файле
#TODO: Лучше переделать + добавить больше проверок для надёжности
def dict_create(filename):
    #Флаг нахождения словаря в файле
    dict_finded = False

    with open(filename) as file:
        #Перебор всех строк в .c файле
        for line in file:
                #Если первая запись словаря(modbus) найдена:
                if dict_finded:
                    #Проверка на правильное обрамление структуры
                    record_start = line.find('{')
                    record_end = line.find('}')
                    if record_start == -1 or record_end == -1: continue

                    #Убираем всё по бокам от структуры
                    line = line[record_start+1:record_end]
                    
                    #Убираем пробелы, запятые и разделяем строку в список
                    rec_list = line.split(',')
                    rec_list = [rec.strip() for rec in rec_list]
                    rec_list[2] = rec_list[2].removeprefix("mb_")

                    print(rec_list[2])
                    
                    #Создаём объект записи и добавлем его в словарь(python)
                    #Модбасовский адрес становиться ключом
                    record = Record(tuple(rec_list))
                    mb_dict[int(rec_list[0])] = record.all

                #Поиск строки с первой записью в словаре
                if line.find('MB_FIRST_UNSUPPORTED_RECORD,') != -1 :
                    dict_finded = True
    return dict_finded

def dict_to_json(dict, filename='mb_dict.json'):
    #Сериализуем и форматируем словарь в JSON формат
    #открываем/создаём JSON файл и записываем в него словарь
    with open(filename, 'w') as f:
        json.dump(dict, fp=f, sort_keys=True, indent=0)
    return

def dict_read(filename='mb_dict.json'):
    with open(filename, 'r') as f:
        obj = json.load(f)
    return dict(obj)
     
if __name__ == '__main__':
    try:
        if len(sys.argv) > 1:
            if dict_create(sys.argv[1]) == False:
            #Если после перебора так и не был найден словарь, то пишем об этом и завершаем скрипт
                print("❌: Словарь не найден.")
                sys.exit()
        else:
            print("❌: Необходим путь к файлу в качестве аргумента.")
            sys.exit()
        dict_to_json(mb_dict)
        #print(dict_read())
    
    except Exception as e:
        print(f"❌ Неопознаная ошибка, обратитесь к разработчику: {e}")
        sys.exit(1)
    
    except FileNotFoundError:
        print("❌: Файл не найден.")
        sys.exit()