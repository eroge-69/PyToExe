# -*- coding: utf-8 -*-
"""
Created on Mon June 23 10:22:42 2025

@author: benfc
"""

#Get filename
filename = input("Input full filename (including extension): ")
new_filename = "TRIMMED_" + filename  

#LJStreamM should always give the time in col 0, amp in col 1, and have 6 header lines
#But it's better to make it a var now in case we use the code with something else
time_col_index = 0
amp_col_index = 1
header_lines = 6

#We are going to find the first amplitude higher than this value, and make the
#corresponding time our new t=0
cutoff_amp = 0.5

'''
If we want the we can get user input for the cutoff value as well, just uncomment
the line below
For now I am just using the above constant for ease of testing
'''
# cutoff_amp = float(input("Enter the cutoff amplitude: "))

cutoff_row = 0 

#Read specified file
with open(filename, 'r') as f:
    lines = f.readlines()

#Testing the formatting of the data file
# for i, line in enumerate(lines[header_lines:header_lines+10]):
#     print(f"Line {i + header_lines + 1}: {repr(line)}")
#     parts = line.strip().split('\t')  # or try split() with no arguments
#     print(f"  Split parts: {parts}")


#Extract column values
values = []
times = []
line_count=0
for line in lines[header_lines:]: #Starts after the header
    line_count +=1
    #This skips any possible empty lines
    #I don't think this should ever be an issue but it's good practice
    if line.strip(): 
        parts = line.strip().split()
        if len(parts) > amp_col_index:
            try:
                t_val = float(parts[time_col_index])
                y0_val = float(parts[amp_col_index])
                times.append(t_val)
                values.append(y0_val)
            except ValueError:
                continue

#Testing that values are actually getting stored
print("Total lines evaluated: " + str(line_count))
print(f"Total values parsed: {len(values)}")
# print(f"First 5 values: {values[:5]}")
print(f"Max y0 value: {max(values) if values else 'N/A'}")
print(f"Using cutoff_amp = {cutoff_amp}")

#Find the first index where y0 exceeds the threshold
cutoff_row = next((i for i, val in enumerate(values) if val >= cutoff_amp), None)
    
#Testing
print(len(values))

#The if statement is mostly just for testing, but might as well leave it in since
#This program isn't time sensitive and it will avoid clogging with useless datasets
if cutoff_row is None:
    print(f"No values found above cutoff amplitude of {cutoff_amp}")
else:
    print(f"Cutoff row index: {cutoff_row}, time: {times[cutoff_row]}, y0: {values[cutoff_row]}")
    with open(new_filename, 'w') as f:
        for i in range(cutoff_row, len(times)):
            f.write(f"{times[i]:.6f}\t{values[i]:.6f}\n")
    print(f"Modified file saved as: {new_filename}")