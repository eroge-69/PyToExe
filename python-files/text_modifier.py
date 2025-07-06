import pyperclip

def process_text(text: str) -> str:
    if not text:
        return ""

    # Шаг 1: Первая буква в верхнем регистре
    text = text[0].upper() + text[1:]

    # Шаг 3: если последние две буквы в нижнем регистре
    if len(text) >= 2 and text[-2:].islower():
        text = text[:-2] + text[-2:].upper()

    # Шаг 2: если последние две буквы в верхнем регистре
    if len(text) >= 2 and text[-2:].isupper():
        last_two = text[-2:]
        rest = text[:-2]
        text = last_two + rest + "101!"

    return text

def main():
    input_text = input("Введите текст: ").strip()
    result = process_text(input_text)
    pyperclip.copy(result)
    print(f"Результат: {result} (скопировано в буфер обмена)")

if __name__ == "__main__":
    main()
