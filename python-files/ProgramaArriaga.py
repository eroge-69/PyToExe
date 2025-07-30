import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk
import math


def draw_rounded_rectangle(draw, box, radius, outline="black", width=1):
    x1, y1, x2, y2 = box
    radius = max(0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    draw.line([(x1 + radius, y1), (x2 - radius, y1)], fill=outline, width=width)
    draw.line([(x1 + radius, y2), (x2 - radius, y2)], fill=outline, width=width)
    draw.line([(x1, y1 + radius), (x1, y2 - radius)], fill=outline, width=width)
    draw.line([(x2, y1 + radius), (x2, y2 - radius)], fill=outline, width=width)
    draw.arc([x1, y1, x1 + 2 * radius, y1 + 2 * radius], 180, 270, fill=outline, width=width)
    draw.arc([x2 - 2 * radius, y1, x2, y1 + 2 * radius], 270, 360, fill=outline, width=width)
    draw.arc([x2 - 2 * radius, y2 - 2 * radius, x2, y2], 0, 90, fill=outline, width=width)
    draw.arc([x1, y2 - 2 * radius, x1 + 2 * radius, y2], 90, 180, fill=outline, width=width)


def generar_layout(draw_stem=False, show_B_label=True, draw_hole=False,
                   horizontal_mm=19.05, vertical_mm=90, diagonal_mm=5,
                   diagonal_switch_offset_mm=9.5):
    mm_to_px = 10
    pad_diameter_mm = 1.8
    pad_diameter = int(pad_diameter_mm * mm_to_px)
    pad_spacing = diagonal_mm * mm_to_px
    switch_spacing = horizontal_mm * mm_to_px
    row_spacing = vertical_mm * mm_to_px
    switch_box = int(14 * mm_to_px)
    hole_diameter_mm = 3
    hole_diameter = int(hole_diameter_mm * mm_to_px)

    rows = [11, 12, 11]
    margin = 60
    max_row = max(rows)

    max_diagonal_offset_px = diagonal_switch_offset_mm * mm_to_px
    image_width = int(margin * 2 + switch_spacing * max_row + max_diagonal_offset_px)
    image_height = int(margin * 2 + row_spacing * (len(rows) - 1) + 100)

    img = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except IOError:
        font = ImageFont.load_default()

    diagonal_offset = pad_spacing / math.sqrt(2)
    stem_size = int(5 * mm_to_px)

    pad_positions = []

    for row_index, switches_in_row in enumerate(rows):
        y_center = margin + row_index * row_spacing + 50
        row_width = switch_spacing * (switches_in_row - 1)
        diagonal_offset_px = int(diagonal_switch_offset_mm * mm_to_px)
        start_x = (image_width - row_width) // 2

        if row_index == 1:
            start_x += diagonal_offset_px

        for i in range(switches_in_row):
            x_center = start_x + i * switch_spacing

            pad1 = (x_center - diagonal_offset / 2, y_center - diagonal_offset / 2)
            pad2 = (x_center + diagonal_offset / 2, y_center + diagonal_offset / 2)

            pad_positions.append({'A': pad1, 'B': pad2})

            draw.ellipse([
                (pad1[0] - pad_diameter // 2, pad1[1] - pad_diameter // 2),
                (pad1[0] + pad_diameter // 2, pad1[1] + pad_diameter // 2)
            ], fill="black")
            draw.text((pad1[0] - 10, pad1[1] - 10), "A", fill="black", font=font)

            draw.ellipse([
                (pad2[0] - pad_diameter // 2, pad2[1] - pad_diameter // 2),
                (pad2[0] + pad_diameter // 2, pad2[1] + pad_diameter // 2)
            ], fill="black")

            if show_B_label:
                draw.text((pad2[0] + 5, pad2[1] + 5), "B", fill="black", font=font)

            top_left = (x_center - switch_box // 2, y_center - switch_box // 2)
            bottom_right = (x_center + switch_box // 2, y_center + switch_box // 2)
            draw.rectangle([top_left, bottom_right], outline="gray", width=1)

            if draw_stem:
                stem_half = stem_size // 2
                stem_thickness = int(stem_size * 0.3)

                draw.rectangle([
                    (x_center - stem_half, y_center - stem_thickness // 2),
                    (x_center + stem_half, y_center + stem_thickness // 2)
                ], fill="black")

                draw.rectangle([
                    (x_center - stem_thickness // 2, y_center - stem_half),
                    (x_center + stem_thickness // 2, y_center + stem_half)
                ], fill="black")

            if draw_hole:
                draw.ellipse([
                    (x_center - hole_diameter // 2, y_center - hole_diameter // 2),
                    (x_center + hole_diameter // 2, y_center + hole_diameter // 2)
                ], outline="black", width=2)

    return img, pad_positions


class CherryMxViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Visualizador Layout Cherry MX")
        self.geometry("1400x900")

        self.stem_var = tk.BooleanVar(value=False)
        self.b_label_var = tk.BooleanVar(value=True)
        self.hole_var = tk.BooleanVar(value=False)
        self.zoom_level = 1.0

        self.horizontal_mm = tk.DoubleVar(value=19.05)
        self.vertical_mm = tk.DoubleVar(value=90)
        self.diagonal_mm = tk.DoubleVar(value=5)
        self.diagonal_switch_offset_mm = tk.DoubleVar(value=9.5)

        self.draw_mode = False
        self.line_thickness = tk.IntVar(value=3)
        self.lines = []
        self.selected_pad = None

        self.draw_frame_var = tk.BooleanVar(value=False)
        self.rounded_corners_var = tk.BooleanVar(value=False)
        self.frame_radius_var = tk.IntVar(value=15)

        # Frame superior estilo barra de herramientas
        top_bar_frame = ttk.Frame(self)
        top_bar_frame.pack(side="top", fill="x")

        # Añadir controles al frame barra de herramientas
        ttk.Checkbutton(top_bar_frame, text="Mostrar soporte central (stem)", variable=self.stem_var,
                        command=self.actualizar_imagen).grid(row=0, column=0, padx=5)
        ttk.Checkbutton(top_bar_frame, text="Mostrar etiqueta B", variable=self.b_label_var,
                        command=self.actualizar_imagen).grid(row=0, column=1, padx=5)
        ttk.Checkbutton(top_bar_frame, text="Mostrar perforación central (círculo)", variable=self.hole_var,
                        command=self.actualizar_imagen).grid(row=0, column=2, padx=5)

        ttk.Button(top_bar_frame, text="Zoom +", command=self.zoom_in).grid(row=0, column=3, padx=5)
        ttk.Button(top_bar_frame, text="Zoom -", command=self.zoom_out).grid(row=0, column=4, padx=5)
        ttk.Button(top_bar_frame, text="Guardar Imagen", command=self.guardar_imagen).grid(row=0, column=5, padx=5)

        self.btn_draw_mode = ttk.Button(top_bar_frame, text="Modo Dibujo OFF", command=self.toggle_draw_mode)
        self.btn_draw_mode.grid(row=0, column=6, padx=5)

        ttk.Label(top_bar_frame, text="Grosor pista:").grid(row=0, column=7, sticky="e")
        self.scale_thickness = ttk.Scale(top_bar_frame, from_=1, to=10, orient="horizontal",
                                         variable=self.line_thickness, command=lambda e: self.mostrar_imagen())
        self.scale_thickness.grid(row=0, column=8, padx=5)

        # Controles de separación
        sep_frame = ttk.LabelFrame(self, text="Separaciones (mm)")
        sep_frame.pack(pady=10, padx=10, fill="x")

        ttk.Label(sep_frame, text="Horizontal (entre switches):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.spin_horizontal = ttk.Spinbox(sep_frame, from_=5, to=50, increment=0.1, textvariable=self.horizontal_mm, width=8,
                                           command=self.actualizar_imagen)
        self.spin_horizontal.grid(row=0, column=1, padx=5, pady=2)

        ttk.Label(sep_frame, text="Vertical (entre filas):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.spin_vertical = ttk.Spinbox(sep_frame, from_=10, to=150, increment=0.5, textvariable=self.vertical_mm, width=8,
                                         command=self.actualizar_imagen)
        self.spin_vertical.grid(row=1, column=1, padx=5, pady=2)

        ttk.Label(sep_frame, text="Diagonal (entre pads A y B):").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.spin_diagonal = ttk.Spinbox(sep_frame, from_=1, to=20, increment=0.1, textvariable=self.diagonal_mm, width=8,
                                         command=self.actualizar_imagen)
        self.spin_diagonal.grid(row=2, column=1, padx=5, pady=2)

        ttk.Label(sep_frame, text="Desplazamiento diagonal entre filas (mm):").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.spin_diagonal_offset = ttk.Spinbox(sep_frame, from_=0, to=30, increment=0.1, textvariable=self.diagonal_switch_offset_mm, width=8,
                                                command=self.actualizar_imagen)
        self.spin_diagonal_offset.grid(row=3, column=1, padx=5, pady=2)

        self.spin_horizontal.bind("<Return>", lambda e: self.actualizar_imagen())
        self.spin_vertical.bind("<Return>", lambda e: self.actualizar_imagen())
        self.spin_diagonal.bind("<Return>", lambda e: self.actualizar_imagen())
        self.spin_diagonal_offset.bind("<Return>", lambda e: self.actualizar_imagen())

        # Mover controles Mostrar PCB y Esquinas redondeadas al frame de separaciones
        ttk.Checkbutton(sep_frame, text="Mostrar contorno PCB", variable=self.draw_frame_var,
                        command=self.actualizar_imagen).grid(row=4, column=0, padx=5, pady=5, sticky="w")
        ttk.Checkbutton(sep_frame, text="Esquinas redondeadas", variable=self.rounded_corners_var,
                        command=self.actualizar_imagen).grid(row=4, column=1, padx=5, pady=5, sticky="w")
        ttk.Label(sep_frame, text="Radio esquinas (px):").grid(row=4, column=2, padx=2, pady=5, sticky="w")
        self.spin_frame_radius = ttk.Spinbox(sep_frame, from_=0, to=100, increment=1,
                                             textvariable=self.frame_radius_var, width=5,
                                             command=self.actualizar_imagen)
        self.spin_frame_radius.grid(row=4, column=3, padx=5, pady=5, sticky="w")

        # Canvas para dibujo
        self.canvas = tk.Canvas(self, width=1200, height=600, bg="white")
        self.canvas.pack(expand=True, fill="both")

        self.img_original = None
        self.img_tk = None
        self.pad_positions = []

        self.canvas.bind("<Button-1>", self.click_canvas)

        self.actualizar_imagen()

    def generar_imagen_y_pads(self):
        img, pad_positions = generar_layout(draw_stem=self.stem_var.get(),
                                           show_B_label=self.b_label_var.get(),
                                           draw_hole=self.hole_var.get(),
                                           horizontal_mm=self.horizontal_mm.get(),
                                           vertical_mm=self.vertical_mm.get(),
                                           diagonal_mm=self.diagonal_mm.get(),
                                           diagonal_switch_offset_mm=self.diagonal_switch_offset_mm.get())
        return img, pad_positions

    def actualizar_imagen(self):
        self.img_original, self.pad_positions = self.generar_imagen_y_pads()
        self.mostrar_imagen()

    def mostrar_imagen(self):
        # Eliminar contenido previo
        self.canvas.delete("all")

        # Preparar la imagen con zoom
        if self.zoom_level != 1.0:
            new_size = (int(self.img_original.width * self.zoom_level), int(self.img_original.height * self.zoom_level))
            img_display = self.img_original.resize(new_size, Image.LANCZOS)
        else:
            img_display = self.img_original

        self.img_tk = ImageTk.PhotoImage(img_display)
        self.canvas.config(width=img_display.width, height=img_display.height)
        self.canvas.create_image(0, 0, anchor="nw", image=self.img_tk)

        # Dibujar contorno PCB si está activado
        if self.draw_frame_var.get():
            centers_x = []
            centers_y = []
            for pad_dict in self.pad_positions:
                pads = list(pad_dict.values())
                cx = sum(p[0] for p in pads) / len(pads)
                cy = sum(p[1] for p in pads) / len(pads)
                centers_x.append(cx)
                centers_y.append(cy)
            if centers_x and centers_y:
                margin_px = 30
                x_min = min(centers_x) - margin_px
                x_max = max(centers_x) + margin_px
                y_min = min(centers_y) - margin_px
                y_max = max(centers_y) + margin_px
                radius = self.frame_radius_var.get() if self.rounded_corners_var.get() else 0

                # Escalar el box con zoom
                box = (x_min * self.zoom_level, y_min * self.zoom_level,
                       x_max * self.zoom_level, y_max * self.zoom_level)

                # Dibujar contorno PCB usando canvas.create_line para no afectar líneas
                # Usamos líneas rectas para aproximar el rectángulo con esquinas redondeadas
                # Para simplicidad, dibujamos un rectángulo simple aquí (si quieres esquinas redondeadas,
                # habría que implementar dibujo en canvas con arcs y líneas)
                if radius == 0:
                    self.canvas.create_rectangle(*box, outline="green", width=3)
                else:
                    # Dibujar esquinas redondeadas en canvas (simplificado)
                    # Dibujar rectángulo con 4 arcos y 4 líneas
                    x1, y1, x2, y2 = box
                    r = radius * self.zoom_level
                    points = [
                        (x1 + r, y1),
                        (x2 - r, y1),
                        (x2, y1 + r),
                        (x2, y2 - r),
                        (x2 - r, y2),
                        (x1 + r, y2),
                        (x1, y2 - r),
                        (x1, y1 + r),
                    ]

                    # Líneas
                    self.canvas.create_line(points[0], points[1], fill="green", width=3)
                    self.canvas.create_line(points[2], points[3], fill="green", width=3)
                    self.canvas.create_line(points[4], points[5], fill="green", width=3)
                    self.canvas.create_line(points[6], points[7], fill="green", width=3)

                    # Arcos (usamos create_arc)
                    self.canvas.create_arc(x2 - 2*r, y1, x2, y1 + 2*r, start=270, extent=90, style="arc", outline="green", width=3)
                    self.canvas.create_arc(x2 - 2*r, y2 - 2*r, x2, y2, start=0, extent=90, style="arc", outline="green", width=3)
                    self.canvas.create_arc(x1, y2 - 2*r, x1 + 2*r, y2, start=90, extent=90, style="arc", outline="green", width=3)
                    self.canvas.create_arc(x1, y1, x1 + 2*r, y1 + 2*r, start=180, extent=90, style="arc", outline="green", width=3)

        # Dibujar líneas (pistas) con coordenadas escaladas
        for (p1, p2, grosor) in self.lines:
            x1, y1 = p1
            x2, y2 = p2
            x1_zoom = x1 * self.zoom_level
            y1_zoom = y1 * self.zoom_level
            x2_zoom = x2 * self.zoom_level
            y2_zoom = y2 * self.zoom_level
            grosor_zoom = max(1, int(grosor * self.zoom_level))
            self.canvas.create_line(x1_zoom, y1_zoom, x2_zoom, y2_zoom, fill="red", width=grosor_zoom)

    def zoom_in(self):
        if self.zoom_level < 3.0:
            self.zoom_level += 0.1
            self.mostrar_imagen()

    def zoom_out(self):
        if self.zoom_level > 0.2:
            self.zoom_level -= 0.1
            self.mostrar_imagen()

    def guardar_imagen(self):
        img_to_save = self.img_original.copy()
        draw = ImageDraw.Draw(img_to_save)

        # Dibujar líneas en imagen original
        for (p1, p2, grosor) in self.lines:
            draw.line([p1, p2], fill="red", width=grosor)

        # Dibujar contorno PCB si está activado (usando PIL)
        if self.draw_frame_var.get():
            centers_x = []
            centers_y = []
            for pad_dict in self.pad_positions:
                pads = list(pad_dict.values())
                cx = sum(p[0] for p in pads) / len(pads)
                cy = sum(p[1] for p in pads) / len(pads)
                centers_x.append(cx)
                centers_y.append(cy)
            if centers_x and centers_y:
                margin_px = 30
                x_min = min(centers_x) - margin_px
                x_max = max(centers_x) + margin_px
                y_min = min(centers_y) - margin_px
                y_max = max(centers_y) + margin_px
                box = (x_min, y_min, x_max, y_max)

                radius = self.frame_radius_var.get() if self.rounded_corners_var.get() else 0
                draw_rounded_rectangle(draw, box, radius, outline="green", width=3)

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")],
                                                 title="Guardar imagen como")
        if file_path:
            try:
                img_to_save.save(file_path, "PNG")
                messagebox.showinfo("Guardar imagen", f"Imagen guardada en:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error al guardar", str(e))

    def toggle_draw_mode(self):
        self.draw_mode = not self.draw_mode
        self.btn_draw_mode.config(text=f"Modo Dibujo {'ON' if self.draw_mode else 'OFF'}")
        if not self.draw_mode:
            self.selected_pad = None

    def click_canvas(self, event):
        if not self.draw_mode:
            return

        radio = 15
        x_click = event.x / self.zoom_level
        y_click = event.y / self.zoom_level

        closest_pad = None
        min_dist = float("inf")

        for pad_dict in self.pad_positions:
            for key in ['A', 'B']:
                px, py = pad_dict[key]
                dist = math.hypot(px - x_click, py - y_click)
                if dist < radio and dist < min_dist:
                    min_dist = dist
                    closest_pad = (px, py)

        if closest_pad is None:
            return

        if self.selected_pad is None:
            self.selected_pad = closest_pad
        else:
            grosor = self.line_thickness.get()
            self.lines.append((self.selected_pad, closest_pad, grosor))
            self.selected_pad = None
            self.mostrar_imagen()


if __name__ == "__main__":
    app = CherryMxViewer()
    app.mainloop()
