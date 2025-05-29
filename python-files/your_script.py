import xml.etree.ElementTree as ET
import pandas as pd
 
# Parse the XML file
tree = ET.parse('presentation.xml')
root = tree.getroot()
 
# Initialize lists to store extracted data
presentation_id = []
author_seq = []
first_name = []
last_name = []
degree = []
 
# Extract data from XML
for presentation in root.findall('Presentation'):
    pres_id = presentation.get('PresentationID')
    for author in presentation.find('Authors'):
        presentation_id.append(pres_id)
        author_seq.append(author.get('AuthorSeq'))
        first_name.append(author.find('FirstName').text)
        last_name.append(author.find('LastName').text)
        degree.append(author.find('Degree').text if author.find('Degree') is not None else '')
 
# Create a DataFrame
data = {
    'PresentationID': presentation_id,
    'AuthorSeq': author_seq,
    'FirstName': first_name,
    'LastName': last_name,
    'Degree': degree
}
df = pd.DataFrame(data)
 
# Export to Excel
df.to_excel('authors.xlsx', index=False)
print("Data has been successfully extracted and saved to authors.xlsx.")