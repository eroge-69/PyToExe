import requests
import subprocess
import shlex
import re
import os
import shutil

# ANSI escape code for coloring the terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
RESET = '\033[0m'  # Reset color to default

# Function to fetch subtitles data from the given URL
def fetch_subtitles(sub_url):
    try:
        sub_response = requests.get(sub_url)
        sub_response.raise_for_status()  # Raise HTTPError for bad status codes
        sub_json_data = sub_response.json()
        return sub_json_data
    except requests.RequestException as e:
        print(f"Failed to fetch subtitles: {e}")
        return None

# Function to download subtitle using yt-dlp
def download_subtitle(subtitle_url, title_name, ep, ep_name, lang_code, input_folder):
    try:
        subtitle_response = requests.get(subtitle_url)
        subtitle_response.raise_for_status()
        subtitle_content = subtitle_response.text

        subtitle_file = os.path.join(f"{title_name}.EP-{ep}.{lang_code}.srt")

        command = [
            ".\\Tools\\yt-dlp.exe",
            "--paths", input_folder,
            subtitle_url,
            "--output", subtitle_file,
            "--quiet",
            "--no-warnings",
            "--no-progress"
        ]
        print("Subprocess Command:", ' '.join(shlex.quote(arg) for arg in command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            print(line.strip())
        process.wait()
        print(GREEN + "Download completed.\n" + RESET)
    except requests.RequestException as e:
        print(f"Failed to fetch subtitle content: {e}")

# Function to process M3U8 URL and download the video using yt-dlp
def process_m3u8_url(m3u8_url, title_name, ep, ep_name, series_language, input_folder):
    pattern = r'&layer=Layer\d+'
    modified_url = re.sub(pattern, "&layer=Layer4", m3u8_url)

    duration_index = modified_url.find("&duration=")
    policy_index = modified_url.find("&Policy=")

    # Assign a default value to video_file
    video_file = os.path.join(input_folder, f"{title_name}.EP-{ep}.mp4")

    if duration_index != -1 and policy_index != -1 and policy_index > duration_index:
        if "viu_var_thaws.m3u8" in modified_url:
            modified_url = modified_url.replace("viu_var_thaws.m3u8", "viu_thaws.m3u8")

    command = [
        ".\\Tools\\yt-dlp.exe",
        f"{modified_url}",
        "--output", video_file,
        "--no-warnings"
    ]

    subprocess.run(command)

# Function to merge video and subtitle files using MKVToolNix
def merge_files(input_folder, output_file, title_name, ep, ep_name, track_num):
    command = r'.\Tools\mkvmerge.exe'
    args = [
        '--ui-language', 'en',
        '--priority', 'lower',
        '--no-date',
        '--disable-track-statistics-tags',
        '--language', '0:und',
        '--compression', '0:none',
        os.path.join(input_folder, f'{title_name}.EP-{ep}.mp4')
    ]
    files = []
    order_num = []
    MUX_LANGUAGE_MAP = {
        'ko': 'ko',
        'en': 'en',
        'id': 'id',
        'ms': 'ms',
        'my': 'my',
        'th': 'th',
        'zh-hant': 'zh-Hant',
        'zh': 'zh'
    }
    MUX_TITLE_MAP = {
        'ko': 'Korean',
        'en': 'English',
        'id': 'Indonesian',
        'ms': 'Malay',
        'my': 'Burmese (Zawgyi)',
        'th': 'Thai',
        'zh-Hant': 'Chinese (Traditional)',
        'zh': 'Chinese (Simplified)'
    }
    
    # Get list of files in input_folder
    sub_list = [os.path.join(input_folder, filename) for filename in os.listdir(input_folder)]
    
    for i, sub in enumerate(sub_list, start=track_num+1):
        order_num.append(f'{i}:0')
        match = re.search(r"\.([^\.]+)\.srt$", sub, re.IGNORECASE)
        if match:
            match_lang = MUX_LANGUAGE_MAP.get(match.group(1).lower(), 'und')
            title = MUX_TITLE_MAP.get(match_lang, '')
            files.append(f'--language 0:{match_lang} --default-track-flag 0:no --track-name 0:"{title}" --compression 0:none "{sub}"')

    full_command = f'"{command}" {" ".join(args)} {" ".join(files)} --output "{output_file}"'

    try:
        result = subprocess.run(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("Output:", result.stdout.decode())
    except subprocess.CalledProcessError as e:
        print("Error:", e)
        print("Output:", e.output.decode())

# Function to clean up the temporary folder
def clean_temp_folder(input_folder):
    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

# Main function to orchestrate the operations
def main():
    print('''
         
         ██╗   ██╗██╗██╗   ██╗      ██████╗ ██╗     
         ██║   ██║██║██║   ██║      ██╔══██╗██║     
         ██║   ██║██║██║   ██║█████╗██║  ██║██║     
         ╚██╗ ██╔╝██║██║   ██║╚════╝██║  ██║██║     
          ╚████╔╝ ██║╚██████╔╝      ██████╔╝███████╗
           ╚═══╝  ╚═╝ ╚═════╝       ╚═════╝ ╚══════╝                                                                                    
    ===================== V.1.0 =====================                                                                                   
    ''')
    
    sub_base_url = "https://api-gateway-global.viu.com/api/mobile?platform_flag_label=web&area_id=4&language_flag_id=4&r=%2Fvod%2Fdetail&product_id=" 

    # Prompt the user to enter the ID
    id = input("Enter the ID: ")
    sub_url = sub_base_url + id  

    print("-------------------------------------------------------")

    sub_data = fetch_subtitles(sub_url)
    if sub_data:
        title_data = sub_data.get('data', {}).get('series', {}) 
        episode_data = sub_data.get('data', {}).get('current_product', {})
        title_name = title_data.get('name', '').replace(":", ".").replace(" ", ".")
        series_language = title_data.get('series_language', '')
        ep = episode_data.get('number', '')
        ep_name = episode_data.get('synopsis', '').replace(" ", ".")
        stream_id = episode_data.get('ccs_product_id', '') 

        print(f"Series Name: {title_name} \nEP Number: {ep}\nStream ID: {stream_id}\n")    

        subtitle_data = sub_data.get('data', {}).get('current_product', {}).get('subtitle', []) 

        input_folder = "E:\KeepOut\VIU\Temp"
        output_folder = "E:\KeepOut\VIU"

        # Ensure both input and output folders exist
        os.makedirs(input_folder, exist_ok=True)
        os.makedirs(output_folder, exist_ok=True)

        for url_object in subtitle_data:
            lang_code = url_object["code"]
            lang_name = url_object["name"]
            subtitle_url = url_object["subtitle_url"]

            print(BLUE + "Language Name: " + RESET + f"{lang_name} " + BLUE + "Subtitle URL: " + RESET + f"{subtitle_url}")

            download_subtitle(subtitle_url, title_name, ep, ep_name, lang_code, input_folder)

        # Take URL input from the user
        m3u8_url = input("Enter M3U8 URL: ")
        process_m3u8_url(m3u8_url, title_name, ep, ep_name, series_language, input_folder)
        
        # Merge files
        output_file = os.path.join(output_folder, f'{title_name} EP - {ep} - 3vilr4gn4r0k.mkv')
        track_num = 0
        merge_files(input_folder, output_file, title_name, ep, ep_name, track_num)

        # Clean the Temp folder after processing
        clean_temp_folder(input_folder)
        
if __name__ == "__main__":
    main()
