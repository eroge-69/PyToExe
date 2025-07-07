import cv2
import numpy as np
import json
import os
import tkinter as tk
from tkinter import filedialog

#for json
data_for_image = []

# Prompt user to select folder at program start
def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Root Folder with Images")
    if folder:
        print("Selected folder:", folder)
    else:
        print("No folder selected. Exiting.")
        exit()
    return folder

# Folder containing images
images_folder = select_folder()
#images_folder = "/home/petra/Documents/APNG/ann_images/originals"
image_files = sorted([f for f in os.listdir(images_folder) if f.lower().endswith(('.bmp', '.jpg', '.jpeg', '.png'))])

parent_dir = os.path.dirname(images_folder)
# Specify your output folder
output_folder = os.path.join(parent_dir, 'annotated')
output_folder_json = os.path.join(parent_dir, 'annotated_json')

os.makedirs(output_folder, exist_ok=True)
os.makedirs(output_folder_json, exist_ok=True)

# Ensure folder exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

if not os.path.exists(output_folder_json):
    os.makedirs(output_folder_json)

# State variables
def reset_state():
    global current_points, boxes, drawing, head_mode, current_box_idx, current_side_index, assigned_head, current_cow_id, cow_id, image_ok, exit, img_display

    current_points = []
    boxes = []  # Each: {'points': ..., 'box': ..., 'head_side': None}
    drawing = False
    head_mode = False
    current_box_idx = None
    current_side_index = 0
    assigned_head = False
    current_cow_id = None
    cow_id = False
    image_ok = True
    exit = False

# Colors for sides
side_colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
highlight_color = (0, 255, 255)  # yellow

def annotate_box_with_label(img, box_pts, label):
    # Compute centroid inside box for label placement
    M = cv2.moments(box_pts)
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
    else:
        # fallback: use the top-left vertex
        cX, cY = box_pts[0][0], box_pts[0][1]
    
    # Draw label text
    cv2.putText(img, label, (cX - 20, cY), cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (255, 255, 255), 1, cv2.LINE_AA, bottomLeftOrigin=False)
    cv2.imshow(image_filename, img)

def mouse_callback(event, x, y, flags, param):
    global current_points, img_display
    if event == cv2.EVENT_LBUTTONDOWN and drawing:
        current_points.append((x, y))
        cv2.circle(img_display, (x, y), 3, (0, 255, 0), -1)
        cv2.imshow(image_filename, img_display)

def draw_box_with_sides(box_pts, highlight_side=None):
    # Draw box
    cv2.drawContours(img_display, [box_pts], 0, (0,0,255), 2)
    # Draw sides in different colors
    for i in range(4):
        pt1 = box_pts[i]
        pt2 = box_pts[(i+1)%4]
        color = side_colors[i]
        if highlight_side == i:
            color = (0, 0, 255)  # red for the selected side
        else:
            color = (0, 255, 0)    # green for the others
        cv2.line(img_display, tuple(pt1), tuple(pt2), color, 2)


def start_head_selection(box_idx):
    global head_mode, current_side_index, current_box_idx
    head_mode = True
    current_side_index = 0
    current_box_idx = box_idx
    box_pts = boxes[box_idx]['box']
    draw_box_with_sides(box_pts, highlight_side=current_side_index)
    cv2.imshow(image_filename, img_display)
    print(f"Starting head orientation for box {box_idx+1}.")
    print("Press 'n' to cycle sides, 'y' to accept, 'Esc' to cancel.")

def assign_label(box_idx):
    global assigned_head
    assigned_head = True
    print("Assign label.\n 's': standing\n 'l': lying\n")


def print_help():
    print("Commands:")
    print("  'i' - image with insufficient information")
    print("  'a' - start a new selection")
    print("  'f' - finalize current selection and draw box")
    print("  'c' - save current image and go to the next (confirmation required)\n")
    print("  'q' - save and exit application")
    print("  'f' - finalize current selection and draw box")
    print("  'p' - delete last point")
    print("  'x' - delete last box")
    print("  'l' - delete last assigned label\n")
    #print("  'h' - start head orientation and label assignement for last box")
    print("Within head mode:")
    print("  'n' - cycle sides")
    print("  'y' - confirm selected side\n")
    print("  'Esc' - cancel head mode")
    print("  -------------------------------\n")


for image_filename in image_files:

    # Prepare annotation json filename: <name>_json.json
    name_without_ext = os.path.splitext(image_filename)[0]
    annotation_path = os.path.join(output_folder_json, f"{name_without_ext}_json.json")
    # Skip if annotation JSON already exists
    if os.path.exists(annotation_path):
        print(f"Skipping {name_without_ext} (already annotated).")
        continue

    # Initialize data for current image
    data_for_image = []
    image_path = os.path.join(images_folder, image_filename)

    # Load image
    img = cv2.imread(image_path)
    resized_img = cv2.resize(img, (640, 480))
    img_display = resized_img.copy()

    # Reset all annotation state variables for the new image:
    reset_state()

    cv2.imshow(image_filename, img_display)
    cv2.setMouseCallback(image_filename, mouse_callback)
    print_help()

    while True:
        key = cv2.waitKey(1) & 0xFF

        # Handle 'q' key to exit the app gracefully
        if key == ord('q'):
            print("Exiting the application.")
            print("Are you sure you want to exit? Current image will not be saved.\nPress 'y' to confirm, any other key to cancel.")
            confirm_key = cv2.waitKey(0) & 0xFF
            if confirm_key == ord('y'):
                exit = True
                break
            else:
                # Cancel exit, continue loop
                print("Continuing...")

        # Handle 'i' key for marking image as not okay
        if key == ord('i'):
            print("Image marked as not OK.\nPress 'c' to save and exit.")
            image_ok = False  # Update the flag
            # Fill JSON data with empty fields
            data_for_image.clear()
            json_entry = {
                "filename": image_filename,
                "image_ok": False,
                "boxes": []
            }
            data_for_image.append(json_entry)
            # Optionally, you might want to save or update your JSON file here
            continue  # Skip other processing, or proceed as needed


        if key == ord('c'):
            print("Are you sure you want to save this image? \nPress 'y' to confirm, any other key to cancel.")
            confirm_key = cv2.waitKey(0) & 0xFF
            if confirm_key == ord('y'):
                # Save image before exit
                base_name = os.path.basename(image_path)  # e.g., 'krave.bmp'
                name, ext = os.path.splitext(base_name)  # ('krave', '.bmp')
                save_name = f"{name}_labeled{ext}"      # 'krave_labeled.bmp
                save_path = os.path.join(output_folder, save_name)
                cv2.imwrite(save_path, img_display)
                print(f"Saved annotated image as '{save_name}'.")
                break
            else:
                # Cancel exit, continue loop
                print("Continuing...")

        elif key == ord('a'):
            # Start annotation mode
            current_points = []
            drawing = True
            print("New annotation. Click points.")

        elif key == ord('f'):
        # Finalize current shape and draw
            if len(current_points) >= 3:
                pts = np.array(current_points, dtype=np.float32)
                rect = cv2.minAreaRect(pts)
                box_pts = cv2.boxPoints(rect)
                box_pts = np.int32(box_pts)

                vertices = [list(map(float, pt)) for pt in box_pts]
                center_x = float(rect[0][0])
                center_y = float(rect[0][1])
                # Save box info
                box_info = {
                    'filename': image_filename,
                    'bbox_vertices': vertices,  # vertices of bounding box
                    'center': [center_x, center_y],  # center of bbox
                    'head_vertices': None,    # to be filled if head side selected
                    'head_orientation_angle': None,  # to be calculated
                    'label': None, # to be filled with 'standing' or 'lying'
                    'cow_id': None,
                    'image_ok' : image_ok
                }
                # Store in your per-image list
                data_for_image.append(box_info)


                boxes.append({'points': pts, 'box': box_pts, 'head_side': None, 'label': None, 'cow_id': None})
                
                # Clear current points and overlay points
                current_points = []
                # Optional: Clear overlays
                # Reset image to original resized image (without points)
                img_display = resized_img.copy()
                
                # Draw the box on the original image
                cv2.drawContours(img_display, [box_pts], 0, (0,0,255), 2)
                cv2.imshow(image_filename, img_display)
                print(f"Box with {len(pts)} points added.")

                # Redraw all existing boxes
                for idx, b in enumerate(boxes):
                    highlight_side = b.get('head_side') if 'head_side' in b else None
                    # If this box is currently being viewed for head selection
                    if head_mode and idx == current_box_idx:
                        highlight_side = current_side_index
                    draw_box_with_sides(b['box'], highlight_side=highlight_side)
                    
                    # If label exists, draw it
                    if b.get('label') is not None:
                        # Compute centroid for label placement
                        M = cv2.moments(b['box'])
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                        else:
                            cX, cY = b['box'][0][0], b['box'][0][1]
                        # Draw the label text
                        cv2.putText(img_display, b['label'], (cX - 20, cY), cv2.FONT_HERSHEY_SIMPLEX,
                                    0.6, (255,255,255), 1, cv2.LINE_AA)
                    cv2.imshow(image_filename, img_display)


                # Head orientation mode, for last added box
                if len(boxes) > 0:
                    start_head_selection(len(boxes)-1)
                else:
                    print("No boxes available to assign head side.")
            else:
                print("Need at least 3 points to make a box.")
            
            #cow_id = True #uncomment when ID is required.
            current_points = []
            drawing = False

        elif key == ord('h'):
            # Head orientation mode, for last added box
            if len(boxes) > 0:
                start_head_selection(len(boxes)-1)
            else:
                print("No boxes available to assign head side.")

        elif key == ord('p'):
            # Delete last point
            if current_points:
                current_points.pop()
                print("Last point removed.")
                # Redraw overlay points
                img_display = resized_img.copy()
                # Draw existing boxes
                for b in boxes:
                    draw_box_with_sides(b['box'], highlight_side=None)
                # Draw remaining overlay points
                for pt in current_points:
                    cv2.circle(img_display, pt, 3, (0,255,0), -1)
                cv2.imshow(image_filename, img_display)
            else:
                print("No points to delete.")

        elif key == ord('x'):
            # Delete last box
            if boxes:
                boxes.pop()
                print("Last box removed.")
                # Remove the last entry from data_for_image as well
                if data_for_image:
                    data_for_image.pop()
                # Reset and redraw all boxes
                img_display = resized_img.copy()
                for b in boxes:
                    draw_box_with_sides(b['box'], highlight_side=b.get('head_side'))
                    if b.get('label'):
                            M = cv2.moments(b['box'])
                            if M["m00"] != 0:
                                cX = int(M["m10"] / M["m00"])
                                cY = int(M["m01"] / M["m00"])
                            else:
                                cX, cY = b['box'][0][0], b['box'][0][1]
                            cv2.putText(img_display, b['label'], (cX - 20, cY),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
                cv2.imshow(image_filename, img_display)
            else:
                print("No boxes to delete.")

        elif key == ord('l'):
            # Delete label of the last box
            if boxes:
                boxes[-1]['label'] = None
                print("Deleted label of the last box.")
                # Redraw all boxes with the label removed
                img_display = resized_img.copy()
                for b in boxes:
                    draw_box_with_sides(b['box'], highlight_side=b.get('head_side'))
                    if b.get('label'):
                        M = cv2.moments(b['box'])
                        if M["m00"] != 0:
                            cX = int(M["m10"] / M["m00"])
                            cY = int(M["m01"] / M["m00"])
                        else:
                            cX, cY = b['box'][0][0], b['box'][0][1]
                        cv2.putText(img_display, b['label'], (cX - 20, cY),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)
                cv2.imshow(image_filename, img_display)
            else:
                print("No boxes to delete labels from.")
        

        elif head_mode:
            # In head selection mode
            if key == ord('n'):
                # Cycle to next side
                current_side_index = (current_side_index + 1) % 4
                box_pts = boxes[current_box_idx]['box']
                # Redraw the box highlighting the new side
                draw_box_with_sides(box_pts, highlight_side=current_side_index)
                cv2.imshow(image_filename, img_display)
            elif key == ord('y'):
                # Confirm current side as head side
                boxes[current_box_idx]['head_side'] = current_side_index
                #print(f"Selected side {current_side_index+1} as head side for box {current_box_idx+1}.")
                # Exit head mode
                head_mode = False
                # Redraw the box with highlight
                box_pts = boxes[current_box_idx]['box']
                draw_box_with_sides(box_pts, highlight_side=current_side_index)
                cv2.imshow(image_filename, img_display)
                print("Head selected.")


                # Assume current_box_idx points to the current box
                b = boxes[current_box_idx]
                side_idx = b.get('head_side')
                if side_idx is not None:
                    # Get the vertices of the selected side
                    vertices = b['box']
                    v1 = vertices[side_idx]
                    v2 = vertices[(side_idx + 1)%4]
                    # Compute midpoint of the side
                    side_midpoint = [(v1[0]+v2[0])/2.0, (v1[1]+v2[1])/2.0]
                    # Save head vertices
                    head_side_vertices = [list(map(float, v1)), list(map(float, v2))]
                    data_for_image[-1]['head_vertices'] = head_side_vertices
                    # Calculate angle between center and side midpoint
                    center = b['points'].mean(axis=0)
                    delta_x = side_midpoint[0] - center[0]
                    delta_y = side_midpoint[1] - center[1]
                    angle = np.degrees(np.arctan2(delta_y, delta_x))
                    data_for_image[-1]['head_orientation_angle'] = angle

                assign_label(current_box_idx)
    

            elif key == 27:  # Esc key
                # Cancel head orientation mode
                head_mode = False
                # Redraw box without highlight
                box_pts = boxes[current_box_idx]['box']
                draw_box_with_sides(box_pts, highlight_side=None)
                cv2.imshow(image_filename, img_display)
            # No other keys handled in head mode


        elif assigned_head:
            if key == ord('s'):
                boxes[current_box_idx]['label'] = 'standing'
                print("Label set to 'standing'")
                data_for_image[-1]['label'] = 'standing'
                assigned_head = False
                print_help()

            elif key == ord('l'):
                boxes[current_box_idx]['label'] = 'lying'
                print("Label set to 'lying'")
                data_for_image[-1]['label'] = 'lying'
                assigned_head = False
                print_help()
    
            if b.get('label'):
                annotate_box_with_label(img_display, b['box'], b['label']) 

        elif cow_id:
            cow_id_input = input("Enter cow ID: ")
            # Assign to last box
            if boxes:
                boxes[-1]['cow_id'] = cow_id_input
                data_for_image[-1]['cow_id'] = cow_id_input
                print(f"Cow ID '{cow_id_input}' assigned.")
                print_help()
            cow_id = False

    # Proceed to next image
    cv2.destroyAllWindows()
                

    if exit == True:
        exit = False
        break
    else:
        base_name = os.path.basename(image_path)  # e.g., 'krave.bmp'
        name, ext = os.path.splitext(base_name)  # ('krave', '.bmp')
        save_name = f"{name}_json.json"      # 'krave_json.json
        save_path = os.path.join(output_folder_json, save_name)
        with open(save_path, 'w') as f:
            json.dump(data_for_image, f, indent=2)
