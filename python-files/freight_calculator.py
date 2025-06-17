def calculate_freight_class(weight, length, width, height):
    # Step 1: Convert inches to cubic feet
    volume = (length * width * height) / 1728
    if volume == 0:
        return "Invalid dimensions. Volume is zero."
    density = weight / volume

    # Step 2: Determine NMFC class based on density
    if density < 1:
        freight_class = 400
    elif density < 2:
        freight_class = 300
    elif density < 4:
        freight_class = 250
    elif density < 6:
        freight_class = 175
    elif density < 8:
        freight_class = 125
    elif density < 10:
        freight_class = 100
    elif density < 12:
        freight_class = 92.5
    elif density < 15:
        freight_class = 85
    elif density < 22.5:
        freight_class = 70
    elif density < 30:
        freight_class = 65
    elif density < 35:
        freight_class = 60
    elif density < 50:
        freight_class = 55
    else:
        freight_class = 50

    return f"""
Weight: {weight} lbs
Dimensions: {length} x {width} x {height} in
Volume: {volume:.2f} cu ft
Density: {density:.2f} lbs/cu ft
NMFC Freight Class: {freight_class}
"""

# Example usage
if __name__ == "__main__":
    w = float(input("Enter weight (lbs): "))
    l = float(input("Enter length (in): "))
    x = float(input("Enter width (in): "))
    h = float(input("Enter height (in): "))
    result = calculate_freight_class(w, l, x, h)
    print(result)
