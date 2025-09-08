import os
import dearpygui.dearpygui as dpg

LOG_FILE = "submissions.txt"
SCALE = 1.6  # 1.0 = default. Try 1.4–2.0 for bigger UI

def is_plausible_email(s: str) -> bool:
    s = s.strip()
    return "@" in s and "." in s.split("@")[-1]

def submit_callback(sender, app_data, user_data):
    first = dpg.get_value("first_name").strip()
    last = dpg.get_value("last_name").strip()
    email = dpg.get_value("email").strip()

    if not first or not last or not is_plausible_email(email):
        dpg.configure_item("status", default_value="Please fill all fields and provide a valid email.", color=(200, 40, 40))
        return

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{first},{last},{email}\n")
        msg = f"Saved: {first} {last} <{email}> → {os.path.abspath(LOG_FILE)}"
        print(msg)
        dpg.configure_item("status", default_value=msg, color=(40, 150, 60))
    except Exception as e:
        dpg.configure_item("status", default_value=f"Failed to write: {e}", color=(200, 40, 40))

dpg.create_context()
dpg.create_viewport(title="Simple Form", width=720, height=360)

# Bigger fonts & spacing
dpg.set_global_font_scale(SCALE)
with dpg.theme() as big_theme:
    with dpg.theme_component(dpg.mvAll):
        dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 20, 16)
        dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 14, 10)
        dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 12, 8)

with dpg.window(tag="main", label="Contact Info"):
    # Wider input fields
    field_width = 420

    dpg.add_input_text(label="First name", hint="Ada", tag="first_name", width=field_width)
    dpg.add_input_text(label="Last name",  hint="Lovelace", tag="last_name", width=field_width)
    dpg.add_input_text(label="Email",      hint="ada@example.com", tag="email", width=field_width)
    dpg.add_separator()
    dpg.add_button(label="Submit", callback=submit_callback, width=120, height=36)
    dpg.add_spacer(height=8)
    dpg.add_text("", tag="status")

dpg.bind_theme(big_theme)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("main", True)
dpg.start_dearpygui()
dpg.destroy_context()
