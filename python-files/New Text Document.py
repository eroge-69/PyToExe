import os
from PIL import Image, ImageDraw

# --- 1. Pixel Checking and Mode Determination Functions ---
def get_pixel_color(image_path, x, y):
    """Gets the RGB color of a pixel at the given x, y coordinates."""
    try:
        with Image.open(image_path) as img:
            pixel = img.getpixel((x, y))
        if isinstance(pixel, int):
             return (pixel, pixel, pixel)
        if len(pixel) == 4:
            return pixel[:3]
        return pixel
    except FileNotFoundError:
        print(f"Error: Image not found at {image_path}")
        return None
    except IndexError:
        print(f"Error: Coordinates ({x}, {y}) are out of bounds for the image {os.path.basename(image_path)}.")
        return None
    except Exception as e:
        print(f"An error occurred while getting pixel color for {os.path.basename(image_path)}: {e}")
        return None

def check_pixel(image_path, x, y, expected_rgb):
    """Checks if the pixel at (x, y) matches the expected RGB color."""
    actual_rgb = get_pixel_color(image_path, x, y)
    if actual_rgb:
        return actual_rgb == expected_rgb
    return False

def determine_mode(image_path):
    """
    Determines the mode based on pixel colors in the image.
    Left/Right error treatment modes are now classified as 'unknown mode'.
    """
    # MPC Mode Check
    # 1. x y 835 66, rgb 153 153 153
    # 2. x y 2867 19, rgb 90 125 164
    mpc_check_1 = check_pixel(image_path, 835, 66, (153, 153, 153))
    mpc_check_2 = check_pixel(image_path, 2867, 19, (90, 125, 164))

    if mpc_check_1 and mpc_check_2:
        return "mpc mode"

    # Treatment Mode Check (if not MPC mode)
    # 1. x y 243 37, rgb 29 62 109
    # 2. x y 1625 191, rgb 255 128 0
    treatment_check_1 = check_pixel(image_path, 243, 37, (29, 62, 109))
    treatment_check_2 = check_pixel(image_path, 1625, 191, (255, 128, 0))

    if treatment_check_1 and treatment_check_2:
        # Left Error Check (now treated as unknown)
        # 1. x y 574 439, rgb 212 208 200
        # 2. x y 1339 348, rgb 212 208 200
        left_error_check_1 = check_pixel(image_path, 574, 439, (212, 208, 200))
        left_error_check_2 = check_pixel(image_path, 1339, 348, (212, 208, 200))
        if left_error_check_1 and left_error_check_2:
            print(f"Info: Left error condition detected for {os.path.basename(image_path)}. Treating as 'unknown mode'.")
            return "unknown mode" # CHANGED: Treat as unknown

        # Right Error Check (now treated as unknown)
        # 1. x y 2459 280, rgb 206 0 0
        # 2. x y 3048 851, rgb 240 240 240
        right_error_check_1 = check_pixel(image_path, 2459, 280, (206, 0, 0))
        right_error_check_2 = check_pixel(image_path, 3048, 851, (240, 240, 240))
        if right_error_check_1 and right_error_check_2:
            print(f"Info: Right error condition detected for {os.path.basename(image_path)}. Treating as 'unknown mode'.")
            return "unknown mode" # CHANGED: Treat as unknown

        return "standard treatment mode" # This is the only "treatment" mode that gets processed

    return "unknown mode" # Default mode

# --- 2. Rectangle Definitions for Each Mode ---
RECTANGLES_CONFIG = {
    "mpc mode": [
        (499, 25, 874, 60),
        (927, 30, 1469, 432)
    ],
    "standard treatment mode": [ # Only this treatment mode will use rectangles
        (0, 67, 477, 243),
        (699, 10, 856, 30),
        (922, 33, 1467, 442),
        (2339, 43, 3837, 1035)
    ]
    # "left error treatment mode" and "right error treatment mode" are no longer needed here
    # as they are handled as "unknown mode".
}

# --- 3. Core Image Processing Function ---
def redact_image_and_move(image_path, new_output_filename, rectangles_to_apply, mode_name, redacted_base_dir):
    """Applies white rectangles to an image, saves it to redacted folder with new name, and deletes original."""
    redacted_path = os.path.join(redacted_base_dir, new_output_filename)
    original_basename = os.path.basename(image_path)

    try:
        with Image.open(image_path) as img:
            draw = ImageDraw.Draw(img)
            for rect in rectangles_to_apply:
                draw.rectangle(rect, fill="white")
            img.save(redacted_path)
        print(f"Redacted ({mode_name}): Original '{original_basename}' saved as '{new_output_filename}' in '{redacted_base_dir}'.")

        os.remove(image_path)
        print(f"Deleted original: {original_basename}")
        return True

    except FileNotFoundError:
        print(f"Error: Original image not found for redaction: {original_basename}")
    except Exception as e:
        print(f"Error processing original '{original_basename}' (saving as '{new_output_filename}') for {mode_name}: {e}")
    return False

# --- 4. Main Script Logic ---
def main_processing_loop():
    """
    Determines mode for each image in the current directory and processes accordingly.
    """
    input_directory = os.getcwd()
    redacted_directory = os.path.join(input_directory, "redacted")

    if not os.path.exists(redacted_directory):
        print(f"'redacted' folder does not exist. Creating it at: {redacted_directory}")
        try:
            os.makedirs(redacted_directory)
            print(f"'redacted' folder created successfully.")
        except OSError as e:
            print(f"Error: Could not create 'redacted' folder: {e}. Please create it manually and re-run.")
            return

    # Counters for summary
    total_files_encountered = 0
    successfully_processed_mpc_count = 0
    successfully_processed_treatment_count = 0
    # Unknown count will be derived at the end

    print(f"\nStarting image processing in directory: {input_directory}")
    for filename in os.listdir(input_directory):
        if filename.lower().endswith((".png", ".jpg", ".jpeg")):
            total_files_encountered += 1
            image_path = os.path.join(input_directory, filename)

            print(f"\nProcessing file: {filename}")
            current_mode = determine_mode(image_path)
            # The determine_mode function might print info about error conditions being treated as unknown.
            print(f"Effective mode for processing: {current_mode}")


            if current_mode == "mpc mode":
                rectangles_for_mode = RECTANGLES_CONFIG[current_mode]
                prefix = "mpc_"
                new_filename = prefix + filename
                if redact_image_and_move(image_path, new_filename, rectangles_for_mode, current_mode, redacted_directory):
                    successfully_processed_mpc_count += 1
            elif current_mode == "standard treatment mode": # Only "standard treatment mode" is processed
                rectangles_for_mode = RECTANGLES_CONFIG[current_mode]
                prefix = "treatment_"
                new_filename = prefix + filename
                if redact_image_and_move(image_path, new_filename, rectangles_for_mode, current_mode, redacted_directory):
                    successfully_processed_treatment_count += 1
            elif current_mode == "unknown mode":
                print(f"Image '{filename}' classified as 'unknown mode'. File will not be redacted or moved.")
                # Original file remains in place.
            else:
                # This case should ideally not be reached if determine_mode is comprehensive
                print(f"Warning: Mode '{current_mode}' for '{filename}' is unexpected. Treating as unknown. File will not be redacted or moved.")

        elif os.path.isdir(os.path.join(input_directory, filename)) and filename == "redacted":
            pass
        elif os.path.isdir(os.path.join(input_directory, filename)):
            print(f"Skipping directory: {filename}")


    print("\n--- Image Redaction Summary ---")
    total_unknown_skipped_failed_count = total_files_encountered - successfully_processed_mpc_count - successfully_processed_treatment_count

    print(f"Total image files encountered: {total_files_encountered}")
    print(f"Total MPC files processed successfully: {successfully_processed_mpc_count}")
    print(f"Total Treatment (Standard) files processed successfully: {successfully_processed_treatment_count}")
    print(f"Total Unknown/Skipped/Failed files: {total_unknown_skipped_failed_count}")
    print("Image processing complete.")

    # Add pause at the end
    input("\nPress Enter to close the window...") # MODIFICATION HERE


if __name__ == "__main__":
    main_processing_loop()
