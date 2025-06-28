import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib.widgets import Button, TextBox
import queue
import random
import numpy as np
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import sys
import os


class ComponentState(Enum):
    IDLE = auto()  # Белый - неактивен
    BUSY = auto()  # Зеленый - активно работает
    WAITING = auto()  # Желтый - ожидает обработки
    ARBITRATION = auto()  # Оранжевый - выборка/арбитраж


@dataclass
class Thread:
    id: int
    total_instructions: int
    current_instruction: int = 0
    start_time: int = -1
    end_time: int = -1
    state: ComponentState = ComponentState.IDLE


@dataclass
class Processor:
    id: int
    current_thread: Optional[Thread] = None
    busy_time: int = 0
    idle_time: int = 0
    state: ComponentState = ComponentState.IDLE


class SystemVisualization:
    def __init__(self):
        self.fig = plt.figure(figsize=(16, 10), facecolor='whitesmoke')
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05, wspace=0.3, hspace=0.3)

        # Создаем сетку 2x3
        self.grid = plt.GridSpec(2, 3, width_ratios=[1.2, 1.5, 1.3], height_ratios=[1, 1])

        # 1. Область для ввода параметров (слева)
        self.input_ax = plt.subplot(self.grid[0, 0])
        self._setup_input_panel()

        # 2. Центральная область для схемы моделирования
        self.ax = plt.subplot(self.grid[:, 1])
        self.ax.set_xlim(0, 12)
        self.ax.set_ylim(0, 10)
        self.ax.set_aspect('equal')
        self.ax.axis('off')
        self._setup_system_visualization(4)  # Инициализация с 4 ПЭ по умолчанию

        # 3.1 Область для графиков работы ПЭ (справа вверху)
        self.timeline_ax = plt.subplot(self.grid[0, 2])
        self.timeline_ax.set_title('График работы ПЭ', pad=10)
        self.timeline_ax.set_xlabel('Такты')
        self.timeline_ax.set_ylabel('Процессорные элементы')
        self.timeline_ax.grid(True, linestyle='--', alpha=0.6)

        # 3.2 Область для активных операций (справа внизу)
        self.queue_ax = plt.subplot(self.grid[1, 2])
        self.queue_ax.set_title('Активные операции', pad=10)
        self.queue_ax.axis('off')

        # Область для статистики
        self.stats_ax = self.fig.add_axes([0.68, 0.13, 0.3, 0.15])
        self.stats_ax.set_title('Статистика системы', pad=10)
        self.stats_ax.axis('off')

        # Текстовые элементы
        self.title = self.ax.text(6, 9.5, 'Мультитредовая система', fontsize=14, ha='center',
                                  bbox=dict(facecolor='white', edgecolor='black', boxstyle='round'))
        self.stats_text = self.stats_ax.text(0.05, 0.9, '', fontsize=10, va='top',
                                             bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'))
        self.queue_text = self.queue_ax.text(0.05, 0.95, 'Активные операции:\n- Система инициализирована',
                                             fontsize=10, va='top',
                                             bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'))

        # Границы для областей
        self._draw_panel_borders()

    def _draw_panel_borders(self):
        """Рисует границы вокруг панелей для лучшей визуализации"""
        for ax in [self.input_ax, self.timeline_ax, self.queue_ax]:
            for spine in ax.spines.values():
                spine.set_color('gray')
                spine.set_linewidth(1)

        # Более толстая рамка для центральной панели
        for spine in self.ax.spines.values():
            spine.set_color('black')
            spine.set_linewidth(2)

    def _setup_input_panel(self):
        """Настройка панели ввода параметров"""
        self.input_ax.set_title('Параметры системы', pad=10)
        self.input_ax.axis('off')

        # Создаем рамку для группы элементов ввода
        input_box = patches.Rectangle((0.02, 0.02), 0.96, 0.96,
                                      transform=self.input_ax.transAxes,
                                      facecolor='white', edgecolor='gray',
                                      alpha=0.8, linewidth=1)
        self.input_ax.add_patch(input_box)

        # Поле для ввода количества ПЭ
        self.input_ax.text(0.1, 0.85, 'Количество ПЭ (1-8):', fontsize=10)
        self.pe_input_ax = plt.axes([0.07, 0.85, 0.19, 0.03])
        self.pe_input = TextBox(self.pe_input_ax, '', initial='4')
        self.pe_input.label.set_visible(False)
        self.pe_input_ax.set_facecolor('white')

        # Поле для ввода количества тредов
        self.input_ax.text(0.1, 0.7, 'Количество тредов (1-20):', fontsize=10)
        self.thread_input_ax = plt.axes([0.07, 0.79, 0.19, 0.03])
        self.thread_input = TextBox(self.thread_input_ax, '', initial='10')
        self.thread_input.label.set_visible(False)
        self.thread_input_ax.set_facecolor('white')

        # Кнопки выбора режима
        self.mode = 'н'  # по умолчанию непрерывный

        mode_text = self.input_ax.text(0.1, 0.55, 'Режим работы:', fontsize=10)

        step_button_ax = plt.axes([0.17, 0.7, 0.09, 0.05])
        self.step_button = Button(step_button_ax, 'Пошаговый', color='lightgoldenrodyellow')
        self.step_button.label.set_fontsize(10)

        cont_button_ax = plt.axes([0.07, 0.7, 0.09, 0.05])
        self.cont_button = Button(cont_button_ax, 'Непрерывный', color='lightblue')
        self.cont_button.label.set_fontsize(10)

        self.step_button.on_clicked(lambda event: setattr(self, 'mode', 'п'))
        self.cont_button.on_clicked(lambda event: setattr(self, 'mode', 'н'))

        # Кнопка запуска
        start_button_ax = plt.axes([0.07, 0.6, 0.19, 0.06])
        self.start_button = Button(start_button_ax, 'Запуск моделирования', color='lightgreen')
        self.start_button.label.set_fontsize(11)

        # Информационный текст
        self.input_ax.text(0.5, 0.3, 'Настройте параметры\nи нажмите "Запуск"',
                           fontsize=10, ha='center', alpha=0.7)

    def _setup_system_visualization(self, num_processors):
        """Настройка визуализации системы"""
        self.ax.clear()
        self.ax.set_xlim(0, 9)
        self.ax.set_ylim(0, 10)
        self.ax.axis('off')

        self._setup_scheduler()
        self._setup_processors(num_processors)
        self._setup_switch()
        self._setup_memory()



    def _setup_scheduler(self):
        """Настройка визуализации планировщика"""
        self.scheduler_rect = patches.Rectangle((4.5, 8), 3, 1, linewidth=2,
                                                edgecolor='black', facecolor='white')
        self.ax.add_patch(self.scheduler_rect)
        self.ax.text(6, 8.5, 'Планировщик', ha='center', va='center', fontsize=12)

    def _setup_processors(self, num_processors: int):
        """Настройка визуализации процессоров"""
        self.processors_rect = []
        processor_width = 1
        spacing = 0.7
        total_width = num_processors * processor_width + (num_processors - 1) * spacing
        start_x = (12 - total_width) / 2

        for i in range(num_processors):
            x = start_x + i * (processor_width + spacing)
            rect = patches.Rectangle((x, 6), processor_width, 1, linewidth=2,
                                     edgecolor='black', facecolor='white')
            self.ax.add_patch(rect)
            self.ax.text(x + processor_width / 2, 6.5, f'ПЭ-{i + 1}',
                         ha='center', va='center', fontsize=11)
            self.processors_rect.append(rect)

            # Соединительные линии к планировщику
            self.ax.plot([6, x + processor_width / 2], [8, 7], 'k-', lw=1, alpha=0.7)

    def _setup_switch(self):
        """Настройка визуализации коммутатора"""
        self.switch_rect = patches.Rectangle((4.5, 4), 3, 1, linewidth=2,
                                             edgecolor='black', facecolor='white')
        self.ax.add_patch(self.switch_rect)
        self.ax.text(6, 4.5, 'Коммутатор', ha='center', va='center', fontsize=12)

        # Соединительные линии к процессорам
        for rect in self.processors_rect:
            x, y = rect.get_xy()
            self.ax.plot([x + rect.get_width() / 2, 6], [6, 5], 'k-', lw=1, alpha=0.7)

    def _setup_memory(self):
        """Настройка визуализации памяти"""
        self.memory_rect = patches.Rectangle((5, 2), 2, 1, linewidth=2,
                                             edgecolor='black', facecolor='white')
        self.ax.add_patch(self.memory_rect)
        self.ax.text(6, 2.5, 'Память', ha='center', va='center', fontsize=12)
        self.ax.plot([6, 6], [4, 3], 'k-', lw=1, alpha=0.7)

    def _get_color(self, state: ComponentState) -> str:
        """Возвращает цвет для состояния компонента"""
        color_map = {
            ComponentState.IDLE: 'white',
            ComponentState.BUSY: 'limegreen',
            ComponentState.WAITING: 'gold',
            ComponentState.ARBITRATION: 'darkorange'
        }
        return color_map.get(state, 'white')

    def update_timeline(self, processors):
        """Обновление временных диаграмм"""
        self.timeline_ax.clear()
        self.timeline_ax.set_title('График работы ПЭ', pad=10)
        self.timeline_ax.set_xlabel('Такты')
        self.timeline_ax.set_ylabel('Процессорные элементы')
        self.timeline_ax.grid(True, linestyle='--', alpha=0.6)

        max_time = max(p.busy_time + p.idle_time for p in processors) if processors else 1
        self.timeline_ax.set_xlim(0, max_time + 1)
        self.timeline_ax.set_ylim(0, len(processors) + 1)

        for i, processor in enumerate(processors):
            y_pos = len(processors) - i
            self.timeline_ax.broken_barh(
                [(0, processor.busy_time)],
                (y_pos - 0.4, 0.8),
                facecolors='limegreen',
                label='Работа' if i == 0 else ""
            )
            self.timeline_ax.broken_barh(
                [(processor.busy_time, processor.idle_time)],
                (y_pos - 0.4, 0.8),
                facecolors='lightgray',
                label='Простой' if i == 0 else ""
            )
            self.timeline_ax.text(
                max_time + 0.5, y_pos,
                f'ПЭ-{i + 1}: {processor.busy_time / (processor.busy_time + processor.idle_time) * 100:.1f}%',
                va='center', fontsize=9
            )

        self.timeline_ax.legend(loc='upper right', fontsize=9)

    def update(self, states: Dict[str, ComponentState], stats: Dict, processors: List[Processor]) -> List[
        patches.Rectangle]:
        """Обновляет все компоненты системы"""
        # Обновляем цвета компонентов
        self.scheduler_rect.set_facecolor(self._get_color(states['scheduler']))
        self.switch_rect.set_facecolor(self._get_color(states['switch']))
        self.memory_rect.set_facecolor(self._get_color(states['memory']))

        for i, proc_state in enumerate(states['processors']):
            self.processors_rect[i].set_facecolor(self._get_color(proc_state))

        # Обновляем заголовок и статистику
        self.title.set_text(f"Мультитредовая система (Такт: {stats['current_time']})")

        stats_text = (
            f"Завершено: {len(stats['completed_threads'])}/{stats['total_threads']} тредов\n"
            f"Очередь: {stats['queue_size']}\n"
            "Загрузка процессоров:\n"
        )
        for i, util in enumerate(stats['processor_utilization']):
            stats_text += f"ПЭ-{i + 1}: {util:.1f}%\n"

        self.stats_text.set_text(stats_text)

        # Обновляем активные операции
        active_ops = "Активные операции:\n" + "\n".join(
            stats['active_operations'][-5:])  # Показываем последние 5 операций
        self.queue_text.set_text(active_ops)

        # Обновляем временные диаграммы
        self.update_timeline(processors)

        return [self.scheduler_rect, self.switch_rect, self.memory_rect] + self.processors_rect

    def show_final_stats(self, stats: Dict):
        """Отображение итоговой статистики в новом окне"""
        fig = plt.figure(figsize=(12, 8), facecolor='whitesmoke')
        fig.suptitle('Итоговая статистика моделирования', fontsize=14)

        # График загрузки процессоров
        ax1 = fig.add_subplot(221)
        processors = [f'ПЭ-{i + 1}' for i in range(len(stats['processor_utilization']))]
        utilizations = stats['processor_utilization']
        bars = ax1.bar(processors, utilizations, color='skyblue', edgecolor='navy')
        ax1.set_title('Загрузка процессоров (%)', pad=10)
        ax1.set_ylim(0, 100)
        ax1.grid(axis='y', linestyle='--', alpha=0.6)

        # Добавляем значения на столбцы
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{height:.1f}%', ha='center', va='bottom')

        # График времени выполнения тредов
        ax2 = fig.add_subplot(222)
        threads = [f'Тред-{i + 1}' for i in range(len(stats['thread_execution_time']))]
        exec_times = stats['thread_execution_time']
        wait_times = stats['thread_waiting_time']

        ax2.bar(threads, exec_times, color='lightgreen', edgecolor='green', label='Выполнение')
        ax2.bar(threads, wait_times, bottom=exec_times, color='salmon', edgecolor='red', label='Ожидание')
        ax2.set_title('Время выполнения тредов', pad=10)
        ax2.legend(loc='upper right')
        ax2.grid(axis='y', linestyle='--', alpha=0.6)

        # Текстовая статистика
        ax3 = fig.add_subplot(212)
        ax3.axis('off')

        stats_text = (
            f"Общее время выполнения: {stats['current_time']} тактов\n"
            f"Среднее время выполнения: {np.mean(exec_times):.1f} ± {np.std(exec_times):.1f} тактов\n"
            f"Максимальное время выполнения: {max(exec_times)} тактов\n"
            f"Минимальное время выполнения: {min(exec_times)} тактов\n"
            f"Среднее время ожидания: {np.mean(wait_times):.1f} ± {np.std(wait_times):.1f} тактов\n"
            f"Общая загрузка системы: {np.mean(utilizations):.1f}%"
        )

        ax3.text(0.05, 0.7, stats_text, fontsize=12,
                 bbox=dict(facecolor='white', alpha=0.9, boxstyle='round'))

        plt.tight_layout()
        plt.show()


class MultithreadedSystemSimulator:
    def __init__(self, num_processors: int = 4, num_threads: int = 10,
                 max_instructions: int = 200, step_mode: bool = False):
        self.num_processors = num_processors
        self.num_threads = num_threads
        self.max_instructions = max_instructions
        self.step_mode = step_mode
        self.steps_per_frame = 1  # 1 такт = 1 кадр

        self.processors: List[Processor] = [Processor(i) for i in range(num_processors)]
        self.thread_queue = queue.Queue()
        self.completed_threads: List[Thread] = []
        self.current_time = 0
        self.active_operations: List[str] = []

        # Состояния компонентов
        self.states = {
            'scheduler': ComponentState.IDLE,
            'switch': ComponentState.IDLE,
            'memory': ComponentState.IDLE,
            'processors': [ComponentState.IDLE] * num_processors
        }

        # Инициализация очереди
        for i in range(num_threads):
            instructions = random.randint(50, max_instructions)
            self.thread_queue.put(Thread(i, instructions))

        # Настройка визуализации
        self.visualization = SystemVisualization()
        self.visualization._setup_system_visualization(num_processors)  # Исправлено: вызов правильного метода

        # Подключение кнопки запуска
        self.visualization.start_button.on_clicked(self.start_simulation)

        plt.show()

    def start_simulation(self, event):
        """Запуск симуляции по нажатию кнопки"""
        try:
            num_processors = int(self.visualization.pe_input.text)
            num_threads = int(self.visualization.thread_input.text)
            step_mode = self.visualization.mode == 'п'

            # Валидация ввода
            if not (1 <= num_processors <= 8) or not (1 <= num_threads <= 20):
                raise ValueError("Некорректные параметры")

            # Обновляем параметры
            self.num_processors = num_processors
            self.num_threads = num_threads
            self.step_mode = step_mode

            # Переинициализация системы
            self.processors = [Processor(i) for i in range(num_processors)]
            self.thread_queue = queue.Queue()
            self.completed_threads = []
            self.current_time = 0
            self.active_operations = []
            self.states = {
                'scheduler': ComponentState.IDLE,
                'switch': ComponentState.IDLE,
                'memory': ComponentState.IDLE,
                'processors': [ComponentState.IDLE] * num_processors
            }

            for i in range(num_threads):
                instructions = random.randint(50, self.max_instructions)
                self.thread_queue.put(Thread(i, instructions))

            # Обновляем визуализацию
            self.visualization._setup_system_visualization(num_processors)  # Исправлено: вызов правильного метода

            # Запуск анимации
            self.ani = animation.FuncAnimation(
                self.visualization.fig,
                self._animate_frame,
                frames=self._simulation_generator(),
                interval=500 if step_mode else 100,
                blit=False,
                repeat=False,
                save_count=1000
            )

            plt.draw()

        except ValueError as e:
            print(f"Ошибка: {e}")

    def _animate_frame(self, frame_data: Optional[tuple]) -> List[patches.Rectangle]:
        if not frame_data:
            return []

        states, stats = frame_data
        return self.visualization.update(states, stats, self.processors)

    def _simulation_generator(self):
        """Генератор кадров анимации"""
        while not self._is_simulation_complete():
            self.active_operations = []

            # Выполняем 1 такт за кадр
            self._execute_cycle()

            # Подготовка данных для отображения
            stats = self._calculate_statistics()
            stats['active_operations'] = self.active_operations

            yield (self.states, stats)

            if self.step_mode:
                plt.waitforbuttonpress()  # Ожидание нажатия для пошагового режима

        # После завершения показываем итоговую статистику
        final_stats = self._calculate_statistics()
        plt.close(self.visualization.fig)
        self.visualization.show_final_stats(final_stats)
        yield None

    def _execute_cycle(self):
        """Обработка одного такта системы"""
        self.current_time += 1
        self._update_memory()
        self._update_processors()
        self._update_switch()
        self._update_scheduler()

    def _update_memory(self):
        """Обновление состояния памяти"""
        if any(p.current_thread is not None for p in self.processors):
            self.states['memory'] = ComponentState.BUSY
            self.active_operations.append(f"Обращение к памяти (тактов: {self.current_time})")
        else:
            self.states['memory'] = ComponentState.IDLE

    def _update_processors(self):
        """Обновление состояния процессоров"""
        for i, processor in enumerate(self.processors):
            if processor.current_thread is not None:
                processor.current_thread.current_instruction += 1
                processor.busy_time += 1

                # Имитация разных состояний процессора
                if random.random() < 0.3:  # 30% вероятность ожидания
                    self.states['processors'][i] = ComponentState.WAITING
                    self.active_operations.append(f"ПЭ-{i + 1} ожидает данные")
                else:
                    self.states['processors'][i] = ComponentState.BUSY

                # Проверка завершения треда
                if processor.current_thread.current_instruction >= processor.current_thread.total_instructions:
                    processor.current_thread.end_time = self.current_time
                    self.completed_threads.append(processor.current_thread)
                    processor.current_thread = None
            else:
                processor.idle_time += 1
                self.states['processors'][i] = ComponentState.IDLE

    def _update_switch(self):
        """Обновление состояния коммутатора"""
        active_processors = sum(1 for p in self.processors if p.current_thread is not None)

        if active_processors > 1:
            self.states['switch'] = ComponentState.ARBITRATION
            self.active_operations.append("Арбитраж доступа к памяти")
        elif active_processors == 1:
            self.states['switch'] = ComponentState.BUSY
        else:
            self.states['switch'] = ComponentState.IDLE

    def _update_scheduler(self):
        """Обновление планировщика"""
        if self.current_time % 3 == 0 and not self.thread_queue.empty():  # Планирование каждые 3 такта
            self.states['scheduler'] = ComponentState.BUSY
            self.active_operations.append("Планирование задач")

            for processor in self.processors:
                if processor.current_thread is None and not self.thread_queue.empty():
                    try:
                        thread = self.thread_queue.get_nowait()
                        thread.start_time = self.current_time
                        processor.current_thread = thread
                    except queue.Empty:
                        pass

            # Имитация времени работы планировщика
            if random.random() < 0.5:
                self.states['scheduler'] = ComponentState.ARBITRATION
                self.active_operations.append("Выбор оптимального треда")
        else:
            self.states['scheduler'] = ComponentState.IDLE

    def _is_simulation_complete(self) -> bool:
        """Проверка завершения симуляции"""
        return (len(self.completed_threads) == self.num_threads and
                all(p.current_thread is None for p in self.processors))

    def _calculate_statistics(self) -> Dict:
        """Расчет статистики"""
        stats = {
            'current_time': self.current_time,
            'total_threads': self.num_threads,
            'completed_threads': self.completed_threads,
            'queue_size': self.thread_queue.qsize(),
            'processor_utilization': [],
            'processor_busy_time': [],
            'processor_idle_time': [],
            'thread_execution_time': [],
            'thread_waiting_time': [],
            'active_operations': []
        }

        for processor in self.processors:
            total_time = processor.busy_time + processor.idle_time
            utilization = (processor.busy_time / total_time) * 100 if total_time > 0 else 0
            stats['processor_utilization'].append(utilization)
            stats['processor_busy_time'].append(processor.busy_time)
            stats['processor_idle_time'].append(processor.idle_time)

        for thread in self.completed_threads:
            stats['thread_execution_time'].append(thread.end_time - thread.start_time)
            stats['thread_waiting_time'].append(thread.start_time)

        return stats


if __name__ == "__main__":
    simulator = MultithreadedSystemSimulator()