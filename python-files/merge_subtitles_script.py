
from datetime import timedelta, datetime
import re
import os

subtitle_parts = [
    ("part1.srt", "00:00:00"),
    ("part2.srt", "00:47:14"),
    ("part3.srt", "01:37:28"),
    ("part4.srt", "02:29:55")
]

folder_path = r"C:\Users\asus\OneDrive\Desktop\the_hunt_srt"
output_file = os.path.join(folder_path, "merged_subtitles.srt")

def parse_timestamp(ts):
    return datetime.strptime(ts, "%H:%M:%S")

def shift_timestamp(original, offset):
    t = datetime.strptime(original, "%H:%M:%S,%f")
    return (t + offset).strftime("%H:%M:%S,%f")[:-3]

def adjust_srt(file_path, offset_seconds):
    adjusted_lines = []
    offset = timedelta(seconds=offset_seconds)
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            match = re.match(r"(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})", line)
            if match:
                start, end = match.groups()
                new_start = shift_timestamp(start, offset)
                new_end = shift_timestamp(end, offset)
                adjusted_lines.append(f"{new_start} --> {new_end}\n")
            else:
                adjusted_lines.append(line)
    return adjusted_lines

def main():
    final_output = []
    for srt_file, start_time in subtitle_parts:
        full_path = os.path.join(folder_path, srt_file)
        if not os.path.exists(full_path):
            print(f"❌ File not found: {srt_file}")
            continue
        start_seconds = (parse_timestamp(start_time) - parse_timestamp("00:00:00")).total_seconds()
        print(f"✅ Processing {srt_file} with offset {start_time}")
        adjusted = adjust_srt(full_path, start_seconds)
        final_output.extend(adjusted)
        final_output.append("\n")

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.writelines(final_output)

    print(f"🎉 Merged subtitles saved as: {output_file}")

if __name__ == "__main__":
    main()
