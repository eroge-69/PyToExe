"""
NeuroSparse Transformer - Био-инспирированная энергоэффективная архитектура
Соответствует стандартам: PEP-8, SOLID, DRY
Версия: 1.2
"""

import os
import json
import random
from datetime import datetime
import torch
import torch.nn as nn
import torch.optim as optim
from transformers import AutoTokenizer
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton,
                            QVBoxLayout, QHBoxLayout, QWidget, QLabel, QProgressBar,
                            QFileDialog, QSlider, QSpinBox, QAction)
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# --- Ядро модели ---
class DynamicSparsityGate(nn.Module):
    """Динамический гейт разреженности (аналог нейромодуляторной системы)"""
    def __init__(self, dim: int, init_sparsity: float = 0.15):
        super().__init__()
        self.context_gate = nn.Linear(dim, 1, bias=False)
        self.sparsity_level = nn.Parameter(torch.tensor(init_sparsity))
       
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Генерация бинарной маски активации"""
        scores = self.context_gate(x).squeeze(-1)
        k = max(1, int(x.size(1) * torch.sigmoid(self.sparsity_level)))
        threshold = torch.topk(scores, k, dim=-1).values[:, -1:]
        return (scores > threshold).float()

class AstroNorm(nn.Module):
    """Астроцитарная нормализация (регуляция экстремальных значений)"""
    def __init__(self, dim: int, decay: float = 0.95):
        super().__init__()
        self.buffer = nn.Parameter(torch.zeros(dim))
        self.decay = nn.Parameter(torch.tensor(decay))
       
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Стабилизация входных данных с динамическим буфером"""
        mean = x.detach().mean(dim=1, keepdim=True)
        var = x.detach().var(dim=1, keepdim=True)
       
        # Обновление буфера с экспоненциальным затуханием
        self.buffer.data = self.decay * self.buffer + (1 - self.decay) * mean.squeeze()
       
        # Подавление экстремальных значений
        buffer_mask = (x - mean).abs() > self.buffer.abs()
        return torch.where(buffer_mask, mean, x) / (var + 1e-6).sqrt()

class SparseExpert(nn.Module):
    """Экспертная система с адаптивной разреженностью"""
    def __init__(self, dim: int, num_experts: int = 4):
        super().__init__()
        self.experts = nn.ModuleList([nn.Linear(dim, dim) for _ in range(num_experts)])
        self.gating = nn.Linear(dim, num_experts)
        self.sparsity_constraint = nn.Parameter(torch.tensor(0.8))
       
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Активация только наиболее релевантных экспертов"""
        gate_scores = self.gating(x)
        k = max(1, int(self.sparsity_constraint * len(self.experts)))
        topk_idx = torch.topk(gate_scores, k, dim=-1).indices
       
        output = torch.zeros_like(x)
        for i, expert in enumerate(self.experts):
            expert_mask = (topk_idx == i).any(dim=-1)
            output[expert_mask] += expert(x[expert_mask])
           
        return output

class NeuroSparseTransformer(nn.Module):
    """Основная модель NeuroSparse Transformer"""
    def __init__(self, vocab_size: int, dim: int = 128, num_layers: int = 4, num_ensembles: int = 4):
        super().__init__()
        self.dim = dim
        self.embedding = nn.Embedding(vocab_size, dim)
        self.layers = nn.ModuleList([self._build_layer(dim, num_ensembles) for _ in range(num_layers)])
        self.norm = nn.LayerNorm(dim)
        self.head = nn.Linear(dim, vocab_size)
       
    def _build_layer(self, dim: int, num_ensembles: int) -> nn.ModuleDict:
        """Конструирование слоя с био-инспирированными компонентами"""
        return nn.ModuleDict({
            'attn_norm': AstroNorm(dim),
            'sparse_gate': DynamicSparsityGate(dim),
            'expert_ffn': SparseExpert(dim, num_experts=num_ensembles)
        })
       
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Прямой проход с разреженной активацией"""
        x = self.embedding(x)
       
        for layer in self.layers:
            # Астроцитарная нормализация
            x = layer['attn_norm'](x)
           
            # Нейромодуляторное гейтирование
            mask = layer['sparse_gate'](x)
            x = x * mask.unsqueeze(-1)
           
            # Экспертная обработка
            x = layer['expert_ffn'](x)
           
        return self.head(self.norm(x))

# --- Механизмы обучения ---
def neuro_consolidation(model: nn.Module):
    """Процедура консолидации знаний через 'сон'"""
    model.eval()
    for module in model.modules():
        if isinstance(module, SparseExpert):
            # Стохастическая рекомбинация экспертов
            for i in range(len(module.experts)):
                j = random.choice([idx for idx in range(len(module.experts)) if idx != i])
                alpha = random.uniform(0.3, 0.7)
               
                with torch.no_grad():
                    for param_i, param_j in zip(module.experts[i].parameters(),
                                                module.experts[j].parameters()):
                        # Перекрестное смешивание весов
                        mix = alpha * param_i + (1 - alpha) * param_j
                        param_i.copy_(mix)
                        param_j.copy_(mix)

class TextProcessor:
    """Обработчик текста с токенизацией"""
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("gpt2")
        self.tokenizer.add_special_tokens({'pad_token': '[PAD]'})
       
    @property
    def vocab_size(self) -> int:
        return len(self.tokenizer)
   
    def encode(self, text: str) -> torch.Tensor:
        return self.tokenizer.encode(text, return_tensors="pt",
                                    max_length=256, truncation=True, padding=True)
   
    def decode(self, tokens: torch.Tensor) -> str:
        return self.tokenizer.decode(tokens.squeeze().tolist(), skip_special_tokens=True)

# --- GUI и асинхронные операции ---
class TrainingThread(QThread):
    """Асинхронный поток для обучения модели"""
    progress_updated = pyqtSignal(int)
    training_completed = pyqtSignal(str)
    status_updated = pyqtSignal(str)

    def __init__(self, model: nn.Module, processor: TextProcessor, text_data: str):
        super().__init__()
        self.model = model
        self.processor = processor
        self.text_data = text_data
        self.is_running = True

    def run(self):
        try:
            inputs = self.processor.encode(self.text_data)
            dataset = torch.utils.data.TensorDataset(inputs)
            loader = torch.utils.data.DataLoader(dataset, batch_size=2, shuffle=True)
           
            optimizer = optim.AdamW(self.model.parameters(), lr=1e-4)
            criterion = nn.CrossEntropyLoss(ignore_index=self.processor.tokenizer.pad_token_id)
           
            total_epochs = 10
            for epoch in range(total_epochs):
                if not self.is_running:
                    return
               
                self.status_updated.emit(f"Эпоха {epoch+1}/{total_epochs}")
                epoch_loss = 0.0
               
                for batch in loader:
                    optimizer.zero_grad()
                    input_ids = batch[0]
                   
                    # Усеченное обучение языковой модели
                    outputs = self.model(input_ids[:, :-1])
                    loss = criterion(outputs.view(-1, self.model.head.out_features),
                                    input_ids[:, 1:].contiguous().view(-1))
                   
                    loss.backward()
                    optimizer.step()
                    epoch_loss += loss.item()
               
                # Консолидация каждые 2 эпохи
                if epoch % 2 == 0:
                    self.status_updated.emit("Консолидация знаний...")
                    neuro_consolidation(self.model)
               
                self.progress_updated.emit(int((epoch+1) / total_epochs * 100))
           
            self.training_completed.emit(f"Обучение завершено | Loss: {epoch_loss/len(loader):.4f}")
        except Exception as e:
            self.training_completed.emit(f"Ошибка: {str(e)}")

    def stop(self):
        self.is_running = False

class NeuroSparseApp(QMainWindow):
    """Главное приложение с графическим интерфейсом"""
    def __init__(self):
        super().__init__()
        self.model = None
        self.processor = TextProcessor()
        self.training_thread = None
        self._init_ui()
       
    def _init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle("NeuroSparse Transformer")
        self.setGeometry(100, 100, 1000, 700)
       
        # Центральный виджет и макет
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
       
        # Левая панель (Обучение)
        train_panel = QVBoxLayout()
        train_panel.addWidget(QLabel("Данные для обучения:"))
       
        self.train_input = QTextEdit()
        self.train_input.setPlaceholderText("Введите текст для обучения...")
        self.train_input.setFont(QFont("Consolas", 10))
        train_panel.addWidget(self.train_input)
       
        self.train_btn = QPushButton("Обучить модель")
        self.train_btn.clicked.connect(self.start_training)
        train_panel.addWidget(self.train_btn)
       
        self.progress_bar = QProgressBar()
        train_panel.addWidget(self.progress_bar)
       
        self.status_label = QLabel("Готов к обучению")
        train_panel.addWidget(self.status_label)
       
        # Правая панель (Взаимодействие)
        interact_panel = QVBoxLayout()
        interact_panel.addWidget(QLabel("Вопрос:"))
       
        self.question_input = QTextEdit()
        self.question_input.setPlaceholderText("Введите ваш вопрос...")
        self.question_input.setFont(QFont("Consolas", 10))
        interact_panel.addWidget(self.question_input)
       
        # Панель параметров генерации
        param_layout = QHBoxLayout()
        param_layout.addWidget(QLabel("Температура:"))
       
        self.temp_slider = QSlider(Qt.Horizontal)
        self.temp_slider.setRange(10, 100)
        self.temp_slider.setValue(70)
        param_layout.addWidget(self.temp_slider)
       
        param_layout.addWidget(QLabel("Top-K:"))
        self.topk_spin = QSpinBox()
        self.topk_spin.setRange(1, 500)
        self.topk_spin.setValue(50)
        param_layout.addWidget(self.topk_spin)
       
        interact_panel.addLayout(param_layout)
       
        self.ask_btn = QPushButton("Задать вопрос")
        self.ask_btn.clicked.connect(self.ask_question)
        interact_panel.addWidget(self.ask_btn)
       
        interact_panel.addWidget(QLabel("Ответ:"))
        self.answer_output = QTextEdit()
        self.answer_output.setReadOnly(True)
        self.answer_output.setFont(QFont("Consolas", 10))
        interact_panel.addWidget(self.answer_output)
       
        # Объединение панелей
        main_layout.addLayout(train_panel, 50)
        main_layout.addLayout(interact_panel, 50)
       
        # Настройка главного окна
        self.setCentralWidget(central_widget)
        self._create_toolbar()
        self._create_statusbar()
       
    def _create_toolbar(self):
        """Создание панели инструментов"""
        toolbar = self.addToolBar("Tools")
       
        # Действия инструментов
        self.save_action = QAction("💾 Сохранить", self)
        self.save_action.triggered.connect(self.save_model)
       
        self.load_action = QAction("📂 Загрузить", self)
        self.load_action.triggered.connect(self.load_model)
       
        self.consolidate_action = QAction("🌙 Консолидировать", self)
        self.consolidate_action.triggered.connect(self.consolidate_model)
       
        # Добавление в панель
        toolbar.addAction(self.save_action)
        toolbar.addAction(self.load_action)
        toolbar.addAction(self.consolidate_action)
       
    def _create_statusbar(self):
        """Создание строки состояния"""
        self.statusBar().showMessage("Система готова")
       
    def start_training(self):
        """Запуск процесса обучения"""
        if self.training_thread and self.training_thread.isRunning():
            return
           
        text_data = self.train_input.toPlainText()
        if len(text_data) < 500:
            self.status_label.setText("Требуется минимум 500 символов")
            return
           
        # Инициализация модели
        self.model = NeuroSparseTransformer(self.processor.vocab_size)
       
        # Настройка и запуск потока обучения
        self.training_thread = TrainingThread(self.model, self.processor, text_data)
        self.training_thread.progress_updated.connect(self.progress_bar.setValue)
        self.training_thread.training_completed.connect(self.status_label.setText)
        self.training_thread.status_updated.connect(self.statusBar().showMessage)
        self.training_thread.start()
       
        # Блокировка интерфейса на время обучения
        self.train_btn.setEnabled(False)
        self.training_thread.finished.connect(lambda: self.train_btn.setEnabled(True))
       
    def ask_question(self):
        """Генерация ответа на вопрос"""
        if not self.model:
            self.answer_output.setText("Сначала обучите модель!")
            return
           
        question = self.question_input.toPlainText().strip()
        if not question:
            self.answer_output.setText("Введите вопрос")
            return
           
        try:
            # Кодирование вопроса
            input_ids = self.processor.encode(question)
           
            # Генерация ответа
            output_ids = self._generate_text(
                input_ids,
                max_length=100,
                temperature=self.temp_slider.value() / 100,
                top_k=self.topk_spin.value()
            )
           
            # Декодирование и вывод
            answer = self.processor.decode(output_ids)
            self.answer_output.setText(f"Ответ: {answer}")
        except Exception as e:
            self.answer_output.setText(f"Ошибка: {str(e)}")
           
    def _generate_text(self, input_ids: torch.Tensor, max_length: int = 100,
                      temperature: float = 0.7, top_k: int = 50) -> torch.Tensor:
        """Генерация текста с заданными параметрами"""
        self.model.eval()
        generated = input_ids.clone()
       
        with torch.no_grad():
            for _ in range(max_length):
                outputs = self.model(generated)
                logits = outputs[:, -1, :] / temperature
               
                # Top-k фильтрация
                values, indices = torch.topk(logits, top_k)
                probs = torch.softmax(values, dim=-1)
               
                # Стохастическая выборка
                next_token = indices[0, torch.multinomial(probs[0], 1)]
                generated = torch.cat([generated, next_token.unsqueeze(0)], dim=-1)
               
                # Критерий остановки
                if next_token.item() == self.processor.tokenizer.eos_token_id:
                    break
                   
        return generated
   
    def save_model(self):
        """Сохранение модели на диск"""
        if not self.model:
            return
           
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить модель", "", "Model Files (*.pt)", options=options
        )
       
        if not file_path:
            return
           
        try:
            # Подготовка данных для сохранения
            state = {
                "model_state": self.model.state_dict(),
                "config": {
                    "dim": self.model.dim,
                    "vocab_size": self.model.head.out_features,
                    "num_layers": len(self.model.layers)
                },
                "tokenizer": self.processor.tokenizer.get_vocab()
            }
           
            torch.save(state, file_path)
            self.statusBar().showMessage(f"Модель сохранена: {os.path.basename(file_path)}")
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка сохранения: {str(e)}")
   
    def load_model(self):
        """Загрузка модели с диска"""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Загрузить модель", "", "Model Files (*.pt)", options=options
        )
       
        if not file_path:
            return
           
        try:
            # Загрузка состояния
            state = torch.load(file_path, map_location=torch.device('cpu'))
            config = state["config"]
           
            # Инициализация модели
            self.model = NeuroSparseTransformer(
                vocab_size=config["vocab_size"],
                dim=config["dim"],
                num_layers=config["num_layers"]
            )
            self.model.load_state_dict(state["model_state"])
           
            # Восстановление токенизатора
            self.processor.tokenizer = AutoTokenizer.from_pretrained("gpt2")
            self.processor.tokenizer.add_tokens(list(state["tokenizer"].keys()))
           
            self.statusBar().showMessage(f"Модель загружена: {os.path.basename(file_path)}")
        except Exception as e:
            self.statusBar().showMessage(f"Ошибка загрузки: {str(e)}")
   
    def consolidate_model(self):
        """Принудительная консолидация модели"""
        if self.model:
            neuro_consolidation(self.model)
            self.statusBar().showMessage("Консолидация знаний выполнена!")
           
    def closeEvent(self, event):
        """Обработка закрытия приложения"""
        if self.training_thread and self.training_thread.isRunning():
            self.training_thread.stop()
            self.training_thread.wait()
        event.accept()

if __name__ == "__main__":
    app = QApplication([])
    app.setStyle("Fusion")  # Современный стиль интерфейса
    window = NeuroSparseApp()
    window.show()
    app.exec() 