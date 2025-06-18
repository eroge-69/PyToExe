{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 from datetime import timedelta\
import csv\
import io\
import re\
\
def format_timecode(tc_str):\
    tc_str = tc_str.strip().replace("\'92", "'").replace("\'94", '"').replace(".", ":")\
    if "'" in tc_str and '"' in tc_str:  # es. 12\'9233\'94\
        try:\
            minutes = int(tc_str.split("'")[0])\
            seconds = int(tc_str.split("'")[1].replace('"', ''))\
            return f"00:\{minutes:02\}:\{seconds:02\}:00"\
        except Exception:\
            return "00:00:00:00"\
    parts = tc_str.split(":")\
    try:\
        if len(parts) == 4:\
            return ":".join(f"\{int(p):02\}" for p in parts)\
        if len(parts) == 3:\
            return f"00:\{int(parts[0]):02\}:\{int(parts[1]):02\}:\{int(parts[2]):02\}"\
        if len(parts) == 2:\
            return f"00:\{int(parts[0]):02\}:\{int(parts[1]):02\}:00"\
    except Exception:\
        return "00:00:00:00"\
    return "00:00:00:00"\
\
def generate_marker_list(text, default_track="V1", default_color="Cyan"):\
    name_match = re.match(r"\\[(.*?)\\]", text.strip())\
    marker_name = name_match.group(1) if name_match else "NOTE"\
    text = re.sub(r"^\\[.*?\\]", "", text).strip()\
\
    output = io.StringIO()\
    writer = csv.writer(output)\
    writer.writerow(["Marker Name", "Timecode", "Track", "Color", "Comment"])\
\
    current_time = timedelta(seconds=0)\
    assigned_timecodes = set()\
\
    text = text.replace("/", "\\n")\
    lines = [line.strip() for line in text.split("\\n") if line.strip()]\
\
    for line in lines:\
        match = re.match(r"^(\\d\{1,2\}[\'92'\\.:]\\d\{2\}(?:[\'94\\"\\.:]?\\d\{0,2\})?)", line)\
        if match:\
            tc_raw = match.group(1)\
            comment = line[len(tc_raw):].strip()\
            tc_formatted = format_timecode(tc_raw)\
            if tc_formatted in assigned_timecodes:\
                h, m, s, f = map(int, tc_formatted.split(":"))\
                tc_td = timedelta(hours=h, minutes=m, seconds=s) + timedelta(seconds=1)\
                tc_formatted = f"\{tc_td.seconds//3600:02\}:\{(tc_td.seconds//60)%60:02\}:\{tc_td.seconds%60:02\}:00"\
            assigned_timecodes.add(tc_formatted)\
            writer.writerow([marker_name, tc_formatted, default_track, default_color, comment])\
        else:\
            while True:\
                tc_formatted = f"\{current_time.seconds//3600:02\}:\{(current_time.seconds//60)%60:02\}:\{current_time.seconds%60:02\}:00"\
                if tc_formatted not in assigned_timecodes:\
                    break\
                current_time += timedelta(seconds=5)\
            assigned_timecodes.add(tc_formatted)\
            writer.writerow([marker_name, tc_formatted, default_track, default_color, f" SENZA TC \{line\}"])\
            current_time += timedelta(seconds=5)\
\
    return output.getvalue()}