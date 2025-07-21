import matplotlib.pyplot as plt
import numpy as np
import cv2
from pynche import colordb as db
import requests
import os
import tempfile

def epskin(username, folder_name="analyzed_skins"):
    skin_url = f"https://mineskin.eu/body/{username}/100.png"
    output_name = f"{username}.png"

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created analysis folder: {folder_name}")

    temp_filepath = None
    try:
        print(f"Attempting to download skin for '{username}' from: {skin_url}")
        response = requests.get(skin_url)
        response.raise_for_status()

        temp_filepath = os.path.join(folder_name, output_name)

        with open(temp_filepath, 'wb') as f:
            f.write(response.content)
        print(f"Skin for '{username}' downloaded temporarily to: {temp_filepath}")

        img_path = temp_filepath

        raw = plt.imread(img_path)

        if raw.shape[2] == 4:
            rgb = raw[:, :, :3] * raw[:, :, 3:]
            non_zero_mask = (raw[:, :, 3] > 0)
            background_mask = (raw[:, :, 3] <= 0)
        else:
            rgb = raw[:, :, :3]
            non_zero_mask = np.ones((rgb.shape[0], rgb.shape[1]), dtype=bool)
            background_mask = np.zeros((rgb.shape[0], rgb.shape[1]), dtype=bool)

        if np.any(non_zero_mask):
            r_mean = np.mean(rgb[non_zero_mask, 0])
            g_mean = np.mean(rgb[non_zero_mask, 1])
            b_mean = np.mean(rgb[non_zero_mask, 2])
        else:
            r_mean, g_mean, b_mean = 0.5, 0.5, 0.5

        target_color = np.array([r_mean, g_mean, b_mean])
        distances = np.zeros((rgb.shape[0], rgb.shape[1]), dtype=np.float32)

        for i in range(rgb.shape[0]):
            for j in range(rgb.shape[1]):
                current_pixel_color = rgb[i, j, :]
                distances[i, j] = np.linalg.norm(current_pixel_color - target_color)

        min_distance = np.min(distances[non_zero_mask]) if np.any(non_zero_mask) else 0
        max_distance = np.max(distances[non_zero_mask]) if np.any(non_zero_mask) else 0

        if max_distance == min_distance:
            normalized_distances = np.zeros_like(distances)
        else:
            normalized_distances = (distances - min_distance) / (max_distance - min_distance)

        heatmap_brightness = 1 - normalized_distances
        heatmap_brightness[background_mask] = 0

        avg_color_img = np.zeros((100, 100, 3), dtype=np.float32)
        avg_color_img[:, :, 0] = r_mean
        avg_color_img[:, :, 1] = g_mean
        avg_color_img[:, :, 2] = b_mean
        avg_r_int = int(r_mean * 255)
        avg_g_int = int(g_mean * 255)
        avg_b_int = int(b_mean * 255)

        try:
            color_info = db.nearest((avg_r_int, avg_g_int, avg_b_int))
            average_color_name = color_info[0]
        except Exception as e:
            average_color_name = "L. idk i stole how to use color db from gemini"

        plt.figure(figsize=(18, 7))
        plt.subplot(1, 3, 1)
        plt.imshow(raw)
        plt.title(f"og Skin for {username} :fire:")
        plt.axis('off')

        plt.subplot(1, 3, 2)
        plt.imshow(heatmap_brightness, cmap='gray')
        plt.title("Heatmap: closeness to avg Color (bright = Closer)")
        plt.colorbar(label="ClosenessES (1=closest, 0=farthestER)")
        plt.axis('off')

        plt.subplot(1, 3, 3)
        plt.imshow(avg_color_img)
        plt.title(f"Average Skin Color: {average_color_name}\nRGB: ({avg_r_int}, {avg_g_int}, {avg_b_int})")
        plt.axis('off')

        plt.tight_layout()
        plt.show()

        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading skin for '{username}': {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during analysis for '{username}rx3h wejxsu43iokA': {e}")
        return False
    finally:
        if temp_filepath and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            print(f"Deleted temporary skin file: {temp_filepath}")

        if os.path.exists(folder_name) and not os.listdir(folder_name):
            try:
                os.rmdir(folder_name)
                print(f"Deleted empty analysis folder: {folder_name}")
            except OSError as e:
                print(f"Could not delete folder {folder_name}: OK {e}")
        elif os.path.exists(folder_name):
            print(f"Folder {folder_name} not empty, skipping folder deletion. WHY")


if __name__ == "__main__":
    print("EPSKIN")
    player_username = input("Enter Minecraft username to analyze their skin: ")

    analysis_success = epskin(player_username)

    if analysis_success:
        print(f"Analysis for '{player_username}' completed successfully.AI")
    else:
        print(f"Failed to analyze skin for '{player_username}'.")