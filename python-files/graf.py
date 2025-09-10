import math

graf = {
    1: [2, 14],
    2: [1, 3, 7],
    3: [2, 9, 4],
    4: [3, 5],
    5: [4, 6],
    6: [5, 10],
    10: [6, 11],
    7: [2, 8],
    8: [7],
    9: [3, 14],
    11: [10, 12],
    12: [11],
    13: [4, 6],
    14: [1, 9],
    15: []
}

vertexNumber = len(graf)
rows = vertexNumber*5
cols = rows*16//9
matrix = []
for r in range(rows):
    row = []
    for c in range(cols):
        row.append("·") #░
    matrix.append(row)

keys = list(graf.keys())

def vertex_injector(x, y, label):
    matrix[x][y] = str(label)
    matrix[x][y+1] = "│"
    matrix[x][y-1] = "│"
    matrix[x+1][y] = "─"
    matrix[x+1][y+1] = "┘"
    matrix[x+1][y-1] = "└"
    matrix[x-1][y] = "─"
    matrix[x-1][y+1] = "┐"
    matrix[x-1][y-1] = "┌"

def vertex_double_injector(x, y, label):
    matrix[x][y] = str(label)[0]
    matrix[x][y+1] = str(label)[1]
    matrix[x][y+2] = "│"
    matrix[x][y-1] = "│"
    matrix[x+1][y] = "─"
    matrix[x+1][y+1] = "─"
    matrix[x+1][y+2] = "┘"
    matrix[x+1][y-1] = "└"
    matrix[x-1][y] = "─"
    matrix[x-1][y+1] = "─"
    matrix[x-1][y+2] = "┐"
    matrix[x-1][y-1] = "┌"

cx, cy = rows // 2, cols // 2
radius = min(rows, cols) // 3  # precnik

vertexPositions = {}
for idx, key in enumerate(graf):
    angle = 2 * math.pi * idx / vertexNumber
    x = int(cx + radius * math.sin(angle))
    y = int(cy + radius * math.cos(angle))
    if matrix[x][y] == "·":
        if key > 9:
            vertex_double_injector(x, y, key)
            vertexPositions[key] = (x, y)
        else:
            vertex_injector(x, y, key)
            vertexPositions[key] = (x, y)

for key, neighbors in graf.items():
    for i in neighbors:
        if vertexPositions[key][0] == vertexPositions[i][0]: #vodoravno
            for j in range(min(vertexPositions[key][1], vertexPositions[i][1])+2, max(vertexPositions[key][1], vertexPositions[i][1])-1):
                matrix[vertexPositions[key][0]][j] = "X"
        elif vertexPositions[key][1] == vertexPositions[i][1]:  # uspravno
            for k in range(min(vertexPositions[key][0], vertexPositions[i][0])+2, max(vertexPositions[key][0], vertexPositions[i][0])-1):
                matrix[k][vertexPositions[key][1]] = "X"
        else:  # ukoso
            x1, y1 = vertexPositions[key][0], vertexPositions[key][1]
            x2, y2 = vertexPositions[i][0], vertexPositions[i][1]
            offset_x = 2 if x2 > x1 else -2
            offset_y = 2 if y2 > y1 else -2
            dx = (x2 + (-offset_x)) - (x1 + offset_x)
            dy = (y2 + (-offset_y)) - (y1 + offset_y)
            steps = max(abs(dx), abs(dy))
            for step in range(steps + 1):
                xi = (x1 + offset_x) + step * dx // steps
                yi = (y1 + offset_y) + step * dy // steps
                matrix[xi][yi] = "X"

red = "\033[31m"
green = "\033[32m"
yellow = "\033[33m"
reset = "\033[0m"


def print_matrix(mat):
    for row in mat:
        for val in row:
            if val not in ["X", "·"]:
                print(green + val + reset, end=" ")
            else:
                print(val, end=" ")
        print()

print_matrix(matrix)
