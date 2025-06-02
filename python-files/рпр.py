import pandas as pd
import numpy as np
import dask.dataframe as dd
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, StringVar, Text
from tkinter.ttk import Progressbar, Style
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN, MiniBatchKMeans
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.covariance import EllipticEnvelope
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
import shap
import plotly.express as px
import plotly.graph_objects as go
import os
import logging
import json
from datetime import datetime
import threading
import time
import webbrowser
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import seaborn as sns
from pandastable import Table
import warnings
from typing import List, Dict, Tuple, Optional, Union
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from functools import partial
import joblib
from numba import jit, njit
import psutil


def set_plot_style():
    """Устанавливает красивый стиль для графиков matplotlib"""
    available_styles = plt.style.available
    preferred_styles = [
        'seaborn-v0_8',  # Новое название для seaborn (matplotlib >= 3.6)
        'seaborn',  # Старое название
        'ggplot',  # Альтернативный стиль
        'fivethirtyeight',  # Другой популярный стиль
        'default'  # Стандартный стиль
    ]

    for style in preferred_styles:
        if style in available_styles:
            plt.style.use(style)
            break
    else:
        # Если ни один из предпочитаемых стилей не доступен
        plt.style.use(available_styles[0] if available_styles else 'default')


# Вызываем функцию при инициализации
set_plot_style()

# Настройка логгирования и отключение предупреждений
warnings.filterwarnings('ignore')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('anomaly_detector.log'),
        logging.StreamHandler()
    ]
)

# Стилизация matplotlib
set_plot_style()
sns.set_palette("husl")


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, pd.Timestamp)):
            return obj.isoformat()
        return super().default(obj)


class OptimizedDataProcessor:
    """Класс для оптимизированной обработки данных"""

    @staticmethod
    def optimize_dtypes(df: pd.DataFrame) -> pd.DataFrame:
        """Оптимизирует типы данных для экономии памяти"""
        original_memory = df.memory_usage(deep=True).sum() / 1024 ** 2

        # Оптимизация числовых типов
        for col in df.select_dtypes(include=['int64']).columns:
            col_min, col_max = df[col].min(), df[col].max()
            if col_min >= np.iinfo(np.int8).min and col_max <= np.iinfo(np.int8).max:
                df[col] = df[col].astype(np.int8)
            elif col_min >= np.iinfo(np.int16).min and col_max <= np.iinfo(np.int16).max:
                df[col] = df[col].astype(np.int16)
            elif col_min >= np.iinfo(np.int32).min and col_max <= np.iinfo(np.int32).max:
                df[col] = df[col].astype(np.int32)

        for col in df.select_dtypes(include=['float64']).columns:
            df[col] = pd.to_numeric(df[col], downcast='float')

        # Оптимизация категориальных данных
        for col in df.select_dtypes(include=['object']).columns:
            if df[col].nunique() / len(df) < 0.5:  # Если меньше 50% уникальных значений
                df[col] = df[col].astype('category')

        optimized_memory = df.memory_usage(deep=True).sum() / 1024 ** 2
        print(f"Оптимизация памяти: {original_memory:.1f}MB -> {optimized_memory:.1f}MB "
              f"({100 * (original_memory - optimized_memory) / original_memory:.1f}% экономии)")

        return df

    @staticmethod
    def stratified_sample(df: pd.DataFrame, sample_size: int = 100000, random_state: int = 42) -> pd.DataFrame:
        """Создает стратифицированную выборку для лучшего представления данных"""
        if len(df) <= sample_size:
            return df

        # Находим числовые колонки для стратификации
        numeric_cols = df.select_dtypes(include=[np.number]).columns[:5]  # Берем первые 5 для скорости

        if len(numeric_cols) == 0:
            return df.sample(n=sample_size, random_state=random_state)

        # Создаем квантили для стратификации
        strata = pd.DataFrame()
        for col in numeric_cols:
            strata[col] = pd.qcut(df[col], q=5, labels=False, duplicates='drop')

        # Создаем составную страту
        strata['combined'] = strata.apply(lambda x: '_'.join(x.astype(str)), axis=1)
        df_with_strata = df.copy()
        df_with_strata['_strata'] = strata['combined']

        # Стратифицированная выборка
        sample_per_stratum = max(1, sample_size // df_with_strata['_strata'].nunique())
        sampled_dfs = []

        for stratum in df_with_strata['_strata'].unique():
            stratum_data = df_with_strata[df_with_strata['_strata'] == stratum]
            n_samples = min(sample_per_stratum, len(stratum_data))
            if n_samples > 0:
                sampled_dfs.append(stratum_data.sample(n=n_samples, random_state=random_state))

        result = pd.concat(sampled_dfs, ignore_index=False)
        return result.drop('_strata', axis=1)

    @staticmethod
    @njit
    def fast_zscore(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
        """Быстрое вычисление Z-score с использованием Numba"""
        mean = np.mean(data)
        std = np.std(data)
        if std == 0:
            return np.zeros_like(data, dtype=np.bool_)
        z_scores = np.abs((data - mean) / std)
        return z_scores > threshold

    @staticmethod
    @njit
    def fast_iqr(data: np.ndarray) -> np.ndarray:
        """Быстрое вычисление IQR аномалий с использованием Numba"""
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        return (data < lower) | (data > upper)


class EnhancedVisuals:
    COLORS = {
        'background': '#f5f7fa',
        'primary': '#4e73df',
        'success': '#1cc88a',
        'info': '#36b9cc',
        'warning': '#f6c23e',
        'danger': '#e74a3b',
        'dark': '#5a5c69',
        'light': '#f8f9fc'
    }

    @staticmethod
    def create_figure(figsize=(8, 6), dpi=100):
        """Создает фигуру matplotlib с настройками стиля"""
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        fig.patch.set_facecolor(EnhancedVisuals.COLORS['light'])
        ax.set_facecolor(EnhancedVisuals.COLORS['light'])
        return fig, ax

    @staticmethod
    def scatter_plot(df: pd.DataFrame, anomalies: List, x_col: str, y_col: str, title: str = None):
        """Точечный график с выделением аномалий"""
        fig = px.scatter(
            df, x=x_col, y=y_col,
            color=df.index.isin([a[0] for a in anomalies]),
            color_discrete_map={True: EnhancedVisuals.COLORS['danger'], False: EnhancedVisuals.COLORS['primary']},
            hover_data=df.columns.tolist(),
            title=title or f"Аномалии: {x_col} vs {y_col}",
            template='plotly_white'
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def parallel_coordinates(df: pd.DataFrame, anomalies: List, numeric_cols: List[str], title: str = None):
        """Параллельные координаты для многомерных данных"""
        fig = px.parallel_coordinates(
            df[numeric_cols],
            color=df.index.isin([a[0] for a in anomalies]),
            color_continuous_scale=[EnhancedVisuals.COLORS['primary'], EnhancedVisuals.COLORS['danger']],
            title=title or "Многомерный анализ аномалий",
            template='plotly_white'
        )
        return fig

    @staticmethod
    def time_series_plot(df: pd.DataFrame, anomalies: List, time_col: str, value_col: str, title: str = None):
        """График временного ряда с аномалиями"""
        fig = px.line(
            df, x=time_col, y=value_col,
            title=title or f"Аномалии во времени ({value_col})",
            template='plotly_white',
            color_discrete_sequence=[EnhancedVisuals.COLORS['primary']]
        )

        anomalies_df = df.loc[[a[0] for a in anomalies]]
        fig.add_trace(
            go.Scatter(
                x=anomalies_df[time_col],
                y=anomalies_df[value_col],
                mode="markers",
                marker=dict(color=EnhancedVisuals.COLORS['danger'], size=10),
                name="Аномалии"
            )
        )
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def feature_importance_plot(shap_values: np.ndarray, features: List[str], title: str = None):
        """Важность признаков через SHAP"""
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=shap_values.mean(0),
                y=features,
                orientation="h",
                marker_color=EnhancedVisuals.COLORS['primary']
            )
        )
        fig.update_layout(
            title=title or "Влияние признаков на аномалии (SHAP)",
            template='plotly_white',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        return fig

    @staticmethod
    def show_histogram(df: pd.DataFrame, column: str, anomalies: List = None, bins: int = 30, title: str = None):
        """Гистограмма распределения с выделением аномалий"""
        fig, ax = EnhancedVisuals.create_figure()

        ax.hist(
            df[column],
            bins=bins,
            color=EnhancedVisuals.COLORS['primary'],
            alpha=0.7,
            label='Нормальные значения'
        )

        if anomalies:
            anomaly_values = df.loc[[a[0] for a in anomalies], column]
            ax.hist(
                anomaly_values,
                bins=bins,
                color=EnhancedVisuals.COLORS['danger'],
                alpha=0.7,
                label='Аномалии'
            )

        ax.set_title(title or f"Распределение {column}", fontsize=12)
        ax.set_xlabel(column, fontsize=10)
        ax.set_ylabel('Частота', fontsize=10)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)

        return fig

    @staticmethod
    def show_boxplot(df: pd.DataFrame, column: str, anomalies: List = None, title: str = None):
        """Боксплот с выделением аномалий"""
        fig, ax = EnhancedVisuals.create_figure()

        sns.boxplot(
            x=df[column],
            color=EnhancedVisuals.COLORS['primary'],
            width=0.4,
            ax=ax
        )

        if anomalies:
            anomaly_values = df.loc[[a[0] for a in anomalies], column]
            ax.scatter(
                x=anomaly_values,
                y=[0] * len(anomaly_values),
                color=EnhancedVisuals.COLORS['danger'],
                s=50,
                label='Аномалии'
            )
            ax.legend()

        ax.set_title(title or f"Боксплот {column}", fontsize=12)
        ax.set_xlabel(column, fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.6)

        return fig


class OptimizedAnomalyClustering:
    @staticmethod
    def cluster_anomalies(
            df: pd.DataFrame,
            anomalies_indices: List,
            eps: float = 0.5,
            min_samples: int = 5,
            random_state: int = 42,
            use_minibatch: bool = True
    ) -> Dict:
        """Оптимизированная группировка аномалий в кластеры"""
        anomaly_data = df.loc[anomalies_indices].select_dtypes(include=[np.number])
        anomaly_data = anomaly_data.dropna()

        if anomaly_data.empty:
            logging.warning("Нет данных для кластеризации после удаления NaN")
            return {}

        cleaned_indices = anomaly_data.index.tolist()

        # Используем RobustScaler для лучшей устойчивости к выбросам
        scaler = RobustScaler()
        scaled_data = scaler.fit_transform(anomaly_data)

        # Для больших данных используем MiniBatch DBSCAN эквивалент
        if len(scaled_data) > 10000 and use_minibatch:
            # Используем MiniBatchKMeans для предварительной кластеризации
            n_clusters = min(max(len(scaled_data) // 1000, 5), 50)
            kmeans = MiniBatchKMeans(
                n_clusters=n_clusters,
                batch_size=1000,
                random_state=random_state,
                n_init=3  # Уменьшаем количество инициализаций
            )
            clusters = kmeans.fit_predict(scaled_data)
        else:
            # Стандартный DBSCAN для меньших данных
            clusters = DBSCAN(
                eps=eps,
                min_samples=min_samples,
                metric='euclidean',
                n_jobs=-1  # Используем все доступные ядра
            ).fit_predict(scaled_data)

        return dict(zip(cleaned_indices, clusters))

    @staticmethod
    def visualize_clusters(
            df: pd.DataFrame,
            anomalies_indices: List,
            cluster_map: Dict,
            x_col: str,
            y_col: str,
            title: str = None
    ):
        """Визуализация кластеров аномалий"""
        anomaly_data = df.loc[anomalies_indices]
        anomaly_data['cluster'] = anomaly_data.index.map(cluster_map)

        fig = px.scatter(
            anomaly_data,
            x=x_col,
            y=y_col,
            color='cluster',
            color_discrete_sequence=px.colors.qualitative.Plotly,
            hover_data=df.columns.tolist(),
            title=title or "Кластеризация аномалий",
            template='plotly_white'
        )

        # Добавляем нормальные точки более прозрачными
        normal_data = df[~df.index.isin(anomalies_indices)]
        if len(normal_data) > 10000:  # Подвыборка для больших данных
            normal_data = normal_data.sample(n=10000, random_state=42)

        fig.add_trace(
            go.Scatter(
                x=normal_data[x_col],
                y=normal_data[y_col],
                mode='markers',
                marker=dict(color='gray', opacity=0.2),
                name='Нормальные точки',
                hoverinfo='skip'
            )
        )

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )

        return fig


class ReportGenerator:
    TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
            margin-top: 30px;
        }}
        .header {{
            background-color: #3498db;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .section {{
            background-color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .anomaly-card {{
            border-left: 4px solid #e74c3c;
            padding: 15px;
            margin-bottom: 15px;
            background-color: #fef5f5;
            border-radius: 0 5px 5px 0;
        }}
        .stats-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        .stats-table th, .stats-table td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        .stats-table th {{
            background-color: #f2f2f2;
        }}
        .highlight {{
            background-color: #fffde7;
            padding: 2px 5px;
            border-radius: 3px;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{title}</h1>
        <p>Отчет сгенерирован {timestamp}</p>
    </div>

    <div class="section">
        <h2>📊 Общая статистика</h2>
        {general_stats}
    </div>

    <div class="section">
        <h2>🔍 Детектированные аномалии</h2>
        <p>Всего обнаружено <span class="highlight">{anomaly_count}</span> аномалий.</p>

        <h3>Топ-10 аномалий</h3>
        {top_anomalies}
    </div>

    <div class="section">
        <h2>📈 Статистика по колонкам</h2>
        {column_stats}
    </div>

    <div class="footer">
        <p>Отчет сгенерирован Advanced Anomaly Detector | {timestamp}</p>
    </div>
</body>
</html>
"""

    @staticmethod
    def generate_html_report(
            df: pd.DataFrame,
            anomalies: List[Tuple[int, str]],
            filename: str = "anomaly_report.html",
            title: str = "Отчет об аномалиях"
    ):
        """Генерирует красивый HTML отчет"""
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")

        # Общая статистика
        general_stats = f"""
        <p>Всего строк: <span class="highlight">{len(df):,}</span></p>
        <p>Всего колонок: <span class="highlight">{len(df.columns)}</span></p>
        <p>Типы данных:</p>
        <ul>
            {"".join(f"<li>{dtype}: {count}</li>" for dtype, count in df.dtypes.value_counts().items())}
        </ul>
        """

        # Топ аномалий
        top_anomalies = "\n".join(
            f"""
            <div class="anomaly-card">
                <h4>Аномалия #{i + 1} (Строка {idx})</h4>
                <pre>{desc}</pre>
            </div>
            """ for i, (idx, desc) in enumerate(anomalies[:10])
        )

        # Статистика по колонкам
        column_stats = ""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if not numeric_cols.empty:
            stats_df = df[numeric_cols].describe().T
            stats_df['missing'] = df[numeric_cols].isna().mean()
            stats_df['anomaly_count'] = [
                sum(1 for idx, _ in anomalies if col in df.loc[idx].index)
                for col in numeric_cols
            ]

            column_stats = stats_df.to_html(
                classes="stats-table",
                float_format="%.2f",
                border=0
            )

        # Заполняем шаблон
        report_content = ReportGenerator.TEMPLATE.format(
            title=title,
            timestamp=timestamp,
            general_stats=general_stats,
            anomaly_count=len(anomalies),
            top_anomalies=top_anomalies,
            column_stats=column_stats
        )

        # Сохраняем файл
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)

        return filename

    @staticmethod
    def generate_pdf_report(df: pd.DataFrame, anomalies: List[Tuple[int, str]], filename: str):
        """Генерирует PDF отчет (использует HTML как промежуточный шаг)"""
        html_file = ReportGenerator.generate_html_report(df, anomalies)
        try:
            import pdfkit
            pdfkit.from_file(html_file, filename)
            return filename
        except Exception as e:
            logging.error(f"Ошибка генерации PDF: {e}")
            raise


class OptimizedAnomalyDetector:
    """Оптимизированный детектор аномалий для больших данных"""

    def __init__(self, n_jobs: int = -1):
        self.n_jobs = n_jobs if n_jobs != -1 else mp.cpu_count()
        self.cache = {}

    def _get_optimal_contamination(self, df_size: int) -> float:
        """Динамически определяет оптимальный уровень загрязнения"""
        if df_size < 1000:
            return 0.1
        elif df_size < 10000:
            return 0.05
        elif df_size < 100000:
            return 0.03
        else:
            return 0.01

    def isolation_forest_analysis(self, df_sample: pd.DataFrame, contamination: float = None) -> List[Tuple[int, str]]:
        """Оптимизированный анализ методом Isolation Forest"""
        if contamination is None:
            contamination = self._get_optimal_contamination(len(df_sample))

        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()

        # Оптимизированные параметры для больших данных
        n_estimators = min(100, max(50, 1000000 // len(df_sample)))
        max_samples = min(256, len(df_sample))

        model = IsolationForest(
            n_estimators=n_estimators,
            max_samples=max_samples,
            contamination=contamination,
            random_state=42,
            n_jobs=self.n_jobs,
            verbose=0,
            warm_start=False
        )

        # Предварительное масштабирование для улучшения производительности
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(df_sample[numeric_cols])

        preds = model.fit_predict(X_scaled)
        scores = model.decision_function(X_scaled)

        anomaly_indices = df_sample[preds == -1].index
        results = []

        for idx in anomaly_indices:
            score_idx = df_sample.index.get_loc(idx)
            row = df_sample.loc[idx]
            report = self._generate_fast_anomaly_report(
                row, df_sample, method="Isolation Forest",
                score=scores[score_idx]
            )
            results.append((idx, report))

        # Сортируем по аномальности (самые аномальные первыми)
        anomaly_scores = {idx: scores[df_sample.index.get_loc(idx)] for idx in anomaly_indices}
        results.sort(key=lambda x: anomaly_scores[x[0]])

        return results

    def lof_analysis(self, df_sample: pd.DataFrame, contamination: float = None) -> List[Tuple[int, str]]:
        """Оптимизированный анализ методом Local Outlier Factor"""
        if contamination is None:
            contamination = self._get_optimal_contamination(len(df_sample))

        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()

        # Проверяем наличие NaN и бесконечных значений
        df_clean = df_sample[numeric_cols].copy()

        # Удаляем строки с NaN или бесконечными значениями
        df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
        df_clean = df_clean.dropna()

        if len(df_clean) == 0:
            logging.warning("Нет данных после очистки NaN для LOF анализа")
            return []

        if len(df_clean) < 10:
            logging.warning("Недостаточно данных для LOF анализа после очистки")
            return []

        # Динамический выбор количества соседей
        n_neighbors = min(20, max(5, len(df_clean) // 100))

        # Убеждаемся, что n_neighbors меньше количества образцов
        n_neighbors = min(n_neighbors, len(df_clean) - 1)

        try:
            model = LocalOutlierFactor(
                n_neighbors=n_neighbors,
                contamination=contamination,
                novelty=False,
                n_jobs=self.n_jobs
            )

            scaler = RobustScaler()
            X_scaled = scaler.fit_transform(df_clean)

            preds = model.fit_predict(X_scaled)
            scores = model.negative_outlier_factor_

            anomaly_indices = df_clean[preds == -1].index
            results = []

            for idx in anomaly_indices:
                if idx in df_sample.index:  # Проверяем, что индекс существует в исходных данных
                    score_idx = df_clean.index.get_loc(idx)
                    row = df_sample.loc[idx]
                    report = self._generate_fast_anomaly_report(
                        row, df_sample, method="Local Outlier Factor",
                        score=scores[score_idx]
                    )
                    results.append((idx, report))

            return results

        except Exception as e:
            logging.error(f"Ошибка в LOF анализе: {str(e)}")
            # Возвращаем пустой результат вместо падения
            return []

    def combined_analysis(self, df_sample: pd.DataFrame) -> List[Tuple[int, str]]:
        """Улучшенный комбинированный анализ с голосованием алгоритмов"""
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            return []

        contamination = self._get_optimal_contamination(len(df_sample))

        # Подготавливаем данные один раз
        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(df_sample[numeric_cols])

        # Создаем словарь для голосования
        votes = {idx: 0 for idx in df_sample.index}
        all_scores = {idx: [] for idx in df_sample.index}
        method_results = {}

        # 1. Isolation Forest
        print("Запуск Isolation Forest...")
        iso_model = IsolationForest(
            n_estimators=min(50, max(25, 100000 // len(df_sample))),
            contamination=contamination,
            random_state=42,
            n_jobs=self.n_jobs
        )
        iso_preds = iso_model.fit_predict(X_scaled)
        iso_scores = iso_model.decision_function(X_scaled)

        for i, idx in enumerate(df_sample.index):
            if iso_preds[i] == -1:
                votes[idx] += 1
                all_scores[idx].append(('iso', abs(iso_scores[i])))

        # 2. Local Outlier Factor (только для данных < 50k строк и без NaN)
        if len(df_sample) < 50000:
            print("Запуск Local Outlier Factor...")
            try:
                # Проверяем данные на корректность для LOF
                df_clean = df_sample[numeric_cols].copy()
                df_clean = df_clean.replace([np.inf, -np.inf], np.nan)
                df_clean = df_clean.dropna()

                if len(df_clean) >= 10:  # Минимум данных для LOF
                    lof_model = LocalOutlierFactor(
                        n_neighbors=min(20, len(df_clean) // 50, len(df_clean) - 1),
                        contamination=contamination,
                        n_jobs=self.n_jobs
                    )

                    scaler_lof = RobustScaler()
                    X_scaled_lof = scaler_lof.fit_transform(df_clean)

                    lof_preds = lof_model.fit_predict(X_scaled_lof)
                    lof_scores = lof_model.negative_outlier_factor_

                    for i, idx in enumerate(df_clean.index):
                        if lof_preds[i] == -1 and idx in df_sample.index:
                            votes[idx] += 1
                            all_scores[idx].append(('lof', abs(lof_scores[i])))
                else:
                    print("Недостаточно данных для LOF после очистки")
            except Exception as e:
                logging.warning(f"LOF анализ пропущен из-за ошибки: {str(e)}")
                print(f"LOF анализ пропущен: {str(e)}")

        # 3. Статистические методы (быстрые)
        print("Запуск статистических методов...")

        # Z-Score анализ
        for col in numeric_cols:
            col_data = df_sample[col].values
            z_anomalies = OptimizedDataProcessor.fast_zscore(col_data, threshold=3.0)
            for i, idx in enumerate(df_sample.index):
                if z_anomalies[i]:
                    votes[idx] += 0.5  # Меньший вес для статистических методов
                    z_score = abs((col_data[i] - np.mean(col_data)) / np.std(col_data))
                    all_scores[idx].append(('zscore', z_score))

        # IQR анализ
        for col in numeric_cols:
            col_data = df_sample[col].values
            iqr_anomalies = OptimizedDataProcessor.fast_iqr(col_data)
            for i, idx in enumerate(df_sample.index):
                if iqr_anomalies[i]:
                    votes[idx] += 0.5  # Меньший вес для статистических методов
                    q1, q3 = np.percentile(col_data, [25, 75])
                    iqr = q3 - q1
                    deviation = min(abs(col_data[i] - q1), abs(col_data[i] - q3))
                    all_scores[idx].append(('iqr', deviation / iqr if iqr > 0 else 0))

        # 4. Для больших данных добавляем MiniBatch подход
        if len(df_sample) > 100000:
            print("Запуск MiniBatch кластеризации...")
            n_clusters = min(max(len(df_sample) // 5000, 10), 100)
            kmeans = MiniBatchKMeans(
                n_clusters=n_clusters,
                batch_size=min(1000, len(df_sample) // 10),
                random_state=42,
                n_init=3
            )
            clusters = kmeans.fit_predict(X_scaled)
            distances = np.min(kmeans.transform(X_scaled), axis=1)

            # Берем топ 5% самых далеких точек
            threshold = np.percentile(distances, 95)
            for i, idx in enumerate(df_sample.index):
                if distances[i] > threshold:
                    votes[idx] += 1
                    all_scores[idx].append(('kmeans', distances[i]))

        # Определяем аномалии на основе голосования
        # Требуем минимум 2 голоса для признания аномалией
        min_votes = 2 if len(df_sample) < 10000 else 1.5
        anomaly_candidates = {idx: vote for idx, vote in votes.items() if vote >= min_votes}

        # Сортируем по количеству голосов и силе аномалии
        def anomaly_strength(idx):
            vote_count = votes[idx]
            avg_score = np.mean([score for _, score in all_scores[idx]]) if all_scores[idx] else 0
            return vote_count + avg_score

        sorted_anomalies = sorted(anomaly_candidates.keys(),
                                  key=anomaly_strength, reverse=True)

        # Ограничиваем количество аномалий
        max_anomalies = max(len(df_sample) // 100, 100)
        sorted_anomalies = sorted_anomalies[:max_anomalies]

        # Генерируем отчеты
        results = []
        for idx in sorted_anomalies:
            row = df_sample.loc[idx]
            vote_count = votes[idx]
            method_scores = all_scores[idx]

            report = self._generate_combined_anomaly_report(
                row, df_sample, vote_count, method_scores
            )
            results.append((idx, report))

        return results

    def _generate_fast_anomaly_report(
            self,
            row: pd.Series,
            df_sample: pd.DataFrame,
            method: str,
            score: float
    ) -> str:
        """Быстрая генерация отчета об аномалии"""
        report = f"🔍 Метод: {method}\n"
        report += f"📊 Аномальность: {abs(score):.3f}\n"
        report += f"📍 Строка: {row.name}\n\n"

        # Показываем только самые отклоняющиеся значения
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
        anomalous_features = []

        for col in numeric_cols[:5]:  # Ограничиваем для скорости
            val = row[col]
            col_std = df_sample[col].std()
            col_mean = df_sample[col].mean()

            if col_std > 0:
                z_score = abs((val - col_mean) / col_std)
                if z_score > 2:  # Значимое отклонение
                    anomalous_features.append((col, val, z_score))

        if anomalous_features:
            report += "🚨 Аномальные признаки:\n"
            for col, val, z_score in sorted(anomalous_features, key=lambda x: x[2], reverse=True)[:3]:
                report += f"• {col}: {val:.2f} (Z-score: {z_score:.2f})\n"

        return report

    def _generate_combined_anomaly_report(
            self,
            row: pd.Series,
            df_sample: pd.DataFrame,
            vote_count: float,
            method_scores: List[Tuple[str, float]]
    ) -> str:
        """Генерирует отчет для комбинированного анализа"""
        report = f"🔍 Комбинированный анализ\n"
        report += f"🗳️ Голосов: {vote_count:.1f}\n"
        report += f"📍 Строка: {row.name}\n\n"

        # Показываем методы, которые обнаружили аномалию
        if method_scores:
            report += "📊 Методы обнаружения:\n"
            method_names = {
                'iso': 'Isolation Forest',
                'lof': 'Local Outlier Factor',
                'zscore': 'Z-Score',
                'iqr': 'IQR',
                'kmeans': 'K-Means clustering'
            }

            grouped_scores = {}
            for method, score in method_scores:
                if method not in grouped_scores:
                    grouped_scores[method] = []
                grouped_scores[method].append(score)

            for method, scores in grouped_scores.items():
                avg_score = np.mean(scores)
                method_name = method_names.get(method, method)
                report += f"• {method_name}: {avg_score:.3f}\n"

        # Находим самые аномальные признаки
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
        anomalous_features = []

        for col in numeric_cols:
            if col in row.index:
                val = row[col]
                col_std = df_sample[col].std()
                col_mean = df_sample[col].mean()

                if col_std > 0:
                    z_score = abs((val - col_mean) / col_std)
                    if z_score > 1.5:
                        anomalous_features.append((col, val, z_score))

        if anomalous_features:
            report += "\n🚨 Наиболее аномальные признаки:\n"
            for col, val, z_score in sorted(anomalous_features, key=lambda x: x[2], reverse=True)[:5]:
                report += f"• {col}: {val:.2f} (отклонение: {z_score:.2f}σ)\n"

        report += "\n💡 Рекомендация: Требует детального изучения"

        return report


class AdvancedAnomalyDetector:
    METHODS = {
        "Isolation Forest": "Метод изолирующего леса (быстрый для больших данных)",
        "Local Outlier Factor": "Локальный фактор выбросов (точный для средних данных)",
        "One-Class SVM": "Метод опорных векторов (медленный, но точный)",
        "Elliptic Envelope": "Эллиптическая оболочка (для гауссовых данных)",
        "Z-Score": "Статистический метод (очень быстрый)",
        "IQR": "Межквартильный размах (быстрый)",
        "Combined": "Комбинированный анализ (рекомендуется)",
        "Auto": "Автоматический выбор (оптимальная скорость)"
    }

    def __init__(self, master):
        self.master = master
        self.df = None
        self.original_df = None  # Сохраняем оригинальные данные
        self.anomalies = []
        self.timer_running = False
        self.timer_id = None
        self.stats_text = None
        self.current_plot = None
        self.shap_values = None
        self.cluster_map = {}
        self.processor = OptimizedDataProcessor()
        self.detector = OptimizedAnomalyDetector()

        # UI variables
        self.mode_var = StringVar(value="local")
        self.method_var = StringVar(value="Combined")
        self.status_var = StringVar(value="Готов к работе")
        self.progress_var = tk.IntVar(value=0)

        self._setup_ui()
        self.master.protocol("WM_DELETE_WINDOW", self._on_close)

    def _bind_scroll_to_all_children(self, parent, canvas):
        """Рекурсивно привязывает события прокрутки ко всем дочерним элементам"""

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            canvas.yview_scroll(-1, "units")

        def _on_mousewheel_linux_up(event):
            canvas.yview_scroll(1, "units")

        # Bind to parent
        parent.bind("<MouseWheel>", _on_mousewheel)  # Windows
        parent.bind("<Button-4>", _on_mousewheel_linux_up)  # Linux
        parent.bind("<Button-5>", _on_mousewheel_linux)  # Linux

        # Recursively bind to all children
        for child in parent.winfo_children():
            child.bind("<MouseWheel>", _on_mousewheel)
            child.bind("<Button-4>", _on_mousewheel_linux_up)
            child.bind("<Button-5>", _on_mousewheel_linux)

            # If child has children, bind recursively
            if child.winfo_children():
                self._bind_scroll_to_all_children(child, canvas)

    def _on_close(self):
        self._stop_timer()
        self.master.destroy()

    def _setup_ui(self):
        self.master.title("Advanced Anomaly Detector v5.1 - Optimized")
        self.master.geometry("1400x900")
        self.master.minsize(1000, 700)

        # Настройка стилей
        style = Style()
        style.theme_use('clam')

        # Цветовая схема
        bg_color = '#f5f7fa'
        primary_color = '#4e73df'
        secondary_color = '#1cc88a'
        accent_color = '#e74a3b'
        text_color = '#5a5c69'

        style.configure('.', background=bg_color, foreground=text_color, font=('Segoe UI', 10))
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=text_color)
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'), foreground=primary_color)
        style.configure('TButton', padding=6, relief='flat', background=primary_color, foreground='white')
        style.map('TButton',
                  background=[('active', primary_color), ('pressed', '#3a56b2')],
                  foreground=[('active', 'white'), ('pressed', 'white')])
        style.configure('Accent.TButton', background=accent_color)
        style.configure('Secondary.TButton', background=secondary_color)
        style.configure('TCombobox', fieldbackground='white', background='white')
        style.configure('TEntry', fieldbackground='white')
        style.configure('TNotebook', background=bg_color)
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab',
                  background=[('selected', bg_color), ('!selected', '#e0e0e0')],
                  foreground=[('selected', primary_color), ('!selected', text_color)])
        style.configure('Treeview',
                        background='white',
                        fieldbackground='white',
                        foreground=text_color,
                        rowheight=25)
        style.map('Treeview', background=[('selected', primary_color)])
        style.configure('Treeview.Heading',
                        background=primary_color,
                        foreground='white',
                        font=('Segoe UI', 10, 'bold'))
        style.configure('Vertical.TScrollbar', background=bg_color)
        style.configure('Horizontal.TScrollbar', background=bg_color)
        style.configure('TProgressbar',
                        thickness=20,
                        troughcolor='#e0e0e0',
                        background=secondary_color)

        # Main container
        main_frame = ttk.Frame(self.master)
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(0, 10))

        title_label = ttk.Label(
            header_frame,
            text="Анализатор аномалий (Оптимизированный)",
            style='Title.TLabel'
        )
        title_label.pack(side='left', padx=10)

        # Индикатор производительности
        self.perf_label = ttk.Label(
            header_frame,
            text=f"CPU: {mp.cpu_count()} ядер | RAM: {psutil.virtual_memory().total // (1024 ** 3)}GB",
            font=('Segoe UI', 9)
        )
        self.perf_label.pack(side='right', padx=10)

        ttk.Label(
            header_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 10, 'italic')
        ).pack(side='right', padx=10)

        # Main content
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)

        # Left panel - controls with scrollbar
        control_canvas = tk.Canvas(content_frame, width=320, bg=bg_color, highlightthickness=0)
        control_scrollbar = ttk.Scrollbar(content_frame, orient="vertical", command=control_canvas.yview)
        control_frame = ttk.Frame(control_canvas, style='TFrame')

        control_frame.bind(
            "<Configure>",
            lambda e: control_canvas.configure(scrollregion=control_canvas.bbox("all"))
        )

        control_canvas.create_window((0, 0), window=control_frame, anchor="nw")
        control_canvas.configure(yscrollcommand=control_scrollbar.set)

        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            control_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        def _on_mousewheel_linux(event):
            control_canvas.yview_scroll(-1, "units")

        def _on_mousewheel_linux_up(event):
            control_canvas.yview_scroll(1, "units")

        # Bind for different OS
        control_canvas.bind("<MouseWheel>", _on_mousewheel)  # Windows
        control_canvas.bind("<Button-4>", _on_mousewheel_linux_up)  # Linux
        control_canvas.bind("<Button-5>", _on_mousewheel_linux)  # Linux

        # Make sure the canvas can receive focus for scroll events
        control_canvas.bind("<Enter>", lambda e: control_canvas.focus_set())

        # Update scroll region when frame size changes
        def update_scroll_region():
            control_canvas.update_idletasks()
            control_canvas.configure(scrollregion=control_canvas.bbox("all"))

        control_frame.bind("<Configure>", lambda e: update_scroll_region())

        # Pack canvas and scrollbar
        control_canvas.pack(side='left', fill='y', padx=(0, 5))
        control_scrollbar.pack(side='left', fill='y', padx=(0, 10))

        # Data loading section
        data_frame = ttk.LabelFrame(control_frame, text="📁 Данные", padding=10)
        data_frame.pack(fill='x', pady=(0, 10))

        ttk.Button(
            data_frame,
            text="Загрузить данные",
            command=self._load_data,
            style='TButton',
            cursor='hand2'
        ).pack(fill='x', pady=5)

        ttk.Button(
            data_frame,
            text="Просмотреть данные",
            command=self._preview_data,
            style='Secondary.TButton',
            cursor='hand2'
        ).pack(fill='x', pady=5)

        # Optimization section
        opt_frame = ttk.LabelFrame(control_frame, text="⚡ Оптимизация", padding=10)
        opt_frame.pack(fill='x', pady=(0, 10))

        self.optimize_memory_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opt_frame,
            text="Оптимизация памяти",
            variable=self.optimize_memory_var,
            cursor='hand2'
        ).pack(anchor='w', pady=2)

        self.use_sampling_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opt_frame,
            text="Умная выборка",
            variable=self.use_sampling_var,
            cursor='hand2'
        ).pack(anchor='w', pady=2)

        self.parallel_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opt_frame,
            text="Параллельные вычисления",
            variable=self.parallel_var,
            cursor='hand2'
        ).pack(anchor='w', pady=2)

        # Analysis settings
        analysis_frame = ttk.LabelFrame(control_frame, text="⚙️ Настройки анализа", padding=10)
        analysis_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(analysis_frame, text="Метод анализа:").pack(anchor='w', pady=(0, 5))
        method_combo = ttk.Combobox(
            analysis_frame,
            textvariable=self.method_var,
            values=list(self.METHODS.keys()),
            state="readonly",
            cursor='hand2'
        )
        method_combo.pack(fill='x', pady=(0, 10))
        method_combo.bind("<<ComboboxSelected>>", self._show_method_info)

        # Info label for method description
        self.method_info = ttk.Label(
            analysis_frame,
            text=self.METHODS[self.method_var.get()],
            wraplength=280,
            justify='left',
            foreground='#666'
        )
        self.method_info.pack(fill='x', pady=5)

        ttk.Button(
            analysis_frame,
            text="Анализировать",
            command=self._start_analysis,
            style='Accent.TButton',
            cursor='hand2'
        ).pack(fill='x', pady=10)

        # Progress bar
        progress_frame = ttk.Frame(control_frame)
        progress_frame.pack(fill='x', pady=(0, 10))

        ttk.Label(progress_frame, text="Прогресс:").pack(anchor='w')
        self.progress = Progressbar(
            progress_frame,
            orient="horizontal",
            length=280,
            variable=self.progress_var,
            style='TProgressbar'
        )
        self.progress.pack(fill='x', pady=5)

        self.timer_label = ttk.Label(progress_frame, text="Время: 00:00")
        self.timer_label.pack(pady=5)

        # Performance info
        self.perf_info = ttk.Label(progress_frame, text="", font=('Segoe UI', 8))
        self.perf_info.pack(pady=2)

        # Visualization section
        viz_frame = ttk.LabelFrame(control_frame, text="📊 Визуализация", padding=10)
        viz_frame.pack(fill='x', pady=(0, 10))

        ttk.Button(
            viz_frame,
            text="Точечный график",
            command=self._show_scatter_plot,
            cursor='hand2'
        ).pack(fill='x', pady=2)

        ttk.Button(
            viz_frame,
            text="Параллельные координаты",
            command=self._show_parallel_coords,
            cursor='hand2'
        ).pack(fill='x', pady=2)

        ttk.Button(
            viz_frame,
            text="Временной ряд",
            command=self._show_time_series,
            cursor='hand2'
        ).pack(fill='x', pady=2)

        ttk.Button(
            viz_frame,
            text="Гистограмма",
            command=self._show_histogram,
            cursor='hand2'
        ).pack(fill='x', pady=2)

        ttk.Button(
            viz_frame,
            text="Боксплот",
            command=self._show_boxplot,
            cursor='hand2'
        ).pack(fill='x', pady=2)

        ttk.Button(
            viz_frame,
            text="Кластеры аномалий",
            command=self._show_clusters,
            cursor='hand2'
        ).pack(fill='x', pady=2)

        # Export section
        export_frame = ttk.LabelFrame(control_frame, text="💾 Экспорт", padding=10)
        export_frame.pack(fill='x')

        ttk.Button(
            export_frame,
            text="Экспорт результатов",
            command=self._export_results,
            cursor='hand2'
        ).pack(fill='x', pady=2)

        ttk.Button(
            export_frame,
            text="HTML отчет",
            command=lambda: self._generate_report("html"),
            style='Secondary.TButton',
            cursor='hand2'
        ).pack(fill='x', pady=2)

        ttk.Button(
            export_frame,
            text="PDF отчет",
            command=lambda: self._generate_report("pdf"),
            style='Secondary.TButton',
            cursor='hand2'
        ).pack(fill='x', pady=2)

        # Right panel - results
        notebook = ttk.Notebook(content_frame)
        notebook.pack(side='right', fill='both', expand=True)

        # Anomalies table tab
        table_frame = ttk.Frame(notebook)
        self._setup_table(table_frame)
        notebook.add(table_frame, text="Аномалии")

        # Details tab
        details_frame = ttk.Frame(notebook)
        self._setup_details(details_frame)
        notebook.add(details_frame, text="Детали")

        # Stats tab
        stats_frame = ttk.Frame(notebook)
        self._setup_stats(stats_frame)
        notebook.add(stats_frame, text="Статистика")

        # Visualization tab
        self.plot_frame = ttk.Frame(notebook)
        notebook.add(self.plot_frame, text="Графики")

        # Status bar
        status_frame = ttk.Frame(main_frame, height=25)
        status_frame.pack(fill='x', padx=10, pady=(5, 0))

        ttk.Label(
            status_frame,
            text="Advanced Anomaly Detector v5.1 - Optimized | © 2023",
            font=('Segoe UI', 8)
        ).pack(side='left')

        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            font=('Segoe UI', 8),
            relief="sunken",
            padding=(5, 0)
        ).pack(side='right')

        # Bind scroll events to all widgets in control frame
        self._bind_scroll_to_all_children(control_frame, control_canvas)

    def _show_method_info(self, event=None):
        """Показывает описание выбранного метода"""
        method = self.method_var.get()
        self.method_info.config(text=self.METHODS.get(method, "Описание недоступно"))

    def _setup_table(self, parent):
        """Настраивает таблицу для отображения аномалий"""
        # Treeview with scrollbars
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(tree_frame, selectmode='browse')

        scroll_y = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Columns
        self.tree["columns"] = ("row_id", "anomaly_type", "score", "cluster")
        self.tree.heading("#0", text="#", anchor='w')
        self.tree.heading("row_id", text="Строка", anchor='w')
        self.tree.heading("anomaly_type", text="Тип аномалии", anchor='w')
        self.tree.heading("score", text="Сила", anchor='w')
        self.tree.heading("cluster", text="Кластер", anchor='w')

        self.tree.column("#0", width=50, minwidth=50)
        self.tree.column("row_id", width=80, minwidth=80)
        self.tree.column("anomaly_type", width=120, minwidth=100)
        self.tree.column("score", width=60, minwidth=60)
        self.tree.column("cluster", width=80, minwidth=60)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", lambda e: self._show_anomaly_details())

    def _setup_details(self, parent):
        """Настраивает панель деталей аномалии"""
        details_frame = ttk.Frame(parent)
        details_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.details_text = Text(
            details_frame,
            wrap="word",
            padx=10,
            pady=10,
            font=('Consolas', 10),
            bg='white',
            fg='#333'
        )

        scroll = ttk.Scrollbar(details_frame, command=self.details_text.yview)
        self.details_text.configure(yscrollcommand=scroll.set)

        # Layout
        self.details_text.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

    def _setup_stats(self, parent):
        """Настраивает панель статистики"""
        stats_frame = ttk.Frame(parent)
        stats_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.stats_text = Text(
            stats_frame,
            wrap="word",
            padx=10,
            pady=10,
            font=('Consolas', 10),
            bg='white',
            fg='#333'
        )

        scroll = ttk.Scrollbar(stats_frame, command=self.stats_text.yview)
        self.stats_text.configure(yscrollcommand=scroll.set)

        # Layout
        self.stats_text.pack(side='left', fill='both', expand=True)
        scroll.pack(side='right', fill='y')

    def _clear_plot_frame(self):
        """Очищает фрейм для графиков"""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    def _show_plot(self, fig):
        """Отображает график matplotlib во фрейме"""
        self._clear_plot_frame()

        if isinstance(fig, go.Figure):
            # Для Plotly сохраняем в HTML и открываем в браузере
            html_file = os.path.join(os.getcwd(), "temp_plot.html")
            fig.write_html(html_file, auto_open=True)
        else:
            # Для matplotlib создаем canvas
            canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)

            # Add toolbar
            from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
            toolbar = NavigationToolbar2Tk(canvas, self.plot_frame)
            toolbar.update()
            canvas._tkcanvas.pack(fill='both', expand=True)

            self.current_plot = canvas

    def _preview_data(self):
        """Показывает предпросмотр данных в отдельном окне"""
        if self.df is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите данные")
            return

        try:
            preview_window = tk.Toplevel(self.master)
            preview_window.title("Просмотр данных")
            preview_window.geometry("1000x600")
            preview_window.state('normal')

            # Создаем основной фрейм
            main_frame = ttk.Frame(preview_window)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Информация о данных
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill='x', pady=(0, 10))

            info_text = f"Данные: {len(self.df):,} строк × {len(self.df.columns)} столбцов"
            ttk.Label(info_frame, text=info_text, font=('Segoe UI', 12, 'bold')).pack()

            # Создаем Treeview для отображения данных
            tree_frame = ttk.Frame(main_frame)
            tree_frame.pack(fill='both', expand=True)

            # Treeview с прокруткой
            tree = ttk.Treeview(tree_frame, show='headings')

            # Scrollbars
            v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)

            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

            # Настраиваем колонки (ограничиваем до 20 для производительности)
            display_cols = list(self.df.columns)[:20]
            tree["columns"] = display_cols

            for col in display_cols:
                tree.heading(col, text=col)
                tree.column(col, width=120, minwidth=80)

            # Заполняем данными (первые 1000 строк для быстродействия)
            display_rows = min(1000, len(self.df))
            for i in range(display_rows):
                row_data = []
                for col in display_cols:
                    val = self.df.iloc[i][col]
                    # Форматируем значения для отображения
                    if pd.isna(val):
                        formatted_val = "NaN"
                    elif isinstance(val, float):
                        formatted_val = f"{val:.3f}" if abs(val) < 1000 else f"{val:.2e}"
                    else:
                        formatted_val = str(val)[:50]  # Ограничиваем длину
                    row_data.append(formatted_val)

                tree.insert("", "end", values=row_data)

            # Размещаем элементы
            tree.grid(row=0, column=0, sticky='nsew')
            v_scrollbar.grid(row=0, column=1, sticky='ns')
            h_scrollbar.grid(row=1, column=0, sticky='ew')

            tree_frame.grid_rowconfigure(0, weight=1)
            tree_frame.grid_columnconfigure(0, weight=1)

            # Кнопки управления
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill='x', pady=(10, 0))

            if len(self.df.columns) > 20:
                ttk.Label(
                    button_frame,
                    text=f"Показаны первые 20 из {len(self.df.columns)} столбцов",
                    foreground='gray'
                ).pack(side='left')

            if len(self.df) > 1000:
                ttk.Label(
                    button_frame,
                    text=f"Показаны первые 1000 из {len(self.df):,} строк",
                    foreground='gray'
                ).pack(side='right')

            ttk.Button(
                button_frame,
                text="Закрыть",
                command=preview_window.destroy,
                cursor='hand2'
            ).pack(side='bottom', pady=5)

            # Статистика по данным
            stats_frame = ttk.LabelFrame(main_frame, text="Краткая статистика", padding=5)
            stats_frame.pack(fill='x', pady=(10, 0))

            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            stats_text = f"Числовых столбцов: {len(numeric_cols)}\n"

            if len(numeric_cols) > 0:
                stats_text += f"Пропущенных значений: {self.df[numeric_cols].isna().sum().sum():,}\n"
                stats_text += f"Дубликатов: {self.df.duplicated().sum():,}"

            ttk.Label(stats_frame, text=stats_text, justify='left').pack(anchor='w')

            # Обновляем окно
            preview_window.focus()

        except Exception as e:
            logging.error(f"Ошибка просмотра данных: {str(e)}", exc_info=True)
            messagebox.showerror("Ошибка", f"Не удалось отобразить данные:\n{str(e)}")

    def _load_data(self):
        """Оптимизированная загрузка данных из файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[
                ("Данные", "*.tsv;*.csv;*.xlsx;*.parquet;*.feather"),
                ("TSV файлы", "*.tsv"),
                ("CSV файлы", "*.csv"),
                ("Excel файлы", "*.xlsx"),
                ("Parquet файлы", "*.parquet"),
                ("Все файлы", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            start_time = time.time()
            self.status_var.set("Загрузка данных...")
            self.progress_var.set(0)
            self.master.update()

            file_ext = os.path.splitext(file_path)[1].lower()
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # в MB

            self.status_var.set(f"Загрузка файла ({file_size:.1f} MB)...")
            self.progress_var.set(10)

            # Оптимизированная загрузка в зависимости от размера файла
            if file_size > 500:  # Очень большие файлы
                self.status_var.set("Загрузка большого файла с оптимизацией...")
                if file_ext == '.tsv':
                    # Используем чанки для очень больших файлов
                    chunks = []
                    for chunk in pd.read_csv(file_path, sep='\t', chunksize=50000, encoding='utf-8'):
                        chunks.append(chunk)
                        if len(chunks) * 50000 > 1000000:  # Ограничиваем до 1M строк
                            break
                    self.df = pd.concat(chunks, ignore_index=True)
                elif file_ext == '.parquet':
                    self.df = pd.read_parquet(file_path)
                else:
                    chunks = []
                    for chunk in pd.read_csv(file_path, chunksize=50000):
                        chunks.append(chunk)
                        if len(chunks) * 50000 > 1000000:
                            break
                    self.df = pd.concat(chunks, ignore_index=True)
            elif file_size > 100:  # Большие файлы
                self.status_var.set(f"Загрузка большого файла ({file_size:.1f} MB)...")
                if file_ext == '.tsv':
                    self.df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
                elif file_ext == '.csv':
                    self.df = pd.read_csv(file_path)
                elif file_ext == '.xlsx':
                    self.df = pd.read_excel(file_path, engine='openpyxl')
                elif file_ext == '.parquet':
                    self.df = pd.read_parquet(file_path)
                elif file_ext == '.feather':
                    self.df = pd.read_feather(file_path)
            else:
                # Для маленьких файлов используем стандартную загрузку
                if file_ext == '.tsv':
                    self.df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
                elif file_ext == '.csv':
                    self.df = pd.read_csv(file_path)
                elif file_ext == '.xlsx':
                    self.df = pd.read_excel(file_path)
                elif file_ext == '.parquet':
                    self.df = pd.read_parquet(file_path)
                elif file_ext == '.feather':
                    self.df = pd.read_feather(file_path)

            self.progress_var.set(50)

            # Сохраняем оригинальные данные
            self.original_df = self.df.copy()

            # Преобразование дат
            self.status_var.set("Обработка дат...")
            date_cols = [col for col in self.df.columns
                         if 'date' in col.lower() or 'time' in col.lower()]
            for col in date_cols:
                try:
                    self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                except:
                    continue

            self.progress_var.set(70)

            # Оптимизация памяти, если включена
            if self.optimize_memory_var.get():
                self.status_var.set("Оптимизация памяти...")
                self.df = self.processor.optimize_dtypes(self.df)

            self.progress_var.set(90)

            load_time = time.time() - start_time
            self.status_var.set(f"Загружено: {len(self.df):,} строк, {len(self.df.columns)} колонок ({load_time:.1f}с)")

            # Обновляем информацию о производительности
            memory_usage = self.df.memory_usage(deep=True).sum() / (1024 ** 2)
            self.perf_info.config(text=f"Память: {memory_usage:.1f}MB | Время: {load_time:.1f}с")

            messagebox.showinfo("Успех",
                                f"Данные успешно загружены\n\nСтрок: {len(self.df):,}\nСтолбцов: {len(self.df.columns)}\nВремя: {load_time:.1f}с")

        except Exception as e:
            logging.error(f"Ошибка загрузки: {str(e)}", exc_info=True)
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл:\n{str(e)}")
            self.status_var.set("Ошибка загрузки")
        finally:
            self.progress_var.set(100)
            time.sleep(0.5)
            self.progress_var.set(0)

    def _start_timer(self):
        """Запускает таймер выполнения"""
        self.start_time = time.time()
        self.timer_running = True
        self._update_timer()

    def _stop_timer(self):
        """Останавливает таймер"""
        self.timer_running = False
        if self.timer_id:
            self.master.after_cancel(self.timer_id)

    def _update_timer(self):
        """Обновляет отображение таймера"""
        if not self.timer_running:
            return

        elapsed = time.time() - self.start_time
        mins, secs = divmod(int(elapsed), 60)
        self.timer_label.config(text=f"Время: {mins:02d}:{secs:02d}")

        # Обновляем информацию о ресурсах
        cpu_percent = psutil.cpu_percent(interval=None)
        memory_percent = psutil.virtual_memory().percent
        self.perf_info.config(text=f"CPU: {cpu_percent:.1f}% | RAM: {memory_percent:.1f}%")

        self.timer_id = self.master.after(1000, self._update_timer)

    def _start_analysis(self):
        """Запускает оптимизированный анализ данных в отдельном потоке"""
        if self.df is None:
            messagebox.showwarning("Ошибка", "Сначала загрузите данные")
            return

        try:
            self.status_var.set("Подготовка анализа...")
            self.progress_var.set(0)
            self._start_timer()

            # Запуск в отдельном потоке
            threading.Thread(
                target=self._run_optimized_analysis,
                daemon=True
            ).start()

        except Exception as e:
            logging.error(f"Ошибка запуска анализа: {str(e)}", exc_info=True)
            messagebox.showerror("Ошибка", f"Ошибка запуска анализа:\n{str(e)}")
            self._stop_timer()
            self.progress_var.set(0)

    def _run_optimized_analysis(self):
        """Основная логика оптимизированного анализа данных"""
        try:
            analysis_start = time.time()

            # 1. Подготовка данных
            self.status_var.set("Подготовка данных...")
            self.progress_var.set(5)

            df_for_analysis = self._prepare_optimized_sample()
            if df_for_analysis is None:
                return

            data_prep_time = time.time() - analysis_start
            self.status_var.set(f"Данные подготовлены ({data_prep_time:.1f}с)")
            self.progress_var.set(20)

            # 2. Выполнение анализа
            analysis_time = time.time()
            self.status_var.set("Выполнение анализа...")

            method = self.method_var.get()
            results = self._analyze_optimized_data(df_for_analysis, method)

            analysis_duration = time.time() - analysis_time
            self.status_var.set(f"Анализ выполнен ({analysis_duration:.1f}с)")
            self.progress_var.set(60)

            # 3. Кластеризация аномалий (если нужно)
            if results and len(results) > 10:
                cluster_time = time.time()
                self.status_var.set("Кластеризация аномалий...")
                self.progress_var.set(70)

                anomalies_indices = [a[0] for a in results][:5000]  # Ограничиваем для скорости
                if anomalies_indices:
                    self.cluster_map = OptimizedAnomalyClustering.cluster_anomalies(
                        df_for_analysis,
                        anomalies_indices,
                        eps='auto' if len(anomalies_indices) < 1000 else 0.5,
                        min_samples=5,
                        use_minibatch=len(anomalies_indices) > 1000
                    )

                    # Обновляем результаты с информацией о кластерах
                    for i, (idx, desc) in enumerate(results[:5000]):
                        cluster = self.cluster_map.get(idx, -1)
                        cluster_info = f"Кластер {cluster}" if cluster != -1 else "Единичная"
                        results[i] = (idx, f"{desc}\n\n🔷 {cluster_info}\n")

                cluster_duration = time.time() - cluster_time
                self.status_var.set(f"Кластеризация завершена ({cluster_duration:.1f}с)")

            # 4. Финализация результатов
            self.progress_var.set(80)
            self.status_var.set("Обработка результатов...")

            self.anomalies = results
            self._generate_optimized_stats_report(df_for_analysis)
            self._display_optimized_results()

            total_time = time.time() - analysis_start

            self.status_var.set(f"Анализ завершен ({total_time:.1f}с). Найдено {len(self.anomalies)} аномалий")

            # Показываем детальную статистику производительности
            perf_stats = (f"Анализ завершен!\n\n"
                          f"Время подготовки: {data_prep_time:.1f}с\n"
                          f"Время анализа: {analysis_duration:.1f}с\n"
                          f"Общее время: {total_time:.1f}с\n"
                          f"Найдено аномалий: {len(self.anomalies)}\n"
                          f"Скорость: {len(df_for_analysis) / total_time:.0f} строк/с")

            messagebox.showinfo("Готово", perf_stats)

        except Exception as e:
            logging.error(f"Ошибка анализа: {str(e)}", exc_info=True)
            messagebox.showerror("Ошибка анализа", str(e))
            self.status_var.set("Ошибка анализа")
        finally:
            self.progress_var.set(100)
            self._stop_timer()

    def _prepare_optimized_sample(self) -> Optional[pd.DataFrame]:
        """Оптимизированная подготовка данных для анализа"""
        if self.df is None or self.df.empty:
            messagebox.showwarning("Ошибка", "Нет данных для анализа")
            return None

        df_sample = self.df.copy()

        # Выбор только числовых колонок для анализа
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Ошибка", "Не найдены числовые колонки для анализа")
            return None

        # Умная выборка для больших данных
        if self.use_sampling_var.get() and len(df_sample) > 100000:
            sample_size = min(100000, len(df_sample))
            if len(df_sample) > 1000000:
                sample_size = min(200000, len(df_sample))

            self.status_var.set(f"Создание умной выборки ({sample_size:,} из {len(df_sample):,})...")
            df_sample = self.processor.stratified_sample(df_sample, sample_size)

        # Оптимизированное заполнение пропущенных значений
        for col in numeric_cols:
            if df_sample[col].isna().any() or np.isinf(df_sample[col]).any():
                # Заменяем бесконечные значения на NaN
                df_sample[col] = df_sample[col].replace([np.inf, -np.inf], np.nan)

                if len(df_sample) > 100000:
                    # Для больших данных используем быстрые методы
                    median_val = df_sample[col].median()
                    df_sample[col].fillna(median_val, inplace=True)
                else:
                    # Для маленьких - более точные методы
                    df_sample[col].interpolate(method='linear', inplace=True, limit_direction='both')
                    median_val = df_sample[col].median()
                    df_sample[col].fillna(median_val, inplace=True)

        # Финальная проверка на наличие NaN или бесконечных значений
        df_sample = df_sample.replace([np.inf, -np.inf], np.nan)
        df_sample = df_sample.dropna()

        if len(df_sample) == 0:
            messagebox.showerror("Ошибка", "Нет корректных данных после очистки")
            return None

        return df_sample

    def _analyze_optimized_data(self, df_sample: pd.DataFrame, method: str) -> List[Tuple[int, str]]:
        """Выполняет оптимизированный анализ данных выбранным методом"""
        if not self.parallel_var.get():
            self.detector.n_jobs = 1

        if method == "Isolation Forest":
            return self.detector.isolation_forest_analysis(df_sample)
        elif method == "Local Outlier Factor":
            return self.detector.lof_analysis(df_sample)
        elif method == "One-Class SVM":
            return self._svm_analysis(df_sample)
        elif method == "Elliptic Envelope":
            return self._elliptic_envelope_analysis(df_sample)
        elif method == "Z-Score":
            return self._fast_zscore_analysis(df_sample)
        elif method == "IQR":
            return self._fast_iqr_analysis(df_sample)
        elif method == "Combined":
            return self.detector.combined_analysis(df_sample)
        else:  # Auto
            return self._auto_optimized_analysis(df_sample)

    def _fast_zscore_analysis(self, df_sample: pd.DataFrame) -> List[Tuple[int, str]]:
        """Быстрый анализ методом Z-Score с использованием Numba"""
        results = []
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols:
            col_data = df_sample[col].values
            anomaly_mask = OptimizedDataProcessor.fast_zscore(col_data, threshold=3.0)

            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    idx = df_sample.index[i]
                    row = df_sample.loc[idx]
                    z_score = abs((col_data[i] - np.mean(col_data)) / np.std(col_data))

                    report = (f"🔍 Метод: Z-Score (быстрый)\n"
                              f"📊 Z-Score: {z_score:.3f}\n"
                              f"📍 Строка: {idx}\n"
                              f"🚨 Аномальная колонка: {col} = {col_data[i]:.2f}\n")

                    results.append((idx, report))

        return results

    def _fast_iqr_analysis(self, df_sample: pd.DataFrame) -> List[Tuple[int, str]]:
        """Быстрый анализ методом IQR с использованием Numba"""
        results = []
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()

        for col in numeric_cols:
            col_data = df_sample[col].values
            anomaly_mask = OptimizedDataProcessor.fast_iqr(col_data)

            for i, is_anomaly in enumerate(anomaly_mask):
                if is_anomaly:
                    idx = df_sample.index[i]
                    row = df_sample.loc[idx]

                    q1, q3 = np.percentile(col_data, [25, 75])
                    iqr = q3 - q1
                    deviation = min(abs(col_data[i] - q1), abs(col_data[i] - q3))

                    report = (f"🔍 Метод: IQR (быстрый)\n"
                              f"📊 Отклонение: {deviation / iqr:.3f} IQR\n"
                              f"📍 Строка: {idx}\n"
                              f"🚨 Аномальная колонка: {col} = {col_data[i]:.2f}\n")

                    results.append((idx, report))

        return results

    def _svm_analysis(self, df_sample: pd.DataFrame) -> List[Tuple[int, str]]:
        """Анализ методом One-Class SVM"""
        results = []
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()

        contamination = self.detector._get_optimal_contamination(len(df_sample))

        model = OneClassSVM(
            nu=contamination,
            kernel="rbf",
            gamma="scale"
        )

        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(df_sample[numeric_cols])

        preds = model.fit_predict(X_scaled)
        scores = model.decision_function(X_scaled)

        anomaly_indices = df_sample[preds == -1].index

        for idx in anomaly_indices:
            score_idx = df_sample.index.get_loc(idx)
            row = df_sample.loc[idx]
            report = self.detector._generate_fast_anomaly_report(
                row, df_sample, method="One-Class SVM",
                score=scores[score_idx]
            )
            results.append((idx, report))

        return results

    def _elliptic_envelope_analysis(self, df_sample: pd.DataFrame) -> List[Tuple[int, str]]:
        """Анализ методом Elliptic Envelope"""
        results = []
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()

        contamination = self.detector._get_optimal_contamination(len(df_sample))

        model = EllipticEnvelope(
            contamination=contamination,
            random_state=42
        )

        scaler = RobustScaler()
        X_scaled = scaler.fit_transform(df_sample[numeric_cols])

        preds = model.fit_predict(X_scaled)
        scores = model.decision_function(X_scaled)

        anomaly_indices = df_sample[preds == -1].index

        for idx in anomaly_indices:
            score_idx = df_sample.index.get_loc(idx)
            row = df_sample.loc[idx]
            report = self.detector._generate_fast_anomaly_report(
                row, df_sample, method="Elliptic Envelope",
                score=scores[score_idx]
            )
            results.append((idx, report))

        return results

    def _auto_optimized_analysis(self, df_sample: pd.DataFrame) -> List[Tuple[int, str]]:
        """Автоматический выбор оптимального метода"""
        sample_size = len(df_sample)

        if sample_size > 500000:
            # Для очень больших данных используем только быстрые методы
            return self._fast_zscore_analysis(df_sample)
        elif sample_size > 100000:
            # Для больших данных используем Isolation Forest
            return self.detector.isolation_forest_analysis(df_sample)
        elif sample_size > 10000:
            # Для средних данных используем комбинированный анализ
            return self.detector.combined_analysis(df_sample)
        else:
            # Для маленьких данных используем полный комбинированный анализ
            return self.detector.combined_analysis(df_sample)

    def _generate_optimized_stats_report(self, df_sample: pd.DataFrame):
        """Генерирует оптимизированный статистический отчет"""
        report = "📊 Статистический отчет (Оптимизированный)\n\n"
        numeric_cols = df_sample.select_dtypes(include=[np.number]).columns.tolist()

        # Общая статистика
        report += f"Исходное количество строк: {len(self.original_df) if self.original_df is not None else len(self.df):,}\n"
        report += f"Анализируемое количество строк: {len(df_sample):,}\n"
        report += f"Общее количество аномалий: {len(self.anomalies):,}\n"

        if len(df_sample) > 0:
            report += f"Процент аномалий: {len(self.anomalies) / len(df_sample) * 100:.2f}%\n\n"

        # Быстрая статистика по колонкам (только для первых 10 колонок)
        for col in numeric_cols[:10]:
            col_data = df_sample[col]
            report += f"📌 {col}:\n"
            report += f"• Среднее: {col_data.mean():.2f}\n"
            report += f"• Медиана: {col_data.median():.2f}\n"
            report += f"• Стд. откл.: {col_data.std():.2f}\n"
            report += f"• Диапазон: [{col_data.min():.2f}, {col_data.max():.2f}]\n\n"

        if len(numeric_cols) > 10:
            report += f"... и еще {len(numeric_cols) - 10} колонок\n\n"

        # Информация о производительности
        if hasattr(self, 'start_time'):
            elapsed = time.time() - self.start_time
            report += f"⚡ Производительность:\n"
            report += f"• Время анализа: {elapsed:.1f} секунд\n"
            report += f"• Скорость: {len(df_sample) / elapsed:.0f} строк/сек\n"
            report += f"• Использование памяти: {df_sample.memory_usage(deep=True).sum() / (1024 ** 2):.1f} MB\n"

        self.stats_text.delete(1.0, "end")
        self.stats_text.insert("end", report)

    def _display_optimized_results(self):
        """Отображает результаты оптимизированного анализа"""
        self.tree.delete(*self.tree.get_children())
        self.details_text.delete(1.0, "end")

        # Настройка колонок таблицы
        self.tree["columns"] = ("row_id", "anomaly_type", "score", "cluster")
        self.tree.heading("row_id", text="Строка")
        self.tree.heading("anomaly_type", text="Тип")
        self.tree.heading("score", text="Сила")
        self.tree.heading("cluster", text="Кластер")

        # Заполнение таблицы (показываем только первые 2000 для производительности)
        display_limit = min(2000, len(self.anomalies))

        for i, (idx, desc) in enumerate(self.anomalies[:display_limit]):
            # Определяем тип аномалии
            if "Комбинированный" in desc:
                anomaly_type = "Комби"
            elif "Isolation Forest" in desc:
                anomaly_type = "IsoFor"
            elif "Z-Score" in desc:
                anomaly_type = "Z-Score"
            elif "IQR" in desc:
                anomaly_type = "IQR"
            elif "Local Outlier Factor" in desc:
                anomaly_type = "LOF"
            elif "One-Class SVM" in desc:
                anomaly_type = "SVM"
            elif "Elliptic Envelope" in desc:
                anomaly_type = "Ellipse"
            else:
                anomaly_type = "Другое"

            # Извлекаем оценку аномальности из описания
            score = "N/A"
            lines = desc.split('\n')
            for line in lines:
                if 'Аномальность:' in line or 'Голосов:' in line or 'Z-Score:' in line:
                    try:
                        score = line.split(':')[1].strip()
                        if score.replace('.', '').replace('-', '').isdigit():
                            score = f"{float(score):.2f}"
                    except:
                        pass
                    break

            # Получаем кластер
            cluster = self.cluster_map.get(idx, "-")
            if cluster == -1:
                cluster = "Един."
            else:
                cluster = str(cluster)

            self.tree.insert(
                "", "end",
                text=str(i + 1),
                values=(idx, anomaly_type, score, cluster)
            )

        if len(self.anomalies) > display_limit:
            self.tree.insert(
                "", "end",
                text="...",
                values=(f"+ еще {len(self.anomalies) - display_limit}", "аномалий", "", "")
            )

    def _show_anomaly_details(self):
        """Показывает детали выбранной аномалии"""
        selected = self.tree.focus()
        if not selected:
            return

        item = self.tree.item(selected)
        if not item['values'] or item['text'] == "...":
            return

        row_id = item['values'][0]

        desc = next((desc for idx, desc in self.anomalies if idx == row_id), "")
        self.details_text.delete(1.0, "end")
        self.details_text.insert("end", desc)

    def _export_results(self):
        """Экспортирует результаты анализа"""
        if not self.anomalies:
            messagebox.showwarning("Ошибка", "Нет данных для экспорта")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx"), ("CSV", "*.csv"), ("JSON", "*.json")]
        )

        if not file_path:
            return

        try:
            self.status_var.set("Экспорт результатов...")
            self.progress_var.set(0)

            # Подготовка данных для экспорта (ограничиваем для производительности)
            export_data = []
            max_export = min(10000, len(self.anomalies))

            for i, (idx, desc) in enumerate(self.anomalies[:max_export]):
                if i % 1000 == 0:
                    self.progress_var.set(int(50 * i / max_export))
                    self.master.update()

                row_data = {
                    "row_id": idx,
                    "description": desc,
                    "cluster": self.cluster_map.get(idx, None)
                }

                # Добавляем данные из оригинальной строки
                if idx in self.df.index:
                    row_data.update(self.df.loc[idx].to_dict())

                export_data.append(row_data)

            export_df = pd.DataFrame(export_data)
            self.progress_var.set(75)

            # Сохранение в выбранном формате
            if file_path.endswith('.xlsx'):
                export_df.to_excel(file_path, index=False)
            elif file_path.endswith('.csv'):
                export_df.to_csv(file_path, index=False)
            elif file_path.endswith('.json'):
                export_df.to_json(file_path, orient='records', indent=2, force_ascii=False)

            self.progress_var.set(100)

            export_info = f"Экспортировано {len(export_data)} аномалий"
            if len(self.anomalies) > max_export:
                export_info += f" из {len(self.anomalies)} (ограничение производительности)"

            messagebox.showinfo("Успех", f"Результаты успешно экспортированы\n\n{export_info}")

        except Exception as e:
            logging.error(f"Ошибка экспорта: {str(e)}", exc_info=True)
            messagebox.showerror("Ошибка", f"Ошибка экспорта:\n{str(e)}")
        finally:
            self.progress_var.set(0)

    def _generate_report(self, report_type: str = "html"):
        """Генерирует отчет в выбранном формате"""
        if not self.anomalies:
            messagebox.showwarning("Ошибка", "Нет данных для отчёта")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=f".{report_type}",
            filetypes=[(report_type.upper(), f"*.{report_type}")]
        )

        if not file_path:
            return

        try:
            self.status_var.set("Генерация отчёта...")
            self.progress_var.set(0)

            # Используем оригинальные данные для отчета, если они есть
            df_for_report = self.original_df if self.original_df is not None else self.df

            if report_type == "html":
                ReportGenerator.generate_html_report(df_for_report, self.anomalies, file_path)
            elif report_type == "pdf":
                ReportGenerator.generate_pdf_report(df_for_report, self.anomalies, file_path)

            self.progress_var.set(100)
            messagebox.showinfo("Успех", "Отчёт успешно сгенерирован")

            # Открываем отчет для просмотра
            if report_type == "html":
                webbrowser.open(file_path)

        except Exception as e:
            logging.error(f"Ошибка генерации отчёта: {str(e)}", exc_info=True)
            messagebox.showerror("Ошибка", f"Ошибка генерации отчёта:\n{str(e)}")
        finally:
            self.progress_var.set(0)

    def _show_scatter_plot(self):
        """Показывает точечный график с аномалиями"""
        if not hasattr(self, 'anomalies') or not self.anomalies:
            messagebox.showwarning("Ошибка", "Сначала выполните анализ данных")
            return

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            messagebox.showwarning("Ошибка", "Недостаточно числовых столбцов для визуализации")
            return

        # Окно выбора столбцов
        selector = tk.Toplevel(self.master)
        selector.title("Выбор столбцов для графика")
        selector.geometry("400x300")

        ttk.Label(selector, text="Выберите столбцы для визуализации").pack(pady=10)

        x_var = tk.StringVar(value=numeric_cols[0])
        y_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])
        color_var = tk.StringVar(value="None")

        # Выбор оси X
        ttk.Label(selector, text="Ось X:").pack()
        ttk.Combobox(selector, textvariable=x_var, values=numeric_cols).pack()

        # Выбор оси Y
        ttk.Label(selector, text="Ось Y:").pack()
        ttk.Combobox(selector, textvariable=y_var, values=numeric_cols).pack()

        # Выбор цвета (опционально)
        ttk.Label(selector, text="Цвет (опционально):").pack(pady=(10, 0))
        color_options = ["None"] + numeric_cols
        ttk.Combobox(selector, textvariable=color_var, values=color_options).pack()

        def show_plot():
            x_col = x_var.get()
            y_col = y_var.get()
            color_col = color_var.get() if color_var.get() != "None" else None

            # Для больших данных используем подвыборку для визуализации
            df_plot = self.df
            if len(self.df) > 50000:
                df_plot = self.df.sample(n=50000, random_state=42)

            if color_col:
                fig = px.scatter(
                    df_plot,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    color_continuous_scale=px.colors.sequential.Viridis,
                    hover_data=df_plot.columns.tolist()[:10],  # Ограничиваем hover данные
                    title=f"{y_col} vs {x_col} (цвет: {color_col})"
                )

                # Добавляем аномалии (только первые 1000 для производительности)
                anomalies_subset = [a for a in self.anomalies[:1000] if a[0] in df_plot.index]
                if anomalies_subset:
                    anomalies_df = df_plot.loc[[a[0] for a in anomalies_subset]]
                    fig.add_trace(
                        go.Scatter(
                            x=anomalies_df[x_col],
                            y=anomalies_df[y_col],
                            mode="markers",
                            marker=dict(color='red', size=8, line=dict(width=1, color='DarkSlateGrey')),
                            name="Аномалии",
                            hoverinfo='text',
                            text=[f"Строка: {idx}" for idx in anomalies_df.index]
                        )
                    )
            else:
                fig = EnhancedVisuals.scatter_plot(
                    df_plot,
                    self.anomalies[:1000],  # Ограничиваем количество аномалий
                    x_col,
                    y_col,
                    title=f"{y_col} vs {x_col}"
                )

            self._show_plot(fig)
            selector.destroy()

        ttk.Button(selector, text="Показать график", command=show_plot).pack(pady=10)

    def _show_parallel_coords(self):
        """Показывает график параллельных координат"""
        if not hasattr(self, 'anomalies') or not self.anomalies:
            messagebox.showwarning("Ошибка", "Сначала выполните анализ данных")
            return

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            messagebox.showwarning("Ошибка", "Недостаточно числовых столбцов для визуализации")
            return

        # Для больших данных используем подвыборку
        df_plot = self.df
        if len(self.df) > 10000:
            df_plot = self.df.sample(n=10000, random_state=42)

        # Ограничиваем количество колонок для производительности
        cols_to_plot = numeric_cols[:8]

        fig = EnhancedVisuals.parallel_coordinates(df_plot, self.anomalies[:1000], cols_to_plot)
        self._show_plot(fig)

    def _show_time_series(self):
        """Показывает временной ряд с аномалиями"""
        if not hasattr(self, 'anomalies') or not self.anomalies:
            messagebox.showwarning("Ошибка", "Сначала выполните анализ данных")
            return

        # Находим столбцы с датой/временем
        time_cols = [col for col in self.df.columns
                     if self.df[col].dtype in ['datetime64[ns]', 'object'] and
                     any(keyword in col.lower() for keyword in ['date', 'time', 'year', 'month', 'day'])]

        if not time_cols:
            messagebox.showwarning("Ошибка", "Не найден столбец с датой/временем")
            return

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Ошибка", "Не найдены числовые столбцы для визуализации")
            return

        # Окно выбора столбцов
        selector = tk.Toplevel(self.master)
        selector.title("Выбор столбцов для графика")
        selector.geometry("400x200")

        ttk.Label(selector, text="Выберите столбцы для визуализации").pack(pady=10)

        time_var = tk.StringVar(value=time_cols[0])
        value_var = tk.StringVar(value=numeric_cols[0])

        ttk.Label(selector, text="Временная ось:").pack()
        ttk.Combobox(selector, textvariable=time_var, values=time_cols).pack()

        ttk.Label(selector, text="Значение:").pack()
        ttk.Combobox(selector, textvariable=value_var, values=numeric_cols).pack()

        def show_plot():
            time_col = time_var.get()
            value_col = value_var.get()

            # Преобразуем в datetime, если еще не
            if not pd.api.types.is_datetime64_any_dtype(self.df[time_col]):
                try:
                    self.df[time_col] = pd.to_datetime(self.df[time_col])
                except:
                    messagebox.showerror("Ошибка", f"Не удалось преобразовать '{time_col}' в дату/время")
                    return

            # Для больших данных используем подвыборку
            df_plot = self.df
            if len(self.df) > 20000:
                df_plot = self.df.sample(n=20000, random_state=42).sort_values(time_col)

            fig = EnhancedVisuals.time_series_plot(
                df_plot,
                [a for a in self.anomalies[:1000] if a[0] in df_plot.index],
                time_col,
                value_col,
                title=f"Временной ряд: {value_col}"
            )
            self._show_plot(fig)
            selector.destroy()

        ttk.Button(selector, text="Показать график", command=show_plot).pack(pady=10)

    def _show_histogram(self):
        """Показывает гистограмму распределения с аномалиями"""
        if not hasattr(self, 'anomalies') or not self.anomalies:
            messagebox.showwarning("Ошибка", "Сначала выполните анализ данных")
            return

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Ошибка", "Не найдены числовые столбцы для визуализации")
            return

        # Окно выбора столбца
        selector = tk.Toplevel(self.master)
        selector.title("Выбор столбца для гистограммы")
        selector.geometry("300x150")

        ttk.Label(selector, text="Выберите столбец:").pack(pady=10)

        col_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(selector, textvariable=col_var, values=numeric_cols).pack()

        def show_plot():
            fig = EnhancedVisuals.show_histogram(
                self.df,
                col_var.get(),
                self.anomalies[:1000],  # Ограничиваем для производительности
                title=f"Распределение {col_var.get()}"
            )
            self._show_plot(fig)
            selector.destroy()

        ttk.Button(selector, text="Показать", command=show_plot).pack(pady=10)

    def _show_boxplot(self):
        """Показывает боксплот с аномалиями"""
        if not hasattr(self, 'anomalies') or not self.anomalies:
            messagebox.showwarning("Ошибка", "Сначала выполните анализ данных")
            return

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if not numeric_cols:
            messagebox.showwarning("Ошибка", "Не найдены числовые столбцы для визуализации")
            return

        # Окно выбора столбца
        selector = tk.Toplevel(self.master)
        selector.title("Выбор столбца для боксплота")
        selector.geometry("300x150")

        ttk.Label(selector, text="Выберите столбец:").pack(pady=10)

        col_var = tk.StringVar(value=numeric_cols[0])
        ttk.Combobox(selector, textvariable=col_var, values=numeric_cols).pack()

        def show_plot():
            fig = EnhancedVisuals.show_boxplot(
                self.df,
                col_var.get(),
                self.anomalies[:1000],  # Ограничиваем для производительности
                title=f"Боксплот {col_var.get()}"
            )
            self._show_plot(fig)
            selector.destroy()

        ttk.Button(selector, text="Показать", command=show_plot).pack(pady=10)

    def _show_clusters(self):
        """Показывает кластеризацию аномалий"""
        if not hasattr(self, 'cluster_map') or not self.cluster_map:
            messagebox.showwarning("Ошибка", "Сначала выполните анализ данных с кластеризацией")
            return

        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            messagebox.showwarning("Ошибка", "Недостаточно числовых столбцов для визуализации")
            return

        # Окно выбора столбцов
        selector = tk.Toplevel(self.master)
        selector.title("Выбор столбцов для кластеризации")
        selector.geometry("400x200")

        ttk.Label(selector, text="Выберите оси для визуализации кластеров").pack(pady=10)

        x_var = tk.StringVar(value=numeric_cols[0])
        y_var = tk.StringVar(value=numeric_cols[1] if len(numeric_cols) > 1 else numeric_cols[0])

        ttk.Label(selector, text="Ось X:").pack()
        ttk.Combobox(selector, textvariable=x_var, values=numeric_cols).pack()

        ttk.Label(selector, text="Ось Y:").pack()
        ttk.Combobox(selector, textvariable=y_var, values=numeric_cols).pack()

        def show_plot():
            # Ограничиваем количество аномалий для визуализации
            anomalies_to_show = [a[0] for a in self.anomalies[:2000]]

            fig = OptimizedAnomalyClustering.visualize_clusters(
                self.df,
                anomalies_to_show,
                self.cluster_map,
                x_var.get(),
                y_var.get(),
                title="Кластеризация аномалий"
            )
            self._show_plot(fig)
            selector.destroy()

        ttk.Button(selector, text="Показать", command=show_plot).pack(pady=10)


if __name__ == "__main__":
    # Проверяем доступность необходимых библиотек
    try:
        import psutil
        import numba
    except ImportError as e:
        print(f"Внимание: Некоторые оптимизации недоступны. Установите: pip install psutil numba")
        print(f"Ошибка: {e}")

    root = tk.Tk()
    app = AdvancedAnomalyDetector(root)
    root.mainloop()