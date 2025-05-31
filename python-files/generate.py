import re
import sys
import os
import webbrowser

def parse_dialogue(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    title = "untitled"
    dialogue = []

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Title detection (ignore case and spaces)
        if re.match(r'^\s*title\s*:', line, re.IGNORECASE):
            title = re.split(r':\s*', line, maxsplit=1)[1].strip()
            continue

        # Parse dialogue line: format 'speaker: text | key=value | key2=function'
        # Split into main part and optional parameters by '|'
        parts = [p.strip() for p in line.split('|')]
        main_part = parts[0]

        # Extract speaker and text from main_part, ignoring spaces around colon
        match = re.match(r'^([^:]+)\s*:\s*(.+)$', main_part)
        if not match:
            print(f"Warning: couldn't parse line: {line}")
            continue
        speaker = match.group(1).strip()
        text = match.group(2).strip()

        # Replace simple color markup [[color:red]]text[[/color]] with Lua ct.Color calls
        # Example: "Hello [[color:red]]world[[/color]]!" -> 'Hello '..ct.Color("world", colors.Red)..'!'
        def repl_color(m):
            color = m.group(1).strip().capitalize()
            inner_text = m.group(2)
            return f'"..ct.Color("{inner_text}", colors.{color}).."'

        text = re.sub(r'\[\[color:(\w+)\]\](.*?)\[\[/color\]\]', repl_color, text)

        entry = {
            'speaker': speaker.lower(),
            'text': f'"{text}"'
        }

        # Parse optional key=value or key=function in remaining parts
        for param in parts[1:]:
            if '=' not in param:
                continue
            key, val = [x.strip() for x in param.split('=', 1)]
            if key == 'endtime':
                try:
                    entry['endTime'] = float(val)
                except:
                    pass
            elif key == 'endfunction':
                # We'll output a stub function, user must edit it manually later
                entry['endFunction'] = val

        dialogue.append(entry)

    return title, dialogue

def lua_format(dialogue_list):
    # Format Lua table from the list
    lua_lines = []
    for entry in dialogue_list:
        lua_lines.append("\t{")
        lua_lines.append(f'\t\tspeaker = "{entry["speaker"]}",')
        lua_lines.append(f'\t\ttext = {entry["text"]},')
        if 'endTime' in entry:
            lua_lines.append(f'\t\tendTime = {entry["endTime"]},')
        if 'endFunction' in entry:
            lua_lines.append(f'\t\tendFunction = function() {entry["endFunction"]} end,')
        lua_lines.append("\t},")
    return lua_lines

def write_lua_file(title, dialogue_list, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("local ct = require(Tools.changeText)\n")
        f.write("local colors = require(Constants.colors)\n")
        f.write("local getRoleName = require(ServerScriptService.Player.RolesInfo).GetName\n\n")
        f.write(f"return {{ {title} = {{\n")
        for line in lua_format(dialogue_list):
            f.write(line + "\n")
        f.write("} } }\n")

def main():
    if len(sys.argv) < 2:
        print("Drag and drop a dialogue .txt file onto this script or run with filename as argument.")
        input("Press Enter to exit...")
        return

    input_path = sys.argv[1]
    if not os.path.isfile(input_path):
        print(f"File not found: {input_path}")
        input("Press Enter to exit...")
        return

    title, dialogue = parse_dialogue(input_path)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(os.path.dirname(input_path), base_name + "_output.lua")

    write_lua_file(title, dialogue, output_path)

    print(f"Output written to {output_path}")
    # Open the output file with the default text editor
    try:
        if sys.platform == "win32":
            os.startfile(output_path)
        elif sys.platform == "darwin":
            os.system(f"open {output_path}")
        else:
            os.system(f"xdg-open {output_path}")
    except:
        pass

if __name__ == "__main__":
    main()
