import pandas as pd 
import matplotlib.pyplot as plt 
 
# Replace 'results.csv' with your CSV filename or path 
csv_file = 'results.csv' 
 
# Load the CSV into a DataFrame 
df = pd.read_csv(csv_file) 
 
# Plotting example: epoch vs train/box_loss and val/box_loss 
plt.figure(figsize = (12, 6)) 
 
plt.plot(df['epoch'], df['train/box_loss'], label='Train Box Loss') 
plt.plot(df['epoch'], df['val/box_loss'], label='Validation Box Loss') 
plt.plot(df['epoch'], df['val/cls_loss'], label='Validation Class Loss') 
plt.plot(df['epoch'], df['train/dfl_loss'], label='Distribution focal Loss') 
 
plt.plot(df['epoch'], df['metrics/precision(B)'], label='precision(B)') 
plt.plot(df['epoch'], df['metrics/recall(B)'], label='recall(B)') 
 
plt.xlabel('Epoch') 
plt.ylabel('Loss') 
plt.title('Train and Validation Box Loss over Epochs') 
plt.legend() 
plt.grid(True) 
 
plt.show() 
