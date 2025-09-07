Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
м
  File "<python-input-0>", line 1
    ship.py
IndentationError: unexpected indent
>>>
>>> from dataclasses import dataclass
>>>
>>> dataclass
<function dataclass at 0x00000263905CC680>
>>> class Ship:
...         """
...             Класс, представляющий корабль с уровнем защиты.
...                 """
...                     level: int   Уровень защиты корабля (от 1 до 10)
...
  File "<python-input-5>", line 5
    level: int   Уровень защиты корабля (от 1 до 10)
IndentationError: unexpected indent
>>>     def can_defend(self, attack_level: int) - bool:
  File "<python-input-6>", line 1
    def can_defend(self, attack_level: int) - bool:
IndentationError: unexpected indent
>>>         """
  File "<python-input-7>", line 1
    """
IndentationError: unexpected indent
>>>         Проверяет, сможет ли корабль защититься от атаки с заданным уровнем.
  File "<python-input-8>", line 1
    Проверяет, сможет ли корабль защититься от атаки с заданным уровнем.
IndentationError: unexpected indent
>>>         :param attack_level: уровень атаки противника (от 1 до 10)
  File "<python-input-9>", line 1
    :param attack_level: уровень атаки противника (от 1 до 10)
IndentationError: unexpected indent
>>>         :return: True, если защита успешна, иначе False
  File "<python-input-10>", line 1
    :return: True, если защита успешна, иначе False
IndentationError: unexpected indent
>>>         """
  File "<python-input-11>", line 1
    """
IndentationError: unexpected indent
>>>          Проверка, что уровни в допустимом диапазоне
  File "<python-input-12>", line 1
    Проверка, что уровни в допустимом диапазоне
IndentationError: unexpected indent
>>>         if not (1 = attack_level = 10):
  File "<python-input-13>", line 1
    if not (1 = attack_level = 10):
IndentationError: unexpected indent
>>>             raise ValueError("Уровень атаки должен быть в диапазоне от 1 до 10.")
  File "<python-input-14>", line 1
    raise ValueError("Уровень атаки должен быть в диапазоне от 1 до 10.")
IndentationError: unexpected indent
>>>          Защита успешна, если уровень защиты = уровня атаки
  File "<python-input-15>", line 1
    Защита успешна, если уровень защиты = уровня атаки
IndentationError: unexpected indent
>>>         return self.level = attack_level main.py
  File "<python-input-16>", line 1
...     return self.level = attack_level main.py
... IndentationError: unexpected indent
... >>>
... >>> from ship import Ship
... Traceback (most recent call last):
...   File "<python-input-18>", line 1, in <module>
...     from ship import Ship
... ModuleNotFoundError: No module named 'ship'
... >>>
... >>> def main():
... ...              Создаем корабль с уровнем защиты 7
... ...                  my_ship = Ship(level=7)
... ...
...   File "<python-input-20>", line 2
...     Создаем корабль с уровнем защиты 7
...             ^^^^^^^
... SyntaxError: invalid syntax
... >>>      Проверяем защиту от атак разного уровня
...   File "<python-input-21>", line 1
...     Проверяем защиту от атак разного уровня
... IndentationError: unexpected indent
... >>>     attack_levels = 3, 7, 9
...   File "<python-input-22>", line 1
...     attack_levels = 3, 7, 9
... IndentationError: unexpected indent
... >>>     for attack in attack_levels:
...   File "<python-input-23>", line 1
...     for attack in attack_levels:
... IndentationError: unexpected indent
... >>>         result = my_ship.can_defend(attack)
...   File "<python-input-24>", line 1
...     result = my_ship.can_defend(attack)
... IndentationError: unexpected indent
... >>>         print(f"Атака уровня attack: Успешная защита if result else Проигрыш")
...   File "<python-input-25>", line 1
...     print(f"Атака уровня attack: Успешная защита if result else Проигрыш")
... IndentationError: unexpected indent
... >>>
