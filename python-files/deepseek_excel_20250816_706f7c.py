import pandas as pd
import random

# Define equipment types and fire zones
equipment_types = ['AHU', 'FCU', 'Damper', 'Escalator', 'Lift', 'Fan', 'Smoke Fan', 'Stair Press']
fire_zones = [f'Zone {i}' for i in range(1, 21)]  # 20 fire zones

# Define Likelihood and Severity levels
likelihood_levels = ['Rare', 'Unlikely', 'Possible', 'Likely', 'Almost Certain']
severity_levels = ['Insignificant', 'Minor', 'Moderate', 'Major', 'Catastrophic']

# Risk Matrix to determine risk rating
risk_matrix = {
    ('Rare', 'Insignificant'): 'Low', ('Rare', 'Minor'): 'Low', ('Rare', 'Moderate'): 'Low',
    ('Rare', 'Major'): 'Medium', ('Rare', 'Catastrophic'): 'Medium',
    ('Unlikely', 'Insignificant'): 'Low', ('Unlikely', 'Minor'): 'Low', ('Unlikely', 'Moderate'): 'Medium',
    ('Unlikely', 'Major'): 'Medium', ('Unlikely', 'Catastrophic'): 'High',
    ('Possible', 'Insignificant'): 'Low', ('Possible', 'Minor'): 'Medium', ('Possible', 'Moderate'): 'Medium',
    ('Possible', 'Major'): 'High', ('Possible', 'Catastrophic'): 'High',
    ('Likely', 'Insignificant'): 'Medium', ('Likely', 'Minor'): 'Medium', ('Likely', 'Moderate'): 'High',
    ('Likely', 'Major'): 'High', ('Likely', 'Catastrophic'): 'Extreme',
    ('Almost Certain', 'Insignificant'): 'Medium', ('Almost Certain', 'Minor'): 'High',
    ('Almost Certain', 'Moderate'): 'High', ('Almost Certain', 'Major'): 'Extreme',
    ('Almost Certain', 'Catastrophic'): 'Extreme',
}

# Generate 1000 equipment entries
data = []
for i in range(1, 1001):
    eq_type = random.choice(equipment_types)
    eq_id = f"{eq_type}-{i:04d}"
    zone = random.choice(fire_zones)
    likelihood = random.choice(likelihood_levels)
    severity = random.choice(severity_levels)
    risk = risk_matrix[(likelihood, severity)]
    data.append([eq_id, eq_type, zone, likelihood, severity, risk])

# Create DataFrame
df = pd.DataFrame(data, columns=['Equipment ID', 'Equipment Type', 'Fire Zone', 'Likelihood', 'Severity', 'Risk Rating'])

# Save to Excel
df.to_excel("Fire_Risk_Matrix_Equipments.xlsx", index=False)
print("Excel file 'Fire_Risk_Matrix_Equipments.xlsx' has been created.")
