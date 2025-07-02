import cv2
import numpy as np

# Görselin adını gir
gorsel_adi = "gorsel.jpg"

# Görseli oku
img = cv2.imread(gorsel_adi)
if img is None:
    print("Görsel bulunamadı. Lütfen betikle aynı klasörde 'gorsel.jpg' olduğundan emin olun.")
    exit()

# Gri tonlama ve bulanıklaştırma
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray, (5, 5), 0)

# Kenar tespiti
edges = cv2.Canny(blur, 50, 150)

# Hough Transform ile çizgi algılama
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                        minLineLength=100, maxLineGap=10)

# Yatay çizgileri filtrele
horizontal_lines = []
for line in lines:
    x1, y1, x2, y2 = line[0]
    if abs(y1 - y2) < 10:  # Yalnızca yatay çizgiler
        horizontal_lines.append((y1 + y2) // 2)

if len(horizontal_lines) < 2:
    print("Yeterli sayıda yatay çizgi bulunamadı.")
    exit()

# En üst ve en alt çizgileri bul
horizontal_lines = sorted(horizontal_lines)
top = horizontal_lines[0]
bottom = horizontal_lines[-1]

# Belirlenen alandan kırp
cropped = img[top:bottom, :]
cv2.imwrite("kirilmis_gorsel.jpg", cropped)

print(f"Kırpma tamamlandı! 'kirilmis_gorsel.jpg' olarak kaydedildi ({top}px - {bottom}px arası).")