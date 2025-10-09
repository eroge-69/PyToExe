def calculate_mass_center():
    try:
        # Input for weights (from three scales)
        print("Enter the weights from three scales in lbs or kg:")
        weight1 = float(input("Nose Gear weight in [g]: "))
        weight2 = float(input("Left Main Gear Wheel weight in [g]: "))
        weight3 = float(input("Right Main Gear Wheel weight in [g]:"))

        # Input for distances (from main gear to each weight)
        #print("\nEnter the distances from the main gear to each weight in ft or m:")
        distance1 = float(input("Distance from NG to MG in [mm] : "))
        distance2=0
        distance3=0
        #distance2 = float(input("Distance 2: "))
        #distance3 = float(input("Distance 3: "))

        # Input for lateral deviations (side-to-side offsets from the longitudinal axis)
        #print("\nEnter the lateral deviations (side-to-side) from the longitudinal axis for each scale in ft or m:")
        lateral0 = float(input("Distance between Main Gear Wheels  [mm] : "))
        lateral1 = 0
        lateral2 = lateral0/2
        lateral3 = lateral0/2

        # Input for the distance between main gear wheels (symmetric on longitudinal axis)
        #main_gear_wheel_distance = float(input("\nEnter the distance between the wheels of the main gear (ft or m): "))

        # Input for the distance from main gear to wing leading edge
        distance_main_to_LE = float(input("Distance from the main gear to the wing leading edge [mm] : "))

        # Calculate total moment and total weight for longitudinal CG
        total_moment = (weight1 * distance1) + (weight2 * distance2) +(weight3 * distance3)
        total_weight = weight1 + weight2 + weight3
        
        # Calculate the center of gravity (CG) relative to the main gear
        cg_main_gear = total_moment / total_weight
        
        # Calculate the center of gravity (CG) relative to the wing leading edge
        cg_wing_LE = cg_main_gear - distance_main_to_LE
        
        # Calculate lateral deviation (side-to-side CG) using the same approach
        lateral_moment = (weight1 * lateral1) + (weight2 * lateral2) - (weight3 * lateral3)
        lateral_deviation = lateral_moment / total_weight
        
        # Calculate the offset in relation to the plane's symmetric main gear
        lateral_offset = lateral_deviation  # Lateral deviation will show how much it is off-center from the longitudinal axis
        
        # Output results
        print(f"\n________________________________________________")
        print(f"                R E S U L T S                   ")
        print(f"________________________________________________")
        print(f"\nTotal Mass =  {total_weight:.0f} [g]")
        print(f"Center of Gravity (CG) from Wing Leading Edge =  {cg_wing_LE:.2f} [mm]")
        print(f"Lateral Deviation of CG from Longitudinal Axis =  {lateral_deviation:.2f} [mm]")
       # print(f"Lateral Offset (from the centerline): {lateral_offset:.2f} units")
       # print(f"Main Gear Wheel Distance (symmetric, between left and right wheels): {main_gear_wheel_distance:.2f} units")
        
    except ValueError:
        print("Error: Please enter valid numeric values.")

# Call the function to run the program
calculate_mass_center()
