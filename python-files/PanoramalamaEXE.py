import json
import math
import os
import copy
import uuid
import tkinter as tk
from tkinter import simpledialog

def calculate_panorama_waypoints(fov, overlap, max_pitch):
    """
    Calculates the required gimbal pitches and headings for a panorama.

    Args:
        fov (float): The camera's field of view in degrees.
        overlap (float): The desired photo overlap in degrees.
        max_pitch (float): The maximum (highest) gimbal pitch in degrees.

    Returns:
        list: A list of tuples, where each tuple contains (pitch, heading).
    """
    # Convert degrees to radians for trigonometric functions
    fov_rad = math.radians(fov)
    overlap_rad = math.radians(overlap)
    max_pitch_rad = math.radians(max_pitch)

    # Calculate the effective FOV after considering overlap
    effective_fov_rad = fov_rad - overlap_rad

    # Store the final list of (pitch, heading) tuples
    panorama_waypoints = []

    # First, calculate pitches and headings for horizontal bands
    # Start at the highest pitch and work down to the nadir (straight down)
    current_pitch_rad = max_pitch_rad
    while current_pitch_rad >= math.radians(-90):
        # Calculate the vertical distance from the center of the sphere
        # This is essentially the radius of the circle of photos at the current pitch
        # The 0.5 is because we're interested in the half-FOV for the calculation
        # of how much the camera "sees" at a given pitch.
        circle_radius = math.cos(current_pitch_rad)

        # Calculate the number of photos needed in the current circle (band)
        # The angle of the camera's FOV projected onto the horizontal plane
        # changes with the pitch. The angle is wider at a lower pitch.
        
        # Clamp the argument to math.asin to prevent a ValueError
        argument = math.sin(effective_fov_rad / 2) / circle_radius
        clamped_argument = max(-1.0, min(1.0, argument))
        
        projected_fov_rad = 2 * math.asin(clamped_argument)
        num_photos = math.ceil(2 * math.pi / projected_fov_rad)

        # Ensure we have at least one photo per band
        if num_photos < 1:
            num_photos = 1

        # Calculate the heading step for this band
        heading_step = 360 / num_photos

        # Add waypoints for this pitch
        for i in range(int(num_photos)):
            heading = i * heading_step
            panorama_waypoints.append((math.degrees(current_pitch_rad), heading))

        # Move to the next pitch band. The vertical step is based on the effective FOV.
        current_pitch_rad -= effective_fov_rad
        
    # Finally, add the single waypoint for the nadir (straight down)
    # The heading doesn't matter for a single point looking straight down
    panorama_waypoints.append((-90.0, 0.0))

    return panorama_waypoints

def get_settings_from_user():
    """
    Prompts the user for settings using a simple GUI window.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    try:
        fov = simpledialog.askfloat("Settings", "Enter Camera FOV (e.g., 41.0):")
        overlap = simpledialog.askfloat("Settings", "Enter Overlap (e.g., 12.0):")
        max_pitch = simpledialog.askfloat("Settings", "Enter Max Gimbal Pitch (e.g., -10.0):")
        
        if fov is None or overlap is None or max_pitch is None:
            print("User cancelled input. Exiting.")
            return None, None, None
            
        return fov, overlap, max_pitch
    except ValueError:
        print("Invalid input. Please enter numbers.")
        return None, None, None
    finally:
        root.destroy()

def main():
    """
    Main function to process the drone mission JSON file.
    """
    # === USER SETTINGS ===
    # Get settings from a pop-up window
    CAMERA_FOV, OVERLAP, MAX_GIMBAL_PITCH = get_settings_from_user()
    
    if CAMERA_FOV is None:
        return

    # Path settings - automatically look in the same folder as the script
    current_directory = os.getcwd()
    input_folder = current_directory
    output_folder = current_directory

    # Ensure output folders exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # === CORE LOGIC ===

    # Step 1: Generate the list of pitches and headings for the panorama
    # The pitches are negative because a negative pitch points the gimbal down.
    print("Step 1: Calculating panorama waypoint positions...")
    
    panorama_positions = calculate_panorama_waypoints(CAMERA_FOV, OVERLAP, MAX_GIMBAL_PITCH)
    
    print(f"Generated {len(panorama_positions)} unique (pitch, heading) positions.")

    # Step 2: Iterate through JSON files in the input folder
    print("Step 2: Processing JSON files...")
    
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            file_path = os.path.join(input_folder, filename)
            print(f"  - Loading {file_path}")
            
            try:
                with open(file_path, 'r') as f:
                    mission_data = json.load(f)
            except json.JSONDecodeError as e:
                print(f"    Error decoding JSON: {e}. Skipping file.")
                continue
            
            # Step 3: Find and replace "move+photo" waypoints with panorama waypoints
            
            top_level_actions = mission_data["actions"][0]["args"]["sequence"]["actions"]
            new_top_level_actions = []

            for action in top_level_actions:
                is_pano_waypoint = False
                original_goto_waypoint = None
                original_take_photo = None
                
                # Check if this is a 'Sequence' action that contains a 'GotoWaypoint' and 'TakePhoto'
                if (action["actionKey"] == "Sequence" and "actions" in action["args"]["sequence"]):
                    inner_actions = action["args"]["sequence"]["actions"]
                    
                    for inner_action in inner_actions:
                        if inner_action["actionKey"] == "GotoWaypoint":
                            original_goto_waypoint = inner_action
                        if inner_action["actionKey"] == "TakePhoto":
                            original_take_photo = inner_action
                    
                    if original_goto_waypoint and original_take_photo:
                        is_pano_waypoint = True

                if is_pano_waypoint:
                    print("    - Found a 'move+photo' waypoint. Generating panorama sequence.")
                    
                    # Use the original action as a template for each new panorama photo
                    for pitch, heading in panorama_positions:
                        # Create a deep copy of the original action
                        new_pano_action = copy.deepcopy(action)
                        new_pano_action["actionUuid"] = str(uuid.uuid4())
                        
                        # Find the GotoWaypoint and TakePhoto actions in the new copy and update them
                        inner_actions_copy = new_pano_action["args"]["sequence"]["actions"]
                        
                        for inner_action in inner_actions_copy:
                            if inner_action["actionKey"] == "GotoWaypoint":
                                # Convert negative degrees to positive radians for the gimbal pitch
                                converted_pitch = math.radians(-pitch)
                                inner_action["args"]["gotoWaypoint"]["waypoint"]["heading"]["value"] = math.radians(heading)
                                inner_action["args"]["gotoWaypoint"]["waypoint"]["gimbalPitch"]["value"] = converted_pitch
                                inner_action["actionUuid"] = str(uuid.uuid4())
                            elif inner_action["actionKey"] == "TakePhoto":
                                inner_action["actionUuid"] = str(uuid.uuid4())
                        
                        new_top_level_actions.append(new_pano_action)

                else:
                    # If it's not a 'move+photo' waypoint, just append a deep copy of the original action
                    new_top_level_actions.append(copy.deepcopy(action))

            # Update the main mission data with the new actions
            if new_top_level_actions:
                mission_data["actions"][0]["args"]["sequence"]["actions"] = new_top_level_actions
            else:
                 print("    - No 'move+photo' waypoints found. Skipping file update.")

            # Step 4: Save the updated JSON file
            output_filename = f"{os.path.splitext(filename)[0]}_panoramized.json"
            output_path = os.path.join(output_folder, output_filename)
            
            print(f"  - Saving new mission to {output_path}")
            
            # Use a more readable indentation for the output JSON
            with open(output_path, 'w') as f:
                json.dump(mission_data, f, indent=2)

    print("\nProcess complete!")

if __name__ == "__main__":
    main()
