import tkinter as tk
import random

# Configurações do jogo
LARGURA = 600
ALTURA = 400
TAMANHO_CELULA = 20
VEL_INICIAL = 150  # milissegundos

class JogoCobrinha:
    def __init__(self, root):
        self.root = root
        self.root.title("🐍 Jogo da Cobrinha")
        self.canvas = tk.Canvas(root, width=LARGURA, height=ALTURA, bg="black")
        self.canvas.pack()

        self.direcao = "Direita"
        self.velocidade = VEL_INICIAL
        self.score = 0

        # Inicializar cobrinha e comida
        self.resetar()

        # Controles
        self.root.bind("<KeyPress>", self.mudar_direcao)
        self.atualizar_jogo()

    def resetar(self):
        self.canvas.delete("all")
        self.cobra = [(5, 5), (4, 5), (3, 5)]
        self.desenhar_cobra()
        self.comida = None
        self.spawn_comida()
        self.direcao = "Direita"
        self.score = 0
        self.game_over = False

    def desenhar_cobra(self):
        self.canvas.delete("cobra")
        for x, y in self.cobra:
            self.desenhar_celula(x, y, "green", tag="cobra")

    def desenhar_celula(self, x, y, cor, tag=None):
        x1 = x * TAMANHO_CELULA
        y1 = y * TAMANHO_CELULA
        x2 = x1 + TAMANHO_CELULA
        y2 = y1 + TAMANHO_CELULA
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=cor, outline="", tags=tag)

    def spawn_comida(self):
        while True:
            x = random.randint(0, (LARGURA // TAMANHO_CELULA) - 1)
            y = random.randint(0, (ALTURA // TAMANHO_CELULA) - 1)
            if (x, y) not in self.cobra:
                self.comida = (x, y)
                self.desenhar_celula(x, y, "red", tag="comida")
                break

    def mudar_direcao(self, evento):
        tecla = evento.keysym
        opostas = {
            "Direita": "Esquerda",
            "Esquerda": "Direita",
            "Cima": "Baixo",
            "Baixo": "Cima"
        }
        if tecla in ["Up", "Down", "Left", "Right"]:
            nova = {
                "Up": "Cima",
                "Down": "Baixo",
                "Left": "Esquerda",
                "Right": "Direita"
            }[tecla]

            if nova != opostas.get(self.direcao):
                self.direcao = nova

    def atualizar_jogo(self):
        if not self.game_over:
            self.mover_cobra()
            self.root.after(self.velocidade, self.atualizar_jogo)

    def mover_cobra(self):
        dx, dy = {
            "Direita": (1, 0),
            "Esquerda": (-1, 0),
            "Cima": (0, -1),
            "Baixo": (0, 1)
        }[self.direcao]

        cabeca = self.cobra[0]
        nova_cabeca = (cabeca[0] + dx, cabeca[1] + dy)

        # Colisão com borda
        if (
            nova_cabeca[0] < 0 or
            nova_cabeca[1] < 0 or
            nova_cabeca[0] >= LARGURA // TAMANHO_CELULA or
            nova_cabeca[1] >= ALTURA // TAMANHO_CELULA or
            nova_cabeca in self.cobra
        ):
            self.fim_de_jogo()
            return

        self.cobra = [nova_cabeca] + self.cobra

        if nova_cabeca == self.comida:
            self.score += 1
            self.canvas.delete("comida")
            self.spawn_comida()
            # Aumenta a velocidade conforme a pontuação
            if self.velocidade > 50:
                self.velocidade -= 5
        else:
            self.cobra.pop()  # remove o final (movimento normal)

        self.desenhar_cobra()

    def fim_de_jogo(self):
        self.game_over = True
        self.canvas.create_text(
            LARGURA//2, ALTURA//2 - 20,
            text="💀 Fim de jogo!",
            fill="white",
            font=("Arial", 24)
        )
        self.canvas.create_text(
            LARGURA//2, ALTURA//2 + 20,
            text=f"Pontuação: {self.score}",
            fill="white",
            font=("Arial", 18)
        )
        self.canvas.create_text(
            LARGURA//2, ALTURA//2 + 60,
            text="Pressione R para reiniciar",
            fill="gray",
            font=("Arial", 12)
        )
        self.root.bind("<r>", self.reiniciar)

    def reiniciar(self, event):
        self.resetar()
        self.atualizar_jogo()

# Iniciar o jogo
if __name__ == "__main__":
    root = tk.Tk()
    jogo = JogoCobrinha(root)
    root.mainloop()
