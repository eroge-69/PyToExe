import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical

# Функция для преобразования числа в блок
def number_to_block(n):
    if 0 <= n <= 5: return 0
    elif 6 <= n <= 11: return 1
    elif 12 <= n <= 17: return 2
    elif 18 <= n <= 23: return 3
    elif 24 <= n <= 29: return 4
    elif 30 <= n <= 37: return 5
    else: return -1  # Для невалидных значений

# Функция для нормализации чисел
def normalize_number(n):
    return n / 37.0

# Создание модели нейросети
model = Sequential()
model.add(Dense(32, input_dim=9, activation='relu'))  # Скрытый слой
model.add(Dense(16, activation='relu'))              # Дополнительный скрытый слой
model.add(Dense(6, activation='softmax'))            # Выходной слой (6 блоков)

model.compile(
    loss='categorical_crossentropy',
    optimizer='adam',
    metrics=['accuracy']
)

# Списки для хранения истории ввода
X_history = []
y_history = []

print("Нейросеть для предсказания блока следующей цифры (0-37)")
print("Блоки: 0-5, 6-11, 12-17, 18-23, 24-29, 30-37")
print("Введите 'exit' для выхода\n")

# Основной цикл взаимодействия с пользователем
while True:
    # Ввод последовательности из 9 цифр
    sequence = []
    for i in range(9):
        while True:
            value = input(f"Введите цифру {i+1}/9: ")
            if value.lower() == 'exit':
                exit()
            
            try:
                num = int(value)
                if 0 <= num <= 37:
                    sequence.append(normalize_number(num))
                    break
                else:
                    print("Число должно быть от 0 до 37!")
            except ValueError:
                print("Ошибка: введите целое число!")
    
    # Преобразование в numpy array
    X_current = np.array([sequence])
    
    # Предсказание блока
    prediction = model.predict(X_current, verbose=0)
    predicted_block = np.argmax(prediction) + 1
    print(f"\nПредсказание: следующая цифра будет в блоке {predicted_block}")
    
    # Ввод 10-й цифры
    while True:
        value = input("Введите 10-ю цифру для обучения: ")
        if value.lower() == 'exit':
            exit()
        
        try:
            num10 = int(value)
            if 0 <= num10 <= 37:
                break
            else:
                print("Число должно быть от 0 до 37!")
        except ValueError:
            print("Ошибка: введите целое число!")
    
    # Определение правильного блока
    true_block = number_to_block(num10)
    
    # Обновление истории
    X_history.append(sequence)
    y_history.append(true_block)
    
    # Преобразование меток в one-hot encoding
    y_train = to_categorical(y_history, num_classes=6)
    
    # Обучение модели на всех данных
    model.fit(
        np.array(X_history), 
        y_train,
        epochs=20,
        batch_size=16,
        verbose=0
    )
    
    # Проверка точности
    true_block_name = true_block + 1
    accuracy = 100 if predicted_block == true_block_name else 0
    print(f"Правильный блок: {true_block_name}")
    print(f"Точность предсказания: {accuracy}%")
    print(f"Всего примеров для обучения: {len(X_history)}\n")
