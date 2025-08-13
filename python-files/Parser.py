# -*- coding: utf-8 -*-
"""
ASP Parser v5.1 (Omega Edition) - Corrected

Профессиональная OSINT-платформа для поиска, анализа и визуализации общедоступных данных.
Версия "Омега" включает систему проектов, интерактивный граф связей и динамический рекурсивный поиск.

Ключевые зависимости:
- pip install PyQt6 requests beautifulsoup4 pyqtgraph numpy

Опциональные зависимости для полного функционала экспорта:
- pip install openpyxl (для экспорта в .xlsx)
- pip install pdfkit (для экспорта в .pdf, требует установки wkhtmltopdf в систему: https://wkhtmltopdf.org/)
"""

import sys
import os
import re
import csv
import json
import time
import random
import sqlite3
import logging
import math
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import quote_plus, urlparse, urljoin
from collections import deque, defaultdict
import numpy

import requests
from bs4 import BeautifulSoup
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QProgressBar, QMessageBox, QFileDialog, QGroupBox, QFormLayout,
    QCheckBox, QHeaderView, QTextEdit, QComboBox, QTabWidget,
    QStyledItemDelegate, QMenu, QPlainTextEdit, QListWidget,
    QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QSettings
from PyQt6.QtGui import (
    QColor, QBrush, QDesktopServices, QIcon, QFont,
    QAction, QTextCursor, QPalette
)
import pyqtgraph as pg

# --- Настройка логирования ---
logging.basicConfig(
    filename=f'asp_parser_omega_{datetime.now().strftime("%Y%m%d")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

# --- Графические настройки для графа ---
pg.setConfigOption('background', '#F5F7FA')
pg.setConfigOption('foreground', '#2c3e50')


class LinkDelegate(QStyledItemDelegate):
    """Делегат для отрисовки кликабельных ссылок в таблице."""
    def paint(self, painter, option, index):
        if index.column() == 2:  # Столбец "Источник"
            option.font.setUnderline(True)
            text_color = option.palette.color(QPalette.ColorRole.Link)
            option.palette.setColor(option.palette.ColorRole.Text, text_color)
        super().paint(painter, option, index)

    def editorEvent(self, event, model, option, index):
        if index.column() == 2 and event.type() == event.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton:
            if (data := index.data(Qt.ItemDataRole.UserRole)) and 'url' in data:
                if (url := data['url']).startswith(('http://', 'https://')):
                    QDesktopServices.openUrl(QUrl(url))
                    return True
        return super().editorEvent(event, model, option, index)


class GraphView(pg.PlotWidget):
    """Виджет для отображения интерактивного графа связей."""
    node_clicked = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.graph = pg.GraphItem()
        self.addItem(self.graph)
        # ИСПРАВЛЕНИЕ: Сигнал находится внутри scatter, а не самого graph
        self.graph.scatter.sigClicked.connect(self._on_node_clicked)
        
        self.nodes = {}
        self.edges = set()
        self.node_index_map = {}
        
        self.node_colors = {
            'initial': (211, 84, 0), 'fio': (41, 128, 185), 'email': (192, 57, 43),
            'phone': (39, 174, 96), 'username': (243, 156, 18), 'company': (142, 68, 173),
            'default': (127, 140, 141), 'url': (52, 73, 94)
        }
        self.symbols = {
            'initial': 'star', 'fio': 'o', 'email': 't', 'phone': 's',
            'username': 'd', 'company': 'h', 'default': '+', 'url': 'x'
        }
        self.main_node_size = 20
        self.sub_node_size = 12

    def _on_node_clicked(self, scatter_plot_item, spot_items):
        if spot_items:
            spot = spot_items[0]
            node_id = spot.data()
            if node_id:
                self.node_clicked.emit(str(node_id))

    def add_relation(self, source_node, found_data):
        source_type = self._get_node_type(source_node)
        self._add_node(source_node, source_type, size=self.main_node_size)

        node_type = found_data.get('type', 'default')
        node_value = found_data.get('value')
        self._add_node(node_value, node_type, size=self.sub_node_size)
        
        self._add_edge(source_node, node_value)
        self.update_graph()

    def _get_node_type(self, value):
        clean_value = re.sub(r'\D', '', value)
        if re.match(r'^(7|8)\d{10}$', clean_value): return 'phone'
        if '@' in value: return 'email'
        if len(value.split()) > 1 and all(p[0].isupper() for p in value.split()): return 'fio'
        if re.match(r'^\d{10}$|^\d{12}$', value): return 'inn'
        return 'username'

    def _add_node(self, node_id, node_type='default', size=12):
        if node_id not in self.nodes:
            self.nodes[node_id] = {'type': node_type, 'size': size}

    def _add_edge(self, source_id, dest_id):
        if source_id and dest_id and source_id != dest_id:
            edge = tuple(sorted((source_id, dest_id)))
            self.edges.add(edge)

    def update_graph(self):
        node_ids = list(self.nodes.keys())
        if not node_ids: return

        self.node_index_map = {nid: i for i, nid in enumerate(node_ids)}
        
        pos = self._calculate_positions(node_ids)
        adj = numpy.array([ (self.node_index_map[u], self.node_index_map[v]) for u,v in self.edges if u in self.node_index_map and v in self.node_index_map], dtype=int)
        symbols = [self.symbols.get(self.nodes[nid]['type'], 'o') for nid in node_ids]
        sizes = [self.nodes[nid]['size'] for nid in node_ids]
        brushes = [pg.mkBrush(self.node_colors.get(self.nodes[nid]['type'], self.node_colors['default'])) for nid in node_ids]
        
        self.graph.setData(pos=pos, adj=adj, symbol=symbols, size=sizes, symbolBrush=brushes, data=node_ids)

    def _calculate_positions(self, node_ids):
        positions = {}
        center_nodes = [nid for nid, data in self.nodes.items() if data.get('is_initial')]
        if not center_nodes:
            center_nodes = [node_ids[0]] if node_ids else []

        for i, nid in enumerate(center_nodes):
            angle = 2 * math.pi * i / len(center_nodes) if len(center_nodes) > 1 else 0
            positions[nid] = (10 * math.cos(angle), 10 * math.sin(angle))

        for nid in node_ids:
            if nid not in positions:
                connected_center = None
                for u, v in self.edges:
                    if u == nid and v in center_nodes: connected_center = v; break
                    if v == nid and u in center_nodes: connected_center = u; break
                
                if connected_center:
                    parent_pos = positions[connected_center]
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.uniform(2, 4)
                    positions[nid] = (parent_pos[0] + radius * math.cos(angle), parent_pos[1] + radius * math.sin(angle))
                else:
                    positions[nid] = (random.uniform(-15, 15), random.uniform(-15, 15))
        
        return numpy.array([positions.get(nid, (0,0)) for nid in node_ids])

    def clear(self):
        self.nodes.clear()
        self.edges.clear()
        self.node_index_map.clear()
        self.graph.setData(pos=None, adj=None)

    def get_state(self):
        return {'nodes': self.nodes, 'edges': list(self.edges)}

    def set_state(self, state):
        self.nodes = state.get('nodes', {})
        self.edges = set(tuple(e) for e in state.get('edges', []))
        self.update_graph()


class EnhancedDataScanner:
    """Гибридный сканер: находит релевантные страницы, затем извлекает все типы ПДн."""
    def __init__(self):
        self.patterns = {
            'phone': r'(?<!\d)(?:\+7|8)[\s\-]?\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}(?!\d)',
            'email': r'(?<!\w)([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})(?!\w)',
            'fio': r'(?<!\w)([А-ЯЁ][а-яё]+(?:-[А-ЯЁ][а-яё]+)?\s+[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)?)(?!\w)',
            'passport': r'(?<!\w)(\d{2}\s?\d{2}\s?\d{6})(?!\w)|(серия\s?\d{4}\s?номер\s?\d{6})',
            'snils': r'(?<!\w)(\d{3}-\d{3}-\d{3}\s?\d{2})(?!\w)',
            'inn': r'(?<!\w)(?<!\d)(\d{10}|\d{12})(?!\d)',
            'car_number': r'(?<!\w)([АВЕКМНОРСТУХ]\d{3}[АВЕКМНОРСТУХ]{2}\d{2,3})(?!\w)',
            'ogrn': r'(?<!\d)(1\d{12}|5\d{14})(?!\d)',
        }
        self.context_width = 150

    def _is_page_relevant(self, text_lower, search_params):
        if not search_params: return True
        for value in search_params.values():
            if value.lower() in text_lower:
                return True
        return False

    def scan_text(self, text, source_url, search_params):
        results = []
        text_lower = text.lower()
        if not self._is_page_relevant(text_lower, search_params):
            return []

        for data_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matched_value = match.group().strip()
                context = self._get_context(text, match.start(), match.end())
                results.append({
                    'source': urlparse(source_url).netloc or source_url,
                    'url': source_url, 'type': data_type, 'value': matched_value,
                    'context': context, 'status': 'found', 'timestamp': datetime.now().isoformat(),
                    'full_text': self._get_full_context(text, match.start(), match.end())
                })
        return results

    def _get_context(self, text, start, end):
        start_pos = max(0, start - self.context_width)
        end_pos = min(len(text), end + self.context_width)
        context = text[start_pos:end_pos].strip()
        context = re.sub(r'\s+', ' ', context)
        if start_pos > 0: context = "... " + context
        if end_pos < len(text): context = context + " ..."
        return context

    def _get_full_context(self, text, start, end, width=500):
        start_pos = max(0, start - width)
        end_pos = min(len(text), end + width)
        return text[start_pos:end_pos].strip()


class DataSearchWorker(QThread):
    new_entity_found = pyqtSignal(str, str)
    found_data = pyqtSignal(dict, str)
    finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, search_entity, selected_sources, search_depth_index=1, api_keys=None):
        super().__init__()
        self.search_entity = search_entity
        self.search_params = {search_entity['type']: search_entity['value']}
        self.selected_sources = selected_sources
        self.api_keys = api_keys or {}
        self.cancel_requested = False
        self.scanner = EnhancedDataScanner()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Accept-Language': 'ru-RU,ru;q=0.9'
        })
        depth_map = {0: 3, 1: 7, 2: 12}
        self.max_links_per_query = depth_map.get(search_depth_index, 7)
        self.processed_urls = set()
        self.load_proxies()

    def run(self):
        try:
            search_queries = self._generate_search_queries()
            all_results = []

            method_map = {
                "Поисковики (Google, Yandex, DDG)": lambda: self.search_generic_engines(search_queries),
                "Социальные сети": lambda: self.search_sites(search_queries, ["vk.com", "ok.ru", "github.com"]),
                "Telegram": lambda: self.search_sites(search_queries, ["t.me", "tgstat.ru", "telegram.me"]),
                "Бизнес-реестры": lambda: self.search_sites(search_queries, ["rusprofile.ru", "list-org.com", "sbis.ru"]),
                "Сайты с резюме": lambda: self.search_sites(search_queries, ["hh.ru", "superjob.ru", "rabota.ru"]),
                "Доски объявлений": lambda: self.search_sites(search_queries, ["avito.ru", "drom.ru", "auto.ru", "cian.ru"]),
                "Форумы": lambda: self.search_sites(search_queries, ["pikabu.ru", "dark2web.com", "breachforums.cx", "xss.is"]),
                "Pastebin и аналоги": lambda: self.search_sites(search_queries, ["pastebin.com", "ps.p.gg", "rentry.co"]),
                "Государственные реестры": self.search_gov_registries,
                "Базы утечек (HIBP)": self.search_leak_databases,
            }

            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = {executor.submit(method_map[source]): source for source in self.selected_sources if source in method_map}
                for future in as_completed(futures):
                    if self.cancel_requested: break
                    try:
                        all_results.extend(future.result())
                    except Exception as e: logger.error(f"Ошибка в под-потоке: {e}", exc_info=True)
            
            unique_results = { (r['value'], r['url']): r for r in all_results }.values()
            for res in unique_results:
                self.found_data.emit(res, self.search_entity['value'])
                if res['value'] != self.search_entity['value']:
                    self.new_entity_found.emit(res['type'], res['value'])
        except Exception as e:
            self.error_occurred.emit(f"Критическая ошибка в потоке: {e}")
            logger.error(f"Критическая ошибка поиска: {e}", exc_info=True)
        finally:
            if not self.isFinished():
                self.finished.emit()

    def _generate_search_queries(self):
        queries, p = set(), self.search_params
        val = self.search_entity['value']
        typ = self.search_entity['type']
        
        queries.add(f'"{val}"')
        if typ == 'fio': queries.add(f'"{val}" резюме | контакты | ИП | "судебное решение"')
        if typ == 'username': queries.add(f'"{val}" profile | user | профиль')
        if typ == 'phone': queries.add(f'"{val}" объявление | whatsapp | telegram')
        if typ == 'email': queries.add(f'"{val}" password | pass | пароль | утечка filetype:sql,log,txt')
        if typ == 'company': queries.add(f'"{val}" ИНН | ОГРН | "генеральный директор" | отзывы')
        if typ == 'car_number': queries.add(f'"{val}" продажа | дтп | штраф')
        return list(queries)

    def _process_links(self, links):
        results = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_url = {executor.submit(self.safe_request, link): link for link in links if link and link not in self.processed_urls}
            for future in as_completed(future_to_url):
                if self.cancel_requested: break
                link, response = future_to_url[future], future.result()
                if response:
                    self.processed_urls.add(link)
                    try: results.extend(self.scanner.scan_text(response.text, link, self.search_params))
                    except Exception as e: logger.warning(f"Ошибка анализа {link}: {e}")
        return results

    def search_generic_engines(self, queries):
        all_links = set()
        for query in queries:
            if self.cancel_requested: break
            # DuckDuckGo
            ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            if response := self.safe_request(ddg_url):
                soup = BeautifulSoup(response.text, 'html.parser')
                for a in soup.select('a.result__a')[:self.max_links_per_query]: all_links.add(a['href'])
            
            # Google API
            if (key := self.api_keys.get('google_key')) and (cx := self.api_keys.get('google_cx')):
                google_url = f"https://www.googleapis.com/customsearch/v1?q={quote_plus(query)}&key={key}&cx={cx}&num={min(10, self.max_links_per_query)}"
                if g_response := self.safe_request(google_url, is_api=True):
                    if g_response.status_code == 200:
                        for item in g_response.json().get('items', []): all_links.add(item['link'])

            # Yandex API
            if (y_key := self.api_keys.get('yandex_key')) and (y_user := self.api_keys.get('yandex_user')):
                yandex_url = f"https://yandex.ru/search/xml?user={y_user}&key={y_key}&query={quote_plus(query)}&l10n=ru&sortby=rlv&filter=none"
                if y_response := self.safe_request(yandex_url, is_api=True):
                    if y_response.status_code == 200:
                        root = ET.fromstring(y_response.text)
                        for url_node in root.findall(".//doc/url"):
                            if url_node.text: all_links.add(url_node.text)

        return self._process_links(list(all_links))
        
    def search_sites(self, queries, sites):
        all_links = set()
        for query in queries:
            if self.cancel_requested: break
            for site in sites:
                site_query = f'{query} site:{site}'
                if (key := self.api_keys.get('google_key')) and (cx := self.api_keys.get('google_cx')):
                     google_url = f"https://www.googleapis.com/customsearch/v1?q={quote_plus(site_query)}&key={key}&cx={cx}&num=3"
                     if g_response := self.safe_request(google_url, is_api=True):
                         if g_response.status_code == 200:
                             for item in g_response.json().get('items', []): all_links.add(item['link'])
        return self._process_links(list(all_links))

    def search_gov_registries(self):
        results = []
        if fio := self.search_params.get('fio'):
            results.append({'source': 'ГАС Правосудие', 'url': f"https://bsr.sudrf.ru/bigs/portal.html#%7B%22query%22:%22text:({quote_plus(fio)})%22%7D", 'type': 'gov_search', 'value': fio, 'context': 'Прямая ссылка на поиск в судебных актах.', 'status': 'link', 'timestamp': datetime.now().isoformat(), 'full_text': ''})
            results.append({'source': 'Реестр ИП (ФНС)', 'url': f"https://egrul.nalog.ru/search-result/?query={quote_plus(fio)}", 'type': 'gov_search', 'value': fio, 'context': 'Прямая ссылка на поиск в реестре ФНС.', 'status': 'link', 'timestamp': datetime.now().isoformat(), 'full_text': ''})
        if company := self.search_params.get('company'):
            results.append({'source': 'Реестр ЮЛ (ФНС)', 'url': f"https://egrul.nalog.ru/search-result/?query={quote_plus(company)}", 'type': 'gov_search', 'value': company, 'context': 'Прямая ссылка на поиск в реестре ФНС.', 'status': 'link', 'timestamp': datetime.now().isoformat(), 'full_text': ''})
        return results

    def search_leak_databases(self):
        results = []
        if not (hibp_key := self.api_keys.get('hibp')) or not (email := self.search_params.get('email')):
            return []
        
        url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
        headers = {"hibp-api-key": hibp_key, "user-agent": "ASP-Parser-Pro"}
        if response := self.safe_request(url, headers=headers, is_api=True):
            if response.status_code == 200:
                for breach in response.json():
                    results.append({
                        'source': 'HaveIBeenPwned', 'url': f"https://haveibeenpwned.com/breach/{breach['Name']}",
                        'type': 'email_leak', 'value': email, 'status': 'leaked',
                        'context': f"Утечка в {breach['Title']} ({breach['BreachDate']})",
                        'timestamp': datetime.now().isoformat(), 'full_text': breach.get('Description', '')})
        return results
    
    def safe_request(self, url, is_api=False, **kwargs):
        if self.cancel_requested: return None
        time.sleep(random.uniform(0.1, 0.3) if is_api else random.uniform(0.4, 1.2))
        try:
            response = self.session.get(url, timeout=15, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.warning(f"Запрос к {url} не удался: {e}")
        return None

    def load_proxies(self):
        if os.path.exists('proxies.txt'):
            try:
                with open('proxies.txt', 'r', encoding='utf-8') as f:
                    proxies = [line.strip() for line in f if line.strip()]
                    if proxies:
                        proxy = random.choice(proxies)
                        self.session.proxies.update({'http': f'http://{proxy}', 'https': f'https://{proxy}'})
                        logger.info(f"Используется прокси: {proxy}")
            except Exception as e: logger.warning(f"Не удалось загрузить прокси: {e}")

    def cancel(self):
        self.cancel_requested = True
        logger.info("Запрошена отмена поиска.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASP Parser 5.0 Omega")
        self.setGeometry(50, 50, 1800, 1000)
        self.setWindowIcon(QIcon.fromTheme("system-search"))
        
        self.search_worker = None
        self.current_project_path = None
        self.is_searching = False
        
        self.dynamic_search_queue = deque()
        self.processed_entities = set()
        self.data_confidence = defaultdict(int)
        self.input_widgets = {}

        self.init_ui()
        self.set_modern_style()
        self.load_settings()
        self.new_project()

    def set_modern_style(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #F5F7FA;
                color: #2c3e50;
                font-family: Segoe UI, Arial;
            }
            QGroupBox {
                border: 1px solid #dbe1e8;
                border-radius: 8px;
                margin-top: 10px;
                padding: 20px 10px 10px 10px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 15px;
                padding: 0 5px;
                color: #3498db;
                font-weight: bold;
                font-size: 11pt;
            }
            QLabel { font-size: 10pt; }
            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QListWidget {
                border: 1px solid #dbe1e8;
                border-radius: 5px;
                padding: 8px;
                background-color: #FFFFFF;
                font-size: 10pt;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QListWidget:focus {
                border-color: #3498db;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 10pt;
                font-weight: bold;
                border: 1px solid #bdc3c7;
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QPushButton:hover { background-color: #e0e6e8; }
            QPushButton#PrimaryButton {
                background-color: #3498db;
                color: white;
                border: none;
            }
            QPushButton#PrimaryButton:hover { background-color: #2980b9; }
            QPushButton:disabled {
                background-color: #ecf0f1;
                color: #95a5a6;
                border-color: #dbe1e8;
            }
            QTableWidget {
                border: 1px solid #dbe1e8;
                background-color: #FFFFFF;
                selection-background-color: #3498db;
                selection-color: white;
                gridline-color: #ecf0f1;
                font-size: 9pt;
            }
            QHeaderView::section {
                padding: 8px;
                background-color: #F5F7FA;
                border: 1px solid #dbe1e8;
                font-weight: bold;
                font-size: 10pt;
            }
            QProgressBar {
                border: 1px solid #dbe1e8;
                border-radius: 5px;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk { background-color: #2ecc71; border-radius: 4px; }
            QTabWidget::pane { border: 1px solid #dbe1e8; border-top: none; }
            QTabBar::tab {
                padding: 12px 25px;
                background: transparent;
                border: 1px solid transparent;
                border-bottom: none;
                color: #7f8c8d;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background: #F5F7FA;
                border-color: #dbe1e8;
                border-bottom-color: #F5F7FA; /* Hide bottom border */
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #3498db;
            }
            QMenu { border: 1px solid #dbe1e8; background-color: #FFFFFF; }
            QMenu::item:selected { background-color: #3498db; color: white; }
            QSplitter::handle { background-color: #dbe1e8; }
            QSplitter::handle:horizontal { width: 4px; }
            QSplitter::handle:vertical { height: 4px; }
        """)

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.create_menu()
        
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.setup_search_panel(left_layout)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Segoe UI", 10))
        self.setup_dashboard_tab()
        self.setup_results_tab()
        self.setup_graph_tab()
        self.setup_log_tab()
        self.setup_settings_tab()
        right_layout.addWidget(self.tabs)

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([500, 1300])

        self.layout.addWidget(main_splitter)

    def create_menu(self):
        menubar = self.menuBar()
        project_menu = menubar.addMenu("Проект")
        new_action = QAction(QIcon.fromTheme("document-new"), "Новый проект", self)
        new_action.triggered.connect(self.new_project)
        project_menu.addAction(new_action)
        open_action = QAction(QIcon.fromTheme("document-open"), "Открыть проект...", self)
        open_action.triggered.connect(self.open_project)
        project_menu.addAction(open_action)
        save_action = QAction(QIcon.fromTheme("document-save"), "Сохранить проект", self)
        save_action.triggered.connect(self.save_project)
        project_menu.addAction(save_action)
        save_as_action = QAction(QIcon.fromTheme("document-save-as"), "Сохранить как...", self)
        save_as_action.triggered.connect(lambda: self.save_project(new_path=True))
        project_menu.addAction(save_as_action)
        
        file_menu = menubar.addMenu("Файл")
        export_action = QAction(QIcon.fromTheme("document-save-as"), "Экспорт результатов...", self)
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Выход", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("Справка")
        about_action = QAction(QIcon.fromTheme("help-about"), "О программе", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_search_panel(self, parent_layout):
        personal_group = QGroupBox("Персональные данные")
        personal_layout = QFormLayout(personal_group)
        self.input_widgets['fio'] = QLineEdit()
        self.input_widgets['username'] = QLineEdit()
        self.input_widgets['phone'] = QLineEdit()
        self.input_widgets['email'] = QLineEdit()
        personal_layout.addRow("ФИО:", self.input_widgets['fio'])
        personal_layout.addRow("Никнейм:", self.input_widgets['username'])
        personal_layout.addRow("Телефон:", self.input_widgets['phone'])
        personal_layout.addRow("Email:", self.input_widgets['email'])
        
        docs_group = QGroupBox("Документы и номера")
        docs_layout = QFormLayout(docs_group)
        self.input_widgets['passport'] = QLineEdit()
        self.input_widgets['snils'] = QLineEdit()
        self.input_widgets['inn'] = QLineEdit()
        self.input_widgets['car_number'] = QLineEdit()
        docs_layout.addRow("Паспорт (серия номер):", self.input_widgets['passport'])
        docs_layout.addRow("СНИЛС:", self.input_widgets['snils'])
        docs_layout.addRow("ИНН физ. лица:", self.input_widgets['inn'])
        docs_layout.addRow("Номер авто:", self.input_widgets['car_number'])

        misc_group = QGroupBox("Другие данные")
        misc_layout = QFormLayout(misc_group)
        self.input_widgets['address'] = QLineEdit()
        self.input_widgets['company'] = QLineEdit()
        misc_layout.addRow("Адрес:", self.input_widgets['address'])
        misc_layout.addRow("Компания (название/ИНН/ОГРН):", self.input_widgets['company'])

        sources_group = QGroupBox("Источники поиска")
        sources_layout = QVBoxLayout(sources_group)
        self.source_checkboxes = {
            "Поисковики (Google, Yandex, DDG)": QCheckBox("Поисковики (требует API)"),
            "Социальные сети": QCheckBox("Социальные сети"),
            "Telegram": QCheckBox("Telegram (поиск по каналам)"),
            "Бизнес-реестры": QCheckBox("Бизнес-реестры"),
            "Сайты с резюме": QCheckBox("Сайты с резюме"),
            "Доски объявлений": QCheckBox("Доски объявлений"),
            "Форумы": QCheckBox("Форумы"),
            "Pastebin и аналоги": QCheckBox("Pastebin и хранилища текста"),
            "Государственные реестры": QCheckBox("Гос. реестры"),
            "Базы утечек (HIBP)": QCheckBox("Базы утечек (по Email)"),
        }
        for cb in self.source_checkboxes.values():
            cb.setChecked(True)
            sources_layout.addWidget(cb)

        controls_layout = QHBoxLayout()
        self.search_button = QPushButton(QIcon.fromTheme("system-search"), "Начать расследование")
        self.search_button.setObjectName("PrimaryButton")
        self.search_button.clicked.connect(self.start_search)
        self.stop_button = QPushButton(QIcon.fromTheme("process-stop"), "Остановить")
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_search)
        controls_layout.addStretch()
        controls_layout.addWidget(self.search_button)
        controls_layout.addWidget(self.stop_button)
        controls_layout.addStretch()

        status_layout = QVBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Готов к работе")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.status_label)

        parent_layout.addWidget(personal_group)
        parent_layout.addWidget(docs_group)
        parent_layout.addWidget(misc_group)
        parent_layout.addWidget(sources_group)
        parent_layout.addStretch()
        parent_layout.addLayout(controls_layout)
        parent_layout.addLayout(status_layout)

    def setup_dashboard_tab(self):
        tab = QWidget()
        layout = QHBoxLayout(tab)
        
        self.email_list = QListWidget()
        self.phone_list = QListWidget()
        self.username_list = QListWidget()
        self.company_list = QListWidget()

        layout.addWidget(self.create_dashboard_group("Найденные Email", self.email_list))
        layout.addWidget(self.create_dashboard_group("Найденные Телефоны", self.phone_list))
        layout.addWidget(self.create_dashboard_group("Найденные Никнеймы", self.username_list))
        layout.addWidget(self.create_dashboard_group("Найденные Компании", self.company_list))
        
        self.tabs.addTab(tab, QIcon.fromTheme("view-dashboard"), "Дашборд")

    def create_dashboard_group(self, title, list_widget):
        group = QGroupBox(title)
        layout = QVBoxLayout(group)
        layout.addWidget(list_widget)
        return group

    def setup_results_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        toolbar = QHBoxLayout()
        self.export_button = QPushButton(QIcon.fromTheme("document-save"), "Экспорт")
        self.export_button.clicked.connect(self.export_results)
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Фильтр по всем полям...")
        self.filter_input.textChanged.connect(self.apply_filter)
        toolbar.addWidget(self.export_button)
        toolbar.addStretch(1)
        toolbar.addWidget(QLabel("Фильтр:"))
        toolbar.addWidget(self.filter_input)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(8)
        self.results_table.setHorizontalHeaderLabels(["", "Доверие", "Источник", "Тип", "Значение", "Контекст", "Статус", "Дата"])
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.results_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)
        self.results_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.results_table.setWordWrap(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setSortingEnabled(True)
        self.results_table.cellDoubleClicked.connect(lambda r, c: self.show_result_details(r))
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_context_menu)
        self.results_table.setItemDelegateForColumn(2, LinkDelegate(self))
        self.results_table.setColumnWidth(2, 150)
        self.results_table.setColumnWidth(3, 100)
        self.results_table.setColumnWidth(4, 200)

        layout.addLayout(toolbar)
        layout.addWidget(self.results_table)
        self.tabs.addTab(tab, QIcon.fromTheme("view-list-details"), "Результаты")

    def setup_graph_tab(self):
        self.graph_view = GraphView()
        self.graph_view.node_clicked.connect(self.highlight_node_in_table)
        self.tabs.addTab(self.graph_view, QIcon.fromTheme("network-workgroup"), "Граф Анализа")

    def setup_log_tab(self):
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 10))
        self.tabs.addTab(self.log_text, QIcon.fromTheme("text-x-generic"), "Журнал")

    def setup_settings_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        tab.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        search_group = QGroupBox("Общие настройки")
        search_layout = QFormLayout(search_group)
        self.search_depth_combo = QComboBox()
        self.search_depth_combo.addItems(["Быстрый (до 3 ссылок/запрос)", "Стандартный (до 7)", "Глубокий (до 12)"])
        self.search_depth_combo.setCurrentIndex(1)
        self.proxy_checkbox = QCheckBox("Использовать прокси из файла proxies.txt")
        self.dynamic_search_checkbox = QCheckBox("Включить динамический (рекурсивный) поиск")
        self.dynamic_search_checkbox.setChecked(True)
        search_layout.addRow("Глубина поиска:", self.search_depth_combo)
        search_layout.addRow(self.proxy_checkbox)
        search_layout.addRow(self.dynamic_search_checkbox)
        
        api_group = QGroupBox("Ключи API")
        api_layout = QFormLayout(api_group)
        self.hibp_api_key_input = QLineEdit()
        self.google_api_key_input = QLineEdit()
        self.google_cx_input = QLineEdit()
        self.yandex_key_input = QLineEdit()
        self.yandex_user_input = QLineEdit()
        api_layout.addRow("HaveIBeenPwned Key:", self.hibp_api_key_input)
        api_layout.addRow("Google API Key:", self.google_api_key_input)
        api_layout.addRow("Google CX ID:", self.google_cx_input)
        api_layout.addRow("Yandex XML Key:", self.yandex_key_input)
        api_layout.addRow("Yandex XML User:", self.yandex_user_input)
        
        info_group = QGroupBox("Как получить ключи")
        info_layout = QVBoxLayout(info_group)
        info_text = QPlainTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(
            "Google: developers.google.com/custom-search/v1/overview\n"
            "Yandex: yandex.ru/dev/xml/\n"
            "HIBP: haveibeenpwned.com/API/Key"
        )
        info_layout.addWidget(info_text)

        save_button_layout = QHBoxLayout()
        save_button = QPushButton(QIcon.fromTheme("document-save"), "Сохранить настройки")
        save_button.setObjectName("PrimaryButton")
        save_button.clicked.connect(self.save_settings)
        save_button_layout.addStretch()
        save_button_layout.addWidget(save_button)
        
        layout.addWidget(search_group)
        layout.addWidget(api_group)
        layout.addWidget(info_group)
        layout.addStretch()
        layout.addLayout(save_button_layout)
        self.tabs.addTab(tab, QIcon.fromTheme("preferences-system"), "Настройки")

    def new_project(self):
        self.current_project_path = None
        self.setWindowTitle("ASP Parser 5.0 Omega - Новый проект")
        
        for widget in self.input_widgets.values():
            widget.clear()
            
        self.results_table.setRowCount(0)
        self.log_text.clear()
        self.graph_view.clear()
        self.email_list.clear()
        self.phone_list.clear()
        self.username_list.clear()
        self.company_list.clear()
        
        self.processed_entities.clear()
        self.data_confidence.clear()
        self.dynamic_search_queue.clear()
        
        self.log("Создан новый проект.")

    def save_project(self, new_path=False):
        if new_path or not self.current_project_path:
            path, _ = QFileDialog.getSaveFileName(self, "Сохранить проект", "", "ASP Project Files (*.aspproj)")
            if not path: return
            self.current_project_path = path
        
        project_data = {
            'version': '5.1',
            'inputs': {name: widget.text() for name, widget in self.input_widgets.items()},
            'results': [self.results_table.item(row, 2).data(Qt.ItemDataRole.UserRole) for row in range(self.results_table.rowCount())],
            'graph': self.graph_view.get_state(),
            'confidence': dict(self.data_confidence),
            'processed_entities': list(self.processed_entities)
        }
        
        try:
            with open(self.current_project_path, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, ensure_ascii=False, indent=4)
            self.log(f"Проект сохранен в {self.current_project_path}")
            self.setWindowTitle(f"ASP Parser 5.0 Omega - {os.path.basename(self.current_project_path)}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка сохранения", f"Не удалось сохранить проект: {e}")

    def open_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Открыть проект", "", "ASP Project Files (*.aspproj)")
        if not path: return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            self.new_project()
            
            for name, value in project_data.get('inputs', {}).items():
                if name in self.input_widgets:
                    self.input_widgets[name].setText(value)
            
            self.data_confidence = defaultdict(int, project_data.get('confidence', {}))
            self.processed_entities = set(project_data.get('processed_entities', []))

            for result in project_data.get('results', []):
                self.add_result(result, None, from_project=True)
            
            self.graph_view.set_state(project_data.get('graph', {}))

            self.current_project_path = path
            self.setWindowTitle(f"ASP Parser 5.0 Omega - {os.path.basename(self.current_project_path)}")
            self.log(f"Проект {self.current_project_path} загружен.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", f"Не удалось загрузить проект: {e}")

    def get_search_params(self):
        return {name: widget.text().strip() for name, widget in self.input_widgets.items()}

    def get_api_keys(self):
        return {
            'hibp': self.hibp_api_key_input.text().strip(),
            'google_key': self.google_api_key_input.text().strip(),
            'google_cx': self.google_cx_input.text().strip(),
            'yandex_key': self.yandex_key_input.text().strip(),
            'yandex_user': self.yandex_user_input.text().strip(),
        }

    def start_search(self):
        if self.is_searching:
            QMessageBox.warning(self, "Поиск уже запущен", "Дождитесь завершения текущего поиска или остановите его.")
            return

        reply = QMessageBox.question(self, "Начать расследование?", "Это действие очистит текущие результаты и начнет новый поиск. Продолжить?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.No:
            return

        self.new_project()
        initial_params = self.get_search_params()
        
        if not any(initial_params.values()):
            QMessageBox.warning(self, "Внимание", "Введите хотя бы один параметр для поиска.")
            return

        for p_type, p_value in initial_params.items():
            if p_value:
                self.processed_entities.add(p_value)
                self.dynamic_search_queue.append({'type': p_type, 'value': p_value})
                self.graph_view.nodes[p_value] = {'type': 'initial', 'size': 25, 'is_initial': True}

        self.graph_view.update_graph()
        self.is_searching = True
        self.search_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.run_next_search_task()

    def run_next_search_task(self):
        if not self.dynamic_search_queue or not self.is_searching:
            self.search_finished()
            return
            
        entity = self.dynamic_search_queue.popleft()
        self.log(f"Запускаю поиск для сущности: {entity['type']} = {entity['value']}", color="#3498db")
        
        api_keys = self.get_api_keys()
        selected_sources = [name for name, cb in self.source_checkboxes.items() if cb.isChecked()]

        self.search_worker = DataSearchWorker(
            search_entity=entity,
            selected_sources=selected_sources,
            search_depth_index=self.search_depth_combo.currentIndex(),
            api_keys=api_keys
        )
        self.search_worker.found_data.connect(self.add_result)
        self.search_worker.new_entity_found.connect(self.handle_new_entity)
        self.search_worker.finished.connect(self.run_next_search_task)
        self.search_worker.start()

    def stop_search(self):
        self.is_searching = False
        if self.search_worker:
            self.search_worker.cancel()
        self.dynamic_search_queue.clear()
        self.stop_button.setEnabled(False)
        self.search_button.setEnabled(True)
        self.log("Поиск остановлен пользователем.", color="#c0392b")
        self.status_label.setText(f"Поиск остановлен. Найдено {self.results_table.rowCount()} записей.")
        self.progress_bar.setVisible(False)

    def search_finished(self):
        if not self.is_searching: return # Already stopped
        self.is_searching = False
        self.search_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Расследование завершено. Найдено {self.results_table.rowCount()} записей.")
        self.log("Расследование завершено.")

    def handle_new_entity(self, entity_type, entity_value):
        if self.dynamic_search_checkbox.isChecked() and entity_value not in self.processed_entities:
            self.processed_entities.add(entity_value)
            self.dynamic_search_queue.append({'type': entity_type, 'value': entity_value})
            self.log(f"Найдена новая сущность, добавлена в очередь: {entity_type} = {entity_value}", color="#2980b9")
    
    def add_result(self, data, source_entity, from_project=False):
        value = data['value']
        for row in range(self.results_table.rowCount()):
            if self.results_table.item(row, 4).text() == value and self.results_table.item(row, 2).text() == data['source']:
                return
        
        if not from_project:
            self.data_confidence[value] += 1
        
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        cb = QCheckBox()
        cb_widget = QWidget()
        cb_layout = QHBoxLayout(cb_widget)
        cb_layout.addWidget(cb)
        cb_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        self.results_table.setCellWidget(row, 0, cb_widget)
        cb.setChecked(True)

        confidence_item = QTableWidgetItem(str(self.data_confidence[value]))
        confidence_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_table.setItem(row, 1, confidence_item)
        
        status = data.get('status', 'found')
        items = {
            2: data.get('source', ''), 3: data.get('type', 'default').capitalize(),
            4: value, 5: data.get('context', ''), 6: status,
            7: datetime.fromisoformat(data['timestamp']).strftime("%d.%m.%Y %H:%M")
        }
        
        for col, text in items.items():
            item = QTableWidgetItem(str(text))
            item.setData(Qt.ItemDataRole.UserRole, data)
            if status == 'leaked': item.setBackground(QBrush(QColor("#e74c3c")))
            elif status == 'link': item.setForeground(QBrush(QColor("#3498db")))
            self.results_table.setItem(row, col, item)
        self.results_table.resizeRowToContents(row)

        if not from_project and source_entity:
            self.update_dashboard(data['type'], value)
            self.graph_view.add_relation(source_entity, data)

    def update_dashboard(self, data_type, value):
        target_list = None
        if data_type == 'email': target_list = self.email_list
        elif data_type == 'phone': target_list = self.phone_list
        elif data_type == 'username': target_list = self.username_list
        elif data_type == 'company': target_list = self.company_list

        if target_list and not target_list.findItems(value, Qt.MatchFlag.MatchExactly):
            target_list.addItem(value)
            
    def highlight_node_in_table(self, node_id):
        self.results_table.clearSelection()
        items = self.results_table.findItems(node_id, Qt.MatchFlag.MatchContains)
        for item in items:
            self.results_table.selectRow(item.row())
        if items:
            self.tabs.setCurrentIndex(1) # Index of Results tab

    def apply_filter(self):
        filter_text = self.filter_input.text().lower()
        for row in range(self.results_table.rowCount()):
            match_found = False
            if not filter_text:
                match_found = True
            else:
                for col in range(1, self.results_table.columnCount()):
                    item = self.results_table.item(row, col)
                    if item and item.text():
                        if filter_text in item.text().lower():
                            match_found = True
                            break
            self.results_table.setRowHidden(row, not match_found)

    def show_context_menu(self, position):
        menu = QMenu(self)
        if self.results_table.itemAt(position):
            open_url_action = QAction(QIcon.fromTheme("browser"), "Открыть ссылку в браузере", self)
            open_url_action.triggered.connect(self.open_selected_url)
            menu.addAction(open_url_action)
            show_details_action = QAction(QIcon.fromTheme("dialog-information"), "Показать детали", self)
            show_details_action.triggered.connect(self.show_selected_details)
            menu.addAction(show_details_action)
            menu.exec(self.results_table.viewport().mapToGlobal(position))

    def open_selected_url(self):
        if (row := self.results_table.currentRow()) >= 0:
            if item := self.results_table.item(row, 2):
                if (data := item.data(Qt.ItemDataRole.UserRole)) and 'url' in data:
                    QDesktopServices.openUrl(QUrl(data['url']))

    def show_selected_details(self):
        if (row := self.results_table.currentRow()) >= 0:
            if item := self.results_table.item(row, 2):
                data = item.data(Qt.ItemDataRole.UserRole)
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Детальная информация")
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setTextFormat(Qt.TextFormat.RichText)
                detail_text = (
                    f"<p><b>Источник:</b> {data.get('source', 'N/A')}<br>"
                    f"<b>URL:</b> <a href='{data.get('url', '')}'>{data.get('url', 'N/A')}</a><br>"
                    f"<b>Тип:</b> {data.get('type', 'N/A').capitalize()}<br>"
                    f"<b>Значение:</b> {data.get('value', 'N/A')}<br>"
                    f"<b>Статус:</b> {data.get('status', 'N/A')}<br>"
                    f"<b>Дата:</b> {datetime.fromisoformat(data.get('timestamp', '')).strftime('%d.%m.%Y %H:%M') if data.get('timestamp') else 'N/A'}</p>"
                )
                msg_box.setText(detail_text)
                msg_box.setInformativeText(data.get('full_text', 'Полный контекст отсутствует.'))
                msg_box.exec()
        
    def export_results(self):
        if self.results_table.rowCount() == 0:
            QMessageBox.information(self, "Информация", "Нет данных для экспорта.")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить результаты", "", "CSV (*.csv);;JSON (*.json);;Excel (*.xlsx)")
        if not file_path: return
        
        try:
            data = [self.results_table.item(row, 2).data(Qt.ItemDataRole.UserRole) for row in range(self.results_table.rowCount()) if self.results_table.cellWidget(row, 0).findChild(QCheckBox).isChecked() and not self.results_table.isRowHidden(row)]
            if not data:
                QMessageBox.warning(self, "Внимание", "Нет выбранных данных для экспорта.")
                return

            if file_path.endswith('.csv'):
                with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader(); writer.writerows(data)
            elif file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
            elif file_path.endswith('.xlsx'):
                try:
                    from openpyxl import Workbook
                    wb = Workbook()
                    ws = wb.active
                    headers = list(data[0].keys())
                    ws.append(headers)
                    for row in data: ws.append([str(row.get(h, '')) for h in headers])
                    wb.save(file_path)
                except ImportError:
                    QMessageBox.warning(self, "Ошибка", "Для экспорта в Excel установите openpyxl: pip install openpyxl")
                    return
            QMessageBox.information(self, "Успех", f"Данные сохранены в {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {e}")

    def save_settings(self):
        settings = QSettings("ASP", "ParserOmega")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("search_depth_index", self.search_depth_combo.currentIndex())
        settings.setValue("use_proxy", self.proxy_checkbox.isChecked())
        settings.setValue("dynamic_search", self.dynamic_search_checkbox.isChecked())
        settings.setValue("hibp_api_key", self.hibp_api_key_input.text())
        settings.setValue("google_api_key", self.google_api_key_input.text())
        settings.setValue("google_cx_id", self.google_cx_input.text())
        settings.setValue("yandex_api_key", self.yandex_key_input.text())
        settings.setValue("yandex_user_id", self.yandex_user_input.text())
        QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены.")

    def load_settings(self):
        settings = QSettings("ASP", "ParserOmega")
        if geometry := settings.value("geometry"): self.restoreGeometry(geometry)
        self.search_depth_combo.setCurrentIndex(settings.value("search_depth_index", 1, type=int))
        self.proxy_checkbox.setChecked(settings.value("use_proxy", True, type=bool))
        self.dynamic_search_checkbox.setChecked(settings.value("dynamic_search", True, type=bool))
        self.hibp_api_key_input.setText(settings.value("hibp_api_key", ""))
        self.google_api_key_input.setText(settings.value("google_api_key", ""))
        self.google_cx_input.setText(settings.value("google_cx_id", ""))
        self.yandex_key_input.setText(settings.value("yandex_api_key", ""))
        self.yandex_user_input.setText(settings.value("yandex_user_id", ""))
        self.log("Настройки загружены.")

    def log(self, message, color=None):
        log_message = f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n"
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
        if color: self.log_text.setTextColor(QColor(color))
        self.log_text.insertPlainText(log_message)
        self.log_text.setTextColor(QColor("#2c3e50")) # Reset to default
        logger.info(message)

    def show_about(self):
        QMessageBox.about(self, "О программе",
            """<h2>ASP Parser 5.0 (Omega Edition)</h2>
            <p>Профессиональная OSINT-платформа для поиска, анализа и визуализации общедоступных данных.</p>
            <p><b>Ключевые возможности версии "Омега":</b></p>
            <ul>
                <li><b>Система проектов:</b> Сохранение и загрузка полных сессий расследования.</li>
                <li><b>Интерактивный граф связей:</b> Визуализация найденных данных и их отношений.</li>
                <li><b>Динамический поиск:</b> Автоматическое использование найденных данных для дальнейшего расследования.</li>
                <li><b>Дашборд:</b> Сводная информация по ключевым найденным сущностям.</li>
                <li><b>Расширенные источники:</b> Включая Yandex API, бизнес-реестры, Telegram и др.</li>
            </ul>
            <p>Версия 5.1, 2025 г.</p>"""
        )

    def show_error(self, message):
        QMessageBox.critical(self, "Критическая ошибка", message)
        self.log(f"Критическая ошибка: {message}", color="#e74c3c")
        if self.is_searching:
            self.search_finished()

    def closeEvent(self, event):
        if self.is_searching:
            reply = QMessageBox.question(self, 'Подтверждение выхода', "Поиск еще выполняется. Вы уверены, что хотите выйти?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.stop_search()
                if self.search_worker:
                    self.search_worker.wait(2000)
                event.accept()
            else:
                event.ignore()
        else:
            self.save_settings()
            event.accept()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.critical(f"Необработанное исключение в main: {e}", exc_info=True)
        print(f"Критическая ошибка: {e}")
