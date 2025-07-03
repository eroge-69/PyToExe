import matplotlib.pyplot as plt
import numpy as np

# Data
labels = [
    "TARGET AOP",
    "TARGET NGBB ATTACK",
    "TARGET UNIFI KAMPUNGKU / IDS-SE",
    "TARGET NIGHT HUNTER",
    "TARGET HIGHRISE",
    "TARGET OPS IMPORT",
    "TARGET SUNSET",
    "MONETIZE SRR 2025",
    "FRESH FUNNEL",
    "OC INDOOR MALL",
    "REWARD CM"
]
values = [1364, 196, 84, 155, 60, 30, 50, 185, 100, 125, 350]
total = sum(values)

# Color setup
cmap = plt.get_cmap('tab20')
colors = [cmap(i) for i in np.linspace(0, 1, len(labels))]

# Create figure
fig, ax = plt.subplots(figsize=(12, 8))
bottom = 0

# Plot each segment with value annotation
for i, (label, value) in enumerate(zip(labels, values)):
    bar = ax.bar(0, value, bottom=bottom, color=colors[i], width=0.6, label=f"{label}: {value}")
    bottom += value
    
    # Add value labels inside segments when space permits
    if value > total*0.03:  # Only label segments >3% of total
        ax.text(0, bottom - value/2, f"{value}", 
                ha='center', va='center', color='white', fontweight='bold')

# Formatting
ax.set_title('MONTHLY TARGETS STACK UP (Total = {})'.format(total), fontsize=14, pad=20)
ax.set_xlim(-0.5, 0.5)
ax.set_ylim(0, total*1.05)
ax.axis('off')  # Hide axes

# Create custom legend
legend_elements = [plt.Rectangle((0,0), 1, 1, color=colors[i], 
                  label=f"{labels[i]}: {val} ({val/total:.1%})") 
                  for i, val in enumerate(values)]

plt.legend(handles=legend_elements, loc='center', 
           bbox_to_anchor=(0.5, -0.12), ncol=2,
           frameon=False, fontsize=9)

# Add total label
plt.text(0, total*1.02, f"TOTAL: {total}", 
         ha='center', va='bottom', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.show()