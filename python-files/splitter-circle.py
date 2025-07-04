import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
from PIL import Image
from scipy.ndimage import label, binary_closing, binary_opening, generate_binary_structure

# === Wczytaj obraz ===
img_color = Image.open("splitter-OCR-empty.png").convert("RGB")
img_np = np.array(img_color)
img_gray = np.array(img_color.convert("L"))

# === Binaryzacja i czyszczenie ===
binary = img_gray < 200
structure = generate_binary_structure(2, 2)
binary_cleaned = binary_closing(binary, structure=structure, iterations=2)
binary_cleaned = binary_opening(binary_cleaned, structure=structure, iterations=1)

# === Detekcja regionów ===
regions, num_features = label(~binary_cleaned)

# === Wczytaj wartości z pliku .txt ===
values = {}
with open("dane-spliter.txt") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            idx, val = line.split()
            values[int(idx)] = float(val)
        except ValueError:
            print(f"Pominięto linię: {line}")

# === Współrzędne numerów logicznych (cx, cy) z obrazka ===
manual_mapping = [
    (24,230.9,811.5,103476,24),(19,254.2,1115.4,87248,19),(29,412.7,418.1,103233,29),
    (14,340.8,1342.4,69257,14),(9,456.2,1514,52471,9),(25,571.4,623.5,105770,25),
    (20,574.7,899.6,88392,20),(15,613.5,1125,69704,15),(5,609.5,1614.8,50769,5),
    (10,670.9,1316.8,52850,10),(30,784,266.3,111323,30),(2,752.7,1707.4,37972,2),
    (6,828.3,1447.9,43067,6),(26,955.7,565.1,105776,26),(21,956.1,826.4,88060,21),
    (16,955.7,1048.6,69746,16),(11,955.7,1245.9,52811,11),(1,955.7,1780.4,38844,1),
    (3,955.7,1602,38201,3),(31,1127.7,266.4,111109,31),(7,1083.4,1447.9,42974,7),
    (12,1240.5,1316.8,52834,12),(17,1298,1125,69716,17),(27,1337.4,900,88363,27),
    (22,1340,623.5,105770,22),(8,1301.9,1614.7,50779,8),(32,1498.7,418.1,103248,32),
    (13,1455.1,1514,52470,13),(18,1570.6,1342.4,69251,18),(23,1657.4,1115.7,87078,23),
    (28,1680.5,811.4,103439,28),(4,1155.5,1707.4,37686,4)
]

# === Automatyczne przypisanie numeru logicznego do region_id ===
logic_to_region_id = {}
region_positions = {}

for logic_num, cy, cx, _, _ in manual_mapping:
    region_id = regions[int(round(cy)), int(round(cx))]
    logic_to_region_id[logic_num] = region_id
    region_positions[region_id] = (cy, cx)

# === Przypisz wartości do regionów
valid_region_values = {}
for logic_num, region_id in logic_to_region_id.items():
    if logic_num in values:
        valid_region_values[region_id] = values[logic_num]
    else:
        print(f"Brak wartości dla numeru {logic_num} (region_id={region_id})")

# === Kolorowanie
norm = Normalize(vmin=min(valid_region_values.values()), vmax=max(valid_region_values.values()))
cmap = cm.get_cmap("coolwarm")

overlay = np.zeros_like(img_np, dtype=np.uint8)
for region_id, value in valid_region_values.items():
    mask = regions == region_id
    color_rgb = (np.array(cmap(norm(value))[:3]) * 255).astype(np.uint8)
    for c in range(3):
        overlay[..., c][mask] = color_rgb[c]

# === Połączenie z oryginałem
alpha = 0.6
blended = (alpha * overlay + (1 - alpha) * img_np).astype(np.uint8)
blended[img_gray < 60] = img_np[img_gray < 60]

# === Stwórz maskę koła (obszar wewnętrzny) ===
# Znajdź wszystkie piksele należące do regionów (koło)
circle_mask = regions > 0

# === Ustaw białe tło poza kołem ===
# Zacznij od oryginalnego obrazu (który ma białe tło i czarne kontury)
final_image = img_np.copy()

# Zastosuj kolorowanie tylko w regionach (segmentach), ale zachowaj czarne kontury
for region_id, value in valid_region_values.items():
    mask = regions == region_id
    color_rgb = (np.array(cmap(norm(value))[:3]) * 255).astype(np.uint8)
    
    # Zastosuj kolor tylko tam gdzie nie ma ciemnych linii (kontury)
    region_mask = mask & (img_gray > 60)  # Nie koloruj ciemnych pikseli (kontury)
    
    for c in range(3):
        final_image[..., c][region_mask] = (alpha * color_rgb[c] + (1 - alpha) * img_np[..., c][region_mask]).astype(np.uint8)

# === Rysowanie wyniku
fig, ax = plt.subplots(figsize=(8, 8))
ax.imshow(final_image)
#ax.set_title("Pokolorowane regiony zgodnie z numeracją z pliku")
ax.axis("off")

# === Zamiana wyświetlanych numerków ===
display_labels = {
    19: 1,
    13: 2,
    20: 3,
    23: 4,    
    10: 5,  
    14: 6,  
    22: 7,  
    28: 8,  
    6: 9,  
    11: 10,  
    18: 11,  
    24: 12,  
    30: 13,  
    5: 14,  
    9: 15,  
    17: 16,  
    25: 17,  
    31: 18,  
    3: 19,  
    8: 20,  
    16: 21,
    26: 22,
    32: 23,
    2: 24,
    7: 25,
    15: 26,
    27: 27,
    33: 28,
    4: 29,
    12: 30,
    21: 31,
    29: 32,
}

# Numery logiczne (1–32) na pokolorowanym obrazie
for region_id, (cy, cx) in region_positions.items():
    label_text = display_labels.get(region_id, region_id)
    ax.text(cx, cy, str(label_text), ha='center', va='center', color='black', fontsize=16)

# Colorbar
sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
plt.colorbar(sm, ax=ax, fraction=0.046, pad=0.04)

plt.tight_layout()
plt.show()

# Zapisz wynik - cały wykres z numerami i colorbar
fig.savefig("splitter-colored-complete.png", dpi=300, bbox_inches='tight', 
            facecolor='white', edgecolor='none')

# Opcjonalnie zapisz też sam obraz bez numerów i colorbar
Image.fromarray(final_image).save("splitter-colored-image-only.png")