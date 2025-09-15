import numpy as np
import matplotlib.pyplot as plt
import logging
import unittest
from typing import Callable, Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod
import time
from scipy import signal as scipy_signal
from scipy.integrate import solve_ivp
from control import NonlinearIOSystem, tf, ss, lqr  # Requires: pip install control
from sklearn.neural_network import MLPRegressor  # Requires: pip install scikit-learn
import warnings
warnings.filterwarnings('ignore')

# ========================
# 1. НАСТРОЙКА ЛОГИРОВАНИЯ
# ========================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("control_system.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ========================
# 2. БАЗОВЫЕ КЛАССЫ И СТРУКТУРЫ ДАННЫХ
# ========================
@dataclass
class ControlSignal:
    """Структура данных для хранения сигнала управления."""
    time: float
    setpoint: float
    measured_value: float
    filtered_value: float
    control_output: float
    pid_components: Dict[str, float]
    system_state: np.ndarray
    is_saturated: bool

class SignalFilter(ABC):
    """Абстрактный базовый класс для фильтров."""
    @abstractmethod
    def update(self, new_value: float) -> float:
        pass

    @abstractmethod
    def reset(self):
        pass

# ========================
# 3. РЕАЛИЗАЦИЯ ФИЛЬТРОВ
# ========================
class LowPassFilter(SignalFilter):
    """Простой цифровой ФНЧ первого порядка."""
    def __init__(self, cutoff_freq: float, dt: float):
        self.alpha = dt / (1.0 / (2 * np.pi * cutoff_freq) + dt) if cutoff_freq > 0 else 1.0
        self.last_output = 0.0

    def update(self, new_value: float) -> float:
        self.last_output = self.alpha * new_value + (1 - self.alpha) * self.last_output
        return self.last_output

    def reset(self):
        self.last_output = 0.0

class KalmanFilter1D:
    """Одномерный фильтр Калмана для оценки состояния."""
    def __init__(self, process_variance: float, measurement_variance: float, initial_value: float = 0.0):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimate = initial_value
        self.error_covariance = 1.0

    def update(self, measurement: float) -> float:
        # Предсказание
        predicted_estimate = self.estimate
        predicted_error_covariance = self.error_covariance + self.process_variance

        # Обновление
        kalman_gain = predicted_error_covariance / (predicted_error_covariance + self.measurement_variance)
        self.estimate = predicted_estimate + kalman_gain * (measurement - predicted_estimate)
        self.error_covariance = (1 - kalman_gain) * predicted_error_covariance

        return self.estimate

    def reset(self, initial_value: float = 0.0):
        self.estimate = initial_value
        self.error_covariance = 1.0

class ExtendedKalmanFilter:
    """Расширенный фильтр Калмана для нелинейных систем."""
    def __init__(self, f: Callable, h: Callable, F_jacobian: Callable, H_jacobian: Callable,
                 Q: np.ndarray, R: np.ndarray, x0: np.ndarray, P0: np.ndarray):
        self.f = f          # Нелинейная функция перехода состояния
        self.h = h          # Нелинейная функция измерения
        self.F_jacobian = F_jacobian  # Якобиан f
        self.H_jacobian = H_jacobian  # Якобиан h
        self.Q = Q          # Ковариация шума процесса
        self.R = R          # Ковариация шума измерения
        self.x = x0.copy()  # Оценка состояния
        self.P = P0.copy()  # Ковариация ошибки оценки

    def predict(self):
        # Предсказание состояния
        self.x = self.f(self.x)
        F = self.F_jacobian(self.x)
        self.P = F @ self.P @ F.T + self.Q

    def update(self, z: np.ndarray):
        # Обновление на основе измерения
        H = self.H_jacobian(self.x)
        y = z - self.h(self.x)  # Инновация
        S = H @ self.P @ H.T + self.R
        K = self.P @ H.T @ np.linalg.inv(S)  # Коэффициент Калмана
        self.x = self.x + K @ y
        I = np.eye(self.P.shape[0])
        self.P = (I - K @ H) @ self.P

    def get_state(self) -> np.ndarray:
        return self.x.copy()

# ========================
# 4. РАСШИРЕННЫЙ ПИД-РЕГУЛЯТОР
# ========================
class AdvancedPID:
    """Расширенный цифровой ПИД-регулятор с множеством функций."""
    def __init__(self, Kp: float, Ki: float, Kd: float, dt: float, setpoint: float = 0.0,
                 output_limits: Tuple[float, float] = (0.0, 100.0),
                 filter_derivative: bool = True, derivative_cutoff_freq: float = 10.0,
                 anti_windup: str = 'clamping', anti_windup_K: float = 1.0,
                 setpoint_weighting: bool = True, beta: float = 0.5, gamma: float = 0.0):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.dt = dt
        self.setpoint = setpoint
        self.output_min, self.output_max = output_limits
        self.anti_windup_method = anti_windup
        self.anti_windup_K = anti_windup_K
        self.setpoint_weighting = setpoint_weighting
        self.beta = beta  # вес уставки для P-составляющей
        self.gamma = gamma  # вес уставки для D-составляющей

        # Внутренние состояния
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        self.last_output = 0.0
        self.is_saturated = False

        # Фильтр для производной составляющей
        self.filter_derivative = filter_derivative
        if self.filter_derivative:
            self.derivative_filter = LowPassFilter(derivative_cutoff_freq, dt)
        else:
            self.derivative_filter = None

    def update(self, measured_value: float, external_setpoint: Optional[float] = None) -> float:
        if external_setpoint is not None:
            self.setpoint = external_setpoint

        # Вычисление ошибки
        error = self.setpoint - measured_value

        # Пропорциональная составляющая с весом уставки
        if self.setpoint_weighting:
            P_error = self.beta * self.setpoint - measured_value
        else:
            P_error = error
        P = self.Kp * P_error

        # Интегральная составляющая
        self.integral += error * self.dt

        # Анти-виндап (Clamping или Back-Calculation)
        if self.anti_windup_method == 'clamping':
            # Ограничение интегратора
            unsaturated_output = P + self.Ki * self.integral + self._calculate_derivative(measured_value)
            if unsaturated_output > self.output_max:
                self.integral -= error * self.dt  # Откатываем интегратор
                self.is_saturated = True
            elif unsaturated_output < self.output_min:
                self.integral -= error * self.dt
                self.is_saturated = True
            else:
                self.is_saturated = False
        elif self.anti_windup_method == 'back_calculation':
            # Back-Calculation
            unsaturated_output = P + self.Ki * self.integral + self._calculate_derivative(measured_value)
            saturated_output = np.clip(unsaturated_output, self.output_min, self.output_max)
            if saturated_output != unsaturated_output:
                # Корректируем интегратор
                back_calc_error = (saturated_output - unsaturated_output) * self.anti_windup_K
                self.integral += back_calc_error * self.dt
                self.is_saturated = True
            else:
                self.is_saturated = False

        I = self.Ki * self.integral

        # Дифференциальная составляющая
        D = self._calculate_derivative(measured_value)

        # Суммирование
        output = P + I + D

        # Ограничение выхода
        self.last_output = np.clip(output, self.output_min, self.output_max)

        # Сохранение предыдущей ошибки
        self.prev_error = error

        return self.last_output

    def _calculate_derivative(self, measured_value: float) -> float:
        # Вычисление производной
        derivative = -(measured_value - self.prev_error) / self.dt if self.prev_error is not None else 0.0
        self.prev_error = measured_value  # Для следующей итерации производной

        # Фильтрация производной
        if self.filter_derivative and self.derivative_filter:
            derivative = self.derivative_filter.update(derivative)

        # Вес уставки для D-составляющей
        if self.setpoint_weighting:
            # Если уставка меняется, её производная тоже влияет (но обычно gamma=0)
            D_component = -self.Kd * derivative  # Обычно gamma=0, чтобы избежать "дерганья" на изменении уставки
        else:
            D_component = -self.Kd * derivative

        return D_component

    def reset(self):
        """Сброс внутреннего состояния регулятора."""
        self.integral = 0.0
        self.prev_error = 0.0
        self.prev_derivative = 0.0
        self.last_output = 0.0
        self.is_saturated = False
        if self.filter_derivative:
            self.derivative_filter.reset()

    def get_components(self) -> Dict[str, float]:
        """Возвращает текущие значения P, I, D компонент."""
        return {
            'P': self.Kp * (self.beta * self.setpoint - self.prev_error) if self.setpoint_weighting else self.Kp * (self.setpoint - self.prev_error),
            'I': self.Ki * self.integral,
            'D': self._calculate_derivative(self.prev_error) if hasattr(self, 'prev_error') else 0.0
        }

# ========================
# 5. АДАПТИВНЫЙ НЕЙРОННЫЙ ПИД
# ========================
class NeuralAdaptivePID:
    """Адаптивный ПИД-регулятор с настройкой коэффициентов через нейронную сеть."""
    def __init__(self, dt: float, setpoint: float = 0.0, output_limits: Tuple[float, float] = (0.0, 100.0)):
        self.dt = dt
        self.setpoint = setpoint
        self.output_min, self.output_max = output_limits
        self.base_pid = AdvancedPID(Kp=1.0, Ki=0.1, Kd=0.01, dt=dt, setpoint=setpoint, output_limits=output_limits)
        self.nn_model = MLPRegressor(hidden_layer_sizes=(10, 5), max_iter=500, random_state=42)
        self.is_trained = False
        self.history = {'errors': [], 'outputs': [], 'states': []}

    def _extract_features(self, error: float, prev_error: float, integral: float) -> np.ndarray:
        """Извлекает признаки для нейронной сети."""
        derivative = (error - prev_error) / self.dt if prev_error is not None else 0.0
        return np.array([[error, derivative, integral, abs(error), error**2]])

    def update(self, measured_value: float, system_state: Optional[np.ndarray] = None) -> float:
        error = self.setpoint - measured_value

        # Используем нейросеть для адаптации коэффициентов, если она обучена
        if self.is_trained and len(self.history['errors']) > 10:
            features = self._extract_features(
                error, self.history['errors'][-1] if self.history['errors'] else None, self.base_pid.integral
            )
            try:
                # Предсказываем поправки к коэффициентам
                delta_gains = self.nn_model.predict(features)[0]
                # Применяем адаптивные коэффициенты
                self.base_pid.Kp = max(0.1, 1.0 + delta_gains[0])
                self.base_pid.Ki = max(0.01, 0.1 + delta_gains[1])
                self.base_pid.Kd = max(0.0, 0.01 + delta_gains[2])
            except Exception as e:
                logger.warning(f"Ошибка адаптации НС: {e}")

        # Обновляем базовый ПИД
        output = self.base_pid.update(measured_value)

        # Сохраняем историю для обучения
        self.history['errors'].append(error)
        self.history['outputs'].append(output)
        if system_state is not None:
            self.history['states'].append(system_state)

        return output

    def train_online(self, target_performance: float = 0.1):
        """Онлайн-обучение нейронной сети на основе истории ошибок."""
        if len(self.history['errors']) < 20:
            return

        # Готовим данные: признаки и целевые значения (поправки к коэффициентам)
        X = []
        y = []

        for i in range(10, len(self.history['errors'])-1):
            features = self._extract_features(
                self.history['errors'][i], self.history['errors'][i-1], self.base_pid.Ki * sum(self.history['errors'][:i+1]) * self.dt
            )
            # Целевая метка: как нужно было изменить коэффициенты, чтобы уменьшить ошибку на следующем шаге
            next_error = self.history['errors'][i+1]
            current_error = self.history['errors'][i]

            # Эвристика: если ошибка уменьшилась, текущие коэффициенты были хороши (поправка ~0)
            # Если ошибка увеличилась, нужны поправки
            if abs(next_error) < abs(current_error) * 0.9:
                delta_gains = [0.0, 0.0, 0.0]
            else:
                # Простая эвристика для генерации целевых значений
                delta_Kp = 0.1 if abs(next_error) > abs(current_error) else -0.05
                delta_Ki = 0.01 if abs(next_error) > abs(current_error) else -0.005
                delta_Kd = 0.005 if abs(next_error) > abs(current_error) else -0.002
                delta_gains = [delta_Kp, delta_Ki, delta_Kd]

            X.append(features.flatten())
            y.append(delta_gains)

        if len(X) > 5:
            X = np.array(X)
            y = np.array(y)
            try:
                self.nn_model.fit(X, y)
                self.is_trained = True
                logger.info("Нейронная сеть успешно дообучена.")
            except Exception as e:
                logger.error(f"Ошибка обучения НС: {e}")

    def reset(self):
        self.base_pid.reset()
        self.history = {'errors': [], 'outputs': [], 'states': []}
        self.is_trained = False

# ========================
# 6. МОДЕЛЬНОЕ ПРЕДИКТИВНОЕ УПРАВЛЕНИЕ (MPC)
# ========================
class SimpleMPC:
    """Простая реализация MPC для линейной системы."""
    def __init__(self, A: np.ndarray, B: np.ndarray, C: np.ndarray, Q: np.ndarray, R: np.ndarray,
                 prediction_horizon: int, control_horizon: int, dt: float,
                 input_constraints: Tuple[float, float]):
        self.A = A
        self.B = B
        self.C = C
        self.Q = Q
        self.R = R
        self.Np = prediction_horizon
        self.Nc = control_horizon
        self.dt = dt
        self.u_min, self.u_max = input_constraints
        self.nx = A.shape[0]
        self.nu = B.shape[1]
        self.ny = C.shape[0]

    def _build_mpc_matrices(self) -> Tuple[np.ndarray, np.ndarray]:
        """Строит матрицы для квадратичной задачи MPC."""
        # Предварительные вычисления
        A_tilde = np.vstack([self.C @ np.linalg.matrix_power(self.A, i+1) for i in range(self.Np)])
        B_tilde = np.zeros((self.Np * self.ny, self.Nc * self.nu))

        for i in range(self.Np):
            for j in range(self.Nc):
                if j <= i:
                    power = i - j
                    B_tilde[i*self.ny:(i+1)*self.ny, j*self.nu:(j+1)*self.nu] = self.C @ np.linalg.matrix_power(self.A, power) @ self.B
                else:
                    B_tilde[i*self.ny:(i+1)*self.ny, j*self.nu:(j+1)*self.nu] = 0

        Q_tilde = np.kron(np.eye(self.Np), self.Q)
        R_tilde = np.kron(np.eye(self.Nc), self.R)

        return A_tilde, B_tilde, Q_tilde, R_tilde

    def compute_control(self, x0: np.ndarray, ref: np.ndarray) -> float:
        """Вычисляет оптимальное управляющее воздействие."""
        try:
            from cvxopt import matrix, solvers  # Requires: pip install cvxopt
            solvers.options['show_progress'] = False
        except ImportError:
            logger.error("CVXOPT не установлен. MPC недоступен.")
            return 0.0

        A_tilde, B_tilde, Q_tilde, R_tilde = self._build_mpc_matrices()

        # Вектор ссылки
        r = np.tile(ref, self.Np)

        # Формулировка QP: min 0.5*u^T*H*u + f^T*u
        H = 2 * (B_tilde.T @ Q_tilde @ B_tilde + R_tilde)
        f = 2 * B_tilde.T @ Q_tilde @ (A_tilde @ x0 - r)

        # Ограничения: G*u <= h
        # Ограничения на вход
        G_upper = np.eye(self.Nc * self.nu)
        G_lower = -np.eye(self.Nc * self.nu)
        G = np.vstack([G_upper, G_lower])
        h_upper = np.full(self.Nc * self.nu, self.u_max)
        h_lower = np.full(self.Nc * self.nu, -self.u_min)
        h = np.hstack([h_upper, h_lower])

        # Решение QP
        P = matrix(H)
        q = matrix(f)
        G_mat = matrix(G)
        h_mat = matrix(h)

        try:
            solution = solvers.qp(P, q, G_mat, h_mat)
            if solution['status'] == 'optimal':
                u_opt = np.array(solution['x']).flatten()
                # Возвращаем первое управляющее воздействие
                return u_opt[0] if self.nu == 1 else u_opt[0:self.nu]
            else:
                logger.warning("QP не сошлось.")
                return 0.0
        except Exception as e:
            logger.error(f"Ошибка решения QP: {e}")
            return 0.0

# ========================
# 7. МОДЕЛИ СИСТЕМ
# ========================
class SystemModel(ABC):
    """Абстрактный базовый класс для моделей систем."""
    @abstractmethod
    def update(self, u: float, dt: float) -> float:
        pass

    @abstractmethod
    def get_state(self) -> np.ndarray:
        pass

    @abstractmethod
    def reset(self):
        pass

class ThermalSystem(SystemModel):
    """Модель тепловой системы (нагреватель + охлаждение)."""
    def __init__(self, ambient_temp: float = 20.0, tau_heating: float = 50.0, tau_cooling: float = 100.0):
        self.ambient_temp = ambient_temp
        self.tau_heating = tau_heating
        self.tau_cooling = tau_cooling
        self.current_temp = ambient_temp
        self.last_u = 0.0

    def update(self, u: float, dt: float) -> float:
        # u в диапазоне [0, 100] - мощность нагрева
        heating_effect = (u / 100.0) * (100.0 - self.current_temp) / self.tau_heating
        cooling_effect = (self.ambient_temp - self.current_temp) / self.tau_cooling
        dT = (heating_effect + cooling_effect) * dt
        self.current_temp += dT
        self.last_u = u
        return self.current_temp

    def get_state(self) -> np.ndarray:
        return np.array([self.current_temp, self.last_u])

    def reset(self):
        self.current_temp = self.ambient_temp
        self.last_u = 0.0

class NonlinearMotorSystem(SystemModel):
    """Нелинейная модель двигателя постоянного тока с трением."""
    def __init__(self, J: float = 0.01, b: float = 0.1, K: float = 0.05, R: float = 0.5, L: float = 0.01):
        self.J = J  # Момент инерции
        self.b = b  # Коэффициент трения
        self.K = K  # Константа двигателя
        self.R = R  # Сопротивление
        self.L = L  # Индуктивность
        self.omega = 0.0  # Угловая скорость
        self.i = 0.0      # Ток
        self.last_u = 0.0 # Напряжение

    def _dynamics(self, t, state, u):
        omega, i = state
        domega_dt = (self.K * i - self.b * omega) / self.J
        di_dt = (u - self.R * i - self.K * omega) / self.L
        return [domega_dt, di_dt]

    def update(self, u: float, dt: float) -> float:
        # Решаем систему ОДУ на шаге dt
        sol = solve_ivp(self._dynamics, [0, dt], [self.omega, self.i], args=(u,), method='RK45')
        self.omega, self.i = sol.y[:, -1]
        self.last_u = u
        return self.omega

    def get_state(self) -> np.ndarray:
        return np.array([self.omega, self.i, self.last_u])

    def reset(self):
        self.omega = 0.0
        self.i = 0.0
        self.last_u = 0.0

# ========================
# 8. СУПЕРВАЙЗЕР УПРАВЛЕНИЯ
# ========================
class ControlSupervisor:
    """Супервайзер, управляющий выбором стратегии управления."""
    def __init__(self, system_model: SystemModel, dt: float, setpoint: float):
        self.system = system_model
        self.dt = dt
        self.setpoint = setpoint

        # Инициализация контроллеров
        self.pid_controller = AdvancedPID(Kp=2.0, Ki=0.1, Kd=0.5, dt=dt, setpoint=setpoint)
        self.neural_pid = NeuralAdaptivePID(dt=dt, setpoint=setpoint)
        # Для MPC нужна линейная модель. Создадим упрощенную для ThermalSystem.
        if isinstance(system_model, ThermalSystem):
            # Линейная аппроксимация вокруг рабочей точки
            A = np.array([[-1.0/(system_model.tau_cooling)]])
            B = np.array([[1.0/(system_model.tau_heating)]])
            C = np.array([[1.0]])
            Q = np.array([[1.0]])
            R = np.array([[0.1]])
            self.mpc_controller = SimpleMPC(A, B, C, Q, R, prediction_horizon=10, control_horizon=3, dt=dt, input_constraints=(0.0, 100.0))
        else:
            self.mpc_controller = None

        self.active_controller = "PID"  # "PID", "NeuralPID", "MPC"
        self.history: List[ControlSignal] = []
        self.kalman_filter = KalmanFilter1D(process_variance=0.1, measurement_variance=0.5, initial_value=setpoint)

    def switch_controller(self, controller_name: str):
        """Переключение активного контроллера."""
        if controller_name in ["PID", "NeuralPID", "MPC"]:
            if controller_name == "MPC" and self.mpc_controller is None:
                logger.warning("MPC недоступен для данной модели системы.")
                return
            self.active_controller = controller_name
            logger.info(f"Переключено на контроллер: {controller_name}")
        else:
            logger.error(f"Неизвестный контроллер: {controller_name}")

    def step(self, noisy_measurement: float) -> Tuple[float, ControlSignal]:
        """Один шаг управления."""
        # Фильтрация измерения
        filtered_value = self.kalman_filter.update(noisy_measurement)

        # Выбор и вызов контроллера
        if self.active_controller == "PID":
            control_output = self.pid_controller.update(filtered_value)
        elif self.active_controller == "NeuralPID":
            system_state = self.system.get_state()
            control_output = self.neural_pid.update(filtered_value, system_state)
            # Онлайн обучение НС
            if len(self.neural_pid.history['errors']) % 20 == 0:
                self.neural_pid.train_online()
        elif self.active_controller == "MPC" and self.mpc_controller:
            # Получаем текущее состояние (для термальной системы - это температура)
            x0 = np.array([filtered_value - self.system.ambient_temp])  # Относительно окружающей среды
            ref = np.array([self.setpoint - self.system.ambient_temp])
            control_output = self.mpc_controller.compute_control(x0, ref)
            # Ограничиваем выход, так как MPC может выдать значение вне [0,100]
            control_output = np.clip(control_output, 0.0, 100.0)
        else:
            control_output = 0.0

        # Обновление модели системы
        actual_value = self.system.update(control_output, self.dt)

        # Создание записи истории
        signal_record = ControlSignal(
            time=len(self.history) * self.dt,
            setpoint=self.setpoint,
            measured_value=noisy_measurement,
            filtered_value=filtered_value,
            control_output=control_output,
            pid_components=self.pid_controller.get_components() if self.active_controller == "PID" else {},
            system_state=self.system.get_state(),
            is_saturated=self.pid_controller.is_saturated if self.active_controller == "PID" else False
        )
        self.history.append(signal_record)

        return control_output, signal_record

    def run_simulation(self, steps: int, noise_std: float = 1.0) -> List[ControlSignal]:
        """Запуск полной симуляции."""
        logger.info(f"Запуск симуляции на {steps} шагов с контроллером {self.active_controller}")
        self.history.clear()

        for step in range(steps):
            # Получаем "реальное" значение от системы
            actual_value = self.system.current_temp if hasattr(self.system, 'current_temp') else self.system.omega
            # Добавляем шум к измерению
            noisy_measurement = actual_value + np.random.normal(0, noise_std)
            # Выполняем шаг управления
            _, _ = self.step(noisy_measurement)

        logger.info("Симуляция завершена.")
        return self.history

    def plot_results(self):
        """Профессиональная визуализация результатов."""
        if not self.history:
            logger.warning("Нет данных для визуализации.")
            return

        times = [record.time for record in self.history]
        setpoints = [record.setpoint for record in self.history]
        measurements = [record.measured_value for record in self.history]
        filtered = [record.filtered_value for record in self.history]
        controls = [record.control_output for record in self.history]
        states = np.array([record.system_state for record in self.history])

        fig, axs = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
        fig.suptitle(f'Результаты управления ({self.active_controller})', fontsize=16)

        # График 1: Сигналы
        axs[0].plot(times, setpoints, 'r--', label='Уставка', linewidth=2)
        axs[0].plot(times, measurements, 'b-', alpha=0.7, label='Измерение (с шумом)')
        axs[0].plot(times, filtered, 'g-', linewidth=2, label='Отфильтрованное значение (Калман)')
        axs[0].set_ylabel('Значение')
        axs[0].legend()
        axs[0].grid(True, alpha=0.3)

        # График 2: Управляющее воздействие
        axs[1].plot(times, controls, 'm-', linewidth=2, label='Управляющее воздействие')
        axs[1].set_ylabel('Управление (%)')
        axs[1].legend()
        axs[1].grid(True, alpha=0.3)

        # График 3: Состояние системы
        for i in range(states.shape[1]):
            axs[2].plot(times, states[:, i], label=f'Состояние {i+1}')
        axs[2].set_xlabel('Время (с)')
        axs[2].set_ylabel('Состояние')
        axs[2].legend()
        axs[2].grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def get_performance_metrics(self) -> Dict[str, float]:
        """Расчет метрик производительности."""
        if not self.history:
            return {}

        errors = np.array([rec.setpoint - rec.filtered_value for rec in self.history])
        controls = np.array([rec.control_output for rec in self.history])

        metrics = {
            'IAE': np.sum(np.abs(errors)) * self.dt,  # Интеграл абсолютной ошибки
            'ISE': np.sum(errors**2) * self.dt,       # Интеграл квадрата ошибки
            'ITAE': np.sum(np.abs(errors) * np.array([rec.time for rec in self.history])) * self.dt,  # Интеграл времени * абсолютной ошибки
            'Control_Effort': np.sum(np.abs(controls)) * self.dt,  # Затраты на управление
            'Max_Error': np.max(np.abs(errors)),
            'RMSE': np.sqrt(np.mean(errors**2)),
            'Settling_Time': self._calculate_settling_time(errors, 0.05),
            'Overshoot': self._calculate_overshoot(errors, self.setpoint)
        }

        return metrics

    def _calculate_settling_time(self, errors: np.ndarray, threshold: float) -> float:
        """Расчет времени установления."""
        steady_state_error = errors[-1]
        within_band = np.abs(errors - steady_state_error) <= threshold * abs(self.setpoint)
        if np.any(within_band):
            idx = np.where(within_band)[0][0]
            return idx * self.dt
        return len(errors) * self.dt

    def _calculate_overshoot(self, errors: np.ndarray, setpoint: float) -> float:
        """Расчет перерегулирования (%)."""
        if setpoint == 0:
            return 0.0
        peak_value = np.max(np.abs(setpoint - errors)) if setpoint > 0 else np.min(setpoint - errors)
        overshoot = (peak_value - setpoint) / setpoint * 100.0
        return max(0.0, overshoot)

# ========================
# 9. ЮНИТ-ТЕСТЫ
# ========================
class TestFilters(unittest.TestCase):
    """Тесты для фильтров."""
    def test_low_pass_filter(self):
        dt = 0.1
        cutoff = 1.0
        filter = LowPassFilter(cutoff, dt)
        # Проверка на постоянном сигнале
        for _ in range(10):
            output = filter.update(10.0)
        self.assertAlmostEqual(output, 10.0, places=1)

    def test_kalman_filter(self):
        kf = KalmanFilter1D(process_variance=0.01, measurement_variance=1.0, initial_value=0.0)
        measurements = [1.0, 1.1, 0.9, 1.05, 0.95]
        estimates = [kf.update(z) for z in measurements]
        self.assertTrue(len(estimates) == len(measurements))
        self.assertLess(abs(estimates[-1] - 1.0), 0.1)

class TestAdvancedPID(unittest.TestCase):
    """Тесты для расширенного ПИД."""
    def test_anti_windup_clamping(self):
        pid = AdvancedPID(Kp=10.0, Ki=1.0, Kd=0.0, dt=0.1, output_limits=(0, 50))
        # Создаем большую ошибку, чтобы вызвать насыщение
        for _ in range(5):
            output = pid.update(-10.0)  # setpoint=0, measured=-10 => error=10
        self.assertEqual(output, 50.0)  # Проверка насыщения
        self.assertTrue(pid.is_saturated)

    def test_derivative_filtering(self):
        pid = AdvancedPID(Kp=1.0, Ki=0.0, Kd=1.0, dt=0.1, filter_derivative=True, derivative_cutoff_freq=1.0)
        outputs = []
        # Ступенчатый вход
        outputs.append(pid.update(0.0))  # t=0
        for _ in range(10):
            outputs.append(pid.update(1.0))  # t>0
        # Производная должна быть большой на первом шаге и быстро затухать
        self.assertGreater(outputs[1], outputs[2])
        self.assertGreater(outputs[2], outputs[3])

# ========================
# 10. ЗАПУСК ДЕМОНСТРАЦИИ
# ========================
def main():
    """Главная функция для демонстрации."""
    print("🚀 Запуск Ultimate Digital Signal Processing & Control Suite: 'NeuroMPC-PID Pro'")

    # Параметры
    dt = 0.5  # сек
    simulation_time = 300  # сек
    steps = int(simulation_time / dt)
    setpoint = 75.0

    # Создание системы и супервайзера
    system = ThermalSystem(ambient_temp=20.0)
    supervisor = ControlSupervisor(system, dt, setpoint)

    # Демонстрация всех контроллеров
    controllers_to_test = ["PID", "NeuralPID"]  # "MPC" можно добавить, если нужно
    all_metrics = {}

    for controller_name in controllers_to_test:
        print(f"\n--- Тестирование контроллера: {controller_name} ---")
        supervisor.switch_controller(controller_name)
        system.reset()  # Сброс системы
        supervisor.pid_controller.reset()  # Сброс ПИД
        supervisor.neural_pid.reset()  # Сброс NeuralPID

        # Запуск симуляции
        history = supervisor.run_simulation(steps, noise_std=2.0)

        # Визуализация
        supervisor.plot_results()

        # Метрики
        metrics = supervisor.get_performance_metrics()
        all_metrics[controller_name] = metrics
        print(f"📈 Метрики для {controller_name}:")
        for key, value in metrics.items():
            print(f"    {key}: {value:.4f}")

    # Сравнение метрик
    print("\n--- СРАВНЕНИЕ МЕТРИК ---")
    for metric in ['IAE', 'ISE', 'ITAE', 'RMSE']:
        print(f"\n{metric}:")
        for ctrl, metrics in all_metrics.items():
            print(f"    {ctrl}: {metrics.get(metric, 'N/A'):.4f}")

    print("\n✅ Демонстрация завершена. Логи сохранены в 'control_system.log'.")

if __name__ == "__main__":
    # Запуск тестов
    print("🧪 Запуск юнит-тестов...")
    unittest.main(argv=[''], exit=False, verbosity=2)

    # Запуск основной демонстрации
    main()
