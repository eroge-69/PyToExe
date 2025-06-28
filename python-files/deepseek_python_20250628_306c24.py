# sparks_analyzer.py
import cv2
import numpy as np
import os
import json
from datetime import datetime

# Конфигурация
THRESHOLD = 30       # Порог обнаружения искр
MIN_AREA = 3         # Минимальный размер искры
MAX_AREA = 50        # Максимальный размер
LIFE_FRAMES = 5      # Длительность жизни искры (кадров)

def analyze_frames(input_folder):
    frames = sorted([f for f in os.listdir(input_folder) if f.startswith("frame_")])
    sparks = []
    
    for i, frame_file in enumerate(frames):
        frame_path = os.path.join(input_folder, frame_file)
        img = cv2.imread(frame_path, cv2.IMREAD_GRAYSCALE)
        _, binary = cv2.threshold(img, THRESHOLD, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if MIN_AREA <= area <= MAX_AREA:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    x = int(M["m10"] / M["m00"])
                    y = int(M["m01"] / M["m00"])
                    sparks.append({
                        "frame": i * 3 + 1,  # Учитываем шаг кадров
                        "x": x,
                        "y": y,
                        "life": LIFE_FRAMES
                    })
    
    return sparks

if __name__ == "__main__":
    input_folder = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(input_folder, "analysis_result.json")
    
    sparks_data = analyze_frames(input_folder)
    
    with open(output_file, "w") as f:
        json.dump(sparks_data, f, indent=2)
    
    print(f"Analysis complete! Found {len(sparks_data)} sparks.")