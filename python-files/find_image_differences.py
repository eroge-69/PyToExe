import cv2
import numpy as np
from tkinter import filedialog, Tk

def select_image():
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
    return file_path

def find_and_highlight_differences(image_path1, image_path2):
    # Load images
    img1 = cv2.imread(image_path1)
    img2 = cv2.imread(image_path2)

    # Check if images are loaded successfully
    if img1 is None or img2 is None:
        print("Error: One of the images could not be loaded.")
        return

    # Check if images have the same dimensions
    if img1.shape != img2.shape:
        print("Error: Images have different dimensions.")
        return

    # Convert images to grayscale
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Compute the absolute difference between images
    diff = cv2.absdiff(gray1, gray2)

    # Apply threshold to detect smaller differences
    _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

    # Find contours of differences
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create a copy of the first image to draw rectangles
    result_img = img1.copy()

    # Draw rectangles around significant differences
    for contour in contours:
        if cv2.contourArea(contour) > 100:  # Reduced to detect smaller differences
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(result_img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    # Display images
    cv2.imshow('First Image', img1)
    cv2.imshow('Second Image', img2)
    cv2.imshow('Differences Highlighted', result_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Save the result image
    cv2.imwrite('differences_highlighted.png', result_img)
    print("Result image with highlighted differences saved as: differences_highlighted.png")

def main():
    print("Please select the first image:")
    image_path1 = select_image()
    print("Please select the second image:")
    image_path2 = select_image()

    if image_path1 and image_path2:
        find_and_highlight_differences(image_path1, image_path2)
    else:
        print("Error: One of the images was not selected.")

if __name__ == "__main__":
    main()