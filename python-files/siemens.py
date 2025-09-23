import cv2
import numpy as np
import matplotlib.pyplot as plt

def load_image(image_path):
    """
    Lädt das Bild des Siemens-Sterns.
    """
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise FileNotFoundError(f"Bild konnte nicht geladen werden: {image_path}")
    return image

def preprocess_image(image):
    """
    Wendet eine Glättung und Normalisierung auf das Bild an.
    """
    # Gaussian Blur zur Rauschunterdrückung
    blurred = cv2.GaussianBlur(image, (5, 5), 0)
    # Normalisierung
    normalized = cv2.normalize(blurred, None, 0, 255, cv2.NORM_MINMAX)
    return normalized

def find_center(image):
    """
    Automatische Erkennung des Zentrums des Siemens-Sterns.
    """
    # Berechnung des Schwerpunkts basierend auf der Bildintensität
    moments = cv2.moments(image)
    if moments["m00"] != 0:
        center_x = int(moments["m10"] / moments["m00"])
        center_y = int(moments["m01"] / moments["m00"])
    else:
        center_x, center_y = image.shape[1] // 2, image.shape[0] // 2  # Fallback
    return (center_x, center_y)

def calculate_mtf(image, center, pixel_size_mm):
    """
    Berechnet die Modulationsübertragungsfunktion (MTF) in Linienpaaren pro Millimeter (lp/mm).
    """
    # Bildgröße
    height, width = image.shape
    
    # Erstelle eine Liste für die MTF-Werte
    mtf_values = []
    radii = np.linspace(1, min(center), 100)  # Radien von 1 bis zum Bildrand
    
    for radius in radii:
        # Erstelle eine Maske für den aktuellen Radius
        mask = np.zeros_like(image, dtype=np.uint8)
        cv2.circle(mask, center, int(radius), 255, -1)
        
        # Berechne den mittleren Intensitätswert innerhalb des Kreises
        mean_intensity = cv2.mean(image, mask=mask)[0]
        mtf_values.append(mean_intensity)
    
    # Normiere die MTF-Werte (maximaler Wert = 1)
    mtf_values = np.array(mtf_values)
    mtf_values /= mtf_values.max()
    
    # Berechne die räumlichen Frequenzen in Linienpaaren pro Millimeter
    spatial_frequencies = 1 / (2 * np.pi * radii * pixel_size_mm)
    
    return spatial_frequencies, mtf_values

def compare_mtf(spatial_frequencies, mtf_values, reference_frequencies, reference_mtf):
    """
    Vergleicht die berechnete MTF-Kurve mit einer Referenzkurve.
    """
    plt.figure(figsize=(8, 6))
    plt.plot(spatial_frequencies, mtf_values, label="Berechnete MTF", color="blue")
    plt.plot(reference_frequencies, reference_mtf, label="Referenz-MTF", color="red", linestyle="--")
    plt.xlabel("Räumliche Frequenz (lp/mm)")
    plt.ylabel("Normierte Intensität")
    plt.title("MTF-Vergleich")
    plt.grid()
    plt.legend()
    plt.show()

def display_results(image, edges, center, spatial_frequencies, mtf_values):
    """
    Zeigt die Ergebnisse der Analyse an.
    """
    print(f"Zentrum des Siemens-Sterns: {center}")
    
    # Anzeigen des Originalbilds und der Kanten
    plt.figure(figsize=(15, 5))
    
    plt.subplot(1, 3, 1)
    plt.title("Originalbild")
    plt.imshow(image, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 2)
    plt.title("Kanten (Canny)")
    plt.imshow(edges, cmap='gray')
    plt.axis('off')
    
    plt.subplot(1, 3, 3)
    plt.title("MTF-Kurve")
    plt.plot(spatial_frequencies, mtf_values, label="MTF")
    plt.xlabel("Räumliche Frequenz (lp/mm)")
    plt.ylabel("Normierte Intensität")
    plt.grid()
    plt.legend()
    
    plt.tight_layout()
    plt.show()

def main(image_path, pixel_size_mm, reference_frequencies=None, reference_mtf=None):
    """
    Hauptfunktion zur Auswertung des Siemens-Sterns.
    """
    # Bild laden
    image = load_image(image_path)
    
    # Bild vorverarbeiten
    processed_image = preprocess_image(image)
    
    # Automatische Zentrumserkennung
    center = find_center(processed_image)
    
    # Kanten finden
    edges = cv2.Canny(processed_image, 50, 150)
    
    # MTF berechnen
    spatial_frequencies, mtf_values = calculate_mtf(processed_image, center, pixel_size_mm)
    
    # Ergebnisse anzeigen
    display_results(image, edges, center, spatial_frequencies, mtf_values)
    
    # Vergleich mit Referenz-MTF (falls vorhanden)
    if reference_frequencies is not None and reference_mtf is not None:
        compare_mtf(spatial_frequencies, mtf_values, reference_frequencies, reference_mtf)


