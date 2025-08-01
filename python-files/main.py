# import cv2
# import os
# import face_recognition

# def crop_faces_from_images(input_folder, output_folder):
#     # Buat folder output jika belum ada
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)

#     # Dapatkan daftar file gambar dari folder input
#     for filename in os.listdir(input_folder):
#         if filename.endswith(('.jpg', '.jpeg', '.png')):
#             # Path lengkap untuk gambar
#             image_path = os.path.join(input_folder, filename)
#             # Load gambar
#             image = face_recognition.load_image_file(image_path)
#             # Temukan lokasi wajah
#             face_locations = face_recognition.face_locations(image)

#             # Proses setiap wajah yang ditemukan
#             for i, face_location in enumerate(face_locations):
#                 top, right, bottom, left = face_location
#                 # Crop wajah
#                 face_image = image[top:bottom, left:right]
                
#                 # Simpan wajah yang telah dipotong
#                 cropped_filename = f"{os.path.splitext(filename)[0]}_face{i+1}.jpg"
#                 output_path = os.path.join(output_folder, cropped_filename)
#                 cv2.imwrite(output_path, face_image)

#                 print(f"Saved cropped face to {output_path}")

# if __name__ == "__main__":
#     input_folder = './bahan/'
#     output_folder = '/foto-cropped/'
#     crop_faces_from_images(input_folder, output_folder)


# import face_recognition
# import cv2
# import os

# # Folder input tempat ribuan gambar
# input_folder = './bahan/'
# # Folder output untuk menyimpan gambar wajah hasil crop
# output_folder = './foto-cropped/'

# # Pastikan folder output ada
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# # Fungsi untuk mendeteksi dan crop wajah
# def crop_faces_from_image(image_path, output_folder, image_name):
#     # Load gambar
#     image = face_recognition.load_image_file(image_path)
#     # Deteksi lokasi wajah
#     face_locations = face_recognition.face_locations(image)

#     # Jika ada wajah yang terdeteksi
#     if face_locations:
#         for i, face_location in enumerate(face_locations):
#             top, right, bottom, left = face_location
#             # Crop wajah
#             face_image = image[top:bottom, left:right]
#             # Convert dari RGB (digunakan face_recognition) ke BGR (digunakan OpenCV)
#             face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
#             # Simpan wajah hasil crop
#             face_filename = os.path.join(output_folder, f"{image_name}_face_{i+1}.jpg")
#             cv2.imwrite(face_filename, face_image_bgr)

# # Proses semua gambar di folder input
# for image_file in os.listdir(input_folder):
#     # Cek apakah file tersebut gambar
#     if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
#         image_path = os.path.join(input_folder, image_file)
#         image_name = os.path.splitext(image_file)[0]
#         crop_faces_from_image(image_path, output_folder, image_name)

# print("Proses cropping wajah selesai.")


import face_recognition
import cv2
import os

# Folder input tempat ribuan gambar
input_folder = './bahan/'
# Folder output untuk menyimpan gambar wajah hasil crop
output_folder = './foto-croped-padding/'


# Pastikan folder output ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Padding umum (kiri, kanan, bawah)
padding_sides = 35  # Padding standar
# Padding lebih besar untuk bagian atas
padding_top = 50  # Padding lebih besar untuk bagian atas

# Fungsi untuk mendeteksi dan crop wajah dengan jarak
def crop_faces_from_image(image_path, output_folder, image_name):
    # Load gambar
    image = face_recognition.load_image_file(image_path)
    # Deteksi lokasi wajah
    face_locations = face_recognition.face_locations(image)
    image_height, image_width = image.shape[:2]  # Ukuran gambar asli

    # Jika ada wajah yang terdeteksi
    if face_locations:
        for i, face_location in enumerate(face_locations):
            top, right, bottom, left = face_location

            # Tambahkan padding dengan lebih ke atas
            top = max(0, top - padding_top)  # Lebih besar ke atas
            right = min(image_width, right + padding_sides)
            bottom = min(image_height, bottom + padding_sides)
            left = max(0, left - padding_sides)

            # Crop wajah dengan padding
            face_image = image[top:bottom, left:right]
            # Convert dari RGB (digunakan face_recognition) ke BGR (digunakan OpenCV)
            face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)

            # Jika lebih dari satu wajah, tambahkan nomor indeks
            if len(face_locations) > 1:
                face_filename = os.path.join(output_folder, f"{image_name}_face_{i+1}.jpg")
            else:
                face_filename = os.path.join(output_folder, f"{image_name}.jpg")

            # Simpan wajah hasil crop dengan padding
            cv2.imwrite(face_filename, face_image_bgr)

# Proses semua gambar di folder input
for image_file in os.listdir(input_folder):
    # Cek apakah file tersebut gambar
    if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_path = os.path.join(input_folder, image_file)
        image_name = os.path.splitext(image_file)[0]
        crop_faces_from_image(image_path, output_folder, image_name)

print("Proses cropping wajah selesai dengan jarak, lebih banyak ke atas.")