import pandas as pd

# Define example structure for Excel template
categories = [
    'Leather', 'Leather Lining', 'Elastic', 'Stamping Foil', 'Buckles', 'Ring',
    'Eyelet', 'Ornaments', 'Hook', 'Rivet', 'Zipper', 'Shoe Lace', 'Outsole',
    'Velcro Tape', 'Thread', 'Moccasin Cord', 'Welt', 'Heel Insert',
    'Non Leather Lining', 'TPR', 'Tape', 'Footbed', 'Foam', 'EVA', 'Shoe Box',
    'Master Carton', 'Lace in length', 'Socks Adhesive', 'Stitched Label',
    'Transfer Label', 'Embossed Label', 'Non TPR Material', 'Last']

# Create main sheet structure
data = {'Category Code': [], 'Category Name': [], 'Field1': [], 'Field2': [], 'Field3': [], 'Field4': [], 'Field5': [], 'Field6': [], 'Field7': [], 'Part No': []}

# Populate with categories
for i, cat in enumerate(categories, start=1):
    data['Category Code'].append(str(i).zfill(2))
    data['Category Name'].append(cat)
    for key in ['Field1','Field2','Field3','Field4','Field5','Field6','Field7','Part No']:
        data[key].append('')  # Empty fields for user input

# Create dataframe
df = pd.DataFrame(data)

# Save to Excel
file_path = '/mnt/data/Footwear_PartCode_Template.xlsx'
df.to_excel(file_path, index=False)
