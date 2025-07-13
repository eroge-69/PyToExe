import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image, ImageDraw, ImageTk
import os

CELL_SIZE = 16
GRID_WIDTH = 32
GRID_HEIGHT = 32
EXPORT_SIZE = 4

class PixelAnimationApp:
    def __init__(self, root):
        self.root = root
        self.root.resizable(False, False)
        self.root.iconbitmap("icon.ico")
        self.root.title("Alamo Animator")
        self.color = "#000000"
        self.tool = "pen"
        self.frames = [self.new_empty_frame()]
        self.current_frame = 0
        self.frame_delay = 200
        self.show_grid = True
        self.show_onion = True
        self.playing = False

        self.prev_show_grid = self.show_grid
        self.prev_show_onion = self.show_onion

        self.canvas = tk.Canvas(root, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE, bg="white")
        self.canvas.grid(row=0, column=0, rowspan=10)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-1>", self.paint)

        # Controls frame
        self.controls = tk.Frame(root)
        self.controls.grid(row=0, column=1, sticky="n")

        tk.Label(self.controls, text="Tools", font=("Arial", 10, "bold")).pack(pady=2)
        tk.Button(self.controls, text="Pen", command=lambda: self.set_tool("pen")).pack(fill="x")
        tk.Button(self.controls, text="Eraser", command=lambda: self.set_tool("eraser")).pack(fill="x")
        tk.Button(self.controls, text="Color", command=self.choose_color).pack(fill="x", pady=5)

        tk.Label(self.controls, text="Playback", font=("Arial", 10, "bold")).pack(pady=2)
        tk.Button(self.controls, text="Play", command=self.play_animation).pack(fill="x")
        tk.Button(self.controls, text="Stop", command=self.stop_animation).pack(fill="x")

        tk.Label(self.controls, text="Speed (ms/frame):").pack()
        self.speed_entry = tk.Entry(self.controls)
        self.speed_entry.insert(0, str(self.frame_delay))
        self.speed_entry.pack()
        tk.Button(self.controls, text="Set Speed", command=self.set_speed).pack(fill="x", pady=2)

        self.grid_toggle = tk.Checkbutton(self.controls, text="Show Grid", command=self.toggle_grid)
        self.grid_toggle.select()
        self.grid_toggle.pack()

        self.onion_toggle = tk.Checkbutton(self.controls, text="Onion Skin", command=self.toggle_onion)
        self.onion_toggle.select()
        self.onion_toggle.pack()

        tk.Label(self.controls, text="Export", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Button(self.controls, text="Export as GIF", command=self.export_gif).pack(fill="x")
        tk.Button(self.controls, text="Export as PNGs", command=self.export_pngs).pack(fill="x")

        # Scrollable Timeline setup
        self.timeline_canvas = tk.Canvas(root, height=50)
        self.timeline_scrollbar = tk.Scrollbar(root, orient="horizontal", command=self.timeline_canvas.xview)
        self.timeline_inner_frame = tk.Frame(self.timeline_canvas)

        self.timeline_inner_frame.bind(
            "<Configure>",
            lambda e: self.timeline_canvas.configure(scrollregion=self.timeline_canvas.bbox("all"))
        )

        self.timeline_canvas.create_window((0, 0), window=self.timeline_inner_frame, anchor="nw")
        self.timeline_canvas.configure(xscrollcommand=self.timeline_scrollbar.set)

        self.timeline_canvas.grid(row=10, column=0, columnspan=2, sticky="ew")
        self.timeline_scrollbar.grid(row=11, column=0, columnspan=2, sticky="ew")

        # Remove frame button below timeline scrollbar
        self.remove_btn = tk.Button(root, text="Remove Current Frame", command=self.remove_current_frame)
        self.remove_btn.grid(row=12, column=0, columnspan=2, pady=5)

        self.update_timeline()
        self.update_remove_button_state()
        self.draw_grid()

    def new_empty_frame(self):
        return [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

    def set_tool(self, tool):
        self.tool = tool

    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.color = color

    def paint(self, event):
        x, y = event.x // CELL_SIZE, event.y // CELL_SIZE
        if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
            self.frames[self.current_frame][y][x] = self.color if self.tool == "pen" else None
            self.draw_pixel(x, y)

    def draw_pixel(self, x, y):
        if self.show_grid and not self.frames[self.current_frame][y][x]:
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                outline="#ccc", fill="", width=1
            )
        color = self.frames[self.current_frame][y][x]
        if color:
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                fill=color, width=0
            )
        elif self.show_grid:
            self.canvas.create_rectangle(
                x * CELL_SIZE, y * CELL_SIZE,
                (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                outline="#ccc", width=1
            )

    def draw_grid(self):
        self.canvas.delete("all")

        if self.show_onion and self.current_frame > 0:
            img = Image.new("RGBA", (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            prev = self.frames[self.current_frame - 1]
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    color = prev[y][x]
                    if color:
                        r, g, b = self.hex_to_rgb(color)
                        draw.rectangle(
                            [x * CELL_SIZE, y * CELL_SIZE, (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE],
                            fill=(r, g, b, 100)
                        )
            self.tk_onion = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_onion)

        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = self.frames[self.current_frame][y][x]
                if color:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE, y * CELL_SIZE,
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                        fill=color, width=0
                    )
                elif self.show_grid:
                    self.canvas.create_rectangle(
                        x * CELL_SIZE, y * CELL_SIZE,
                        (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE,
                        outline="#ccc", width=1
                    )

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def toggle_grid(self):
        self.show_grid = not self.show_grid
        self.draw_grid()

    def toggle_onion(self):
        self.show_onion = not self.show_onion
        self.draw_grid()

    def set_speed(self):
        try:
            self.frame_delay = max(50, int(self.speed_entry.get()))
        except ValueError:
            pass

    def play_animation(self):
        if self.playing:
            return
        self.prev_show_grid = self.show_grid
        self.prev_show_onion = self.show_onion
        self.show_grid = False
        self.show_onion = False
        self.grid_toggle.deselect()
        self.onion_toggle.deselect()
        self.playing = True
        self._play_loop(0)

    def stop_animation(self):
        if not self.playing:
            return
        self.playing = False
        self.show_grid = self.prev_show_grid
        self.show_onion = self.prev_show_onion
        if self.show_grid:
            self.grid_toggle.select()
        else:
            self.grid_toggle.deselect()
        if self.show_onion:
            self.onion_toggle.select()
        else:
            self.onion_toggle.deselect()
        self.draw_grid()

    def _play_loop(self, idx):
        if not self.playing:
            return
        self.current_frame = idx
        self.draw_grid()
        self.update_timeline()
        self.root.after(self.frame_delay, lambda: self._play_loop((idx + 1) % len(self.frames)))

    def export_gif(self):
        filename = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
        if not filename:
            return
        images = []
        for frame in self.frames:
            img = Image.new("RGB", (GRID_WIDTH, GRID_HEIGHT), "white")
            draw = ImageDraw.Draw(img)
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    color = frame[y][x]
                    if color:
                        draw.point((x, y), fill=color)
            img = img.resize((GRID_WIDTH * EXPORT_SIZE, GRID_HEIGHT * EXPORT_SIZE), Image.NEAREST)
            images.append(img)
        images[0].save(filename, save_all=True, append_images=images[1:], duration=self.frame_delay, loop=0)

    def export_pngs(self):
        folder = filedialog.askdirectory(title="Choose folder to save PNGs")
        if not folder:
            return
        for i, frame in enumerate(self.frames):
            img = Image.new("RGB", (GRID_WIDTH, GRID_HEIGHT), "white")
            draw = ImageDraw.Draw(img)
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    color = frame[y][x]
                    if color:
                        draw.point((x, y), fill=color)
            img = img.resize((GRID_WIDTH * EXPORT_SIZE, GRID_HEIGHT * EXPORT_SIZE), Image.NEAREST)
            img.save(os.path.join(folder, f"frame_{i:03d}.png"))

    def update_timeline(self):
        for widget in self.timeline_inner_frame.winfo_children():
            widget.destroy()

        for i, frame in enumerate(self.frames):
            preview = self.create_thumbnail(frame)
            btn = tk.Button(self.timeline_inner_frame, image=preview, command=lambda idx=i: self.switch_frame(idx))
            btn.image = preview
            btn.grid(row=0, column=i, padx=2)

        add_btn = tk.Button(self.timeline_inner_frame, text="+", command=self.add_frame, width=3)
        add_btn.grid(row=0, column=len(self.frames), padx=5)

    def switch_frame(self, idx):
        self.current_frame = idx
        self.draw_grid()
        self.update_timeline()
        self.update_remove_button_state()

    def add_frame(self):
        self.frames.append(self.new_empty_frame())
        self.current_frame = len(self.frames) - 1
        self.draw_grid()
        self.update_timeline()
        self.update_remove_button_state()
        self.root.after(10, lambda: self.timeline_canvas.xview_moveto(1.0))

    def remove_current_frame(self):
        if len(self.frames) > 1:
            del self.frames[self.current_frame]
            if self.current_frame >= len(self.frames):
                self.current_frame = len(self.frames) - 1
            self.draw_grid()
            self.update_timeline()
            self.update_remove_button_state()

    def update_remove_button_state(self):
        if len(self.frames) <= 1:
            self.remove_btn.config(state="disabled")
        else:
            self.remove_btn.config(state="normal")

    def create_thumbnail(self, frame):
        thumb = Image.new("RGB", (GRID_WIDTH, GRID_HEIGHT), "white")
        draw = ImageDraw.Draw(thumb)
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                color = frame[y][x]
                if color:
                    draw.point((x, y), fill=color)
        thumb = thumb.resize((32, 32), Image.NEAREST)
        return ImageTk.PhotoImage(thumb)

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelAnimationApp(root)
    root.mainloop()
