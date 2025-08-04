import os

def update_11th_line_in_files(folder, script_filename):
    for filename in os.listdir(folder):
        if filename == script_filename:
            continue  # Skip modifying itself
        filepath = os.path.join(folder, filename)
        if os.path.isfile(filepath):
            with open(filepath, 'r') as f:
                lines = f.readlines()
            # Ensure there are at least 11 lines
            while len(lines) < 11:
                lines.append('\n')
            lines[10] = f"WAFER {filename}\n"
            with open(filepath, 'w') as f:
                f.writelines(lines)

if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    script_filename = os.path.basename(__file__)
    update_11th_line_in_files(folder, script_filename)