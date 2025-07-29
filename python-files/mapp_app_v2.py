# -*- coding: utf-8 -*-
"""
Created on Tue Jul 29 21:59:23 2025

@author: sbeka
"""

import webview
import csv
import os

class API:
    def __init__(self):
        self.points = []
        self.filename = "punkty.csv"
        self.load_from_csv()

    def save_point(self, lat, lng, note, param1, param2):
        print(f"Zapisano punkt: ({lat}, {lng}) - {note}, {param1}, {param2}")
        self.points.append({
            'lat': lat,
            'lng': lng,
            'note': note,
            'param1': param1,
            'param2': param2
        })
        return "OK"

    def save_to_csv(self):
        with open(self.filename, "w", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["lat", "lng", "note", "param1", "param2"])
            writer.writeheader()
            writer.writerows(self.points)
        print(f"Zapisano do pliku {self.filename}")
        return "OK"

    def load_from_csv(self):
        if os.path.exists(self.filename):
            
            with open(self.filename, "r", encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.points = []
                for row in reader:
                    try:
                        row['lat'] = float(row['lat'])
                        row['lng'] = float(row['lng'])
                        self.points.append(row)
                    except Exception as e:
                        print(f"Błąd konwersji wiersza {row}: {e}")
            
        else:
            print(f"Plik {self.filename} nie istnieje.")



    def get_saved_points(self):
        return self.points

if __name__ == '__main__':
    api = API()
    html_path = os.path.abspath("index.html")
    webview.create_window("Mapa z formularzem", html_path, js_api=api)
    webview.start()
    # webview.start(debug=True)
