def convert_non_ascii_chars():
    # 读取输入文本文件
    with open('gtavc.txt', 'r', encoding='utf-8') as input_file:
        input_text = input_file.read()

    # 读取手机hex对照表
    with open('手机hex对照表.txt', 'r', encoding='utf-8') as hex_table_file:
        hex_table = hex_table_file.readlines()

    # 将非ASCII字符转换为对应的字符
    converted_text = ""
    for char in input_text:
        if ord(char) > 127:  # 非ASCII字符
            hex_value = f"{ord(char):04x}"
            for line in hex_table:
                line = line.strip().split('\t')
                if len(line) == 2 and line[1] == hex_value:
                    converted_text += line[0]
                    break
            else:
                converted_text += char
        else:
            converted_text += char

    # 将转换后的文本写回文件
    with open('test.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(converted_text)

convert_non_ascii_chars()
