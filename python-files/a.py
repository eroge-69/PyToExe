# i_love_speed.py
import os
import sys
import threading
import ctypes
import time
from collections import deque

# Networking lib (kept but ensure you use responsibly)
import pydivert

# keyboard for hotkey capture
import keyboard

# ImGui + windowing
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
from OpenGL import GL

# sound on toggle (Windows only)
try:
    import winsound
    def beep_on(): winsound.Beep(1000, 120)
    def beep_off(): winsound.Beep(500, 120)
except Exception:
    def beep_on(): pass
    def beep_off(): pass

# ============ ADMIN CHECK ============
if os.name == "nt":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

# ============ FILTERS ============
FILTER_TELE = "outbound and udp.PayloadLength >= 24 and udp.PayloadLength <= 68"
FILTER_FREEZE = "udp.PayloadLength>= 25 && inbound && not tcp"
FILTER_GHOST = "(udp.DstPort>=10011 and udp.DstPort<=10020) and udp.PayloadLength>=50 && udp.PayloadLength<=300"

# ============ GLOBAL STATE ============
states = {
    "Freeze Enemy": False,
    "Ghost Hack": False,
    "Telekill Infinite": False
}
hotkeys = {
    "Freeze Enemy": None,
    "Ghost Hack": None,
    "Telekill Infinite": None
}
# simple counters & small packet queues for visualization
counters = {
    "tele_held": 0,
    "tele_sent": 0,
    "ghost_held": 0,
    "ghost_sent": 0,
    "freeze_held": 0,
    "freeze_sent": 0,
    "total_forwarded": 0
}
packet_tele = deque(maxlen=1000)
packet_ghost = deque(maxlen=1000)
packet_freeze = deque(maxlen=1000)

lock = threading.Lock()
running = True

# ============ BACKEND: divert & send ============
def send_packets_from_list(packets, filter_rule):
    """Sends packets back onto the network via pydivert. Use responsibly."""
    try:
        with pydivert.WinDivert(filter_rule, layer=pydivert.Layer.NETWORK) as sender:
            while packets:
                pkt = packets.popleft()
                try:
                    sender.send(pkt)
                except Exception:
                    pass
    except Exception as e:
        print("send_packets_from_list error:", e)

def divert_loop():
    global running
    combined = f"({FILTER_TELE}) or ({FILTER_GHOST}) or ({FILTER_FREEZE})"
    try:
        with pydivert.WinDivert(combined) as w:
            for packet in w:
                if not running:
                    break
                handled = False
                with lock:
                    # outbound tele
                    if states["Telekill Infinite"] and packet.udp and packet.direction == pydivert.Direction.OUTBOUND and 24 <= packet.udp.payload_len <= 68:
                        packet_tele.append(packet); counters['tele_held'] += 1; handled = True
                    # outbound ghost
                    elif states["Ghost Hack"] and packet.udp and packet.direction == pydivert.Direction.OUTBOUND and 50 <= packet.udp.payload_len <= 300:
                        packet_ghost.append(packet); counters['ghost_held'] += 1; handled = True
                    # inbound freeze
                    elif states["Freeze Enemy"] and packet.udp and packet.direction == pydivert.Direction.INBOUND and packet.udp.payload_len >= 25:
                        packet_freeze.append(packet); counters['freeze_held'] += 1; handled = True
                if not handled:
                    try:
                        w.send(packet)
                        counters['total_forwarded'] += 1
                    except Exception:
                        pass
    except Exception as e:
        print("divert_loop error:", e)

# ============ TOGGLE HANDLERS ============
def toggle_feature(name):
    """Toggle on/off and play beep. If toggled off, flush stored packets (non-blocking)."""
    with lock:
        new = not states[name]
        states[name] = new

    if new:
        beep_on()
    else:
        beep_off()
        # flush corresponding queue by launching a sender thread (non-blocking)
        if name == "Telekill Infinite":
            send_list = deque()
            with lock:
                while packet_tele:
                    send_list.append(packet_tele.popleft()); counters['tele_sent'] += 1
            if send_list:
                threading.Thread(target=send_packets_from_list, args=(send_list, FILTER_TELE), daemon=True).start()
        elif name == "Ghost Hack":
            send_list = deque()
            with lock:
                while packet_ghost:
                    send_list.append(packet_ghost.popleft()); counters['ghost_sent'] += 1
            if send_list:
                threading.Thread(target=send_packets_from_list, args=(send_list, FILTER_GHOST), daemon=True).start()
        elif name == "Freeze Enemy":
            send_list = deque()
            with lock:
                while packet_freeze:
                    send_list.append(packet_freeze.popleft()); counters['freeze_sent'] += 1
            if send_list:
                threading.Thread(target=send_packets_from_list, args=(send_list, FILTER_FREEZE), daemon=True).start()

def set_hotkey_for(name):
    """Capture a single key press and set as hotkey"""
    print(f"Press a key to assign for '{name}', or ESC to cancel...")
    # wait for a keydown event
    while True:
        event = keyboard.read_event(suppress=False)
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'esc':
                print("hotkey set cancelled.")
                return None
            print(f"Assigned {event.name} to {name}")
            return event.name

# background thread to listen for hotkeys (non-blocking)
def hotkey_listener():
    global running              # <--- ensure global declared before use
    while running:
        try:
            event = keyboard.read_event(suppress=False)
            if event.event_type == keyboard.KEY_DOWN:
                # exit keys
                if event.name in ('esc', 'f10'):
                    running = False
                    break
                for name, key in hotkeys.items():
                    if key and event.name == key:
                        toggle_feature(name)
        except Exception:
            time.sleep(0.01)

# ============ ImGui UI ============
def impl_glfw_init(window_title="I love speed"):
    if not glfw.init():
        print("Could not initialize GLFW")
        return None
    # Window hint for gl version
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL.GL_TRUE)

    window = glfw.create_window(800, 560, window_title, None, None)
    glfw.make_context_current(window)
    return window

def imgui_mainloop():
    imgui.create_context()
    window = impl_glfw_init("I love speed")
    impl = GlfwRenderer(window)

    # start backend threads
    t_divert = threading.Thread(target=divert_loop, daemon=True)
    t_divert.start()
    t_hot = threading.Thread(target=hotkey_listener, daemon=True)
    t_hot.start()

    global running
    last_update = time.time()
    while not glfw.window_should_close(window) and running:
        glfw.poll_events()
        impl.process_inputs()
        GL.glClearColor(0.1, 0.105, 0.11, 1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        imgui.new_frame()

        # Main control window (title text changed here too)
        imgui.set_next_window_size(780, 520, imgui.FIRST_USE_EVER)
        imgui.begin("I love speed - Control Panel", True)

        # Toggle buttons
        imgui.text("Features:")
        for name in ["Freeze Enemy", "Ghost Hack", "Telekill Infinite"]:
            on = states[name]
            changed, _ = imgui.checkbox(name, on)
            # ImGui checkboxes don't automatically change our state reference, so:
            if changed:
                toggle_feature(name)

            imgui.same_line()
            imgui.text(f" Hotkey: {hotkeys.get(name) or '-'}")
            imgui.same_line()
            if imgui.button(f"Set Hotkey##{name}"):
                # blocking capture (simple); in a real app you'd want non-blocking capture
                assigned = set_hotkey_for(name)
                if assigned:
                    hotkeys[name] = assigned

        imgui.separator()

        # Counters panel
        imgui.text("Packet counters (approx):")
        imgui.columns(3, "counts", border=True)
        imgui.text(f"Tele Held: {counters['tele_held']}")
        imgui.next_column()
        imgui.text(f"Ghost Held: {counters['ghost_held']}")
        imgui.next_column()
        imgui.text(f"Freeze Held: {counters['freeze_held']}")
        imgui.next_column()
        imgui.text(f"Tele Sent: {counters['tele_sent']}")
        imgui.next_column()
        imgui.text(f"Ghost Sent: {counters['ghost_sent']}")
        imgui.next_column()
        imgui.text(f"Freeze Sent: {counters['freeze_sent']}")
        imgui.columns(1)

        imgui.separator()
        imgui.text(f"Total forwarded: {counters['total_forwarded']}")
        imgui.text(f"Packets queues sizes: Tele {len(packet_tele)} Ghost {len(packet_ghost)} Freeze {len(packet_freeze)}")

        imgui.separator()
        if imgui.button("Flush All Queues (send)"):
            # flush each queue (non-blocking threads)
            with lock:
                send_list = deque()
                while packet_tele:
                    send_list.append(packet_tele.popleft()); counters['tele_sent'] += 1
            if send_list:
                threading.Thread(target=send_packets_from_list, args=(send_list, FILTER_TELE), daemon=True).start()

            with lock:
                send_list = deque()
                while packet_ghost:
                    send_list.append(packet_ghost.popleft()); counters['ghost_sent'] += 1
            if send_list:
                threading.Thread(target=send_packets_from_list, args=(send_list, FILTER_GHOST), daemon=True).start()

            with lock:
                send_list = deque()
                while packet_freeze:
                    send_list.append(packet_freeze.popleft()); counters['freeze_sent'] += 1
            if send_list:
                threading.Thread(target=send_packets_from_list, args=(send_list, FILTER_FREEZE), daemon=True).start()

        imgui.same_line()
        if imgui.button("Clear Counters"):
            for k in counters: counters[k] = 0

        imgui.separator()
        imgui.text("Notes:")
        imgui.text_wrapped("https://guns.lol/speedx4.")

        imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

        # small sleep so UI remains responsive
        time.sleep(0.01)

    # cleanup
    running = False
    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    try:
        imgui_mainloop()
    except KeyboardInterrupt:
        running = False
        print("Exiting...")