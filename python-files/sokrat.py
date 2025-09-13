import pandas as pd

INPUT_FILE = "input.xlsx"   # исходный файл
OUTPUT_FILE = "output.xlsx" # файл с результатом

MAX_LEN = 500  # максимальная длина текста

def shorten_text(text, max_len=MAX_LEN):
    if pd.isna(text):
        return ""
    if len(text) <= max_len:
        return text
    sentences = text.split('. ')
    result = ""
    for sentence in sentences:
        if len(result) + len(sentence) + 2 <= max_len:
            result += sentence.strip() + ". "
        else:
            break
    return result.strip()

def main():
    df = pd.read_excel(INPUT_FILE)
    col_name = df.columns[1]   # столбец B
    df[col_name] = df[col_name].apply(lambda x: shorten_text(x, MAX_LEN))
    df.to_excel(OUTPUT_FILE, index=False)
    print(f"Файл успешно сохранён: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
