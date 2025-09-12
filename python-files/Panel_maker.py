# This script generates an AutoCAD script file (.scr) to draw a rectangle with square cut corners
# and two sets of circles with distinct parameters inside.
import math

def create_rectangle_script(filename, ln, ht, cut_size):
    """
    Generates an AutoCAD script file to draw a polyline rectangle with square cut corners
    and two sets of circles with distinct parameters inside.

    Args:
        filename (str): The name of the output script file (e.g., 'rectangle.scr').
        length (float): The length of the main rectangle.
        height (float): The height of the main rectangle.
        cut_size (float): The size of the square cutout at each corner.
        insertion_point_x (float): The X-coordinate of the starting point.
        insertion_point_y (float): The Y-coordinate of the starting point.
    """
    try:
        # Fixed parameters for the first set of circles (4mm diameter)
        circle1_diameter = 4.0
        circle1_radius = circle1_diameter / 2.0
        dist1_from_corner = cut_size + 25
        dist1_from_side = 10.0
        min_gap_1 = 200.0
        max_gap_1 = 260.0
        
        # Fixed parameters for the second set of circles (12mm diameter)
        circle2_diameter = 12.0
        circle2_radius = circle2_diameter / 2.0
        dist2_from_corner = cut_size + 100
        dist2_from_side = cut_size + 11

        min_gap_2 = 250.00
        max_gap_2 = 300.0

        #Insertion
        insertion_point_x = 0.0
        insertion_point_y = 0.0

        # Check if the dimensions are large enough to accommodate the cutouts and corner circles.
        min_dim_1 = max(cut_size, dist1_from_corner) * 2
        min_dim_2 = 100
        min_total_dim = max(min_dim_1, min_dim_2)

        # Open the file in write mode, which creates it or overwrites it if it exists.
        with open(filename, 'w') as file:
            for length,height in zip(ln,ht):

                if length < min_total_dim or height < min_total_dim:
                    print("Error: The rectangle dimensions are too small to place the cutouts and circles.")
                    print(f"Minimum length and height must be at least {min_total_dim}mm.")
                    return

                # --- Calculate circles for the first set (4mm diameter) ---
                horizontal_segment_length_1 = length - (2 * dist1_from_corner)

                if horizontal_segment_length_1 > 350:
                    num_horizontal_circles_1 = math.floor(horizontal_segment_length_1/max_gap_1) + 1
                else:
                    num_horizontal_circles_1 = 0

                vertical_segment_length_1 = height - (2 * dist1_from_corner)

                if vertical_segment_length_1 > 350:
                    num_vertical_circles_1 = math.floor(vertical_segment_length_1/max_gap_1) + 1
                else:
                    num_vertical_circles_1 = 0

                    
                # --- Calculate circles for the second set (12mm diameter) ---
                horizontal_segment_length_2 = length - (2 * dist2_from_corner)

                if horizontal_segment_length_2 >= 350:
                    num_horizontal_circles_2 = math.floor(horizontal_segment_length_2/max_gap_2)+ 1
                else:
                    num_horizontal_circles_2 = 0

                vertical_segment_length_2 = height - (2 * dist2_from_corner)

                if vertical_segment_length_2 >= 350:
                    num_vertical_circles_2 = math.floor(vertical_segment_length_2/max_gap_2) + 1
                else:
                    num_vertical_circles_2 = 0
                
                # --- Draw the outer polyline with cut corners ---
                file.write("PLINE\n")

                # Calculate the coordinates for the 12 points, starting from the bottom-left cutout.
                # Point 1
                file.write(f"{insertion_point_x},{insertion_point_y + cut_size}\n")
                # Point 2
                file.write(f"{insertion_point_x},{insertion_point_y + height - cut_size}\n")
                # Point 3
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y + height - cut_size}\n")
                # Point 4
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y + height}\n")
                # Point 5
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y + height}\n")
                # Point 6
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y + height - cut_size}\n")
                # Point 7
                file.write(f"{insertion_point_x + length},{insertion_point_y + height - cut_size}\n")
                # Point 8
                file.write(f"{insertion_point_x + length},{insertion_point_y + cut_size}\n")
                # Point 9
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y + cut_size}\n")
                # Point 10
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y}\n")
                # Point 11
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y}\n")
                # Point 12
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y + cut_size}\n")
                # Origin
                file.write(f"{insertion_point_x},{insertion_point_y + cut_size}\n")
                
                # --- Draw the eight corner circles (Set 1) ---
                file.write("\n")
                
                circle_points_1 = [
                    (insertion_point_x + dist1_from_side, insertion_point_y + dist1_from_corner),   
                    (insertion_point_x + dist1_from_corner, insertion_point_y + dist1_from_side), 
                    (insertion_point_x + length - dist1_from_side, insertion_point_y + dist1_from_corner), 
                    (insertion_point_x + length - dist1_from_corner, insertion_point_y + dist1_from_side), 
                    (insertion_point_x + length - dist1_from_side, insertion_point_y + height - dist1_from_corner),
                    (insertion_point_x + length - dist1_from_corner, insertion_point_y + height - dist1_from_side),
                    (insertion_point_x + dist1_from_side, insertion_point_y + height - dist1_from_corner),
                    (insertion_point_x + dist1_from_corner, insertion_point_y + height - dist1_from_side)
                ]
                
                for cx, cy in circle_points_1:
                    file.write(f"CIRCLE\n")
                    file.write(f"{cx},{cy}\n")
                    file.write(f"{circle1_radius}\n")

                # --- Draw the mid-circles on each side (Set 1) ---
                if num_horizontal_circles_1 > 0:
                    if num_horizontal_circles_1 == 1:
                        cx = insertion_point_x + dist1_from_corner + horizontal_segment_length_1 / 2
                        cy = insertion_point_y + dist1_from_side
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle1_radius}\n")
                    else:
                        gap_h_1 = horizontal_segment_length_1 / num_horizontal_circles_1
                        for i in range(num_horizontal_circles_1):
                            cx = insertion_point_x + dist1_from_corner + (i + 1) * gap_h_1
                            cy = insertion_point_y + dist1_from_side
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle1_radius}\n")

                if num_horizontal_circles_1 > 0:
                    if num_horizontal_circles_1 == 1:
                        cx = insertion_point_x + dist1_from_corner + horizontal_segment_length_1 / 2
                        cy = insertion_point_y + height - dist1_from_side
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle1_radius}\n")
                    else:
                        gap_h_1 = horizontal_segment_length_1 / num_horizontal_circles_1
                        for i in range(num_horizontal_circles_1):
                            cx = insertion_point_x + dist1_from_corner + (i + 1) * gap_h_1
                            cy = insertion_point_y + height - dist1_from_side
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle1_radius}\n")

                if num_vertical_circles_1 > 0:
                    if num_vertical_circles_1 == 1:
                        cx = insertion_point_x + dist1_from_side
                        cy = insertion_point_y + dist1_from_corner + vertical_segment_length_1 / 2
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle1_radius}\n")
                    else:
                        gap_v_1 = vertical_segment_length_1 / num_vertical_circles_1
                        for i in range(num_vertical_circles_1):
                            cx = insertion_point_x + dist1_from_side
                            cy = insertion_point_y + dist1_from_corner + (i + 1) * gap_v_1
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle1_radius}\n")
                
                if num_vertical_circles_1 > 0:
                    if num_vertical_circles_1 == 1:
                        cx = insertion_point_x + length - dist1_from_side
                        cy = insertion_point_y + dist1_from_corner + vertical_segment_length_1 / 2
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle1_radius}\n")
                    else:
                        gap_v_1 = vertical_segment_length_1 / num_vertical_circles_1
                        for i in range(num_vertical_circles_1):
                            cx = insertion_point_x + length - dist1_from_side
                            cy = insertion_point_y + dist1_from_corner + (i + 1) * gap_v_1
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle1_radius}\n")
                
                # --- Draw the eight corner circles (Set 2) ---
                file.write("\n")

                circle_points_2 = []
                bush_criteria = 400 + 2* cut_size

                if length <= bush_criteria:
                    circle_points_2.append((insertion_point_x + (length/2) , insertion_point_y + dist2_from_side))
                    circle_points_2.append((insertion_point_x + (length/2), insertion_point_y + height - dist2_from_side))
                else:
                    circle_points_2.append((insertion_point_x + dist2_from_corner, insertion_point_y + dist2_from_side))
                    circle_points_2.append((insertion_point_x + length - dist2_from_corner, insertion_point_y + dist2_from_side))
                    circle_points_2.append((insertion_point_x + length - dist2_from_corner, insertion_point_y + height - dist2_from_side))
                    circle_points_2.append((insertion_point_x + dist2_from_corner, insertion_point_y + height - dist2_from_side))

                if height <= bush_criteria:
                    circle_points_2.append((insertion_point_x + dist2_from_side, insertion_point_y + (height/2) ))
                    circle_points_2.append((insertion_point_x + length - dist2_from_side, insertion_point_y + (height/2) ))
                else:
                    circle_points_2.append((insertion_point_x + dist2_from_side, insertion_point_y + dist2_from_corner))
                    circle_points_2.append((insertion_point_x + length - dist2_from_side, insertion_point_y + dist2_from_corner))
                    circle_points_2.append((insertion_point_x + length - dist2_from_side, insertion_point_y + height - dist2_from_corner))
                    circle_points_2.append((insertion_point_x + dist2_from_side, insertion_point_y + height - dist2_from_corner))
                
                for cx, cy in circle_points_2:
                    file.write(f"CIRCLE\n")
                    file.write(f"{cx},{cy}\n")
                    file.write(f"{circle2_radius}\n")

                # --- Draw the mid-circles on each side (Set 2) ---
                if num_horizontal_circles_2 > 0:
                    if num_horizontal_circles_2 == 1:
                        cx = insertion_point_x + dist2_from_corner + horizontal_segment_length_2 / 2
                        cy = insertion_point_y + dist2_from_side
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle2_radius}\n")
                    else:
                        gap_h_2 = horizontal_segment_length_2 / num_horizontal_circles_2
                        for i in range(num_horizontal_circles_2):
                            cx = insertion_point_x + dist2_from_corner + (i + 1) * gap_h_2
                            cy = insertion_point_y + dist2_from_side
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle2_radius}\n")

                if num_horizontal_circles_2 > 0:
                    if num_horizontal_circles_2 == 1:
                        cx = insertion_point_x + dist2_from_corner + horizontal_segment_length_2 / 2
                        cy = insertion_point_y + height - dist2_from_side
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle2_radius}\n")
                    else:
                        gap_h_2 = horizontal_segment_length_2 / num_horizontal_circles_2
                        for i in range(num_horizontal_circles_2):
                            cx = insertion_point_x + dist2_from_corner + (i + 1) * gap_h_2
                            cy = insertion_point_y + height - dist2_from_side
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle2_radius}\n")

                if num_vertical_circles_2 > 0:
                    if num_vertical_circles_2 == 1:
                        cx = insertion_point_x + dist2_from_side
                        cy = insertion_point_y + dist2_from_corner + vertical_segment_length_2 / 2
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle2_radius}\n")
                    else:
                        gap_v_2 = vertical_segment_length_2 / num_vertical_circles_2
                        for i in range(num_vertical_circles_2):
                            cx = insertion_point_x + dist2_from_side
                            cy = insertion_point_y + dist2_from_corner + (i + 1) * gap_v_2 
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle2_radius}\n")
                
                if num_vertical_circles_2 > 0:
                    if num_vertical_circles_2 == 1:
                        cx = insertion_point_x + length - dist2_from_side
                        cy = insertion_point_y + dist2_from_corner + vertical_segment_length_2 / 2
                        file.write(f"CIRCLE\n")
                        file.write(f"{cx},{cy}\n")
                        file.write(f"{circle2_radius}\n")
                    else:
                        gap_v_2 = vertical_segment_length_2 / num_vertical_circles_2
                        for i in range(num_vertical_circles_2):
                            cx = insertion_point_x + length - dist2_from_side
                            cy = insertion_point_y + dist2_from_corner + (i + 1) * gap_v_2
                            file.write(f"CIRCLE\n")
                            file.write(f"{cx},{cy}\n")
                            file.write(f"{circle2_radius}\n")

                # --- Draw the inner panel with cut corners ---
                insertion_point_x = insertion_point_x + length + 200
                length = length - 4
                height = height - 4
                
                file.write("PLINE\n")

                # Calculate the coordinates for the 12 points, starting from the bottom-left cutout.
                # Point 1
                file.write(f"{insertion_point_x},{insertion_point_y + cut_size}\n")
                # Point 2
                file.write(f"{insertion_point_x},{insertion_point_y + height - cut_size}\n")
                # Point 3
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y + height - cut_size}\n")
                # Point 4
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y + height}\n")
                # Point 5
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y + height}\n")
                # Point 6
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y + height - cut_size}\n")
                # Point 7
                file.write(f"{insertion_point_x + length},{insertion_point_y + height - cut_size}\n")
                # Point 8
                file.write(f"{insertion_point_x + length},{insertion_point_y + cut_size}\n")
                # Point 9
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y + cut_size}\n")
                # Point 10
                file.write(f"{insertion_point_x + length - cut_size},{insertion_point_y}\n")
                # Point 11
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y}\n")
                # Point 12
                file.write(f"{insertion_point_x + cut_size},{insertion_point_y + cut_size}\n")
                # Origin
                file.write(f"{insertion_point_x},{insertion_point_y + cut_size}\n")
                #End command
                file.write("\n")

                insertion_point_x = insertion_point_x + length + 400
            
        print(f"Successfully created AutoCAD script file: {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- User Input and Script Generation ---

def input_float_list(str):
  try:
    user_input = input(str)

    string_list = user_input.split(',')

    float_list = [float(item.strip()) for item in string_list]

    return float_list

  except ValueError:
    print("Error: Please make sure all entries are valid numbers.")
    return None

if __name__ == "__main__":
    output_filename = "draw_panels.scr"
    
    # Get user input for the rectangle's dimensions and starting point.
    try:
        cutout_size = float(input("Panel (25/50)"))
        rect_length = input_float_list("Enter lengths of panels sep by comma(,): ")
        rect_height = input_float_list("Enter heights of panels sep by comma(,): ")

        # Call the function to generate the script with the fixed cutout size.
        cutout_size -= 2
        create_rectangle_script(output_filename, rect_length, rect_height, cutout_size)
        
    except ValueError:
        print("Invalid input. Please enter numbers only.")
