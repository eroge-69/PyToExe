import time
import random
import string
print("начало загрузки")
time.sleep(5)

# Генерируем случайную строку длиной 10000 символов
распоковка = ''.join(random.choices(
    string.ascii_letters + string.digits + string.punctuation + " ", 
    k=10000
))



# Вызываем исключение
raise ValueError(распоковка)
