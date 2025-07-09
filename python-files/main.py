import re
def test(s):
    s = re.sub(r'[^\d]', ',', s)
    s = re.sub(r',+', ',', s)
    s = s.strip(',')
    return s

print("Введите значения, для окончания ввода дважды нажмите Enter \n")
lines = []
while True:
    line = input()
    if line == "":
        break
    lines.append(line)
s = '\n'.join(lines)

result = test(s)
print("Результат:", result)
