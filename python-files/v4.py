import sys
import numpy as np
import pandas as pd
import random
import json
from datetime import datetime, timedelta
from collections import defaultdict, deque
import torch
import torch.nn as nn
import torch.optim as optim
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
                             QTextEdit, QTabWidget, QGroupBox, QFormLayout, QScrollArea,
                             QProgressBar, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal 
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


CONFIG = {
    "power_levels": {
        "Active": 490,      # 490 Вт из [3], таблица I
        "Signaling": 490,   # 490 Вт
        "Idle": 328,        # 328 Вт
        "SM1": 157,         # 157 Вт
        "SM2": 42.9,        # 42.9 Вт
        "SM3": 28.5         # 28.5 Вт
    },
    "activation_times": {   # Из [4], таблица I
        "SM1": 71e-6,       # 71 μs
        "SM2": 1e-3,        # 1 ms
        "SM3": 5e-3         # 5 ms
    },
    "min_sleep_times": {    # Из [4], таблица I
        "SM1": 71e-6,
        "SM2": 1e-3,
        "SM3": 10e-3        # 10 ms
    },
    "traffic_profiles": ["eMBB", "URLLC", "mMTC"],
    "qos_requirements": {   
        "eMBB": 0.01,       # 10 ms
        "URLLC": 0.001,     # 1 ms
        "mMTC": 0.1         # 100 ms
    },
    "traffic_parameters": {  # Параметры трафика 
        "eMBB": {"interval": (0.01, 0.3), "size": (1, 10)},
        "URLLC": {"interval": (0.001, 0.1), "size": (0.01, 0.1)},
        "mMTC": {"interval": (0.1, 10), "size": (0.1, 1)}
    },
    "simulation_duration_sec": 60  
}

class EnhancedTrafficGenerator:
    
    def __init__(self, traffic_type="eMBB"):
        self.traffic_type = traffic_type
        self.params = CONFIG["traffic_parameters"][traffic_type]
        
    def generate_request(self, current_time):
       
        time_to_next = random.uniform(*self.params["interval"])
        size = random.uniform(*self.params["size"])
        return time_to_next, size, current_time + timedelta(seconds=time_to_next)

class PowerModel:
    
    @staticmethod
    def calculate(state, traffic_load=0.0):
        power = CONFIG["power_levels"].get(state, 0)
 
        if state == "Active":
            power += 2.8 * traffic_load  
        return power

class PowerAnalyzer:
   
    def __init__(self):
        self.power_stats = defaultdict(list)
        self.time_stats = defaultdict(float)
        self.start_time = datetime.now()
        
    def add_measurement(self, state, power, duration):
        
        self.power_stats[state].append(power)
        self.time_stats[state] += duration
        
    def get_summary(self):
        
        total_time = sum(self.time_stats.values())

 
        if total_time == 0:
            return {
                "total_time_sec": 0,
                "avg_power": {},
                "weighted_avg_power": 0,
                "time_per_mode": {},
                "time_percent": {}
            }

        avg_power = {state: np.mean(values) if values else 0 for state, values in self.power_stats.items()}

  
        weighted_power = sum(
            avg_power.get(state, 0) * time 
            for state, time in self.time_stats.items()
        ) / total_time

        return {
            "total_time_sec": total_time,
            "avg_power": avg_power,
            "weighted_avg_power": weighted_power,
            "time_per_mode": self.time_stats,
            "time_percent": {k: v/total_time*100 for k, v in self.time_stats.items()}
        }

class DeepQNetwork(nn.Module):
    
    def __init__(self, input_size, output_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_size)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

class DQNAgent:
    
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=10000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.batch_size = 64
        self.model = DeepQNetwork(state_size, action_size)
        self.target_model = DeepQNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.model.parameters())
        self.update_target_model()
        
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        if random.random() <= self.epsilon:
            return random.randrange(self.action_size)
        state_tensor = torch.FloatTensor(np.array(state))
        with torch.no_grad():
            act_values = self.model(state_tensor)
        return torch.argmax(act_values).item()
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        minibatch = random.sample(self.memory, self.batch_size)
        
     
        states = np.array([x[0] for x in minibatch])
        states = torch.FloatTensor(states)
        
        actions = torch.LongTensor([x[1] for x in minibatch])
        rewards = torch.FloatTensor([x[2] for x in minibatch])
        
        next_states = np.array([x[3] for x in minibatch])
        next_states = torch.FloatTensor(next_states)
        
        dones = torch.FloatTensor([x[4] for x in minibatch])
        
       
        current_q = self.model(states).gather(1, actions.unsqueeze(1))
        
     
        with torch.no_grad():
            next_q = self.target_model(next_states).max(1)[0]
        
        
        target = rewards + (1 - dones) * self.gamma * next_q.unsqueeze(1)
        
       
        loss = nn.MSELoss()(current_q, target)
        
        
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

class BSEnvironment:
    
    def __init__(self, traffic_type="eMBB"):
        self.traffic_type = traffic_type
        self.traffic_gen = EnhancedTrafficGenerator(traffic_type)
        self.power_analyzer = PowerAnalyzer()
        self.sleep_sequence = ["SM3", "SM2", "SM1", "Active"]
        self.current_sleep_level = 3  
        self.current_state = "Active"
        self.simulation_start = datetime.now()
        self.last_update_time = self.simulation_start
        self.next_event_time = self.simulation_start
        
        
        self.total_energy = 0.0
        self.total_delay = 0.0
        self.request_count = 0
        self.qos_violations = 0
        self.history = []
        
    def reset(self):
        self.__init__(self.traffic_type)
        return self._get_state()
    
    def _get_state(self):
        
        elapsed = (datetime.now() - self.simulation_start).total_seconds()
        return np.array([
            elapsed,
            self.current_sleep_level / 3.0,
            self.total_energy / max(1, self.request_count),
            self.total_delay / max(1, self.request_count),
            self.qos_violations / max(1, self.request_count),
            1 if self.current_state == "Active" else 0,
            1 if self.current_state == "SM1" else 0,
            1 if self.current_state == "SM3" else 0
        ], dtype=np.float32)
    
    def step(self, action):
        
        now = datetime.now()
        
       
        if action == 0 and self.current_sleep_level > 0:
            self.current_sleep_level -= 1
        elif action == 1 and self.current_sleep_level < 3:
            self.current_sleep_level += 1
            
        new_state = self.sleep_sequence[self.current_sleep_level]
        
       
        time_in_previous_mode = (now - self.last_update_time).total_seconds()
        power = PowerModel.calculate(self.current_state)
        self.power_analyzer.add_measurement(
            self.current_state, 
            power,
            time_in_previous_mode
        )
        self.total_energy += power * time_in_previous_mode
        
       
        time_to_next, size, self.next_event_time = self.traffic_gen.generate_request(now)
        
      
        delay = self._calculate_delay(new_state, time_to_next)
        self.total_delay += delay
        
       
        qos_ok = delay <= CONFIG["qos_requirements"][self.traffic_type]
        if not qos_ok:
            self.qos_violations += 1
        
       
        reward = self._calculate_reward(power, delay, qos_ok)
        
      
        self.current_state = new_state
        self.last_update_time = now
        self.request_count += 1
        
      
        self.history.append({
            "timestamp": now.isoformat(),
            "state": new_state,
            "power": power,
            "delay": delay,
            "load": size,
            "qos_ok": qos_ok,
            "time_elapsed": (now - self.simulation_start).total_seconds()
        })
        
        return self._get_state(), reward, delay, power, not qos_ok
    
    def _calculate_delay(self, new_state, time_to_next):
        
        if new_state.startswith("SM"):
            activation_time = CONFIG["activation_times"][new_state]
            if time_to_next < activation_time:
                return activation_time - time_to_next
        return 0.0
    
    def _calculate_reward(self, power, delay, qos_ok):
        
        power_norm = power / CONFIG["power_levels"]["Active"]
        delay_norm = delay / CONFIG["qos_requirements"][self.traffic_type]
        qos_penalty = 0 if qos_ok else -10
        return - (0.4 * power_norm + 0.6 * delay_norm) + qos_penalty
    
    def get_detailed_stats(self):
        
        stats = self.power_analyzer.get_summary()
        stats.update({
            "total_requests": self.request_count,
            "qos_violations": self.qos_violations,
            "avg_delay": self.total_delay / max(1, self.request_count),
            "total_energy": self.total_energy,
            "simulation_duration": (datetime.now() - self.simulation_start).total_seconds()
        })
        return stats
    
    def get_mode_time_stats(self):
        
        return self.power_analyzer.time_stats

class MplCanvas(FigureCanvas):
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


class SimulationThread(QThread):
    episode_completed = pyqtSignal(dict)
    stats_updated = pyqtSignal(dict)
    
    def __init__(self, env, agent, episodes):
        super().__init__()
        self.env = env
        self.agent = agent
        self.episodes = episodes
        self.current_episode = 0
        self.episode_duration = CONFIG["simulation_duration_sec"]
        self._is_running = True
        self.time_step = 0.01  
        
    def run(self):
        while self.current_episode < self.episodes and self._is_running:
            start_time = datetime.now()
            
            state = self.env.reset()
            episode_data = {
                "episode": self.current_episode,
                "start_time": start_time,
                "total_reward": 0,
                "avg_delay": 0,
                "total_energy": 0,
                "qos_violations": 0,
                "request_count": 0
            }
            
            virtual_time = 0.0
            while virtual_time < self.episode_duration and self._is_running:
               
                virtual_time += self.time_step
                
                action = self.agent.act(state)
                next_state, reward, delay, power, qos_violation = self.env.step(action)
                self.agent.remember(state, action, reward, next_state, qos_violation)
                
                episode_data["total_reward"] += reward
                episode_data["avg_delay"] += delay
                episode_data["total_energy"] += power * self.time_step  
                episode_data["qos_violations"] += int(qos_violation)
                episode_data["request_count"] += 1
                
                state = next_state
                
               
                if episode_data["request_count"] % 10 == 0:
                    self.agent.replay()
                
               
                if episode_data["request_count"] % 50 == 0:
                    self.stats_updated.emit(self.env.get_detailed_stats())
            
            if episode_data["request_count"] > 0:
                episode_data["avg_delay"] /= episode_data["request_count"]
                episode_data["end_time"] = datetime.now()
                episode_data["duration"] = (episode_data["end_time"] - episode_data["start_time"]).total_seconds()
            
            self.current_episode += 1
            self.episode_completed.emit(episode_data)
            self.stats_updated.emit(self.env.get_detailed_stats())
    
    def stop(self):
        self._is_running = False
        self.wait()


class MainWindow(QMainWindow):
   
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASM")
        self.setGeometry(100, 100, 1400, 900)
        
       
        self.env = None
        self.agent = None
        self.simulation_thread = None
        self.results = []
        
      
        self.init_ui()
        
    def init_ui(self):
       
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
     
        left_panel = QVBoxLayout()
        self.create_control_panel(left_panel)
        self.create_stats_panel(left_panel)
        main_layout.addLayout(left_panel, stretch=2)
        
        
        right_panel = QVBoxLayout()
        self.create_results_tabs(right_panel)
        main_layout.addLayout(right_panel, stretch=3)
        
    def create_stats_panel(self, layout):
       
        stats_group = QGroupBox("Текущая статистика")
        stats_layout = QFormLayout()
        
        self.stats_labels = {
            "time": QLabel("0.0 сек"),
            "avg_power": QLabel("0.0 Вт"),
            "active_time": QLabel("0.0%"),
            "requests": QLabel("0"),
            "qos_violations": QLabel("0 (0.0%)"),
            "avg_delay": QLabel("0.0 мс")
        }
        
        for name, label in self.stats_labels.items():
            stats_layout.addRow(f"{name.replace('_', ' ').title()}:", label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
    def update_stats_display(self, stats):
        
        elapsed = stats.get("simulation_duration", 0)
        self.stats_labels["time"].setText(f"{elapsed:.1f} сек")
        
        avg_power = stats.get("weighted_avg_power", 0)
        self.stats_labels["avg_power"].setText(f"{avg_power:.1f} Вт")
        
        active_percent = stats.get("time_percent", {}).get("Active", 0)
        self.stats_labels["active_time"].setText(f"{active_percent:.1f}%")
        
        requests = stats.get("total_requests", 0)
        violations = stats.get("qos_violations", 0)
        violation_percent = violations / requests * 100 if requests > 0 else 0
        self.stats_labels["requests"].setText(str(requests))
        self.stats_labels["qos_violations"].setText(
            f"{violations} ({violation_percent:.1f}%)"
        )
        
        avg_delay = stats.get("avg_delay", 0) * 1000  
        self.stats_labels["avg_delay"].setText(f"{avg_delay:.2f} мс")
        
    def create_control_panel(self, layout):
        
        control_group = QGroupBox("Параметры симуляции")
        control_layout = QFormLayout()
        
      
        self.traffic_combo = QComboBox()
        self.traffic_combo.addItems(CONFIG["traffic_profiles"])
        control_layout.addRow("Тип трафика:", self.traffic_combo)
        
       
        self.episodes_spin = QSpinBox()
        self.episodes_spin.setRange(1, 10000)
        self.episodes_spin.setValue(100)
        control_layout.addRow("Количество эпизодов:", self.episodes_spin)
        
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.001, 1.0)
        self.alpha_spin.setValue(0.1)
        self.alpha_spin.setSingleStep(0.01)
        control_layout.addRow("Скорость обучения (alpha):", self.alpha_spin)
        
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.1, 0.99)
        self.gamma_spin.setValue(0.95)
        self.gamma_spin.setSingleStep(0.01)
        control_layout.addRow("Коэффициент дисконтирования (gamma):", self.gamma_spin)
        
       
        self.start_button = QPushButton("Запустить симуляцию")
        self.start_button.clicked.connect(self.start_simulation)
        
        self.stop_button = QPushButton("Остановить")
        self.stop_button.clicked.connect(self.stop_simulation)
        self.stop_button.setEnabled(False)
        
        self.save_button = QPushButton("Сохранить результаты")
        self.save_button.clicked.connect(self.save_results)
        
        self.stats_button = QPushButton("Показать время по режимам")
        self.stats_button.clicked.connect(self.show_mode_stats)
        
       
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
      
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        
       
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.save_button)
        layout.addWidget(self.stats_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("Лог:"))
        layout.addWidget(self.log_text)
        
    def create_results_tabs(self, layout):
        
        self.tabs = QTabWidget()
        
      
        self.graph_tab = QWidget()
        graph_layout = QVBoxLayout(self.graph_tab)
        
        self.canvas_reward = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_delay = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_energy = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_qos = MplCanvas(self, width=5, height=4, dpi=100)
        self.canvas_modes = MplCanvas(self, width=5, height=4, dpi=100)
        
        graph_layout.addWidget(self.canvas_reward)
        graph_layout.addWidget(self.canvas_delay)
        graph_layout.addWidget(self.canvas_energy)
        graph_layout.addWidget(self.canvas_qos)
        graph_layout.addWidget(self.canvas_modes)
        
        self.tabs.addTab(self.graph_tab, "Графики")
        
       
        self.table_tab = QWidget()
        self.table_layout = QVBoxLayout(self.table_tab)
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.table_layout.addWidget(self.results_text)
        self.tabs.addTab(self.table_tab, "Результаты")
        
        
        self.agent_tab = QWidget()
        self.agent_layout = QVBoxLayout(self.agent_tab)
        self.agent_text = QTextEdit()
        self.agent_text.setReadOnly(True)
        self.agent_layout.addWidget(self.agent_text)
        self.tabs.addTab(self.agent_tab, "Состояние агента")
        
        layout.addWidget(self.tabs)
        
    def start_simulation(self):
       
        traffic_type = self.traffic_combo.currentText()
        episodes = self.episodes_spin.value()
        
        self.log_message(f"Запуск симуляции для {traffic_type}...")
        self.log_message(f"Параметры: {episodes} эпизодов, alpha={self.alpha_spin.value()}, gamma={self.gamma_spin.value()}")
        
      
        self.env = BSEnvironment(traffic_type)
        self.agent = DQNAgent(state_size=8, action_size=2)
        self.results = []
       
        self.progress_bar.setRange(0, episodes)
        self.progress_bar.setValue(0)
      
        self.simulation_thread = SimulationThread(self.env, self.agent, episodes)
        self.simulation_thread.episode_completed.connect(self.update_results)
        self.simulation_thread.stats_updated.connect(self.update_stats_display)
        self.simulation_thread.finished.connect(self.simulation_finished)
        
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.simulation_thread.start()

    def stop_simulation(self):
     
        if self.simulation_thread:
            self.simulation_thread.stop()
            self.log_message("Симуляция остановлена")

    def simulation_finished(self):
       
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.log_message("Симуляция завершена!")
        QMessageBox.information(self, "Завершено", "Симуляция успешно завершена!")
        
    def stop_simulation(self):
     
        if self.simulation_thread:
            self.simulation_thread.stop()
            self.log_message("Симуляция остановлена")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
        
    def update_results(self, episode_data):
      
        self.results.append(episode_data)
        self.progress_bar.setValue(len(self.results))
        
      
        self.update_plots()
        self.update_results_table()
        self.update_agent_info()
        
  
        self.log_message(
            f"Эпизод {len(self.results)}: "
            f"Награда={episode_data['total_reward']:.2f}, "
            f"Задержка={episode_data['avg_delay']:.6f}с, "
            f"Нарушения QoS={episode_data['qos_violations']}"
        )
        
   
        if len(self.results) == self.episodes_spin.value():
            self.simulation_completed()
    
    def simulation_completed(self):
    
        self.log_message("Симуляция успешно завершена!")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
      
        self.update_plots()
        self.update_results_table()
        self.update_agent_info()
        
     
        QMessageBox.information(self, "Завершено", "Симуляция успешно завершена!")
    
    def update_plots(self):
     
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
     
        for canvas in [self.canvas_reward, self.canvas_delay, 
                      self.canvas_energy, self.canvas_qos, self.canvas_modes]:
            canvas.axes.clear()
        
    
        df['total_reward'].plot(ax=self.canvas_reward.axes)
        self.canvas_reward.axes.set_title('Накопленная награда')
        self.canvas_reward.axes.set_xlabel('Эпизод')
        self.canvas_reward.axes.set_ylabel('Награда')
        self.canvas_reward.axes.grid(True)
        
    
        df['avg_delay'].plot(ax=self.canvas_delay.axes)
        self.canvas_delay.axes.axhline(
            y=CONFIG["qos_requirements"][self.traffic_combo.currentText()],
            color='r', linestyle='--',
            label='QoS предел'
        )
        self.canvas_delay.axes.set_title('Средняя задержка')
        self.canvas_delay.axes.set_xlabel('Эпизод')
        self.canvas_delay.axes.set_ylabel('Задержка (с)')
        self.canvas_delay.axes.legend()
        self.canvas_delay.axes.grid(True)
        
  
        df['total_energy'].plot(ax=self.canvas_energy.axes)
        self.canvas_energy.axes.set_title('Общее энергопотребление')
        self.canvas_energy.axes.set_xlabel('Эпизод')
        self.canvas_energy.axes.set_ylabel('Энергия (Дж)')
        self.canvas_energy.axes.grid(True)
        
      
        df['qos_violations'].plot(ax=self.canvas_qos.axes)
        self.canvas_qos.axes.set_title('Нарушения QoS')
        self.canvas_qos.axes.set_xlabel('Эпизод')
        self.canvas_qos.axes.set_ylabel('Количество нарушений')
        self.canvas_qos.axes.grid(True)
     
        if self.env:
            mode_stats = self.env.get_mode_time_stats()
            modes = list(mode_stats.keys())
            times = [val for val in mode_stats.values()]
            
            bars = self.canvas_modes.axes.bar(modes, times)
            for bar in bars:
                height = bar.get_height()
                self.canvas_modes.axes.text(bar.get_x() + bar.get_width()/2., height,
                                            f'{height:.1f}',
                                            ha='center', va='bottom')
            
            self.canvas_modes.axes.set_title('Распределение времени по режимам')
            self.canvas_modes.axes.set_xlabel('Режим')
            self.canvas_modes.axes.set_ylabel('Время (сек)')
            self.canvas_modes.axes.grid(True)
     
        for canvas in [self.canvas_reward, self.canvas_delay, 
                      self.canvas_energy, self.canvas_qos, self.canvas_modes]:
            canvas.draw()
    def update_results_table(self):
      
        if not self.results:
            return
        
        df = pd.DataFrame(self.results)
        summary = df.describe().to_string()
        self.results_text.setPlainText(
            f"Общие результаты ({len(self.results)} эпизодов):\n\n"
            f"{summary}\n\n"
            f"Последние 10 эпизодов:\n\n"
            f"{df.tail(10).to_string()}"
        )
    
    def update_agent_info(self):
   
        if not self.agent:
            return
        
        info = (
            f"Параметры агента:\n"
            f"Epsilon: {self.agent.epsilon:.4f}\n"
            f"Размер памяти: {len(self.agent.memory)}\n"
            f"Размер батча: {self.agent.batch_size}\n"
            f"Коэффициент дисконтирования: {self.agent.gamma}\n\n"
            f"Архитектура модели:\n"
            f"{self.agent.model}"
        )
        
        self.agent_text.setPlainText(info)
    
    def show_mode_stats(self):
     
        if not self.env:
            QMessageBox.warning(self, "Ошибка", "Сначала запустите симуляцию!")
            return
        
        time_stats = self.env.get_mode_time_stats()
        
   
        stats_text = "Время работы по режимам:\n"
        for mode, time_sec in time_stats.items():
            stats_text += f"- {mode}: {time_sec:.2f} сек\n"
        
      
        QMessageBox.information(self, "Статистика режимов", stats_text)
    
    def save_results(self):
     
        if not self.results:
            QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Сохранить результаты", "", "JSON Files (*.json)"
        )
        
        if filename:
            try:
                report = {
                    "config": CONFIG,
                    "parameters": {
                        "traffic_type": self.traffic_combo.currentText(),
                        "episodes": self.episodes_spin.value(),
                        "alpha": self.alpha_spin.value(),
                        "gamma": self.gamma_spin.value()
                    },
                    "results": self.results,
                    "mode_time_stats": self.env.get_mode_time_stats() if self.env else {},
                    "detailed_stats": self.env.get_detailed_stats() if self.env else {}
                }
                
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                
                self.log_message(f"Результаты сохранены в {filename}")
                QMessageBox.information(self, "Успех", "Результаты успешно сохранены")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def log_message(self, message):
      
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        self.log_text.verticalScrollBar().setValue(self.log_text.verticalScrollBar().maximum())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())       