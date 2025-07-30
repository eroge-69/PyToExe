import numpy as np
import matplotlib.pyplot as plt
import matplotlib.tri as tri

# Function to convert ternary to Cartesian coordinates
def ternary_to_cartesian(a, b, c):
    x = 0.5 * (2 * b + c) / (a + b + c)
    y = (np.sqrt(3) / 2) * c / (a + b + c)
    return x, y

# Duval's Triangle regions (simplified)
def get_duval_region(ch4, c2h2, c2h4):
    total = ch4 + c2h2 + c2h4
    ch4_pct = (ch4 / total) * 100
    c2h2_pct = (c2h2 / total) * 100
    c2h4_pct = (c2h4 / total) * 100

    if c2h2_pct > 20 and ch4_pct < 50:
        return "Partial Discharge (PD)"
    elif c2h4_pct > 50 and ch4_pct < 30:
        return "Thermal Fault (T3)"
    elif c2h4_pct > 30 and c2h4_pct <= 50 and ch4_pct < 30:
        return "Thermal Fault (T2)"
    elif ch4_pct > 50 and c2h2_pct < 20:
        return "Thermal Fault (T1)"
    elif c2h2_pct > 20 and ch4_pct > 50:
        return "Discharge (D1/D2)"
    else:
        return "Uncertain Region"

# Get user input
print("Enter DGA gas concentrations (in ppm):")
ch4 = float(input("CH4: "))
c2h2 = float(input("C2H2: "))
c2h4 = float(input("C2H4: "))

# Normalize and convert to Cartesian
x, y = ternary_to_cartesian(ch4, c2h2, c2h4)
region = get_duval_region(ch4, c2h2, c2h4)

# Plot Duval's Triangle
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_aspect('equal')

# Triangle vertices (CH4, C2H2, C2H4)
vertices = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2], [0, 0]])
ax.plot(vertices[:, 0], vertices[:, 1], 'k-', linewidth=2)

# Label vertices
ax.text(0, 0, 'CH4 (100%)', ha='center', va='top')
ax.text(1, 0, 'C2H2 (100%)', ha='center', va='top')
ax.text(0.5, np.sqrt(3)/2, 'C2H4 (100%)', ha='center', va='bottom')

# Plot user point
ax.scatter(x, y, color='red', s=100, zorder=5)
ax.text(x, y, f'Your Data\n{region}', ha='center', va='bottom', color='red')

# Add gridlines (optional)
corners = np.array([[0, 0], [1, 0], [0.5, np.sqrt(3)/2]])
triangle = tri.Triangulation(corners[:, 0], corners[:, 1])
refiner = tri.UniformTriRefiner(triangle)
trimesh = refiner.refine_triangulation(subdiv=4)
ax.triplot(trimesh, color='gray', linestyle=':', alpha=0.5)

# Formatting
ax.axis('off')
ax.set_title("Duval's Triangle for DGA Analysis", pad=20)
plt.tight_layout()
plt.show()

# Print result
print(f"\nDiagnosis: The point lies in the *{region}*.")