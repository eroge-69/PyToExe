import os
import pandas as pd

def main():
    # Step 1: Set working directory to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Step 2: Load Excel file
    file_path = os.path.join(script_dir, 'Sankey.xlsx')
    df = pd.read_excel(file_path)

    # Step 3: Fill NaNs and set index
    df = df.fillna(0)
    df = df.set_index('Stage 1')

    # Step 4: Convert from wide to long format
    df_long = df.stack().reset_index()
    df_long.columns = ['Row', 'Column', 'Value']
    df_long = df_long[df_long['Value'] > 0]

    # Step 5: Format into SankeyMATIC code
    df_long['Sankey_Format'] = df_long.apply(lambda x: f"{x['Column']}[{x['Value']}] {x['Row']}", axis=1)

    # Step 6: Sort by Column and Row
    df_long = df_long.sort_values(by=['Column', 'Row'])

    # Step 7: Write output to text file
    with open('Sankey.txt', 'w', encoding='utf-8') as f:
        for line in df_long['Sankey_Format']:
            f.write(line + '\n')

    print("Sankey Code stored to Sankey.txt")

if __name__ == "__main__":
    main()
