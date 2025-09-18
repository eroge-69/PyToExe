from ultralytics import YOLO
from tkinter import Tk, filedialog
Tk().withdraw()
image_path = filedialog.askopenfilename(
    title="Select an Image",
    filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")]
)

if image_path:
    # Load pretrained YOLOv8 model
    model = YOLO("yolov8n.pt")
    results = model.predict(source=image_path, show=True)
    for r in results:
        print(r.boxes)
else:
    print("❌ No file selected.")
