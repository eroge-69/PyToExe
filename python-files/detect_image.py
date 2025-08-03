from inference_sdk import InferenceHTTPClient
import cv2

# Khởi tạo client Roboflow
CLIENT = InferenceHTTPClient(
    api_url="https://serverless.roboflow.com",
    api_key="NixIpJrhX63GRhaDOElM"
)

# Đường dẫn ảnh
img_path = "Apples-184940975-770x533-1_jpg.webp"

# Gửi ảnh lên để dự đoán
result = CLIENT.infer(img_path, model_id="apples-fvpl5-kshpb/1")

# Load ảnh gốc
image = cv2.imread(img_path)

# Vẽ box cho từng prediction
for pred in result["predictions"]:
    x, y = int(pred["x"]), int(pred["y"])
    w, h = int(pred["width"]), int(pred["height"])
    class_name = pred["class"]
    confidence = pred["confidence"]

    # Tính toạ độ box
    x1, y1 = int(x - w / 2), int(y - h / 2)
    x2, y2 = int(x + w / 2), int(y + h / 2)

    # Vẽ box và nhãn
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    label = f"{class_name} {confidence:.2f}"
    cv2.putText(image, label, (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

# Đếm số lượng theo class
counts = {}
for pred in result["predictions"]:
    cls = pred["class"]
    counts[cls] = counts.get(cls, 0) + 1

# In ra số lượng
print("Số lượng từng class:")
for cls, count in counts.items():
    print(f"{cls}: {count}")

# Resize vừa màn hình 1920x1080, giữ tỷ lệ
screen_w, screen_h = 1920, 1080
h, w = image.shape[:2]
scale = min(screen_w / w, screen_h / h)
new_w = int(w * scale)
new_h = int(h * scale)
resized = cv2.resize(image, (new_w, new_h))

# Hiển thị ảnh
cv2.imshow("Result", resized)
cv2.waitKey(0)
cv2.destroyAllWindows()
