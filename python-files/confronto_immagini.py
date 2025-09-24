import cv2
import numpy as np

# Carica le due immagini
img1 = cv2.imread("immagine1.jpg")
img2 = cv2.imread("immagine2.jpg")

if img1 is None or img2 is None:
    raise FileNotFoundError("Assicurati che immagine1.jpg e immagine2.jpg siano nella stessa cartella di questo script.")

# Ridimensiona se necessario (solo se non hanno le stesse dimensioni)
if img1.shape != img2.shape:
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

# Converte in scala di grigi
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

# Differenza assoluta
diff = cv2.absdiff(gray1, gray2)

# Applica una soglia per evidenziare le differenze
_, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

# Opzionale: dilatazione per rendere più visibili le aree
kernel = np.ones((5, 5), np.uint8)
mask = cv2.dilate(thresh, kernel, iterations=2)

# Trova i contorni delle aree diverse
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
output = img1.copy()
cv2.drawContours(output, contours, -1, (0, 0, 255), 2)  # rosso

# Mostra i risultati
cv2.imshow("Differenza (grayscale)", diff)
cv2.imshow("Differenze evidenziate", output)
cv2.waitKey(0)
cv2.destroyAllWindows()
