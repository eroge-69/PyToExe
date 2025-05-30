import json
import base64
import gzip
import io
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
from tkinter import ttk
import os
from functools import partial

all_shapes = {
    0: [(0, 0)],
    1: [(0, 0), (1, 0), (0, 1), (1, 1)],
    2: [(0, 0), (1, 0)],
    3: [(0, 0), (0, 1)],
    4: [(0, 0), (1, 0), (2, 0)],
    5: [(0, 0), (0, 1), (0, 2)],
    6: [(0, 0), (1, 0), (2, 0), (3, 0)],
    7: [(0, 0), (0, 1), (0, 2), (0, 3)],
    8: [(0, 0), (1, 0), (0, 1)],
    9: [(0, 0), (0, 1), (1, 1)],
    10: [(0, 1), (1, 0), (1, 1)],
    11: [(0, 0), (1, 0), (1, 1)],
    12: [(0, 0), (0, 1), (1, 0), (2, 0)],
    13: [(0, 0), (0, 1), (0, 2), (1, 2)],
    14: [(0, 1), (1, 1), (2, 1), (2, 0)],
    15: [(0, 0), (1, 0), (1, 1), (1, 2)],
    16: [(0, 0), (0, 1), (1, 0), (0, 2)],
    17: [(0, 0), (0, 1), (1, 1), (2, 1)],
    18: [(0, 2), (1, 2), (1, 1), (1, 0)],
    19: [(0, 0), (1, 0), (2, 0), (2, 1)],
    20: [(0, 0), (0, 1), (0, 2), (1, 0), (2, 0)],
    21: [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)],
    22: [(0, 2), (1, 2), (2, 2), (2, 1), (2, 0)],
    23: [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2)],
    24: [(0, 1), (1, 1), (2, 1), (1, 0)],
    25: [(1, 0), (0, 1), (1, 1), (1, 2)],
    26: [(0, 0), (1, 0), (2, 0), (1, 1)],
    27: [(0, 0), (0, 1), (0, 2), (1, 1)],
    28: [(0, 2), (1, 2), (2, 2), (1, 1), (1, 0)],
    29: [(0, 1), (1, 1), (2, 1), (2, 0), (2, 2)],
    30: [(0, 0), (1, 0), (2, 0), (1, 1), (1, 2)],
    31: [(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)],
    32: [(1, 0), (1, 1), (0, 1), (2, 0)],
    33: [(0, 0), (0, 1), (1, 1), (1, 2)],
    34: [(0, 0), (1, 0), (1, 1), (2, 1)],
    35: [(1, 0), (1, 1), (0, 1), (0, 2)],
    36: [(1, 0), (0, 1), (1, 1), (2, 1), (1, 2)],
}

def load_data(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    b64data = raw['mapData']
    compressed = base64.b64decode(b64data)
    with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as gz:
        decompressed = gz.read()
    data = json.loads(decompressed.decode('utf-8'))
    return data

def get_max_coordinates(data):
    xs, ys = [], []
    if 'floorData' in data:
        xs.extend([pos['x'] for pos in data['floorData']])
        ys.extend([pos['y'] for pos in data['floorData']])
    if 'blockData' in data:
        xs.extend([pos['x'] for pos in data['blockData']])
        ys.extend([pos['y'] for pos in data['blockData']])
    if 'mapData' in data:
        xs.extend([pos['x'] for pos in data['mapData']])
        ys.extend([pos['y'] for pos in data['mapData']])
    max_x = max(xs)
    max_y = max(ys)
    return max_x, max_y

def floor_data_to_grid(floor_data, max_x, max_y):
    grid = np.zeros((max_y + 1, max_x + 1), dtype=int)
    for pos in floor_data:
        grid[pos['y'], pos['x']] = 1
    return grid

def build_color_map(block_data, map_data):
    used_colors = set()

    for b in block_data:
        color = b.get('color1')
        if color is not None:
            used_colors.add(color)

    for m in map_data:
        color = m.get('color')
        if color is not None:
            used_colors.add(color)

    # Ánh xạ số sang màu
    color_map_custom = {
        0: '#FF66CC',
        1: '#AE2626', #ok
        2: '#E87e18', #ok
        3: '#E8b51d', #ok
        4: '#62A32B', #ok
        5: '#16328A', #ok
        6: '#2c9caa', #ok
        7: '#5E2E90', #ok
        8: '#FF66CC',
        9:  '#286028', #ok
        10: '#1E57C1', #ok
        11: '#FF6699',
        12: '#339999',
        13: '#9966FF',
        14: '#FFCC66',
        15: '#6699FF',
        16: '#CC6666',
        17: '#4FABC9', #ok
        18: '#999966',
    }

    # Mặc định nếu thiếu màu trong bảng
    default_palette = list(plt.cm.tab10.colors)

    cmap = {}
    for i, color in enumerate(sorted(used_colors)):
        cmap[color] = color_map_custom.get(color, default_palette[i % len(default_palette)])

    return cmap


def prepare_block_index_grid(block_data, all_shapes, width, height):
    grid = np.full((height, width), -1, dtype=int)
    if not all_shapes:
        for b in block_data:
            all_shapes[b['shape']] = [(0,0)]
    for idx, b in enumerate(block_data):
        x0, y0 = b['x'], b['y']
        shape = b['shape']
        coords = all_shapes.get(shape, [(0,0)])
        for dx, dy in coords:
            x, y = x0+dx, y0+dy
            if 0 <= x < width and 0 <= y < height:
                grid[y, x] = idx
    return grid

def create_map_canvas(map_data, width, height, color_map):
    canvas = np.zeros((height, width), dtype=int)
    colors = np.full((height, width), 'black', dtype=object)

    for item in map_data:
        x, y = item['x'], item['y']
        shape = item.get('shape', 0)
        color_id = item.get('color', 0)
        color = color_map.get(color_id, 'black')
        size = item.get('size', 1)

        # Vẽ dọc
        if shape in [11, 10, 9, 8]:
            for dy in range(size):
                ny = y + dy
                if 0 <= x < width and 0 <= ny < height:
                    canvas[ny, x] = shape
                    colors[ny, x] = color

        # Vẽ ngang
        elif shape in [7, 6, 5, 4]:
            for dx in range(size):
                nx = x + dx
                if 0 <= nx < width and 0 <= y < height:
                    canvas[y, nx] = shape
                    colors[y, nx] = color

        # Vẽ 1 ô
        else:
            if 0 <= x < width and 0 <= y < height:
                canvas[y, x] = 1
                colors[y, x] = color

    return canvas, colors

def draw_arrow(ax, x, y, direction):
    center = (x + 0.5, y + 0.5)
    if direction == 'right_to_left':
        ax.arrow(center[0] + 0.2, center[1], -0.4, 0,
                 head_width=0.3, head_length=0.2, fc='black', ec='black')
    elif direction == 'left_to_right':
        ax.arrow(center[0] - 0.2, center[1], 0.4, 0,
                 head_width=0.3, head_length=0.2, fc='black', ec='black')
    elif direction == 'top_to_bottom':
        ax.arrow(center[0], center[1] + 0.2, 0, -0.4,
                 head_width=0.3, head_length=0.2, fc='black', ec='black')
    elif direction == 'bottom_to_top':
        ax.arrow(center[0], center[1] - 0.2, 0, 0.4,
                 head_width=0.3, head_length=0.2, fc='black', ec='black')

def draw_level_shape(data):
    max_x, max_y = get_max_coordinates(data)
    floor_grid = floor_data_to_grid(data['floorData'], max_x, max_y)
    height, width = floor_grid.shape

    block_data = data['blockData']
    map_data = data['mapData']
    color_map = build_color_map(block_data, map_data)

    block_index_grid = prepare_block_index_grid(block_data, all_shapes, width, height)
    map_canvas, map_colors = create_map_canvas(map_data, width, height, color_map)

    fig, ax = plt.subplots(figsize=(8, 8))

    for y in range(height):
        for x in range(width):
            if floor_grid[y, x] == 1:
                ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor='lightgray', edgecolor='gray'))

            bidx = block_index_grid[y, x]
            if bidx != -1 and 0 <= bidx < len(block_data):
                block = block_data[bidx]
                color_id = block.get('color1', 0)
                color = color_map.get(color_id, 'gray')
                ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=color))

                # Vẽ viền nếu khác block
                if y == height - 1 or block_index_grid[y + 1, x] != bidx:
                    ax.plot([x, x + 1], [y + 1, y + 1], color='black', linewidth=2.5)
                if y == 0 or block_index_grid[y - 1, x] != bidx:
                    ax.plot([x, x + 1], [y, y], color='black', linewidth=2.5)
                if x == 0 or block_index_grid[y, x - 1] != bidx:
                    ax.plot([x, x], [y, y + 1], color='black', linewidth=2.5)
                if x == width - 1 or block_index_grid[y, x + 1] != bidx:
                    ax.plot([x + 1, x + 1], [y, y + 1], color='black', linewidth=2.5)

            shape = map_canvas[y, x]
            if shape != 0 or map_colors[y, x] != 'black':
                face_color = map_colors[y, x]
                ax.add_patch(patches.Rectangle((x, y), 1, 1, facecolor=face_color, alpha=1.0))
                ax.text(x + 0.5, y + 0.5, str(shape), ha='center', va='center', fontsize=6, color='white')
                if shape == 11:
                    draw_arrow(ax, x, y, 'right_to_left')
                elif shape == 9:
                    draw_arrow(ax, x, y, 'left_to_right')
                elif shape == 7:
                    draw_arrow(ax, x, y, 'top_to_bottom')
                elif shape == 5:
                    draw_arrow(ax, x, y, 'bottom_to_top')

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])
    return fig

selected_index = -1
preview_widgets = []
preview_images = []
preview_paths = []
preview_titles = []


def figure_to_image(fig, scale=1.0):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=int(fig.get_dpi() * scale), bbox_inches='tight')
    buf.seek(0)
    image = Image.open(buf)
    return image

def refresh_thumbnail_grid():
    for i, widget in enumerate(preview_widgets):
        widget.grid(row=i // max_cols, column=i % max_cols, padx=10, pady=10)
        img_label = widget.winfo_children()[1]
        img_label.bind("<Button-1>", lambda e, idx=i: (
            set_selected_index(idx),
            update_preview(idx)
        ))

def on_key(event):
    global selected_index
    if not preview_images:
        return

    num_items = len(preview_images)
    cols = 3
    rows = (num_items + cols - 1) // cols
    row = selected_index // cols if selected_index != -1 else 0
    col = selected_index % cols if selected_index != -1 else 0

    if event.keysym == "Right":
        col = (col + 1) % cols
    elif event.keysym == "Left":
        col = (col - 1 + cols) % cols
    elif event.keysym == "Down":
        row = (row + 1) % rows
    elif event.keysym == "Up":
        row = (row - 1 + rows) % rows
    elif event.keysym == "Delete":
        if selected_index != -1:
            file_to_delete = preview_paths[selected_index]
            delete_file_callback(selected_index, file_to_delete)
        return  # Tránh update nếu đang xóa
    else:
        return

    new_index = row * cols + col
    if 0 <= new_index < num_items:
        selected_index = new_index
        update_preview(new_index)


def update_preview(index):
    for widget in preview_frame.winfo_children():
        widget.pack_forget()

    label = tk.Label(preview_frame, text=preview_titles[index], font=("Arial", 10, "bold"), bg="white")
    label.pack(pady=(10, 5))

    image_label = tk.Label(preview_frame, image=preview_images[index])
    image_label.image = preview_images[index]
    image_label.pack(fill="both", expand=True)

    for i, widget in enumerate(preview_widgets):
        if i == index:
            widget.config(highlightbackground="red", highlightcolor="red", highlightthickness=2)
        else:
            widget.config(highlightthickness=0)

    # Scroll đến widget đang chọn nếu bị khuất
    selected_widget = preview_widgets[index]
    canvas_wrapper.update_idletasks()

    widget_top = selected_widget.winfo_rooty()
    canvas_top = canvas_wrapper.winfo_rooty()
    widget_relative_y = widget_top - canvas_top

    if widget_relative_y < 0 or widget_relative_y > canvas_wrapper.winfo_height() - selected_widget.winfo_height():
        canvas_wrapper.yview_moveto(selected_widget.winfo_y() / frame_grid.winfo_height())

def _on_mousewheel(event):
    if event.delta:
        canvas_wrapper.yview_scroll(int(-1 * (event.delta / 120)), "units")
    elif hasattr(event, 'num'):
        if event.num == 4:
            canvas_wrapper.yview_scroll(-1, "units")
        elif event.num == 5:
            canvas_wrapper.yview_scroll(1, "units")

def enable_scroll_on_enter(widget):
    widget.bind("<Enter>", lambda e: _bind_mousewheel())
    widget.bind("<Leave>", lambda e: _unbind_mousewheel())

def _bind_mousewheel():
    canvas_wrapper.bind_all("<MouseWheel>", _on_mousewheel)
    canvas_wrapper.bind_all("<Button-4>", _on_mousewheel)
    canvas_wrapper.bind_all("<Button-5>", _on_mousewheel)

def _unbind_mousewheel():
    canvas_wrapper.unbind_all("<MouseWheel>")
    canvas_wrapper.unbind_all("<Button-4>")
    canvas_wrapper.unbind_all("<Button-5>")


root = tk.Tk()
root.title("Preview level shapes - Powered by CDIT")
root.geometry("1200x768")
root.bind("<Key>", on_key)

btn = tk.Button(root, text="Chọn các file để preview")
btn.pack(padx=10, pady=10)

progress_frame = tk.Frame(root)
progress_frame.pack(pady=(0, 10))

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=400, variable=progress_var, mode="determinate")
progress_bar.pack()

progress_label = tk.Label(progress_frame, text="", font=("Arial", 10))
progress_label.pack_forget()  # Ẩn ban đầu


main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True)

canvas_wrapper = tk.Canvas(main_frame, width=700)
scroll_y = tk.Scrollbar(main_frame, orient="vertical", command=canvas_wrapper.yview)
scroll_y.pack(side="right", fill="y")

canvas_wrapper.pack(side="left", fill="both", expand=True)
canvas_wrapper.configure(yscrollcommand=scroll_y.set)

frame_grid = tk.Frame(canvas_wrapper)
canvas_wrapper.create_window((0, 0), window=frame_grid, anchor="nw")

preview_frame = tk.Frame(main_frame, bg="white", width=500)
preview_frame.pack(side="left", fill="both", expand=True)


def on_frame_configure(event):
    canvas_wrapper.configure(scrollregion=canvas_wrapper.bbox("all"))

frame_grid.bind("<Enter>", lambda e: canvas_wrapper.bind("<MouseWheel>", _on_mousewheel))
frame_grid.bind("<Leave>", lambda e: canvas_wrapper.unbind("<MouseWheel>"))
frame_grid.bind("<Leave>", lambda e: (
    frame_grid.unbind_all("<Button-4>"),
    frame_grid.unbind_all("<Button-5>")
))

frame_grid.bind("<Configure>", on_frame_configure)
enable_scroll_on_enter(frame_grid)


canvas_widget = None

def set_selected_index(idx):
    global selected_index
    selected_index = idx

filepaths = []
total_files = 0
max_cols = 3

def delete_file_callback(index, path):
    if messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa file:\n{path}?"):
        try:
            os.remove(path)

            preview_widgets[index].destroy()
            preview_widgets.pop(index)
            preview_images.pop(index)
            preview_titles.pop(index)
            preview_paths.pop(index)  # ✅ Xóa luôn đường dẫn tương ứng

            global selected_index
            if selected_index == index:
                selected_index = -1
                for w in preview_frame.winfo_children():
                    w.destroy()
            elif selected_index > index:
                selected_index -= 1

            # Cập nhật lại vị trí + callback
            refresh_thumbnail_grid()

            if selected_index != -1 and selected_index < len(preview_images):
                update_preview(selected_index)

        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa file:\n{path}\n\n{e}")


def select_and_preview(index, event=None):
    global selected_index
    selected_index = index
    update_preview(index)


def on_open():
    global filepaths, total_files, selected_index
    global preview_widgets, preview_images, preview_titles

    progress_label.pack_forget()
    progress_bar.pack()

    filepaths = filedialog.askopenfilenames(
        title="Chọn nhiều file gen1.txt",
        filetypes=[("JSON files", "*.txt *.json"), ("All files", "*.*")]
    )
    if not filepaths:
        return

    total_files = len(filepaths)
    progress_var.set(0)
    progress_bar["maximum"] = total_files
    root.update_idletasks()

    # Reset lại UI
    for widget in frame_grid.winfo_children():
        widget.destroy()
    for widget in preview_frame.winfo_children():
        widget.destroy()

    preview_widgets = []
    preview_images = []
    preview_titles = []
    selected_index = -1

    def load_and_display(idx, filepath):
        try:
            data = load_data(filepath)
            fig = draw_level_shape(data)

            thumb_img = figure_to_image(fig, scale=0.3)
            photo_thumb = ImageTk.PhotoImage(thumb_img)

            # Tạo ảnh preview lớn
            preview_full = figure_to_image(fig, scale=0.8)
            photo_preview = ImageTk.PhotoImage(preview_full)

            fig.clf()
            plt.close(fig)

            frame_item = tk.Frame(frame_grid, highlightthickness=0)
            frame_item.grid(row=idx // max_cols, column=idx % max_cols, padx=10, pady=10)

            filename = filepath.split("/")[-1]
            label = tk.Label(frame_item, text=filename, font=("Arial", 9, "bold"))
            label.pack()

            label_img = tk.Label(frame_item, image=photo_thumb)
            label_img.image = photo_thumb
            label_img.pack()

            preview_widgets.append(frame_item)
            preview_images.append(photo_preview)
            preview_titles.append(filename)
            preview_paths.append(filepath)  # ✅ Lưu full path


            curr_index = len(preview_images) - 1

            btn_delete = tk.Button(frame_item, text="Xóa", fg="red", font=("Arial", 8, "bold"))
            btn_delete.config(command=lambda path=filepath: delete_file_callback(preview_paths.index(path), path))
            btn_delete.pack(pady=(4, 0))

            label_img.bind("<Button-1>", partial(select_and_preview, curr_index))

        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi xử lý file:\n{filepath}\n\n{e}")

    def process_next_file(index):
        if index >= total_files:
            progress_bar.pack_forget()
            progress_label.config(text="Successfully loaded!")
            progress_label.pack()
            return

        filepath = filepaths[index]
        load_and_display(index, filepath)
        progress_var.set(index + 1)
        root.update_idletasks()
        root.after(10, lambda: process_next_file(index + 1))

    process_next_file(0)


btn.config(command=on_open)

root.mainloop()
