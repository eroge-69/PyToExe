import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy.signal import convolve2d
from typing import List, Tuple
import os
from collections import defaultdict
import tkinter as tk
from tkinter import filedialog, messagebox


def find_largest_table(image, padding=40):
    """Находит самый большой прямоугольник, похожий на таблицу, и добавляет внешний отступ"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours:
        perimeter = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * perimeter, True)

        if len(approx) == 4:
            # Получаем координаты вершин
            pts = approx.reshape(4, 2)

            # Вычисляем центр прямоугольника
            center = pts.mean(axis=0)

            # Сдвигаем каждую точку НАРУЖУ на `padding` пикселей
            direction = pts - center  # Вектор от центра к вершине
            norm = np.linalg.norm(direction, axis=1)
            direction = direction / norm[:, np.newaxis]  # Нормализуем

            padded_pts = pts + direction * padding

            # Ограничиваем, чтобы не выйти за границы изображения
            padded_pts[:, 0] = np.clip(padded_pts[:, 0], 0, image.shape[1] - 1)  # X
            padded_pts[:, 1] = np.clip(padded_pts[:, 1], 0, image.shape[0] - 1)  # Y

            return padded_pts.astype(np.int32)

    return None


def order_points(pts):
    """Упорядочивает точки для преобразования перспективы"""
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    
    return rect

def perspective_transform(image, pts):
    """Выполняет преобразование перспективы"""
    rect = order_points(pts)
    (tl, tr, br, bl) = rect
    
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    max_width = max(int(width_a), int(width_b))
    
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    max_height = max(int(height_a), int(height_b))
    
    dst = np.array([
        [0, 0],
        [max_width - 1, 0],
        [max_width - 1, max_height - 1],
        [0, max_height - 1]], dtype="float32")
    
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (max_width, max_height))
    
    return warped

def detect_header(table_image):
    """Определяет шапку таблицы (самую узкую строку)"""
    gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Определяем горизонтальные линии
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
    detect_horizontal = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)
    
    # Находим контуры горизонтальных линий
    cnts, _ = cv2.findContours(detect_horizontal, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(cnts) < 2:
        return None, False  # Не найдено достаточно строк
    
    # Сортируем строки по вертикальной позиции
    cnts = sorted(cnts, key=lambda c: cv2.boundingRect(c)[1])
    
    # Определяем самую узкую строку (вероятно, это шапка)
    header_idx = np.argmin([cv2.boundingRect(c)[3] for c in cnts[:3]])  # Проверяем только первые 3 строки
    header_rect = cv2.boundingRect(cnts[header_idx])
    
    # Проверяем, находится ли шапка в верхней трети таблицы
    is_header_on_top = header_rect[1] < table_image.shape[0] / 3
    
    return header_rect, is_header_on_top

def find_intersection_points(table_image, min_distance=20):
    """
    Находит точки пересечения линий в таблице (включая углы)

    Параметры:
        table_image: изображение таблицы (после перспективного преобразования)
        min_distance: минимальное расстояние между точками для их объединения

    Возвращает:
        Список точек пересечения (x, y)
    """
    gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Определяем горизонтальные линии
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
    horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel, iterations=2)

    # Определяем вертикальные линии
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel, iterations=2)

    # Создаем маску пересечений
    intersections = cv2.bitwise_and(horizontal_lines, vertical_lines)

    # Находим центры пересечений
    intersections = cv2.dilate(intersections, None)

    # Находим контуры пересечений
    cnts, _ = cv2.findContours(intersections, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Вычисляем центроиды контуров
    points = []
    for cnt in cnts:
        if cv2.contourArea(cnt) > 10:  # Игнорируем маленькие области
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                points.append((cx, cy))

    # Удаляем близко расположенные точки (дубликаты)
    unique_points = []
    for point in points:
        is_unique = True
        for unique_point in unique_points:
            if np.sqrt((point[0]-unique_point[0])**2 + (point[1]-unique_point[1])**2) < min_distance:
                is_unique = False
                break
        if is_unique:
            unique_points.append(point)

    return unique_points

def sort_points(points):
    """
    Сортирует точки в порядке слева-направо, сверху-вниз
    с группировкой по строкам
    """
    # Сначала сортируем по Y (вертикальная координата)
    points_sorted = sorted(points, key=lambda p: p[1])
    
    # Затем группируем по строкам и сортируем каждую строку по X
    sorted_rows = []
    current_row = [points_sorted[0]]
    
    for point in points_sorted[1:]:
        # Если Y отличается более чем на 10 пикселей - новая строка
        if abs(point[1] - current_row[-1][1]) > 10:
            sorted_rows.append(sorted(current_row, key=lambda p: p[0]))
            current_row = [point]
        else:
            current_row.append(point)
    
    # Добавляем последнюю строку
    sorted_rows.append(sorted(current_row, key=lambda p: p[0]))
    
    # Преобразуем в плоский список
    return [point for row in sorted_rows for point in row]

def count_dark_pixels_in_quadrilateral(
    gray_image: np.ndarray,
    points: List[Tuple[int, int]],
    threshold: int = 50,
    padding: int = 50,
    debug: bool = True
) -> int:

    # Проверяем, что ровно 4 точки
    if len(points) != 4:
        raise ValueError("Функция требует ровно 4 точки для задания четырехугольника")

    # Если изображение уже BGR (3 канала), конвертируем в grayscale
    if len(gray_image.shape) == 3 and gray_image.shape[2] == 3:
        gray_image_for_processing = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image_for_processing = gray_image.copy()

    # Для отладки используем оригинальное изображение (если оно BGR) или конвертируем
    debug_image = gray_image.copy() if (debug and len(gray_image.shape) == 3) else None
    if debug and debug_image is None:
        debug_image = cv2.cvtColor(gray_image_for_processing, cv2.COLOR_GRAY2BGR)

    # Преобразуем точки в формат для OpenCV
    pts = np.array(points, dtype=np.int32)
    
    # Создаем уменьшенный четырехугольник с учетом отступа
    if padding > 0:
        # Вычисляем центр четырехугольника
        center = np.mean(pts, axis=0)
        
        # Смещаем каждую точку к центру на величину отступа
        direction_vectors = center - pts
        norms = np.linalg.norm(direction_vectors, axis=1)
        normalized_directions = direction_vectors / norms[:, np.newaxis]
        
        # Убедимся, что отступ не слишком большой
        min_distance = np.min(norms)
        actual_padding = min(padding, min_distance * 0.9)
        
        pts_padded = pts + normalized_directions * actual_padding
        pts_padded = pts_padded.astype(np.int32)
    else:
        pts_padded = pts

    # Создаем маску для области (1 внутри, 0 снаружи)
    mask = np.zeros(gray_image_for_processing.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [pts_padded], color=255)

    # Находим пиксели, которые:
    # 1) Лежат внутри маски (mask > 0)
    # 2) Их значение < threshold
    dark_pixels_mask = (gray_image_for_processing < threshold) & (mask > 0)
    dark_pixels_count = np.sum(dark_pixels_mask)

    # Визуализация (если debug=True)
    if debug:
        # Закрашиваем всю область полупрозрачным синим
        overlay = debug_image.copy()
        cv2.fillPoly(overlay, [pts], color=(255, 0, 0))
        cv2.addWeighted(overlay, 0.3, debug_image, 0.7, 0, debug_image)
        
        # Закрашиваем область с отступом полупрозрачным зеленым
        if padding > 0:
            overlay_padded = debug_image.copy()
            cv2.fillPoly(overlay_padded, [pts_padded], color=(0, 255, 0))
            cv2.addWeighted(overlay_padded, 0.2, debug_image, 0.8, 0, debug_image)

        # Помечаем темные пиксели красным
        debug_image[dark_pixels_mask] = (0, 0, 255)

        # Рисуем контур исходной области (зеленый)
        cv2.polylines(debug_image, [pts], isClosed=True, color=(0, 255, 0), thickness=2)
        
        # Рисуем контур области с отступом (желтый)
        if padding > 0:
            cv2.polylines(debug_image, [pts_padded], isClosed=True, color=(0, 255, 255), thickness=2)

        # Добавляем текст с информацией
        #text = f"Dark pixels: {dark_pixels_count} (threshold={threshold}, padding={padding})"
        #cv2.putText(debug_image, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        # Показываем результат
        #cv2.imshow('Debug View: Dark Pixels in Quadrilateral', debug_image)
        #cv2.waitKey(4000)

    return int(dark_pixels_count)

def count_and_visualize_non_white_pixels(
    image: np.ndarray,
    zone_points: np.ndarray,
    inward_offset: int,
    white_threshold: int = 255,
    show_plots: bool = True
) -> int:
    """Подсчитывает количество небелых пикселей в указанной зоне изображения с возможным отступом.
    
    Args:
        image: Входное изображение (2D для grayscale или 3D для RGB)
        zone_points: Точки полигона, определяющего зону
        inward_offset: Отступ внутрь зоны (в пикселях)
        white_threshold: Порог для определения белых пикселей
        show_plots: Флаг для отображения визуализации
        
    Returns:
        Количество небелых пикселей в зоне
    """
    # Проверка входных данных
    if len(image.shape) not in (2, 3):
        raise ValueError("Изображение должно быть 2D (grayscale) или 3D (RGB)")
    
    h, w = image.shape[:2]
    
    # 1. Оптимизированное создание маски зоны
    poly_path = Path(zone_points)
    # Используем более эффективное создание координатной сетки
    y_coords, x_coords = np.indices((h, w))
    coords = np.column_stack((x_coords.ravel(), y_coords.ravel()))
    mask = poly_path.contains_points(coords).reshape((h, w))
    
    # 2. Оптимизированная эрозия
    if inward_offset > 0:
        # Используем бинарную эрозию с оптимальным ядром
        kernel_size = 2 * inward_offset + 1
        kernel = np.ones((kernel_size, kernel_size), dtype=bool)
        # Используем mode='same' и boundary='fill', fillvalue=0 для более точной эрозии
        conv = convolve2d(mask, kernel.astype(float), mode='same', boundary='fill', fillvalue=0)
        eroded_mask = (conv == kernel.sum())
    else:
        eroded_mask = mask
    
    # 3. Оптимизированное определение небелых пикселей
    if len(image.shape) == 3:
        is_white = np.all(image >= white_threshold, axis=2)
    else:
        is_white = image >= white_threshold
    
    non_white_pixels = eroded_mask & ~is_white
    count = np.count_nonzero(non_white_pixels)  # Быстрее, чем sum() для булевых массивов
    
    return count


def process_table(image_path, output_path=None):
    """Основная функция обработки таблицы"""
    # Загрузка изображения
    image = cv2.imread(image_path)
    if image is None:
        print("Ошибка: Не удалось загрузить изображение")
        return None
    
    # Находим и выравниваем таблицу
    table_contour = find_largest_table(image)
    if table_contour is None:
        print("Таблица не обнаружена")
        return None
    
    table_contour = table_contour.reshape(4, 2)
    warped = perspective_transform(image, table_contour)
    
    # Определяем шапку таблицы
    header_rect, is_header_on_top = detect_header(warped)
    
    # Если шапка не вверху, переворачиваем таблицу
    if header_rect is not None and not is_header_on_top:
        warped = cv2.rotate(warped, cv2.ROTATE_180)
        print("Таблица перевернута, чтобы шапка оказалась сверху")
    
    # Находим точки пересечения линий
    intersection_points = sort_points(find_intersection_points(warped))
    #print(intersection_points)
    za = np.array([intersection_points[6], intersection_points[7], intersection_points[9], intersection_points[8]])
    protiv = np.array([intersection_points[8], intersection_points[9], intersection_points[13], intersection_points[12]])
    count_pr = 20800
    count_za = 4100
    print(count_za, count_dark_pixels_in_quadrilateral(warped, za))
    print(count_pr, count_dark_pixels_in_quadrilateral(warped, protiv))
    if (count_dark_pixels_in_quadrilateral(warped, za) - count_za < 300) and (count_dark_pixels_in_quadrilateral(warped, protiv) - count_pr > 300):
        return 1
    elif (count_dark_pixels_in_quadrilateral(warped, za) - count_za > 300) and (count_dark_pixels_in_quadrilateral(warped, protiv) - count_pr < 300):
        return -1
    else:
        return 0
    # Сохранение результата


def process_folder(folder_path):
    """
    Обрабатывает все изображения в указанной папке с помощью process_table()
    и возвращает количество каждого из возвращаемых значений (1, 0, -1)

    Args:
        folder_path (str): Путь к папке с изображениями для обработки

    Returns:
        dict: Словарь с количеством каждого результата {'1': count, '0': count, '-1': count}
    """
    # Инициализируем счетчик
    counts = {"1": 0, "0": 0, "-1": 0}

    try:
        # Нормализуем путь (убираем двойные слеши и т.д.)
        folder_path = os.path.normpath(folder_path)

        # Проверяем, существует ли папка
        if not os.path.exists(folder_path):
            print(f"Ошибка: Путь {folder_path} не существует")
            return dict(counts)

        if not os.path.isdir(folder_path):
            print(f"Ошибка: {folder_path} не является папкой")
            return dict(counts)

        # Допустимые расширения изображений
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp', '.tif'}

        # Перебираем все файлы в папке
        for filename in os.listdir(folder_path):
            try:
                # Полный путь к файлу
                file_path = os.path.join(folder_path, filename)

                # Дополнительная проверка на случай проблем с символами в пути
                if not os.path.exists(file_path):
                    print(f"Предупреждение: Файл {file_path} недоступен, пропускаем")
                    continue

                # Проверяем что это файл (а не подпапка)
                if not os.path.isfile(file_path):
                    continue

                # Получаем расширение файла в нижнем регистре
                _, file_ext = os.path.splitext(filename)
                file_ext = file_ext.lower()

                if file_ext in image_extensions:
                    try:
                        # Обрабатываем файл
                        result = process_table(file_path)
                        print(f"Обработан файл: {file_path}")

                        # Увеличиваем счетчик для соответствующего результата
                        if result in (1, 0, -1):
                            counts[str(result)] += 1
                    except Exception as e:
                        print(f"Ошибка при обработке файла {file_path}: {str(e)}")
                else:
                    print(f"Пропускаем файл {file_path} - не изображение или неподдерживаемый формат")

            except Exception as e:
                print(f"Ошибка при обработке элемента {filename}: {str(e)}")

    except Exception as e:
        print(f"Критическая ошибка при обработке папки {folder_path}: {str(e)}")

    return dict(counts)

#print(process_folder(rf"{input()}"))

def select_path():
    """Открывает проводник для выбора пути"""
    path = filedialog.askdirectory()
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)


def process_path():
    """Обрабатывает путь и показывает результат в новом окне"""
    path = entry_path.get()
    if not path:
        messagebox.showwarning("Ошибка", "Пожалуйста, выберите путь")
        return

    # Здесь можно заменить на вашу функцию
    res = process_folder(path)
    print(res)
    result = f"Проголосовали ЗА: {res["1"]}\nПроголосовали ПРОТИВ: {res["-1"]}\nНедействительные бюллетени: {res["0"]}"
    # Создаем новое окно для вывода результата
    result_window = tk.Toplevel(root)
    result_window.title("Результат обработки")
    result_window.geometry("400x300")

    text_result = tk.Text(result_window, wrap=tk.WORD)
    text_result.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    text_result.insert(tk.END, result)
    text_result.config(state=tk.DISABLED)  # Запрещаем редактирование

    # Кнопка закрытия окна с результатом
    btn_close = tk.Button(result_window, text="Закрыть", command=result_window.destroy)
    btn_close.pack(pady=10)


def exit_app():
    """Закрывает приложение"""
    root.destroy()


# Создаем главное окно
root = tk.Tk()
root.title("Обработчик путей")
root.geometry("500x150")

# Фрейм для ввода пути
frame_path = tk.Frame(root)
frame_path.pack(pady=10, padx=10, fill=tk.X)

label_path = tk.Label(frame_path, text="Путь:")
label_path.pack(side=tk.LEFT)

entry_path = tk.Entry(frame_path, width=40)
entry_path.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)

btn_browse = tk.Button(frame_path, text="Обзор", command=select_path)
btn_browse.pack(side=tk.LEFT)

# Фрейм для кнопок
frame_buttons = tk.Frame(root)
frame_buttons.pack(pady=10)

btn_process = tk.Button(frame_buttons, text="Ввод", command=process_path)
btn_process.pack(side=tk.LEFT, padx=5)

btn_exit = tk.Button(frame_buttons, text="Выход", command=exit_app)
btn_exit.pack(side=tk.LEFT, padx=5)

root.mainloop()