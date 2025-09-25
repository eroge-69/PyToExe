import os
import sys
from enum import Enum
from typing import List, Dict, Set, Tuple, Optional, Union, Any
from abc import ABC, abstractmethod
import platform

# Утилиты для работы с консолью
class ConsoleUI:
    @staticmethod
    def clear():
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    @staticmethod
    def clear_and_draw_header(title: str):
        ConsoleUI.clear()
        ConsoleUI.draw_header(title)

    @staticmethod
    def draw_header(title: str):
        safe_title = title if title else ""
        print(safe_title)
        print()

    @staticmethod
    def draw_info_box(message: str):
        safe_message = message if message else ""
        lines = safe_message.split('\n')
        for line in lines:
            print(line)
        print()

    @staticmethod
    def draw_table(headers: List[str], rows: List[List[str]], max_width_for_last_col: int = -1):
        if not headers or not rows:
            return

        cols = len(headers)
        widths = [1] * cols

        for c in range(cols):
            max_len = len(headers[c])
            for row in rows:
                if c < len(row):
                    cell = row[c] if row[c] else ""
                    max_len = max(max_len, len(cell))
            
            if max_width_for_last_col > 0 and c == cols - 1:
                max_len = min(max_len, max_width_for_last_col)
            widths[c] = max(max_len, 1)

        print(ConsoleUI._build_row(headers, widths))
        for row in rows:
            print(ConsoleUI._build_row(row, widths))

    @staticmethod
    def _repeat_string(s: str, n: int) -> str:
        return s * n

    @staticmethod
    def _split(s: str, delimiter: str) -> List[str]:
        return s.split(delimiter)

    @staticmethod
    def _build_row(cells: List[str], widths: List[int]) -> str:
        result = []
        for i, width in enumerate(widths):
            cell = cells[i] if i < len(cells) else ""
            if len(cell) > width:
                cell = ConsoleUI._truncate(cell, width)
            result.append(ConsoleUI._pad_right(cell, width))
        return "  ".join(result)

    @staticmethod
    def _truncate(value: str, max_width: int) -> str:
        if len(value) <= max_width:
            return value
        if max_width <= 1:
            return value[:max_width]
        if max_width == 2:
            return value[:2]
        return value[:max_width - 1] + "…"

    @staticmethod
    def _pad_right(s: str, width: int) -> str:
        if len(s) >= width:
            return s
        return s + ' ' * (width - len(s))


# Логическое значение условной вершины X
class XValue(Enum):
    NOT_STATED = -1
    FALSE = 0
    TRUE = 1


# Базовый интерфейс вершины блок-схемы
class ISchemeVertex(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_next(self) -> Optional['ISchemeVertex']:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass


# Операторная вершина Y
class YVertex(ISchemeVertex):
    def __init__(self, name: str):
        self.name = name
        self.next = None

    def get_name(self) -> str:
        return self.name

    def get_next(self) -> Optional['ISchemeVertex']:
        return self.next

    def set_next(self, next_vertex: Optional['ISchemeVertex']):
        self.next = next_vertex

    def get_description(self) -> str:
        return f"Пройдена операторная вершина {self.name}"


# Начальная вершина
class StartVertex(YVertex):
    def __init__(self, name: str):
        super().__init__(name)

    def get_description(self) -> str:
        return f"Пройдена начальная вершина {self.name}"


# Конечная вершина
class EndVertex(YVertex):
    def __init__(self, name: str):
        super().__init__(name)

    def get_next(self) -> Optional['ISchemeVertex']:
        return None

    def get_description(self) -> str:
        return f"Пройдена конечная вершина {self.name}"


# Вспомогательная точка P
class PVertex(ISchemeVertex):
    def __init__(self, name: str):
        self.name = name
        self.next = None

    def get_name(self) -> str:
        return self.name

    def get_next(self) -> Optional['ISchemeVertex']:
        return self.next

    def set_next(self, next_vertex: Optional['ISchemeVertex']):
        self.next = next_vertex

    def get_description(self) -> str:
        return f"Пройдена точка {self.name}"


# Условная вершина X
class XVertex(ISchemeVertex):
    def __init__(self, name: str):
        self.name = name
        self.value = XValue.NOT_STATED
        self.lhs = None
        self.rhs = None

    def get_name(self) -> str:
        return self.name

    def get_next(self) -> Optional['ISchemeVertex']:
        if self.value == XValue.FALSE:
            return self.lhs
        elif self.value == XValue.TRUE:
            return self.rhs
        else:
            return None

    def get_value(self) -> XValue:
        return self.value

    def set_value(self, val: XValue):
        self.value = val

    def get_lhs(self) -> Optional['ISchemeVertex']:
        return self.lhs

    def set_lhs(self, left: Optional['ISchemeVertex']):
        self.lhs = left

    def get_rhs(self) -> Optional['ISchemeVertex']:
        return self.rhs

    def set_rhs(self, right: Optional['ISchemeVertex']):
        self.rhs = right

    def get_description(self) -> str:
        if self.value == XValue.TRUE:
            val_str = "1"
        elif self.value == XValue.FALSE:
            val_str = "0"
        else:
            val_str = ""
        
        if not val_str:
            return f"Пройдена условная вершина {self.name}"
        return f"Пройдена условная вершина {self.name} (значение: {val_str})"


# Блок-схема
class Scheme:
    class TraceResult:
        def __init__(self, is_cycle: bool, trace: List[str]):
            self.is_cycle = is_cycle
            self.trace = trace

    def __init__(self):
        self.vertices = []
        self.start = None
        self.end = None
        self.edge_ids = {}  # (from, to) -> id
        self.edge_dirs = {}  # (from, to) -> 'U' or 'D'
        self.cycle_detected = False

    def get_vertices(self) -> List[ISchemeVertex]:
        return self.vertices

    def get_start(self) -> Optional[StartVertex]:
        return self.start

    def set_start(self, s: StartVertex):
        self.start = s

    def get_end(self) -> Optional[EndVertex]:
        return self.end

    def set_end(self, e: EndVertex):
        self.end = e

    def add_vertex(self, vertex: ISchemeVertex) -> ISchemeVertex:
        self.vertices.append(vertex)
        return vertex

    def register_edge(self, from_vertex: ISchemeVertex, to_vertex: ISchemeVertex, edge_id: int, direction: str):
        self.edge_ids[(from_vertex, to_vertex)] = edge_id
        self.edge_dirs[(from_vertex, to_vertex)] = direction

    def connect(self, from_vertex: ISchemeVertex, to_vertex: ISchemeVertex, 
                edge_id: Optional[int] = None, direction: Optional[str] = None) -> 'Scheme':
        if not to_vertex:
            raise ValueError("Целевая вершина не может быть None")

        if isinstance(from_vertex, EndVertex):
            raise RuntimeError("Нельзя соединять после конечной вершины.")
        elif isinstance(from_vertex, YVertex):
            from_vertex.set_next(to_vertex)
        elif isinstance(from_vertex, PVertex):
            from_vertex.set_next(to_vertex)
        else:
            raise RuntimeError("Неизвестный тип вершины для соединения.")

        if edge_id is not None and direction is not None:
            self.register_edge(from_vertex, to_vertex, edge_id, direction)

        return self

    def connect_x(self, x: XVertex, lhs: ISchemeVertex, rhs: ISchemeVertex, 
                  lhs_id: Optional[int] = None, lhs_dir: Optional[str] = None,
                  rhs_id: Optional[int] = None, rhs_dir: Optional[str] = None) -> 'Scheme':
        x.set_lhs(lhs)
        x.set_rhs(rhs)
        
        if lhs_id is not None and lhs_dir is not None:
            self.register_edge(x, lhs, lhs_id, lhs_dir)
        if rhs_id is not None and rhs_dir is not None:
            self.register_edge(x, rhs, rhs_id, rhs_dir)
            
        return self

    def get_conditionals(self) -> List[XVertex]:
        result = []
        for vertex in self.vertices:
            if isinstance(vertex, XVertex):
                result.append(vertex)
        return result

    def reset_conditions(self):
        for x in self.get_conditionals():
            x.set_value(XValue.NOT_STATED)

    def validate(self):
        errors = []

        if not self.start:
            errors.append("Не задана начальная вершина (Start).")
        if not self.end:
            errors.append("Не задана конечная вершина (End).")

        if self.start and self.start not in self.vertices:
            errors.append("Начальная вершина не добавлена в список вершин схемы.")
        if self.end and self.end not in self.vertices:
            errors.append("Конечная вершина не добавлена в список вершин схемы.")

        if self.end and self.end.get_next():
            errors.append("У конечной вершины (Yк) не должно быть следующей вершины.")

        for x in self.get_conditionals():
            if not x.get_lhs():
                errors.append(f"У условной вершины {x.get_name()} не задана ветвь LHS (False).")
            if not x.get_rhs():
                errors.append(f"У условной вершины {x.get_name()} не задана ветвь RHS (True).")
            if x.get_lhs() and x.get_lhs() not in self.vertices:
                errors.append(f"Ветвь LHS вершины {x.get_name()} указывает на вершину, отсутствующую в схеме.")
            if x.get_rhs() and x.get_rhs() not in self.vertices:
                errors.append(f"Ветвь RHS вершины {x.get_name()} указывает на вершину, отсутствующую в схеме.")

        for vertex in self.vertices:
            if isinstance(vertex, YVertex) and not isinstance(vertex, EndVertex):
                if not vertex.get_next():
                    errors.append(f"У вершины {vertex.get_name()} (Y) не задан Next.")
                elif vertex.get_next() not in self.vertices:
                    errors.append(f"Next вершины {vertex.get_name()} указывает на вершину, отсутствующую в схеме.")
            elif isinstance(vertex, PVertex):
                if not vertex.get_next():
                    errors.append(f"У вершины {vertex.get_name()} (P) не задан Next.")
                elif vertex.get_next() not in self.vertices:
                    errors.append(f"Next вершины {vertex.get_name()} указывает на вершину, отсутствующую в схеме.")

        if self.start:
            if any(v.get_next() == self.start for v in self.vertices 
                   if isinstance(v, (YVertex, PVertex))):
                errors.append("В начальную вершину (Start) не должно входить ребро от Y или P.")
            
            if any(x.get_lhs() == self.start or x.get_rhs() == self.start 
                   for x in self.get_conditionals()):
                errors.append("В начальную вершину (Start) не должно входить ребро от X.")

        if self.start:
            reachable = set()
            stack = [self.start]

            while stack:
                current = stack.pop()
                if current in reachable:
                    continue
                reachable.add(current)

                if isinstance(current, YVertex):
                    if current.get_next():
                        stack.append(current.get_next())
                elif isinstance(current, PVertex):
                    if current.get_next():
                        stack.append(current.get_next())
                elif isinstance(current, XVertex):
                    if current.get_lhs():
                        stack.append(current.get_lhs())
                    if current.get_rhs():
                        stack.append(current.get_rhs())

            for vertex in self.vertices:
                if vertex not in reachable:
                    errors.append(f"Вершина {vertex.get_name()} недостижима из Start.")

            if self.end and self.end not in reachable:
                errors.append("Конечная вершина (End) недостижима из Start.")

        if errors:
            error_msg = "Ошибки валидации схемы:\n- " + "\n- ".join(errors)
            raise RuntimeError(error_msg)

    def build_lsa_trace(self) -> str:
        parts = []
        if not self.start:
            return ""

        current = self.start
        parts.append(current.get_name())

        seen = {current: 0}

        while current and not isinstance(current, EndVertex):
            if isinstance(current, XVertex):
                if current.get_value() == XValue.NOT_STATED:
                    break

            next_vertex = self._resolve_next(current)
            if not next_vertex:
                break

            key = (current, next_vertex)
            edge_id = self.edge_ids.get(key)
            edge_dir = self.edge_dirs.get(key)
            
            if edge_id is not None and edge_dir is not None:
                if edge_dir == 'D':
                    parts.append(f"w^{edge_id}")
                    parts.append(f"v{edge_id}")
                else:
                    parts.append(f"^{edge_id}")

            current = next_vertex
            parts.append(current.get_name())

            if current in seen:
                break
            seen[current] = len(seen)

        return " ".join(parts)

    def run_m1(self):
        self._ensure_ready()
        ConsoleUI.clear_and_draw_header("Режим 1 (последовательный ввод значений)")

        self.reset_conditions()

        xs_all = self.get_conditionals()
        by_name = {x.get_name(): x for x in xs_all}

        order = ["P0", "X0", "X1", "X2"]
        ordered = []
        for name in order:
            if name in by_name:
                ordered.append(by_name[name])

        remaining = [x for x in xs_all if x not in ordered]
        remaining.sort(key=lambda x: x.get_name())
        ordered.extend(remaining)

        for xv in ordered:
            b = self._read_bool_for_x(xv)
            xv.set_value(XValue.TRUE if b else XValue.FALSE)

            print(f"\nВыполняемые шаги после ввода {xv.get_name()} = {1 if b else 0}:")
            self._execute_with_console(False)
            if self.cycle_detected:
                print("\nВвод значений прекращён: обнаружен цикл.")
                break

        self.reset_conditions()

    def run_m2(self):
        self._ensure_ready()
        ConsoleUI.clear_and_draw_header("Режим 2 (разовый ввод всех условий)")
        
        xs = self.get_conditionals()
        xs.sort(key=lambda x: x.get_name())

        print("Введите значения для ", end="")
        names = [x.get_name() for x in xs]
        print(", ".join(names), end="")
        print(" (0/1) одним вводом (например: 0100)")

        while True:
            user_input = input("> ").replace(" ", "")
            
            if len(user_input) != len(xs):
                print(f"Количество значений должно быть {len(xs)}. Попробуйте снова.")
                continue

            valid = True
            for i, char in enumerate(user_input):
                if char == '0':
                    xs[i].set_value(XValue.FALSE)
                elif char == '1':
                    xs[i].set_value(XValue.TRUE)
                else:
                    valid = False
                    break

            if not valid:
                print("Допустимы только 0 и 1. Попробуйте снова.")
                continue
            break

        combo = ''.join(['1' if x.get_value() == XValue.TRUE else '0' for x in xs])
        lsa = self.build_lsa_trace()
        print(f"\nКомбинация | Ход работы алгоритма")
        print(f"{combo} | {lsa}")
        self.reset_conditions()

    def run_m3(self):
        self._ensure_ready()
        ConsoleUI.clear_and_draw_header("Режим 3 (полный перебор всех комбинаций)")
        
        xs_sorted = self.get_conditionals()
        xs_sorted.sort(key=lambda x: x.get_name())

        k = len(xs_sorted)
        total = 1 << k

        col_left_title = "Комбинация"
        col_right_title = "Ход работы алгоритма"
        col_left_width = len(col_left_title)

        print(f"{col_left_title} | {col_right_title}")

        path_count = 0
        cycle_count = 0

        for mask in range(total):
            for i in range(k):
                shift = k - 1 - i
                bit = (mask >> shift) & 1
                xs_sorted[i].set_value(XValue.TRUE if bit else XValue.FALSE)

            lsa = self.build_lsa_trace()
            combo_str = ''.join(['1' if x.get_value() == XValue.TRUE else '0' for x in xs_sorted])

            print(f"{combo_str:<{col_left_width}} | {lsa}")

            result = self._trace_once_for_m3()
            if result.is_cycle:
                cycle_count += 1
            else:
                path_count += 1
            self.reset_conditions()

        print()

    def _contains_vertex(self, vertex: ISchemeVertex) -> bool:
        return vertex in self.vertices

    def _resolve_next(self, vertex: ISchemeVertex) -> Optional[ISchemeVertex]:
        return vertex.get_next()

    def _read_bool_for_x(self, x: XVertex) -> bool:
        while True:
            user_input = input(f"Введите значение для {x.get_name()} (0/1): ").replace(" ", "")
            if user_input == "0":
                return False
            elif user_input == "1":
                return True
            else:
                print("Некорректный ввод. Введите 0 или 1.")

    def _ensure_ready(self):
        if not self.start or not self.end:
            raise RuntimeError("Не задана начальная или конечная вершина.")
        self.validate()

    def _compare_x_names(self, a: XVertex, b: XVertex) -> int:
        return (a.get_name() > b.get_name()) - (a.get_name() < b.get_name())

    def _trace_once_for_m3(self) -> 'Scheme.TraceResult':
        names = []
        index_map = {}

        current = self.start
        step = 0

        while current:
            if isinstance(current, XVertex):
                if current.get_value() == XValue.NOT_STATED:
                    break

            if current in index_map:
                cycle_vertices = self._extract_cycle_vertices_for_m3(current)
                final_seq = names[:index_map[current]]
                final_seq.extend(cycle_vertices)
                final_seq.extend(cycle_vertices)
                return Scheme.TraceResult(True, final_seq)

            index_map[current] = step
            names.append(current.get_name())
            step += 1

            if isinstance(current, EndVertex):
                break
            current = self._resolve_next(current)

        return Scheme.TraceResult(False, names)

    def _extract_cycle_vertices_for_m3(self, start_vertex: ISchemeVertex) -> List[str]:
        vertices_list = []
        seen = set()
        v = start_vertex

        while v and v not in seen:
            seen.add(v)
            vertices_list.append(v.get_name())
            v = self._resolve_next(v)
        return vertices_list

    def _execute_with_console(self, interactive: bool):
        self.cycle_detected = False
        visited_index = {}
        current = self.start
        step = 0

        while current:
            if current not in visited_index:
                visited_index[current] = step
                step += 1

                if isinstance(current, XVertex):
                    if interactive and current.get_value() == XValue.NOT_STATED:
                        b = self._read_bool_for_x(current)
                        current.set_value(XValue.TRUE if b else XValue.FALSE)
                    print(current.get_description())
                else:
                    print(current.get_description())

                if isinstance(current, EndVertex):
                    break
                current = self._resolve_next(current)
            else:
                cycle_vertices = self._extract_cycle_vertices_for_console(current)
                to_print = len(cycle_vertices)
                printed = 0
                v = current

                while printed < to_print and v:
                    if isinstance(v, XVertex):
                        print(v.get_description())
                    else:
                        print(v.get_description())
                    printed += 1
                    v = self._resolve_next(v)

                self.cycle_detected = True
                ConsoleUI.draw_info_box("Обнаружен цикл!")
                return

    def _extract_cycle_vertices_for_console(self, start_vertex: ISchemeVertex) -> List[ISchemeVertex]:
        vertices_list = []
        seen = set()
        v = start_vertex

        while v and v not in seen:
            seen.add(v)
            vertices_list.append(v)
            v = self._resolve_next(v)
        return vertices_list


# Главная функция
def main():
    scheme = Scheme()

    # Создание вершин
    yn = scheme.add_vertex(StartVertex("Yн"))
    y0 = scheme.add_vertex(YVertex("Y0"))
    y1 = scheme.add_vertex(YVertex("Y1"))
    y2 = scheme.add_vertex(YVertex("Y2"))
    p0 = scheme.add_vertex(XVertex("P0"))
    x0 = scheme.add_vertex(XVertex("X0"))
    x1 = scheme.add_vertex(XVertex("X1"))
    x2 = scheme.add_vertex(XVertex("X2"))
    yk = scheme.add_vertex(EndVertex("Yк"))

    scheme.set_start(yn)
    scheme.set_end(yk)

    # Прямой ход сверху вниз (ребра 1,2,3):
    scheme.connect(yn, y0, 1, 'D')
    scheme.connect(y0, y1, 2, 'D')
    scheme.connect(y1, y2, 3, 'D')
    scheme.connect(y2, p0)  # без номера

    # P0: 0 -> X0, 1 -> X1
    scheme.connect_x(p0, x0, x1, 4, 'U', 5, 'D')

    # X0: 0 -> P0, 1 -> X1
    scheme.connect_x(x0, p0, x1, 4, 'U', 5, 'D')

    # X1: 0 -> X2, 1 -> Y0
    scheme.connect_x(x1, x2, y0, 6, 'D', 2, 'U')

    # X2: 0 -> Y0, 1 -> Yк
    scheme.connect_x(x2, y0, yk)
    scheme.register_edge(x2, y0, 1, 'U')

    while True:
        ConsoleUI.clear_and_draw_header("Выберите режим:")
        print("1 - Последовательный ввод(P0,X0,X1,X2)")
        print("2 - Ввод сразу всех значений")
        print("3 - Вывод всех возможных комбинаций")
        print("0 - Выход")
        choice = input("Ваш выбор: ").strip()

        try:
            if choice == "1":
                scheme.run_m1()
            elif choice == "2":
                scheme.run_m2()
            elif choice == "3":
                scheme.run_m3()
            elif choice == "0":
                break
            else:
                ConsoleUI.draw_info_box("Некорректный выбор.")
        except Exception as ex:
            ConsoleUI.draw_info_box(f"Ошибка: {str(ex)}")

        print()
        input("Нажмите Enter для возврата в меню...")


if __name__ == "__main__":
    main()
