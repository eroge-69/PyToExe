import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import face_recognition
import os

# متغیرهای جهانی
known_encodings = []
video_file_path = ""

def select_face_images():
    global known_encodings
    file_paths = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.png;*.jpeg")])
    if file_paths:
        known_encodings = []
        for path in file_paths:
            image = face_recognition.load_image_file(path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_encodings.append(encodings[0])
        face_label.config(text=f"✔️ {len(known_encodings)} چهره انتخاب شد")

def select_video_file():
    global video_file_path
    video_file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    if video_file_path:
        video_label.config(text=f"✔️ ویدیو انتخاب شد: {os.path.basename(video_file_path)}")

def process_video():
    if not known_encodings or not video_file_path:
        messagebox.showerror("خطا", "لطفاً حداقل یک عکس چهره و یک ویدیو انتخاب کنید.")
        return

    output_dir = "output_frames"
    output_video_path = "output_detected_video.mp4"
    save_every_n_seconds = 5

    os.makedirs(output_dir, exist_ok=True)

    video_capture = cv2.VideoCapture(video_file_path)
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * save_every_n_seconds)
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (frame_width, frame_height))

    frame_index = 0
    saved_index = 0
    first_detected = False
    last_saved_frame = -frame_interval

    print("[INFO] شروع پردازش...")

    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        frame_index += 1
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        person_found = False
        for encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
            if True in matches:
                person_found = True
                break

        display_text = "[FOUND]" if person_found else "[NOT FOUND]"
        color = (0, 255, 0) if person_found else (0, 0, 255)
        cv2.putText(frame, display_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        if person_found:
            if not first_detected:
                first_detected = True
                saved_index += 1
                filename = os.path.join(output_dir, "first_detection.jpg")
                cv2.imwrite(filename, frame)
                video_writer.write(frame)
                last_saved_frame = frame_index
                print(f"[✅] اولین حضور → {filename}")
            elif frame_index - last_saved_frame >= frame_interval:
                saved_index += 1
                filename = os.path.join(output_dir, f"detected_{saved_index:03d}.jpg")
                cv2.imwrite(filename, frame)
                video_writer.write(frame)
                last_saved_frame = frame_index
                print(f"[✔️] ذخیره فریم در {filename}")

        cv2.imshow("Live Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    video_writer.release()
    cv2.destroyAllWindows()
    messagebox.showinfo("پایان", f"✅ پردازش کامل شد.\n🎬 خروجی: {output_video_path}")

root = tk.Tk()
root.title("شناسایی چهره در ویدیو (چند چهره‌ای)")
root.geometry("500x300")

tk.Label(root, text="👤 انتخاب عکس‌های چهره (می‌توانید چند عکس انتخاب کنید):", font=("Arial", 12)).pack(pady=5)
tk.Button(root, text="انتخاب عکس‌ها", command=select_face_images).pack()
face_label = tk.Label(root, text="هیچ عکسی انتخاب نشده", fg="red")
face_label.pack()

tk.Label(root, text="🎞️ انتخاب فایل ویدیویی:", font=("Arial", 12)).pack(pady=10)
tk.Button(root, text="انتخاب ویدیو", command=select_video_file).pack()
video_label = tk.Label(root, text="هیچ ویدیویی انتخاب نشده", fg="red")
video_label.pack()

tk.Button(root, text="▶️ شروع پردازش", bg="green", fg="white", font=("Arial", 14), command=process_video).pack(pady=20)

root.mainloop()
