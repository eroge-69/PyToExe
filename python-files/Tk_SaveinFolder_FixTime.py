import requests
import pandas as pd
import tkinter as tk #using python3 so is tkinter
from tkinter import ttk, messagebox
import cv2
import os
from PIL import Image, ImageTk
import datetime
from datetime import datetime, timedelta


def convert_iso_to_local(iso_str):
    # try:
    #     dt_utc = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
    #     malaysia_time = dt_utc + timedelta(hours=8)  # UTC+8 for Malaysia
    #     return malaysia_time.strftime("%-m/%-d/%Y %-I:%M:%S %p")
    try:
        # Handle both with/without milliseconds
        if "." in iso_str:
            dt_utc = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        else:
            dt_utc = datetime.strptime(iso_str, "%Y-%m-%dT%H:%M:%SZ")
        malaysia_time = dt_utc + timedelta(hours=8)
        return malaysia_time.strftime("%-m/%-d/%Y %-I:%M:%S %p")
    except:
        return iso_str  # If already formatted or invalid


# ====== Fetch data from Google Apps Script Web App ======
url = "https://script.google.com/macros/s/AKfycbxofq77n9OQj5Bbpnp9YXXSL-yxKjClA-uvdGgI_usK7Y7S4420jDkQuq5Uml4FSODf/exec"

response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data)

    # 🔹 Convert all ISO timestamps to Malaysia time
    for col in df.columns:
         if df[col].astype(str).str.contains("T").any():
            df[col] = df[col].apply(convert_iso_to_local)
else:
    messagebox.showerror("Error", f"Failed to fetch data: {response.status_code}")
    exit()

photo_refs = {}  # Keep image references alive





# ====== Functions ======
def load_table(dataframe):
    tree.delete(*tree.get_children())
    for _, row in dataframe.iterrows():
        tree.insert("", "end", values=list(row))


def search_wo():
    wo_value = entry_wo.get().strip()
    if wo_value:
        result_df = df[df['WO'].astype(str).str.contains(wo_value, case=False, na=False)]
        if not result_df.empty:
            load_table(result_df)
        else:
            messagebox.showinfo("Not Found", f"No Work Orders matching '{wo_value}'.")
            load_table(df)
    else:
        load_table(df)


def on_row_select(event):
    selected = tree.focus()
    if not selected:
        return

    values = tree.item(selected, "values")
    if not values:
        return

    try:
        start_num = int(values[df.columns.get_loc('Starting Running Number')])
        end_num = int(values[df.columns.get_loc('End Running Number')])
    except ValueError:
        messagebox.showerror("Error", "Start/End running numbers are invalid.")
        return

    global selected_wo
    selected_wo = values[df.columns.get_loc('WO')]

    for widget in photo_inner_frame.winfo_children():
        widget.destroy()

    total_photos = end_num - start_num + 1
    if total_photos <= 0:
        messagebox.showinfo("Info", "No photos required for this range.")
        return

    tk.Label(photo_inner_frame, text=f"Snap {total_photos} Photos:", font=("Arial", 10, "bold")).pack(anchor="w",
                                                                                                      pady=2)

    wo_folder = os.path.join(SAVE_BASE_PATH, str(selected_wo))
    os.makedirs(wo_folder, exist_ok=True)

    for i in range(total_photos):
        running_number = start_num + i
        frame_row = tk.Frame(photo_inner_frame)
        frame_row.pack(fill=tk.X, pady=2)

        tk.Label(frame_row, text=f"Running Number {start_num + i}:").pack(side=tk.LEFT, padx=5)
        tk.Button(frame_row, text="Snap Photo", command=lambda idx=i, fr=frame_row: snap_photo(idx, fr)).pack(
            side=tk.LEFT, padx=5)


        filename = os.path.join(wo_folder, f"Running Number {running_number}.jpg")
        if os.path.exists(filename):
            try:
                img = Image.open(filename)
                img.thumbnail((100, 100))
                photo = ImageTk.PhotoImage(img)
                photo_refs[f"{selected_wo}_{running_number}"] = photo  # Keep reference
                lbl_img = tk.Label(frame_row, image=photo)
                lbl_img.pack(side=tk.LEFT, padx=5)
            except Exception as e:
                print(f"Error loading {filename}: {e}")


SAVE_BASE_PATH = r"C:\Users\ws_lim\Desktop\Python Project LAM Semi 3\WO Photo Blocked by google drive"


def snap_photo(index, frame_container):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        messagebox.showerror("Camera Error", "Unable to access camera.")
        return

    messagebox.showinfo("Camera", f"Press SPACE to capture Photo {index + 1}, or close the window to cancel.")

    while True:
        ret, frame = cap.read()
        if not ret:
            messagebox.showerror("Camera Error", "Failed to capture frame.")
            break

        cv2.imshow("Camera - Press SPACE to Capture", frame)
        key = cv2.waitKey(1)

        # Detect if user closed the window
        if cv2.getWindowProperty("Camera - Press SPACE to Capture", cv2.WND_PROP_VISIBLE) < 1:
            break

        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE

            wo_folder = os.path.join(SAVE_BASE_PATH, str(selected_wo))
            os.makedirs(wo_folder, exist_ok=True)
            # Get Starting Running Number for correct file naming
            start_num = int(tree.item(tree.focus(), "values")[df.columns.get_loc('Starting Running Number')])
            running_number = start_num + index
            filename = os.path.join(wo_folder, f"Running Number {running_number}.jpg")
            if os.path.exists(filename):
                base, ext = os.path.splitext(filename)
                count = 1
                while os.path.exists(f"{base} ({count}){ext}"):
                    count += 1
                filename = f"{base} ({count}){ext}"

            cv2.imwrite(filename, frame)
            cap.release()
            cv2.destroyAllWindows()

            img = Image.open(filename)
            img.thumbnail((100, 100))
            photo = ImageTk.PhotoImage(img)
            photo_refs[index] = photo

            lbl_img = tk.Label(frame_container, image=photo)
            lbl_img.pack(side=tk.LEFT, padx=5)

            messagebox.showinfo("Saved", f"Running Number Photo {index + 1} saved and displayed.")
            return

    cap.release()
    cv2.destroyAllWindows()


def on_mousewheel(event):
    """Enable mouse wheel scrolling on canvas."""
    canvas_photos.yview_scroll(int(-1 * (event.delta / 120)), "units")


#Tkinter Setup declare as root
root = tk.Tk()
root.title("SEMI 3 LAM WO Filtering System")
root.geometry("1500x700")
root.configure(bg="lightblue")

# ====== Search Bar ======z
frame_search = tk.Frame(root)
frame_search.pack(fill=tk.X, padx=10, pady=5)

tk.Label(frame_search, text="Enter Work Order:").pack(side=tk.LEFT, padx=5)
entry_wo = tk.Entry(frame_search)
entry_wo.pack(side=tk.LEFT, padx=5)
btn_search = tk.Button(frame_search, text="Search", command=search_wo)
btn_search.pack(side=tk.LEFT, padx=5)

# ====== Table Frame ======
frame_table = tk.Frame(root)
frame_table.pack(fill=tk.BOTH, expand=True)

tree_scroll_y = tk.Scrollbar(frame_table, orient="vertical")
tree_scroll_x = tk.Scrollbar(frame_table, orient="horizontal")
tree_scroll_y.pack(side="right", fill="y")
tree_scroll_x.pack(side="bottom", fill="x")

tree = ttk.Treeview(frame_table, yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set)
tree.pack(fill=tk.BOTH, expand=True)

tree_scroll_y.config(command=tree.yview)
tree_scroll_x.config(command=tree.xview)

tree["columns"] = list(df.columns)
tree["show"] = "headings"

for col in df.columns:
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor="w")

tree.bind("<<TreeviewSelect>>", on_row_select)

# ====== Scrollable Photo Section ======
frame_photos = tk.LabelFrame(root, text="Photo Capture Section", padx=10, pady=10)
frame_photos.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

canvas_photos = tk.Canvas(frame_photos)
scrollbar_photos = tk.Scrollbar(frame_photos, orient="vertical", command=canvas_photos.yview)
photo_inner_frame = tk.Frame(canvas_photos)

photo_inner_frame.bind(
    "<Configure>",
    lambda e: canvas_photos.configure(scrollregion=canvas_photos.bbox("all"))
)

canvas_photos.create_window((0, 0), window=photo_inner_frame, anchor="nw")
canvas_photos.configure(yscrollcommand=scrollbar_photos.set)

canvas_photos.pack(side="left", fill="both", expand=True)
scrollbar_photos.pack(side="right", fill="y")

#  Bind mouse wheel to scroll
canvas_photos.bind_all("<MouseWheel>", on_mousewheel)  # Windows & Mac
canvas_photos.bind_all("<Button-4>", lambda e: canvas_photos.yview_scroll(-1, "units"))  # Linux scroll up
canvas_photos.bind_all("<Button-5>", lambda e: canvas_photos.yview_scroll(1, "units"))  # Linux scroll down

load_table(df)

root.mainloop()
