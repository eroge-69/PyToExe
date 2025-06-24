import cv2
import numpy as np
import pymem
import pymem.process
import dxcam
import torch
import torch.nn as nn
from torchvision import transforms
from collections import deque
import keyboard
import time

# ИИ-модель для предсказания позиций
class PositionPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.fc1 = nn.Linear(64 * 16 * 16, 256)
        self.fc2 = nn.Linear(256, 4)  # x, y, confidence, time_offset
        
    def forward(self, x):
        x = torch.relu(self.conv1(x))
        x = nn.MaxPool2d(2)(x)
        x = torch.relu(self.conv2(x))
        x = nn.MaxPool2d(2)(x)
        x = x.view(x.size(0), -1)
        x = torch.relu(self.fc1(x))
        return self.fc2(x)

# Загрузка предобученной модели
model = PositionPredictor()
model.load_state_dict(torch.load('ai_cheat_model.pth'))
model.eval()

# Инициализация захвата экрана
camera = dxcam.create(output_idx=0, output_color="BGR")
region = (0, 0, 1920, 1080)  # Подстройте под разрешение экрана

# Инициализация доступа к памяти игры
pm = pymem.Pymem("DeltaForceClient-Win64-Shipping.exe")
game_module = None
for module in pymem.process.list_modules(pm.process_handle):
    if "deltaforce" in module.name.lower():
        game_module = module.lpBaseOfDll
        break

if not game_module:
    raise Exception("Основной модуль игры не найден")

# Поиск указателя на контроллер игрока
player_controller_ptr = pm.read_uint(game_module + 0x00A3F7C)
local_player = pm.read_uint(player_controller_ptr + 0x1B8)

# Конфигурация ИИ-чита
PREDICTION_TIME = 0.5  # Предсказание на 500 мс вперед
HISTORY_SIZE = 10      # История позиций для анализа

# Очередь для отслеживания истории позиций
position_history = deque(maxlen=HISTORY_SIZE)

def predict_enemy_position(frame):
    """Анализ кадра и предсказание позиций врагов"""
    transform = transforms.Compose([
        transforms.ToPILImage(),
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    frame_tensor = transform(frame).unsqueeze(0)
    with torch.no_grad():
        predictions = model(frame_tensor)
    
    # Фильтрация предсказаний
    valid_predictions = []
    for i in range(predictions.shape[1]):
        x, y, conf, t_offset = predictions[0, i].tolist()
        if conf > 0.7:  # Порог уверенности
            valid_predictions.append({
                'x': int(x * frame.shape[1]),
                'y': int(y * frame.shape[0]),
                'confidence': conf,
                'time_offset': t_offset
            })
    
    return valid_predictions

def get_local_player_position():
    """Получение позиции локального игрока"""
    return {
        'x': pm.read_float(local_player + 0x1C),
        'y': pm.read_float(local_player + 0x20),
        'z': pm.read_float(local_player + 0x24)
    }

def aim_at_position(target_x, target_y):
    """Автоматическое наведение на цель"""
    player_pos = get_local_player_position()
    
    # Расчет углов для наведения
    dx = target_x - player_pos['x']
    dy = target_y - player_pos['y']
    yaw = np.arctan2(dy, dx) * (180 / np.pi)
    
    # Запись угла в память игры
    pm.write_float(local_player + 0x40, float(yaw))

def main_loop():
    print("ИИ-чит активирован. Нажмите END для выхода")
    last_time = time.time()
    
    while not keyboard.is_pressed('end'):
        # Захват экрана
        frame = camera.grab(region=region)
        if frame is None: 
            continue
            
        # Анализ кадра нейросетью
        predictions = predict_enemy_position(frame)
        
        # Выбор наиболее опасной цели
        if predictions:
            main_target = max(predictions, key=lambda x: x['confidence'])
            
            # Автонаведение с упреждением
            aim_at_position(main_target['x'], main_target['y'])
            
            # Автоматический выстрел при высокой уверенности
            if main_target['confidence'] > 0.9:
                pm.write_int(game_module + 0x1B8820, 1)  # Симуляция нажатия огня
        
        # Контроль FPS
        current_time = time.time()
        elapsed = current_time - last_time
        if elapsed < 0.05:  # 20 FPS
            time.sleep(0.05 - elapsed)
        last_time = current_time
    
    print("ИИ-чит деактивирован")

if __name__ == "__main__":
    main_loop()