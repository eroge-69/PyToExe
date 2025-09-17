import csv

input_txt_file = 'D:\APF100ITMMGTL15.txt'
output_csv_file = 'D:\output.csv'

with open(input_txt_file, 'r') as in_file, open(output_csv_file, 'w', newline='') as out_file:
    reader = csv.reader(in_file) # Assuming comma-separated values in the text file
    writer = csv.writer(out_file)

    for row in reader:
        writer.writerow(row)