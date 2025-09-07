# pink_menu.py
# Visual-only pink "settings" menu that mimics a cheat-style UI.
# Dependencies: imgui[glfw], PyOpenGL, glfw
#   pip install imgui[glfw] PyOpenGL glfw
#
# Run (dev): python pink_menu.py
# Build EXE (no console, Windows): pyinstaller --noconsole --onefile --name PinkMenu pink_menu.py

import sys
import json
import glfw
import OpenGL.GL as gl
import imgui
from imgui.integrations.glfw import GlfwRenderer

CONFIG_FILE = "pink_menu_config.json"

# --------------------------- Helpers ---------------------------

def apply_pink_theme():
    """A soft pink theme close to your screenshot."""
    s = imgui.get_style()
    # Rounded corners & spacing
    s.window_rounding = 4
    s.frame_rounding = 4
    s.grab_rounding = 4
    s.child_rounding = 4
    s.tab_rounding = 4
    s.item_spacing = (8, 6)
    s.frame_padding = (8, 6)
    s.window_padding = (10, 10)
    s.window_border_size = 1.0
    s.frame_border_size = 1.0
    s.tab_border_size = 1.0

    # Palette (rgba): heavy pinks, light borders
    pink_bg   = (1.00, 0.76, 0.90, 1.00)  # window bg
    pink_mid  = (0.95, 0.58, 0.80, 1.00)  # headers, active
    pink_low  = (0.90, 0.40, 0.70, 1.00)  # accents
    text_col  = (0.10, 0.10, 0.10, 1.00)
    border    = (0.60, 0.25, 0.45, 1.00)
    hover     = (0.98, 0.67, 0.85, 1.00)
    active    = (0.88, 0.30, 0.62, 1.00)
    # Set many key colors
    imgui.push_style_color(imgui.COLOR_TEXT, *text_col)
    imgui.push_style_color(imgui.COLOR_WINDOW_BACKGROUND, *pink_bg)
    imgui.push_style_color(imgui.COLOR_CHILD_BACKGROUND, 1.0, 0.85, 0.93, 1.0)
    imgui.push_style_color(imgui.COLOR_BORDER, *border)
    imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 1.0, 0.83, 0.92, 1.0)
    imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_HOVERED, *hover)
    imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND_ACTIVE, *active)
    imgui.push_style_color(imgui.COLOR_TITLE_BACKGROUND, *pink_mid)
    imgui.push_style_color(imgui.COLOR_TITLE_BACKGROUND_ACTIVE, *pink_low)
    imgui.push_style_color(imgui.COLOR_TITLE_BACKGROUND_COLLAPSED, 0.95, 0.67, 0.84, 1.0)
    imgui.push_style_color(imgui.COLOR_BUTTON, 0.97, 0.70, 0.87, 1.0)
    imgui.push_style_color(imgui.COLOR_BUTTON_HOVERED, *hover)
    imgui.push_style_color(imgui.COLOR_BUTTON_ACTIVE, *active)
    imgui.push_style_color(imgui.COLOR_HEADER, *pink_mid)
    imgui.push_style_color(imgui.COLOR_HEADER_HOVERED, *hover)
    imgui.push_style_color(imgui.COLOR_HEADER_ACTIVE, *active)
    imgui.push_style_color(imgui.COLOR_CHECK_MARK, 0.40, 0.05, 0.20, 1.0)
    imgui.push_style_color(imgui.COLOR_SLIDER_GRAB, 0.75, 0.25, 0.50, 1.0)
    imgui.push_style_color(imgui.COLOR_SLIDER_GRAB_ACTIVE, 0.60, 0.15, 0.40, 1.0)
    imgui.push_style_color(imgui.COLOR_TAB, 0.97, 0.70, 0.87, 1.0)
    imgui.push_style_color(imgui.COLOR_TAB_HOVERED, *hover)
    imgui.push_style_color(imgui.COLOR_TAB_ACTIVE, *active)
    imgui.push_style_color(imgui.COLOR_SEPARATOR, 0.75, 0.35, 0.55, 1.0)
    # Return how many colors we pushed to pop later
    return 20

def labeled_separator(label: str):
    imgui.text_colored(label, 0.25, 0.05, 0.15, 1.0)
    imgui.separator()

def int_slider(label, val, lo, hi):
    changed, f = imgui.slider_int(label, int(val), lo, hi)
    return changed, int(f)

def float_slider(label, val, lo, hi, fmt="%.3f"):
    changed, f = imgui.slider_float(label, float(val), lo, hi, format=fmt)
    return changed, float(f)

# --------------------------- App State ---------------------------

def default_state():
    return {
        # Aimbot tab
        "aim_enabled": True,
        "aim_key": "mouse 4",
        "triggerbot": True,
        "trigger_key": "e",
        "trigger_range": 328,

        "aim_mode": 1,  # 0: mouse, 1: silent, 2: smooth
        "target_select": 1,  # 0: nearest, 1: fov, 2: health
        "smoothing": 0.8,
        "fov": 139,
        "auto_fire": True,
        "engine_prediction": True,
        "recoil_control": 1.000,
        "no_spread": True,
        "target_color": [0.85, 0.25, 0.55],
        "circle_color": [0.75, 0.20, 0.50],
        "line_color":   [0.60, 0.15, 0.40],
        "disable_vischeck": 0,  # [none, basic, strict]
        "targets": {
            "players": True, "friends": False, "autowall": True,
            "only_target_enemies": True, "ignore_same_team": True, "ignore_other_team": False,
            "ignore_selected_team": False, "ignore_invisible": True, "ignore_transparent": True,
            "ignore_noclipping": True, "ignore_dormant": True, "target_lock": False,
            "treat_generic_as_body": True, "head_fallback": True,
            "aim_head": True, "aim_body": True, "aim_legs": False, "aim_arms": False, "aim_generic": True
        },

        # ESP tab
        "esp_enabled": True,
        "esp_players": True,
        "esp_items": True,
        "esp_health": True,
        "esp_boxes": True,
        "esp_box_type": 1,  # 0-edge,1-corners
        "esp_thickness": 1.5,
        "esp_color": [0.85, 0.20, 0.55],

        # Misc tab
        "bhop": True, "auto_strafe": False, "night_mode": True,
        "speed": 72.0, "third_person": False, "custom_crosshair": True,

        # Anti Aim tab (visual-only)
        "aa_enabled": False,
        "aa_pitch": 1,  # 0: up,1: down,2: zero
        "aa_yaw": 2,    # 0: left,1: right,2: spin
        "aa_jitter": 0.3,
        "aa_spin_speed": 2.0,
        "aa_fakelag": 0,
        "aa_desync": False,
        "aa_invert_key": "alt",
        "aa_slow_walk": False,

        # Configs
        "selected_config": 0,
        "configs": ["default", "legit", "rage"]
    }

def save_config(state):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return True
    except Exception as e:
        print("[save_config]", e)
        return False

def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# --------------------------- UI Panels ---------------------------

def tab_aimbot(state):
    imgui.columns(3, "aimbot_cols", border=True)

    # LEFT: state
    labeled_separator("state")
    changed, state["aim_enabled"] = imgui.checkbox("enabled", state["aim_enabled"])
    imgui.text(f"key [{state['aim_key']}]")
    changed, state["triggerbot"] = imgui.checkbox("triggerbot", state["triggerbot"])
    imgui.text(f"triggerbot key [{state['trigger_key']}]")
    _, state["trigger_range"] = int_slider("triggerbot range", state["trigger_range"], 0, 500)

    imgui.next_column()

    # MIDDLE: aiming
    labeled_separator("aiming")
    aim_modes = ["mouse", "silent", "smooth"]
    sel_modes = ["nearest", "fov", "health"]
    _, state["aim_mode"] = imgui.combo("aim mode", state["aim_mode"], aim_modes)
    _, state["target_select"] = imgui.combo("target selection", state["target_select"], sel_modes)
    _, state["smoothing"] = float_slider("smoothing", state["smoothing"], 0.0, 5.0, "%.1f units")
    _, state["fov"] = int_slider("fov", state["fov"], 0, 360)
    _, state["auto_fire"] = imgui.checkbox("auto fire", state["auto_fire"])
    _, state["engine_prediction"] = imgui.checkbox("engine prediction", state["engine_prediction"])
    _, state["recoil_control"] = float_slider("recoil control", state["recoil_control"], 0.0, 3.0)
    _, state["no_spread"] = imgui.checkbox("no spread", state["no_spread"])
    labeled_separator("")
    imgui.text("target color override")
    _, state["target_color"] = imgui.color_edit3("##tcol", *state["target_color"])
    imgui.text("circle color")
    _, state["circle_color"] = imgui.color_edit3("##ccol", *state["circle_color"])
    imgui.text("line color")
    _, state["line_color"] = imgui.color_edit3("##lcol", *state["line_color"])
    dis_vis = ["none", "basic", "strict"]
    _, state["disable_vischeck"] = imgui.combo("disable vischeck", state["disable_vischeck"], dis_vis)

    imgui.next_column()

    # RIGHT: targets
    labeled_separator("targets")
    tg = state["targets"]
    for label in [
        "players", "friends", "autowall", "only target enemies", "ignore same team",
        "ignore other team", "ignore selected team", "ignore invisible",
        "ignore transparent", "ignore noclipping", "ignore dormant", "target lock",
        "treat generic as body", "head fallback",
        "aim at head", "aim at body", "aim at legs", "aim at arms", "aim at generic"
    ]:
        key = label.replace(" ", "_").replace("at_", "")
        # map display label to dict keys used in default_state
        mapping = {
            "players":"players", "friends":"friends", "autowall":"autowall",
            "only_target_enemies":"only_target_enemies", "ignore_same_team":"ignore_same_team",
            "ignore_other_team":"ignore_other_team", "ignore_selected_team":"ignore_selected_team",
            "ignore_invisible":"ignore_invisible", "ignore_transparent":"ignore_transparent",
            "ignore_noclipping":"ignore_noclipping", "ignore_dormant":"ignore_dormant",
            "target_lock":"target_lock", "treat_generic_as_body":"treat_generic_as_body",
            "head_fallback":"head_fallback",
            "aim_head":"aim_head", "aim_body":"aim_body", "aim_legs":"aim_legs",
            "aim_arms":"aim_arms", "aim_generic":"aim_generic"
        }
        k = mapping.get(key, None)
        if k is None:
            # handle "aim at ..." display -> map manually
            disp_to_key = {
                "aim at head":"aim_head",
                "aim at body":"aim_body",
                "aim at legs":"aim_legs",
                "aim at arms":"aim_arms",
                "aim at generic":"aim_generic",
            }
            k = disp_to_key.get(label, None)
        if k is None:
            continue
        _, tg[k] = imgui.checkbox(label, bool(tg.get(k, False)))
    imgui.columns(1)

def tab_esp(state):
    imgui.columns(3, "esp_cols", border=True)

    labeled_separator("state")
    _, state["esp_enabled"] = imgui.checkbox("enabled", state["esp_enabled"])
    _, state["esp_players"] = imgui.checkbox("players", state["esp_players"])
    _, state["esp_items"] = imgui.checkbox("items", state["esp_items"])
    _, state["esp_health"] = imgui.checkbox("health bars", state["esp_health"])
    _, state["esp_boxes"] = imgui.checkbox("boxes", state["esp_boxes"])

    imgui.next_column()
    labeled_separator("style")
    _, state["esp_box_type"] = imgui.combo("box type", state["esp_box_type"], ["edges", "corners", "filled"])
    _, state["esp_thickness"] = float_slider("line thickness", state["esp_thickness"], 0.5, 5.0, "%.1f")
    imgui.text("esp color")
    _, state["esp_color"] = imgui.color_edit3("##espcol", *state["esp_color"])

    imgui.next_column()
    labeled_separator("filters")
    imgui.checkbox("show weapons", True)
    imgui.checkbox("show dropped loot", True)
    imgui.checkbox("show grenades", False)
    imgui.checkbox("show crosshair", True)
    imgui.checkbox("occluded fade", True)
    imgui.columns(1)

def tab_misc(state):
    imgui.columns(3, "misc_cols", border=True)
    labeled_separator("movement")
    _, state["bhop"] = imgui.checkbox("bunnyhop", state["bhop"])
    _, state["auto_strafe"] = imgui.checkbox("auto strafe", state["auto_strafe"])
    _, state["third_person"] = imgui.checkbox("third person", state["third_person"])
    _, state["speed"] = float_slider("speed", state["speed"], 0.0, 200.0, "%.0f")

    imgui.next_column()
    labeled_separator("visual fun")
    _, state["night_mode"] = imgui.checkbox("night mode", state["night_mode"])
    _, state["custom_crosshair"] = imgui.checkbox("custom crosshair", state["custom_crosshair"])
    imgui.checkbox("rainbow ui", False)
    imgui.checkbox("freeze time (fake)", False)

    imgui.next_column()
    labeled_separator("other")
    imgui.checkbox("chat notifier", True)
    imgui.checkbox("fps cap", False)
    imgui.checkbox("screenshot safe mode", True)
    imgui.columns(1)

def tab_antiaim(state):
    imgui.columns(3, "aa_cols", border=True)

    labeled_separator("state")
    _, state["aa_enabled"] = imgui.checkbox("enabled", state["aa_enabled"])
    _, state["aa_pitch"] = imgui.combo("pitch", state["aa_pitch"], ["up", "down", "zero"])
    _, state["aa_yaw"] = imgui.combo("yaw", state["aa_yaw"], ["left", "right", "spin"])

    imgui.next_column()
    labeled_separator("tuning")
    _, state["aa_jitter"] = float_slider("jitter", state["aa_jitter"], 0.0, 2.0)
    _, state["aa_spin_speed"] = float_slider("spin speed", state["aa_spin_speed"], 0.0, 10.0)
    _, state["aa_fakelag"] = int_slider("fake lag", state["aa_fakelag"], 0, 20)

    imgui.next_column()
    labeled_separator("extras")
    _, state["aa_desync"] = imgui.checkbox("desync", state["aa_desync"])
    imgui.text(f"invert key [{state['aa_invert_key']}]")
    _, state["aa_slow_walk"] = imgui.checkbox("slow walk", state["aa_slow_walk"])
    imgui.columns(1)

def tab_configs(state, save_cb, load_cb, reset_cb):
    labeled_separator("configs")
    _, state["selected_config"] = imgui.combo(
        "active config", state["selected_config"], state["configs"]
    )
    if imgui.button("Save Config"):
        save_cb()
    imgui.same_line()
    if imgui.button("Load Config"):
        load_cb()
    imgui.same_line()
    if imgui.button("Reset Defaults"):
        reset_cb()

# --------------------------- Main ---------------------------

def main():
    if not glfw.init():
        sys.exit(1)

    # Create a window (no console is handled at packaging time; see instructions below)
    window = glfw.create_window(980, 620, "settings", None, None)
    if not window:
        glfw.terminate()
        sys.exit(1)
    glfw.make_context_current(window)

    imgui.create_context()
    impl = GlfwRenderer(window)

    state = default_state()
    loaded = load_config()
    if loaded:
        # merge any known keys
        try:
            state.update(loaded)
            # nested targets dict may need merging
            if "targets" in loaded and isinstance(loaded["targets"], dict):
                state["targets"].update(loaded["targets"])
        except Exception:
            pass

    pushed = apply_pink_theme()

    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        # Optional: clear to soft pink
        gl.glClearColor(1.00, 0.76, 0.90, 1.00)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        imgui.set_next_window_size(960, 600, condition=imgui.FIRST_USE_EVER)
        imgui.set_next_window_position(10, 10, condition=imgui.FIRST_USE_EVER)
        imgui.begin("settings", True, imgui.WINDOW_NO_COLLAPSE)

        if imgui.begin_tab_bar("##tabs"):
            if imgui.begin_tab_item("aimbot")[0]:
                tab_aimbot(state)
                imgui.end_tab_item()

            if imgui.begin_tab_item("esp")[0]:
                tab_esp(state)
                imgui.end_tab_item()

            if imgui.begin_tab_item("misc")[0]:
                tab_misc(state)
                imgui.end_tab_item()

            if imgui.begin_tab_item("anti aim")[0]:
                tab_antiaim(state)
                imgui.end_tab_item()

            if imgui.begin_tab_item("configs")[0]:
                tab_configs(
                    state,
                    save_cb=lambda: save_config(state),
                    load_cb=lambda: (state.update(load_config() or {}) if load_config() else None),
                    reset_cb=lambda: state.update(default_state())
                )
                imgui.end_tab_item()
            imgui.end_tab_bar()

        imgui.end()

        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)

    for _ in range(pushed):
        imgui.pop_style_color()

    impl.shutdown()
    glfw.terminate()

if __name__ == "__main__":
    main()
