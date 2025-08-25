
import os
import subprocess

def resize_and_compress_video(input_path, output_path, target_resolution="1280x720", target_bitrate="3000k"):
    """
    Reduce la resolución de un video MP4 y ajusta el bitrate usando ffmpeg.

    Parámetros:
    - input_path: ruta del archivo de video original
    - output_path: ruta donde se guardará el video procesado
    - target_resolution: resolución deseada (por defecto 1280x720)
    - target_bitrate: bitrate deseado (por defecto 3000k)
    """
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vf", f"scale={target_resolution}",
        "-b:v", target_bitrate,
        "-c:v", "libx265",
        "-c:a", "aac",
        output_path
    ]

    subprocess.run(command)

# Ejemplo de uso:
# resize_and_compress_video("video_original.mp4", "video_reducido.mp4")
