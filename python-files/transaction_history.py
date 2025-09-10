
import os
import pandas as pd

def combine_csv_files():
    folder = os.path.dirname(os.path.abspath(__file__))
    files = [f for f in os.listdir(folder) if f.lower().endswith(".csv")]

    if not files:
        print("No CSV files found in folder.")
        return

    print("\nCSV files found:")
    for i, f in enumerate(files, 1):
        print(f"{i}. {f}")

    choice = input("\nCombine all files? (y/n): ").strip().lower()

    if choice == "y":
        selected_files = files
    else:
        selected_files = []
        file_nums = input("Enter file numbers separated by commas (e.g. 1,3,5): ").split(",")
        for num in file_nums:
            try:
                idx = int(num.strip()) - 1
                if 0 <= idx < len(files):
                    selected_files.append(files[idx])
            except ValueError:
                pass

    if not selected_files:
        print("No valid files selected. Exiting.")
        return

    combined_data = []
    header_saved = False

    for file in selected_files:
        file_path = os.path.join(folder, file)
        print(f"Reading: {file}")

        df = pd.read_csv(file_path, sep=";")

        if not header_saved:
            combined_data.append(df)
            header_saved = True
        else:
            combined_data.append(df.iloc[1:] if df.columns[0] == df.iloc[0, 0] else df)

    result = pd.concat(combined_data, ignore_index=True)

    output_csv = os.path.join(folder, "combined.csv")
    result.to_csv(output_csv, sep=";", index=False)
    print(f"\n✅ Combined file saved as: {output_csv}")

    output_xlsx = os.path.join(folder, "combined.xlsx")
    result.to_excel(output_xlsx, index=False)
    print(f"✅ Also saved as: {output_xlsx}")


if __name__ == "__main__":
    combine_csv_files()
