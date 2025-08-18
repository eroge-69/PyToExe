import pandas as pd

file_path = r"D:/data/a.csv"  


output_path = r"D:/data/split_file_"

chunksize = 10000
i = 1

for chunk in pd.read_csv(file_path, chunksize=chunksize):
    chunk.to_csv(f"{output_path}{i}.csv", index=False)
    print(f"Created: {output_path}{i}.csv")
    i += 1

print("Splitting completed successfully!")
