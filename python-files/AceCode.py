# AceCode v0.5 - TUI-based programming and gaming platform
import curses
import time
import re
import random

# --- 1. Вспомогательная функция для подсветки синтаксиса ---
def get_command_color(line):
    """Определяет цветовую пару для строки кода."""
    line = line.strip().upper()
    if line.startswith("REM"):
        return 5 # Magenta (Комментарий)
    elif line.startswith("IF") or line.startswith("GOTO") or line.startswith("CHECK"):
        return 3 # Yellow (Управление Потоком/Проверка)
    elif line.startswith("PRINT") or line.startswith("VAR"):
        return 4 # Green (Вывод/Переменные)
    elif line.startswith("SCENE") or line.startswith("PLACE") or line.startswith("MOVE") or line.startswith("GETKEY"):
        return 6 # Blue (Игровые команды)
    elif line in ["ADD", "SUB", "MUL", "DIV"]:
        return 2 # Cyan (Арифметика)
    else:
        return 1 # White/Black (Обычный текст)

# --- 2. Логика выполнения команд AceCode ---
def execute_command(line, variables, current_line_num, game_state, key_queue):
    """Выполняет одну строку AceCode, изменяя переменные и состояние игры."""
    parts = line.strip().upper().split(maxsplit=1)
    if not parts: return ""
    
    command = parts[0]
    args = parts[1].strip() if len(parts) > 1 else ""
    
    prefix = f"[{current_line_num or '-'}] "
    
    # Разбираем game_state для удобства
    scene = game_state['scene']
    width = game_state['width']
    height = game_state['height']
    default_char = game_state['default_char']

    # --- АРИФМЕТИКА и ПЕРЕМЕННЫЕ ---
    if command == "PRINT":
        if args.startswith('"') and args.endswith('"'): return f"{prefix}💻: {args[1:-1]}"
        elif args in variables: return f"{prefix}💻: {variables[args]}"
        else: return f"{prefix}💻: {args}"
    
    elif command == "VAR":
        try:
            name, value = [p.strip() for p in args.split('=', 1)]
            variables[name] = value
            return f"{prefix}✅ VAR {name} set to '{value}'."
        except ValueError:
            return f"{prefix}❌ Invalid format. Use: VAR NAME = VALUE"
    
    elif command in ["ADD", "SUB", "MUL", "DIV"]:
        try:
            name, value_str = [p.strip() for p in args.split(',', 1)]
            value = float(value_str)
            current_value = float(variables.get(name, 0))
            
            new_value = current_value
            if command == "ADD": new_value += value
            elif command == "SUB": new_value -= value
            elif command == "MUL": new_value *= value
            elif command == "DIV":
                if value == 0: return f"{prefix}❌ Error: Division by zero!"
                new_value /= value
            
            variables[name] = str(round(new_value, 4))
            return f"{prefix}✅ {command} done. {name} is now {variables[name]}."
        except (ValueError, KeyError):
            return f"{prefix}❌ Invalid format. Use: {command} VAR, VALUE"

    # --- УПРАВЛЕНИЕ ПОТОКОМ ---
    elif command == "IF":
        try:
            cond_part, goto_part = [p.strip() for p in args.split("GOTO", 1)]
            target_line = int(goto_part)
            match = re.match(r"(\w+)\s*([<>=!]+)\s*(\S+)", cond_part)
            if not match: return f"{prefix}❌ Invalid IF format."
            
            var_name, op, comp_val_str = match.groups()
            var_value = float(variables.get(var_name, 0))
            comp_value = float(comp_val_str)
            
            condition_met = False
            if op == ">": condition_met = var_value > comp_value
            elif op == "<": condition_met = var_value < comp_value
            elif op in ["==", "="]: condition_met = var_value == comp_value
            elif op == "!=": condition_met = var_value != comp_value
            
            if condition_met: return f"GOTO_COMMAND:{target_line}"
            else: return f"{prefix}⏭ IF condition false."
        except Exception:
            return f"{prefix}❌ Invalid IF format. Use: IF VAR > VALUE GOTO LINE"
            
    elif command == "GOTO":
        try:
            target_line = int(args.strip())
            return f"GOTO_COMMAND:{target_line}"
        except ValueError:
            return f"{prefix}❌ Invalid GOTO target."
    
    # --- ИГРОВЫЕ КОМАНДЫ ---
    elif command == "SCENE":
        try:
            parts = [p.strip() for p in args.split(',', 2)]
            new_w = int(parts[0])
            new_h = int(parts[1])
            new_char = parts[2][0] if len(parts) > 2 else ' '

            game_state['width'] = new_w
            game_state['height'] = new_h
            game_state['default_char'] = new_char
            game_state['scene'] = [[new_char for _ in range(new_w)] for _ in range(new_h)]
            return f"{prefix}🖼 SCENE created: {new_w}x{new_h} with '{new_char}'."
        except Exception:
            return f"{prefix}❌ Invalid SCENE format. Use: SCENE W, H, CHAR"

    elif command == "PLACE":
        try:
            parts = [p.strip() for p in args.split(',', 2)]
            x, y = int(parts[0]), int(parts[1])
            char = parts[2][0]
            
            if 0 <= y < height and 0 <= x < width:
                scene[y][x] = char
                return f"{prefix}📍 PLACED '{char}' at ({x}, {y})."
            else:
                return f"{prefix}❌ PLACE error: Coordinates out of bounds."
        except Exception:
            return f"{prefix}❌ Invalid PLACE format. Use: PLACE X, Y, CHAR"

    elif command == "MOVE":
        try:
            parts = [p.strip() for p in args.split(',', 3)]
            fx, fy, tx, ty = [int(p) for p in parts]
            
            if all(0 <= c < dim for c, dim in zip([fx, tx], [width, width])) and \
               all(0 <= r < dim for r, dim in zip([fy, ty], [height, height])):
                
                char_to_move = scene[fy][fx]
                scene[ty][tx] = char_to_move
                scene[fy][fx] = default_char
                return f"{prefix}➡️ MOVED '{char_to_move}' from ({fx}, {fy}) to ({tx}, {ty})."
            else:
                return f"{prefix}❌ MOVE error: Coordinates out of bounds."
        except Exception:
            return f"{prefix}❌ Invalid MOVE format. Use: MOVE FX, FY, TX, TY"
            
    elif command == "CHECK":
        try:
            cond_part, goto_part = [p.strip() for p in args.split("GOTO", 1)]
            target_line = int(goto_part)
            
            parts = [p.strip() for p in cond_part.split(',', 2)]
            x, y = int(parts[0]), int(parts[1])
            char_to_check = parts[2][0]

            if 0 <= y < height and 0 <= x < width:
                if scene[y][x] == char_to_check:
                    return f"GOTO_COMMAND:{target_line}"
                else:
                    return f"{prefix}⏭ CHECK failed."
            else:
                return f"{prefix}❌ CHECK error: Coordinates out of bounds."
        except Exception:
            return f"{prefix}❌ Invalid CHECK format. Use: CHECK X, Y, CHAR GOTO LINE"

    elif command == "GETKEY":
        try:
            var_name = args
            if key_queue:
                key = key_queue.pop(0)
                variables[var_name] = key
                return f"{prefix}⌨️ GETKEY: '{key}' saved to {var_name}."
            else:
                variables[var_name] = ""
                return f"{prefix}❌ GETKEY: Key queue empty. Storing empty string."
        except Exception:
            return f"{prefix}❌ Invalid GETKEY format. Use: GETKEY VAR_NAME"
    
    # --- ПРОЧИЕ ---
    elif command == "CLS":
        return "CLS_COMMAND" 
    elif command == "REM":
        return f"💬 Comment ignored: {args}"
    
    else:
        return f"{prefix}❌ Unknown command: '{command}'"

# --- 3. Основная функция интерфейса на curses ---
def main(stdscr):
    # Настройки Curses
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)
    
    # Цветовые пары для подсветки синтаксиса
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK) # Default
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK) # Арифметика (ADD/SUB/MUL/DIV)
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Управление Потоком (IF/GOTO/CHECK)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK) # Вывод/Переменные (PRINT/VAR)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK) # Комментарии (REM)
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK) # Игровые (SCENE/PLACE/MOVE/GETKEY)
    
    # Состояние приложения
    tabs = ["File (Run)", "Console", "Help", "Exit"]
    selected_tab_idx = 0
    
    # Игровое состояние
    game_state = {
        'scene': [[' ']],
        'width': 1,
        'height': 1,
        'default_char': ' '
    }
    # Очередь для имитации ввода W/A/S/D
    key_queue = ['W', 'S', 'D', 'A', 'W', 'S', 'D', 'A'] * 3 
    
    variables = {}
    output_lines = ["Welcome to AceCode v0.5! Press TAB to switch modes. File(Run) to run code."]
    input_buffer = ""
    
    # Состояние Редактора
    code_lines = [
        "REM --- AceCode Game Demo ---", 
        "VAR PX = 1", 
        "VAR PY = 1",
        "VAR SCORE = 0",
        "VAR KEY = \"\"",
        "SCENE 7, 7, '.'",
        "PLACE 5, 5, 'G'",
        "PLACE 1, 1, '@'",
        "REM --- 10: Main Loop ---",
        "PRINT \"Score:\"", 
        "PRINT SCORE",
        "GETKEY KEY",
        "IF KEY == \"W\" GOTO 20",
        "IF KEY == \"S\" GOTO 30",
        "IF KEY == \"A\" GOTO 40",
        "IF KEY == \"D\" GOTO 50",
        "GOTO 60",
        "REM --- Movement UP (20) ---",
        "SUB PY, 1",
        "MOVE PX, PY+1, PX, PY",
        "GOTO 60",
        "REM --- Movement DOWN (30) ---",
        "ADD PY, 1",
        "MOVE PX, PY-1, PX, PY",
        "GOTO 60",
        "REM --- Movement LEFT (40) ---",
        "SUB PX, 1",
        "MOVE PX+1, PY, PX, PY",
        "GOTO 60",
        "REM --- Movement RIGHT (50) ---",
        "ADD PX, 1",
        "MOVE PX-1, PY, PX, PY",
        "GOTO 60",
        "REM --- 60: Check Collision ---",
        "CHECK PX, PY, 'G' GOTO 70",
        "GOTO 10",
        "REM --- 70: Goal Pickup ---",
        "PRINT \"Goal!\"",
        "ADD SCORE, 10",
        "GOTO 10"
    ]
    editor_mode = True 
    cursor_y = 0
    
    # Состояние Симуляции
    is_simulating = False
    sim_line_ptr = 0

    # Главный цикл приложения
    while True:
        try:
            key = stdscr.getch()
        except:
            key = -1

        # --- Обработка Ввода ---
        if key == curses.KEY_LEFT:
            selected_tab_idx = (selected_tab_idx - 1 + len(tabs)) % len(tabs)
        elif key == curses.KEY_RIGHT:
            selected_tab_idx = (selected_tab_idx + 1) % len(tabs)
        elif key == ord('\t'):
            editor_mode = not editor_mode
            output_lines.append(f">>> Switched to {'Editor' if editor_mode else 'Console'} Mode.")

        # Логика ввода в Режиме Редактора
        if editor_mode:
            if key == curses.KEY_UP:
                cursor_y = max(0, cursor_y - 1)
            elif key == curses.KEY_DOWN:
                cursor_y = min(len(code_lines) - 1, cursor_y + 1)
            elif key in [curses.KEY_ENTER, 10, 13]:
                current_line_content = code_lines[cursor_y]
                code_lines.insert(cursor_y + 1, "")
                cursor_y += 1
            elif key == curses.KEY_BACKSPACE or key == 127:
                if code_lines[cursor_y]:
                    code_lines[cursor_y] = code_lines[cursor_y][:-1]
                elif len(code_lines) > 1:
                    code_lines.pop(cursor_y)
                    cursor_y = max(0, cursor_y - 1)
            elif key != -1 and 32 <= key <= 126:
                code_lines[cursor_y] += chr(key)
        
        # Логика ввода в Режиме Консоли
        elif not editor_mode:
            if key in [curses.KEY_ENTER, 10, 13]:
                if tabs[selected_tab_idx] == "Exit" and not input_buffer: break
                
                output_lines.append(f">>> {input_buffer}")
                result = execute_command(input_buffer, variables, None, game_state, []) # Игнорируем key_queue в консоли
                if result == "CLS_COMMAND": output_lines.clear()
                else: output_lines.append(result)
                input_buffer = ""

            elif key == curses.KEY_BACKSPACE or key == 127: input_buffer = input_buffer[:-1]
            elif key != -1 and 32 <= key <= 126: input_buffer += chr(key)

        # Обработка команды "Run"
        if tabs[selected_tab_idx] == "File (Run)" and key in [curses.KEY_ENTER, 10, 13] and not input_buffer:
            if editor_mode and not is_simulating:
                is_simulating = True
                sim_line_ptr = 0
                variables.clear() # Сбросить переменные перед запуском
                # Восстановить начальную очередь ключей для нового запуска
                key_queue = ['W', 'S', 'D', 'A', 'W', 'S', 'D', 'A'] * 3 
                output_lines.append("===== SIMULATION STARTED =====")
                output_lines.append(f"Loaded {len(code_lines)} lines.")
            elif not editor_mode:
                output_lines.append("❌ Must be in Editor Mode to run code.")
        
        # Обработка команды "Exit"
        elif tabs[selected_tab_idx] == "Exit" and key in [curses.KEY_ENTER, 10, 13] and not input_buffer:
            break
            
        # --- СИМУЛЯЦИЯ ---
        if is_simulating:
            if sim_line_ptr < len(code_lines):
                line_to_execute = code_lines[sim_line_ptr]
                
                result = execute_command(line_to_execute, variables, sim_line_ptr + 1, game_state, key_queue)
                
                if result:
                    if result == "CLS_COMMAND": output_lines.clear()
                    elif result.startswith("GOTO_COMMAND:"):
                        target_line = int(result.split(':')[1])
                        if 1 <= target_line <= len(code_lines):
                            sim_line_ptr = target_line - 1
                        else:
                            output_lines.append(f"❌ Invalid GOTO target line: {target_line}. Halting.")
                            is_simulating = False
                    else:
                        output_lines.append(result)
                        sim_line_ptr += 1
                else: # Пустые строки пропускаем
                    sim_line_ptr += 1

            else:
                is_simulating = False
                output_lines.append("===== SIMULATION FINISHED =====")
                time.sleep(1)

        # --- Отрисовка интерфейса ---
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        split_x = int(width * 2 / 3) 
        split_x = max(1, min(width - 1, split_x))

        # 1. Вкладки
        tab_y, tab_x = 0, 1
        for i, tab in enumerate(tabs):
            style = curses.color_pair(1) if i == selected_tab_idx else curses.A_NORMAL
            stdscr.addstr(tab_y, tab_x, f" {tab} ", style)
            tab_x += len(tab) + 3
        
        # 2. Разделитель
        stdscr.addstr(1, 0, "=" * width)

        # 3. Редактор / Окно Вывода
        if editor_mode:
            stdscr.addstr(1, 1, " Code Editor ", curses.A_BOLD)
            max_code_lines = height - 5
            start_line = max(0, cursor_y - max_code_lines + 1)
            
            for i, line in enumerate(code_lines):
                line_num = i + 1
                if line_num >= start_line + 1 and line_num <= start_line + max_code_lines:
                    relative_y = 2 + (line_num - start_line) - 1
                    
                    color_pair = get_command_color(line)
                    style = curses.color_pair(color_pair)
                    
                    cursor_indicator = ">" if i == cursor_y and not is_simulating else " "
                    
                    sim_style = curses.A_REVERSE if is_simulating and i == sim_line_ptr else curses.A_NORMAL
                    
                    code_display = f"{cursor_indicator}{line_num:02d}| {line}"
                    stdscr.addstr(relative_y, 1, code_display[:split_x - 2], style | sim_style)
        
        else: # Консольный режим
            stdscr.addstr(1, 1, " Console Output ", curses.A_BOLD)
            max_output_lines = height - 5
            start_line = max(0, len(output_lines) - max_output_lines)
            for i, line in enumerate(output_lines[start_line:]):
                if 2 + i < height - 3:
                    stdscr.addstr(2 + i, 1, line[:split_x - 2])

        # 4. Нижний разделитель
        stdscr.addstr(height - 3, 0, "=" * split_x)

        # 5. Строка состояния/ввода
        if not editor_mode:
            stdscr.addstr(height - 1, 1, f">>> {input_buffer}")
        else:
            mode_status = f"Editor Mode | Line: {cursor_y + 1}/{len(code_lines)}"
            stdscr.addstr(height - 1, 1, mode_status[:split_x - 2])
        
        # --- 6. Окно переменных ---
        if width > split_x + 2:
            stdscr.vline(1, split_x, "|", height - 2)
            stdscr.addstr(0, split_x + 1, "| VARIABLES |", curses.A_REVERSE)
            
            var_y = 2
            stdscr.addstr(var_y, split_x + 2, "Name = Value")
            stdscr.addstr(var_y + 1, split_x, "-" * (width - split_x))
            
            # Выводим переменные
            max_var_lines = (height - 5) // 2
            for i, (name, value) in enumerate(variables.items()):
                if i >= max_var_lines:
                    stdscr.addstr(var_y + 2 + max_var_lines, split_x + 2, f"...and {len(variables) - i} more")
                    break
                stdscr.addstr(var_y + 2 + i, split_x + 2, f"{name} = {value}"[:width - split_x - 4])

            # --- 7. Игровое окно ---
            game_win_y = var_y + 2 + max_var_lines + 2
            if game_win_y < height - 1:
                stdscr.addstr(game_win_y, split_x + 1, "| GAME SCENE |", curses.A_REVERSE)
                stdscr.addstr(game_win_y + 1, split_x, "=" * (width - split_x))
                
                scene = game_state['scene']
                scene_h = game_state['height']
                
                for y in range(scene_h):
                    if game_win_y + 2 + y < height - 1:
                        row_str = "".join(scene[y])
                        stdscr.addstr(game_win_y + 2 + y, split_x + 2, row_str[:width - split_x - 4])


        stdscr.refresh()
        
        # Управление скоростью симуляции
        if is_simulating:
            time.sleep(0.3) 
        else:
            time.sleep(0.01)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except curses.error as e:
        print(f"Error initializing curses: {e}")
        print("On Windows, please run 'pip install windows-curses' first.")