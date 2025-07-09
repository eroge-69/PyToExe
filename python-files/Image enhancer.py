import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import json
import os

# Clase para la IA de edición de imágenes
class ImageEnhancer:
    def __init__(self):
        self.image = None
        self.reference_image = None
        self.background_image = None
        self.preferences = {
            "brightness_factor": 1.0,
            "contrast_factor": 1.2,
            "color_match_strength": 0.8,
            "sky_color": [135, 206, 235],  # Azul claro por defecto (RGB)
            "blur_intensity": 15,  # Intensidad de desenfoque
        }
        self.load_preferences()

    def load_image(self, file_path):
        self.image = cv2.imread(file_path)
        if self.image is None:
            raise ValueError("No se pudo cargar la imagen")
        return self.image

    def load_reference_image(self, file_path):
        self.reference_image = cv2.imread(file_path)
        if self.reference_image is None:
            raise ValueError("No se pudo cargar la imagen de referencia")
        return self.reference_image

    def load_background_image(self, file_path):
        self.background_image = cv2.imread(file_path)
        if self.background_image is None:
            raise ValueError("No se pudo cargar la imagen de fondo")
        return self.background_image

    def enhance_image(self):
        if self.image is None:
            return None
        img = self.image.astype(np.float32)
        if self.reference_image is not None:
            img = self.match_color_histogram(img)
        else:
            img = img * self.preferences["contrast_factor"] + self.preferences["brightness_factor"] * 50
            img = np.clip(img, 0, 255).astype(np.uint8)
        return img

    def match_color_histogram(self, img):
        img_lab = cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_BGR2LAB)
        ref_lab = cv2.cvtColor(self.reference_image, cv2.COLOR_BGR2LAB)
        img_l, img_a, img_b = cv2.split(img_lab)
        ref_l, ref_a, ref_b = cv2.split(ref_lab)
        img_l = self.match_histogram(img_l, ref_l)
        img_a = self.match_histogram(img_a, ref_a)
        img_b = self.match_histogram(img_b, ref_b)
        img_matched = cv2.merge([img_l, img_a, img_b])
        img_matched = cv2.cvtColor(img_matched, cv2.COLOR_LAB2BGR)
        img = (1 - self.preferences["color_match_strength"]) * img + self.preferences["color_match_strength"] * img_matched
        return np.clip(img, 0, 255).astype(np.uint8)

    def match_histogram(self, src, ref):
        src_hist, bins = np.histogram(src.flatten(), 256, [0, 256])
        ref_hist, bins = np.histogram(ref.flatten(), 256, [0, 256])
        src_cdf = src_hist.cumsum()
        src_cdf = src_cdf / src_cdf[-1]
        ref_cdf = ref_hist.cumsum()
        ref_cdf = ref_cdf / ref_cdf[-1]
        mapping = np.zeros(256, dtype=np.uint8)
        for i in range(256):
            j = 0
            while j < 255 and ref_cdf[j] < src_cdf[i]:
                j += 1
            mapping[i] = j
        return cv2.LUT(src, mapping)

    def change_background(self):
        if self.image is None:
            return None
        # Segmentar el sujeto (simple segmentación basada en umbral)
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
        mask_inv = cv2.bitwise_not(mask)

        # Redimensionar fondo si es necesario
        background = self.background_image if self.background_image is not None else np.zeros_like(self.image)
        if background.shape != self.image.shape:
            background = cv2.resize(background, (self.image.shape[1], self.image.shape[0]))

        # Combinar sujeto con nuevo fondo
        fg = cv2.bitwise_and(self.image, self.image, mask=mask_inv)
        bg = cv2.bitwise_and(background, background, mask=mask)
        result = cv2.add(fg, bg)
        return result

    def edit_sky(self):
        if self.image is None:
            return None
        # Detectar cielo (simple segmentación por color azul)
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        lower_sky = np.array([90, 30, 30])
        upper_sky = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_sky, upper_sky)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)

        # Ajustar color, brillo y contraste del cielo
        img = self.image.astype(np.float32)
        sky_area = cv2.bitwise_and(img, img, mask=mask)
        sky_area = sky_area * self.preferences["contrast_factor"] + self.preferences["brightness_factor"] * 50
        sky_area = np.clip(sky_area, 0, 255)
        for c in range(3):
            sky_area[:, :, c] = sky_area[:, :, c] * (self.preferences["sky_color"][c] / 255)
        img = cv2.bitwise_and(img, img, mask=cv2.bitwise_not(mask)) + cv2.bitwise_and(sky_area, sky_area, mask=mask)
        return img.astype(np.uint8)

    def replace_sky(self, sky_type="cloudy"):
        if self.image is None:
            return None
        # Detectar cielo
        hsv = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
        lower_sky = np.array([90, 30, 30])
        upper_sky = np.array([130, 255, 255])
        mask = cv2.inRange(hsv, lower_sky, upper_sky)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)

        # Crear cielo nuevo
        sky = np.zeros_like(self.image)
        if sky_type == "cloudy":
            sky[:] = [200, 200, 200]  # Gris para nubes
        elif sky_type == "clear":
            sky[:] = [135, 206, 235]  # Azul claro
        elif sky_type == "stormy":
            sky[:] = [50, 50, 50]  # Gris oscuro tormentoso

        # Combinar
        fg = cv2.bitwise_and(self.image, self.image, mask=cv2.bitwise_not(mask))
        bg = cv2.bitwise_and(sky, sky, mask=mask)
        return cv2.add(fg, bg)

    def blur_background(self):
        if self.image is None:
            return None
        # Segmentar sujeto
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        mask = cv2.dilate(mask, np.ones((5, 5), np.uint8), iterations=2)
        mask_inv = cv2.bitwise_not(mask)

        # Desenfocar fondo
        blurred = cv2.GaussianBlur(self.image, (self.preferences["blur_intensity"], self.preferences["blur_intensity"]), 0)
        fg = cv2.bitwise_and(self.image, self.image, mask=mask_inv)
        bg = cv2.bitwise_and(blurred, blurred, mask=mask)
        return cv2.add(fg, bg)

    def remove_object(self, x, y, radius=20):
        if self.image is None:
            return None
        # Crear máscara circular para el objeto
        mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
        cv2.circle(mask, (x, y), radius, 255, -1)
        # Rellenar usando inpainting
        result = cv2.inpaint(self.image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)
        return result

    def save_image(self, output_path, img):
        cv2.imwrite(output_path, img)

    def update_preferences(self, feedback, operation):
        if feedback == "good":
            if operation in ["enhance", "edit_sky"]:
                self.preferences["brightness_factor"] *= 1.05
                self.preferences["contrast_factor"] *= 1.05
            if operation == "enhance":
                self.preferences["color_match_strength"] = min(1.0, self.preferences["color_match_strength"] * 1.1)
            if operation == "blur_background":
                self.preferences["blur_intensity"] = min(31, self.preferences["blur_intensity"] + 2)
        else:
            if operation in ["enhance", "edit_sky"]:
                self.preferences["brightness_factor"] = max(0.8, self.preferences["brightness_factor"] * np.random.uniform(0.9, 1.1))
                self.preferences["contrast_factor"] = max(0.8, self.preferences["contrast_factor"] * np.random.uniform(0.9, 1.1))
            if operation == "enhance":
                self.preferences["color_match_strength"] = max(0.5, self.preferences["color_match_strength"] * np.random.uniform(0.9, 1.1))
            if operation == "blur_background":
                self.preferences["blur_intensity"] = max(5, self.preferences["blur_intensity"] - 2)
        self.save_preferences()

    def save_preferences(self):
        with open("preferences.json", "w") as f:
            json.dump(self.preferences, f)

    def load_preferences(self):
        try:
            with open("preferences.json", "r") as f:
                self.preferences = json.load(f)
        except FileNotFoundError:
            pass

# Interfaz gráfica
class ImageEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Imágenes Avanzado")
        self.enhancer = ImageEnhancer()
        self.operation = None
        self.mouse_x, self.mouse_y = 0, 0

        # Botones
        tk.Button(root, text="Cargar Imagen Objetivo", command=self.load_image).pack()
        tk.Button(root, text="Cargar Imagen de Referencia", command=self.load_reference_image).pack()
        tk.Button(root, text="Cargar Imagen de Fondo", command=self.load_background_image).pack()
        tk.Button(root, text="Mejorar Imagen (Colores)", command=self.enhance_image).pack()
        tk.Button(root, text="Cambiar Fondo", command=self.change_background).pack()
        tk.Button(root, text="Editar Cielo", command=self.edit_sky).pack()
        tk.Button(root, text="Cielo Nuboso", command=lambda: self.replace_sky("cloudy")).pack()
        tk.Button(root, text="Cielo Despejado", command=lambda: self.replace_sky("clear")).pack()
        tk.Button(root, text="Cielo Tormentoso", command=lambda: self.replace_sky("stormy")).pack()
        tk.Button(root, text="Desenfocar Fondo", command=self.blur_background).pack()
        tk.Button(root, text="Quitar Objeto (Clic en Imagen)", command=self.start_remove_object).pack()
        tk.Button(root, text="Me gusta", command=lambda: self.feedback("good")).pack()
        tk.Button(root, text="No me gusta", command=lambda: self.feedback("bad")).pack()
        tk.Button(root, text="Guardar Imagen", command=self.save_image).pack()

        # Área para mensajes
        self.label = tk.Label(root, text="Carga una imagen para empezar")
        self.label.pack()

        self.image = None
        self.enhanced_image = None
        self.operation = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.image = self.enhancer.load_image(file_path)
            self.label.config(text="Imagen objetivo cargada.")
            cv2.imshow("Imagen Actual", self.image)
            cv2.waitKey(1)

    def load_reference_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.enhancer.load_reference_image(file_path)
            self.label.config(text="Imagen de referencia cargada.")

    def load_background_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.jpeg")])
        if file_path:
            self.enhancer.load_background_image(file_path)
            self.label.config(text="Imagen de fondo cargada.")

    def enhance_image(self):
        if self.image is not None:
            self.enhanced_image = self.enhancer.enhance_image()
            self.operation = "enhance"
            self.label.config(text="Imagen mejorada. ¿Te gusta?")
            cv2.imshow("Imagen Mejorada", self.enhanced_image)
            cv2.waitKey(1)
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen objetivo.")

    def change_background(self):
        if26if self.image is not None:
            self.enhanced_image = self.enhancer.change_background()
            self.operation = "change_background"
            self.label.config(text="Fondo cambiado. ¿Te gusta?")
            cv2.imshow("Imagen Mejorada", self.enhanced_image)
            cv2.waitKey(1)
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen objetivo.")

    def edit_sky(self):
        if self.image is not None:
            self.enhanced_image = self.enhancer.edit_sky()
            self.operation = "edit_sky"
            self.label.config(text="Cielo editado. ¿Te gusta?")
            cv2.imshow("Imagen Mejorada", self.enhanced_image)
            cv2.waitKey(1)
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen objetivo.")

    def replace_sky(self, sky_type):
        if self.image is not None:
            self.enhanced_image = self.enhancer.replace_sky(sky_type)
            self.operation = f"replace_sky_{sky_type}"
            self.label.config(text=f"Cielo {sky_type} aplicado. ¿Te gusta?")
            cv2.imshow("Imagen Mejorada", self.enhanced_image)
            cv2.waitKey(1)
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen objetivo.")

    def blur_background(self):
        if self.image is not None:
            self.enhanced_image = self.enhancer.blur_background()
            self.operation = "blur_background"
            self.label.config(text="Fondo desenfocado. ¿Te gusta?")
            cv2.imshow("Imagen Mejorada", self.enhanced_image)
            cv2.waitKey(1)
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen objetivo.")

    def start_remove_object(self):
        if self.image is not None:
            self.label.config(text="Haz clic en el objeto a quitar en la ventana de la imagen")
            cv2.setMouseCallback("Imagen Actual", self.mouse_click)
        else:
            messagebox.showwarning("Advertencia", "Primero carga una imagen objetivo.")

    def mouse_click(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.mouse_x, self.mouse_y = x, y
            self.enhanced_image = self.enhancer.remove_object(self.mouse_x, self.mouse_y)
            self.operation = "remove_object"
            self.label.config(text="Objeto eliminado. ¿Te gusta?")
            cv2.imshow("Imagen Mejorada", self.enhanced_image)
            cv2.waitKey(1)

    def save_image(self):
        if self.enhanced_image is not None:
            output_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG", "*.jpg")])
            if output_path:
                self.enhancer.save_image(output_path, self.enhanced_image)
                self.label.config(text="Imagen guardada.")
        else:
            messagebox.showwarning("Advertencia", "Primero realiza una edición.")

    def feedback(self, rating):
        if self.enhanced_image is not None:
            self.enhancer.update_preferences(rating, self.operation)
            self.label.config(text=f"Feedback recibido: {rating}. Prueba otra edición.")
        else:
            messagebox.showwarning("Advertencia", "Primero realiza una edición.")

# Ejecutar la aplicación
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageEditorApp(root)
    root.mainloop()