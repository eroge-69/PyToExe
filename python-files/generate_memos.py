# Import the libraries we need
import pandas as pd
from docxtpl import DocxTemplate  # Only import DocxTemplate
import os

# Step 1: Define the paths to your files
folder_path = r"C:\WinPython\WPy64-31290\trainingMemos"
folder_path_memos = r"C:\WinPython\WPy64-31290\trainingMemos\memos"
excel_file = os.path.join(folder_path, "trainings.xlsx")
template_file = os.path.join(folder_path, "memo_template.docx")

# Create the memos folder if it doesn't exist
os.makedirs(folder_path_memos, exist_ok=True)

# Step 2: Load the Excel file into a pandas DataFrame
df_trainings = pd.read_excel(excel_file, sheet_name='Removed assignments', names=["UIN", "Name", "Course Number", "Course Name"], dtype={"UIN": str})
#print("Columns in DataFrame:", df_trainings.columns.tolist())
#print(df_trainings.head())

df_additional = pd.read_excel(excel_file, sheet_name='AWP', dtype={"UIN": str})

# Step 3: Clean and fill in the blank cells
# Replace non-breaking spaces and strip whitespace
df_trainings["UIN"] = df_trainings["UIN"].astype(str).str.replace('\xa0', '').str.strip()
df_trainings["Name"] = df_trainings["Name"].astype(str).str.replace('\xa0', '').str.strip()
# Replace empty strings with NaN for ffill
df_trainings["UIN"] = df_trainings["UIN"].replace('', pd.NA)
df_trainings["Name"] = df_trainings["Name"].replace('', pd.NA)
# Apply ffill
df_trainings["UIN"] = df_trainings["UIN"].ffill()
df_trainings["Name"] = df_trainings["Name"].ffill()
df_trainings["Course Number"] = df_trainings["Course Number"].ffill()
df_trainings["Course Name"] = df_trainings["Course Name"].ffill()
#print("DataFrame after filling blanks:")
#print(df_trainings)
print("Number of rows before grouping:", len(df_trainings))
print("Unique UIN/Name combinations before grouping:", len(df_trainings.groupby(["UIN", "Name"])))

df_merged = pd.merge(df_trainings, df_additional[['UIN', 'Job Profile']], on='UIN', how='left')
print("Merged DataFrame:")
print(df_merged.head())

# Step 4: Group the data by UIN and Name
grouped = df_merged.groupby(["UIN", "Name"]).agg({
    "Course Number": lambda x: list(x),
    "Course Name": lambda x: list(x),
    "Job Profile": "first"  # Take the first Department value (should be the same for each UIN)
}).reset_index()
#print(f"Number of unique users: {len(grouped)}")
#print("Grouped data with all columns:")
#print(grouped[["UIN", "Name", "Course Number", "Course Name"]])

# Step 5: Load the Word template
template = DocxTemplate(template_file)

# Step 6: Generate a memo for each user
for index, row in grouped.iterrows():
    # Create a list of dictionaries for the trainings
    trainings = [{"Code": code, "Name": name} for code, name in zip(row["Course Number"], row["Course Name"]) if code and name]
    print(f"Trainings for {row['Name']}: {trainings}")
    
    # Calculate the maximum length of the Course Number
    max_code_length = max(len(str(training['Code'])) for training in trainings)
    padding_width = max_code_length + 4  # Add a small buffer for consistent spacing
    
    # Create a formatted string with fixed-width spacing and newlines
    training_text = "\n".join(
        f"{str(training['Code']):<{padding_width}}  {training['Name']}"
        for training in trainings
    )
    
    # Prepare the data to fill in the template
    context = {
        "name": row["Name"],
        "title": row["Job Profile"] if pd.notna(row["Job Profile"]) else "N/A",  # Handle missing Departments
        "training_text": training_text,
        "training_count": len(trainings)
    }
    #print(f"Context for {row['Name']}: {context}")
    
    # Render the template with this user's data
    template.render(context)   
    
    # Save the memo with a unique filename
    output_filename = f"memo_{row['UIN']}_{row['Name'].replace(', ', '_')}.docx"
    output_path = os.path.join(folder_path_memos, output_filename)
    template.save(output_path)

# Step 7: Print a confirmation message
print("Memos generated successfully!")
