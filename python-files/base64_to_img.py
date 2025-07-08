import os
import json
import glob
import argparse
import base64
from io import BytesIO
from PIL import Image

def get_all_files(path):
    files = glob.glob(f"{path}/**/*.json", recursive=True)
    return files

def arg_parse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default="./detection_labelme")
    return parser.parse_args()

if __name__ == "__main__":
    args = arg_parse()
    input_path = args.input
    #  give me explain: input_path is the path to the folder containing the json files, input method: python base64_to_img.py --input ./detection_labelme
    files = get_all_files(input_path)
    print("Count: ", len(files))
    
    for idx, file in enumerate(files):
        if idx % 1000 == 0:
            print(f"{idx} processed.")
        file_name = file.split('\\')[-1]
        img_path = file.replace('.json', '.jpg')
        if os.path.exists(img_path) or os.path.exists(file.replace('.json', '.png')):
            continue
        
        seg_json = json.load(open(file))
        img = Image.open(BytesIO(base64.b64decode(seg_json['imageData'])))
        # Convert image to RGB mode if it's not already
        if img.mode != 'RGB':
            img = img.convert('RGB')
        img.save(img_path, 'JPEG')
        
    print("Completed!")