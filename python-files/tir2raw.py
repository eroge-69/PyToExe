import sys

if len(sys.argv) < 2:
    print("Tiqiaa signal (TIR) to IR raw data (RAW) file converter")
    print("USAGE: tir2raw <tir-file name>")
    sys.exit()

file_content = open(sys.argv[1], 'rb').read()
content_length = len(file_content)
current_value = 0
high_level = True
skip_first_level = True

for i in range(content_length):
    byte_value = file_content[i]
    if byte_value < 128 and skip_first_level:
        continue
    skip_first_level = False
    if byte_value >= 128:
        if high_level:
            current_value += (byte_value - 128) * 16
        else:
            print(current_value, end=' ')
            current_value = (byte_value - 128) * 16
            high_level = True
    else:
        if not high_level:
            current_value += byte_value * 16
        else:
            print(current_value, end=' ')
            current_value = byte_value * 16
            high_level = False

print(current_value)
