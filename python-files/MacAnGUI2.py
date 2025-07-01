import cv2
import numpy as np
from sklearn.cluster import DBSCAN
import PySimpleGUI as sg
import sys
import os
from datetime import datetime

points = []
drawing = False
length = 0
pixelDim = 0
sections = 0
scalePercent = 20
# Custom print function that writes to GUI output
def gui_print(*args, window=None, end="\n", sep=" "):
    """Simplified print function that works better with PySimpleGUI event loop"""
    text = sep.join(str(arg) for arg in args) + end
    print(text, end="")  # Console output
    
    if window:
        try:
            # Directly update the output element
            output_element = window['-OUTPUT-']
            current = output_element.get()
            output_element.update(current + text)
            window.refresh()  # Force immediate update
        except Exception as e:
            print(f"GUI Update Error: {e}")

def draw_line(event, x, y, flags, param):
    global points, drawing, length, xi, yi, window
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        cv2.imshow("Image", img_scaled)
        points = [(x, y)]
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img_scaled.copy()
            cv2.line(img_copy, points[0], (x, y), (100,200,50), 3)
            cv2.imshow("Image", img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        points.append((x, y))

        #Snaps the line to an axis if the angle is less than 10 degrees (0.1744 radians)
        gui_print(points, window=window)
        dx, dy = np.array(points[1]) - np.array(points[0])
        angleRadiansVert = np.arcsin(np.abs(dx) / np.linalg.norm([dx, dy]))
        angleRadiansHor = np.arcsin(np.abs(dy) / np.linalg.norm([dx, dy]))
        angleToSnap = 0.1744
        gui_print("Radians from Horizontal: ", angleRadiansHor, "Radians from Vertical: ", angleRadiansVert, window=window)
        if angleRadiansVert < angleToSnap:
            points[1] = (points[0][0], points[1][1])
        elif angleRadiansHor < angleToSnap:
            points[1] = (points[1][0], points[0][1]) 
        gui_print(points, window=window)
        
        cv2.line(img_scaled, points[0], points[1], (100, 255, 0), 5)
        cv2.imshow("Image", img_scaled)
        length =  np.linalg.norm((100 / scalePercent) * np.array(points[1]) - (100 / scalePercent) * np.array(points[0]))
        gui_print(f"\nLine Length: {length:.2f} pixels", window=window)

pointsRectangleReal = []
pointsRectangleScaled = []
def crop_image(event, x, y, flags, param):
    global pointsRectangleReal, pointsRectangleScaled, drawing, length, window

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        full_x = int(100 / scalePercent * x)
        full_y = int((100 / scalePercent) * y)
        pointsRectangleReal = [(full_x, full_y)]
        pointsRectangleScaled = [(x, y)]
        
        img_copy = img_scaled.copy()
        cv2.rectangle(img_copy, (x,y), (x,y), (0,255,0), 2)
        cv2.imshow("Image", img_copy)
        
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing and pointsRectangleScaled:
            img_copy = img_scaled.copy()
            # Draw rectangle from start point to current (scaled) position
            cv2.rectangle(img_copy, pointsRectangleScaled[0], (x,y), (0,255,0), 2)
            cv2.imshow("Image", img_copy)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        full_x = int(x * (100 / scalePercent))
        full_y = int(y * (100 / scalePercent))
        pointsRectangleReal.append((full_x, full_y))
        
        sectionsOfImage = []
        for i in range(sections):
            croppedImagei = full_size_image[pointsRectangleReal[0][1] + (i * 10 * round(pixelDim)):(pointsRectangleReal[0][1] + ((i + 1) * 10 * round(pixelDim))), pointsRectangleReal[0][0]:pointsRectangleReal[1][0]]
            sectionsOfImage.append(croppedImagei)
        
        #Output each section of the image
        for i, image in enumerate(sectionsOfImage):
            processed_image = image.copy()  # Keep original intact
            processed_image= process_image(processed_image, window=window)  # Draw contours/circles at full resolution
            # Scale down ONLY for display
            scale_percent = 20  # Display at 20% size
            width = int(processed_image.shape[1] * scale_percent / 100)
            height = int(processed_image.shape[0] * scale_percent / 100)
            dim = (width, height)
            display_image = cv2.resize(processed_image, dim, interpolation=cv2.INTER_AREA)
            
            # Show the scaled-down result
            cv2.destroyWindow("Image")
            cv2.imshow(f"Section {i} (Scaled Down)", display_image)
            gui_print("guh")
        
           

def process_image(image, window=None):
    #blur this image
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX, dtype = cv2.CV_8U)
    threshold_value = 105  # Adjust this (0-255)
    max_value = 255       # White value
    #change back to binary threhsolding original with thresholds
    _, binary_img = cv2.threshold(image, threshold_value, max_value, type=cv2.THRESH_BINARY)
    edges = cv2.Canny(binary_img, 90, 110)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    contours, _ = cv2.findContours(closed_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pixelDim_mm = pixelDim / 10
    if len(image.shape) == 2:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    circles = []
    for cnt in contours:
        if len(cnt) >= 7:  # Need at least 5 points to fit ellipse
            # Get minimum enclosing circle
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            center = (int(x), int(y))
            radius = int(radius)
            if 2 * radius < pixelDim_mm:
                continue
            circles.append((x, y, radius))
    cv2.drawContours(image, contours, -1, (255, 100, 0), 3)

            
    aggregrated_circles = aggregate_circles(circles, 1, pixelDim / 10)

    small = 0
    medium = 0
    large = 0
    for (x, y, r) in aggregrated_circles:
        
        pixelDim_mm = pixelDim / 10
        d = r * 2 / pixelDim_mm
        if (1 < d < 3):
            cv2.circle(image, (x,y), r, (255, 0, 0), 3)
            small += 1
        if (3 < d < 5):
            cv2.circle(image, (x,y), r, (0, 255, 0), 3)
            medium += 1
        if (d > 5):
            cv2.circle(image, (x,y), r, (0, 0, 255), 3)
            large += 1
    cat = calculate_category(small, medium, large)
    output_text = f"\nSmall: {small}, Medium: {medium}, Large: {large}, Category: {cat}"
        
    if window:
        # Use the simplified gui_print
        gui_print(output_text, window=window)
    else:
        print(output_text)
    return image

def min_contour_distance(contour1, contour2):
    minDist = float('inf')
    for point in contour1[:, 0]:
        dist = abs(cv2.pointPolygonTest(contour2, tuple(point), True))
        if dist < minDist:
            dist = minDist
    return minDist

def aggregate_circles(circles, min_distance_mm, pixels_per_mm):
    """
    Combine nearby circles into larger circles.
    
    Args:
        circles: List of circles in format [(x1,y1,r1), (x2,y2,r2), ...]
        min_distance_mm: Minimum distance threshold in mm (e.g., 1mm)
        pixels_per_mm: Conversion factor from pixels to mm
    
    Returns:
        List of aggregated circles
    """
    if len(circles) == 0:
        return []
    
    # Convert min distance to pixels
    min_distance_px = min_distance_mm * pixels_per_mm
    
    # Prepare data for clustering (just centers, ignore radii)
    centers = np.array([(x, y) for (x, y, r) in circles])
    
    # Use DBSCAN to cluster nearby centers
    clustering = DBSCAN(eps=min_distance_px, min_samples=1).fit(centers)
    labels = clustering.labels_
    
    aggregated_circles = []
    
    # For each cluster
    for label in set(labels):
        if label == -1:
            continue  # noise points (shouldn't happen with min_samples=1)
        
        # Get all circles in this cluster
        cluster_circles = [circles[i] for i in range(len(circles)) if labels[i] == label]
        
        # Calculate new center as mean of all centers
        mean_x = np.mean([x for (x, y, r) in cluster_circles])
        mean_y = np.mean([y for (x, y, r) in cluster_circles])
        
        # Calculate new radius to encompass all circles
        max_radius = 0
        for (x, y, r) in cluster_circles:
            # Distance from new center to this circle's edge
            dist_to_edge = np.sqrt((x - mean_x)**2 + (y - mean_y)**2) + r
            if dist_to_edge > max_radius:
                max_radius = dist_to_edge
        
        aggregated_circles.append((int(mean_x), int(mean_y), int(max_radius)))
    
    return aggregated_circles

def calculate_category(s, m, l):
    #calculates mannesmann category based on spectra energy inc scale
    if (s <= 10) and (m == 0 and l == 0):
        return 1
    elif (s + m < 18) and (m < 5):
        return 2
    elif (s + m + l >= 19) or (l >= 1) or (m >= 6):
        return 3
    else:
        return 4

def load_image(input_file):
    macro = cv2.imread(input_file, 0)
    if macro is None:
        gui_print("Error: Macro not found.", window=window)
    else:
        scale_percent = scalePercent # Percentage of original size
        width = int(macro.shape[1] * scale_percent / 100)
        height = int(macro.shape[0] * scale_percent / 100)
        dim = (width, height)
        img_scaled = cv2.resize(macro, dim, interpolation=cv2.INTER_AREA)
        return img_scaled, macro

def find_newest_file(directory, window=None):
    newest_file = None
    newest_time = None  # Will store as datetime
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if window:  # Only print if window is provided
                gui_print(" . ", window=window)
            file_path = os.path.join(root, file)
            mod_time_seconds = os.path.getmtime(file_path)
            
            # Convert timestamp to datetime
            mod_time = datetime.fromtimestamp(mod_time_seconds)
            
            if newest_time is None or mod_time > newest_time:
                newest_time = mod_time
                newest_file = file_path
                
    return newest_file, newest_time

sg.theme('LightBlue2')

# Define the layout
layout = [
    [sg.Button("Load Image Automatically"),sg.Button("Browse For Macro"), sg.Button("Line Drawing"), sg.Button("Crop")],
    [sg.Text("Output:", font=('Helvetica', 10, 'bold'))],
    [sg.Multiline("", 
                 key='-OUTPUT-', 
                 size=(45, 5), 
                 autoscroll=True,
                 disabled=True,  # Makes it read-only
                 background_color='white',
                 text_color='black')],
    [sg.Button("Clear Output"), sg.Button("Exit")]
]

# Create the window
window = sg.Window("MacroAnalyzer", layout)
img_scaled = None
full_size_image = None
# Event loop
while True:
    event, values = window.read()
    
    # Exit if window is closed or Exit button pressed
    if event == sg.WINDOW_CLOSED or event == "Exit":
        cv2.destroyAllWindows()
        window.close()
        sys.exit()
        break
        
    # Handle print events from process_image
    if event == '-PRINT-':
        gui_print(values[event], window=window)
        
    # Handle button events
    if event == "Crop":
        if img_scaled is None:
            gui_print("Please load an image first!", window=window)
            continue
        
        output_text = "Draw the box around the centerline at the top of the macro\n"
        window['-OUTPUT-'].update(output_text + window['-OUTPUT-'].get(), append=True)
        
        # Create main window if it doesn't exist
        if cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
            cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
            cv2.imshow("Image", img_scaled)
            
        cv2.setMouseCallback("Image", crop_image)
        
        try:
            while True:
                key = cv2.waitKey(1) & 0xFF
                # Exit on ESC or if window closed
                if key == 27 or cv2.getWindowProperty("Image", cv2.WND_PROP_VISIBLE) < 1:
                    break
                    
                # Allow PySimpleGUI to process events
                window.read(timeout=10)
            
        finally:
            # Cleanup all OpenCV windows
            cv2.destroyAllWindows()
            cv2.waitKey(1)  # Ensure windows close
            
    elif event == "Line Drawing":
        if img_scaled is None:
            gui_print("Please load an image first!", window=window)
            continue
        output_text = "Draw a line between two measurement marks\n"
        window['-OUTPUT-'].update(output_text + window['-OUTPUT-'].get(), append=True)
        cv2.imshow("Image", img_scaled)
        cv2.setMouseCallback("Image", draw_line)
        cv2.waitKey(0)
        realLength = float(sg.popup_get_text("How many centimeters was the line you drew?"))
        pixelDim = float(length) / float(realLength)
        sections = 2  
        
    elif event == "Load Image Automatically":
        try:
            current_year = datetime.now().year
            macros_path = f"S:\L2 Warehouse\ProcessImages\Macros\{current_year}"
            macro_input, macro_upload_time = find_newest_file(macros_path, window = window)
            if macro_input is not None:
                gui_print(f"\nSuccessfully grabbed macro, uploaded at {macro_upload_time}", window = window)
                img_scaled, full_size_image = load_image(macro_input)
        except Exception as e:
            print(f"There was an exception: {e}")
        #macro_input = sg.popup_get_text("Load in a slab macro! (Make sure this program is in the same directory as the image)")
    
    elif event == "Browse For Macro":
        macro_input = sg.popup_get_text("Load in a slab macro! (Please include the full directory)")
        img_scaled = load_image(macro_input)
        if img_scaled is not None:
            output_text = f"\n{macro_input} loaded succesfully!"
            window['-OUTPUT-'].update(output_text + window['-OUTPUT-'].get(), append=True)
        else:
            gui_print("Macro not found", window = window)
            continue
    
    elif event == "Clear Output":
        window['-OUTPUT-'].update("")
        
# Close the window
cv2.destroyAllWindows()
sys.exit()
window.close()