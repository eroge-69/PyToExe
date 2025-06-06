import pandas as pd
import numpy as np
import os

input_dir = os.getcwd()
rows = []

# Loop through files 1.csv to 18.csv
for i in range(1, 19):
    filename = f'{i}.csv'
    filepath = os.path.join(input_dir, filename)

    try:
        df = pd.read_csv(filepath, header=None, skiprows=1)
        for j in range(0, df.shape[1] - 1, 2):
            x = df.iloc[:, j]
            y = df.iloc[:, j + 1]

            # Remove any rows with missing values
            mask = x.notnull() & y.notnull()
            x = x[mask]
            y = y[mask]

            if len(x) > 1:
                # Linear regression: slope = cov(x, y) / var(x)
                slope = np.cov(x, y, bias=True)[0][1] / np.var(x, ddof=0)
                rows.append({
                    'source_file': filename,
                    'pair_id': (j // 2) + 1,
                    'slope': slope
                })

        print(f"Processed {filename}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# Save combined output
summary_df = pd.DataFrame(rows)
summary_df.to_csv('all_slopes.csv', index=False)
print("Saved all slopes to all_slopes.csv")