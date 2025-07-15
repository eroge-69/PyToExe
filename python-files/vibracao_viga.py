import numpy as np
import matplotlib.pyplot as plt
from scipy.linalg import eigh

# Parâmetros da viga
L = 1.0  # Comprimento da viga (m)
E = 210e9  # Módulo de Young (Pa)
I = 1e-6  # Momento de inércia (m^4)
rho = 7800  # Densidade (kg/m^3)
A = 0.01  # Área da seção transversal (m^2)
n = 10  # Número de elementos

# Comprimento de cada elemento
le = L / n

# Matrizes de rigidez e massa de um elemento (simplificadas)
Ke = (E * I / le**3) * np.array(
    [
        [12, -6 * le, -12, -6 * le],
        [-6 * le, 4 * le**2, 6 * le, 2 * le**2],
        [-12, 6 * le, 12, 6 * le],
        [-6 * le, 2 * le**2, 6 * le, 4 * le**2],
    ]
)

Me = (rho * A * le / 420) * np.array(
    [
        [156, 22 * le, 54, -13 * le],
        [22 * le, 4 * le**2, 13 * le, -3 * le**2],
        [54, 13 * le, 156, -22 * le],
        [-13 * le, -3 * le**2, -22 * le, 4 * le**2],
    ]
)

# Montagem das matrizes globais
dof = 2 * (n + 1)
K = np.zeros((dof, dof))
M = np.zeros((dof, dof))

for i in range(n):
    idx = slice(2 * i, 2 * i + 4)
    K[idx, idx] += Ke
    M[idx, idx] += Me

# Aplicar condições de contorno (engastada na ponta esquerda)
K = K[2:, 2:]
M = M[2:, 2:]

# Resolver o problema de autovalores generalizado
w2, phi = eigh(K, M)

# Frequências naturais (Hz)
freqs = np.sqrt(w2) / (2 * np.pi)

# Mostrar as primeiras frequências
print("Frequências naturais (Hz):")
for i in range(5):
    print(f"Modo {i+1}: {freqs[i]:.2f} Hz")

# Visualizar os modos
x = np.linspace(0, L, n + 1)

for i in range(3):
    modo = np.zeros(n + 1)
    modo[1:] = phi[::2, i]  # apenas deslocamentos verticais
    plt.plot(x, modo, label=f"Modo {i+1}")

plt.title("Modos de vibração da viga")
plt.xlabel("Comprimento (m)")
plt.ylabel("Deslocamento (arbitrário)")
plt.legend()
plt.grid()
plt.show()
