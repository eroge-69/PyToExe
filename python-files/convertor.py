import re
import json
import os

def remove_non_ascii(input_file_path):
    try:
        with open(input_file_path, "r", encoding="utf-8") as input_file:
            content = input_file.read()

        cleaned_content = content.encode("ascii", errors="ignore").decode("ascii")

        with open(input_file_path, "w", encoding="utf-8") as output_file:
            output_file.write(cleaned_content)

        print(f"Non-ASCII characters removed")

    except Exception as e:
        print(f"Error: {e}")


def js_to_json(js_file_path, json_file_path):
    with open(js_file_path, "r") as js_file:
        js_content = js_file.read()

    pattern = r"(?:const|let|var)\s+\w+\s*=\s*(\[.*?\]);"
    match = re.search(pattern, js_content, re.DOTALL)

    if not match:
        raise ValueError("Could not find a valid JavaScript object")

    js_object_str = match.group(1)
    js_object_str = js_object_str.replace("'", '"')

    js_object_str = re.sub(r"\/\/.*|\/\*[\s\S]*?\*\/", "", js_object_str)
    js_object_str = re.sub(r",\s*([}\]])", r"\1", js_object_str)
    js_object_str = re.sub(
        r"([{,])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:",
        lambda m: f'{m.group(1)}"{m.group(2)}":',
        js_object_str,
    )

    try:
        python_object = json.loads(js_object_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JavaScript object: {e}")

    json_string = json.dumps(python_object, indent=2)

    with open(json_file_path, "w") as json_file:
        json_file.write(json_string)

    print(f"JavaScript object converted to JSON and saved to {json_file_path}")


# cwd bcs python was being fucky
current_directory = os.getcwd()
files_in_directory = os.listdir(current_directory)
js_files = [file for file in files_in_directory if file.endswith(".js")]

for js_file in js_files:
    input_js_file = os.path.join(current_directory, js_file)
    output_json_file = os.path.join(current_directory, js_file.replace(".js", ".json"))

    remove_non_ascii(input_js_file)
    js_to_json(input_js_file, output_json_file)