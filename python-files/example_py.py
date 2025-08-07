import pandas as pd

df = pd.read_excel("example_df.xlsx")
df.rename(columns = {'spending':'total_spend'}, inplace = True)
df.to_excel("output_df.xlsx")