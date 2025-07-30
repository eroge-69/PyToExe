# ? Libraries
import subprocess
from subprocess import TimeoutExpired
import logging
import serial
import json
import os
import platform
import sys
import configparser

# ? Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("video_log.txt"), logging.StreamHandler(sys.stdout)],
)

# ? Read settings from the config file
config = configparser.ConfigParser()
config.read("settings.ini")

# ? Prompt the user for a video folder if not specified in the settings file
if "Paths" not in config:
    config["Paths"] = {}
if "video_folder" not in config["Paths"]:
    default_video_folder = "./media"
    video_folder = input(
        f"Enter the path to the video folder (default: {default_video_folder}): "
    )
    video_folder = video_folder.strip() or default_video_folder
    config["Paths"]["video_folder"] = video_folder

# ? Prompt the user for Arduino serial port if not specified in the settings file
if "Serial" not in config:
    config["Serial"] = {}
if "serial_port" not in config["Serial"]:
    serial_port = input("Enter the Arduino Serial Port (e.g., COM3): ")
    config["Serial"]["serial_port"] = serial_port

# ? Prompt the user for baudrate if not specified in the settings file
if "baudrate" not in config["Serial"]:
    baudrate = input("Enter the baud rate (default: 9600): ")
    baudrate = int(baudrate) if baudrate.isdigit() else 9600
    config["Serial"]["baudrate"] = str(baudrate)

# ? Prompt the user for media player path if not specified in the settings file
if "Paths" not in config or "media_player_path" not in config["Paths"]:
    media_player_path = input("Enter the path to the media player executable file: ")
    config["Paths"]["media_player_path"] = media_player_path

# ? Prompt the user for stop number if not specified in the settings file
if "Stop" not in config:
    config["Stop"] = {}
if "stop_number" not in config["Stop"]:
    stop_number = input("Enter the desired number to use to stop the program: ")
    config["Stop"]["stop_number"] = stop_number

# ? Save the updated settings to the config file
with open("settings.ini", "w") as configfile:
    config.write(configfile)

# ? Get values from the settings file
video_folder = config.get("Paths", "video_folder")
serial_port = config.get("Serial", "serial_port")
baudrate = config.getint("Serial", "baudrate")
media_player_path = config.get("Paths", "media_player_path")
stop_number = config.get("Stop", "stop_number")

# ? Generate video mapping from the files in the video folder
video_mapping = {}
for root, dirs, files in os.walk(video_folder):
    for index, file in enumerate(files):
        number = str(index + 1)
        video_mapping[number] = os.path.join(root, file)

# ? Save video mapping to a JSON file
with open("video_mapping.json", "w") as file:
    json.dump(video_mapping, file)

# ? Minimize the terminal window
if platform.system() == "Windows":
    subprocess.call(
        'powershell -command "$shell = New-Object -ComObject Shell.Application"'
        ';$shell.minimizeall()"',
        shell=True,
    )
elif platform.system() == "Linux":
    subprocess.call("xdotool getactivewindow windowminimize", shell=True)

current_number = None
current_process = None
play_background = 1

# ? Open the serial port connection
serial_port_value = config.get("Serial", "serial_port")

while True:
    try:
        serial_port = serial.Serial(serial_port_value, baudrate, timeout=1)
        break  # Break the loop if the serial port is successfully opened
    except serial.SerialException as e:
        logging.error(f"Error opening serial port: {e}")
        # Prompt the user for a new serial port if it's not specified in the settings file
        if serial_port_value:
            serial_port_value = input("Enter the Arduino Serial Port (e.g., COM3): ")
        else:
            break  # Break the loop if there's no serial port specified in the settings file

if serial_port is None:
    # Prompt the user for a serial port if it's not specified in the settings file or if the port couldn't be opened
    serial_port_value = input("Enter the Arduino Serial Port (e.g., COM3): ")
    serial_port = serial.Serial(serial_port_value, baudrate)

while True:

    # play the background video (video #8) if no video is playing (play_background == 1)
    if play_background is 1:
        # ? Get the video file for the current number
        play_background = 0
        default_video = video_mapping.get("8")
        if default_video:
            logging.info(f"Number: {number} - Playing video: {default_video}")
            # ? Open the video in fullscreen mode
            try:
                current_process = subprocess.Popen(
                    [media_player_path, "--fullscreen", default_video]
                )
            except Exception as e:
                logging.error(f"Error playing video: {e}")
        else:
            logging.info(f"No video found for the number: {number}")
            break


    # ? Read a line from the serial port
    try:
        current_number = None
        line = serial_port.read().decode().strip()
        logging.info(f"serial data: {line}")
    except Exception as e:
        logging.error(f"Error reading from serial port: {e}")
        serial_port.close()

        # ? Search for the serial port again based on the value stored in the settings file
        serial_port_value = config.get("Serial", "serial_port")

        while True:
            try:
                serial_port = serial.Serial(serial_port_value, baudrate)
                break  # ? Break the loop if the serial port is successfully opened
            except serial.SerialException as e:
                logging.error(f"Error opening serial port: {e}")
                # ? Prompt the user for a new serial port if it's not specified in the settings file
                if serial_port_value:
                    serial_port_value = input(
                        "Enter the Arduino Serial Port (e.g., COM3): "
                    )
                else:
                    break  # ? Break the loop if there's no serial port specified in the settings file

        continue

    # ? Check if the received line is the stop number
    if line == stop_number:
        logging.info(f"Number: {line} - Stopping the program.")
        # ? Stop the current video if one is playing
        if current_process is not None:
            current_process.terminate()
            current_process.wait()  # ? Wait for the process to finish
        break

    try:
        # ? Convert the received data to an integer
        number = int(line)
    except ValueError:
        # ? Skip non-integer values
        logging.error(f"Received non-integer value: {line}")
        if current_process is not None:
            try:
                # Check if playing the video is finnished
                outs, errs = current_process.communicate(timeout=1)
                retCode = current_process.returncode
                logging.info(f"return code: {retCode}")
                play_background = 1     # if video is played, the play_background is set to play the background video
            except TimeoutExpired:
                continue
        continue

    # ? Convert the number to string for video mapping
    number = str(number)

    # ? Check if the number has changed
    if number != current_number:
        current_number = number

        # ? Stop the current video if one is playing
        if current_process is not None:
            logging.info("Stopping the current video...")
            current_process.terminate()
            current_process.wait()  # ? Wait for the process to finish

        # ? Get the video file for the current number
        current_video = video_mapping.get(number)
        if current_video:
            logging.info(f"Number: {number} - Playing video: {current_video}")
            # ? Open the video in fullscreen mode
            try:
                current_process = subprocess.Popen(
                    [media_player_path, "--fullscreen", current_video]
                )
            except Exception as e:
                logging.error(f"Error playing video: {e}")
        else:
            logging.info(f"No video found for the number: {number}")
            break

# ? Close the serial port connection
serial_port.close()
