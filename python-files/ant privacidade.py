import ctypes
import time
import random
import math

# Configurações da Win32 API
SendInput = ctypes.windll.user32.SendInput

# Estrutura POINT para GetCursorPos
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

# Estruturas necessárias para o INPUT (mouse)
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
    ]

class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("mi", MOUSEINPUT),
    ]

# Constantes para movimento do mouse
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_ABSOLUTE = 0x8000

def get_cursor_pos():
    """Obtém a posição atual do cursor"""
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y

def move_mouse(x, y):
    """
    Move o mouse para coordenadas (x, y) usando SendInput.
    """
    # Converte coordenadas para o sistema absoluto (0-65535)
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    absolute_x = int((x / screen_width) * 65535)
    absolute_y = int((y / screen_height) * 65535)

    # Configura o movimento do mouse
    mouse_input = MOUSEINPUT(
        dx=absolute_x,
        dy=absolute_y,
        mouseData=0,
        dwFlags=MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE,
        time=0,
        dwExtraInfo=None,
    )

    input_structure = INPUT(
        type=0,  # INPUT_MOUSE
        mi=mouse_input,
    )

    # Envia o movimento
    SendInput(1, ctypes.byref(input_structure), ctypes.sizeof(input_structure))

def human_like_mouse_move(x, y, duration=0.5):
    """
    Move o mouse de forma mais humana, com curva de aceleração e micro-ajustes.
    """
    start_x, start_y = get_cursor_pos()
    steps = max(1, int(duration * 60))  # Ajuste o número de passos conforme necessário
    
    for step in range(steps + 1):
        # Interpolação com curva de Bezier para movimento mais natural
        t = step / steps
        t = math.sin(t * math.pi / 2)  # Suaviza início/fim
        current_x = start_x + (x - start_x) * t
        current_y = start_y + (y - start_y) * t
        
        # Adiciona um pequeno tremor humano
        tremor_x = random.randint(-2, 2)
        tremor_y = random.randint(-2, 2)
        
        move_mouse(current_x + tremor_x, current_y + tremor_y)
        time.sleep(duration / steps)

def anti_afk(duration_minutes=60, move_interval=5):
    """
    Anti-AFK usando movimentos de mouse em baixo nível (Win32 API).
    """
    print("Anti-AFK com Win32 API (Ctrl+C para parar)")
    end_time = time.time() + duration_minutes * 60
    
    try:
        while time.time() < end_time:
            # Gera posição aleatória (evitando bordas)
            x = random.randint(100, ctypes.windll.user32.GetSystemMetrics(0) - 100)
            y = random.randint(100, ctypes.windll.user32.GetSystemMetrics(1) - 100)
            
            human_like_mouse_move(x, y, duration=random.uniform(0.3, 0.7))
            print(f"Mouse movido para ({x}, {y})")
            
            time.sleep(move_interval + random.uniform(-1, 1))
    
    except KeyboardInterrupt:
        print("\nParado pelo usuário.")
    finally:
        print("Anti-AFK finalizado.")

if __name__ == "__main__":
    anti_afk(duration_minutes=9999, move_interval=5)