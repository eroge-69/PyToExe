import re
import random
import string

def load_vbs_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def junk_string(length=20):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:',.<>/?`~"
    return ''.join(random.choices(chars, k=length))

def randomize_variables(vbs_code):
    vars_found = list(set(re.findall(r'\b(?:Dim|Set)\s+(\w+)', vbs_code)))
    var_map = {var: junk_string(random.randint(16, 24)) for var in vars_found}
    for old, new in var_map.items():
        vbs_code = re.sub(rf'\b{old}\b', new, vbs_code)
    return vbs_code

def split_string_to_chars(s):
    return '" & "'.join(list(s))

def obfuscate_strings(vbs_code):
    return re.sub(r'"([^"]{1,40})"', lambda m: '"' + split_string_to_chars(m.group(1)) + '"', vbs_code)

def insert_massive_junk(vbs_code, min_lines=30):
    lines = vbs_code.splitlines()
    new_lines = []
    while len(new_lines) < min_lines:
        new_lines.append(f"' {junk_string(30)}")
        new_lines.append(f"If False Then {junk_string(10)} = \"{junk_string(10)}\"")
        if lines:
            new_lines.append(lines.pop(0))
    new_lines.extend(lines)
    return "\n".join(new_lines)

def brutalize_vbs(vbs_code):
    vbs_code = randomize_variables(vbs_code)
    vbs_code = obfuscate_strings(vbs_code)
    vbs_code = insert_massive_junk(vbs_code, min_lines=30)
    return vbs_code

def save_output(content, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

input_vbs = "output_obfuscated.vbs"
output_vbs = "output_vbs_ultrabrutal.vbs"

original_vbs = load_vbs_file(input_vbs)
ultrabrutal_vbs = brutalize_vbs(original_vbs)
save_output(ultrabrutal_vbs, output_vbs)

output_vbs