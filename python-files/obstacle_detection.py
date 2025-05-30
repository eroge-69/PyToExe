import numpy as np
import cv2

# Настройки для камеры
MIN_CONTOUR_AREA = 150       # Минимальный размер объекта
DOT_COLOR = (0, 0, 255)      # Красный цвет маркера
CROSSHAIR_COLOR = (0, 255, 0) # Зеленый цвет перекрестия
DETECTION_ZONE_COLOR = (255, 0, 0, 0.2) # Синий цвет зоны обнаружения
DOT_RADIUS = 6               # Размер точки
FONT_SCALE = 0.6             # Размер шрифта
FONT_THICKNESS = 2           # Толщина шрифта
LINE_THICKNESS = 2           # Толщина линий
UPPER_ZONE_HEIGHT = 30       # Зона выше перекрестия (в пикселях)

# Инициализация камеры
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)

def draw_detection_zone(frame, center_x, center_y):
    """Рисует зону обнаружения от перекрестия до низа экрана + небольшую область выше"""
    h, w = frame.shape[:2]
    
    # Создаем прозрачный слой для зоны обнаружения
    overlay = frame.copy()
    cv2.rectangle(overlay, 
                 (0, center_y - UPPER_ZONE_HEIGHT),  # Начинаем немного выше перекрестия
                 (w, h),                             # До самого низа кадра
                 DETECTION_ZONE_COLOR, -1)
    
    # Наложение с прозрачностью
    cv2.addWeighted(overlay, 0.2, frame, 0.8, 0, frame)
    
    # Рисуем границы зоны
    cv2.rectangle(frame,
                 (0, center_y - UPPER_ZONE_HEIGHT),
                 (w, h),
                 DETECTION_ZONE_COLOR, 1)

def draw_crosshair(frame, center_x, center_y):
    """Рисует перекрестие в центре кадра"""
    size = 20
    # Горизонтальная линия
    cv2.line(frame, (center_x - size, center_y), 
             (center_x + size, center_y), CROSSHAIR_COLOR, LINE_THICKNESS)
    # Вертикальная линия
    cv2.line(frame, (center_x, center_y - size), 
             (center_x, center_y + size), CROSSHAIR_COLOR, LINE_THICKNESS)

def is_near(contour_area, frame_area):
    """Определяет, находится ли объект в радиусе 1 метра"""
    return (contour_area / frame_area) > 0.0035  # Эмпирическая формула

def process_frame(frame, center_x, center_y):
    """Обрабатывает кадр и отмечает препятствия в зоне обнаружения"""
    frame_area = frame.shape[0] * frame.shape[1]
    
    # Улучшенная обработка изображения
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    edges = cv2.Canny(blurred, 30, 100)
    
    # Улучшение контуров
    kernel = np.ones((3,3), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    
    # Поиск контуров
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) < MIN_CONTOUR_AREA:
            continue
            
        x, y, w, h = cv2.boundingRect(contour)
        obj_center_y = y + h//2
        
        # Проверяем что объект в зоне обнаружения (от чуть выше перекрестия до низа)
        # и в радиусе 1 метра
        if (obj_center_y > center_y - UPPER_ZONE_HEIGHT and 
            is_near(cv2.contourArea(contour), frame_area)):
            
            # Центр объекта для маркировки
            obj_center = (x + w//2, y + h//2)
            
            # Рисуем точку
            cv2.circle(frame, obj_center, DOT_RADIUS, DOT_COLOR, -1)
            
            # Подпись "OBSTACLE" со смещением
            text_offset = 15
            cv2.putText(frame, "OBSTACLE", 
                       (obj_center[0] + text_offset, obj_center[1]),
                       cv2.FONT_HERSHEY_SIMPLEX, FONT_SCALE, 
                       DOT_COLOR, FONT_THICKNESS)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    h, w = frame.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    # Рисуем зону обнаружения (от перекрестия до низа + немного выше)
    draw_detection_zone(frame, center_x, center_y)
    
    # Рисуем перекрестие
    draw_crosshair(frame, center_x, center_y)
    
    # Обработка кадра
    process_frame(frame, center_x, center_y)
    
    # Информационная строка
    cv2.putText(frame, "Detecting obstacles", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    
    # Отображение результата
    cv2.imshow('Wi-Fi video communication with obstacle detection', frame)
    
    if cv2.waitKey(1) == 27:  # Выход по ESC
        break

cap.release()
cv2.destroyAllWindows()