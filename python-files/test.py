import pandas as pd

def convert_txt_to_csv(input_txt_path, output_csv_path):
with open(input_txt_path, "r", encoding="utf-8") as f:
lines = f.readlines()

rows = [line.strip().split("#") for line in lines if line.strip() and not all(col == "None" for col in line.split("#"))]

header = rows[1]
data_rows = rows[3:]

df = pd.DataFrame(data_rows, columns=header)
df.to_csv(output_csv_path, index=False, encoding="utf-8-sig")
print(f"Đã xuất CSV: {output_csv_path}")


def convert_csv_to_txt(input_csv_path, output_txt_path):
df = pd.read_csv(input_csv_path, dtype=str).fillna("None")

header_1 = "id#Cn#En#Jp#Tc#Kr#De#None#None"
header_2 = "id#中文翻譯#英文翻譯#日語翻譯#繁體中文#韓語#德語#None#None"
header_3 = "string#string#string#string#string#string#string#None#None"

with open(output_txt_path, "w", encoding="utf-8") as f:
f.write(header_1 + "\n")
f.write(header_2 + "\n")
f.write(header_3 + "\n")
for _, row in df.iterrows():
f.write("#".join(row.astype(str)) + "\n")

print(f"Đã tạo lại TXT: {output_txt_path}")

if __name__ == "__main__":

MODE = "txt_to_csv"
txt_input = "CfgDialogueText.txt"
csv_output = "dialogue_translation.csv"
csv_input = "dialogue_translation.csv"
txt_output = "CfgDialogueText_reimported.txt"

if MODE == "txt_to_csv":
convert_txt_to_csv(txt_input, csv_output)
elif MODE == "csv_to_txt":
convert_csv_to_txt(csv_input, txt_output)
else:
print("erorr.")