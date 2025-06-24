# ALEX.py (Main Integrated Launcher)

import time
from core.listen_google import listen
from core.speak_interrupt import speak
from feature.system_monitor import show_system_status
from feature.memory_mode import remember_fact, recall_fact
from feature.ai_planner import plan_day
from feature.self_heal import handle_error
from feature.file_ops import create_folder, delete_file, download_file
from feature.launch_app import open_app, search_web
from feature.nasa_alert import check_nasa_alerts
from feature.satellite_weather import get_satellite_weather
from feature.search_and_time import tell_time
from feature.typing import type_text
from feature.whatsapp_messenger import send_message_to
# You can add more features like Telegram integration, Firebase login etc.

def run_alex():
    speak("Hello Sir, Alex ready for your command.")
    while True:
        command = listen()

        if not command:
            continue

        try:
            if 'system status' in command:
                show_system_status()

            elif 'my name is' in command:
                remember_fact(command)

            elif 'what is my name' in command:
                recall_fact()

            elif 'plan my day' in command:
                plan_day()

            elif 'create folder' in command:
                folder_name = command.replace('create folder', '').strip()
                create_folder(folder_name)

            elif 'delete file' in command:
                file_path = command.replace('delete file', '').strip()
                delete_file(file_path)

            elif 'download' in command:
                url = command.split("download")[-1].strip()
                download_file(url)

            elif 'open' in command:
                app = command.replace('open', '').strip()
                open_app(app)

            elif 'search' in command:
                query = command.replace('search', '').strip()
                search_web(query)

            elif 'send message to' in command:
                send_message_to(command)

            elif 'type' in command:
                text = command.split("type")[-1].strip()
                type_text(text)

            elif 'nasa alert' in command:
                check_nasa_alerts()

            elif 'weather' in command:
                get_satellite_weather()

            elif 'time' in command:
                tell_time()

            elif 'stop' in command or 'exit' in command or 'bye' in command:
                speak("Goodbye sir, shutting down.")
                break

            else:
                speak("Sorry, I can't process that command.")

        except Exception as e:
            handle_error(e)

if __name__ == "__main__":
    run_alex()