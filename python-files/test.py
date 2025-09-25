import time
user_input = input('Дрочишь? (да/нет): ')

if user_input.lower() == 'да':
    print('Не отвлекайся')
#elif user_input.lower() == 'no':
#    print('Не пизди')
else:
    print('Не пизди')
time.sleep(10)