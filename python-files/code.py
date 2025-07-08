# Returns the minor of the matrix after removing the i-th row and j-th column
def get_minor(matrix, i, j):
    return [row[:j] + row[j+1:] for row in (matrix[:i] + matrix[i+1:])]

# Computes the determinant of a square matrix (recursive for n > 2)
def determinant(matrix):
    n = len(matrix)
    # Base case for 1x1 matrix
    if n == 1:
        return matrix[0][0]
    # Base case for 2x2 matrix
    if n == 2:
        return matrix[0][0]*matrix[1][1] - matrix[0][1]*matrix[1][0]
    
    det = 0
    # Expand along the first row
    for col in range(n):
        minor = get_minor(matrix, 0, col)
        det += ((-1) ** col) * matrix[0][col] * determinant(minor)
    return det

# Get matrix size from user
n = int(input("Enter the size of the square matrix: "))

# Get matrix elements from user
print(f"Enter the {n}x{n} matrix row by row:")
matrix = []
for i in range(n):
    row = []
    for j in range(n):
        element = float(input(f"Enter element [{i}][{j}]: "))
        row.append(element)
    matrix.append(row)

print("Input matrix:")
for row in matrix:
    print(row)
print("Determinant:", determinant(matrix))
