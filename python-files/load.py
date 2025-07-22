import matplotlib.pyplot as plt
import pandas as pd
# import sys
# import glob
# import os

# def find_latest_hist_file():
#     files = glob.glob("*_hist.csv")
#     if not files:
#         return None
#     latest_file = max(files, key=os.path.getctime)
#     return latest_file

# # Se non viene passato un file come argomento
# if len(sys.argv) < 2:
#     latest_file = find_latest_hist_file()
#     if latest_file:
#         print(f"No input file given. Loading latest hist file: {latest_file}")
#         input_file = latest_file
#     else:
#         input_file = input("No hist CSV file found. Please enter filename: ")
# else:
#     input_file = sys.argv[1]

column_names = ['energy'] + [f'channel_{i}' for i in range(8)]
# df = pd.read_csv(input_file, skiprows=1, names=column_names)
df = pd.read_csv("prova_hist.csv", skiprows=1, names=column_names)

plt.close('all')

fig, axes = plt.subplots(4, 2, figsize=(12, 10))
fig.suptitle('Histograms of Channel Counts', fontsize=16)

for i in range(8):
    ax = axes[i // 2, i % 2]
    x = df['energy']
    y = df[f'channel_{i}']
    ax.fill_between(x, y, step='mid', alpha=0.6)
    ax.set_xlim([0,500])
    ax.set_title(f'Channel {i}')
    ax.set_xlabel('Energy bin')
    ax.set_ylabel('Counts')

plt.tight_layout()
plt.show()
