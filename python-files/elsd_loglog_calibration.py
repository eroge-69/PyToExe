### ELSD Calibration Excel Template with Chart

# Columns:
# A: Concentration (µg/mL)
# B: log10(C)
# C: Slope (n) (fixed)
# D: Intercept log10(k) (fixed)
# E: log10(Predicted S)
# F: Predicted S

# Example Excel Formulas:

# B2 (log10(C))
=LOG10(A2)

# C2 (Slope n)
=1.30  # fixed, copy down

# D2 (Intercept log10(k))
=-0.301  # fixed, copy down

# E2 (log10(Predicted S))
=C2*B2 + D2

# F2 (Predicted S)
=10^E2

# Drag all formulas down for all rows of concentrations.

# Optional: create a scatter plot of log10(S) vs log10(C) to visualize the calibration line.
# Excel Steps to Add Chart:
# 1. Select columns B (log10(C)) and E (log10(Predicted S)).
# 2. Go to Insert → Scatter → Scatter with Straight Lines.
# 3. Add axis titles: X-axis = log10(C), Y-axis = log10(S).
# 4. Optionally, add trendline and display equation on chart to confirm slope and intercept.