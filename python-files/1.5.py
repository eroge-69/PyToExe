# -*- coding: utf-8 -*-
import sys
import os
import numpy as np
import cv2
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import threading
import warnings
import json
import csv
import logging
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import pandas as pd

# Отключаем предупреждения
warnings.filterwarnings('ignore')

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mammography_analysis.log'),
        logging.StreamHandler()
    ]
)

class MLModelManager:
    """Менеджер машинного обучения"""
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.selected_model = 'random_forest'
        self.model_trained = False
        self.scaler_fitted = False
        self.feature_columns = ['area', 'compactness', 'solidity', 'contrast', 'energy', 'homogeneity']
        self.load_models()
    
    def load_models(self):
        """Загрузка предварительно обученных моделей"""
        try:
            model_files = {
                'random_forest': 'random_forest_model.pkl',
                'svm': 'svm_model.pkl',
                'logistic_regression': 'logistic_regression_model.pkl'
            }
            
            for model_name, filename in model_files.items():
                if os.path.exists(filename):
                    self.models[model_name] = joblib.load(filename)
                    logging.info(f"Модель {model_name} загружена")
            
            # Загрузка scaler
            if os.path.exists('scaler.pkl'):
                self.scaler = joblib.load('scaler.pkl')
                self.scaler_fitted = True
                logging.info("Scaler загружен")
            
            if self.models:
                self.model_trained = True
                logging.info("Модели успешно загружены")
                
        except Exception as e:
            logging.error(f"Ошибка загрузки моделей: {e}")
    
    def train_models(self, features, labels):
        """Обучение моделей машинного обучения"""
        try:
            # Разделение данных
            X_train, X_test, y_train, y_test = train_test_split(
                features, labels, test_size=0.2, random_state=42
            )
            
            # Масштабирование features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            self.scaler_fitted = True
            
            # Инициализация моделей
            models = {
                'random_forest': RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced'),
                'svm': SVC(kernel='rbf', probability=True, random_state=42, class_weight='balanced'),
                'logistic_regression': LogisticRegression(random_state=42, class_weight='balanced', max_iter=1000)
            }
            
            results = {}
            
            for name, model in models.items():
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
                accuracy = accuracy_score(y_test, y_pred)
                
                self.models[name] = model
                results[name] = {
                    'accuracy': accuracy,
                    'report': classification_report(y_test, y_pred)
                }
                
                # Сохранение модели
                joblib.dump(model, f'{name}_model.pkl')
                logging.info(f"Модель {name} обучена с точностью: {accuracy:.3f}")
            
            self.model_trained = True
            joblib.dump(self.scaler, 'scaler.pkl')
            
            return results
            
        except Exception as e:
            logging.error(f"Ошибка обучения моделей: {e}")
            return None
    
    def prepare_features_for_prediction(self, features_dict):
        """Подготовка признаков для предсказания в правильном порядке"""
        try:
            # Создаем массив признаков в правильном порядке
            prepared_features = []
            for col in self.feature_columns:
                if col in features_dict:
                    value = features_dict[col]
                    # Преобразуем numpy типы в стандартные Python типы
                    if hasattr(value, 'item'):
                        value = value.item()
                    prepared_features.append(float(value))
                else:
                    prepared_features.append(0.0)  # Значение по умолчанию
                    logging.warning(f"Признак {col} отсутствует, используется 0.0")
            
            return np.array([prepared_features])
            
        except Exception as e:
            logging.error(f"Ошибка подготовки признаков: {e}")
            return None
    
    def predict_risk(self, features):
        """Предсказание риска с использованием ML"""
        try:
            if not self.model_trained or self.selected_model not in self.models:
                return self._rule_based_predict(features)
            
            # Подготовка признаков
            features_array = self.prepare_features_for_prediction(features)
            if features_array is None:
                return self._rule_based_predict(features)
            
            # Если scaler не обучен, используем rule-based метод
            if not self.scaler_fitted:
                logging.warning("Scaler не обучен, используется rule-based предсказание")
                return self._rule_based_predict(features)
            
            features_scaled = self.scaler.transform(features_array)
            
            # Предсказание
            model = self.models[self.selected_model]
            
            if hasattr(model, 'predict_proba'):
                probability = model.predict_proba(features_scaled)[0][1]
                return float(probability)
            else:
                prediction = model.predict(features_scaled)[0]
                return float(prediction)
                
        except Exception as e:
            logging.error(f"Ошибка ML предсказания: {e}")
            return self._rule_based_predict(features)
    
    def _rule_based_predict(self, features):
        """Резервное правило-базированное предсказание"""
        try:
            risk_score = 0.0
            
            # Более агрессивные веса для выявления патологий
            weights = {
                'area': 0.35, 
                'compactness': 0.30, 
                'solidity': 0.15,
                'contrast': 0.10,
                'energy': 0.05,
                'homogeneity': 0.05
            }
            
            for feature_name, weight in weights.items():
                if feature_name in features:
                    normalized = self._normalize_feature(feature_name, features[feature_name])
                    risk_score += normalized * weight
            
            # Гарантируем, что риск находится в диапазоне [0, 1]
            risk_score = max(0.0, min(1.0, risk_score))
            
            # Повышаем чувствительность для подозрительных образований
            if 'area' in features and features['area'] > 1000:
                risk_score = min(1.0, risk_score * 1.5)
            if 'compactness' in features and features['compactness'] > 1.5:
                risk_score = min(1.0, risk_score * 1.6)
            if 'solidity' in features and features['solidity'] < 0.7:
                risk_score = min(1.0, risk_score * 1.3)
            if 'contrast' in features and features['contrast'] > 300:
                risk_score = min(1.0, risk_score * 1.4)
                
            return risk_score
            
        except Exception as e:
            logging.error(f"Ошибка rule-based предсказания: {e}")
            return 0.7  # В случае ошибки возвращаем высокий риск
    
    def _normalize_feature(self, feature_name, value):
        """Нормализация значения признака"""
        try:
            # Преобразуем значение в float
            if hasattr(value, 'item'):
                value = value.item()
            value = float(value)
            
            # Более чувствительные диапазоны для выявления патологий
            ranges = {
                'area': (0, 3000, True),           # Большая площадь = выше риск
                'compactness': (0.8, 2.5, True),   # Высокая компактность = выше риск
                'solidity': (0.5, 1.0, False),     # Низкая сплошность = выше риск
                'contrast': (0, 500, True),        # Высокий контраст = выше риск
                'energy': (0, 1, False),           # Низкая энергия = выше риск
                'homogeneity': (0, 1, False)       # Низкая однородность = выше риск
            }
            
            if feature_name not in ranges:
                return 0.5
            
            min_val, max_val, ascending = ranges[feature_name]
            
            if max_val <= min_val:
                return 0.5
            
            # Нормализуем значение в диапазон [0, 1]
            normalized = (value - min_val) / (max_val - min_val)
            normalized = max(0.0, min(1.0, normalized))
            
            if not ascending:
                normalized = 1.0 - normalized
            
            # Увеличиваем чувствительность для крайних значений
            if normalized > 0.8:
                normalized = 0.8 + (normalized - 0.8) * 2.5  # Усиливаем высокие значения
            
            return normalized
            
        except Exception as e:
            logging.error(f"Ошибка нормализации признака {feature_name}: {e}")
            return 0.7  # В случае ошибки возвращаем высокий риск

class SmartFeatures:
    """Класс для вычисления умных признаков"""
    
    @staticmethod
    def calculate_glcm_features(image, distances=[1], angles=[0, np.pi/4, np.pi/2, 3*np.pi/4]):
        """Вычисление признаков GLCM с оптимизацией"""
        features = {}
        try:
            # Уменьшаем разрешение для ускорения
            if image.shape[0] > 128 or image.shape[1] > 128:
                image = cv2.resize(image, (128, 128), interpolation=cv2.INTER_AREA)
            
            # Нормализуем изображение
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Квантование
            quantized = (image // 8).astype(np.uint8)  # Меньше уровней для лучшей статистики
            quantized = np.clip(quantized, 0, 31)  # 32 уровня
            
            glcm_features = []
            
            for distance in distances:
                for angle in angles:
                    # Создаем смещенные изображения
                    dx = int(round(distance * np.cos(angle)))
                    dy = int(round(distance * np.sin(angle)))
                    
                    # Создаем GLCM матрицу
                    glcm = np.zeros((32, 32), dtype=np.float32)
                    
                    # Заполняем GLCM матрицу
                    height, width = quantized.shape
                    for i in range(max(0, -dy), min(height, height - dy)):
                        for j in range(max(0, -dx), min(width, width - dx)):
                            val1 = quantized[i, j]
                            val2 = quantized[i + dy, j + dx]
                            if val1 < 32 and val2 < 32:
                                glcm[val1, val2] += 1
                    
                    # Нормализация
                    glcm_sum = np.sum(glcm)
                    if glcm_sum > 0:
                        glcm /= glcm_sum
                    
                    # Вычисление признаков
                    i_idx, j_idx = np.indices(glcm.shape)
                    
                    # Контраст
                    contrast = np.sum(glcm * (i_idx - j_idx) ** 2)
                    
                    # Энергия (равномерность)
                    energy = np.sum(glcm ** 2)
                    
                    # Однородность
                    homogeneity = np.sum(glcm / (1 + (i_idx - j_idx) ** 2))
                    
                    # Энтропия
                    entropy = -np.sum(glcm * np.log(glcm + 1e-10))
                    
                    glcm_features.extend([contrast, energy, homogeneity, entropy])
            
            # Усреднение по всем направлениям
            if glcm_features:
                num_features = 4  # contrast, energy, homogeneity, entropy
                features['contrast'] = np.mean(glcm_features[::num_features])
                features['energy'] = np.mean(glcm_features[1::num_features])
                features['homogeneity'] = np.mean(glcm_features[2::num_features])
                features['entropy'] = np.mean(glcm_features[3::num_features])
            
        except Exception as e:
            logging.error(f"Ошибка GLCM: {e}")
            features = {'contrast': 200.0, 'energy': 0.3, 'homogeneity': 0.4, 'entropy': 2.0}
        
        return features
    
    @staticmethod
    def calculate_morphological_features(contour):
        """Вычисление морфологических признаков"""
        features = {}
        try:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            
            features['area'] = area
            features['perimeter'] = perimeter
            
            # Компактность (круглость)
            if area > 0 and perimeter > 0:
                features['compactness'] = (perimeter ** 2) / (4 * np.pi * area)
            else:
                features['compactness'] = 0
            
            # Сплошность (отношение площади к площади выпуклой оболочки)
            hull = cv2.convexHull(contour)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                features['solidity'] = area / hull_area
            else:
                features['solidity'] = 0
            
            # Эксцентриситет (форма)
            if len(contour) >= 5:
                try:
                    ellipse = cv2.fitEllipse(contour)
                    major_axis = max(ellipse[1])
                    minor_axis = min(ellipse[1])
                    features['ellipse_major_axis'] = major_axis
                    features['ellipse_minor_axis'] = minor_axis
                    if minor_axis > 0:
                        features['eccentricity'] = np.sqrt(1 - (minor_axis ** 2) / (major_axis ** 2))
                    else:
                        features['eccentricity'] = 0
                except:
                    features['ellipse_major_axis'] = 0
                    features['ellipse_minor_axis'] = 0
                    features['eccentricity'] = 0
            
            # Прямоугольность
            rect = cv2.minAreaRect(contour)
            rect_area = rect[1][0] * rect[1][1]
            if rect_area > 0:
                features['rectangularity'] = area / rect_area
            else:
                features['rectangularity'] = 0
            
        except Exception as e:
            logging.error(f"Ошибка морфологических признаков: {e}")
            features = {'area': 0, 'perimeter': 0, 'compactness': 0, 'solidity': 0}
        
        return features

class IntelligentSegmenter:
    """Умный сегментатор с multiple методами"""
    
    def smart_segmentation(self, image, method='combined'):
        """Сегментация изображения с выбором метода"""
        try:
            # Гауссово размытие для уменьшения шума
            blurred = cv2.GaussianBlur(image, (5, 5), 0)
            
            if method == 'combined':
                # Комбинированный подход: Otsu + морфологические операции
                _, otsu_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                
                # Морфологические операции для очистки
                kernel = np.ones((3, 3), np.uint8)
                cleaned = cv2.morphologyEx(otsu_thresh, cv2.MORPH_CLOSE, kernel)
                cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel)
                
                return cleaned
                
            elif method == 'adaptive':
                return cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY_INV, 11, 2
                )
            elif method == 'otsu':
                _, result = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                return result
            elif method == 'canny':
                edges = cv2.Canny(blurred, 30, 100)
                kernel = np.ones((3, 3), np.uint8)
                return cv2.dilate(edges, kernel, iterations=2)
            else:
                return cv2.adaptiveThreshold(
                    blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY_INV, 11, 2
                )
                
        except Exception as e:
            logging.error(f"Ошибка сегментации: {e}")
            _, result = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV)
            return result

class FeedbackSystem:
    """Система обратной связи для обучения ML"""
    
    def __init__(self):
        self.feedback_file = "feedback_data.csv"
        self.training_file = "training_data.csv"
        self._ensure_files()
    
    def _ensure_files(self):
        """Создание файлов, если они не существуют"""
        # Файл обратной связи
        if not os.path.exists(self.feedback_file):
            with open(self.feedback_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'patient_id', 'patient_fio', 'patient_age', 'breast_density',
                    'image_path', 'predicted_birads', 'actual_birads', 
                    'predicted_risk', 'actual_diagnosis', 'tumor_type', 'features', 'correct_prediction'
                ])
        
        # Файл тренировочных данных для ML
        if not os.path.exists(self.training_file):
            with open(self.training_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'area', 'compactness', 'solidity', 'contrast', 'energy', 'homogeneity',
                    'actual_risk', 'birads_category', 'tumor_type'
                ])
    
    def generate_synthetic_training_data(self, num_samples=500):
        """Генерация синтетических тренировочных данных для начального обучения"""
        try:
            # Генерация реалистичных синтетических данных
            np.random.seed(42)
            
            for i in range(num_samples):
                # Определяем, будет ли это злокачественный случай (20% случаев)
                is_malignant = np.random.random() < 0.2
                
                if is_malignant:
                    # Признаки злокачественных образований
                    area = np.random.uniform(800, 4000)
                    compactness = np.random.uniform(1.5, 3.0)
                    solidity = np.random.uniform(0.4, 0.8)
                    contrast = np.random.uniform(300, 800)
                    energy = np.random.uniform(0.1, 0.4)
                    homogeneity = np.random.uniform(0.3, 0.6)
                    actual_risk = np.random.uniform(0.7, 0.95)
                    birads_category = np.random.choice([4, 5], p=[0.4, 0.6])
                    tumor_type = 'злокачественная'
                else:
                    # Признаки доброкачественных образований
                    area = np.random.uniform(100, 2000)
                    compactness = np.random.uniform(0.8, 2.0)
                    solidity = np.random.uniform(0.7, 0.95)
                    contrast = np.random.uniform(50, 400)
                    energy = np.random.uniform(0.3, 0.8)
                    homogeneity = np.random.uniform(0.5, 0.9)
                    actual_risk = np.random.uniform(0.1, 0.4)
                    birads_category = np.random.choice([1, 2, 3], p=[0.3, 0.4, 0.3])
                    tumor_type = 'доброкачественная' if np.random.random() > 0.3 else 'нормальная'
                
                training_row = [
                    area, compactness, solidity, contrast, energy, homogeneity,
                    actual_risk, birads_category, tumor_type
                ]
                
                with open(self.training_file, 'a', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(training_row)
            
            logging.info(f"Сгенерировано {num_samples} синтетических примеров для обучения")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка генерации синтетических данных: {e}")
            return False
    
    def save_feedback(self, analysis_results, actual_birads, actual_diagnosis, tumor_type, patient_info, image_path):
        """Сохранение обратной связи"""
        try:
            features = {}
            if 'lesions' in analysis_results:
                for i, lesion in enumerate(analysis_results['lesions']):
                    for key, value in lesion.items():
                        if key != 'index' and key != 'risk_score':
                            # Преобразуем numpy типы в стандартные Python типы для сериализации
                            if isinstance(value, (np.float32, np.float64)):
                                value = float(value)
                            elif isinstance(value, (np.int32, np.int64)):
                                value = int(value)
                            features[f'lesion_{i+1}_{key}'] = value
            
            # Парсим actual_birads в числовое значение
            actual_birads_num = self._parse_birads(actual_birads)
            
            feedback_data = {
                'timestamp': datetime.now().isoformat(),
                'patient_id': patient_info.get('patient_id', ''),
                'patient_fio': patient_info.get('fio', ''),
                'patient_age': patient_info.get('age', ''),
                'breast_density': patient_info.get('breast_density', ''),
                'image_path': image_path,
                'predicted_birads': float(analysis_results.get('overall_risk', 0)) * 6,  # Масштабируем до 0-6
                'actual_birads': actual_birads_num,
                'predicted_risk': float(analysis_results.get('overall_risk', 0)),
                'actual_diagnosis': actual_diagnosis,
                'tumor_type': tumor_type,
                'features': json.dumps(features, ensure_ascii=False),
                'correct_prediction': abs(float(analysis_results.get('overall_risk', 0)) - (actual_birads_num / 6)) < 0.15
            }
            
            with open(self.feedback_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(list(feedback_data.values()))
            
            # Также сохраняем для тренировочных данных
            self._save_training_data(analysis_results, actual_birads_num, tumor_type)
            
            return True
        except Exception as e:
            logging.error(f"Ошибка сохранения обратной связи: {e}")
            return False
    
    def _parse_birads(self, birads_str):
        """Парсинг BI-RADS строки в числовое значение"""
        try:
            if isinstance(birads_str, (int, float)):
                return float(birads_str)
            
            if '0' in str(birads_str):
                return 0
            elif '1' in str(birads_str):
                return 1
            elif '2' in str(birads_str):
                return 2
            elif '3' in str(birads_str):
                return 3
            elif '4' in str(birads_str):
                return 4
            elif '5' in str(birads_str):
                return 5
            elif '6' in str(birads_str):
                return 6
            else:
                return 1  # По умолчанию
        except:
            return 1
    
    def _save_training_data(self, analysis_results, actual_birads, tumor_type):
        """Сохранение данных для обучения ML"""
        try:
            if 'lesions' in analysis_results:
                for lesion in analysis_results['lesions']:
                    # Преобразуем tumor_type в числовой формат для обучения
                    tumor_numeric = 2 if 'злокачествен' in str(tumor_type).lower() else (1 if 'доброкачествен' in str(tumor_type).lower() else 0)
                    
                    training_row = [
                        float(lesion.get('area', 0)),
                        float(lesion.get('compactness', 0)),
                        float(lesion.get('solidity', 0)),
                        float(lesion.get('contrast', 0)),
                        float(lesion.get('energy', 0)),
                        float(lesion.get('homogeneity', 0)),
                        float(lesion.get('risk_score', 0)),
                        float(actual_birads),
                        tumor_numeric
                    ]
                    
                    with open(self.training_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(training_row)
                        
        except Exception as e:
            logging.error(f"Ошибка сохранения тренировочных данных: {e}")

class MarkerVisualizer:
    """Класс для визуализации маркеров на изображении"""
    
    @staticmethod
    def draw_markers_on_image(original_image, contours, risk_scores):
        """Рисует маркеры на изображении с разными цветами в зависимости от уровня риска"""
        try:
            if len(original_image.shape) == 2:
                marked_image = cv2.cvtColor(original_image, cv2.COLOR_GRAY2BGR)
            else:
                marked_image = original_image.copy()
            
            for i, (contour, risk_score) in enumerate(zip(contours, risk_scores)):
                if risk_score > 0.7:
                    color = (0, 0, 255)  # Красный - высокий риск
                    thickness = 3
                elif risk_score > 0.5:
                    color = (0, 100, 255)  # Оранжевый - средний риск
                    thickness = 2
                elif risk_score > 0.3:
                    color = (0, 255, 255)  # Желтый - низкий риск
                    thickness = 2
                else:
                    color = (0, 255, 0)  # Зеленый - очень низкий риск
                    thickness = 1
                
                cv2.drawContours(marked_image, [contour], -1, color, thickness)
                
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    
                    label = f"{i+1}: {risk_score:.0%}"
                    cv2.putText(marked_image, label, (cX-25, cY-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    cv2.circle(marked_image, (cX, cY), 6, color, -1)
            
            return marked_image
            
        except Exception as e:
            logging.error(f"Ошибка при рисовании маркеров: {e}")
            return original_image

class IntelligentAnalysisSystem:
    def __init__(self):
        self.feature_extractor = SmartFeatures()
        self.segmenter = IntelligentSegmenter()
        self.ml_manager = MLModelManager()
        self.feedback_system = FeedbackSystem()
        self.visualizer = MarkerVisualizer()
    
    def analyze_mammogram(self, image_path, patient_info=None):
        """Анализ маммограммы с ML"""
        try:
            image = self._load_image(image_path)
            if image is None:
                return {'success': False, 'error': 'Не удалось загрузить изображение'}
            
            original_image = image.copy()
            processed = self._preprocess_image(image)
            segmented = self.segmenter.smart_segmentation(processed, method='combined')
            analysis_results = self._analyze_lesions(processed, segmented)
            marked_image = self._visualize_analysis(original_image, analysis_results)
            report = self._generate_report(analysis_results, patient_info)
            
            return {
                'success': True,
                'report': report,
                'analysis': analysis_results,
                'marked_image': marked_image,
                'image_path': image_path
            }
            
        except Exception as e:
            logging.error(f"Ошибка анализа: {e}")
            return {'success': False, 'error': str(e)}
    
    def train_ml_models(self, use_synthetic_data=True):
        """Обучение ML моделей на исторических данных"""
        try:
            if not os.path.exists(self.feedback_system.training_file):
                if use_synthetic_data:
                    # Генерация синтетических данных
                    self.feedback_system.generate_synthetic_training_data(200)
                else:
                    return {"success": False, "error": "Нет данных для обучения"}
            
            # Загрузка данных с обработкой ошибок формата
            try:
                data = pd.read_csv(self.feedback_system.training_file)
            except pd.errors.ParserError as e:
                logging.error(f"Ошибка чтения CSV файла: {e}")
                # Создаем новый корректный файл
                self._recreate_training_file()
                if use_synthetic_data:
                    self.feedback_system.generate_synthetic_training_data(200)
                    data = pd.read_csv(self.feedback_system.training_file)
                else:
                    return {"success": False, "error": "Ошибка формата данных. Создан новый файл."}
            
            if len(data) < 20:
                if use_synthetic_data:
                    # Догенерация данных если мало
                    additional_samples = 100 - len(data)
                    self.feedback_system.generate_synthetic_training_data(additional_samples)
                    data = pd.read_csv(self.feedback_system.training_file)
                else:
                    return {"success": False, "error": "Недостаточно данных для обучения"}
            
            # Подготовка features и labels
            feature_columns = self.ml_manager.feature_columns
            
            # Проверяем наличие всех необходимых колонок
            missing_columns = [col for col in feature_columns if col not in data.columns]
            if missing_columns:
                logging.warning(f"Отсутствующие колонки: {missing_columns}")
                # Создаем недостающие колонки со значениями по умолчанию
                for col in missing_columns:
                    data[col] = 0.0
            
            # Проверяем наличие целевых колонок
            if 'birads_category' not in data.columns:
                data['birads_category'] = 1  # Значение по умолчанию
            
            if 'actual_risk' not in data.columns:
                data['actual_risk'] = 0.1  # Значение по умолчанию
            
            # Фильтруем некорректные данные и преобразуем в числа
            data = data.dropna()
            
            # Преобразуем все числовые колонки в float
            for col in feature_columns + ['actual_risk', 'birads_category']:
                if col in data.columns:
                    data[col] = pd.to_numeric(data[col], errors='coerce')
            
            # Удаляем строки с NaN значениями после преобразования
            data = data.dropna()
            
            features = data[feature_columns].values
            # Используем actual_risk как целевую переменную для регрессии
            labels = (data['actual_risk'] > 0.5).astype(int).values  # Бинарная классификация
            
            # Проверяем, что есть данные для обучения
            if len(np.unique(labels)) < 2:
                logging.warning("Недостаточно разнообразных данных для обучения")
                if use_synthetic_data:
                    self.feedback_system.generate_synthetic_training_data(200)
                    data = pd.read_csv(self.feedback_system.training_file)
                    
                    # Повторно преобразуем в числа
                    for col in feature_columns + ['actual_risk', 'birads_category']:
                        if col in data.columns:
                            data[col] = pd.to_numeric(data[col], errors='coerce')
                    data = data.dropna()
                    
                    features = data[feature_columns].values
                    labels = (data['actual_risk'] > 0.5).astype(int).values
            
            # Обучение моделей
            results = self.ml_manager.train_models(features, labels)
            
            if results:
                return {"success": True, "results": results, "samples_used": len(data)}
            else:
                return {"success": False, "error": "Ошибка обучения моделей"}
                
        except Exception as e:
            logging.error(f"Ошибка обучения ML: {e}")
            return {"success": False, "error": str(e)}
    
    def _recreate_training_file(self):
        """Пересоздание файла тренировочных данных"""
        try:
            # Создаем резервную копию поврежденного файла
            if os.path.exists(self.feedback_system.training_file):
                backup_name = f"{self.feedback_system.training_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.feedback_system.training_file, backup_name)
                logging.info(f"Создана резервная копия поврежденного файла: {backup_name}")
            
            # Создаем новый корректный файл
            with open(self.feedback_system.training_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'area', 'compactness', 'solidity', 'contrast', 'energy', 'homogeneity',
                    'actual_risk', 'birads_category', 'tumor_type'
                ])
            
            logging.info("Создан новый корректный файл тренировочных данных")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка пересоздания файла: {e}")
            return False
    
    def _load_image(self, image_path):
        """Загрузка изображения"""
        try:
            if not os.path.exists(image_path):
                return None
            
            # Загрузка обычных изображений
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                # Попытка загрузки через PIL для других форматов
                try:
                    pil_image = Image.open(image_path).convert('L')
                    image = np.array(pil_image)
                except Exception as e:
                    logging.error(f"Ошибка загрузки изображения через PIL: {e}")
                    return None
            
            if image is None:
                return None
            
            if image.dtype != np.uint8:
                image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # Сохраняем оригинальный размер для вычислений, но работаем с уменьшенной копией для скорости
            self.original_size = image.shape
            
            if max(image.shape) > 1024:
                scale = 1024 / max(image.shape)
                new_width = int(image.shape[1] * scale)
                new_height = int(image.shape[0] * scale)
                image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            return image
            
        except Exception as e:
            logging.error(f"Ошибка загрузки изображения: {e}")
            return None
    
    def _preprocess_image(self, image):
        """Предобработка изображения"""
        try:
            # Нормализация
            image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            
            # CLAHE для улучшения контраста
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(image)
            
            # Медианный фильтр для уменьшения шума
            denoised = cv2.medianBlur(enhanced, 5)
            
            # Гауссово размытие для сглаживания
            blurred = cv2.GaussianBlur(denoised, (5, 5), 0)
            
            return blurred
        except Exception as e:
            logging.error(f"Ошибка предобработки: {e}")
            return image
    
    def _analyze_lesions(self, image, mask):
        """Анализ образований с ML"""
        analysis = {
            'total_lesions': 0,
            'suspicious_lesions': 0,
            'lesions': [],
            'contours': [],
            'risk_scores': [],
            'overall_risk': 0.0
        }
        
        try:
            # Находим контуры
            contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Фильтруем маленькие контуры (шум)
            min_area = max(50, image.shape[0] * image.shape[1] * 0.0001)  # Динамический порог
            large_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
            
            analysis['total_lesions'] = len(large_contours)
            
            total_risk = 0.0
            max_risk = 0.0
            valid_lesions = 0
            
            # Сортируем контуры по площади (от большего к меньшему)
            large_contours.sort(key=cv2.contourArea, reverse=True)
            
            for i, contour in enumerate(large_contours[:10]):  # Анализируем до 10 самых больших образований
                try:
                    # Морфологические признаки
                    morph_features = self.feature_extractor.calculate_morphological_features(contour)
                    
                    # Создаем маску для текущего контура
                    contour_mask = np.zeros_like(image)
                    cv2.drawContours(contour_mask, [contour], -1, 255, -1)
                    
                    # Извлекаем область изображения внутри контура
                    roi = cv2.bitwise_and(image, image, mask=contour_mask)
                    
                    # Текстуральные признаки GLCM
                    glcm_features = self.feature_extractor.calculate_glcm_features(roi)
                    
                    # Объединяем все признаки
                    all_features = {**morph_features, **glcm_features}
                    
                    # ML предсказание риска
                    risk_score = self.ml_manager.predict_risk(all_features)
                    
                    # Сохраняем информацию об образовании
                    lesion_info = {
                        'index': i + 1,
                        'area': morph_features.get('area', 0),
                        'compactness': morph_features.get('compactness', 0),
                        'solidity': morph_features.get('solidity', 0),
                        'contrast': glcm_features.get('contrast', 0),
                        'energy': glcm_features.get('energy', 0),
                        'homogeneity': glcm_features.get('homogeneity', 0),
                        'risk_score': risk_score
                    }
                    
                    analysis['lesions'].append(lesion_info)
                    analysis['contours'].append(contour)
                    analysis['risk_scores'].append(risk_score)
                    
                    if risk_score > 0.5:
                        analysis['suspicious_lesions'] += 1
                    
                    # Взвешиваем риск по площади и обновляем общий риск
                    area_weight = morph_features.get('area', 0) / (image.shape[0] * image.shape[1])
                    weighted_risk = risk_score * min(area_weight * 50, 1.0)  # Более агрессивное взвешивание
                    
                    total_risk += weighted_risk
                    max_risk = max(max_risk, risk_score)
                    valid_lesions += 1
                    
                except Exception as e:
                    logging.error(f"Ошибка анализа образования {i+1}: {e}")
                    continue
            
            # Вычисляем общий риск - используем максимальный риск и средневзвешенный
            if valid_lesions > 0:
                # Более агрессивная комбинация: 60% максимального риска + 40% средневзвешенный
                weighted_avg = total_risk / valid_lesions
                analysis['overall_risk'] = min(0.6 * max_risk + 0.4 * weighted_avg, 0.99)
            else:
                analysis['overall_risk'] = 0.01  # Минимальный риск при отсутствии образований
            
            return analysis
            
        except Exception as e:
            logging.error(f"Ошибка анализа образований: {e}")
            return analysis
    
    def _visualize_analysis(self, original_image, analysis_results):
        """Визуализация результатов анализа"""
        try:
            marked_image = self.visualizer.draw_markers_on_image(
                original_image, 
                analysis_results['contours'], 
                analysis_results['risk_scores']
            )
            return marked_image
        except Exception as e:
            logging.error(f"Ошибка визуализации: {e}")
            return original_image
    
    def _generate_report(self, analysis_results, patient_info):
        """Генерация отчета"""
        try:
            overall_risk = analysis_results.get('overall_risk', 0.0)
            
            # Более чувствительная классификация BI-RADS
            if overall_risk >= 0.85:
                birads = "BI-RADS 5"
                recommendation = "ВЫСОКАЯ ВЕРОЯТНОСТЬ ЗЛОКАЧЕСТВЕННОСТИ. Необходима немедленная биопсия и консультация онколога."
            elif overall_risk >= 0.65:
                birads = "BI-RADS 4"
                recommendation = "ПОДОЗРИТЕЛЬНЫЕ ИЗМЕНЕНИЯ. Рекомендуется биопсия и дополнительное обследование."
            elif overall_risk >= 0.35:
                birads = "BI-RADS 3"
                recommendation = "ВЕРОЯТНО ДОБРОКАЧЕСТВЕННЫЕ ИЗМЕНЕНИЯ. Рекомендуется наблюдение через 3-6 месяцев."
            elif overall_risk >= 0.15:
                birads = "BI-RADS 2"
                recommendation = "ДОБРОКАЧЕСТВЕННЫЕ ИЗМЕНЕНИЯ. Рекомендуется плановое наблюдение."
            else:
                birads = "BI-RADS 1"
                recommendation = "НОРМА. Рекомендуется плановое наблюдение."
            
            report = {
                'patient_info': patient_info or {},
                'analysis_summary': {
                    'total_lesions': analysis_results.get('total_lesions', 0),
                    'suspicious_lesions': analysis_results.get('suspicious_lesions', 0),
                    'overall_risk': overall_risk,
                    'birads_category': birads,
                    'recommendation': recommendation
                },
                'detailed_analysis': analysis_results.get('lesions', []),
                'timestamp': datetime.now().isoformat()
            }
            
            return report
            
        except Exception as e:
            logging.error(f"Ошибка генерации отчета: {e}")
            return {'error': 'Ошибка генерации отчета'}

class MammographyAnalyzerGUI:
    """GUI для анализа маммограмм"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Intelligent Mammography Analysis System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        self.system = IntelligentAnalysisSystem()
        self.current_image_path = None
        self.current_marked_image = None
        self.patient_info = {}
        self.last_report = None  # Для хранения последнего отчета
        
        self._setup_gui()
        self._setup_menu()
        
        # Автоматическое обучение моделей при запуске
        self._auto_train_models()
    
    def _auto_train_models(self):
        """Автоматическое обучение моделей при запуке"""
        def train_in_background():
            try:
                result = self.system.train_ml_models(use_synthetic_data=True)
                if result['success']:
                    logging.info(f"Модели успешно обучены на {result['samples_used']} примерах")
                else:
                    logging.warning(f"Автообучение не удалось: {result['error']}")
            except Exception as e:
                logging.error(f"Ошибка автообучения: {e}")
        
        threading.Thread(target=train_in_background, daemon=True).start()
    
    def _setup_menu(self):
        """Настройка меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Меню файла
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Открыть изображение", command=self.load_image)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню анализа
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Анализ", menu=analysis_menu)
        analysis_menu.add_command(label="Запустить анализ", command=self.run_analysis)
        analysis_menu.add_command(label="Обучить модели", command=self.train_models)
        
        # Меню помощи
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Помощь", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def _setup_gui(self):
        """Настройка интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Конфигурация весов
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Панель пациента
        patient_frame = ttk.LabelFrame(main_frame, text="Информация о пациенте", padding="5")
        patient_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(patient_frame, text="ФИО:").grid(row=0, column=0, sticky=tk.W)
        self.fio_entry = ttk.Entry(patient_frame, width=30)
        self.fio_entry.grid(row=0, column=1, padx=(5, 0))
        
        ttk.Label(patient_frame, text="Возраст:").grid(row=0, column=2, sticky=tk.W, padx=(10, 0))
        self.age_entry = ttk.Entry(patient_frame, width=10)
        self.age_entry.grid(row=0, column=3, padx=(5, 0))
        
        ttk.Label(patient_frame, text="ID:").grid(row=0, column=4, sticky=tk.W, padx=(10, 0))
        self.id_entry = ttk.Entry(patient_frame, width=15)
        self.id_entry.grid(row=0, column=5, padx=(5, 0))
        
        ttk.Label(patient_frame, text="Плотность груди:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.density_var = tk.StringVar(value="B")
        density_combo = ttk.Combobox(patient_frame, textvariable=self.density_var, 
                                   values=["A", "B", "C", "D"], width=5)
        density_combo.grid(row=1, column=1, padx=(5, 0), pady=(10, 0))
        
        # Панель изображения
        image_frame = ttk.LabelFrame(main_frame, text="Изображение", padding="5")
        image_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        image_frame.columnconfigure(0, weight=1)
        image_frame.rowconfigure(0, weight=1)
        
        self.image_label = ttk.Label(image_frame, text="Загрузите изображение для анализа", 
                                   background='white', anchor='center')
        self.image_label.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Панель результатов
        result_frame = ttk.LabelFrame(main_frame, text="Результаты анализа", padding="5")
        result_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(1, weight=1)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(result_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Текстовое поле для результатов
        self.result_text = tk.Text(result_frame, height=20, width=50, wrap=tk.WORD)
        result_scroll = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=result_scroll.set)
        
        self.result_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        result_scroll.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Панель кнопок
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(button_frame, text="Загрузить изображение", 
                  command=self.load_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Анализировать", 
                  command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обучить модели", 
                  command=self.train_models).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить отчет", 
                  command=self.save_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Обратная связь", 
                  command=self.show_feedback_dialog).pack(side=tk.LEFT, padx=5)
    
    def load_image(self):
        """Загрузка изображения"""
        file_path = filedialog.askopenfilename(
            title="Выберите маммограмму",
            filetypes=[
                ("Изображения", "*.png *.jpg *.jpeg *.tiff *.tif *.bmp *.dcm"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.status_var.set(f"Загружено: {os.path.basename(file_path)}")
            
            # Показываем превью
            try:
                image = Image.open(file_path)
                image.thumbnail((400, 400))
                photo = ImageTk.PhotoImage(image)
                self.image_label.configure(image=photo)
                self.image_label.image = photo
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить изображение: {e}")
    
    def run_analysis(self):
        """Запуск анализа"""
        if not self.current_image_path:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение")
            return
        
        self.status_var.set("Анализ выполняется...")
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Выполняется анализ...\nПожалуйста, подождите.")
        
        # Сбор информации о пациенте
        self.patient_info = {
            'fio': self.fio_entry.get(),
            'age': self.age_entry.get(),
            'patient_id': self.id_entry.get(),
            'breast_density': self.density_var.get()
        }
        
        # Запуск анализа в отдельном потоке
        def analyze():
            try:
                result = self.system.analyze_mammogram(self.current_image_path, self.patient_info)
                
                if result['success']:
                    self.current_marked_image = result['marked_image']
                    self.last_report = result  # Сохраняем отчет для обратной связи
                    self.display_results(result['report'])
                    self.show_marked_image()
                    self.status_var.set("Анализ завершен успешно")
                else:
                    self.status_var.set("Ошибка анализа")
                    messagebox.showerror("Ошибка", result['error'])
                    
            except Exception as e:
                self.status_var.set("Ошибка анализа")
                messagebox.showerror("Ошибка", f"Ошибка при анализе: {e}")
        
        threading.Thread(target=analyze, daemon=True).start()
    
    def display_results(self, report):
        """Отображение результатов"""
        self.result_text.delete(1.0, tk.END)
        
        summary = report.get('analysis_summary', {})
        risk = summary.get('overall_risk', 0.0)
        
        result_text = f"РЕЗУЛЬТАТЫ АНАЛИЗА\n"
        result_text += f"Время анализа: {report.get('timestamp', 'N/A')}\n\n"
        
        result_text += f"ОБЩАя ОЦЕНКА РИСКА: {risk:.1%}\n"
        result_text += f"Категория BI-RADS: {summary.get('birads_category', 'N/A')}\n\n"
        
        result_text += f"ОБНАРУЖЕНО ОБРАЗОВАНИЙ: {summary.get('total_lesions', 0)}\n"
        result_text += f"Подозрительных образований: {summary.get('suspicious_lesions', 0)}\n\n"
        
        result_text += f"РЕКОМЕНДАЦИИ:\n{summary.get('recommendation', 'N/A')}\n\n"
        
        # Детальная информация об образованиях
        lesions = report.get('detailed_analysis', [])
        if lesions:
            result_text += "ДЕТАЛЬНЫЙ АНАЛИЗ ОБРАЗОВАНИЙ:\n"
            for i, lesion in enumerate(lesions):
                result_text += f"\nОбразование {i+1}:\n"
                result_text += f"  Площадь: {lesion.get('area', 0):.1f} px²\n"
                result_text += f"  Компактность: {lesion.get('compactness', 0):.3f}\n"
                result_text += f"  Сплошность: {lesion.get('solidity', 0):.3f}\n"
                result_text += f"  Оценка риска: {lesion.get('risk_score', 0):.1%}\n"
        
        self.result_text.insert(tk.END, result_text)
    
    def show_marked_image(self):
        """Показ размеченного изображения"""
        if self.current_marked_image is not None:
            try:
                # Конвертируем BGR в RGB для PIL
                if len(self.current_marked_image.shape) == 3:
                    marked_rgb = cv2.cvtColor(self.current_marked_image, cv2.COLOR_BGR2RGB)
                else:
                    marked_rgb = cv2.cvtColor(self.current_marked_image, cv2.COLOR_GRAY2RGB)
                
                pil_image = Image.fromarray(marked_rgb)
                pil_image.thumbnail((400, 400))
                photo = ImageTk.PhotoImage(pil_image)
                
                self.image_label.configure(image=photo)
                self.image_label.image = photo
                
            except Exception as e:
                logging.error(f"Ошибка отображения изображения: {e}")
    
    def train_models(self):
        """Обучение моделей"""
        self.status_var.set("Обучение моделей...")
        
        def train():
            try:
                result = self.system.train_ml_models(use_synthetic_data=True)
                
                if result['success']:
                    self.status_var.set("Модели обучены успешно")
                    messagebox.showinfo("Обучение", 
                                      f"Модели обучены на {result['samples_used']} примерах\n"
                                      f"Точность Random Forest: {result['results']['random_forest']['accuracy']:.3f}")
                else:
                    self.status_var.set("Ошибка обучения")
                    messagebox.showerror("Ошибка", result['error'])
                    
            except Exception as e:
                self.status_var.set("Ошибка обучения")
                messagebox.showerror("Ошибка", f"Ошибка при обучении: {e}")
        
        threading.Thread(target=train, daemon=True).start()
    
    def save_report(self):
        """Сохранение отчета"""
        if not hasattr(self, 'last_report') or self.last_report is None:
            messagebox.showwarning("Предупреждение", "Сначала выполните анализ")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.result_text.get(1.0, tk.END))
                messagebox.showinfo("Успех", "Отчет сохранен успешно")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить отчет: {e}")
    
    def show_feedback_dialog(self):
        """Диалог обратной связи"""
        if not hasattr(self, 'last_report') or self.last_report is None:
            messagebox.showwarning("Предупреждение", "Сначала выполните анализ")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Обратная связь")
        dialog.geometry("400x300")
        
        ttk.Label(dialog, text="Фактическая категория BI-RADS:").pack(pady=(10, 5))
        birads_var = tk.StringVar()
        birads_combo = ttk.Combobox(dialog, textvariable=birads_var, 
                                  values=["BI-RADS 0", "BI-RADS 1", "BI-RADS 2", 
                                         "BI-RADS 3", "BI-RADS 4", "BI-RADS 5", "BI-RADS 6"])
        birads_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Фактический диагноз:").pack(pady=(10, 5))
        diagnosis_var = tk.StringVar()
        diagnosis_combo = ttk.Combobox(dialog, textvariable=diagnosis_var,
                                     values=["нормальная", "доброкачественная", "злокачественная"])
        diagnosis_combo.pack(pady=5)
        
        ttk.Label(dialog, text="Тип опухоли:").pack(pady=(10, 5))
        tumor_var = tk.StringVar()
        tumor_entry = ttk.Entry(dialog, textvariable=tumor_var, width=30)
        tumor_entry.pack(pady=5)
        
        def submit_feedback():
            try:
                success = self.system.feedback_system.save_feedback(
                    self.last_report['analysis'],
                    birads_var.get(),
                    diagnosis_var.get(),
                    tumor_var.get(),
                    self.patient_info,
                    self.current_image_path
                )
                
                if success:
                    messagebox.showinfo("Успех", "Обратная связь сохранена")
                    dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось сохранить обратную связь")
                    
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при сохранении: {e}")
        
        ttk.Button(dialog, text="Сохранить", command=submit_feedback).pack(pady=20)
    
    def show_about(self):
        """О программе"""
        about_text = """Intelligent Mammography Analysis System

Версия 2.0
Система анализа маммограмм с искусственным интеллектом

Возможности:
- Автоматическое обнаружение образований
- Оценка риска с использованием ML
- Генерация отчетов в формате BI-RADS
- Система обучения с обратной связью

Разработано для помощи врачам-рентгенологам"""
        
        messagebox.showinfo("О программе", about_text)

def main():
    """Главная функция"""
    try:
        root = tk.Tk()
        app = MammographyAnalyzerGUI(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")
        messagebox.showerror("Ошибка", f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()