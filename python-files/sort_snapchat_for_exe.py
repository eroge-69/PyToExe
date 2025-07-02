
import os
import shutil

def sort_snapchat_media():
    folder = r"C:\Users\DeskTop\Desktop\phone backup\Snapchat"

    images_folder = os.path.join(folder, "Snapchat Images")
    videos_folder = os.path.join(folder, "Snapchat Videos")

    os.makedirs(images_folder, exist_ok=True)
    os.makedirs(videos_folder, exist_ok=True)

    image_exts = ('.jpg', '.jpeg', '.png', '.heic', '.webp')
    video_exts = ('.mp4', '.mov', '.avi', '.mkv')

    files = os.listdir(folder)
    image_count = 0
    video_count = 0

    for f in files:
        file_path = os.path.join(folder, f)
        if os.path.isfile(file_path):
            if f.lower().endswith(image_exts):
                shutil.move(file_path, os.path.join(images_folder, f))
                image_count += 1
            elif f.lower().endswith(video_exts):
                shutil.move(file_path, os.path.join(videos_folder, f))
                video_count += 1

    print(f"✅ Done! {image_count} images and {video_count} videos moved successfully.")
    input("Press Enter to exit...")

if __name__ == "__main__":
    sort_snapchat_media()
