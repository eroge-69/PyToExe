from datetime import datetime, timedelta, date
from os import system, name
import pyperclip
from typing import Callable, List, Tuple

# ===== Colors (ANSI) =====
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37
BRIGHT_BLACK = 90
BRIGHT_RED = 91
BRIGHT_GREEN = 92
BRIGHT_YELLOW = 93
BRIGHT_BLUE = 94
BRIGHT_MAGENTA = 95
BRIGHT_CYAN = 96
BRIGHT_WHITE = 97

# ===== Time constants =====
TICKS_PER_SECOND = 10_000_000  # 1 tick = 100 ns
BASE_DATE = datetime(1, 1, 1)  # Reference date (year 0001)
TODAY = date.today()

# ===== Defaults for time input =====
DEFAULT_HOUR = 8
DEFAULT_MINUTE = 23
DEFAULT_SECOND = 54

# ===== Utils =====
def col(text, code=MAGENTA) -> str:
    """Return text wrapped with ANSI color escape codes."""
    return f"\033[{code}m{str(text)}\033[0m"

def clear() -> None:
    """Clear the console screen (cross-platform)."""
    if name == 'nt':
        _ = system('cls')
    else:
        _ = system('clear')

def date_show(dt: date, daysback: int = 0, thismonth: bool = False) -> str:
    """Return formatted date string with an optional offset."""
    d = dt - timedelta(days=daysback)
    return d.strftime("../%m/%Y") if thismonth else d.strftime("%d/%m/%Y")

# ===== Conversion =====
def ticks_to_date(ticks: int) -> datetime:
    """Convert .NET-style ticks (100 ns since year 1) to datetime."""
    delta = timedelta(seconds=ticks / TICKS_PER_SECOND)
    return BASE_DATE + delta

def date_to_ticks(year: int, month: int, day: int,
                  hour: int = 0, minute: int = 0, second: int = 0) -> int:
    """Convert datetime components (Y-M-D H:M:S) to ticks."""
    input_date = datetime(year, month, day, hour, minute, second)
    delta = input_date - BASE_DATE
    return int(delta.total_seconds() * TICKS_PER_SECOND)

# ===== Input helpers =====
def read_int(prompt: str, default: int | None = None) -> int:
    """Prompt for an integer with an optional default."""
    s = input(prompt)
    if s.strip() == "" and default is not None:
        return default
    return int(s)

def prompt_hms_and_print(year: int, month: int, day: int) -> int:
    """Prompt for hour/minute/second, compute ticks, print and copy."""
    hour = read_int(f"Enter hour (0-23, optional, default={DEFAULT_HOUR}): ", DEFAULT_HOUR)
    minute = read_int(f"Enter minute (0-59, optional, default={DEFAULT_MINUTE}): ", DEFAULT_MINUTE)
    second = read_int(f"Enter second (0-59, optional, default={DEFAULT_SECOND}): ", DEFAULT_SECOND)
    ticks_result = date_to_ticks(year, month, day, hour, minute, second)

    print("-----------------------------")
    print(f"Ticks value for {day:02d}/{month:02d}/{year} "
          f"{hour:02d}:{minute:02d}:{second:02d} ticks: {ticks_result}")

    try:
        pyperclip.copy(str(ticks_result))
        print(col("[✔] Copied to clipboard", BRIGHT_GREEN))
    except Exception as e:
        print(col(f"[!] Could not copy to clipboard: {e}", BRIGHT_RED))

    return ticks_result

# ===== Handlers =====
def handle_today_offset(days: int) -> None:
    """Compute ticks for TODAY minus offset days."""
    ref = TODAY - timedelta(days=days)
    prompt_hms_and_print(ref.year, ref.month, ref.day)

def handle_this_month_specific_day() -> None:
    """Prompt for a day in the current month and compute ticks."""
    ref = TODAY
    year, month = ref.year, ref.month
    day = read_int("Enter day: ")
    prompt_hms_and_print(year, month, day)

def handle_date_to_ticks_prompt() -> None:
    """Prompt for a full date and compute ticks."""
    year = read_int("Enter year: ")
    month = read_int("Enter month: ")
    day = read_int("Enter day: ")
    prompt_hms_and_print(year, month, day)

def handle_ticks_to_date_prompt() -> None:
    """Prompt for ticks, convert to date, print and copy."""
    ticks_input = int(input("Enter the number of ticks: "))
    result_date = ticks_to_date(ticks_input)
    iso = result_date.strftime("%d/%m/%Y %H:%M:%S")
    print("-----------------------------")
    print(f"Date and time for {ticks_input} ticks: {iso}")
    try:
        pyperclip.copy(iso)
        print(col("[✔] Copied to clipboard", BRIGHT_GREEN))
    except Exception as e:
        print(col(f"[!] Could not copy to clipboard: {e}", BRIGHT_RED))

# ===== Menu label factories =====
def make_label_today() -> Callable[[int], str]:
    def label(idx: int) -> str:
        return f"{col(idx)} Today   \t{col(date_show(TODAY), GREEN)}"
    return label

def make_label_today_n(n: int) -> Callable[[int], str]:
    def label(idx: int) -> str:
        return f"{col(idx)} Today-{n} \t{col(date_show(TODAY - timedelta(days=n)), GREEN)}"
    return label

def make_label_this_month() -> Callable[[int], str]:
    def label(idx: int) -> str:
        return f"{col(idx)} This month \t{col(date_show(TODAY, 0, True), GREEN)}"
    return label

def make_label_text(text: str) -> Callable[[int], str]:
    def label(idx: int) -> str:
        return f"{col(idx)} {text}"
    return label

# ===== Menu model =====
def build_menu() -> List[Tuple[Callable[[int], str], Callable[[], None]]]:
    """Build the menu as a list of (label_fn(index), action) tuples."""
    items: List[Tuple[Callable[[int], str], Callable[[], None]]] = []

    # Today and offsets
    offsets = [0, 1, 2, 3, 4]  # Add more offsets if needed
    items.append((make_label_today(),          lambda: handle_today_offset(0)))
    for n in offsets[1:]:
        items.append((make_label_today_n(n),   lambda n=n: handle_today_offset(n)))

    # Other actions
    items.append((make_label_this_month(),     handle_this_month_specific_day))
    items.append((make_label_text("Date to Ticks"), handle_date_to_ticks_prompt))
    items.append((make_label_text("Ticks to Date"), handle_ticks_to_date_prompt))

    return items

# ===== UI & Dispatcher =====
def print_menu() -> None:
    """Print the menu with auto-indexed, colored options."""
    clear()
    for idx, (label_fn, _) in enumerate(build_menu(), start=1):
        print(label_fn(idx))

def process_choice(choice: str) -> None:
    """Dispatch a menu choice to the correct handler."""
    print("-----------------------------")
    items = build_menu()
    actions = {str(i): action for i, (_, action) in enumerate(items, start=1)}
    action = actions.get(choice)
    if action:
        action()
    else:
        keys = list(actions.keys())
        lo, hi = keys[0], keys[-1]
        print(col(f"Invalid choice. Please select {lo}..{hi}", BRIGHT_RED))

# ===== Main =====
def main() -> None:
    """Entry point for the program."""
    print_menu()
    choice = input("Choose an option: ").strip()
    process_choice(choice)

if __name__ == "__main__":
    main()
