
m, n = map(int, input().split())
k = int(input())
s = [input().split() for _ in range(k)]
w = []
for i in s:
    if i[2] == 'S':
        for j in range(int(i[1])):
            a = (int(i[0]), int(i[1]) - j)
            if a not in w:
                w.append(a)
    if i[2] == 'N':
        for j in range(n - int(i[1]) + 1):
            a = (int(i[0]), int(i[1]) + j)
            if a not in w:
                w.append(a)
    if i[2] == 'W':
        for j in range(int(i[0])):
            a = (int(i[0]) - j, int(i[1]))
            if a not in w:
                w.append(a)
    if i[2] == 'E':
        for j in range(m - int(i[0]) + 1):
            a = (int(i[0]) + j, int(i[1]))
            if a not in w:
                w.append(a)
print(len(w))