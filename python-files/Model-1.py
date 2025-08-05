# %%
import json
import sys
import random
import math
import heapq
from typing import List, Dict, Optional, Union
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QGroupBox, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox,
                             QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QLabel, QTreeWidget, QTreeWidgetItem, QSplitter, QMessageBox, 
                             QListWidget, QDialog, QDialogButtonBox, QFileDialog, QProgressBar,
                             QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
                             QGraphicsTextItem, QGraphicsLineItem, QStyle, QGraphicsSimpleTextItem, 
                             QGraphicsPolygonItem, QLabel, QScrollArea)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRectF, QPointF, QLineF
from PyQt5.QtGui import QBrush, QPen, QColor, QFont, QPainter, QPolygonF, QPixmap, QIcon


def resource_path(relative_path):
    """ Получает абсолютный путь к ресурсу """
    try:
        # PyInstaller создает временную папку в _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# Функция для генерации нормально распределенной случайной величины
def normal_distribution(mean, std_dev):
    for _ in range(10000):  # Увеличено до 10000 попыток
        u = random.uniform(0, 1)
        v = random.uniform(0, 1)
        z = math.sqrt(-2.0 * math.log(u)) * math.cos(2.0 * math.pi * v)
        value = mean + std_dev * z
        if value > 0:  # Обеспечиваем положительное значение времени
            return value
    return 0.001  # Возвращаем минимальное значение после неудачных попыток

# Класс Типового Элемента Замены (ТЭЗ)
class TEZ:
    def __init__(self, n_nom: str, gabarits: str, cost: float, 
                 theta: float, sigma_theta: float, 
                 t_izg: float, sigma_t_izg: float):
        self.n_nom = n_nom          # Номенклатурный номер
        self.gabarits = gabarits    # Габаритные характеристики
        self.cost = cost            # Стоимость
        self.theta = theta          # МО наработки на отказ
        self.sigma_theta = sigma_theta  # СКО наработки на отказ
        self.t_izg = t_izg          # МО времени изготовления
        self.sigma_t_izg = sigma_t_izg  # СКО времени изготовления

    def time_to_failure(self) -> float:
        return normal_distribution(self.theta, self.sigma_theta)
    
    def production_time(self, n_pl_sv: int, n_opip: int) -> float:
        k_pl = min(1.0, n_pl_sv / 10.0)  # Упрощенный коэффициент эффективности ПЛ
        k_opip = min(1.0, n_opip / 5.0)   # Упрощенный коэффициент эффективности ОПИП
        base_time = normal_distribution(self.t_izg, self.sigma_t_izg)
        return base_time / (k_pl * k_opip)

# Класс Обслуживающего Персонала
class Personnel:
    def __init__(self, name: str, n_count: int):
        self.name = name            # Название группы персонала
        self.n_count = n_count      # Количество персонала
    
    def efficiency_coeff(self) -> float:
        return min(1.0, math.log(1 + self.n_count))  # Логарифмическая зависимость эффективности

# Класс Изделия
class Product:
    def __init__(self, name: str, tez_list: List[TEZ], personnel: Personnel, base: 'StorageBase'):
        self.name = name            # Название изделия
        self.tez_list = tez_list    # Список ТЭЗ в изделии
        self.personnel = personnel  # Обслуживающий персонал изделия
        self.base = base            # Привязанная база хранения
        self.state = "Р"            # Начальное состояние: Работоспособное
        self.failure_times = [tez.time_to_failure() for tez in self.tez_list]
        self.operational_time = 0.0  # Суммарное время работы
        self.downtime = 0.0          # Суммарное время простоя
        self.repair_costs = 0.0      # Стоимость восстановления
        self.last_event_time = 0.0   # Время последнего события
        self.failure_count = 0       # Счетчик отказов
        self.last_failure_time = 0.0 # Время последнего отказа
    
    def update_time(self, current_time: float):
        """Обновляет время работы/простоя до текущего момента"""
        if self.last_event_time < current_time:
            time_diff = current_time - self.last_event_time
            if self.state == "Р":
                self.operational_time += time_diff
            else:
                self.downtime += time_diff
            self.last_event_time = current_time
    
    def check_failure(self, current_time: float) -> Optional[TEZ]:
        """Проверяет, произошел ли отказ в текущее время"""
        self.update_time(current_time)
        
        if self.state == "Н":
            return None
            
        # Проверяем, наступил ли отказ любого ТЭЗа
        for i, fail_time in enumerate(self.failure_times):
            if current_time >= fail_time:
                self.state = "Н"
                self.failure_count += 1
                self.last_failure_time = current_time
                return self.tez_list[i]
        return None
    
    def restore(self, tez_to_replace: TEZ, current_time: float) -> float:
        """Выполняет восстановление изделия"""
        self.update_time(current_time)
        
        # Эффективность персонала
        k_eff = self.personnel.efficiency_coeff()
        
        # Время поиска неисправности
        t_search = normal_distribution(0.5, 0.1) / k_eff
        
        # Время формирования заявки
        t_request = normal_distribution(0.2, 0.05) / k_eff
        
        # Логирование создания заявки
        print(f"[{current_time + t_search:.2f} ч] ЗАЯВКА: Изделие {self.name} создало заявку на ТЭЗ {tez_to_replace.n_nom} на базе {self.base.name}")
        
        # Время замены ТЭЗ
        t_repair = normal_distribution(1.0, 0.2) / k_eff
        
        total_time = t_search + t_request + t_repair
        
        # Учитываем время восстановления как время простоя
        self.downtime += total_time
        self.last_event_time += total_time
        
        self.state = "Р"
        # Генерируем новое время отказа для замененного ТЭЗа
        idx = self.tez_list.index(tez_to_replace)
        self.failure_times[idx] = self.last_event_time + tez_to_replace.time_to_failure()
        return total_time
    
    def add_repair_cost(self, cost: float):
        """Добавляет стоимость ремонта к общим затратам изделия"""
        self.repair_costs += cost
    
    def get_availability(self, total_time: float) -> float:
        """Рассчитывает коэффициент готовности"""
        # Обновляем время до конца моделирования
        if self.last_event_time < total_time:
            time_diff = total_time - self.last_event_time
            if self.state == "Р":
                self.operational_time += time_diff
            else:
                self.downtime += time_diff
            self.last_event_time = total_time
        
        # Расчет коэффициента готовности
        if self.operational_time + self.downtime == 0:
            return 1.0
        
        return self.operational_time / (self.operational_time + self.downtime)

# Класс Базы Хранения
class StorageBase:
    def __init__(self, name: str, level: str, personnel: Personnel, 
                 tez_catalog: Optional[Dict[str, TEZ]] = None):
        self.name = name
        self.level = level
        self.personnel = personnel
        self.stock: Dict[str, int] = {}
        self.min_stock_levels: Dict[str, int] = {}
        self.max_stock_levels: Dict[str, int] = {}
        self.safety_stock_levels: Dict[str, int] = {}  # Неснижаемые уровни запаса
        self.replenish_strategies: Dict[str, str] = {}
        self.replenish_periods: Dict[str, float] = {}
        
        # Новые словари для хранения источников пополнения по типам ТЭЗ
        self.higher_bases: Dict[str, StorageBase] = {}  # Для каждого ТЭЗа - вышестоящая база
        self.sources: Dict[str, ReplenishmentSource] = {}  # Для каждого ТЭЗа - источник пополнения
        self.transports: Dict[str, Transport] = {}  # Для каждого ТЭЗа - транспорт
        self.distances: Dict[str, float] = {}  # Для каждого ТЭЗа - расстояние до источника
        
        self.tez_catalog = tez_catalog or {}
        self.operational_costs = 0.0
        self.requests_processed = 0
        self.last_replenishment = 0.0
    
    def set_stock_policy(self, tez_nom: str, min_stock: int, max_stock: int, 
                         strategy: str, period: Optional[float] = None,
                         safety_stock: Optional[int] = None):
        """Устанавливает политику управления запасами для ТЭЗа"""
        self.min_stock_levels[tez_nom] = min_stock
        self.max_stock_levels[tez_nom] = max_stock
        self.replenish_strategies[tez_nom] = strategy
        
        if period:
            self.replenish_periods[tez_nom] = period
            
        if safety_stock is not None:
            self.safety_stock_levels[tez_nom] = safety_stock
        else:
            # По умолчанию неснижаемый уровень равен минимальному
            self.safety_stock_levels[tez_nom] = min_stock
            
        self.stock[tez_nom] = max_stock
    
    def set_replenish_source(self, tez_nom: str, 
                            higher_base: Optional['StorageBase'] = None, 
                            source: Optional['ReplenishmentSource'] = None,
                            transport: Optional['Transport'] = None,
                            distance: float = 100.0):
        """Устанавливает источник пополнения для конкретного ТЭЗа"""
        if higher_base:
            self.higher_bases[tez_nom] = higher_base
        if source:
            self.sources[tez_nom] = source
        if transport:
            self.transports[tez_nom] = transport
        self.distances[tez_nom] = distance
    
    def check_replenishment(self, current_time: float) -> List[tuple]:
        """Проверяет необходимость пополнения запасов"""
        replenishments = []
        
        for tez_nom, strategy in self.replenish_strategies.items():
            current_stock = self.stock.get(tez_nom, 0)
            min_stock = self.min_stock_levels.get(tez_nom, 0)
            max_stock = self.max_stock_levels.get(tez_nom, 0)
            safety_stock = self.safety_stock_levels.get(tez_nom, min_stock)
            period = self.replenish_periods.get(tez_nom, 0)
            
            if strategy == "safety_stock" and current_stock < safety_stock:
                # Стратегия по неснижаемому запасу
                order_qty = max_stock - current_stock
                if order_qty > 0:
                    replenishments.append((tez_nom, order_qty))
            elif strategy == "continuous" and current_stock < min_stock:
                # Стратегия непрерывного пополнения
                order_qty = max_stock - current_stock
                if order_qty > 0:
                    replenishments.append((tez_nom, order_qty))
            elif strategy == "periodic" and current_time - self.last_replenishment >= period:
                # Периодическая стратегия
                order_qty = max_stock - current_stock
                if order_qty > 0:
                    replenishments.append((tez_nom, order_qty))
        
        return replenishments
    
    def process_replenishment(self, tez_nom: str, quantity: int, current_time: float) -> tuple:
        if quantity <= 0:
            return 0.0, 0.0
        
        # Получаем источник пополнения для этого ТЭЗа
        higher_base = self.higher_bases.get(tez_nom)
        source = self.sources.get(tez_nom)
        transport = self.transports.get(tez_nom)
        distance = self.distances.get(tez_nom, 100.0)
        
        if higher_base and transport:
            t_process, success, cost = higher_base.process_request(
                tez_nom, quantity, current_time
            )
            if success:
                t_delivery, transport_cost = transport.calculate_delivery_time(
                    distance, quantity
                )
                total_time = t_process + t_delivery
                total_cost = cost + transport_cost
                t_receive = self.receive_replenishment(tez_nom, quantity)
                total_time += t_receive
                self.stock[tez_nom] = self.stock.get(tez_nom, 0) + quantity
                self.operational_costs += total_cost
                return total_time, total_cost
            return 0.0, 0.0
        
        elif source and transport:
            tez_type = self.tez_catalog.get(tez_nom)
            if tez_type:
                t_production = source.process_request(tez_type, quantity)
                tez_cost = tez_type.cost * quantity
                t_delivery, transport_cost = transport.calculate_delivery_time(
                    distance, quantity
                )
                total_time = t_production + t_delivery
                total_cost = tez_cost + transport_cost
                t_receive = self.receive_replenishment(tez_nom, quantity)
                total_time += t_receive
                self.stock[tez_nom] = self.stock.get(tez_nom, 0) + quantity
                self.operational_costs += total_cost
                return total_time, total_cost
        
        return 0.0, 0.0
    
    def process_request(self, tez_nom: str, quantity: int, current_time: float) -> tuple:
        self.requests_processed += 1
        k_eff = self.personnel.efficiency_coeff()
        t_process = normal_distribution(0.3, 0.05) / k_eff
        
        # Логирование запроса
        print(f"[{current_time:.2f} ч] ОБРАБОТКА ЗАПРОСА: База {self.name} получила запрос на ТЭЗ {tez_nom}, количество: {quantity}")
        current_stock = self.stock.get(tez_nom, 0)
        print(f"    Текущий запас: {current_stock} шт, минимальный уровень: {self.min_stock_levels.get(tez_nom, 'N/A')}")
        
        if self.stock.get(tez_nom, 0) >= quantity:
            t_issue = normal_distribution(0.4, 0.1) / k_eff
            self.stock[tez_nom] -= quantity
            tez_cost = self.tez_catalog[tez_nom].cost * quantity
            self.operational_costs += tez_cost
            
            # Логирование успешной обработки
            print(f"    Запрос УДОВЛЕТВОРЕН: выдано {quantity} шт. ТЭЗ {tez_nom}")
            print(f"    Новый запас: {self.stock[tez_nom]} шт")
            
            min_stock = self.min_stock_levels.get(tez_nom, 0)
            if self.stock[tez_nom] < min_stock:
                max_stock = self.max_stock_levels.get(tez_nom, 0)
                order_qty = max_stock - self.stock[tez_nom]
                if order_qty > 0:
                    # Логирование инициации пополнения
                    print(f"    Запас ниже минимума! Инициировано пополнение: {order_qty} шт")
                    t_replenish, _ = self.process_replenishment(tez_nom, order_qty, current_time)
                    t_process += t_replenish
            return t_process + t_issue, True, tez_cost
        else:
            t_transfer = normal_distribution(0.2, 0.03) / k_eff
            
            # Логирование недостаточного запаса
            print(f"    Запас НЕДОСТАТОЧЕН! Требуется: {quantity} шт, доступно: {current_stock} шт")
            
            # Получаем источник для этого ТЭЗа
            higher_base = self.higher_bases.get(tez_nom)
            source = self.sources.get(tez_nom)
            transport = self.transports.get(tez_nom)
            distance = self.distances.get(tez_nom, 100.0)
            
            if higher_base and transport:
                t_higher, success, tez_cost = higher_base.process_request(
                    tez_nom, quantity, current_time
                )
                if not success:
                    return t_process + t_transfer + t_higher, False, 0.0
                t_delivery, transport_cost = transport.calculate_delivery_time(
                    distance, quantity
                )
                t_receive = self.receive_replenishment(tez_nom, quantity)
                t_issue = normal_distribution(0.4, 0.1) / k_eff
                self.stock[tez_nom] = self.stock.get(tez_nom, 0) + quantity
                self.stock[tez_nom] -= quantity
                total_time = t_process + t_transfer + t_higher + t_delivery + t_receive + t_issue
                total_cost = tez_cost + transport_cost
                self.operational_costs += transport_cost
                return total_time, True, total_cost
            elif source and transport:
                tez_type = self.tez_catalog.get(tez_nom)
                if not tez_type:
                    return t_process + t_transfer, False, 0.0
                t_production = source.process_request(tez_type, quantity)
                tez_cost = tez_type.cost * quantity
                t_delivery, transport_cost = transport.calculate_delivery_time(
                    distance, quantity
                )
                t_receive = self.receive_replenishment(tez_nom, quantity)
                t_issue = normal_distribution(0.4, 0.1) / k_eff
                self.stock[tez_nom] = self.stock.get(tez_nom, 0) + quantity
                self.stock[tez_nom] -= quantity
                total_time = t_process + t_transfer + t_production + t_delivery + t_receive + t_issue
                total_cost = tez_cost + transport_cost
                self.operational_costs += total_cost
                return total_time, True, total_cost
            else:
                return t_process + t_transfer, False, 0.0
    
    def receive_replenishment(self, tez_nom: str, quantity: int) -> float:
        k_eff = self.personnel.efficiency_coeff()
        return normal_distribution(0.5, 0.1) / k_eff

# Класс Транспорта
class Transport:
    def __init__(self, name: str, avg_speed: float, capacity: int, cost_per_km: float):
        self.name = name            # Название транспортной системы
        self.avg_speed = avg_speed  # Средняя скорость (км/ч)
        self.capacity = capacity    # Грузоподъемность (в единицах ТЭЗ)
        self.cost_per_km = cost_per_km  # Стоимость перевозки за км
        self.total_distance = 0.0   # Суммарное расстояние перевозок
        self.total_cost = 0.0       # Суммарная стоимость перевозок
    
    def calculate_delivery_time(self, distance: float, cargo_volume: int) -> tuple:
        """Рассчитывает время доставки и стоимость"""
        # Расчет времени доставки
        trips = math.ceil(cargo_volume / self.capacity)
        travel_time = (distance / self.avg_speed) * 2 * trips  # Учет обратного пути
        handling_time = trips * normal_distribution(0.5, 0.1)  # Время погрузки/разгрузки
        
        # Логирование транспортировки
        print(f"    ТРАНСПОРТИРОВКА: {self.name} начал доставку {cargo_volume} ед. груза")
        print(f"    Расстояние: {distance} км, количество рейсов: {trips}")
        print(f"    Ожидаемое время доставки: {travel_time + handling_time:.2f} ч")
        
        # Расчет стоимости перевозки
        total_distance = distance * 2 * trips
        transport_cost = total_distance * self.cost_per_km
        
        # Логирование завершения транспортировки
        print(f"    ТРАНСПОРТИРОВКА ЗАВЕРШЕНА: Доставлено {cargo_volume} ед. груза, стоимость: {transport_cost:.2f} руб")
        
        # Обновляем статистику
        self.total_distance += total_distance
        self.total_cost += transport_cost
        
        return travel_time + handling_time, transport_cost

# Класс Источника Пополнения
class ReplenishmentSource:
    def __init__(self, name: str, personnel: Personnel, production_lines: int, tez_types: List[str]):
        self.name = name                # Название источника
        self.personnel = personnel
        self.production_lines = production_lines
        self.tez_types = tez_types      # Список производимых ТЭЗ
        self.free_lines = production_lines
        self.operational_costs = 0.0    # Эксплуатационные расходы
        self.items_produced = 0         # Счетчик произведенных ТЭЗов
    
    def can_produce(self, tez_nom: str) -> bool:
        """Проверяет, может ли источник производить указанный ТЭЗ"""
        return tez_nom in self.tez_types
    
    def process_request(self, tez_type: TEZ, quantity: int) -> float:
        """Обрабатывает запрос на производство ТЭЗов"""
        # Проверяем, может ли источник производить этот ТЭЗ
        if not self.can_produce(tez_type.n_nom):
            raise ValueError(f"Источник {self.name} не может производить ТЭЗ {tez_type.n_nom}")
        
        # Время обработки заявки
        k_eff = self.personnel.efficiency_coeff()
        t_process = normal_distribution(0.4, 0.08) / k_eff
        
        # Время производства
        t_production = tez_type.production_time(self.production_lines, self.personnel.n_count) * quantity
        
        # Логирование производства
        print(f"    ПРОИЗВОДСТВО: Завод {self.name} начал изготовление {quantity} шт. ТЭЗ {tez_type.n_nom}")
        print(f"    Ожидаемое время производства: {t_production:.2f} ч")
        
        # Учет стоимости производства
        production_cost = tez_type.cost * quantity
        self.operational_costs += production_cost
        self.items_produced += quantity
        
        # Логирование завершения производства
        print(f"    ПРОИЗВОДСТВО ЗАВЕРШЕНО: Изготовлено {quantity} шт. ТЭЗ {tez_type.n_nom}, стоимость: {production_cost:.2f} руб")
        
        return t_process + t_production

# Класс потока для выполнения моделирования
class SimulationThread(QThread):
    update_progress = pyqtSignal(int)
    update_log = pyqtSignal(str)
    finished = pyqtSignal()
    paused = pyqtSignal()
    stopped = pyqtSignal()
    
    def __init__(self, gui):
        super().__init__()
        self.gui = gui
        self.running = True
        self.paused = False
        self.stopped = False
        
    def run(self):
        try:
            config = self.gui.create_configuration()
            products = config["products"]
            bases = config["bases"]
            sources = config["sources"]
            transports = config["transports"]
            replenishment_interval = config["replenishment_interval"]
            max_time = self.gui.sim_time_spin.value()
            
            # Инициализация событий
            events = []
            simulation_time = 0.0
            event_count = 0
            max_events = 1000000  # Максимальное количество событий
            
            self.update_log.emit(f"[{simulation_time:.2f} ч] НАЧАЛО МОДЕЛИРОВАНИЯ")
            
            # Планируем начальные события отказов
            for product in products:
                for i, tez in enumerate(product.tez_list):
                    failure_time = product.failure_times[i]
                    heapq.heappush(events, (failure_time, "failure", product, tez))
            
            # Планируем первую проверку пополнения
            next_replenish_check = replenishment_interval
            heapq.heappush(events, (next_replenish_check, "replenish_check", None, None))
            
            # Основной цикл моделирования
            while events and simulation_time < max_time and event_count < max_events and self.running:
                if self.stopped:
                    break
                    
                if self.paused:
                    self.paused.emit()
                    while self.paused and self.running:
                        self.msleep(100)
                    continue
                
                # Извлекаем ближайшее событие
                event_time, event_type, product, tez = heapq.heappop(events)
                simulation_time = event_time
                event_count += 1
                
                # Обновляем прогресс
                progress = min(100, int(simulation_time / max_time * 100))
                self.update_progress.emit(progress)
                
                # Обработка события
                if event_type == "failure":
                    # Обновляем состояние системы до времени события
                    for p in products:
                        p.update_time(simulation_time)
                    
                    # Обрабатываем отказ
                    failed_tez = product.check_failure(simulation_time)
                    if failed_tez:
                        self.update_log.emit(f"\n[{simulation_time:.2f} ч] ОТКАЗ: Изделие {product.name} из-за ТЭЗ {failed_tez.n_nom}")
                        
                        # Локализация неисправности и подготовка к замене
                        restore_time = product.restore(failed_tez, simulation_time)
                        
                        # Обработка заявки на привязанной базе
                        request_time, success, repair_cost = product.base.process_request(
                            failed_tez.n_nom, 1, simulation_time
                        )
                        
                        if success:
                            total_downtime = restore_time + request_time
                            recovery_time = simulation_time + total_downtime
                            
                            # Учет стоимости ремонта
                            product.add_repair_cost(repair_cost)
                            
                            # Планируем восстановление
                            heapq.heappush(events, (recovery_time, "restore", product, failed_tez))
                            
                            self.update_log.emit(f"    Восстановление запланировано на {recovery_time:.2f} ч")
                            self.update_log.emit(f"    Общее время простоя: {total_downtime:.2f} ч")
                        else:
                            self.update_log.emit("    ОШИБКА: Не удалось получить ТЭЗ для восстановления!")
                
                elif event_type == "restore":
                    # Обновляем состояние системы до времени события
                    for p in products:
                        p.update_time(simulation_time)
                    
                    # Восстанавливаем изделие
                    product.state = "Р"
                    self.update_log.emit(f"\n[{simulation_time:.2f} ч] ВОССТАНОВЛЕНИЕ: Изделие {product.name} работоспособно")
                    
                    # Планируем следующий отказ для этого ТЭЗа
                    idx = product.tez_list.index(tez)
                    new_failure_time = simulation_time + tez.time_to_failure()
                    product.failure_times[idx] = new_failure_time
                    heapq.heappush(events, (new_failure_time, "failure", product, tez))
                
                elif event_type == "replenish_check":
                    # Проверяем необходимость пополнения для всех баз
                    for base in bases:
                        replenishments = base.check_replenishment(simulation_time)
                        for tez_nom, quantity in replenishments:
                            # Пропускаем нулевые заказы
                            if quantity <= 0:
                                continue
                                
                            self.update_log.emit(f"\n[{simulation_time:.2f} ч] ПРОВЕРКА ПОПОЛНЕНИЯ: База {base.name}")
                            self.update_log.emit(f"    Требуется пополнение: ТЭЗ {tez_nom}, количество: {quantity}")
                            
                            # Информация об источнике
                            if base.higher_bases.get(tez_nom):
                                self.update_log.emit(f"    Источник: вышестоящая база {base.higher_bases[tez_nom].name}")
                            elif base.sources.get(tez_nom):
                                self.update_log.emit(f"    Источник: завод {base.sources[tez_nom].name}")
                            
                            t_replenish, cost = base.process_replenishment(tez_nom, quantity, simulation_time)
                            if t_replenish > 0:
                                self.update_log.emit(f"    Пополнение получено за {t_replenish:.2f} ч, стоимость: {cost:.2f} руб")
                                self.update_log.emit(f"[{simulation_time + t_replenish:.2f} ч] ПОПОЛНЕНИЕ: База {base.name} получила {quantity} шт. ТЭЗ {tez_nom}")
                                
                                # Информация о запасах после пополнения
                                new_stock = base.stock.get(tez_nom, 0)
                                self.update_log.emit(f"    Текущий запас ТЭЗ {tez_nom}: {new_stock} шт")
                            else:
                                self.update_log.emit("    Пополнение не удалось!")
                    
                    # Планируем следующую проверку
                    next_check = simulation_time + replenishment_interval
                    heapq.heappush(events, (next_check, "replenish_check", None, None))
                
                # Обработка событий GUI каждые 100 событий
                if event_count % 100 == 0:
                    QApplication.processEvents()
            
            if event_count >= max_events:
                self.update_log.emit(f"\n[ВНИМАНИЕ] Достигнуто максимальное количество событий: {max_events}")
            
            # Завершение моделирования
            self.update_log.emit(f"\n[{simulation_time:.2f} ч] ОКОНЧАНИЕ МОДЕЛИРОВАНИЯ")
            
            # Обновляем время для всех продуктов до окончания моделирования
            for product in products:
                product.get_availability(simulation_time)  # Принудительно обновляем время
            
            # Выводим итоговое состояние системы
            self.print_final_state(simulation_time, products, bases, sources, transports)
            
            self.finished.emit()
            
        except Exception as e:
            self.update_log.emit(f"\n[ОШИБКА] Произошла ошибка: {str(e)}")
            self.finished.emit()
    
    def print_final_state(self, time: float, products: List[Product], bases: List[StorageBase], 
                         sources: List[ReplenishmentSource], transports: List[Transport]):
        """Выводит итоговое состояние системы в текстовое поле"""
        self.update_log.emit("\n" + "="*50)
        self.update_log.emit(f"ИТОГОВОЕ СОСТОЯНИЕ СИСТЕМЫ (время: {time:.2f} ч)")
        self.update_log.emit("="*50)
        
        # Состояние изделий
        self.update_log.emit("\nСОСТОЯНИЕ ИЗДЕЛИЙ:")
        for product in products:
            state = "Работоспособно" if product.state == "Р" else "Неисправно"
            availability = product.get_availability(time)
            total_time = product.operational_time + product.downtime
            self.update_log.emit(f"  {product.name}:")
            self.update_log.emit(f"    Состояние: {state}")
            self.update_log.emit(f"    Коэффициент готовности: {availability:.4f}")
            self.update_log.emit(f"    Время работы: {product.operational_time:.2f} ч ({product.operational_time/time*100:.1f}%)")
            self.update_log.emit(f"    Время простоя: {product.downtime:.2f} ч ({product.downtime/time*100:.1f}%)")
            self.update_log.emit(f"    Отказов: {product.failure_count}")
            self.update_log.emit(f"    Затраты на восстановление: {product.repair_costs:.2f} руб")
            self.update_log.emit(f"    Общее время изделия: {total_time:.2f} ч (модельное время: {time:.2f} ч)")
        
        # Запасы на базах
        self.update_log.emit("\nЗАПАСЫ НА БАЗАХ:")
        for base in bases:
            self.update_log.emit(f"  {base.name} ({base.level}):")
            for n_nom, count in base.stock.items():
                min_stock = base.min_stock_levels.get(n_nom, "N/A")
                max_stock = base.max_stock_levels.get(n_nom, "N/A")
                safety_stock = base.safety_stock_levels.get(n_nom, "N/A")
                strategy = base.replenish_strategies.get(n_nom, "N/A")
                self.update_log.emit(f"    {n_nom}: {count} шт (min: {min_stock}, max: {max_stock}, неснижаемый: {safety_stock}, стратегия: {strategy})")
        
        # Статистика источников
        self.update_log.emit("\nИСТОЧНИКИ ПОПОЛНЕНИЯ:")
        for source in sources:
            self.update_log.emit(f"  {source.name}:")
            self.update_log.emit(f"    Произведено ТЭЗов: {source.items_produced} шт")
            self.update_log.emit(f"    Затраты на производство: {source.operational_costs:.2f} руб")
        
        # Статистика транспорта
        self.update_log.emit("\nТРАНСПОРТНЫЕ СИСТЕМЫ:")
        for transport in transports:
            self.update_log.emit(f"  {transport.name}:")
            self.update_log.emit(f"    Суммарное расстояние: {transport.total_distance:.2f} км")
            self.update_log.emit(f"    Затраты на перевозки: {transport.total_cost:.2f} руб")
        self.update_log.emit("="*50)

class SystemBlock(QGraphicsRectItem):
    """Графический элемент для представления компонента системы с встроенной подписью"""
    def __init__(self, name, x, y, width, height, color, parent=None):
        super().__init__(x, y, width, height, parent)
        self.name = name
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 2))
        self.setZValue(1)
        
        # Создаем текстовый элемент как часть блока
        self.text = QGraphicsTextItem(name, self)
        self.text.setDefaultTextColor(Qt.black)
        self.text.setFont(QFont("Arial", 8, QFont.Bold))
        
        # Центрируем текст внутри блока
        self.update_text_position()
        
        # Параметры для соединений
        self.inputs = []
        self.outputs = []
    
    def update_text_position(self):
        """Обновляет позицию текста при изменении размера блока"""
        text_rect = self.text.boundingRect()
        rect = self.rect()
        self.text.setPos(
            rect.x() + (rect.width() - text_rect.width()) / 2,
            rect.y() + (rect.height() - text_rect.height()) / 2
        )
    
    def setRect(self, rect):
        """Переопределяем установку прямоугольника для обновления текста"""
        super().setRect(rect)
        self.update_text_position()

class SystemConnection(QGraphicsLineItem):
    """Графический элемент для представления связи между компонентами со стрелкой"""
    def __init__(self, source, source_port, target, target_port, color=Qt.black, parent=None):
        # Создаем линию между центрами блоков
        line = QLineF(source_port, target_port)
        super().__init__(line, parent)
        self.source = source
        self.target = target
        
        # Устанавливаем цвет линии
        pen = QPen(color)
        pen.setWidth(2)
        self.setPen(pen)
        
        # Добавляем стрелку в конце линии
        self.add_arrow(line, color)
    
    def add_arrow(self, line, color):
        """Добавляет стрелку в конце линии"""
        arrow_size = 12
        
        # Рассчитываем угол линии
        angle = math.atan2(-line.dy(), line.dx())
        
        # Вычисляем точку начала стрелки (отступаем от конца)
        arrow_tip = line.p2()
        
        # Вычисляем точки стрелки
        arrow_p1 = arrow_tip - QPointF(
            math.cos(angle + math.pi/3) * arrow_size,
            math.sin(angle + math.pi/3) * arrow_size
        )
        
        arrow_p2 = arrow_tip - QPointF(
            math.cos(angle + math.pi - math.pi/3) * arrow_size,
            math.sin(angle + math.pi - math.pi/3) * arrow_size
        )
        
        # Создаем полигон для стрелки
        arrow_head = QGraphicsPolygonItem(
            QPolygonF([arrow_tip, arrow_p1, arrow_p2]), 
            self
        )
        arrow_head.setBrush(QBrush(color))
        arrow_head.setPen(QPen(color))

class SystemDiagram(QGraphicsView):
    """Виджет для отображения структурной схемы системы"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.blocks = {}
        self.connections = []
        
        # Настройки внешнего вида
        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        self.setSceneRect(0, 0, 1000, 800)  # Фиксированный размер сцены
    
    def clear_diagram(self):
        """Очищает схему"""
        self.scene.clear()
        self.blocks = {}
        self.connections = []
    
    def add_block(self, name, x, y, width=150, height=60, color=Qt.lightGray):
        """Добавляет блок на схему"""
        block = SystemBlock(name, x, y, width, height, color)
        self.scene.addItem(block)
        self.blocks[name] = block
        return block
    
    def add_connection(self, source_block, target_block, transport_name=""):
        """Добавляет связь между блоками"""
        # Рассчитываем точки соединения как центры блоков
        source_rect = source_block.rect()
        source_port = source_block.mapToScene(source_rect.center())
        
        target_rect = target_block.rect()
        target_port = target_block.mapToScene(target_rect.center())
        
        # Генерируем цвет для связи
        color = self.generate_color(transport_name) if transport_name else Qt.black
        
        # Создаем линию между точками
        connection = SystemConnection(
            source_block, source_port,
            target_block, target_port,
            color
        )
        self.scene.addItem(connection)
        self.connections.append(connection)
        return color
    
    def generate_color(self, transport_name):
        """Генерирует уникальный цвет для типа транспорта"""
        if not transport_name:
            return Qt.black
        
        # Используем хеш имени для генерации предсказуемого цвета
        h = hash(transport_name) % 360
        return QColor.fromHsv(h, 255, 255)

# Основной класс GUI
class TEZSystemGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Расчет системы обеспечения ЗИП")
        self.setGeometry(100, 100, 1200, 800)
        
        # Установка иконки
        icon_path = resource_path("ZIP.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        # Центральный виджет и компоновка
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Создаем вкладки
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Инициализируем структуры данных
        self.tez_types = {}
        self.personnel_groups = {}
        self.storage_bases = {}
        self.products = {}
        self.sources = {}
        self.transports = {}
        
        # Добавляем тестовые данные
        self.add_test_data()
        
        # Создаем вкладки
        self.create_tez_tab()
        self.create_personnel_tab()
        self.create_bases_tab()
        self.create_products_tab()
        self.create_sources_tab()
        self.create_transport_tab()
        self.create_simulation_tab()
        self.create_diagram_tab()

        # Кнопки управления
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить конфигурацию")
        self.load_button = QPushButton("Загрузить конфигурацию")
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)
        main_layout.addLayout(button_layout)
        
        # Связываем кнопки с функциями
        self.save_button.clicked.connect(self.save_configuration)
        self.load_button.clicked.connect(self.load_configuration)

        # Обновляем визуализацию
        self.update_structure_visualization()
    
    def add_test_data(self):
        # Тестовые ТЭЗ
        self.tez_types["A-123"] = {
            "n_nom": "A-123",
            "gabarits": "10x20x5",
            "cost": 1500,
            "theta": 500,
            "sigma_theta": 50,
            "t_izg": 20,
            "sigma_t_izg": 2
        }
        
        self.tez_types["B-456"] = {
            "n_nom": "B-456",
            "gabarits": "15x25x7",
            "cost": 2500,
            "theta": 800,
            "sigma_theta": 100,
            "t_izg": 30,
            "sigma_t_izg": 3
        }
        
        self.tez_types["C-789"] = {
            "n_nom": "C-789",
            "gabarits": "20x30x10",
            "cost": 3500,
            "theta": 1000,
            "sigma_theta": 150,
            "t_izg": 40,
            "sigma_t_izg": 4
        }
        
        # Тестовый персонал
        self.personnel_groups["ОПИ изделия"] = {"name": "ОПИ изделия", "n_count": 3}
        self.personnel_groups["ОПБХ нижней базы"] = {"name": "ОПБХ нижней базы", "n_count": 2}
        self.personnel_groups["ОПБХ средней базы"] = {"name": "ОПБХ средней базы", "n_count": 4}
        self.personnel_groups["ОПИП завода"] = {"name": "ОПИП завода", "n_count": 6}
        
        # Тестовые базы
        self.storage_bases["Нижняя база 1"] = {
            "name": "Нижняя база 1",
            "level": "lower",
            "personnel": "ОПБХ нижней базы",
            "policies": {
                "A-123": {"min": 5, "max": 20, "strategy": "safety_stock", "safety_stock": 8,
                         "higher_base": "Средняя база A", "source": "", 
                         "transport": "Грузовик", "distance": 50},
                "B-456": {"min": 3, "max": 10, "strategy": "safety_stock", "safety_stock": 5,
                         "higher_base": "", "source": "Завод-1", 
                         "transport": "Фура", "distance": 100}
            }
        }
        
        self.storage_bases["Нижняя база 2"] = {
            "name": "Нижняя база 2",
            "level": "lower",
            "personnel": "ОПБХ нижней базы",
            "policies": {
                "C-789": {"min": 4, "max": 15, "strategy": "safety_stock", "safety_stock": 6,
                         "higher_base": "Средняя база B", "source": "", 
                         "transport": "Микроавтобус", "distance": 70}
            }
        }
        
        self.storage_bases["Средняя база A"] = {
            "name": "Средняя база A",
            "level": "middle",
            "personnel": "ОПБХ средней базы",
            "policies": {
                "A-123": {"min": 10, "max": 30, "strategy": "safety_stock", "safety_stock": 15,
                         "higher_base": "", "source": "Завод-1", 
                         "transport": "Самолет", "distance": 1500}
            }
        }
        
        self.storage_bases["Средняя база B"] = {
            "name": "Средняя база B",
            "level": "middle",
            "personnel": "ОПБХ средней базы",
            "policies": {
                "C-789": {"min": 5, "max": 15, "strategy": "safety_stock", "safety_stock": 8,
                         "higher_base": "", "source": "Завод-2", 
                         "transport": "Самолет", "distance": 2000}
            }
        }
        
        # Тестовые изделия
        self.products["Изделие-1"] = {
            "name": "Изделие-1",
            "tez_list": ["A-123", "A-123", "B-456"],
            "personnel": "ОПИ изделия",
            "base": "Нижняя база 1"
        }
        
        self.products["Изделие-2"] = {
            "name": "Изделие-2",
            "tez_list": ["C-789", "C-789", "A-123"],
            "personnel": "ОПИ изделия",
            "base": "Нижняя база 2"
        }
        
        # Тестовые источники
        self.sources["Завод-1"] = {
            "name": "Завод-1",
            "personnel": "ОПИП завода",
            "production_lines": 3,
            "tez_types": ["A-123", "B-456"]
        }
        
        self.sources["Завод-2"] = {
            "name": "Завод-2",
            "personnel": "ОПИП завода",
            "production_lines": 2,
            "tez_types": ["C-789"]
        }
        
        # Тестовый транспорт
        self.transports["Грузовик"] = {
            "name": "Грузовик",
            "avg_speed": 60,
            "capacity": 10,
            "cost_per_km": 50
        }
        
        self.transports["Фура"] = {
            "name": "Фура",
            "avg_speed": 80,
            "capacity": 20,
            "cost_per_km": 70
        }
        
        self.transports["Микроавтобус"] = {
            "name": "Микроавтобус",
            "avg_speed": 70,
            "capacity": 5,
            "cost_per_km": 40
        }
        
        self.transports["Самолет"] = {
            "name": "Самолет",
            "avg_speed": 500,
            "capacity": 100,
            "cost_per_km": 200
        }
    
    def create_tez_tab(self):
        """Создает вкладку для настройки ТЭЗ"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для добавления ТЭЗ
        group = QGroupBox("Добавить/Редактировать ТЭЗ")
        form_layout = QFormLayout()
        
        self.tez_nom_edit = QLineEdit()
        self.tez_gabarits_edit = QLineEdit()
        self.tez_cost_spin = QDoubleSpinBox()
        self.tez_cost_spin.setRange(0, 100000)
        self.tez_cost_spin.setValue(1500)
        self.tez_theta_spin = QDoubleSpinBox()
        self.tez_theta_spin.setRange(0, 10000)
        self.tez_theta_spin.setValue(500)
        self.tez_sigma_theta_spin = QDoubleSpinBox()
        self.tez_sigma_theta_spin.setRange(0, 1000)
        self.tez_sigma_theta_spin.setValue(50)
        self.tez_t_izg_spin = QDoubleSpinBox()
        self.tez_t_izg_spin.setRange(0, 1000)
        self.tez_t_izg_spin.setValue(20)
        self.tez_sigma_t_izg_spin = QDoubleSpinBox()
        self.tez_sigma_t_izg_spin.setRange(0, 100)
        self.tez_sigma_t_izg_spin.setValue(2)
        
        form_layout.addRow("Номенклатурный номер:", self.tez_nom_edit)
        form_layout.addRow("Габаритные характеристики:", self.tez_gabarits_edit)
        form_layout.addRow("Стоимость:", self.tez_cost_spin)
        form_layout.addRow("МО наработки на отказ:", self.tez_theta_spin)
        form_layout.addRow("СКО наработки на отказ:", self.tez_sigma_theta_spin)
        form_layout.addRow("МО времени изготовления:", self.tez_t_izg_spin)
        form_layout.addRow("СКО времени изготовления:", self.tez_sigma_t_izg_spin)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.add_tez_button = QPushButton("Добавить")
        self.update_tez_button = QPushButton("Обновить")
        self.delete_tez_button = QPushButton("Удалить")
        
        button_layout.addWidget(self.add_tez_button)
        button_layout.addWidget(self.update_tez_button)
        button_layout.addWidget(self.delete_tez_button)
        
        form_layout.addRow(button_layout)
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # Таблица существующих ТЭЗ
        self.tez_table = QTableWidget()
        self.tez_table.setColumnCount(7)
        self.tez_table.setHorizontalHeaderLabels([
            "Номенк. номер", "Габариты", "Стоимость", 
            "МО наработки", "СКО наработки", 
            "МО изготовления", "СКО изготовления"
        ])
        self.tez_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.tez_table)
        
        # Связываем кнопки с функциями
        self.add_tez_button.clicked.connect(self.add_tez)
        self.update_tez_button.clicked.connect(self.update_tez)
        self.delete_tez_button.clicked.connect(self.delete_tez)
        self.tez_table.itemSelectionChanged.connect(self.tez_selection_changed)
        
        # Обновляем таблицу
        self.update_tez_table()
        
        self.tab_widget.addTab(tab, "ТЭЗ")
    
    def add_tez(self):
        """Добавляет новый ТЭЗ"""
        n_nom = self.tez_nom_edit.text().strip()
        if not n_nom:
            QMessageBox.warning(self, "Ошибка", "Введите номенклатурный номер")
            return
        
        tez_data = {
            "n_nom": n_nom,
            "gabarits": self.tez_gabarits_edit.text(),
            "cost": self.tez_cost_spin.value(),
            "theta": self.tez_theta_spin.value(),
            "sigma_theta": self.tez_sigma_theta_spin.value(),
            "t_izg": self.tez_t_izg_spin.value(),
            "sigma_t_izg": self.tez_sigma_t_izg_spin.value()
        }
        
        self.tez_types[n_nom] = tez_data
        self.update_tez_table()
        self.clear_tez_form()
        self.update_structure_visualization()
    
    def update_tez(self):
        """Обновляет существующий ТЭЗ"""
        selected_items = self.tez_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите ТЭЗ для обновления")
            return
        
        n_nom = selected_items[0].text()
        if n_nom not in self.tez_types:
            return
        
        tez_data = {
            "n_nom": n_nom,
            "gabarits": self.tez_gabarits_edit.text(),
            "cost": self.tez_cost_spin.value(),
            "theta": self.tez_theta_spin.value(),
            "sigma_theta": self.tez_sigma_theta_spin.value(),
            "t_izg": self.tez_t_izg_spin.value(),
            "sigma_t_izg": self.tez_sigma_t_izg_spin.value()
        }
        
        self.tez_types[n_nom] = tez_data
        self.update_tez_table()
        self.update_structure_visualization()
    
    def delete_tez(self):
        """Удаляет выбранный ТЭЗ"""
        selected_items = self.tez_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите ТЭЗ для удаления")
            return
        
        n_nom = selected_items[0].text()
        if n_nom in self.tez_types:
            del self.tez_types[n_nom]
        
        self.update_tez_table()
        self.clear_tez_form()
        self.update_structure_visualization()
    
    def tez_selection_changed(self):
        """Обновляет форму при выборе ТЭЗ в таблице"""
        selected_items = self.tez_table.selectedItems()
        if not selected_items:
            return
        
        n_nom = selected_items[0].text()
        if n_nom in self.tez_types:
            tez = self.tez_types[n_nom]
            self.tez_nom_edit.setText(tez["n_nom"])
            self.tez_gabarits_edit.setText(tez["gabarits"])
            self.tez_cost_spin.setValue(tez["cost"])
            self.tez_theta_spin.setValue(tez["theta"])
            self.tez_sigma_theta_spin.setValue(tez["sigma_theta"])
            self.tez_t_izg_spin.setValue(tez["t_izg"])
            self.tez_sigma_t_izg_spin.setValue(tez["sigma_t_izg"])
    
    def clear_tez_form(self):
        """Очищает форму ТЭЗ"""
        self.tez_nom_edit.clear()
        self.tez_gabarits_edit.clear()
        self.tez_cost_spin.setValue(1500)
        self.tez_theta_spin.setValue(500)
        self.tez_sigma_theta_spin.setValue(50)
        self.tez_t_izg_spin.setValue(20)
        self.tez_sigma_t_izg_spin.setValue(2)
    
    def update_tez_table(self):
        """Обновляет таблицу ТЭЗ"""
        self.tez_table.setRowCount(len(self.tez_types))
        
        for row, (n_nom, tez) in enumerate(self.tez_types.items()):
            self.tez_table.setItem(row, 0, QTableWidgetItem(tez["n_nom"]))
            self.tez_table.setItem(row, 1, QTableWidgetItem(tez["gabarits"]))
            self.tez_table.setItem(row, 2, QTableWidgetItem(str(tez["cost"])))
            self.tez_table.setItem(row, 3, QTableWidgetItem(str(tez["theta"])))
            self.tez_table.setItem(row, 4, QTableWidgetItem(str(tez["sigma_theta"])))
            self.tez_table.setItem(row, 5, QTableWidgetItem(str(tez["t_izg"])))
            self.tez_table.setItem(row, 6, QTableWidgetItem(str(tez["sigma_t_izg"])))
    
    def create_personnel_tab(self):
        """Создает вкладку для настройки персонала"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для добавления персонала
        group = QGroupBox("Добавить/Редактировать группу персонала")
        form_layout = QFormLayout()
        
        self.personnel_name_edit = QLineEdit()
        self.personnel_count_spin = QSpinBox()
        self.personnel_count_spin.setRange(1, 100)
        self.personnel_count_spin.setValue(3)
        
        form_layout.addRow("Название группы:", self.personnel_name_edit)
        form_layout.addRow("Количество персонала:", self.personnel_count_spin)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.add_personnel_button = QPushButton("Добавить")
        self.update_personnel_button = QPushButton("Обновить")
        self.delete_personnel_button = QPushButton("Удалить")
        
        button_layout.addWidget(self.add_personnel_button)
        button_layout.addWidget(self.update_personnel_button)
        button_layout.addWidget(self.delete_personnel_button)
        
        form_layout.addRow(button_layout)
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # Таблица существующих групп персонала
        self.personnel_table = QTableWidget()
        self.personnel_table.setColumnCount(2)
        self.personnel_table.setHorizontalHeaderLabels(["Название группы", "Количество"])
        self.personnel_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.personnel_table)
        
        # Связываем кнопки с функциями
        self.add_personnel_button.clicked.connect(self.add_personnel)
        self.update_personnel_button.clicked.connect(self.update_personnel)
        self.delete_personnel_button.clicked.connect(self.delete_personnel)
        self.personnel_table.itemSelectionChanged.connect(self.personnel_selection_changed)
        
        # Обновляем таблицу
        self.update_personnel_table()
        
        self.tab_widget.addTab(tab, "Персонал")
    
    def add_personnel(self):
        """Добавляет новую группу персонала"""
        name = self.personnel_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название группы")
            return
        
        personnel_data = {
            "name": name,
            "n_count": self.personnel_count_spin.value()
        }
        
        self.personnel_groups[name] = personnel_data
        self.update_personnel_table()
        self.clear_personnel_form()
        self.update_structure_visualization()
    
    def update_personnel(self):
        """Обновляет существующую группу персонала"""
        selected_items = self.personnel_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите группу для обновления")
            return
        
        name = selected_items[0].text()
        if name not in self.personnel_groups:
            return
        
        personnel_data = {
            "name": name,
            "n_count": self.personnel_count_spin.value()
        }
        
        self.personnel_groups[name] = personnel_data
        self.update_personnel_table()
        self.update_structure_visualization()
    
    def delete_personnel(self):
        """Удаляет выбранную группу персонала"""
        selected_items = self.personnel_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите группу для удаления")
            return
        
        name = selected_items[0].text()
        if name in self.personnel_groups:
            del self.personnel_groups[name]
        
        self.update_personnel_table()
        self.clear_personnel_form()
        self.update_structure_visualization()
    
    def personnel_selection_changed(self):
        """Обновляет форму при выборе группы персонала в таблице"""
        selected_items = self.personnel_table.selectedItems()
        if not selected_items:
            return
        
        name = selected_items[0].text()
        if name in self.personnel_groups:
            personnel = self.personnel_groups[name]
            self.personnel_name_edit.setText(personnel["name"])
            self.personnel_count_spin.setValue(personnel["n_count"])
    
    def clear_personnel_form(self):
        """Очищает форму персонала"""
        self.personnel_name_edit.clear()
        self.personnel_count_spin.setValue(3)
    
    def update_personnel_table(self):
        """Обновляет таблицу персонала"""
        self.personnel_table.setRowCount(len(self.personnel_groups))
        
        for row, (name, personnel) in enumerate(self.personnel_groups.items()):
            self.personnel_table.setItem(row, 0, QTableWidgetItem(personnel["name"]))
            self.personnel_table.setItem(row, 1, QTableWidgetItem(str(personnel["n_count"])))
    
    def create_bases_tab(self):
        """Создает вкладку для настройки баз хранения с политиками пополнения"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для добавления базы
        group = QGroupBox("Добавить/Редактировать базу хранения")
        form_layout = QFormLayout()
        
        self.base_name_edit = QLineEdit()
        self.base_level_combo = QComboBox()
        self.base_level_combo.addItems(["lower", "middle"])
        self.base_personnel_combo = QComboBox()
        
        form_layout.addRow("Название базы:", self.base_name_edit)
        form_layout.addRow("Уровень:", self.base_level_combo)
        form_layout.addRow("Персонал:", self.base_personnel_combo)
        
        # Группа для политик управления запасами
        policies_group = QGroupBox("Политики управления запасами")
        policies_layout = QVBoxLayout()
        
        self.policies_table = QTableWidget()
        self.policies_table.setColumnCount(9)  # Увеличено количество колонок
        self.policies_table.setHorizontalHeaderLabels([
            "ТЭЗ", "Min", "Max", "Стратегия", "Период", "Неснижаемый уровень",
            "Источник пополнения", "Транспорт", "Расстояние (км)"
        ])
        self.policies_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        policies_layout.addWidget(self.policies_table)
        
        # Кнопки для управления политиками
        policies_buttons_layout = QHBoxLayout()
        self.add_policy_button = QPushButton("Добавить политику")
        self.edit_policy_button = QPushButton("Изменить")
        self.delete_policy_button = QPushButton("Удалить")
        
        policies_buttons_layout.addWidget(self.add_policy_button)
        policies_buttons_layout.addWidget(self.edit_policy_button)
        policies_buttons_layout.addWidget(self.delete_policy_button)
        
        policies_layout.addLayout(policies_buttons_layout)
        policies_group.setLayout(policies_layout)
        form_layout.addRow(policies_group)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.add_base_button = QPushButton("Добавить")
        self.update_base_button = QPushButton("Обновить")
        self.delete_base_button = QPushButton("Удалить")
        
        button_layout.addWidget(self.add_base_button)
        button_layout.addWidget(self.update_base_button)
        button_layout.addWidget(self.delete_base_button)
        
        form_layout.addRow(button_layout)
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # Таблица существующих баз
        self.base_table = QTableWidget()
        self.base_table.setColumnCount(3)
        self.base_table.setHorizontalHeaderLabels(["Название", "Уровень", "Персонал"])
        self.base_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.base_table)
        
        # Связываем кнопки с функциями
        self.add_base_button.clicked.connect(self.add_base)
        self.update_base_button.clicked.connect(self.update_base)
        self.delete_base_button.clicked.connect(self.delete_base)
        self.base_table.itemSelectionChanged.connect(self.base_selection_changed)
        self.add_policy_button.clicked.connect(self.add_policy)
        self.edit_policy_button.clicked.connect(self.edit_policy)
        self.delete_policy_button.clicked.connect(self.delete_policy)
        
        # Обновляем комбобоксы
        self.update_personnel_combo()
        self.update_base_combo()
        self.update_source_combo()
        self.update_transport_combo()
        
        # Обновляем таблицы
        self.update_base_table()
        
        self.tab_widget.addTab(tab, "Базы хранения")
    
    def update_personnel_combo(self):
        """Обновляет комбобокс персонала"""
        self.base_personnel_combo.clear()
        for name in self.personnel_groups:
            self.base_personnel_combo.addItem(name)
    
    def update_base_combo(self):
        """Обновляет комбобокс баз"""
        self.base_higher_combo = QComboBox()
        self.base_higher_combo.addItem("")  # Пустой элемент
        for name in self.storage_bases:
            self.base_higher_combo.addItem(name)
    
    def update_source_combo(self):
        """Обновляет комбобокс источников"""
        self.base_source_combo = QComboBox()
        self.base_source_combo.addItem("")  # Пустой элемент
        for name in self.sources:
            self.base_source_combo.addItem(name)
    
    def update_transport_combo(self):
        """Обновляет комбобоксы транспорта"""
        self.base_transport_combo = QComboBox()
        self.base_transport_combo.addItem("")  # Пустой элемент
        for name in self.transports:
            self.base_transport_combo.addItem(name)
    
    def add_policy(self):
        """Добавляет новую политику управления запасами"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Добавить политику управления запасами")
        layout = QFormLayout(dialog)
        
        # Выбор ТЭЗ
        tez_combo = QComboBox()
        tez_combo.addItems(list(self.tez_types.keys()))
        
        # Параметры запасов
        min_spin = QSpinBox()
        min_spin.setRange(0, 1000)
        min_spin.setValue(5)
        
        max_spin = QSpinBox()
        max_spin.setRange(1, 10000)
        max_spin.setValue(20)
        
        # Стратегия пополнения
        strategy_combo = QComboBox()
        strategy_combo.addItems(["continuous", "periodic", "safety_stock"])  # Добавлена новая стратегия
        
        # Период пополнения (только для периодической стратегии)
        period_spin = QDoubleSpinBox()
        period_spin.setRange(1, 1000)
        period_spin.setValue(24)
        period_spin.setEnabled(False)  # По умолчанию выключен
        
        # Неснижаемый уровень (только для стратегии safety_stock)
        safety_stock_spin = QSpinBox()
        safety_stock_spin.setRange(0, 1000)
        safety_stock_spin.setValue(8)
        safety_stock_spin.setEnabled(False)  # По умолчанию выключен
        
        # Источники пополнения
        source_type_combo = QComboBox()
        source_type_combo.addItems(["Вышестоящая база", "Источник"])
        
        higher_base_combo = QComboBox()
        higher_base_combo.addItem("")
        for name in self.storage_bases:
            higher_base_combo.addItem(name)
        
        source_combo = QComboBox()
        source_combo.addItem("")
        for name in self.sources:
            source_combo.addItem(name)
        
        transport_combo = QComboBox()
        transport_combo.addItem("")
        for name in self.transports:
            transport_combo.addItem(name)
        
        distance_spin = QDoubleSpinBox()
        distance_spin.setRange(0, 10000)
        distance_spin.setValue(100)
        
        def on_strategy_changed(index):
            """Активирует поле периода только для периодической стратегии и неснижаемый уровень для safety_stock"""
            strategy = strategy_combo.currentText()
            period_spin.setEnabled(strategy == "periodic")
            safety_stock_spin.setEnabled(strategy == "safety_stock")
        
        def on_source_type_changed(index):
            """Переключает между базой и источником"""
            if source_type_combo.currentText() == "Вышестоящая база":
                higher_base_combo.setEnabled(True)
                source_combo.setEnabled(False)
            else:
                higher_base_combo.setEnabled(False)
                source_combo.setEnabled(True)
        
        strategy_combo.currentIndexChanged.connect(on_strategy_changed)
        source_type_combo.currentIndexChanged.connect(on_source_type_changed)
        
        # Начальное состояние
        higher_base_combo.setEnabled(False)
        source_combo.setEnabled(False)
        
        layout.addRow("ТЭЗ:", tez_combo)
        layout.addRow("Минимальный запас:", min_spin)
        layout.addRow("Максимальный запас:", max_spin)
        layout.addRow("Стратегия пополнения:", strategy_combo)
        layout.addRow("Период пополнения (ч):", period_spin)
        layout.addRow("Неснижаемый уровень:", safety_stock_spin)  # Новое поле
        layout.addRow("Тип источника пополнения:", source_type_combo)
        layout.addRow("Вышестоящая база:", higher_base_combo)
        layout.addRow("Источник:", source_combo)
        layout.addRow("Транспорт:", transport_combo)
        layout.addRow("Расстояние (км):", distance_spin)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            tez_nom = tez_combo.currentText()
            min_stock = min_spin.value()
            max_stock = max_spin.value()
            strategy = strategy_combo.currentText()
            period = period_spin.value() if strategy == "periodic" else None
            safety_stock = safety_stock_spin.value() if strategy == "safety_stock" else None
            
            # Определяем источник пополнения
            source_type = source_type_combo.currentText()
            higher_base = higher_base_combo.currentText() if source_type == "Вышестоящая база" else ""
            source = source_combo.currentText() if source_type == "Источник" else ""
            transport = transport_combo.currentText()
            distance = distance_spin.value()
            
            # Добавляем в таблицу
            row = self.policies_table.rowCount()
            self.policies_table.insertRow(row)
            self.policies_table.setItem(row, 0, QTableWidgetItem(tez_nom))
            self.policies_table.setItem(row, 1, QTableWidgetItem(str(min_stock)))
            self.policies_table.setItem(row, 2, QTableWidgetItem(str(max_stock)))
            self.policies_table.setItem(row, 3, QTableWidgetItem(strategy))
            self.policies_table.setItem(row, 4, QTableWidgetItem(str(period) if period else ""))
            self.policies_table.setItem(row, 5, QTableWidgetItem(str(safety_stock) if safety_stock is not None else ""))
            self.policies_table.setItem(row, 6, QTableWidgetItem(f"{higher_base} {source}"))
            self.policies_table.setItem(row, 7, QTableWidgetItem(transport))
            self.policies_table.setItem(row, 8, QTableWidgetItem(str(distance)))
    
    def edit_policy(self):
        """Редактирует выбранную политику"""
        selected_row = self.policies_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите политику для редактирования")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Редактировать политику")
        layout = QFormLayout(dialog)
        
        # Текущие значения
        tez_nom = self.policies_table.item(selected_row, 0).text()
        min_stock = int(self.policies_table.item(selected_row, 1).text())
        max_stock = int(self.policies_table.item(selected_row, 2).text())
        strategy = self.policies_table.item(selected_row, 3).text()
        period_item = self.policies_table.item(selected_row, 4)
        period = float(period_item.text()) if period_item and period_item.text() else None
        
        safety_stock_item = self.policies_table.item(selected_row, 5)
        safety_stock = int(safety_stock_item.text()) if safety_stock_item and safety_stock_item.text() else None
        
        # Источник пополнения
        source_text = self.policies_table.item(selected_row, 6).text().split()
        higher_base = source_text[0] if len(source_text) > 0 else ""
        source = source_text[1] if len(source_text) > 1 else ""
        
        transport = self.policies_table.item(selected_row, 7).text()
        distance = float(self.policies_table.item(selected_row, 8).text())
        
        # Определяем тип источника
        if higher_base:
            source_type = "Вышестоящая база"
        else:
            source_type = "Источник"
        
        # Виджеты с текущими значениями
        tez_label = QLabel(tez_nom)
        min_spin = QSpinBox()
        min_spin.setRange(0, 1000)
        min_spin.setValue(min_stock)
        
        max_spin = QSpinBox()
        max_spin.setRange(1, 10000)
        max_spin.setValue(max_stock)
        
        strategy_combo = QComboBox()
        strategy_combo.addItems(["continuous", "periodic", "safety_stock"])  # Добавлена новая стратегия
        strategy_combo.setCurrentText(strategy)
        
        period_spin = QDoubleSpinBox()
        period_spin.setRange(1, 1000)
        period_spin.setValue(period if period else 24)
        period_spin.setEnabled(strategy == "periodic")
        
        safety_stock_spin = QSpinBox()
        safety_stock_spin.setRange(0, 1000)
        safety_stock_spin.setValue(safety_stock if safety_stock is not None else min_stock)
        safety_stock_spin.setEnabled(strategy == "safety_stock")
        
        # Источники пополнения
        source_type_combo = QComboBox()
        source_type_combo.addItems(["Вышестоящая база", "Источник"])
        source_type_combo.setCurrentText(source_type)
        
        higher_base_combo = QComboBox()
        higher_base_combo.addItem("")
        for name in self.storage_bases:
            higher_base_combo.addItem(name)
        higher_base_combo.setCurrentText(higher_base)
        
        source_combo = QComboBox()
        source_combo.addItem("")
        for name in self.sources:
            source_combo.addItem(name)
        source_combo.setCurrentText(source)
        
        transport_combo = QComboBox()
        transport_combo.addItem("")
        for name in self.transports:
            transport_combo.addItem(name)
        transport_combo.setCurrentText(transport)
        
        distance_spin = QDoubleSpinBox()
        distance_spin.setRange(0, 10000)
        distance_spin.setValue(distance)
        
        def on_strategy_changed(index):
            """Активирует нужные поля в зависимости от стратегии"""
            strategy = strategy_combo.currentText()
            period_spin.setEnabled(strategy == "periodic")
            safety_stock_spin.setEnabled(strategy == "safety_stock")
        
        def on_source_type_changed(index):
            """Переключает между базой и источником"""
            if source_type_combo.currentText() == "Вышестоящая база":
                higher_base_combo.setEnabled(True)
                source_combo.setEnabled(False)
            else:
                higher_base_combo.setEnabled(False)
                source_combo.setEnabled(True)
        
        strategy_combo.currentIndexChanged.connect(on_strategy_changed)
        source_type_combo.currentIndexChanged.connect(on_source_type_changed)
        
        # Начальное состояние
        if source_type == "Вышестоящая база":
            higher_base_combo.setEnabled(True)
            source_combo.setEnabled(False)
        else:
            higher_base_combo.setEnabled(False)
            source_combo.setEnabled(True)
        
        layout.addRow("ТЭЗ:", tez_label)
        layout.addRow("Минимальный запас:", min_spin)
        layout.addRow("Максимальный запас:", max_spin)
        layout.addRow("Стратегия пополнения:", strategy_combo)
        layout.addRow("Период пополнения (ч):", period_spin)
        layout.addRow("Неснижаемый уровень:", safety_stock_spin)  # Новое поле
        layout.addRow("Тип источника пополнения:", source_type_combo)
        layout.addRow("Вышестоящая база:", higher_base_combo)
        layout.addRow("Источник:", source_combo)
        layout.addRow("Транспорт:", transport_combo)
        layout.addRow("Расстояние (км):", distance_spin)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            min_stock = min_spin.value()
            max_stock = max_spin.value()
            strategy = strategy_combo.currentText()
            period = period_spin.value() if strategy == "periodic" else None
            safety_stock = safety_stock_spin.value() if strategy == "safety_stock" else None
            
            # Определяем источник пополнения
            source_type = source_type_combo.currentText()
            higher_base = higher_base_combo.currentText() if source_type == "Вышестоящая база" else ""
            source = source_combo.currentText() if source_type == "Источник" else ""
            transport = transport_combo.currentText()
            distance = distance_spin.value()
            
            # Обновляем таблицу
            self.policies_table.setItem(selected_row, 1, QTableWidgetItem(str(min_stock)))
            self.policies_table.setItem(selected_row, 2, QTableWidgetItem(str(max_stock)))
            self.policies_table.setItem(selected_row, 3, QTableWidgetItem(strategy))
            self.policies_table.setItem(selected_row, 4, QTableWidgetItem(str(period) if period else ""))
            self.policies_table.setItem(selected_row, 5, QTableWidgetItem(str(safety_stock) if safety_stock is not None else ""))
            self.policies_table.setItem(selected_row, 6, QTableWidgetItem(f"{higher_base} {source}"))
            self.policies_table.setItem(selected_row, 7, QTableWidgetItem(transport))
            self.policies_table.setItem(selected_row, 8, QTableWidgetItem(str(distance)))
    
    def delete_policy(self):
        """Удаляет выбранную политику"""
        selected_row = self.policies_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Ошибка", "Выберите политику для удаления")
            return
        
        self.policies_table.removeRow(selected_row)
    
    def add_base(self):
        """Добавляет новую базу хранения с политиками"""
        name = self.base_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название базы")
            return
        
        # Собираем политики из таблицы
        policies = {}
        for row in range(self.policies_table.rowCount()):
            tez_nom = self.policies_table.item(row, 0).text()
            min_stock = int(self.policies_table.item(row, 1).text())
            max_stock = int(self.policies_table.item(row, 2).text())
            strategy = self.policies_table.item(row, 3).text()
            period_item = self.policies_table.item(row, 4)
            period = float(period_item.text()) if period_item and period_item.text() else None
            
            safety_stock_item = self.policies_table.item(row, 5)
            safety_stock = int(safety_stock_item.text()) if safety_stock_item and safety_stock_item.text() else None
            
            # Источник пополнения
            source_text = self.policies_table.item(row, 6).text().split()
            higher_base = source_text[0] if len(source_text) > 0 else ""
            source = source_text[1] if len(source_text) > 1 else ""
            
            transport = self.policies_table.item(row, 7).text()
            distance = float(self.policies_table.item(row, 8).text())
            
            policies[tez_nom] = {
                "min": min_stock,
                "max": max_stock,
                "strategy": strategy,
                "period": period,
                "safety_stock": safety_stock,
                "higher_base": higher_base,
                "source": source,
                "transport": transport,
                "distance": distance
            }
        
        base_data = {
            "name": name,
            "level": self.base_level_combo.currentText(),
            "personnel": self.base_personnel_combo.currentText(),
            "policies": policies
        }
        
        self.storage_bases[name] = base_data
        self.update_base_table()
        self.clear_base_form()
        self.update_base_combo()
        self.update_structure_visualization()
    
    def update_base(self):
        """Обновляет существующую базу хранения с политиками"""
        selected_items = self.base_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите базу для обновления")
            return
        
        name = selected_items[0].text()
        if name not in self.storage_bases:
            return
        
        # Собираем политики из таблицы
        policies = {}
        for row in range(self.policies_table.rowCount()):
            tez_nom = self.policies_table.item(row, 0).text()
            min_stock = int(self.policies_table.item(row, 1).text())
            max_stock = int(self.policies_table.item(row, 2).text())
            strategy = self.policies_table.item(row, 3).text()
            period_item = self.policies_table.item(row, 4)
            period = float(period_item.text()) if period_item and period_item.text() else None
            
            safety_stock_item = self.policies_table.item(row, 5)
            safety_stock = int(safety_stock_item.text()) if safety_stock_item and safety_stock_item.text() else None
            
            # Источник пополнения
            source_text = self.policies_table.item(row, 6).text().split()
            higher_base = source_text[0] if len(source_text) > 0 else ""
            source = source_text[1] if len(source_text) > 1 else ""
            
            transport = self.policies_table.item(row, 7).text()
            distance = float(self.policies_table.item(row, 8).text())
            
            policies[tez_nom] = {
                "min": min_stock,
                "max": max_stock,
                "strategy": strategy,
                "period": period,
                "safety_stock": safety_stock,
                "higher_base": higher_base,
                "source": source,
                "transport": transport,
                "distance": distance
            }
        
        base_data = {
            "name": name,
            "level": self.base_level_combo.currentText(),
            "personnel": self.base_personnel_combo.currentText(),
            "policies": policies
        }
        
        self.storage_bases[name] = base_data
        self.update_base_table()
        self.update_base_combo()
        self.update_structure_visualization()
    
    def delete_base(self):
        """Удаляет выбранную базу хранения"""
        selected_items = self.base_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите базу для удаления")
            return
        
        name = selected_items[0].text()
        if name in self.storage_bases:
            del self.storage_bases[name]
        
        self.update_base_table()
        self.clear_base_form()
        self.update_base_combo()
        self.update_structure_visualization()
    
    def base_selection_changed(self):
        """Обновляет форму при выборе базы в таблице"""
        selected_items = self.base_table.selectedItems()
        if not selected_items:
            return
        
        name = selected_items[0].text()
        if name in self.storage_bases:
            base = self.storage_bases[name]
            self.base_name_edit.setText(base["name"])
            self.base_level_combo.setCurrentText(base["level"])
            self.base_personnel_combo.setCurrentText(base["personnel"])
            
            # Загружаем политики для выбранной базы
            self.policies_table.setRowCount(0)
            if "policies" in base:
                for tez_nom, policy in base["policies"].items():
                    row = self.policies_table.rowCount()
                    self.policies_table.insertRow(row)
                    self.policies_table.setItem(row, 0, QTableWidgetItem(tez_nom))
                    self.policies_table.setItem(row, 1, QTableWidgetItem(str(policy["min"])))
                    self.policies_table.setItem(row, 2, QTableWidgetItem(str(policy["max"])))
                    self.policies_table.setItem(row, 3, QTableWidgetItem(policy["strategy"]))
                    period = policy.get("period", "")
                    self.policies_table.setItem(row, 4, QTableWidgetItem(str(period) if period else ""))
                    
                    safety_stock = policy.get("safety_stock", "")
                    self.policies_table.setItem(row, 5, QTableWidgetItem(str(safety_stock) if safety_stock is not None else ""))
                    
                    # Источник пополнения
                    source_text = f"{policy.get('higher_base', '')} {policy.get('source', '')}"
                    self.policies_table.setItem(row, 6, QTableWidgetItem(source_text.strip()))
                    
                    self.policies_table.setItem(row, 7, QTableWidgetItem(policy.get("transport", "")))
                    self.policies_table.setItem(row, 8, QTableWidgetItem(str(policy.get("distance", 0))))
    
    def clear_base_form(self):
        """Очищает форму базы"""
        self.base_name_edit.clear()
        self.base_level_combo.setCurrentIndex(0)
        self.base_personnel_combo.setCurrentIndex(0)
        self.policies_table.setRowCount(0)
    
    def update_base_table(self):
        """Обновляет таблицу баз"""
        self.base_table.setRowCount(len(self.storage_bases))
        
        for row, (name, base) in enumerate(self.storage_bases.items()):
            self.base_table.setItem(row, 0, QTableWidgetItem(base["name"]))
            self.base_table.setItem(row, 1, QTableWidgetItem(base["level"]))
            self.base_table.setItem(row, 2, QTableWidgetItem(base["personnel"]))
    
    def create_products_tab(self):
        """Создает вкладку для настройки изделий"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для добавления изделия
        group = QGroupBox("Добавить/Редактировать изделие")
        form_layout = QFormLayout()
        
        self.product_name_edit = QLineEdit()
        self.product_personnel_combo = QComboBox()
        self.product_base_combo = QComboBox()
        
        # Виджет для выбора ТЭЗ
        tez_selection_layout = QHBoxLayout()
        
        self.available_tez_list = QListWidget()
        self.available_tez_list.setSelectionMode(QListWidget.MultiSelection)
        self.selected_tez_list = QListWidget()
        self.selected_tez_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Кнопки управления выбором ТЭЗ
        tez_buttons_layout = QVBoxLayout()
        self.add_tez_button = QPushButton(">")
        self.remove_tez_button = QPushButton("<")
        self.add_all_tez_button = QPushButton(">>")
        self.remove_all_tez_button = QPushButton("<<")
        
        tez_buttons_layout.addWidget(self.add_all_tez_button)
        tez_buttons_layout.addWidget(self.add_tez_button)
        tez_buttons_layout.addWidget(self.remove_tez_button)
        tez_buttons_layout.addWidget(self.remove_all_tez_button)
        tez_buttons_layout.addStretch()
        
        tez_selection_layout.addWidget(QLabel("Доступные ТЭЗ:"))
        tez_selection_layout.addWidget(self.available_tez_list)
        tez_selection_layout.addLayout(tez_buttons_layout)
        tez_selection_layout.addWidget(QLabel("ТЭЗ в изделии:"))
        tez_selection_layout.addWidget(self.selected_tez_list)
        
        form_layout.addRow("Название изделия:", self.product_name_edit)
        form_layout.addRow("Персонал:", self.product_personnel_combo)
        form_layout.addRow("База хранения:", self.product_base_combo)
        form_layout.addRow("Состав ТЭЗ:", tez_selection_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.add_product_button = QPushButton("Добавить")
        self.update_product_button = QPushButton("Обновить")
        self.delete_product_button = QPushButton("Удалить")
        
        button_layout.addWidget(self.add_product_button)
        button_layout.addWidget(self.update_product_button)
        button_layout.addWidget(self.delete_product_button)
        
        form_layout.addRow(button_layout)
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # Таблица существующих изделий
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(4)
        self.product_table.setHorizontalHeaderLabels(["Название", "Персонал", "База", "ТЭЗ"])
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.product_table)
        
        # Связываем кнопки с функциями
        self.add_product_button.clicked.connect(self.add_product)
        self.update_product_button.clicked.connect(self.update_product)
        self.delete_product_button.clicked.connect(self.delete_product)
        self.add_tez_button.clicked.connect(self.add_selected_tez)
        self.remove_tez_button.clicked.connect(self.remove_selected_tez)
        self.add_all_tez_button.clicked.connect(self.add_all_tez)
        self.remove_all_tez_button.clicked.connect(self.remove_all_tez)
        self.product_table.itemSelectionChanged.connect(self.product_selection_changed)
        
        # Обновляем комбобоксы
        self.update_product_personnel_combo()
        self.update_product_base_combo()
        self.update_tez_lists()
        
        # Обновляем таблицу
        self.update_product_table()
        
        self.tab_widget.addTab(tab, "Изделия")
    
    def update_product_personnel_combo(self):
        """Обновляет комбобокс персонала для изделий"""
        self.product_personnel_combo.clear()
        for name in self.personnel_groups:
            self.product_personnel_combo.addItem(name)
    
    def update_product_base_combo(self):
        """Обновляет комбобокс баз для изделий"""
        self.product_base_combo.clear()
        for name in self.storage_bases:
            self.product_base_combo.addItem(name)
    
    def update_tez_lists(self):
        """Обновляет списки доступных и выбранных ТЭЗ"""
        self.available_tez_list.clear()
        self.selected_tez_list.clear()
        
        for tez_name in self.tez_types:
            self.available_tez_list.addItem(tez_name)
    
    def add_selected_tez(self):
        """Добавляет выбранные ТЭЗ в изделие"""
        selected_items = self.available_tez_list.selectedItems()
        for item in selected_items:
            self.selected_tez_list.addItem(item.text())
            #self.available_tez_list.takeItem(self.available_tez_list.row(item))
    
    def remove_selected_tez(self):
        """Удаляет выбранные ТЭЗ из изделия"""
        selected_items = self.selected_tez_list.selectedItems()
        for item in selected_items:
            #self.available_tez_list.addItem(item.text())
            #self.selected_tez_list.takeItem(self.selected_tez_list.row(item))
            row = self.selected_tez_list.row(item)
            self.selected_tez_list.takeItem(row)
    
    def add_all_tez(self):
        """Добавляет все ТЭЗ в изделие"""
        while self.available_tez_list.count() > 0:
            item = self.available_tez_list.item(0)
            self.selected_tez_list.addItem(item.text())
            self.available_tez_list.takeItem(0)
    
    def remove_all_tez(self):
        """Удаляет все ТЭЗ из изделия"""
        while self.selected_tez_list.count() > 0:
            item = self.selected_tez_list.item(0)
            self.available_tez_list.addItem(item.text())
            self.selected_tez_list.takeItem(0)
    
    def add_product(self):
        """Добавляет новое изделие"""
        name = self.product_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название изделия")
            return
        
        # Получаем список ТЭЗ
        tez_list = []
        for i in range(self.selected_tez_list.count()):
            tez_list.append(self.selected_tez_list.item(i).text())
        
        if not tez_list:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один ТЭЗ")
            return
        
        product_data = {
            "name": name,
            "personnel": self.product_personnel_combo.currentText(),
            "base": self.product_base_combo.currentText(),
            "tez_list": tez_list
        }
        
        self.products[name] = product_data
        self.update_product_table()
        self.clear_product_form()
        self.update_structure_visualization()
    
    def update_product(self):
        """Обновляет существующее изделие"""
        selected_items = self.product_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите изделие для обновления")
            return
        
        name = selected_items[0].text()
        if name not in self.products:
            return
        
        # Получаем список ТЭЗ
        tez_list = []
        for i in range(self.selected_tez_list.count()):
            tez_list.append(self.selected_tez_list.item(i).text())
        
        if not tez_list:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один ТЭЗ")
            return
        
        product_data = {
            "name": name,
            "personnel": self.product_personnel_combo.currentText(),
            "base": self.product_base_combo.currentText(),
            "tez_list": tez_list
        }
        
        self.products[name] = product_data
        self.update_product_table()
        self.update_structure_visualization()
    
    def delete_product(self):
        """Удаляет выбранное изделие"""
        selected_items = self.product_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите изделие для удаления")
            return
        
        name = selected_items[0].text()
        if name in self.products:
            del self.products[name]
        
        self.update_product_table()
        self.clear_product_form()
        self.update_structure_visualization()
    
    def product_selection_changed(self):
        """Обновляет форму при выборе изделия в таблице"""
        selected_items = self.product_table.selectedItems()
        if not selected_items:
            return
        
        name = selected_items[0].text()
        if name in self.products:
            product = self.products[name]
            self.product_name_edit.setText(product["name"])
            self.product_personnel_combo.setCurrentText(product["personnel"])
            self.product_base_combo.setCurrentText(product["base"])
            
            # Обновляем список ТЭЗ
            self.selected_tez_list.clear()
            for tez in product["tez_list"]:
                self.selected_tez_list.addItem(tez)
            
            # Обновляем список доступных ТЭЗ
            self.available_tez_list.clear()
            for tez_name in self.tez_types:
                #if tez_name not in product["tez_list"]:
                self.available_tez_list.addItem(tez_name)
    
    def clear_product_form(self):
        """Очищает форму изделия"""
        self.product_name_edit.clear()
        self.product_personnel_combo.setCurrentIndex(0)
        self.product_base_combo.setCurrentIndex(0)
        self.selected_tez_list.clear()
        #self.update_tez_lists()
        self.available_tez_list.clear()
        # Загружаем ВСЕ ТЭЗы в доступный список
        for tez_name in self.tez_types:
            self.available_tez_list.addItem(tez_name)
    
    def update_product_table(self):
        """Обновляет таблицу изделий"""
        self.product_table.setRowCount(len(self.products))
        
        for row, (name, product) in enumerate(self.products.items()):
            self.product_table.setItem(row, 0, QTableWidgetItem(product["name"]))
            self.product_table.setItem(row, 1, QTableWidgetItem(product["personnel"]))
            self.product_table.setItem(row, 2, QTableWidgetItem(product["base"]))
            
            # Формируем строку с ТЭЗ
            tez_str = ", ".join(product["tez_list"])
            self.product_table.setItem(row, 3, QTableWidgetItem(tez_str))
    
    def create_sources_tab(self):
        """Создает вкладку для настройки источников пополнения"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для добавления источника
        group = QGroupBox("Добавить/Редактировать источник пополнения")
        form_layout = QFormLayout()
        
        self.source_name_edit = QLineEdit()
        self.source_personnel_combo = QComboBox()
        self.source_lines_spin = QSpinBox()
        self.source_lines_spin.setRange(1, 100)
        self.source_lines_spin.setValue(3)
        
        # Виджет для выбора ТЭЗ
        tez_selection_layout = QHBoxLayout()
        
        self.source_available_tez_list = QListWidget()
        self.source_selected_tez_list = QListWidget()
        
        # Кнопки управления выбором ТЭЗ
        tez_buttons_layout = QVBoxLayout()
        self.source_add_tez_button = QPushButton(">")
        self.source_remove_tez_button = QPushButton("<")
        self.source_add_all_tez_button = QPushButton(">>")
        self.source_remove_all_tez_button = QPushButton("<<")
        
        tez_buttons_layout.addWidget(self.source_add_all_tez_button)
        tez_buttons_layout.addWidget(self.source_add_tez_button)
        tez_buttons_layout.addWidget(self.source_remove_tez_button)
        tez_buttons_layout.addWidget(self.source_remove_all_tez_button)
        tez_buttons_layout.addStretch()
        
        tez_selection_layout.addWidget(QLabel("Доступные ТЭЗ:"))
        tez_selection_layout.addWidget(self.source_available_tez_list)
        tez_selection_layout.addLayout(tez_buttons_layout)
        tez_selection_layout.addWidget(QLabel("Производимые ТЭЗ:"))
        tez_selection_layout.addWidget(self.source_selected_tez_list)
        
        form_layout.addRow("Название источника:", self.source_name_edit)
        form_layout.addRow("Персонал:", self.source_personnel_combo)
        form_layout.addRow("Количество производственных линий:", self.source_lines_spin)
        form_layout.addRow("Производимые ТЭЗ:", tez_selection_layout)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.add_source_button = QPushButton("Добавить")
        self.update_source_button = QPushButton("Обновить")
        self.delete_source_button = QPushButton("Удалить")
        
        button_layout.addWidget(self.add_source_button)
        button_layout.addWidget(self.update_source_button)
        button_layout.addWidget(self.delete_source_button)
        
        form_layout.addRow(button_layout)
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # Таблица существующих источников
        self.source_table = QTableWidget()
        self.source_table.setColumnCount(4)
        self.source_table.setHorizontalHeaderLabels(["Название", "Персонал", "Производств. линии", "ТЭЗ"])
        self.source_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.source_table)
        
        # Связываем кнопки с функциими
        self.add_source_button.clicked.connect(self.add_source)
        self.update_source_button.clicked.connect(self.update_source)
        self.delete_source_button.clicked.connect(self.delete_source)
        self.source_table.itemSelectionChanged.connect(self.source_selection_changed)
        self.source_add_tez_button.clicked.connect(self.source_add_selected_tez)
        self.source_remove_tez_button.clicked.connect(self.source_remove_selected_tez)
        self.source_add_all_tez_button.clicked.connect(self.source_add_all_tez)
        self.source_remove_all_tez_button.clicked.connect(self.source_remove_all_tez)
        
        # Обновляем комбобокс персонала
        self.update_source_personnel_combo()
        self.update_source_tez_lists()
        
        # Обновляем таблицу
        self.update_source_table()
        
        self.tab_widget.addTab(tab, "Источники пополнения")
    
    def update_source_personnel_combo(self):
        """Обновляет комбобокс персонала для источников"""
        self.source_personnel_combo.clear()
        for name in self.personnel_groups:
            self.source_personnel_combo.addItem(name)
    
    def update_source_tez_lists(self):
        """Обновляет списки доступных и выбранных ТЭЗ для источников"""
        self.source_available_tez_list.clear()
        self.source_selected_tez_list.clear()
        
        for tez_name in self.tez_types:
            self.source_available_tez_list.addItem(tez_name)
    
    def source_add_selected_tez(self):
        """Добавляет выбранные ТЭЗ в источник"""
        selected_items = self.source_available_tez_list.selectedItems()
        for item in selected_items:
            self.source_selected_tez_list.addItem(item.text())
            self.source_available_tez_list.takeItem(self.source_available_tez_list.row(item))
    
    def source_remove_selected_tez(self):
        """Удаляет выбранные ТЭЗ из источника"""
        selected_items = self.source_selected_tez_list.selectedItems()
        for item in selected_items:
            self.source_available_tez_list.addItem(item.text())
            self.source_selected_tez_list.takeItem(self.source_selected_tez_list.row(item))
    
    def source_add_all_tez(self):
        """Добавляет все ТЭЗ в источник"""
        while self.source_available_tez_list.count() > 0:
            item = self.source_available_tez_list.item(0)
            self.source_selected_tez_list.addItem(item.text())
            self.source_available_tez_list.takeItem(0)
    
    def source_remove_all_tez(self):
        """Удаляет все ТЭЗ из источника"""
        while self.source_selected_tez_list.count() > 0:
            item = self.source_selected_tez_list.item(0)
            self.source_available_tez_list.addItem(item.text())
            self.source_selected_tez_list.takeItem(0)
    
    def add_source(self):
        """Добавляет новый источник пополнения"""
        name = self.source_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название источника")
            return
        
        # Получаем список ТЭЗ
        tez_list = []
        for i in range(self.source_selected_tez_list.count()):
            tez_list.append(self.source_selected_tez_list.item(i).text())
        
        if not tez_list:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один ТЭЗ")
            return
        
        source_data = {
            "name": name,
            "personnel": self.source_personnel_combo.currentText(),
            "production_lines": self.source_lines_spin.value(),
            "tez_types": tez_list
        }
        
        self.sources[name] = source_data
        self.update_source_table()
        self.clear_source_form()
        self.update_base_combo()  # Обновляем комбобоксы, где используются источники
        self.update_structure_visualization()
    
    def update_source(self):
        """Обновляет существующий источник пополнения"""
        selected_items = self.source_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите источник для обновления")
            return
        
        name = selected_items[0].text()
        if name not in self.sources:
            return
        
        # Получаем список ТЭЗ
        tez_list = []
        for i in range(self.source_selected_tez_list.count()):
            tez_list.append(self.source_selected_tez_list.item(i).text())
        
        if not tez_list:
            QMessageBox.warning(self, "Ошибка", "Добавьте хотя бы один ТЭЗ")
            return
        
        source_data = {
            "name": name,
            "personnel": self.source_personnel_combo.currentText(),
            "production_lines": self.source_lines_spin.value(),
            "tez_types": tez_list
        }
        
        self.sources[name] = source_data
        self.update_source_table()
        self.update_structure_visualization()
    
    def delete_source(self):
        """Удаляет выбранный источник пополнения"""
        selected_items = self.source_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите источник для удаления")
            return
        
        name = selected_items[0].text()
        if name in self.sources:
            del self.sources[name]
        
        self.update_source_table()
        self.clear_source_form()
        self.update_base_combo()  # Обновляем комбобоксы, где используются источники
        self.update_structure_visualization()
    
    def source_selection_changed(self):
        """Обновляет форму при выборе источника в таблице"""
        selected_items = self.source_table.selectedItems()
        if not selected_items:
            return
        
        name = selected_items[0].text()
        if name in self.sources:
            source = self.sources[name]
            self.source_name_edit.setText(source["name"])
            self.source_personnel_combo.setCurrentText(source["personnel"])
            self.source_lines_spin.setValue(source["production_lines"])
            
            # Обновляем список ТЭЗ
            self.source_selected_tez_list.clear()
            for tez in source["tez_types"]:
                self.source_selected_tez_list.addItem(tez)
            
            # Обновляем список доступных ТЭЗ
            self.source_available_tez_list.clear()
            for tez_name in self.tez_types:
                if tez_name not in source["tez_types"]:
                    self.source_available_tez_list.addItem(tez_name)
    
    def clear_source_form(self):
        """Очищает форму источника"""
        self.source_name_edit.clear()
        self.source_personnel_combo.setCurrentIndex(0)
        self.source_lines_spin.setValue(3)
        self.source_selected_tez_list.clear()
        self.update_source_tez_lists()
    
    def update_source_table(self):
        """Обновляет таблицу источников"""
        self.source_table.setRowCount(len(self.sources))
        
        for row, (name, source) in enumerate(self.sources.items()):
            self.source_table.setItem(row, 0, QTableWidgetItem(source["name"]))
            self.source_table.setItem(row, 1, QTableWidgetItem(source["personnel"]))
            self.source_table.setItem(row, 2, QTableWidgetItem(str(source["production_lines"])))
            
            # Формируем строку с ТЭЗ
            tez_str = ", ".join(source["tez_types"])
            self.source_table.setItem(row, 3, QTableWidgetItem(tez_str))
    
    def create_transport_tab(self):
        """Создает вкладку для настройки транспорта"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа для добавления транспорта
        group = QGroupBox("Добавить/Редактировать транспортную систему")
        form_layout = QFormLayout()
        
        self.transport_name_edit = QLineEdit()
        self.transport_speed_spin = QDoubleSpinBox()
        self.transport_speed_spin.setRange(0, 1000)
        self.transport_speed_spin.setValue(60)
        self.transport_capacity_spin = QSpinBox()
        self.transport_capacity_spin.setRange(1, 1000)
        self.transport_capacity_spin.setValue(10)
        self.transport_cost_spin = QDoubleSpinBox()
        self.transport_cost_spin.setRange(0, 1000)
        self.transport_cost_spin.setValue(50)
        
        form_layout.addRow("Название системы:", self.transport_name_edit)
        form_layout.addRow("Средняя скорость (км/ч):", self.transport_speed_spin)
        form_layout.addRow("Грузоподъемность (ед. ТЭЗ):", self.transport_capacity_spin)
        form_layout.addRow("Стоимость за км:", self.transport_cost_spin)
        
        # Кнопки
        button_layout = QHBoxLayout()
        self.add_transport_button = QPushButton("Добавить")
        self.update_transport_button = QPushButton("Обновить")
        self.delete_transport_button = QPushButton("Удалить")
        
        button_layout.addWidget(self.add_transport_button)
        button_layout.addWidget(self.update_transport_button)
        button_layout.addWidget(self.delete_transport_button)
        
        form_layout.addRow(button_layout)
        group.setLayout(form_layout)
        layout.addWidget(group)
        
        # Таблица существующих транспортных систем
        self.transport_table = QTableWidget()
        self.transport_table.setColumnCount(4)
        self.transport_table.setHorizontalHeaderLabels([
            "Название", "Скорость (км/ч)", "Грузоподъемность", "Стоимость за км"
        ])
        self.transport_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.transport_table)
        
        # Связываем кнопки с функциями
        self.add_transport_button.clicked.connect(self.add_transport)
        self.update_transport_button.clicked.connect(self.update_transport)
        self.delete_transport_button.clicked.connect(self.delete_transport)
        self.transport_table.itemSelectionChanged.connect(self.transport_selection_changed)
        
        # Обновляем таблицу
        self.update_transport_table()
        
        self.tab_widget.addTab(tab, "Транспорт")
    
    def add_transport(self):
        """Добавляет новую транспортную систему"""
        name = self.transport_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Введите название транспортной системы")
            return
        
        transport_data = {
            "name": name,
            "avg_speed": self.transport_speed_spin.value(),
            "capacity": self.transport_capacity_spin.value(),
            "cost_per_km": self.transport_cost_spin.value()
        }
        
        self.transports[name] = transport_data
        self.update_transport_table()
        self.clear_transport_form()
        self.update_base_combo()  # Обновляем комбобоксы, где используется транспорт
        self.update_structure_visualization()
    
    def update_transport(self):
        """Обновляет существующую транспортную систему"""
        selected_items = self.transport_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите транспорт для обновления")
            return
        
        name = selected_items[0].text()
        if name not in self.transports:
            return
        
        transport_data = {
            "name": name,
            "avg_speed": self.transport_speed_spin.value(),
            "capacity": self.transport_capacity_spin.value(),
            "cost_per_km": self.transport_cost_spin.value()
        }
        
        self.transports[name] = transport_data
        self.update_transport_table()
        self.update_structure_visualization()
    
    def delete_transport(self):
        """Удаляет выбранную транспортную систему"""
        selected_items = self.transport_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Ошибка", "Выберите транспорт для удаления")
            return
        
        name = selected_items[0].text()
        if name in self.transports:
            del self.transports[name]
        
        self.update_transport_table()
        self.clear_transport_form()
        self.update_base_combo()  # Обновляем комбобоксы, где используется транспорт
        self.update_structure_visualization()
    
    def transport_selection_changed(self):
        """Обновляет форму при выборе транспорта в таблице"""
        selected_items = self.transport_table.selectedItems()
        if not selected_items:
            return
        
        name = selected_items[0].text()
        if name in self.transports:
            transport = self.transports[name]
            self.transport_name_edit.setText(transport["name"])
            self.transport_speed_spin.setValue(transport["avg_speed"])
            self.transport_capacity_spin.setValue(transport["capacity"])
            self.transport_cost_spin.setValue(transport["cost_per_km"])
    
    def clear_transport_form(self):
        """Очищает форму транспорта"""
        self.transport_name_edit.clear()
        self.transport_speed_spin.setValue(60)
        self.transport_capacity_spin.setValue(10)
        self.transport_cost_spin.setValue(50)
    
    def update_transport_table(self):
        """Обновляет таблицу транспорта"""
        self.transport_table.setRowCount(len(self.transports))
        
        for row, (name, transport) in enumerate(self.transports.items()):
            self.transport_table.setItem(row, 0, QTableWidgetItem(transport["name"]))
            self.transport_table.setItem(row, 1, QTableWidgetItem(str(transport["avg_speed"])))
            self.transport_table.setItem(row, 2, QTableWidgetItem(str(transport["capacity"])))
            self.transport_table.setItem(row, 3, QTableWidgetItem(str(transport["cost_per_km"])))
    
    def create_simulation_tab(self):
        """Создает вкладку для запуска моделирования"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Группа параметров моделирования
        group_params = QGroupBox("Параметры моделирования")
        params_layout = QFormLayout()
        
        self.sim_time_spin = QDoubleSpinBox()
        self.sim_time_spin.setRange(1, 100000)
        self.sim_time_spin.setValue(500)
        self.replenish_interval_spin = QDoubleSpinBox()
        self.replenish_interval_spin.setRange(1, 1000)
        self.replenish_interval_spin.setValue(24)
        
        params_layout.addRow("Время моделирования (ч):", self.sim_time_spin)
        params_layout.addRow("Интервал проверки пополнения (ч):", self.replenish_interval_spin)
        group_params.setLayout(params_layout)
        layout.addWidget(group_params)
        
        # Кнопки управления симуляцией
        control_layout = QHBoxLayout()
        self.run_button = QPushButton("Запуск моделирования")
        self.pause_button = QPushButton("Пауза")
        self.stop_button = QPushButton("Остановить")
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        control_layout.addWidget(self.run_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        layout.addLayout(control_layout)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Визуализация структуры системы
        group_structure = QGroupBox("Структура системы")
        structure_layout = QVBoxLayout()
        
        self.structure_tree = QTreeWidget()
        self.structure_tree.setHeaderLabels(["Компонент", "Параметры"])
        self.structure_tree.setColumnWidth(0, 250)
        
        structure_layout.addWidget(self.structure_tree)
        group_structure.setLayout(structure_layout)
        layout.addWidget(group_structure)
        
        # Вывод результатов
        group_results = QGroupBox("Результаты моделирования")
        results_layout = QVBoxLayout()
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        
        # Кнопка очистки результатов
        clear_button_layout = QHBoxLayout()
        self.clear_results_button = QPushButton("Очистить результаты")
        clear_button_layout.addStretch()
        clear_button_layout.addWidget(self.clear_results_button)
        
        results_layout.addWidget(self.results_text)
        results_layout.addLayout(clear_button_layout)
        group_results.setLayout(results_layout)
        layout.addWidget(group_results)
        
        # Связываем кнопки
        self.run_button.clicked.connect(self.start_simulation)
        self.pause_button.clicked.connect(self.pause_simulation)
        self.stop_button.clicked.connect(self.stop_simulation)
        self.clear_results_button.clicked.connect(self.clear_results)
        
        self.tab_widget.addTab(tab, "Моделирование")
    
    def clear_results(self):
        """Очищает результаты моделирования"""
        self.results_text.clear()
    
    def start_simulation(self):
        """Запускает моделирование в отдельном потоке"""
        try:
            # Очищаем предыдущие результаты
            self.results_text.clear()
        
            # Создаем и настраиваем поток
            self.sim_thread = SimulationThread(self)
            self.sim_thread.update_log.connect(self.results_text.append)
            self.sim_thread.update_progress.connect(self.progress_bar.setValue)
            self.sim_thread.finished.connect(self.simulation_finished)
        
            # Активируем кнопки управления
            self.run_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        
            # Запускаем поток
            self.sim_thread.start()
        except Exception as e:
            self.results_text.append(f"Ошибка запуска: {str(e)}")
            import traceback
            self.results_text.append(traceback.format_exc())

    def pause_simulation(self):
        """Приостанавливает или возобновляет моделирование"""
        if self.sim_thread.paused:
            self.sim_thread.paused = False
            self.pause_button.setText("Пауза")
        else:
            self.sim_thread.paused = True
            self.pause_button.setText("Продолжить")

    def stop_simulation(self):
        """Останавливает моделирование"""
        self.sim_thread.stopped = True
        self.sim_thread.running = False
        self.simulation_finished()

    def simulation_finished(self):
        """Обрабатывает завершение моделирования"""
        self.run_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.pause_button.setText("Пауза")
        
        # Ждем завершения потока
        if hasattr(self, 'sim_thread'):
            self.sim_thread.wait(2000)
    
    def update_structure_visualization(self):
        """Обновляет визуализацию структуры системы"""
        self.structure_tree.clear()
        
        # Добавляем ТЭЗ
        tez_root = QTreeWidgetItem(self.structure_tree, ["ТЭЗ", ""])
        for tez in self.tez_types.values():
            params = f"Габариты: {tez['gabarits']}, Стоимость: {tez['cost']}, МО наработки: {tez['theta']}"
            QTreeWidgetItem(tez_root, [tez["n_nom"], params])
        
        # Добавляем персонал
        personnel_root = QTreeWidgetItem(self.structure_tree, ["Персонал", ""])
        for personnel in self.personnel_groups.values():
            params = f"Количество: {personnel['n_count']}"
            QTreeWidgetItem(personnel_root, [personnel["name"], params])
        
        # Добавляем базы
        bases_root = QTreeWidgetItem(self.structure_tree, ["Базы хранения", ""])
        for base in self.storage_bases.values():
            base_item = QTreeWidgetItem(bases_root, [base["name"], f"Уровень: {base['level']}"])
            
            # Политики запасов
            policies_item = QTreeWidgetItem(base_item, ["Политики управления запасами", ""])
            for tez_nom, policy in base.get("policies", {}).items():
                strategy = policy.get("strategy", "")
                min_stock = policy.get("min", 0)
                max_stock = policy.get("max", 0)
                safety_stock = policy.get("safety_stock", 0)
                
                policy_str = f"ТЭЗ: {tez_nom}, Стратегия: {strategy}, Min: {min_stock}, Max: {max_stock}, Неснижаемый: {safety_stock}"
                if strategy == "periodic":
                    policy_str += f", Период: {policy.get('period', 0)}"
                
                QTreeWidgetItem(policies_item, [tez_nom, policy_str])
            
            # Транспортные связи
            transport_item = QTreeWidgetItem(base_item, ["Транспортные связи", ""])
            for tez_nom, policy in base.get("policies", {}).items():
                transport = policy.get("transport", "")
                distance = policy.get("distance", 0)
                source = policy.get("higher_base", "") or policy.get("source", "")
                
                if source:
                    source_type = "База" if policy.get("higher_base") else "Источник"
                    QTreeWidgetItem(transport_item, [
                        f"{tez_nom} -> {source}", 
                        f"{source_type}: {source}, Транспорт: {transport}, Расстояние: {distance} км"
                    ])
        
        # Добавляем изделия
        products_root = QTreeWidgetItem(self.structure_tree, ["Изделия", ""])
        for product in self.products.values():
            product_item = QTreeWidgetItem(products_root, [product["name"], f"База: {product['base']}"])
            
            # ТЭЗ в изделии
            tez_item = QTreeWidgetItem(product_item, ["ТЭЗ", ""])
            for tez in product["tez_list"]:
                QTreeWidgetItem(tez_item, [tez, ""])
        
        # Добавляем источники
        sources_root = QTreeWidgetItem(self.structure_tree, ["Источники пополнения", ""])
        for source in self.sources.values():
            source_item = QTreeWidgetItem(sources_root, [
                source["name"], 
                f"Производств. линии: {source['production_lines']}, Персонал: {source['personnel']}"
            ])
            
            # Производимые ТЭЗ
            tez_item = QTreeWidgetItem(source_item, ["Производимые ТЭЗ", ""])
            for tez in source["tez_types"]:
                QTreeWidgetItem(tez_item, [tez, ""])
        
        # Добавляем транспорт
        transport_root = QTreeWidgetItem(self.structure_tree, ["Транспорт", ""])
        for transport in self.transports.values():
            params = f"Скорость: {transport['avg_speed']} км/ч, Грузоподъемность: {transport['capacity']}, Стоимость: {transport['cost_per_km']}/км"
            QTreeWidgetItem(transport_root, [transport["name"], params])
        
        self.structure_tree.expandAll()
    
    def create_configuration(self):
        """Создает конфигурацию системы на основе введенных данных"""
        # Создаем персонал
        personnel_objects = {}
        for name, data in self.personnel_groups.items():
            personnel_objects[name] = Personnel(data["name"], data["n_count"])
        
        # Создаем ТЭЗ
        tez_objects = {}
        for name, data in self.tez_types.items():
            tez_objects[name] = TEZ(
                data["n_nom"], data["gabarits"], data["cost"],
                data["theta"], data["sigma_theta"],
                data["t_izg"], data["sigma_t_izg"]
            )
        
        # Создаем источники
        source_objects = {}
        for name, data in self.sources.items():
            personnel = personnel_objects.get(data["personnel"])
            if not personnel:
                raise ValueError(f"Персонал {data['personnel']} не найден для источника {name}")
            
            source_objects[name] = ReplenishmentSource(
                data["name"], personnel, data["production_lines"], data["tez_types"]
            )
        
        # Создаем транспорт
        transport_objects = {}
        for name, data in self.transports.items():
            transport_objects[name] = Transport(
                data["name"], data["avg_speed"], data["capacity"], data["cost_per_km"]
            )
        
        # Создаем базы хранения - КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ: создаем словарь сразу
        base_objects = {}
        bases_to_configure = []
        
        # Сначала создаем все объекты баз
        for name, data in self.storage_bases.items():
            personnel = personnel_objects.get(data["personnel"])
            if not personnel:
                raise ValueError(f"Персонал {data['personnel']} не найден для базы {name}")
            
            base = StorageBase(
                name=data["name"],
                level=data["level"],
                personnel=personnel,
                tez_catalog=tez_objects
            )
            base_objects[name] = base
            bases_to_configure.append((name, data))
        
        # Теперь конфигурируем базы (когда все объекты уже созданы)
        for name, data in bases_to_configure:
            base = base_objects[name]
            # Устанавливаем политики управления запасами и источники пополнения
            for tez_nom, policy in data.get("policies", {}).items():
                period = policy.get("period")
                safety_stock = policy.get("safety_stock")
                base.set_stock_policy(
                    tez_nom, policy["min"], policy["max"], 
                    policy["strategy"], period, safety_stock
                )
                
                # Устанавливаем источник пополнения
                higher_base = base_objects.get(policy.get("higher_base", ""))
                source = source_objects.get(policy.get("source", ""))
                transport = transport_objects.get(policy.get("transport", ""))
                distance = policy.get("distance", 100.0)
                
                base.set_replenish_source(
                    tez_nom,
                    higher_base=higher_base,
                    source=source,
                    transport=transport,
                    distance=distance
                )
        
        # Создаем изделия (после создания и конфигурации баз)
        product_objects = []
        for name, data in self.products.items():
            personnel = personnel_objects.get(data["personnel"])
            if not personnel:
                raise ValueError(f"Персонал {data['personnel']} не найден для изделия {name}")
            
            base = base_objects.get(data["base"])
            if not base:
                raise ValueError(f"База {data['base']} не найдена для изделия {name}")
            
            tez_list = []
            for tez_nom in data["tez_list"]:
                tez = tez_objects.get(tez_nom)
                if not tez:
                    raise ValueError(f"ТЭЗ {tez_nom} не найден для изделия {name}")
                tez_list.append(tez)
            
            product_objects.append(Product(
                data["name"], tez_list, personnel, base
            ))
        
        return {
            "products": product_objects,
            "bases": list(base_objects.values()),
            "sources": list(source_objects.values()),
            "transports": list(transport_objects.values()),
            "replenishment_interval": self.replenish_interval_spin.value()
        }
    
    def save_configuration(self):
        """Сохраняет текущую конфигурацию в файл"""
        try:
            config = {
                "tez_types": self.tez_types,
                "personnel_groups": self.personnel_groups,
                "storage_bases": self.storage_bases,
                "products": self.products,
                "sources": self.sources,
                "transports": self.transports
            }
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить конфигурацию", "", "JSON Files (*.json)"
            )
            
            if file_path:
                if not file_path.endswith('.json'):
                    file_path += '.json'
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Успех", "Конфигурация успешно сохранена!")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при сохранении: {str(e)}")

    def load_configuration(self):
        """Загружает конфигурацию из файла"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Загрузить конфигурацию", "", "JSON Files (*.json)"
            )
            
            if file_path:
                with open(file_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Обновляем данные
                self.tez_types = config.get("tez_types", {})
                self.personnel_groups = config.get("personnel_groups", {})
                self.storage_bases = config.get("storage_bases", {})
                self.products = config.get("products", {})
                self.sources = config.get("sources", {})
                self.transports = config.get("transports", {})
                
                # Обновляем интерфейс
                self.update_tez_table()
                self.update_personnel_table()
                self.update_base_table()
                self.update_product_table()
                self.update_source_table()
                self.update_transport_table()
                
                self.update_personnel_combo()
                self.update_base_combo()
                self.update_source_combo()
                self.update_transport_combo()
                self.update_product_personnel_combo()
                self.update_product_base_combo()
                self.update_source_personnel_combo()
                self.update_tez_lists()
                self.update_source_tez_lists()
                
                self.update_structure_visualization()
                QMessageBox.information(self, "Успех", "Конфигурация успешно загружена!")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке: {str(e)}")
    def create_diagram_tab(self):
        """Создает вкладку для графического представления структуры системы с легендой"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
    
        # Кнопка обновления схемы
        self.update_diagram_button = QPushButton("Обновить схему")
        self.update_diagram_button.clicked.connect(self.update_diagram)
        layout.addWidget(self.update_diagram_button)
    
        # Контейнер для схемы и легенды
        container = QWidget()
        container_layout = QHBoxLayout(container)
    
        # Создаем виджет схемы
        self.diagram_view = SystemDiagram()
        container_layout.addWidget(self.diagram_view, 85)  # 85% ширины для схемы
    
        # Контейнер для легенды
        legend_container = QWidget()
        self.legend_layout = QVBoxLayout(legend_container)
        self.legend_layout.setAlignment(Qt.AlignTop)
        self.legend_label = QLabel("Легенда транспорта")
        self.legend_layout.addWidget(self.legend_label)
    
        # Виджет для элементов легенды
        self.legend_widget = QWidget()
        self.legend_items_layout = QVBoxLayout(self.legend_widget)
        self.legend_items_layout.setAlignment(Qt.AlignTop)
    
        scroll = QScrollArea()
        scroll.setWidget(self.legend_widget)
        scroll.setWidgetResizable(True)
    
        self.legend_layout.addWidget(scroll)
        self.legend_layout.addStretch()
    
        container_layout.addWidget(legend_container, 15)  # 15% ширины для легенды
    
        layout.addWidget(container)
        self.tab_widget.addTab(tab, "Структурная схема")
    
        # Словарь для хранения элементов легенды
        self.legend_items = {}
    
    def update_diagram(self):
        """Обновляет графическое представление структуры системы в древовидном стиле"""
        self.diagram_view.clear_diagram()
        # Очищаем легенду
        for i in reversed(range(self.legend_layout.count())):
            item = self.legend_layout.itemAt(i)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.legend_label = QLabel("Легенда транспорта")
        self.legend_layout.addWidget(self.legend_label)
        self.legend_items = {}


        # Константы для позиционирования
        MARGIN = 20
        LEVEL_HEIGHT = 150
        HORIZONTAL_SPACING = 200
    
        # Цвета для разных типов компонентов
        product_color = QColor(173, 216, 230)    # Голубой
        lower_base_color = QColor(144, 238, 144) # Светло-зеленый (нижние базы)
        middle_base_color = QColor(100, 200, 100) # Темно-зеленый (средние базы)
        source_color = QColor(255, 218, 185)     # Персиковый
    
        # Цвета для разных типов транспорта
        transport_colors = {
            "Грузовик": Qt.red,
            "Фура": Qt.blue,
            "Микроавтобус": QColor(255, 165, 0), # Оранжевый
            "Самолет": QColor(128, 0, 128),      # Фиолетовый
            "default": Qt.darkGray
        }
    
        # Словари для хранения блоков
        blocks = {}
    
        # Уровни (y-координаты)
        levels = {
            "product": MARGIN + LEVEL_HEIGHT * 3,
            "lower_base": MARGIN + LEVEL_HEIGHT * 2.5,
            "middle_base": MARGIN + LEVEL_HEIGHT * 1.7,
            "source": MARGIN
        }
    
        # 1. СОЗДАЕМ ИЗДЕЛИЯ (САМЫЙ НИЖНИЙ УРОВЕНЬ)
        x = MARGIN
        for name, product in self.products.items():
            block = self.diagram_view.add_block(
                f"Изделие: \n{name}", 
                x, levels["product"], 
                150, 50, 
                product_color
            )
            blocks[name] = block
            x += HORIZONTAL_SPACING
    
        # 2. СОЗДАЕМ БАЗЫ НИЖНЕГО УРОВНЯ
        base_to_products = {}
        for name, product in self.products.items():
            base_name = product.get("base", "")
            if base_name:
                if base_name not in base_to_products:
                    base_to_products[base_name] = []
                base_to_products[base_name].append(name)
    
        x = MARGIN
        for base_name, products in base_to_products.items():
            if base_name not in self.storage_bases:
                continue
            
            # Позиция базы над центром ее изделий
            product_count = len(products)
            center_x = x + (product_count - 1) * HORIZONTAL_SPACING / 2
        
            base = self.storage_bases[base_name]
            level = base.get("level", "unknown")
            block = self.diagram_view.add_block(
                f"База: \n{base_name}", 
                center_x, levels["lower_base"], 
                150, 50, 
                lower_base_color
            )
            blocks[base_name] = block
        
            # Сдвигаем позицию для следующей группы
            x += product_count * HORIZONTAL_SPACING
    
        # 3. СОЗДАЕМ БАЗЫ СРЕДНЕГО УРОВНЯ И ИСТОЧНИКИ
        source_to_bases = {}
        for base_name, base in self.storage_bases.items():
            if "policies" not in base:
                continue
            
            source_name = None
            for policy in base["policies"].values():
                if policy.get("higher_base"):
                    source_name = policy["higher_base"]
                    break
                elif policy.get("source"):
                    source_name = policy["source"]
                    break
        
            if source_name and source_name in blocks:
                continue  # Уже создан
            
            if source_name:
                if source_name not in source_to_bases:
                    source_to_bases[source_name] = []
                source_to_bases[source_name].append(base_name)
    
        x = MARGIN
        for source_name, bases in source_to_bases.items():
            # Позиция источника над центром его баз
            base_count = len(bases)
            center_x = x + (base_count - 1) * HORIZONTAL_SPACING / 2
        
            if source_name in self.storage_bases:
                # Это база среднего уровня
                base = self.storage_bases[source_name]
                level = base.get("level", "unknown")
                block = self.diagram_view.add_block(
                    f"База: \n{source_name}", 
                    center_x, levels["middle_base"], 
                    150, 50, 
                    middle_base_color
                )
            elif source_name in self.sources:
                # Это источник
                block = self.diagram_view.add_block(
                    f"Источник: \n{source_name}", 
                    center_x, levels["source"], 
                    150, 50, 
                    source_color
                )
        
            blocks[source_name] = block
            x += base_count * HORIZONTAL_SPACING
        
        # 4. СОЗДАЕМ ОСТАВШИЕСЯ ИСТОЧНИКИ
        x = MARGIN
        for name, source in self.sources.items():
            if name not in blocks:
                block = self.diagram_view.add_block(
                    f"Источник: {name}", 
                    x, levels["source"], 
                    150, 50, 
                    source_color
                )
                blocks[name] = block
                x += HORIZONTAL_SPACING
    
        # 5. СОЗДАЕМ СВЯЗИ
        # 5.1 Связи между изделиями и их базами
        for name, product in self.products.items():
            base_name = product.get("base", "")
            if base_name in blocks and name in blocks:
                self.diagram_view.add_connection(
                    blocks[name], 
                    blocks[base_name]
                )
    
        # 5.2 Связи между базами и их источниками
        for base_name, base in self.storage_bases.items():
            if "policies" not in base or base_name not in blocks:
                continue
        
            for tez_nom, policy in base.get("policies", {}).items():
                source_name = policy.get("higher_base") or policy.get("source")
                if not source_name or source_name not in blocks:
                    continue
            
                transport_name = policy.get("transport", "")
                color = self.diagram_view.add_connection(
                    blocks[base_name], 
                    blocks[source_name],
                    transport_name
                )
            
                # Добавляем в легенду, если это новый тип транспорта
                if transport_name and transport_name not in self.legend_items:
                    self.add_legend_item(transport_name, color)
    
        # Автоматически масштабируем вид
        self.diagram_view.fitInView(
            self.diagram_view.scene.itemsBoundingRect(), 
            Qt.KeepAspectRatio
        )

    def add_legend_item(self, transport_name, color):
        """Добавляет элемент в легенду"""
        # Создаем виджет для элемента легенды
        item_widget = QWidget()
        layout = QHBoxLayout(item_widget)
        layout.setContentsMargins(2, 2, 2, 2)
    
        # Цветной квадратик
        color_label = QLabel()
        pixmap = QPixmap(20, 20)
        pixmap.fill(color)
        color_label.setPixmap(pixmap)
    
        # Название транспорта
        name_label = QLabel(transport_name)
    
        layout.addWidget(color_label)
        layout.addWidget(name_label)
        self.legend_layout.addWidget(item_widget)
        self.legend_items[transport_name] = item_widget
    
        # Автоматически масштабируем вид
        self.diagram_view.fitInView(self.diagram_view.scene.itemsBoundingRect(), Qt.KeepAspectRatio)
# Запуск приложения
if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Установка иконки для приложения (опционально)
    app.setWindowIcon(QIcon(resource_path("app_icon.ico")))

    window = TEZSystemGUI()
    window.show()
    sys.exit(app.exec_())



# %%
