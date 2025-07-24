import math

def calculate_steel_coil_weight(outer_diameter_mm, inner_diameter_mm, thickness_mm, width_mm):
    # Convert mm to meters
    OD = outer_diameter_mm / 1000
    ID = inner_diameter_mm / 1000
    T = thickness_mm / 1000
    W = width_mm / 1000

    # Density of mild steel in kg/m^3
    density = 7850

    # Volume of the coil (in cubic meters)
    volume = (math.pi / 4) * (OD ** 2 - ID ** 2) * T * W

    # Weight in kilograms
    weight = volume * density
    return weight

# Example usage
if __name__ == "__main__":
    outer_diameter = float(input("Enter outer diameter (mm): "))
    inner_diameter = float(input("Enter inner diameter (mm): "))
    thickness = float(input("Enter thickness (mm): "))
    width = float(input("Enter width (mm): "))

    weight = calculate_steel_coil_weight(outer_diameter, inner_diameter, thickness, width)
    print(f"Estimated coil weight: {weight:.2f} kg")