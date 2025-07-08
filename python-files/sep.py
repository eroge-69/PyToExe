import os
import sys
import requests
import json
import argparse
import subprocess
import signal
import csv
from datetime import datetime

CACHE_FILE_PATTERN = "cache-{server}-{data_type}.json"
CREDENTIALS_FILE = "saved_credentials.json"
DEBUG_MODE = False  # Default: Debugging is off


def debug_log(message):
    """
    Logs a debug message if debugging is enabled.
    """
    if DEBUG_MODE:
        print(f"[DEBUG] {message}")


def load_credentials():
    """Loads saved credentials from a JSON file."""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                return json.load(f)
        except (OSError, IOError, json.JSONDecodeError) as e:
            print(f"Error reading credentials file: {e}", file=sys.stderr)
    return []


def save_credentials(credentials_list):
    """Saves the list of credentials to a JSON file."""
    try:
        with open(CREDENTIALS_FILE, 'w') as f:
            json.dump(credentials_list, f)
    except (OSError, IOError) as e:
        print(f"Error saving credentials file: {e}", file=sys.stderr)


def get_credentials_interactively(saved_credentials):
    """Gets server credentials interactively, allowing selection of saved ones."""
    print("\nSaved Server Configurations:")
    if saved_credentials:
        for i, cred in enumerate(saved_credentials):
            masked_server = f"{'.'.join(['xxxxx'] + cred['server'].split('.')[1:])}"
            print(f"{i + 1}. Server: {masked_server}, User: {cred['user']}")
        print("0. Enter new credentials")

        while True:
            choice = input(
                "Choose a saved configuration (1-{}) or 0 to enter new: ".format(len(saved_credentials))
            ).strip()
            if choice.isdigit():
                index = int(choice)
                if 1 <= index <= len(saved_credentials):
                    return saved_credentials[index - 1]['server'], saved_credentials[index - 1]['user'], saved_credentials[index - 1]['password'], True
                elif index == 0:
                    server = input("Enter Xtream server address: ")
                    user = input("Enter username: ")
                    password = input("Enter password: ")
                    return server, user, password, False
            print("Invalid choice. Please try again.")
    else:
        server = input("Enter Xtream server address: ")
        user = input("Enter username: ")
        password = input("Enter password: ")
        return server, user, password, False


def load_cache(server, data_type):
    """Load data from the cache file if it exists and is up-to-date."""
    debug_log(f"Attempting to load cache for {data_type} on server {server}")
    cache_file = CACHE_FILE_PATTERN.format(server=server, data_type=data_type)
    if os.path.exists(cache_file):
        # Check if the cache file was created today
        file_date = datetime.fromtimestamp(os.path.getmtime(cache_file)).date()
        if file_date == datetime.today().date():
            try:
                with open(cache_file, 'r') as file:
                    return json.load(file)
            except (OSError, IOError, json.JSONDecodeError) as e:
                print(f"Error reading cache file {cache_file}: {e}", file=sys.stderr)
    return None


def save_cache(server, data_type, data):
    """Save data to the cache file."""
    debug_log(f"Attempting to save cache for {data_type} on server {server}")
    cache_file = CACHE_FILE_PATTERN.format(server=server, data_type=data_type)
    try:
        with open(cache_file, 'w') as file:
            json.dump(data, file)
    except (OSError, IOError) as e:
        print(f"Error saving cache file {cache_file}: {e}", file=sys.stderr)


def download_data(server, user, password, endpoint, additional_params=None):
    """Download data from the Xtream IPTV server."""
    debug_log(f"Downloading data from {server}, endpoint: {endpoint}")
    url = f"http://{server}/player_api.php"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }
    params = {"username": user, "password": password, "action": endpoint}
    if additional_params:
        params.update(additional_params)
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        debug_log(f"Response from server ({endpoint}): {response.text[:500]}")  # Print first 500 characters
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch {endpoint} data: {e}", file=sys.stderr)
        sys.exit(1)



def check_epg(server, user, password, stream_id):
    """Check EPG data for a specific channel."""
    debug_log(f"Checking EPG for stream ID {stream_id}")
    epg_data = download_data(server, user, password, "get_simple_data_table", {"stream_id": stream_id})

    if isinstance(epg_data, dict) and epg_data.get("epg_listings"):
        return len(epg_data["epg_listings"])  # Return the count of EPG entries

    elif isinstance(epg_data, list):
        debug_log(f"Unexpected list response for EPG data: {epg_data}")
        return len(epg_data)  # Return the length of the list

    else:
        debug_log(f"Unexpected EPG response type: {type(epg_data)}")
        return 0  # No EPG data available



def filter_data(live_categories, live_streams, group, channel):
    """Filter the live streams based on group and channel arguments."""
    filtered_streams = []
    group = group.lower() if group else None
    channel = channel.lower() if channel else None

    for stream in live_streams:
        # Filter by group if specified
        if group:
            matching_categories = [cat for cat in live_categories if group in cat["category_name"].lower()]
            if not any(cat["category_id"] == stream["category_id"] for cat in matching_categories):
                continue
        # Filter by channel if specified
        if channel and channel not in stream["name"].lower():
            continue
        # Add the stream to the filtered list
        filtered_streams.append(stream)

    return filtered_streams



def check_ffprobe():
    """
    Checks if the ffprobe command is available on the system.
    Exits the program with an error message if not found.
    """
    try:
        subprocess.run(
            ["ffprobe", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
        debug_log("ffprobe is installed and reachable.")
    except FileNotFoundError:
        print(
            "Error: ffprobe is not installed or not found in the system PATH. Please install ffprobe before running this program."
        )
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Error: ffprobe check failed with error: {e}")
        sys.exit(1)



def check_channel(url, bitrate_check_duration=10):
    """
    Checks stream details (codec, resolution, frame rate) using ffprobe and
    estimates bitrate using ffmpeg by analyzing the stream with VLC user-agent.

    Args:
        url (str): The URL of the stream.
        bitrate_check_duration (int): The duration in seconds to analyze for bitrate estimation. Defaults to 10.

    Returns:
        dict: A dictionary containing stream status and details, including estimated bitrate.
    """
    stream_info = {"status": "not working", "bitrate": "N/A"}

    try:
        # Use ffprobe to get basic stream information
        ffprobe_command = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=codec_name,width,height,avg_frame_rate",
            "-of",
            "json",
            url,
        ]
        ffprobe_result = subprocess.run(
            ffprobe_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=10
        )
        ffprobe_output = json.loads(ffprobe_result.stdout)

        if 'streams' in ffprobe_output and len(ffprobe_output['streams']) > 0:
            video_stream = ffprobe_output['streams'][0]
            codec_name = video_stream.get('codec_name', 'Unknown')[:5]
            width = video_stream.get('width', 'Unknown')
            height = video_stream.get('height', 'Unknown')
            avg_frame_rate = video_stream.get('avg_frame_rate', 'Unknown')

            frame_rate = "Unknown"
            if avg_frame_rate != 'Unknown' and '/' in avg_frame_rate:
                num, denom = map(int, avg_frame_rate.split('/'))
                frame_rate = round(num / denom) if denom != 0 else "Unknown"
            else:
                frame_rate = avg_frame_rate

            stream_info.update(
                {
                    "status": "working",
                    "codec_name": codec_name,
                    "width": width,
                    "height": height,
                    "frame_rate": frame_rate,
                }
            )
        else:
            debug_log(f"No video stream found for URL: {url}")
            return stream_info

        # Use ffmpeg to estimate bitrate with VLC user-agent and null output
        ffmpeg_command = [
            'ffmpeg',
            '-v',
            'debug',
            '-user_agent',
            'VLC/3.0.14',
            '-i',
            url,
            '-t',
            str(bitrate_check_duration),
            '-f',
            'null',
            '-',
        ]
        ffmpeg_result = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15)

        if ffmpeg_result.returncode == 0:
            error_output = ffmpeg_result.stderr.decode(errors='ignore')
            debug_log(f"ffmpeg stderr output:\n{error_output}")  # Print for debugging

            total_bytes = 0
            for line in error_output.splitlines():
                if "Statistics:" in line and "bytes read" in line:
                    parts = line.split("bytes read")
                    size_str = parts[0].strip().split()[-1]
                    if size_str.isdigit():
                        total_bytes = int(size_str)
                        break  # Exit loop after finding bytes read

            if total_bytes > 0:
                bitrate_kbps = (total_bytes * 8) / 1000 / bitrate_check_duration
                stream_info["bitrate"] = f"{round(bitrate_kbps)} kbps"
            else:
                stream_info["bitrate"] = "N/A"  # No bytes read
        else:
            error_output = ffmpeg_result.stderr.decode(errors='ignore')
            debug_log(
                f"ffmpeg bitrate check failed for {url}: Return Code: {ffmpeg_result.returncode}, Error Output: {error_output}"
            )
            stream_info["bitrate"] = "N/A"

    except FileNotFoundError:
        print("Error: ffmpeg and/or ffprobe are not installed or not found in the system PATH.")
        stream_info["bitrate"] = "N/A"
    except subprocess.TimeoutExpired as e:
        debug_log(f"Timeout during bitrate check for {url}: {e}")
        stream_info["bitrate"] = "Timeout"
    except Exception as e:
        debug_log(f"Error during bitrate check for {url}: {e}")
        stream_info["bitrate"] = "Error"

    return stream_info


def save_to_csv(file_name, data, fieldnames):
    """
    Save data to a CSV file, ensuring all fields are enclosed in double quotes.

    :param file_name: The name of the CSV file to save.
    :param data: A list of dictionaries containing the data to write.
    :param fieldnames: A list of field names for the CSV header.
    """
    try:
        with open(file_name, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(data)
        print(f"Output saved to {file_name}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")


def handle_sigint(signal, frame):
    """Handle Ctrl+C gracefully."""
    print("\nProgram interrupted by user. Exiting...")
    sys.exit(0)


def main():
    global DEBUG_MODE

    # Set up the signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_sigint)

    while True:  # Keep looping
        parser = argparse.ArgumentParser(description="Xtream IPTV Downloader and Filter")
        parser.add_argument("--debug", action="store_true", help="Enable debug mode.")
        args = parser.parse_args()

        # Enable debug mode if the --debug flag is present
        DEBUG_MODE = args.debug
        debug_log("Debug mode enabled")

        # Load saved credentials
        saved_credentials = load_credentials()

        # Get server credentials interactively
        server, user, password, used_saved = get_credentials_interactively(saved_credentials)

        # If new credentials were entered, add them to the list and save
        if not used_saved:
            new_credential = {"server": server, "user": user, "password": password}
            saved_credentials.append(new_credential)
            # Remove duplicates if any (optional, based on your preference)
            unique_credentials = []
            seen = set()
            for cred in saved_credentials:
                key = (cred['server'], cred['user'])
                if key not in seen:
                    unique_credentials.append(cred)
                    seen.add(key)
            save_credentials(unique_credentials)

        nocache = input("Force download and ignore cache? (y/n): ").lower() == "y"
        channel = input("Filter by channel name (or leave blank): ")
        category = input("Filter by category name (or leave blank): ")
        epgcheck = input("Check EPG data? (y/n): ").lower() == "y"
        
        # Separate questions for resolution and bitrate
        check_resolution = input("Check stream resolution (e.g., 1920x1080)? (y/n): ").lower() == "y"
        check_bitrate = input("Check stream bitrate (estimates data transfer rate)? (y/n): ").lower() == "y"

        bitrate_duration = 10 # Default
        if check_bitrate:
            bitrate_duration = int(input("Enter bitrate check duration in seconds (default: 10): ") or 10)

        save_file = input("Enter CSV file name to save output be sure to include .CSV at end (or leave blank): ")

        # Determine if any stream checks are needed
        perform_stream_checks = check_resolution or check_bitrate

        # Print the date and time when the program is run
        masked_server = f"{'.'.join(['xxxxx'] + server.split('.')[1:])}"
        run_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        print(f"\n\nfind-iptv-channels-details - Running for server {masked_server} on {run_time}\n")

        # Check ffprobe if any stream checks are enabled
        if perform_stream_checks:
            check_ffprobe()

        # Check cache or download data
        live_categories = load_cache(server, "live_categories") if not nocache else None
        live_streams = load_cache(server, "live_streams") if not nocache else None

        if not live_categories or not live_streams:
            live_categories = download_data(server, user, password, "get_live_categories")
            live_streams = download_data(server, user, password, "get_live_streams")
            save_cache(server, "live_categories", live_categories)
            save_cache(server, "live_streams", live_streams)

        # Filter data
        filtered_streams = filter_data(live_categories, live_streams, category, channel)

        # Prepare CSV data and headers
        csv_data = []
        # Adjust fieldnames based on what's actually checked
        fieldnames = ["Stream ID", "Name", "Category", "Archive", "EPG"]
        if check_resolution:
            fieldnames.extend(["Codec", "Resolution", "Frame Rate"])
        if check_bitrate:
            fieldnames.append("Bitrate")

        # Print and collect results
        # Dynamically build the header string
        header_parts = [
            f"{'ID':<10}",
            f"{'Name':<60}",
            f"{'Category':<40}",
            f"{'Archive':<8}",
            f"{'EPG':<5}"
        ]
        if check_resolution:
            header_parts.extend([
                f"{'Codec':<8}",
                f"{'Resolution':<15}",
                f"{'Frame':<10}"
            ])
        if check_bitrate:
            header_parts.append(f"{'Bitrate':<10}")

        header = "".join(header_parts)
        print(header)
        print("=" * len(header)) # Adjust separator length dynamically

        category_map = {cat["category_id"]: cat["category_name"] for cat in live_categories}
        for stream in filtered_streams:
            category_name = category_map.get(stream["category_id"], "Unknown")
            epg_count = (
                check_epg(server, user, password, stream["stream_id"]) if epgcheck else ""
            )
            # Generate stream URL
            stream_url = f"http://{server}/{user}/{password}/{stream['stream_id']}"

            stream_info = {"codec_name": "N/A", "width": "N/A", "height": "N/A", "frame_rate": "N/A", "bitrate": "N/A"}
            if perform_stream_checks:
                # Call check_channel if either resolution or bitrate is requested
                temp_stream_info = check_channel(stream_url, bitrate_check_duration=bitrate_duration)
                # Only update stream_info with relevant details based on user's choice
                if check_resolution:
                    stream_info["codec_name"] = temp_stream_info.get('codec_name', 'N/A')
                    stream_info["width"] = temp_stream_info.get('width', 'N/A')
                    stream_info["height"] = temp_stream_info.get('height', 'N/A')
                    stream_info["frame_rate"] = temp_stream_info.get('frame_rate', 'N/A')
                if check_bitrate:
                    stream_info["bitrate"] = temp_stream_info.get('bitrate', 'N/A')

            resolution_display = f"{stream_info['width']}x{stream_info['height']}" if check_resolution else "N/A"
            bitrate_display = stream_info['bitrate'] if check_bitrate else "N/A"


            # Print to console - dynamically build the print string
            row_parts = [
                f"{stream['stream_id']:<10}",
                f"{stream['name'][:60]:<60}",
                f"{category_name[:40]:<40}",
                f"{stream.get('tv_archive_duration', 'N/A'):<8}",
                f"{epg_count:<5}"
            ]
            if check_resolution:
                row_parts.extend([
                    f"{stream_info['codec_name']:<8}",
                    f"{resolution_display:<15}",
                    f"{stream_info['frame_rate']:<10}"
                ])
            if check_bitrate:
                row_parts.append(f"{bitrate_display:<10}")

            print("".join(row_parts))


            # Collect data for CSV - dynamically add to dictionary
            csv_row = {
                "Stream ID": stream["stream_id"],
                "Name": stream['name'][:60],
                "Category": category_name[:40],
                "Archive": stream.get('tv_archive_duration', 'N/A'),
                "EPG": epg_count,
            }
            if check_resolution:
                csv_row["Codec"] = stream_info['codec_name']
                csv_row["Resolution"] = resolution_display
                csv_row["Frame Rate"] = stream_info['frame_rate']
            if check_bitrate:
                csv_row["Bitrate"] = bitrate_display
            csv_data.append(csv_row)

        print(f"\n")
        # Write to CSV if --save is provided
        if save_file:
            save_to_csv(save_file, csv_data, fieldnames)
        print(f"\n\n")

        repeat = input("Repeat the script? (y/n): ").lower() == "y"
        if not repeat:
            break  # Exit the loop if the user doesn't want to repeat



if __name__ == "__main__":
    main()
