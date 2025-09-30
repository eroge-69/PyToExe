import numpy as np
import cv2
import rasterio
from ultralytics import YOLO
import ezdxf
from shapely.geometry import LineString, Point, box
import rasterio.sample
def convert_geotiff_to_jpg(input_geotiff, output_jpg):
    with rasterio.open(input_geotiff) as src:
        band = src.read()  # Чтение всех каналов изображения в массив
        num_bands = band.shape[0]
        print(f'Количество каналов: {num_bands}')

        if num_bands >= 3:
            rgb_bands = band[[2, 1, 0]]  # Смена порядка каналов
            array = np.transpose(rgb_bands, (1, 2, 0))

            if array.dtype == np.float32 or array.dtype == np.float64:
                array = (array - np.min(array)) / (np.max(array) - np.min(array)) * 255
                array = array.astype(np.uint8)

            cv2.imwrite(output_jpg, array)
        else:
            print("Изображение не содержит достаточное количество каналов для RGB данных, пожалуйста, проверьте файл")

    return src.transform


def pixel_to_geo(transform, pixel_x, pixel_y):
    """Преобразование пиксельных координат в географические."""
    pos_x, pos_y = transform * (pixel_x, pixel_y)
    return pos_x, pos_y


def get_polylines_and_texts(dwg_file):
    doc = ezdxf.readfile(dwg_file)
    polylines = []
    texts = []

    for entity in doc.modelspace().query('LWPOLYLINE'):
        points = entity.get_points()
        polylines.append(LineString([(pt[0], pt[1]) for pt in points]))

    for entity in doc.modelspace().query('TEXT'):
        texts.append({
            'point': Point(entity.dxf.insert.x, entity.dxf.insert.y),
            'text': entity.dxf.text
        })

    return polylines, texts


def find_intersections(frame, polyline):
    intersections = frame.intersection(polyline)
    return intersections


def find_nearest_text(intersection, texts):
    nearest_text = None
    min_distance = float('inf')

    for text in texts:
        distance = intersection.distance(text['point'])
        if distance < min_distance:
            nearest_text = text
            min_distance = distance

    return nearest_text


def main():
    input_geotiff = input("Введите путь к GeoTIFF файлу: без ковычек")
    output_jpg = "converted_image.jpg"
    transform = convert_geotiff_to_jpg(input_geotiff, output_jpg)

    # Загружаем модель YOLO
    model = YOLO("best.pt")
    results = model(output_jpg)

    # Получаем DWG файл
    dwg_file = input("Введите путь к DXF файлу: без ковычек")
    polylines, texts = get_polylines_and_texts(dwg_file)

    # Обработка результатов
    for result in results:
        for box_data in result.boxes.data:
            x1 = int(box_data[0])  # x1
            y1 = int(box_data[1])  # y1
            x2 = int(box_data[2])  # x2
            y2 = int(box_data[3])  # y2

            # Преобразуем в географические координаты
            geo_top_left = pixel_to_geo(transform, x1, y1)
            geo_bottom_right = pixel_to_geo(transform, x2, y2)

            # Создаем рамку от географических координат
            frame = box(geo_top_left[0], geo_top_left[1], geo_bottom_right[0], geo_bottom_right[1])
            #print(frame)
            for polyline in polylines:
                intersection = find_intersections(frame, polyline)

                if not intersection.is_empty:  # Если есть пересечение
                    # Если intersection - это LineString, берем его координаты
                    if isinstance(intersection, LineString):
                        for coord in intersection.coords:
                            nearest_text = find_nearest_text(Point(coord), texts)
                            if nearest_text:
                                print(f"Класс: {result.names[int(box_data[5])]}, "
                                      f"Географические координаты пересечения: ({coord[0]}, {coord[1]}), "
                                      f"Метраж: {nearest_text['text']}")


if __name__ == "__main__":
    main()
