#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Программа для расчета десантирования с самолета Ил-76МД
Автор: Manus AI
Версия: 1.1 (исправленная)
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import json


@dataclass
class AtmosphereParams:
    """Параметры стандартной атмосферы"""
    T0: float = 288.15  # Температура на уровне моря (К)
    P0: float = 101325  # Давление на уровне моря (Па)
    L: float = 0.0065   # Температурный градиент (К/м)
    g: float = 9.81     # Ускорение свободного падения (м/с²)
    R_specific: float = 287.05  # Удельная газовая постоянная для воздуха (Дж/(кг·К))
    M: float = 0.0289644  # Молярная масса воздуха (кг/моль)
    R: float = 8.31446    # Универсальная газовая постоянная (Дж/(моль·К))


@dataclass
class WindLayer:
    """Слой ветра с определенными параметрами"""
    altitude_min: float  # Минимальная высота слоя (м)
    altitude_max: float  # Максимальная высота слоя (м)
    wind_speed: float    # Скорость ветра (м/с)
    wind_direction: float  # Направление ветра (градусы, 0° = север)


@dataclass
class ParachuteParams:
    """Параметры парашютной системы"""
    name: str
    cd_freefall: float  # Коэффициент сопротивления при свободном падении
    area_freefall: float  # Площадь при свободном падении (м²)
    cd_deployed: float   # Коэффициент сопротивления раскрытого парашюта
    area_deployed: float  # Площадь раскрытого парашюта (м²)
    deployment_time: float  # Время раскрытия парашюта (с)


@dataclass
class DescentObject:
    """Десантируемый объект"""
    mass: float  # Масса (кг)
    parachute: ParachuteParams


@dataclass
class AircraftParams:
    """Параметры самолета"""
    altitude: float  # Высота десантирования (м)
    speed: float     # Скорость самолета (м/с)
    heading: float   # Курс самолета (градусы, 0° = север)


@dataclass
class SimulationResult:
    """Результат симуляции"""
    trajectory: List[Tuple[float, float, float, float]]  # (x, y, z, time)
    landing_point: Tuple[float, float]  # (x, y)
    total_time: float  # Общее время снижения (с)
    landing_velocity: Tuple[float, float, float]  # (vx, vy, vz) при приземлении
    horizontal_drift: float  # Горизонтальное смещение (м)
    max_altitude: float  # Максимальная высота (м)


class AtmosphereModel:
    """Модель стандартной атмосферы"""
    
    def __init__(self, params: AtmosphereParams = None):
        self.params = params or AtmosphereParams()
    
    def get_temperature(self, altitude: float) -> float:
        """Получить температуру на заданной высоте"""
        if altitude < 11000:
            return self.params.T0 - self.params.L * altitude
        else:
            return 216.65  # Температура в стратосфере
    
    def get_pressure(self, altitude: float) -> float:
        """Получить давление на заданной высоте"""
        if altitude < 11000:  # Тропосфера
            return self.params.P0 * (1 - self.params.L * altitude / self.params.T0) ** (
                self.params.g * self.params.M / (self.params.R * self.params.L)
            )
        else:
            # Упрощенная модель для высот выше 11 км
            return self.params.P0 * 0.2233 * math.exp(-self.params.g * self.params.M * (altitude - 11000) / (self.params.R * 216.65))
    
    def get_density(self, altitude: float) -> float:
        """Получить плотность воздуха на заданной высоте"""
        temperature = self.get_temperature(altitude)
        pressure = self.get_pressure(altitude)
        return pressure / (self.params.R_specific * temperature)


class WindModel:
    """Модель ветра"""
    
    def __init__(self, wind_layers: List[WindLayer] = None):
        self.wind_layers = wind_layers or []
    
    def get_wind_velocity(self, altitude: float) -> Tuple[float, float]:
        """Получить компоненты скорости ветра на заданной высоте"""
        for layer in self.wind_layers:
            if layer.altitude_min <= altitude <= layer.altitude_max:
                # Преобразование направления ветра в компоненты скорости
                wind_rad = math.radians(layer.wind_direction)
                wind_x = layer.wind_speed * math.sin(wind_rad)  # Восточная компонента
                wind_y = layer.wind_speed * math.cos(wind_rad)  # Северная компонента
                return wind_x, wind_y
        
        # Если высота не попадает ни в один слой, возвращаем нулевой ветер
        return 0.0, 0.0


class ParachuteSimulator:
    """Симулятор движения парашютиста/груза"""
    
    def __init__(self, atmosphere: AtmosphereModel = None, wind: WindModel = None):
        self.atmosphere = atmosphere or AtmosphereModel()
        self.wind = wind or WindModel()
    
    def simulate_descent(self, 
                        aircraft: AircraftParams,
                        descent_object: DescentObject,
                        dt: float = 0.1) -> SimulationResult:
        """
        Симулировать снижение объекта
        
        Args:
            aircraft: Параметры самолета
            descent_object: Параметры десантируемого объекта
            dt: Шаг по времени (с)
        
        Returns:
            Результат симуляции
        """
        
        # Начальные условия
        x, y, z = 0.0, 0.0, aircraft.altitude
        
        # Начальная скорость равна скорости самолета
        aircraft_heading_rad = math.radians(aircraft.heading)
        vx = aircraft.speed * math.sin(aircraft_heading_rad)
        vy = aircraft.speed * math.cos(aircraft_heading_rad)
        vz = 0.0
        
        time = 0.0
        trajectory = []
        parachute_deployed = False
        
        mass = descent_object.mass
        parachute = descent_object.parachute
        
        while z > 0:
            # Сохранить текущее состояние
            trajectory.append((x, y, z, time))
            
            # Определить, раскрыт ли парашют
            if time >= parachute.deployment_time and not parachute_deployed:
                parachute_deployed = True
            
            # Выбрать параметры сопротивления
            if parachute_deployed:
                cd = parachute.cd_deployed
                area = parachute.area_deployed
            else:
                cd = parachute.cd_freefall
                area = parachute.area_freefall
            
            # Получить параметры атмосферы
            rho = self.atmosphere.get_density(z)
            
            # Получить скорость ветра
            wind_x, wind_y = self.wind.get_wind_velocity(z)
            
            # Относительная скорость объекта относительно воздуха
            vrel_x = vx - wind_x
            vrel_y = vy - wind_y
            vrel_z = vz
            
            vrel_magnitude = math.sqrt(vrel_x**2 + vrel_y**2 + vrel_z**2)
            
            # Сила сопротивления воздуха
            if vrel_magnitude > 0:
                drag_force = 0.5 * rho * vrel_magnitude**2 * cd * area
                
                # Компоненты силы сопротивления (противоположны направлению движения)
                fd_x = -drag_force * vrel_x / vrel_magnitude
                fd_y = -drag_force * vrel_y / vrel_magnitude
                fd_z = -drag_force * vrel_z / vrel_magnitude
            else:
                fd_x = fd_y = fd_z = 0.0
            
            # Сила тяжести
            fg_z = -mass * self.atmosphere.params.g
            
            # Общие силы
            fx_total = fd_x
            fy_total = fd_y
            fz_total = fg_z + fd_z
            
            # Ускорения
            ax = fx_total / mass
            ay = fy_total / mass
            az = fz_total / mass
            
            # Обновление скорости и положения (метод Эйлера)
            vx += ax * dt
            vy += ay * dt
            vz += az * dt
            
            x += vx * dt
            y += vy * dt
            z += vz * dt
            
            time += dt
            
            # Защита от бесконечного цикла
            if time > 3600:  # 1 час максимум
                break
        
        # Расчет результатов
        landing_point = (x, y)
        horizontal_drift = math.sqrt(x**2 + y**2)
        landing_velocity = (vx, vy, vz)
        max_altitude = aircraft.altitude
        
        return SimulationResult(
            trajectory=trajectory,
            landing_point=landing_point,
            total_time=time,
            landing_velocity=landing_velocity,
            horizontal_drift=horizontal_drift,
            max_altitude=max_altitude
        )


class ParachuteDatabase:
    """База данных парашютных систем"""
    
    @staticmethod
    def get_parachute_systems() -> Dict[str, ParachuteParams]:
        """Получить словарь доступных парашютных систем"""
        return {
            "Д-10": ParachuteParams(
                name="Д-10",
                cd_freefall=0.8,
                area_freefall=0.7,
                cd_deployed=1.3,
                area_deployed=55.0,
                deployment_time=3.0
            ),
            "Д-1-5У": ParachuteParams(
                name="Д-1-5У",
                cd_freefall=0.8,
                area_freefall=0.7,
                cd_deployed=1.2,
                area_deployed=50.0,
                deployment_time=2.5
            ),
            "ПГС-1000": ParachuteParams(
                name="ПГС-1000 (грузовая система)",
                cd_freefall=1.2,
                area_freefall=2.0,
                cd_deployed=1.4,
                area_deployed=120.0,
                deployment_time=5.0
            ),
            "Крыло": ParachuteParams(
                name="Парашют-крыло",
                cd_freefall=0.8,
                area_freefall=0.7,
                cd_deployed=0.8,  # Меньшее сопротивление из-за планирующих свойств
                area_deployed=35.0,
                deployment_time=3.0
            )
        }


def create_default_wind_profile() -> List[WindLayer]:
    """Создать профиль ветра по умолчанию"""
    return [
        WindLayer(0, 500, 5.0, 270),      # 0-500м: 5 м/с, западный ветер
        WindLayer(500, 2000, 8.0, 280),   # 500-2000м: 8 м/с, северо-западный
        WindLayer(2000, 5000, 12.0, 290), # 2000-5000м: 12 м/с, северо-западный
        WindLayer(5000, 15000, 15.0, 300) # 5000-15000м: 15 м/с, северо-западный
    ]


def run_test_scenarios():
    """Запустить тестовые сценарии"""
    
    print("=== ТЕСТИРОВАНИЕ ПРОГРАММЫ РАСЧЕТА ДЕСАНТИРОВАНИЯ ===\n")
    
    # Создание моделей
    atmosphere = AtmosphereModel()
    wind = WindModel(create_default_wind_profile())
    simulator = ParachuteSimulator(atmosphere, wind)
    
    # База данных парашютов
    parachute_db = ParachuteDatabase.get_parachute_systems()
    
    # Тестовые сценарии
    test_scenarios = [
        {
            "name": "Стандартное десантирование парашютиста",
            "aircraft": AircraftParams(altitude=600, speed=100, heading=90),
            "object": DescentObject(mass=90, parachute=parachute_db["Д-10"])
        },
        {
            "name": "Высотное десантирование",
            "aircraft": AircraftParams(altitude=2000, speed=120, heading=45),
            "object": DescentObject(mass=85, parachute=parachute_db["Д-1-5У"])
        },
        {
            "name": "Десантирование груза",
            "aircraft": AircraftParams(altitude=800, speed=90, heading=180),
            "object": DescentObject(mass=1000, parachute=parachute_db["ПГС-1000"])
        },
        {
            "name": "Десантирование с парашютом-крылом",
            "aircraft": AircraftParams(altitude=1200, speed=110, heading=270),
            "object": DescentObject(mass=80, parachute=parachute_db["Крыло"])
        }
    ]
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"ТЕСТ {i}: {scenario['name']}")
        print("-" * 50)
        
        # Симуляция
        result = simulator.simulate_descent(scenario["aircraft"], scenario["object"])
        
        # Вывод результатов
        print(f"Параметры самолета: высота {scenario['aircraft'].altitude}м, скорость {scenario['aircraft'].speed}м/с, курс {scenario['aircraft'].heading}°")
        print(f"Объект: масса {scenario['object'].mass}кг, парашют {scenario['object'].parachute.name}")
        print(f"Точка приземления: X = {result.landing_point[0]:.1f} м, Y = {result.landing_point[1]:.1f} м")
        print(f"Горизонтальное смещение: {result.horizontal_drift:.1f} м")
        print(f"Время снижения: {result.total_time:.1f} с ({result.total_time/60:.1f} мин)")
        print(f"Скорость приземления: {abs(result.landing_velocity[2]):.1f} м/с (вертикальная)")
        print(f"Горизонтальная скорость: {math.sqrt(result.landing_velocity[0]**2 + result.landing_velocity[1]**2):.1f} м/с")
        
        # Анализ безопасности
        vertical_speed = abs(result.landing_velocity[2])
        if vertical_speed < 6:
            safety_status = "БЕЗОПАСНО"
        elif vertical_speed < 8:
            safety_status = "ПРИЕМЛЕМО"
        else:
            safety_status = "ОПАСНО"
        
        print(f"Оценка безопасности: {safety_status}")
        print()


def main():
    """Основная функция"""
    run_test_scenarios()


if __name__ == "__main__":
    main()

