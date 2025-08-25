"""
Waterfall chart with per‑step scaling sliders 
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.widgets import TextBox
from matplotlib.widgets import Slider, Button

# ----------------- Data -----------------
labels = ["Available Funds", "Cyber", "ROW", "CAVS/AI", "TA/NEVI/EVChart", "Grid Reliability", "End"]
values = [100000, -15000, -10800, -35000, -22400, -23900, 0.0]  # End is ignored/recomputed
# ----------------------------------------------------------
initial_available_funds = values[0]
delta_labels = labels[1:-1]

def compute_waterfall_coords(values):
    start = values[0]
    deltas_only = values[1:-1]
    end = start + sum(deltas_only)

    cumulative = [start]
    running = start
    for d in deltas_only:
        running += d
        cumulative.append(running)
    cumulative.append(end)

    bar_bottoms, bar_heights = [], []
    for i in range(len(cumulative)):
        if i == 0:
            bar_bottoms.append(0)
            bar_heights.append(start)
        elif i == len(cumulative) - 1:
            bar_bottoms.append(0)
            bar_heights.append(end)
        else:
            prev = cumulative[i-1]
            curr = cumulative[i]
            bar_bottoms.append(min(prev, curr))
            bar_heights.append(abs(curr - prev))

    x = np.arange(len(cumulative))
    return x, bar_bottoms, bar_heights, cumulative

# Figure layout: make room for N sliders at the bottom
n = len(delta_labels)
fig_height = 4.5 + 0.45 * n  # grow height with number of sliders
fig, ax = plt.subplots(figsize=(10, fig_height))
plt.subplots_adjust(bottom=0.12 + 0.05 * n)  # reserve space for sliders

# Initial plot with multipliers all 1.0
multipliers = np.ones(n, dtype=float) # Multipliers for the delta values
orig_deltas = values[1:-1].copy() # Make a copy to allow modification

def redraw(available_funds_val=None):
    scaled_values = [values[0]] + [d * m for d, m in zip(orig_deltas, multipliers)] + [0.0]
    ax.clear()
    x, bottoms, heights, cumulative = compute_waterfall_coords(scaled_values)
    
    # Create a list of colors for the bars
    colors = ['blue'] * len(x)
    colors[0] = 'green'  # Color for the first bar
    colors[-1] = 'green' # Color for the last bar
    ax.bar(x, heights, bottom=bottoms, color=colors)
    xtick_labels = [labels[0]] + delta_labels + ["End"]
    ax.set_xticks(x, xtick_labels)
    ax.set_ylabel("Value")
    ax.set_title("Waterfall Chart (Per-Step Scaling)")
    for xi, top in zip(x, [b + h for b, h in zip(bottoms, heights)]):
        ax.text(xi, top, f"{top:.0f}", ha="center", va="bottom", fontsize=9)
    ax.axhline(0, linewidth=1)
    fig.tight_layout()
    fig.canvas.draw_idle()
    
# Add a TextBox for "Available Funds"
available_funds_ax = fig.add_axes([0.15, 0.02, 0.15, 0.03])
available_funds_textbox = TextBox(ax=available_funds_ax, label='Available Funds:', initial=f"{initial_available_funds:.0f}")

def submit_available_funds(text):
    try:
        new_value = float(text)
        values[0] = new_value # Update the initial available funds
        redraw()
    except ValueError:
        pass # Ignore invalid input

available_funds_textbox.on_submit(submit_available_funds)


# Create one slider per step
sliders = []
text_boxes = []

slider_axes = []
left, width, height = 0.15, 0.7, 0.03
for i, name in enumerate(delta_labels):
    bottom = 0.06 + 0.03 * i  # stack upward
    sax = fig.add_axes([left, bottom, width, height])
    s = Slider(ax=sax, label=f"{name}: {orig_deltas[i]*multipliers[i]:.0f}",
        valmin=-3.0, valmax=3.0, valinit=1.0, valstep=0.05
    )
    sliders.append(s)
    slider_axes.append(sax)

    def make_onchange(idx):
        def _on_change(val):
            multipliers[idx] = sliders[idx].val
            sliders[idx].label.set_text(f"{delta_labels[idx]}: {orig_deltas[idx]*multipliers[idx]:.0f}")
            redraw()
        return _on_change
    s.on_changed(make_onchange(i))

    # Add a TextBox for direct value input
    text_box_ax = fig.add_axes([left + width + 0.02, bottom, 0.1, height])
    tb = TextBox(ax=text_box_ax, label='', initial=f"{orig_deltas[i]:.0f}")
    text_boxes.append(tb)

    def make_onsubmit(idx):
        def _on_submit(text):
            try:
                new_value = float(text)
                orig_deltas[idx] = new_value / multipliers[idx] # Adjust orig_delta based on current multiplier
                redraw()
            except ValueError:
                pass # Ignore invalid input
        return _on_submit
    tb.on_submit(make_onsubmit(i))

# Reset button
button_ax = fig.add_axes([0.88, 0.02, 0.1, 0.03])
reset_btn = Button(button_ax, "Reset")

def on_reset(event):
    for i, s in enumerate(sliders):
        s.reset()  # triggers on_changed
    # Reset original deltas to initial values
    values[0] = initial_available_funds # Reset available funds
    available_funds_textbox.set_val(f"{initial_available_funds:.0f}") # Update textbox
    for i in range(len(orig_deltas)):
        orig_deltas[i] = values[i+1] # Reset to initial values from the 'values' array
    # Ensure redraw for backends that don't trigger immediately
    redraw()

reset_btn.on_clicked(on_reset)

# Initial draw
redraw()

if __name__ == "__main__":
    plt.show()
